"""
MongoDB Database Connection and Models
Uses Motor for async MongoDB operations with FastAPI
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from datetime import datetime

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "proctoriq"

client: Optional[AsyncIOMotorClient] = None
database = None


async def connect_to_mongo():
    """Connect to MongoDB database"""
    global client, database
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        database = client[DATABASE_NAME]
        
        # Test connection
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")


async def create_indexes():
    """Create database indexes for better query performance"""
    try:
        # Users collection indexes
        await database.users.create_index("email", unique=True)
        await database.users.create_index("student_id", unique=True, sparse=True)
        await database.users.create_index("role")
        
        # Submissions collection indexes
        await database.submissions.create_index("user_id")
        await database.submissions.create_index("created_at")
        await database.submissions.create_index([("user_id", 1), ("created_at", -1)])
        
        # Analysis results collection indexes
        await database.analysis_results.create_index("submission_id", unique=True)
        await database.analysis_results.create_index("ai_confidence")
        await database.analysis_results.create_index("originality_score")
        
        print("✅ Database indexes created")
    except Exception as e:
        print(f"⚠️  Index creation warning: {e}")


def get_database():
    """Get database instance"""
    return database


# Database schema documentation
"""
USERS COLLECTION:
{
    "_id": ObjectId,
    "email": str (unique),
    "password_hash": str,
    "role": str ("student" | "teacher"),
    "name": str,
    "student_id": str (unique, optional for students),
    "created_at": datetime,
    "updated_at": datetime,
    "is_active": bool,
    "last_login": datetime
}

SUBMISSIONS COLLECTION:
{
    "_id": ObjectId,
    "submission_id": str (UUID),
    "user_id": ObjectId,
    "file_name": str,
    "file_path": str,
    "file_type": str,
    "file_size": int,
    "content": str,
    "created_at": datetime,
    "status": str ("pending" | "analyzing" | "completed" | "failed")
}

ANALYSIS_RESULTS COLLECTION:
{
    "_id": ObjectId,
    "submission_id": str (UUID),
    "user_id": ObjectId,
    "ai_detection": {
        "classification": str,
        "confidence": float,
        "reasoning": str,
        "patterns_detected": list
    },
    "plagiarism": {
        "originality_score": float,
        "risk_level": str,
        "matches": list,
        "cross_submission_matches": list
    },
    "code_analysis": {
        "quality_score": float,
        "issues": list,
        "suggestions": list
    },
    "created_at": datetime
}

PEER_REVIEWS COLLECTION (Future):
{
    "_id": ObjectId,
    "reviewer_id": ObjectId,
    "reviewed_submission_id": str,
    "rating": float,
    "feedback": str,
    "created_at": datetime
}
"""
