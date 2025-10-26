"""
Plagiarism Detection Service - Simplified Version
Uses text-based similarity and LLM analysis (NO vector database)
"""

import os
import sys
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import difflib
import re
import json
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Vector database disabled for performance
VECTOR_STORE_AVAILABLE = False
VectorStoreManager = None

@dataclass
class SimilarityMatch:
    """Data class for similarity match between two submissions"""
    submission_id: str
    student_name: str
    similarity_percentage: float
    matching_sections: List[Dict[str, str]]  # List of {source, target, similarity}
    match_type: str  # "exact", "paraphrased", "structural"
    confidence: float
    flagged: bool


@dataclass
class PlagiarismReport:
    """Comprehensive plagiarism detection report"""
    submission_id: str
    student_name: str
    submission_type: str  # "code", "writeup", "mixed"
    overall_originality_score: float  # 0-100, higher is more original
    total_matches_found: int
    similarity_matches: List[SimilarityMatch]
    flagged_sections: List[Dict[str, Any]]
    risk_level: str  # "low", "medium", "high", "critical"
    recommendations: List[str]
    analysis_timestamp: str
    sources_checked: int


class PlagiarismDetector:
    """
    Advanced plagiarism detection using multiple techniques:
    1. Vector-based semantic similarity (using existing vector DB)
    2. Text-based similarity (difflib, cosine similarity)
    3. Code structure similarity (AST comparison for code)
    4. N-gram matching for exact phrase detection
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, use_vector_db: bool = True):
        """
        Initialize plagiarism detector
        
        Args:
            openai_api_key: API key for LLM analysis (uses Groq now, much faster!)
            use_vector_db: Enable vector DB for cross-submission plagiarism detection
        """
        # Enable vector DB for cross-submission checking
        self.use_vector_db = use_vector_db
        self.vector_manager = None
        
        if self.use_vector_db:
            try:
                from db.vector_store import VectorStoreManager
                self.vector_manager = VectorStoreManager()
                print("✅ Vector database enabled for cross-submission plagiarism detection")
            except Exception as e:
                print(f"⚠️  Vector DB unavailable: {e}")
                print("   Cross-submission checking disabled (only internal + AI detection)")
                self.use_vector_db = False
        
        # Try Groq first (faster), fallback to OpenAI
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
            self.model = "llama-3.3-70b-versatile"
            print("✅ Plagiarism detector initialized with Groq (lightning fast!)")
        elif self.openai_api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_api_key)
            self.model = "gpt-4o-mini"
            print("✅ Plagiarism detector initialized with OpenAI")
        else:
            self.client = None
            self.model = None
            print("⚠️ No AI API key found. Using text-based similarity only.")
        
        # Thresholds for plagiarism detection
        self.thresholds = {
            "high_similarity": 0.85,  # 85%+ similarity
            "medium_similarity": 0.70,  # 70-85% similarity
            "low_similarity": 0.50,  # 50-70% similarity
            "exact_match": 0.95,  # 95%+ is considered exact
        }
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using difflib
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        # Normalize texts
        text1_norm = self._normalize_text(text1)
        text2_norm = self._normalize_text(text2)
        
        # Use SequenceMatcher for similarity
        similarity = difflib.SequenceMatcher(None, text1_norm, text2_norm).ratio()
        return similarity
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove punctuation (optional, can be configured)
        # text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def find_matching_sections(self, text1: str, text2: str, 
                              min_length: int = 50) -> List[Dict[str, Any]]:
        """
        Find matching sections between two texts
        
        Args:
            text1: Source text
            text2: Target text
            min_length: Minimum character length for a match
            
        Returns:
            List of matching sections with metadata
        """
        matches = []
        
        # Split texts into sentences or chunks
        chunks1 = self._split_into_chunks(text1, chunk_size=100)
        chunks2 = self._split_into_chunks(text2, chunk_size=100)
        
        for i, chunk1 in enumerate(chunks1):
            for j, chunk2 in enumerate(chunks2):
                similarity = self.calculate_text_similarity(chunk1, chunk2)
                
                if similarity >= self.thresholds["medium_similarity"] and len(chunk1) >= min_length:
                    matches.append({
                        "source_index": i,
                        "target_index": j,
                        "source_text": chunk1[:200],  # Truncate for display
                        "target_text": chunk2[:200],
                        "similarity": round(similarity * 100, 2),
                        "length": len(chunk1),
                        "match_type": self._classify_match_type(similarity)
                    })
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return matches
    
    def _split_into_chunks(self, text: str, chunk_size: int = 100) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size // 2):  # 50% overlap
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk) > 20:  # Minimum chunk size
                chunks.append(chunk)
        
        return chunks
    
    def _classify_match_type(self, similarity: float) -> str:
        """Classify the type of match based on similarity score"""
        if similarity >= self.thresholds["exact_match"]:
            return "exact"
        elif similarity >= self.thresholds["high_similarity"]:
            return "near_exact"
        elif similarity >= self.thresholds["medium_similarity"]:
            return "paraphrased"
        else:
            return "structural"
    
    def detect_code_similarity(self, code1: str, code2: str) -> Dict[str, Any]:
        """
        Detect similarity between two code snippets
        Uses both text-based and structure-based comparison
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            
        Returns:
            Dictionary with similarity metrics
        """
        # Basic text similarity
        text_similarity = self.calculate_text_similarity(code1, code2)
        
        # Normalize code (remove comments and whitespace)
        code1_normalized = self._normalize_code(code1)
        code2_normalized = self._normalize_code(code2)
        
        # Calculate normalized similarity
        normalized_similarity = self.calculate_text_similarity(
            code1_normalized, code2_normalized
        )
        
        # Extract code structure (variable names, function names, etc.)
        structure1 = self._extract_code_structure(code1)
        structure2 = self._extract_code_structure(code2)
        
        structure_similarity = self.calculate_text_similarity(
            ' '.join(structure1), ' '.join(structure2)
        )
        
        # Weighted average
        overall_similarity = (
            text_similarity * 0.3 +
            normalized_similarity * 0.4 +
            structure_similarity * 0.3
        )
        
        return {
            "overall_similarity": round(overall_similarity * 100, 2),
            "text_similarity": round(text_similarity * 100, 2),
            "normalized_similarity": round(normalized_similarity * 100, 2),
            "structure_similarity": round(structure_similarity * 100, 2),
            "verdict": self._classify_match_type(overall_similarity)
        }
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code by removing comments and extra whitespace"""
        # Remove single-line comments
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        code = re.sub(r'#.*?$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Remove extra whitespace
        code = ' '.join(code.split())
        
        return code
    
    def _extract_code_structure(self, code: str) -> List[str]:
        """Extract structural elements from code (function names, class names, etc.)"""
        elements = []
        
        # Extract function definitions
        functions = re.findall(r'def\s+(\w+)', code)
        elements.extend(functions)
        
        # Extract class definitions
        classes = re.findall(r'class\s+(\w+)', code)
        elements.extend(classes)
        
        # Extract variable assignments (simplified)
        variables = re.findall(r'(\w+)\s*=', code)
        elements.extend(variables[:10])  # Limit to first 10 to avoid noise
        
        return elements
    
    def detect_ai_generated_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        PRODUCTION-GRADE AI detection with multi-stage analysis and detailed feedback
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Comprehensive dictionary with AI detection results and detailed feedback
        """
        if not self.client:
            return {
                "is_ai_generated": False,
                "confidence": 0.0,
                "indicators": [],
                "detailed_indicators": [],
                "human_elements": [],
                "confidence_breakdown": {},
                "explanation": "AI detection unavailable (no API key)",
                "recommendation": "Manual review recommended",
                "ai_tool_signature": "unknown"
            }
        
        try:
            # STAGE 1: Initial Triage (Fast classification)
            triage_prompt = f"""You are an expert AI content detector analyzing code/text for academic integrity.

CONTENT TO ANALYZE ({language}):
```
{code[:1500]}
```

TASK: Quick triage - is this obviously AI-generated, obviously human, or uncertain?

UNIVERSAL AI RED FLAGS (works for ALL content types):

FOR CODE (Python, JS, HTML, CSS, Java, etc.):
• Perfect formatting with ZERO inconsistencies
• Excessive comments explaining obvious code
• Generic names: data, result, output, temp, handler
• Copy-paste errors: .Value, getElementByID, align-item
• No personal coding style or shortcuts

FOR NATURAL TEXT (Essays, answers, reports):
• Perfect grammar and punctuation throughout
• Academic/formal tone with no personal voice
• Generic vocabulary: comprehensive, multifaceted, various, numerous
• Structured like a textbook (clear topic sentences, perfect transitions)
• No contractions, no informal language, no personal anecdotes
• Phrases like "It is important to note", "In conclusion", "Furthermore"
• Every paragraph has equal length and perfect structure

UNIVERSAL HUMAN PATTERNS:

FOR CODE:
• Some formatting inconsistencies
• Pragmatic shortcuts and abbreviations
• Personal style that repeats
• Comments explain WHY not WHAT

FOR NATURAL TEXT:
• Grammar errors or typos (its/it's, their/there)
• Informal language: "really", "pretty", "kind of", "I think"
• Personal voice and anecdotes
• Contractions: can't, don't, it's, they're
• Uneven paragraph lengths
• Stream-of-consciousness feel in places

RESPOND IN JSON:
{{
  "quick_verdict": "ai_generated" | "human_written" | "uncertain",
  "confidence_level": "high" | "medium" | "low",
  "initial_confidence": 0-100,
  "proceed_to_deep_analysis": true/false
}}"""

            triage_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code authenticity expert. Respond ONLY with valid JSON."},
                    {"role": "user", "content": triage_prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            triage_text = triage_response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            import json
            import re
            json_match = re.search(r'\{.*\}', triage_text, re.DOTALL)
            if json_match:
                triage_result = json.loads(json_match.group())
            else:
                triage_result = {"quick_verdict": "uncertain", "proceed_to_deep_analysis": True}
            
            # If high confidence in triage, return early
            if triage_result.get("confidence_level") == "high" and not triage_result.get("proceed_to_deep_analysis", True):
                is_ai = triage_result.get("quick_verdict") == "ai_generated"
                return {
                    "is_ai_generated": is_ai,
                    "confidence": triage_result.get("initial_confidence", 85),
                    "indicators": ["Quick triage: " + triage_result.get("quick_verdict", "")],
                    "verdict": triage_result.get("quick_verdict", ""),
                    "explanation": "High confidence determination from initial analysis"
                }
            
            # STAGE 2: Deep Analysis (Detailed pattern matching)
            deep_analysis_prompt = f"""EXPERT AI-GENERATED CONTENT DETECTION - UNIVERSAL ANALYSIS

CONTENT TO ANALYZE ({language}):
```
{code[:2000]}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UNIVERSAL ANALYSIS FRAMEWORK - Score each category 0-100:
(Works for ALL languages: Python, JavaScript, HTML, CSS, Java, C++, text, essays, etc.)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. DOCUMENTATION/COMMENTS STYLE (Weight: 25%)
   
   FOR CODE - AI Patterns (100 = strong AI):
   • Comments/docs on EVERY function, variable, or statement
   • Educational tone explaining obvious things ("This increments...", "Set color to red...")
   • Perfect grammar, punctuation, and formatting in ALL comments
   • No personal voice - reads like a textbook or tutorial
   • Comments explain WHAT code does (not WHY)
   
   FOR TEXT/ESSAYS - AI Patterns (100 = strong AI):
   • Perfect grammar and punctuation throughout (no errors)
   • Academic vocabulary: comprehensive, multifaceted, various, numerous, significant
   • Generic transitional phrases: "Furthermore", "Moreover", "In conclusion"
   • Formal tone with no personal voice or informal language
   • Phrases like "It is important to note", "It should be emphasized"
   
   FOR CODE - Human Patterns (0 = strong human):
   • Sparse comments - code is self-documenting
   • Comments explain WHY not WHAT
   • Typos, informal language, or conversational tone
   • Inconsistent comment style/density
   • Personal shortcuts or inside jokes
   
   FOR TEXT/ESSAYS - Human Patterns (0 = strong human):
   • Grammar errors: its/it's, their/there, affect/effect
   • Informal language: "really", "pretty", "kind of", "sort of", "I think"
   • Contractions: can't, don't, won't, it's, they're
   • Personal anecdotes: "I saw", "I learned", "In my experience"
   • Conversational tone that feels natural

2. STRUCTURE & FORMATTING (Weight: 20%)
   
   FOR CODE - AI Patterns (100 = strong AI):
   • PERFECT formatting with zero inconsistencies (indentation, spacing, alignment)
   • Textbook-level organization (every section in perfect order)
   • Over-abstraction for simple tasks
   • Every component is isolated and "pure"
   • No signs of iterative development or refactoring
   
   FOR TEXT/ESSAYS - AI Patterns (100 = strong AI):
   • Every paragraph has equal length (4-5 sentences each)
   • Perfect topic sentences in every paragraph
   • Perfectly balanced introduction-body-conclusion structure
   • Transitions are formal and explicit
   • No stream-of-consciousness or tangents
   
   FOR CODE - Human Patterns (0 = strong human):
   • Some formatting inconsistencies (mixed tabs/spaces, uneven alignment)
   • Pragmatic shortcuts (inline code, quick fixes)
   • Signs of evolution (commented-out old code, TODO notes)
   • Some sections more polished than others
   • Practical structure vs theoretical perfection
   
   FOR TEXT/ESSAYS - Human Patterns (0 = strong human):
   • Uneven paragraph lengths
   • Some paragraphs more developed than others
   • Occasional tangents or stream-of-consciousness
   • Informal transitions: "Also", "Plus", "And another thing"
   • Development shows natural flow of thought

3. NAMING & IDENTIFIERS (Weight: 20%)
   
   FOR CODE - AI Patterns (100 = strong AI):
   • Generic names repeated: data, result, output, value, temp, item, response, handler
   • Perfectly descriptive names EVERYWHERE (no shortcuts)
   • No abbreviations or shortcuts ever
   • Consistent naming throughout (no evolution)
   • Names match language conventions perfectly
   
   FOR TEXT/ESSAYS - AI Patterns (100 = strong AI):
   • Generic vocabulary repeated: "significant", "various", "numerous", "substantial"
   • Overly formal word choices for simple concepts
   • Academic buzzwords: "multifaceted", "comprehensive", "pivotal"
   • No slang, no informal expressions
   • Consistent vocabulary level throughout
   
   FOR CODE - Human Patterns (0 = strong human):
   • Mix of abbreviations (tmp, idx, res, val, btn, msg)
   • Some lazy names (x, i, temp, data1, data2)
   • Naming style evolves through file
   • Context-specific creative names
   • Personal naming preferences visible
   
   FOR TEXT/ESSAYS - Human Patterns (0 = strong human):
   • Mix of simple and complex vocabulary
   • Natural word choice that varies
   • Some informal expressions or slang
   • Vocabulary level fluctuates naturally
   • Personal voice comes through

4. ERROR HANDLING & LOGIC (Weight: 15%)
   
   FOR CODE - AI Patterns (100 = strong AI):
   • Handles EVERY possible error/edge case
   • Perfect error messages for all scenarios
   • Extensive validation before every operation
   • No assumptions about valid inputs
   • Defensive programming everywhere
   
   FOR TEXT/ESSAYS - AI Patterns (100 = strong AI):
   • Every claim is balanced with counterpoint
   • Arguments are perfectly structured (claim-evidence-reasoning)
   • No logical gaps or leaps
   • Every perspective is acknowledged
   • Perfectly neutral, balanced tone
   
   FOR CODE - Human Patterns (0 = strong human):
   • Basic/minimal error handling
   • Assumes happy path initially
   • Some bare catch blocks or generic errors
   • Error handling added progressively
   • Practical vs paranoid validation
   
   FOR TEXT/ESSAYS - Human Patterns (0 = strong human):
   • Some logical leaps or gaps
   • Emotional language or strong opinions
   • Arguments may be one-sided
   • Natural flow may skip obvious points
   • Personal biases show through

5. COMPLEXITY & APPROACH (Weight: 10%)
   
   FOR CODE - AI Patterns (100 = strong AI):
   • Over-engineered simple solutions
   • Unnecessary abstraction layers
   • Design patterns for trivial tasks
   • Premature optimization
   • Textbook "perfect" approaches
   
   FOR TEXT/ESSAYS - AI Patterns (100 = strong AI):
   • Every sentence is complex and detailed
   • Never uses simple direct statements
   • Over-explanation of obvious points
   • Unnecessarily academic language
   • Every idea gets equal depth of treatment
   
   FOR CODE - Human Patterns (0 = strong human):
   • Simple solutions for simple problems
   • Direct, pragmatic approaches
   • Optimization only where needed
   • Signs of refactoring/evolution
   • Some technical debt or quick fixes
   
   FOR TEXT/ESSAYS - Human Patterns (0 = strong human):
   • Mix of simple and complex sentences
   • Direct statements when appropriate
   • Natural level of detail (varies by importance)
   • Practical language level
   • Some ideas more developed than others

6. PERSONAL STYLE & FINGERPRINT (Weight: 10%)
   
   FOR CODE - AI Indicators (100 = strong AI - ABSENCE of personality):
   • Zero personal idioms or coding quirks
   • No repeated patterns unique to author
   • No shortcuts, tricks, or "style moves"
   • Completely sterile and generic
   • No consistency in personal choices
   
   FOR TEXT/ESSAYS - AI Indicators (100 = strong AI - ABSENCE of personality):
   • No personal voice or unique perspective
   • No recurring phrases or writing style
   • Feels like a template or formula
   • Generic examples (climate change, technology, society)
   • No personal experiences or specific details
   
   FOR CODE - Human Indicators (0 = strong human - PRESENCE of personality):
   • Recognizable personal style
   • Repeated patterns/habits (same var names, same structure)
   • Unique shortcuts or approaches
   • Consistent personal preferences
   • "Fingerprint" visible across code
   
   FOR TEXT/ESSAYS - Human Indicators (0 = strong human - PRESENCE of personality):
   • Unique voice and perspective
   • Personal anecdotes or specific examples
   • Recurring phrases or writing patterns
   • Distinctive style choices
   • Author's personality comes through

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: CHECK FOR COPY-PASTE AI INDICATORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MAJOR RED FLAGS (typical when copying from AI assistants):
• Wrong capitalization in common methods (.Value vs .value, getElementByID vs getElementById)
• CSS typos in property names (align-item vs align-items, tranform vs transform)
• Mix of perfect structure + careless errors (suggests copy without understanding)
• Generic placeholder names never customized (myFunction, handleClick, doSomething)
• Boilerplate comments left unchanged ("TODO: add your code here")
• Code that works but has conceptual mismatches for actual use case

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPOND IN JSON FORMAT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "detailed_indicators": [
    {{
      "category": "Documentation Style" | "Structure & Formatting" | "Naming & Identifiers" | "Error Handling" | "Complexity" | "Personal Style" | "Copy-Paste Errors",
      "severity": "critical" | "high" | "medium" | "low",
      "ai_score": 0-100,
      "specific_evidence": "Exact line, pattern, or error found",
      "explanation": "Why this indicates AI generation or copy-paste",
      "line_numbers": "approximate location if known"
    }}
  ],
  "human_elements": [
    {{
      "evidence": "specific pattern found",
      "explanation": "why this suggests human authorship"
    }}
  ],
  "confidence_breakdown": {{
    "documentation_style": 0-100,
    "structure_formatting": 0-100,
    "naming_identifiers": 0-100,
    "error_handling": 0-100,
    "complexity": 0-100,
    "personal_style": 0-100,
    "overall_weighted": 0-100
  }},
  "is_ai_generated": true/false,
  "confidence": 0-100,
  "ai_tool_signature": "chatgpt" | "copilot" | "claude" | "gemini" | "mixed" | "unknown",
  "verdict": "ai_generated" | "human_written" | "heavily_ai_assisted" | "lightly_ai_assisted",
  "recommendation": "specific action for instructor",
  "alternative_explanations": ["other possible reasons for patterns"],
  "detailed_explanation": "comprehensive 2-3 sentence analysis"
}}"""

            deep_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a forensic content authenticity expert with 15 years experience detecting AI-generated academic submissions across ALL programming languages, markup languages, and natural text. Analyze systematically and provide evidence-based conclusions. RESPOND ONLY IN VALID JSON."},
                    {"role": "user", "content": deep_analysis_prompt}
                ],
                max_tokens=1500,
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            deep_text = deep_response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', deep_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Add summary indicators for backward compatibility
                if "detailed_indicators" in result:
                    result["indicators"] = [
                        f"{ind.get('severity', '').upper()}: {ind.get('specific_evidence', '')[:80]}"
                        for ind in result["detailed_indicators"][:5]
                    ]
                
                return result
            else:
                # Fallback parsing
                is_ai = "ai" in deep_text.lower() and "generated" in deep_text.lower()
                return {
                    "is_ai_generated": is_ai,
                    "confidence": 50.0,
                    "indicators": ["Unable to parse detailed analysis"],
                    "detailed_indicators": [],
                    "explanation": deep_text[:300]
                }
                
        except Exception as e:
            print(f"⚠️ AI detection error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "is_ai_generated": False,
                "confidence": 0.0,
                "indicators": [],
                "detailed_indicators": [],
                "explanation": f"Analysis error: {str(e)}"
            }
    
    def compare_files_within_submission(self, files_content: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        PRODUCTION-GRADE internal plagiarism detection with detailed analysis
        
        Args:
            files_content: List of dicts with 'filename' and 'content' keys
            
        Returns:
            List of detailed similarity matches between files with evidence
        """
        matches = []
        
        print(f"🔍 Checking for internal plagiarism across {len(files_content)} files...")
        
        # Compare each pair of files
        for i in range(len(files_content)):
            for j in range(i + 1, len(files_content)):
                file1 = files_content[i]
                file2 = files_content[j]
                
                # Calculate similarity
                similarity = self.calculate_text_similarity(
                    file1['content'], 
                    file2['content']
                )
                
                # Only report significant similarities (>40% is suspicious)
                if similarity > 0.40:
                    # Find matching sections
                    matching_sections = self.find_matching_sections(
                        file1['content'],
                        file2['content'],
                        min_length=50
                    )
                    
                    # Get detailed analysis using LLM if available and similarity is high
                    detailed_analysis = None
                    if self.client and similarity > 0.60:
                        try:
                            analysis_prompt = f"""Analyze these two code files for plagiarism evidence:

FILE 1: {file1['filename']}
```
{file1['content'][:1000]}
```

FILE 2: {file2['filename']}
```
{file2['content'][:1000]}
```

Similarity Score: {similarity * 100:.1f}%

Provide detailed forensic analysis in JSON format:
{{
  "is_copy_paste": true/false,
  "evidence_quality": "conclusive" | "strong" | "moderate" | "weak",
  "specific_findings": [
    {{
      "type": "identical_function" | "identical_class" | "identical_block" | "similar_structure",
      "description": "what was copied",
      "location_file1": "approximate line or function name",
      "location_file2": "approximate line or function name",
      "severity": "critical" | "high" | "medium"
    }}
  ],
  "unique_differences": ["list of things that ARE different"],
  "verdict": "direct_copy" | "heavy_copying" | "shared_template" | "coincidental_similarity",
  "explanation": "2-3 sentence analysis",
  "recommendation": "specific action for instructor"
}}"""

                            response = self.client.chat.completions.create(
                                model=self.model,
                                messages=[
                                    {"role": "system", "content": "You are a forensic code analyst detecting internal plagiarism. Provide evidence-based analysis. RESPOND ONLY IN VALID JSON."},
                                    {"role": "user", "content": analysis_prompt}
                                ],
                                max_tokens=800,
                                temperature=0.1
                            )
                            
                            analysis_text = response.choices[0].message.content.strip()
                            
                            # Extract JSON
                            import json
                            import re
                            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                            if json_match:
                                detailed_analysis = json.loads(json_match.group())
                        except Exception as e:
                            print(f"⚠️ Detailed analysis failed: {e}")
                    
                    match_data = {
                        "file1": file1['filename'],
                        "file2": file2['filename'],
                        "similarity_percentage": round(similarity * 100, 2),
                        "matching_sections": len(matching_sections),
                        "top_matches": matching_sections[:5],  # Increased from 3 to 5
                        "verdict": "Critical" if similarity > 0.85 else "Suspicious" if similarity > 0.70 else "Similar",
                        "flagged": similarity > 0.70,
                        "detailed_analysis": detailed_analysis
                    }
                    
                    matches.append(match_data)
                    
                    # Print detailed findings
                    if detailed_analysis:
                        print(f"  📋 {file1['filename']} ↔ {file2['filename']}: {similarity*100:.1f}%")
                        print(f"     Verdict: {detailed_analysis.get('verdict', 'unknown')}")
                        print(f"     Evidence: {detailed_analysis.get('evidence_quality', 'unknown')}")
        
        if matches:
            print(f"⚠️ Found {len(matches)} internal similarities!")
        else:
            print(f"✅ No internal plagiarism detected")
        
        return matches
    
    def check_against_submissions(self, 
                                  submission_text: str,
                                  submission_id: str,
                                  submission_type: str = "writeup",
                                  student_name: str = "Unknown",
                                  check_limit: int = 50,
                                  files_content: Optional[List[Dict[str, str]]] = None) -> PlagiarismReport:
        """
        Comprehensive plagiarism detection:
        1. Internal plagiarism (files within submission)
        2. AI-generated code detection
        
        Args:
            submission_text: Combined text content
            submission_id: Unique identifier
            submission_type: Type of submission (code/writeup/mixed)
            student_name: Student name
            check_limit: Not used anymore
            files_content: List of files for internal comparison
            
        Returns:
            PlagiarismReport with detailed findings
        """
        print(f"🔍 Starting comprehensive plagiarism detection for submission: {submission_id}")
        
        similarity_matches = []
        flagged_sections = []
        sources_checked = 0
        
        # FEATURE 1: Internal Plagiarism Detection (files within submission)
        if files_content and len(files_content) > 1:
            print(f"\n📁 Checking internal plagiarism across {len(files_content)} files...")
            internal_matches = self.compare_files_within_submission(files_content)
            
            for match in internal_matches:
                similarity_matches.append(SimilarityMatch(
                    submission_id=f"internal_{match['file2']}",
                    student_name=f"Same submission: {match['file2']}",
                    similarity_percentage=match['similarity_percentage'],
                    matching_sections=[{
                        "source_text": m["source_text"][:100],
                        "target_text": m["target_text"][:100],
                        "similarity": m["similarity"]
                    } for m in match['top_matches']],
                    match_type="internal_copy",
                    confidence=0.95,
                    flagged=match['flagged']
                ))
                
                if match['flagged']:
                    flagged_sections.append({
                        "source_submission": match['file1'],
                        "text": f"Files {match['file1']} and {match['file2']} are {match['similarity_percentage']}% similar",
                        "similarity": match['similarity_percentage'],
                        "type": "internal_plagiarism"
                    })
        
        # FEATURE 2: Cross-Submission Plagiarism (check against OTHER students)
        if self.use_vector_db and self.vector_manager and submission_text.strip():
            print(f"\n🔍 Checking against {check_limit} previous submissions...")
            try:
                # Search for similar submissions from OTHER students
                similar_docs = self.vector_manager.search_similar_submissions(
                    content=submission_text,
                    k=check_limit,
                    filter_metadata={"type": "submission"}
                )
                
                sources_checked += len(set(doc.metadata.get("submission_id") for doc in similar_docs if doc.metadata.get("submission_id") != submission_id))
                
                # Group by submission and calculate similarity
                submission_groups = {}
                for doc in similar_docs:
                    other_id = doc.metadata.get("submission_id")
                    other_student = doc.metadata.get("student_name", "Unknown")
                    other_filename = doc.metadata.get("filename", "unknown")
                    
                    # Skip if same submission
                    if other_id == submission_id:
                        continue
                    
                    if other_id not in submission_groups:
                        submission_groups[other_id] = {
                            "student": other_student,
                            "filename": other_filename,
                            "chunks": [],
                            "submission_id": other_id
                        }
                    
                    submission_groups[other_id]["chunks"].append(doc.page_content)
                
                # Calculate similarity for each submission
                for other_id, data in submission_groups.items():
                    other_content = "\n".join(data["chunks"])
                    similarity = self.calculate_text_similarity(submission_text, other_content)
                    
                    if similarity >= 0.40:  # 40% threshold for reporting
                        similarity_matches.append(SimilarityMatch(
                            submission_id=other_id,
                            student_name=data["student"],
                            similarity_percentage=similarity * 100,
                            matching_sections=[{
                                "source_text": submission_text[:200],
                                "target_text": other_content[:200],
                                "similarity": str(similarity)
                            }],
                            match_type="cross_submission",
                            confidence=similarity,
                            flagged=similarity > 0.70
                        ))
                        
                        if similarity > 0.70:
                            flagged_sections.append({
                                "source_submission": f"{data['student']} ({other_id})",
                                "text": f"High similarity ({similarity*100:.1f}%) with {data['student']}'s submission",
                                "similarity": similarity * 100,
                                "type": "cross_plagiarism"
                            })
                        
                        print(f"   📊 Found {similarity*100:.1f}% similarity with {data['student']}")
                
                if not submission_groups:
                    print(f"   ✅ No similar submissions found in database")
                    
            except Exception as e:
                print(f"❌ Cross-submission check failed: {e}")
                import traceback
                traceback.print_exc()
        
        # FEATURE 3: AI-Generated Code Detection
        if self.client and submission_type == "code" and submission_text.strip():
            print(f"\n🤖 Checking for AI-generated code patterns...")
            try:
                ai_detection = self.detect_ai_generated_code(submission_text, language="python")
                
                sources_checked += 1
                
                # Check if AI-generated with multiple possible indicators
                is_ai = ai_detection.get("is_ai_generated", False)
                verdict = ai_detection.get("verdict", "").lower()
                
                # Consider various verdict values
                if not is_ai and verdict:
                    is_ai = verdict in ["ai_generated", "likely_ai", "suspicious"]
                
                if is_ai:
                    confidence_raw = ai_detection.get("confidence", 0)
                    # Normalize confidence to 0-1 range
                    confidence = confidence_raw / 100.0 if confidence_raw > 1 else confidence_raw
                    confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
                    
                    # Add AI-generated code as a "match"
                    similarity_matches.append(SimilarityMatch(
                        submission_id="ai_generated",
                        student_name="AI Tool (ChatGPT/Copilot/Claude)",
                        similarity_percentage=confidence * 100,
                        matching_sections=[{
                            "source_text": str(indicator)[:100] if not isinstance(indicator, dict) else indicator.get("specific_evidence", "")[:100],
                            "target_text": "AI pattern detected",
                            "similarity": str(confidence)
                        } for indicator in ai_detection.get("indicators", ai_detection.get("detailed_indicators", []))[:3]],
                        match_type="ai_generated",
                        confidence=confidence,
                        flagged=confidence > 0.50  # Lower threshold for flagging
                    ))
                    
                    if confidence > 0.50:
                        flagged_sections.append({
                            "source_submission": "AI_Tool",
                            "text": ai_detection.get("explanation", ai_detection.get("detailed_explanation", "High likelihood of AI generation")),
                            "similarity": confidence * 100,
                            "type": "ai_generated"
                        })
                        
                    print(f"⚠️  AI Detection: {verdict or 'AI-generated'} ({confidence*100:.1f}% confidence)")
                else:
                    print(f"✅ Code appears human-written (confidence: {ai_detection.get('confidence', 0):.1f}%)")
            except Exception as e:
                print(f"❌ AI detection failed: {e}")
                import traceback
                traceback.print_exc()
        elif self.client and submission_type == "code":
            print(f"⚠️  Skipping AI detection: empty submission")
        
        # Calculate overall originality score
        
        # Calculate overall originality score
        if similarity_matches:
            max_similarity = max(m.similarity_percentage for m in similarity_matches)
            originality_score = max(0, 100 - max_similarity)
        else:
            originality_score = 100.0
        
        # Determine risk level
        risk_level = self._determine_risk_level(originality_score, similarity_matches)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            originality_score, similarity_matches, submission_type
        )
        
        # Create report
        report = PlagiarismReport(
            submission_id=submission_id,
            student_name=student_name,
            submission_type=submission_type,
            overall_originality_score=round(originality_score, 2),
            total_matches_found=len(similarity_matches),
            similarity_matches=similarity_matches[:10],  # Top 10 matches
            flagged_sections=flagged_sections,
            risk_level=risk_level,
            recommendations=recommendations,
            analysis_timestamp=datetime.now().isoformat(),
            sources_checked=sources_checked
        )
        
        print(f"✅ Plagiarism detection complete: {len(similarity_matches)} matches found")
        print(f"📈 Originality Score: {originality_score:.2f}% | Risk Level: {risk_level}")
        
        return report
    
    def _determine_risk_level(self, originality_score: float, 
                            matches: List[SimilarityMatch]) -> str:
        """Determine risk level based on originality score and matches"""
        if originality_score >= 85:
            return "low"
        elif originality_score >= 70:
            return "medium"
        elif originality_score >= 50:
            return "high"
        else:
            return "critical"
    
    def _generate_recommendations(self, originality_score: float,
                                 matches: List[SimilarityMatch],
                                 submission_type: str) -> List[str]:
        """Generate detailed, actionable recommendations based on plagiarism findings"""
        recommendations = []
        
        # Categorize matches by type
        ai_generated = [m for m in matches if m.match_type == "ai_generated"]
        internal_copies = [m for m in matches if m.match_type == "internal_copy"]
        exact_matches = [m for m in matches if m.match_type == "exact"]
        paraphrased = [m for m in matches if m.match_type == "paraphrased"]
        
        # Overall assessment
        if originality_score >= 90:
            recommendations.append("✅ **Excellent Originality**: Content demonstrates strong original work with minimal issues.")
        elif originality_score >= 70:
            recommendations.append("⚠️ **Minor Concerns**: Some similarities detected that warrant review.")
        elif originality_score >= 50:
            recommendations.append("🚨 **Moderate Risk**: Significant similarities found. Manual review required.")
        else:
            recommendations.append("� **High Risk**: Substantial plagiarism indicators. Immediate investigation needed.")
        
        # AI-Generated Code Analysis
        if ai_generated:
            high_confidence_ai = [m for m in ai_generated if m.confidence >= 0.7]
            if high_confidence_ai:
                file_names = [m.submission_id for m in high_confidence_ai[:3]]
                recommendations.append(
                    f"\n**🤖 AI-Generated Content** ({len(high_confidence_ai)} high-confidence detections):\n"
                    f"   • Review files: {', '.join(file_names)}\n"
                    f"   • Evidence includes: Over-commenting, perfect formatting, generic naming patterns\n"
                    f"   • **Action**: Interview student about code development process\n"
                    f"   • **Action**: Request Git commit history or development artifacts"
                )
            else:
                recommendations.append(
                    f"\n**🤖 Possible AI Assistance** ({len(ai_generated)} low-confidence detections):\n"
                    f"   • Some AI patterns detected but could be coincidental\n"
                    f"   • May indicate use of AI suggestions or autocompletion\n"
                    f"   • **Action**: Discuss acceptable AI tool usage policies with student"
                )
        
        # Internal Plagiarism Analysis
        if internal_copies:
            high_similarity = [m for m in internal_copies if m.similarity_percentage >= 80]
            if high_similarity:
                recommendations.append(
                    f"\n**📁 Internal File Duplication** ({len(high_similarity)} high-similarity matches):\n"
                    f"   • Files contain nearly identical code blocks\n"
                    f"   • This may indicate: Copy-paste programming, code generation, or shared templates\n"
                    f"   • **Action**: Check for proper refactoring (should use functions/modules instead)\n"
                    f"   • **Action**: Verify student can explain code purpose and differences"
                )
            else:
                recommendations.append(
                    f"\n**📁 Code Similarity Detected** ({len(internal_copies)} moderate matches):\n"
                    f"   • Some code blocks share similar structure\n"
                    f"   • Could be legitimate shared utilities or templates\n"
                    f"   • **Action**: Review if code reuse is appropriate for the assignment"
                )
        
        # Exact Matches
        if exact_matches:
            recommendations.append(
                f"\n**⚠️ Exact/Near-Exact Matches** ({len(exact_matches)} found):\n"
                f"   • Verbatim or nearly verbatim content detected\n"
                f"   • **Action**: Verify proper quotations and citations\n"
                f"   • **Action**: Check if content is allowed reference material"
            )
        
        # Paraphrased Content
        if paraphrased:
            recommendations.append(
                f"\n**📝 Paraphrasing Patterns** ({len(paraphrased)} instances):\n"
                f"   • Content shows structural similarity to sources\n"
                f"   • **Action**: Ensure proper attribution of ideas\n"
                f"   • **Action**: Verify paraphrasing is substantial, not just synonym substitution"
            )
        
        # Type-specific best practices
        if submission_type == "code":
            recommendations.append(
                "\n**💻 Code Submission Guidelines**:\n"
                "   • Similar algorithms are acceptable if independently implemented\n"
                "   • Code should show understanding through comments and variable names\n"
                "   • Avoid copying implementation details from online sources\n"
                "   • Document any external libraries or frameworks used"
            )
        else:
            recommendations.append(
                "\n**📚 Written Work Guidelines**:\n"
                "   • Use quotation marks for direct quotes\n"
                "   • Cite all sources following required format\n"
                "   • Paraphrase substantially, don't just rearrange words\n"
                "   • Include bibliography/references section"
            )
        
        # Next steps based on risk level
        if originality_score < 70:
            recommendations.append(
                "\n**🎯 Recommended Next Steps**:\n"
                "   1. Schedule meeting with student to discuss findings\n"
                "   2. Request original drafts, notes, or development history\n"
                "   3. Ask student to explain key concepts/code sections\n"
                "   4. Consider re-submission opportunity with proper citations\n"
                "   5. Document findings and meeting outcomes for records"
            )
        
        return recommendations
    
    def generate_plagiarism_report_markdown(self, report: PlagiarismReport) -> str:
        """Generate a markdown-formatted plagiarism report"""
        md = f"""# Plagiarism Detection Report

**Submission ID**: {report.submission_id}
**Student Name**: {report.student_name}
**Submission Type**: {report.submission_type}
**Analysis Date**: {report.analysis_timestamp}

---

## Summary

- **Originality Score**: {report.overall_originality_score:.2f}% / 100%
- **Risk Level**: **{report.risk_level.upper()}**
- **Total Matches Found**: {report.total_matches_found}
- **Sources Checked**: {report.sources_checked}

---

## Detailed Findings

"""
        
        if report.similarity_matches:
            md += "### Similar Submissions Detected\n\n"
            
            for i, match in enumerate(report.similarity_matches, 1):
                flag = "🚨" if match.flagged else "⚠️"
                md += f"{flag} **Match #{i}**: {match.similarity_percentage:.2f}% similarity\n"
                md += f"- **Submission**: {match.submission_id}\n"
                md += f"- **Student**: {match.student_name}\n"
                md += f"- **Match Type**: {match.match_type}\n"
                md += f"- **Confidence**: {match.confidence:.2f}\n"
                
                if match.matching_sections:
                    md += f"- **Matching Sections**: {len(match.matching_sections)}\n"
                    for section in match.matching_sections[:2]:
                        md += f"  - Section: {section['similarity']:.1f}% similar\n"
                
                md += "\n"
        else:
            md += "✅ **No significant similarities detected**\n\n"
        
        if report.flagged_sections:
            md += "### Flagged Sections\n\n"
            for i, section in enumerate(report.flagged_sections, 1):
                md += f"**Section #{i}** (from {section['source_submission']})\n"
                md += f"- Similarity: {section['similarity']:.2f}%\n"
                md += f"- Type: {section['type']}\n"
                md += f"- Text: `{section['text'][:150]}...`\n\n"
        
        md += "## Recommendations\n\n"
        for rec in report.recommendations:
            md += f"- {rec}\n"
        
        md += f"\n---\n\n*Report generated by ProctorIQ Plagiarism Detector*\n"
        
        return md
    
    def export_report_json(self, report: PlagiarismReport) -> str:
        """Export plagiarism report as JSON"""
        def convert_to_dict(obj):
            """Convert dataclass objects to dictionaries"""
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, list):
                        result[key] = [convert_to_dict(item) for item in value]
                    elif hasattr(value, '__dict__'):
                        result[key] = convert_to_dict(value)
                    else:
                        result[key] = value
                return result
            return obj
        
        report_dict = convert_to_dict(report)
        return json.dumps(report_dict, indent=2)


# Standalone function for quick plagiarism check
def quick_plagiarism_check(text1: str, text2: str, text_type: str = "writeup") -> Dict[str, Any]:
    """
    Quick plagiarism check between two texts
    
    Args:
        text1: First text
        text2: Second text
        text_type: Type of content ("code" or "writeup")
        
    Returns:
        Dictionary with similarity results
    """
    detector = PlagiarismDetector(use_vector_db=False)
    
    if text_type == "code":
        return detector.detect_code_similarity(text1, text2)
    else:
        similarity = detector.calculate_text_similarity(text1, text2)
        matches = detector.find_matching_sections(text1, text2)
        
        return {
            "overall_similarity": round(similarity * 100, 2),
            "matching_sections": len(matches),
            "top_matches": matches[:5],
            "verdict": detector._classify_match_type(similarity)
        }


if __name__ == "__main__":
    # Test the plagiarism detector
    print("🧪 Testing Plagiarism Detector...\n")
    
    # Test text similarity
    text1 = """
    Machine learning is a subset of artificial intelligence that focuses on 
    developing algorithms that allow computers to learn from data. Through 
    iterative processes, machine learning models can identify patterns and 
    make predictions without being explicitly programmed.
    """
    
    text2 = """
    Machine learning represents a branch of artificial intelligence dedicated to 
    creating algorithms enabling computers to learn from information. Via 
    repeated processes, these models discover patterns and generate predictions 
    without explicit programming instructions.
    """
    
    detector = PlagiarismDetector(use_vector_db=False)
    
    print("Testing text similarity detection:")
    similarity = detector.calculate_text_similarity(text1, text2)
    print(f"Similarity: {similarity * 100:.2f}%")
    print(f"Match Type: {detector._classify_match_type(similarity)}\n")
    
    # Test code similarity
    code1 = """
    def calculate_sum(numbers):
        total = 0
        for num in numbers:
            total += num
        return total
    """
    
    code2 = """
    def compute_total(nums):
        sum_val = 0
        for n in nums:
            sum_val += n
        return sum_val
    """
    
    print("Testing code similarity detection:")
    code_sim = detector.detect_code_similarity(code1, code2)
    print(f"Overall Similarity: {code_sim['overall_similarity']:.2f}%")
    print(f"Verdict: {code_sim['verdict']}")
    
    print("\n✅ Plagiarism Detector tests complete!")
