"""
FAISS Local Vector Store
Replaces Pinecone with free, local vector similarity search
"""

import os
# Set threading environment variables before any imports
os.environ['TF_NUM_INTEROP_THREADS'] = '1'
os.environ['TF_NUM_INTRAOP_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

import faiss
import numpy as np
import pickle
import threading
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Global lock to prevent concurrent embedding operations
_embedding_lock = threading.Lock()


class FAISSVectorStore:
    """Local vector store using FAISS for similarity search"""
    
    def __init__(
        self,
        index_path: str = "data/faiss_index",
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384
    ):
        """
        Initialize FAISS vector store
        
        Args:
            index_path: Path to save/load FAISS index
            model_name: SentenceTransformer model name
            dimension: Vector dimension (384 for all-MiniLM-L6-v2)
        """
        self.index_path = Path(index_path)
        self.index_file = self.index_path / "faiss.index"
        self.metadata_file = self.index_path / "metadata.pkl"
        self.dimension = dimension
        self.model_name = model_name
        
        # Create directory if it doesn't exist
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Delay model loading to avoid startup blocking
        self.model = None
        
        # Initialize or load FAISS index
        self.index = None
        self.metadata = []  # List of dicts with submission info
        self.id_to_index = {}  # Map submission_id to index position
        
        self._load_or_create_index()
        
        logger.info(f"✅ FAISS vector store initialized with {len(self.metadata)} vectors")
    
    def _ensure_model_loaded(self):
        """Lazy load the model only when first needed"""
        if self.model is None:
            with _embedding_lock:
                # Double-check after acquiring lock
                if self.model is None:
                    # Import here to delay TensorFlow initialization
                    from sentence_transformers import SentenceTransformer
                    logger.info("Loading sentence transformer model...")
                    self.model = SentenceTransformer(self.model_name)
                    logger.info("Model loaded successfully")
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if self.index_file.exists() and self.metadata_file.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_file))
                
                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                # Rebuild ID mapping
                self.id_to_index = {
                    meta["submission_id"]: i
                    for i, meta in enumerate(self.metadata)
                }
                
                logger.info(f"Loaded existing index with {len(self.metadata)} vectors")
            except Exception as e:
                logger.warning(f"Failed to load index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        # Using L2 (Euclidean) distance
        # For cosine similarity, normalize vectors and use L2
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self.id_to_index = {}
        logger.info("Created new FAISS index")
    
    def _save_index(self):
        """Save index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Index saved with {len(self.metadata)} vectors")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def add_submission(
        self,
        submission_id: str,
        text: str,
        user_id: str,
        file_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a submission to the vector store
        
        Args:
            submission_id: Unique submission ID
            text: Text content to embed
            user_id: User who submitted
            file_name: Name of the file
            metadata: Additional metadata
        """
        # Ensure model is loaded
        self._ensure_model_loaded()
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Normalize for cosine similarity (optional but recommended)
        embedding = embedding / np.linalg.norm(embedding)
        
        # Add to FAISS index
        self.index.add(np.array([embedding], dtype=np.float32))
        
        # Store metadata
        meta = {
            "submission_id": submission_id,
            "user_id": user_id,
            "file_name": file_name,
            "text_length": len(text),
            **(metadata or {})
        }
        
        self.metadata.append(meta)
        self.id_to_index[submission_id] = len(self.metadata) - 1
        
        # Save to disk
        self._save_index()
        
        logger.info(f"Added submission {submission_id} to index")
    
    def search_similar(
        self,
        text: str,
        k: int = 5,
        exclude_user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar submissions
        
        Args:
            text: Query text
            k: Number of results to return
            exclude_user_id: Exclude submissions from this user (for cross-student check)
        
        Returns:
            List of similar submissions with scores
        """
        if len(self.metadata) == 0:
            return []
        
        # Ensure model is loaded
        self._ensure_model_loaded()
        
        # Generate query embedding
        query_embedding = self.model.encode(text, convert_to_numpy=True)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search FAISS index
        # We'll search for more than k to account for filtering
        search_k = min(k * 3, len(self.metadata))
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            search_k
        )
        
        # Convert distances to similarity scores (1 - normalized_distance)
        # Since we normalized vectors, L2 distance relates to cosine similarity
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            meta = self.metadata[idx]
            
            # Exclude submissions from the same user if specified
            if exclude_user_id and meta["user_id"] == exclude_user_id:
                continue
            
            # Convert L2 distance to similarity score
            # For normalized vectors: similarity = 1 - (distance^2 / 2)
            similarity = 1 - (dist / 2)
            similarity = max(0, min(1, similarity))  # Clamp to [0, 1]
            
            results.append({
                "submission_id": meta["submission_id"],
                "user_id": meta["user_id"],
                "file_name": meta["file_name"],
                "similarity": float(similarity),
                "distance": float(dist),
                **{k: v for k, v in meta.items() if k not in ["submission_id", "user_id", "file_name"]}
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def get_submission_by_id(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission metadata by ID"""
        idx = self.id_to_index.get(submission_id)
        if idx is not None:
            return self.metadata[idx]
        return None
    
    def remove_submission(self, submission_id: str) -> bool:
        """
        Remove a submission from the index
        
        Note: FAISS doesn't support deletion, so we rebuild the index
        This is acceptable for smaller datasets
        """
        idx = self.id_to_index.get(submission_id)
        if idx is None:
            return False
        
        # Remove from metadata
        self.metadata.pop(idx)
        
        # Rebuild index
        if len(self.metadata) > 0:
            # Extract all vectors except the one to remove
            all_vectors = []
            for i in range(len(self.metadata)):
                if i != idx:
                    # Note: This is a simplified version
                    # In production, you'd need to store vectors separately
                    pass
            
            # For now, rebuild from scratch (requires re-embedding)
            logger.warning("Deletion requires rebuilding index from scratch")
            # TODO: Implement full rebuild if needed
        
        # Rebuild ID mapping
        self.id_to_index = {
            meta["submission_id"]: i
            for i, meta in enumerate(self.metadata)
        }
        
        self._save_index()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_submissions": len(self.metadata),
            "index_dimension": self.dimension,
            "index_type": type(self.index).__name__,
            "index_size_mb": os.path.getsize(self.index_file) / (1024 * 1024) if self.index_file.exists() else 0,
            "unique_users": len(set(m["user_id"] for m in self.metadata))
        }
    
    def clear_index(self):
        """Clear all data from the index"""
        self._create_new_index()
        self._save_index()
        logger.info("Index cleared")


# Global instance
vector_store: Optional[FAISSVectorStore] = None


def get_vector_store() -> FAISSVectorStore:
    """Get or create vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = FAISSVectorStore()
    return vector_store


def initialize_vector_store():
    """Initialize vector store at startup"""
    global vector_store
    vector_store = FAISSVectorStore()
    return vector_store
