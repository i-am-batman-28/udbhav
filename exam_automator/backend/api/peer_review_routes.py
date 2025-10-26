"""
Peer Review API Routes
Handles submissions, plagiarism detection, code analysis, and reviews
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from typing import List, Optional, Dict, Any
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
import shutil

from pydantic import BaseModel

# Import models
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.submission_models import (
    Submission, SubmissionType, SubmissionStatus,
    SubmissionMetadata, ProgrammingLanguage,
    Review, ReviewType, ReviewStatus,
    PlagiarismReport, CodeAnalysisReport,
    SubmissionCreateRequest, ReviewCreateRequest, ReviewUpdateRequest,
    PlagiarismCheckRequest, CodeAnalysisRequest,
    SubmissionResponse, ReviewSummary, DashboardSummary
)

from services.plagiarism_detector import PlagiarismDetector
from services.code_analyzer import CodeAnalyzer
from ocr.extractor import OCRExtractor
from config.settings import get_settings
from db.mongodb import get_database

router = APIRouter(prefix="/peer-review", tags=["peer-review"])

# Directory setup
SUBMISSIONS_DIR = Path("submissions")
SUBMISSIONS_DIR.mkdir(exist_ok=True)

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# SUBMISSION ENDPOINTS
# ============================================================================

@router.post("/submissions/upload", response_model=Dict[str, Any])
async def upload_submission(
    files: List[UploadFile] = File(...),
    student_id: str = Form(...),
    student_name: str = Form(...),
    student_email: Optional[str] = Form(None),
    submission_type: str = Form(...),  # "code", "writeup", "mixed"
    title: str = Form(...),
    description: Optional[str] = Form(None),
    assignment_id: Optional[str] = Form(None),
    course_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated
    programming_languages: Optional[str] = Form(None)  # Comma-separated
):
    """
    Upload a new submission with code or documents
    
    Args:
        files: List of files (code, PDFs, images, documents)
        student_id: Unique student identifier
        student_name: Student's name
        student_email: Student's email (optional)
        submission_type: Type of submission (code/writeup/mixed)
        title: Submission title
        description: Detailed description
        assignment_id: Assignment identifier
        course_id: Course identifier
        tags: Comma-separated tags
        programming_languages: Comma-separated language names
    
    Returns:
        Submission details with upload confirmation
    """
    try:
        # Generate submission ID
        submission_id = str(uuid.uuid4())
        
        # Create submission directory
        submission_dir = SUBMISSIONS_DIR / submission_id
        submission_dir.mkdir(exist_ok=True)
        
        # Process files
        uploaded_files = []
        total_size = 0
        
        for file in files:
            # Validate file type
            if not file.content_type:
                continue
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            file_id = str(uuid.uuid4())
            saved_filename = f"{file_id}{file_extension}"
            file_path = submission_dir / saved_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Detect programming language for code files
            detected_language = None
            if submission_type in ["code", "mixed"]:
                if file_extension in ['.py']:
                    detected_language = "python"
                elif file_extension in ['.java']:
                    detected_language = "java"
                elif file_extension in ['.js', '.jsx']:
                    detected_language = "javascript"
                elif file_extension in ['.cpp', '.cc']:
                    detected_language = "cpp"
                elif file_extension in ['.c', '.h']:
                    detected_language = "c"
            
            uploaded_files.append({
                "file_id": file_id,
                "original_name": file.filename,
                "saved_name": saved_filename,
                "file_path": str(file_path),
                "file_size": file_size,
                "file_type": file.content_type,
                "language": detected_language,
                "uploaded_at": datetime.now().isoformat()
            })
        
        # Parse tags and languages
        tag_list = [t.strip() for t in tags.split(",")] if tags else []
        lang_list = [l.strip() for l in programming_languages.split(",")] if programming_languages else []
        
        # Create submission metadata
        metadata = {
            "title": title,
            "description": description,
            "assignment_id": assignment_id,
            "course_id": course_id,
            "tags": tag_list,
            "programming_languages": lang_list,
            "total_files": len(uploaded_files),
            "total_size": total_size
        }
        
        # Create submission object
        submission_data = {
            "submission_id": submission_id,
            "student_id": student_id,
            "student_name": student_name,
            "student_email": student_email,
            "submission_type": submission_type,
            "status": "submitted",
            "metadata": metadata,
            "files": uploaded_files,
            "submitted_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),  # Add created_at for frontend compatibility
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to MongoDB
        db = get_database()
        result = await db["submissions"].insert_one(submission_data.copy())
        print(f"✅ Submission saved to MongoDB: {submission_id}")
        
        # Also save submission metadata as JSON backup
        metadata_path = submission_dir / "submission.json"
        with open(metadata_path, "w") as f:
            json.dump(submission_data, f, indent=2)
        
        # Return without MongoDB ObjectId
        return {
            "success": True,
            "message": "Submission uploaded successfully",
            "submission_id": submission_id,
            "files_uploaded": len(uploaded_files),
            "total_size": total_size,
            "submission": submission_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Upload error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/submissions/{submission_id}", response_model=Dict[str, Any])
async def get_submission(submission_id: str):
    """
    Get submission details
    
    Args:
        submission_id: Unique submission identifier
    
    Returns:
        Complete submission information
    """
    try:
        # Fetch from MongoDB
        db = get_database()
        submission = await db["submissions"].find_one({"submission_id": submission_id})
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Convert MongoDB _id to string
        if "_id" in submission:
            submission["_id"] = str(submission["_id"])
        
        # Check for analysis reports in filesystem
        submission_dir = SUBMISSIONS_DIR / submission_id
        plagiarism_report_path = submission_dir / "plagiarism_report.json"
        code_analysis_path = submission_dir / "code_analysis.json"
        ai_tools_results_path = submission_dir / "ai_tools_results.json"
        
        has_plagiarism_report = plagiarism_report_path.exists()
        has_code_analysis = code_analysis_path.exists()
        has_ai_tools_results = ai_tools_results_path.exists()
        
        return {
            "submission": submission,
            "has_plagiarism_report": has_plagiarism_report,
            "has_code_analysis": has_code_analysis,
            "has_ai_tools_results": has_ai_tools_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve submission: {str(e)}")


@router.get("/submissions/student/{student_id}", response_model=List[Dict[str, Any]])
async def get_student_submissions(student_id: str):
    """
    Get all submissions for a student
    
    Args:
        student_id: Student identifier
    
    Returns:
        List of submissions
    """
    try:
        # Fetch from MongoDB
        db = get_database()
        cursor = db["submissions"].find({"student_id": student_id})
        submissions = await cursor.to_list(length=None)
        
        # Convert MongoDB _id to string
        for submission in submissions:
            if "_id" in submission:
                submission["_id"] = str(submission["_id"])
        
        # Sort by submission date (newest first)
        submissions.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        
        return submissions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve submissions: {str(e)}")


# ============================================================================
# PLAGIARISM DETECTION ENDPOINTS
# ============================================================================

@router.post("/submissions/{submission_id}/check-plagiarism", response_model=Dict[str, Any])
async def check_plagiarism(
    submission_id: str,
    check_limit: int = 50,
    include_archived: bool = False
):
    """
    Run plagiarism detection on a submission
    
    Args:
        submission_id: Submission to check
        check_limit: Maximum number of submissions to compare against
        include_archived: Whether to include archived submissions
    
    Returns:
        Plagiarism report with similarity matches
    """
    try:
        print(f"🔍 Starting plagiarism check for submission: {submission_id}")
        
        # Load submission
        submission_dir = SUBMISSIONS_DIR / submission_id
        metadata_path = submission_dir / "submission.json"
        
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Submission not found")
        
        with open(metadata_path, "r") as f:
            submission = json.load(f)
        
        # Extract text from files
        ocr = OCRExtractor()
        extracted_texts = []
        files_content = []  # For internal plagiarism detection
        
        for file_info in submission.get("files", []):
            file_path = file_info["file_path"]
            try:
                text = ocr.extract_text(file_path)
                extracted_texts.append(text)
                files_content.append({
                    "filename": file_info["original_name"],
                    "content": text
                })
            except Exception as e:
                print(f"⚠️ Failed to extract text from {file_info['original_name']}: {e}")
        
        combined_text = "\n\n".join(extracted_texts)
        
        if not combined_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in submission")
        
        # Initialize plagiarism detector 
        # Note: Vector DB disabled by default due to TensorFlow mutex locks
        # For cross-submission checking, use file-based comparison instead
        settings = get_settings()
        use_vector = False  # Set to True only if you have resolved TensorFlow issues
        
        detector = PlagiarismDetector(
            openai_api_key=settings.openai_api_key,
            use_vector_db=use_vector
        )
        
        if use_vector:
            print("✅ Vector DB enabled - cross-submission checking active")
        else:
            print("ℹ️  Vector DB disabled - using internal + AI detection only")
        
        # Run plagiarism detection with file comparison and AI detection
        # Note: Always pass files_content, even if only 1 file (for AI detection)
        report = detector.check_against_submissions(
            submission_text=combined_text,
            submission_id=submission_id,
            submission_type=submission.get("submission_type", "writeup"),
            student_name=submission.get("student_name", "Unknown"),
            check_limit=check_limit,
            files_content=files_content  # Always pass files for AI detection
        )
        
        # Convert report to dict
        def convert_to_dict(obj):
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
        
        # Save report
        report_path = submission_dir / "plagiarism_report.json"
        with open(report_path, "w") as f:
            json.dump(report_dict, f, indent=2)
        
        # Generate markdown report
        markdown_report = detector.generate_plagiarism_report_markdown(report)
        markdown_path = submission_dir / "plagiarism_report.md"
        with open(markdown_path, "w") as f:
            f.write(markdown_report)
        
        # Update submission status
        submission["plagiarism_report_id"] = str(uuid.uuid4())
        submission["updated_at"] = datetime.now().isoformat()
        with open(metadata_path, "w") as f:
            json.dump(submission, f, indent=2)
        
        print(f"✅ Plagiarism check complete: {report.overall_originality_score:.2f}% originality")
        
        # AUTO-STORE SUBMISSION in vector database (only if enabled)
        if use_vector and detector.use_vector_db and detector.vector_manager:
            try:
                print(f"💾 Storing submission in vector database for future comparisons...")
                stored = detector.vector_manager.add_submission_to_vector_store(
                    submission_id=submission_id,
                    content=combined_text,
                    metadata={
                        "student_name": submission.get("student_name", "Unknown"),
                        "submission_type": submission.get("submission_type", "writeup"),
                        "timestamp": datetime.now().isoformat(),
                        "file_count": len(files_content)
                    }
                )
                if stored:
                    print(f"✅ Submission indexed - future uploads will be checked against this")
                else:
                    print(f"⚠️  Failed to index submission (cross-checking may be limited)")
            except Exception as e:
                print(f"⚠️  Could not index submission: {e}")
        
        return {
            "success": True,
            "submission_id": submission_id,
            "report": report_dict,
            "markdown_report_path": str(markdown_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plagiarism check failed: {str(e)}")


@router.get("/submissions/{submission_id}/plagiarism-report", response_model=Dict[str, Any])
async def get_plagiarism_report(submission_id: str):
    """
    Get plagiarism report for a submission
    
    Args:
        submission_id: Submission identifier
    
    Returns:
        Plagiarism report data
    """
    try:
        report_path = SUBMISSIONS_DIR / submission_id / "plagiarism_report.json"
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404, 
                detail="Plagiarism report not found. Run plagiarism check first."
            )
        
        with open(report_path, "r") as f:
            report = json.load(f)
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")


# ============================================================================
# CODE ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/submissions/{submission_id}/analyze-code", response_model=Dict[str, Any])
async def analyze_code(
    submission_id: str,
    file_ids: Optional[List[str]] = None,
    include_ai_feedback: bool = True
):
    """
    Run code analysis on a submission
    
    Args:
        submission_id: Submission to analyze
        file_ids: Specific files to analyze (all code files if None)
        include_ai_feedback: Whether to include AI-powered feedback
    
    Returns:
        Code analysis report with quality metrics
    """
    try:
        print(f"🔍 Starting code analysis for submission: {submission_id}")
        
        # Load submission
        submission_dir = SUBMISSIONS_DIR / submission_id
        metadata_path = submission_dir / "submission.json"
        
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Submission not found")
        
        with open(metadata_path, "r") as f:
            submission = json.load(f)
        
        # Filter code files
        code_files = []
        for file_info in submission.get("files", []):
            if file_ids and file_info["file_id"] not in file_ids:
                continue
            
            # Check if it's a code file
            file_ext = os.path.splitext(file_info["original_name"])[1].lower()
            if file_ext in ['.py', '.java', '.js', '.jsx', '.cpp', '.c', '.h', '.ts', '.go', '.rs']:
                code_files.append(file_info)
        
        if not code_files:
            raise HTTPException(status_code=400, detail="No code files found in submission")
        
        # Initialize code analyzer
        settings = get_settings()
        analyzer = CodeAnalyzer(
            openai_api_key=settings.openai_api_key if include_ai_feedback else None
        )
        
        # Analyze each code file
        file_reports = []
        overall_scores = []
        
        for file_info in code_files:
            file_path = file_info["file_path"]
            
            try:
                # Read code content
                with open(file_path, "r", encoding="utf-8") as f:
                    code_content = f.read()
                
                # Detect language
                language = analyzer.detect_language(code_content)
                
                # Analyze based on language
                if language == "python":
                    report = analyzer.analyze_python_code(
                        code_content, 
                        submission_id=f"{submission_id}_{file_info['file_id']}"
                    )
                    
                    # Convert to dict
                    def convert_to_dict(obj):
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
                    report_dict["file_name"] = file_info["original_name"]
                    report_dict["file_id"] = file_info["file_id"]
                    
                    file_reports.append(report_dict)
                    overall_scores.append(report.quality_score.overall_score)
                else:
                    file_reports.append({
                        "file_name": file_info["original_name"],
                        "file_id": file_info["file_id"],
                        "language": language,
                        "message": f"Analysis not yet supported for {language}. Coming soon!"
                    })
                    
            except Exception as e:
                print(f"⚠️ Failed to analyze {file_info['original_name']}: {e}")
                file_reports.append({
                    "file_name": file_info["original_name"],
                    "file_id": file_info["file_id"],
                    "error": str(e)
                })
        
        # Calculate overall metrics
        average_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        # Create comprehensive report
        analysis_report = {
            "submission_id": submission_id,
            "total_files_analyzed": len(file_reports),
            "files_with_errors": len([r for r in file_reports if "error" in r]),
            "average_overall_score": round(average_score, 2),
            "file_reports": file_reports,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Save report
        report_path = submission_dir / "code_analysis.json"
        with open(report_path, "w") as f:
            json.dump(analysis_report, f, indent=2)
        
        # Generate markdown reports for each file
        for i, report_data in enumerate(file_reports):
            if "error" not in report_data and "message" not in report_data:
                # Reconstruct report object for markdown generation
                try:
                    markdown_path = submission_dir / f"code_analysis_{report_data['file_id']}.md"
                    # For now, just save JSON version
                    # Full markdown generation would require reconstructing the dataclass
                except Exception as e:
                    print(f"⚠️ Markdown generation skipped: {e}")
        
        # Update submission
        submission["code_analysis_id"] = str(uuid.uuid4())
        submission["updated_at"] = datetime.now().isoformat()
        with open(metadata_path, "w") as f:
            json.dump(submission, f, indent=2)
        
        print(f"✅ Code analysis complete: Average score {average_score:.2f}/100")
        
        return {
            "success": True,
            "submission_id": submission_id,
            "report": analysis_report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")


@router.get("/submissions/{submission_id}/code-analysis", response_model=Dict[str, Any])
async def get_code_analysis(submission_id: str):
    """
    Get code analysis report for a submission
    
    Args:
        submission_id: Submission identifier
    
    Returns:
        Code analysis report data
    """
    try:
        report_path = SUBMISSIONS_DIR / submission_id / "code_analysis.json"
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Code analysis report not found. Run code analysis first."
            )
        
        with open(report_path, "r") as f:
            report = json.load(f)
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")


@router.get("/submissions/{submission_id}/ai-tools-results", response_model=Dict[str, Any])
async def get_ai_tools_results(submission_id: str):
    """
    Get AI tools results for a submission
    
    Args:
        submission_id: Submission identifier
    
    Returns:
        AI tools results data
    """
    try:
        report_path = SUBMISSIONS_DIR / submission_id / "ai_tools_results.json"
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail="AI tools results not found. Run AI tools analysis first."
            )
        
        with open(report_path, "r") as f:
            results = json.load(f)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve AI tools results: {str(e)}")


# ============================================================================
# COMPREHENSIVE ANALYSIS ENDPOINT
# ============================================================================

@router.post("/submissions/{submission_id}/analyze-all", response_model=Dict[str, Any])
async def analyze_all(
    submission_id: str,
    ai_tools: Optional[str] = Query(None, description="Comma-separated list of AI tools to run: ai-detector,plagiarism,humanizer,paraphraser,grammar")
):
    """
    Run both plagiarism detection and code analysis, plus selected AI tools
    
    Args:
        submission_id: Submission to analyze
        ai_tools: Optional comma-separated list of AI tools to run
    
    Returns:
        Combined analysis results including AI tool outputs
    """
    try:
        print(f"🚀 Running comprehensive analysis for submission: {submission_id}")
        if ai_tools:
            print(f"📊 AI Tools selected: {ai_tools}")
        
        results = {
            "submission_id": submission_id,
            "plagiarism_check": None,
            "code_analysis": None,
            "ai_tools_results": {},
            "errors": []
        }
        
        # Get submission to extract file content
        try:
            # Fetch from MongoDB
            db = get_database()
            print(f"📁 Fetching submission from MongoDB: {submission_id}")
            submission_doc = await db["submissions"].find_one({"submission_id": submission_id})
            
            if not submission_doc:
                raise HTTPException(status_code=404, detail="Submission not found")
            
            print(f"✅ Found submission with {len(submission_doc.get('files', []))} files")
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error fetching submission: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error fetching submission: {str(e)}")
        
        # Extract text from uploaded files for AI tools
        file_content = ""
        if submission_doc.get("files"):
            # Get first file content (you can modify to handle multiple files)
            first_file = submission_doc["files"][0]
            file_path = first_file.get("file_path", "")
            print(f"📄 Reading file: {file_path}")
            if os.path.exists(file_path):
                try:
                                        # Check if it's a PDF
                    if file_path.lower().endswith('.pdf'):
                        # Try to extract text from PDF using OCR
                        ocr = OCRExtractor()
                        file_content = ocr.extract_text(file_path)
                        print(f"✅ Extracted {len(file_content)} characters from PDF")
                    else:
                        # Read as text file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        print(f"✅ Read {len(file_content)} characters from file")
                except Exception as e:
                    print(f"❌ Error reading file: {str(e)}")
                    # Try reading first 2000 bytes as fallback
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_content = f.read(2000)
                        print(f"⚠️  Used fallback: read {len(file_content)} characters")
                    except:
                        file_content = ""
            else:
                print(f"⚠️  File does not exist: {file_path}")
        
        # Run selected AI tools
        if ai_tools and file_content:
            from services.plagiarism_detector import PlagiarismDetector
            from services.groq_ai_service import get_groq_ai_service
            
            print(f"🔧 Initializing AI services...")
            tool_list = [t.strip() for t in ai_tools.split(',')]
            detector = PlagiarismDetector()
            groq_service = get_groq_ai_service()
            
            for tool in tool_list:
                try:
                    if tool == 'ai-detector':
                        print(f"🤖 Running AI Detector...")
                        ai_result = detector.detect_ai_generated_code(file_content, "submission_file.py")
                        confidence = ai_result.get('confidence', 0)
                        if confidence > 1:
                            confidence = confidence / 100.0
                        results["ai_tools_results"]["ai_detector"] = {
                            "is_ai_generated": ai_result.get('is_ai_generated', False),
                            "confidence": round(confidence * 100, 2),
                            "confidence_level": ai_result.get('confidence_level', 'unknown'),
                            "explanation": ai_result.get('explanation', '')
                        }
                    
                    elif tool == 'plagiarism':
                        print(f"📋 Running FULL Plagiarism Check...")
                        try:
                            # Run the full plagiarism detection (same as the old system)
                            plagiarism_result = await check_plagiarism(submission_id, check_limit=50)
                            
                            # Extract the report from the result
                            report = plagiarism_result.get("report", {})
                            
                            # Clean up recommendations - split into separate readable points
                            raw_recommendations = report.get("recommendations", [])
                            clean_recommendations = []
                            
                            for rec in raw_recommendations:
                                # Remove markdown headers (###, ##, #)
                                cleaned = rec.replace('###', '').replace('##', '').replace('#', '')
                                # Remove bold markers
                                cleaned = cleaned.replace('**', '')
                                # Remove existing bullet points
                                cleaned = cleaned.replace('✅', '').replace('•', '').replace('*', '')
                                
                                # Split by common sentence delimiters that indicate separate points
                                # Look for numbered points (1. 2. 3.) or sentence endings
                                sentences = []
                                
                                # First, split by numbered points
                                import re
                                parts = re.split(r'(?:\d+\.\s+)', cleaned)
                                for part in parts:
                                    if part.strip():
                                        # Further split long paragraphs by sentence endings followed by capital letters
                                        sub_parts = re.split(r'\.(?=\s+[A-Z])', part)
                                        for sub in sub_parts:
                                            clean_text = sub.strip()
                                            # Clean up common labels
                                            clean_text = clean_text.replace('ASSESSMENT', '').replace('DETAILED FINDINGS', '')
                                            clean_text = clean_text.replace('REQUIRED ACTIONS', '').replace('BEST PRACTICES', '')
                                            clean_text = clean_text.replace('RECOMMENDED NEXT STEPS', '')
                                            clean_text = ' '.join(clean_text.split())  # Clean whitespace
                                            
                                            # Only add if it's meaningful (more than 20 chars and not just labels)
                                            if len(clean_text) > 20 and clean_text not in ['Given the results', 'The instructor may consider']:
                                                # Add period if it doesn't end with one
                                                if not clean_text.endswith('.'):
                                                    clean_text += '.'
                                                sentences.append(clean_text)
                                
                                clean_recommendations.extend(sentences)
                            
                            # Limit to max 8 most meaningful recommendations
                            clean_recommendations = clean_recommendations[:8]
                            
                            results["ai_tools_results"]["plagiarism"] = {
                                "success": True,
                                "overall_originality_score": report.get("overall_originality_score", 0),
                                "total_matches_found": report.get("total_matches_found", 0),
                                "similarity_matches": report.get("similarity_matches", []),
                                "flagged_sections": report.get("flagged_sections", []),
                                "risk_level": report.get("risk_level", "unknown"),
                                "recommendations": clean_recommendations,
                                "sources_checked": report.get("sources_checked", 0)
                            }
                            print(f"✅ Plagiarism check complete: {report.get('overall_originality_score')}% original")
                        except Exception as plag_err:
                            print(f"❌ Full plagiarism check failed: {str(plag_err)}")
                            # Fallback to quick AI detection if full check fails
                            plag_result = detector.detect_ai_generated_code(file_content, "submission_file.py")
                            confidence = plag_result.get('confidence', 0)
                            if confidence > 1:
                                confidence = confidence / 100.0
                            originality = (1.0 - confidence) * 100.0
                            
                            # Determine risk level based on originality
                            if originality >= 80:
                                risk_level = "low"
                            elif originality >= 60:
                                risk_level = "medium"
                            else:
                                risk_level = "high"
                            
                            results["ai_tools_results"]["plagiarism"] = {
                                "success": True,
                                "overall_originality_score": round(originality, 2),
                                "total_matches_found": 0,
                                "similarity_matches": [],
                                "flagged_sections": [],
                                "risk_level": risk_level,
                                "recommendations": [
                                    plag_result.get('explanation', 'AI detection analysis performed'),
                                    f"Originality Score: {round(originality, 2)}%",
                                    f"AI Confidence: {round(confidence * 100, 2)}%"
                                ],
                                "sources_checked": 0,
                                "note": "Full plagiarism check unavailable. Showing AI detection results only."
                            }
                    
                    elif tool == 'humanizer':
                        print(f"👤 Running AI Humanizer...")
                        humanize_result = groq_service.humanize_text(file_content[:2000], "professional")  # Limit length
                        results["ai_tools_results"]["humanizer"] = humanize_result
                    
                    elif tool == 'paraphraser':
                        print(f"✍️  Running Paraphraser...")
                        paraphrase_result = groq_service.paraphrase_text(file_content[:2000], "academic")
                        results["ai_tools_results"]["paraphraser"] = paraphrase_result
                    
                    elif tool == 'grammar':
                        print(f"📝 Running Grammar Checker...")
                        grammar_result = groq_service.check_grammar(file_content[:2000])
                        results["ai_tools_results"]["grammar"] = grammar_result
                        
                except Exception as e:
                    print(f"❌ AI tool '{tool}' failed: {str(e)}")
                    results["errors"].append(f"AI tool '{tool}' failed: {str(e)}")
                    results["ai_tools_results"][tool] = {"success": False, "error": str(e)}
        
        # Only run standard plagiarism check if NOT using AI tools (for backward compatibility)
        # If user selected AI tools, they control what runs
        if not ai_tools:
            try:
                plagiarism_result = await check_plagiarism(submission_id)
                results["plagiarism_check"] = {
                    "success": True,
                    "originality_score": plagiarism_result["report"]["overall_originality_score"],
                    "risk_level": plagiarism_result["report"]["risk_level"],
                    "matches_found": plagiarism_result["report"]["total_matches_found"]
                }
            except Exception as e:
                results["errors"].append(f"Plagiarism check failed: {str(e)}")
                results["plagiarism_check"] = {"success": False, "error": str(e)}
            
            # Run code analysis
            try:
                code_result = await analyze_code(submission_id)
                results["code_analysis"] = {
                    "success": True,
                    "average_score": code_result["report"]["average_overall_score"],
                    "files_analyzed": code_result["report"]["total_files_analyzed"]
                }
            except Exception as e:
                results["errors"].append(f"Code analysis failed: {str(e)}")
                results["code_analysis"] = {"success": False, "error": str(e)}
        
        print(f"✅ Comprehensive analysis complete")
        
        # Save AI tool results to file if any were run
        if results.get("ai_tools_results"):
            submission_dir = SUBMISSIONS_DIR / submission_id
            ai_results_path = submission_dir / "ai_tools_results.json"
            try:
                with open(ai_results_path, "w") as f:
                    json.dump(results["ai_tools_results"], f, indent=2)
                print(f"💾 Saved AI tool results to {ai_results_path}")
            except Exception as e:
                print(f"⚠️  Failed to save AI tool results: {str(e)}")
        
        return {
            "success": True,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Comprehensive analysis error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")


# ============================================================================
# REVIEW ENDPOINTS
# ============================================================================

@router.post("/reviews/create", response_model=Dict[str, Any])
async def create_review(
    submission_id: str = Form(...),
    reviewer_id: str = Form(...),
    reviewer_name: Optional[str] = Form(None),
    reviewer_type: str = Form(...),  # "ai", "peer", "instructor"
    is_anonymous: bool = Form(True)
):
    """
    Create a new review assignment
    
    Args:
        submission_id: Submission to review
        reviewer_id: Reviewer identifier
        reviewer_name: Reviewer name (optional for anonymous)
        reviewer_type: Type of reviewer
        is_anonymous: Whether review is anonymous
    
    Returns:
        Review assignment details
    """
    try:
        review_id = str(uuid.uuid4())
        
        review_data = {
            "review_id": review_id,
            "submission_id": submission_id,
            "reviewer_id": reviewer_id,
            "reviewer_name": None if is_anonymous else reviewer_name,
            "reviewer_type": reviewer_type,
            "status": "pending",
            "is_anonymous": is_anonymous,
            "assigned_at": datetime.now().isoformat(),
            "criteria_scores": None,
            "overall_score": None,
            "feedback": None
        }
        
        # Save review
        reviews_dir = SUBMISSIONS_DIR / submission_id / "reviews"
        reviews_dir.mkdir(exist_ok=True)
        
        review_path = reviews_dir / f"{review_id}.json"
        with open(review_path, "w") as f:
            json.dump(review_data, f, indent=2)
        
        return {
            "success": True,
            "review_id": review_id,
            "review": review_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")


@router.get("/reviews/submission/{submission_id}", response_model=List[Dict[str, Any]])
async def get_submission_reviews(submission_id: str):
    """
    Get all reviews for a submission
    
    Args:
        submission_id: Submission identifier
    
    Returns:
        List of reviews
    """
    try:
        reviews_dir = SUBMISSIONS_DIR / submission_id / "reviews"
        
        if not reviews_dir.exists():
            return []
        
        reviews = []
        for review_file in reviews_dir.glob("*.json"):
            with open(review_file, "r") as f:
                review = json.load(f)
                reviews.append(review)
        
        return reviews
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reviews: {str(e)}")


# ============================================================================
# DASHBOARD/ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard/student/{student_id}", response_model=Dict[str, Any])
async def get_student_dashboard(student_id: str):
    """
    Get dashboard summary for a student
    
    Args:
        student_id: Student identifier
    
    Returns:
        Dashboard data with submissions and statistics
    """
    try:
        submissions = await get_student_submissions(student_id)
        
        # Calculate statistics based on actual statuses
        total_submissions = len(submissions)
        submitted = len([s for s in submissions if s.get("status") == "submitted"])
        processing = len([s for s in submissions if s.get("status") == "processing"])
        completed = len([s for s in submissions if s.get("status") == "completed"])
        flagged = len([s for s in submissions if s.get("status") == "flagged"])
        under_review = len([s for s in submissions if s.get("status") in ["under_review", "processing"]])
        
        # Get all submissions (most recent first) for the list
        all_submissions = submissions
        
        dashboard = {
            "student_id": student_id,
            "student_name": submissions[0].get("student_name") if submissions else "Student",
            "total_submissions": total_submissions,
            "submissions_completed": completed,
            "submissions_under_review": under_review,
            "submissions_flagged": flagged,
            "recent_submissions": all_submissions,  # Return all submissions
            "statistics": {
                "total": total_submissions,
                "submitted": submitted,
                "processing": processing,
                "completed": completed,
                "under_review": under_review,
                "flagged": flagged
            }
        }
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_system_stats():
    """
    Get overall system statistics
    
    Returns:
        System-wide statistics
    """
    try:
        total_submissions = 0
        total_plagiarism_reports = 0
        total_code_analyses = 0
        
        for submission_dir in SUBMISSIONS_DIR.iterdir():
            if submission_dir.is_dir():
                total_submissions += 1
                
                if (submission_dir / "plagiarism_report.json").exists():
                    total_plagiarism_reports += 1
                
                if (submission_dir / "code_analysis.json").exists():
                    total_code_analyses += 1
        
        return {
            "total_submissions": total_submissions,
            "plagiarism_reports_generated": total_plagiarism_reports,
            "code_analyses_completed": total_code_analyses,
            "system_status": "operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.delete("/submissions/{submission_id}")
async def delete_submission(submission_id: str):
    """
    Delete a submission and all associated data
    
    Args:
        submission_id: Submission to delete
    
    Returns:
        Deletion confirmation
    """
    try:
        submission_dir = SUBMISSIONS_DIR / submission_id
        
        if not submission_dir.exists():
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Delete directory and all contents
        shutil.rmtree(submission_dir)
        
        return {
            "success": True,
            "message": f"Submission {submission_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete submission: {str(e)}")
