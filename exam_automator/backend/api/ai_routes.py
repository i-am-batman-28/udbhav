"""
AI Writing Tools API Routes
Endpoints for Paraphraser Grammar Checker AI Humanizer AI Detector Plagiarism Checker
All using HTTP API NO SDK NO MUTEX LOCKS
Direct service instantiation no global state no lazy init
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel

from services.groq_ai_service import get_groq_ai_service
from services.plagiarism_detector import PlagiarismDetector

router = APIRouter(prefix="/api/ai-tools", tags=["AI Writing Tools"])

class ParaphraseRequest(BaseModel):
    text: str
    style: str = "academic"

class GrammarCheckRequest(BaseModel):
    text: str

class HumanizeRequest(BaseModel):
    text: str
    tone: str = "natural"

class AIDetectionRequest(BaseModel):
    text: str
    submission_type: str = "writeup"

class TextResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/paraphrase", response_model=TextResponse)
async def paraphrase_text(request: ParaphraseRequest):
    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text must be at least 10 characters")
        
        groq_service = get_groq_ai_service()
        result = groq_service.paraphrase_text(request.text, style=request.style)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Paraphrasing failed'))
        
        return TextResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        return TextResponse(success=False, error=str(e))


@router.post("/grammar-check", response_model=TextResponse)
async def check_grammar(request: GrammarCheckRequest):
    try:
        if not request.text or len(request.text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Text must be at least 5 characters")
        
        groq_service = get_groq_ai_service()
        result = groq_service.check_grammar(request.text)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Grammar check failed'))
        
        return TextResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        return TextResponse(success=False, error=str(e))


@router.post("/humanize", response_model=TextResponse)
async def humanize_text(request: HumanizeRequest):
    try:
        if not request.text or len(request.text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Text must be at least 20 characters")
        
        groq_service = get_groq_ai_service()
        result = groq_service.humanize_text(request.text, tone=request.tone)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Humanization failed'))
        
        return TextResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        return TextResponse(success=False, error=str(e))


@router.post("/detect-ai", response_model=TextResponse)
async def detect_ai(request: AIDetectionRequest):
    try:
        if not request.text or len(request.text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Text must be at least 20 characters")
        
        detector = PlagiarismDetector()
        
        # Use detect_ai_generated_code for both code and text
        # It works for any content type
        ai_result = detector.detect_ai_generated_code(request.text, "user_submission.py")
        
        # Normalize confidence to 0-1 range if it's in 0-100 range
        confidence = ai_result.get('confidence', 0)
        if confidence > 1:
            confidence = confidence / 100.0
        
        # Determine confidence_level if not provided
        confidence_level = ai_result.get('confidence_level', 'unknown')
        if confidence_level == 'unknown':
            if confidence >= 0.8:
                confidence_level = 'high'
            elif confidence >= 0.5:
                confidence_level = 'medium'
            else:
                confidence_level = 'low'
        
        return TextResponse(
            success=True,
            data={
                'is_ai_generated': ai_result.get('is_ai_generated', False),
                'confidence': confidence,
                'confidence_level': confidence_level,
                'evidence': ai_result.get('evidence', ai_result.get('indicators', [])),
                'ai_tool_signature': ai_result.get('ai_tool_signature', 'unknown'),
                'explanation': ai_result.get('explanation', ''),
                'submission_type': request.submission_type
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return TextResponse(success=False, error=str(e))


@router.post("/check-plagiarism", response_model=TextResponse)
async def check_plagiarism(request: AIDetectionRequest):
    try:
        if not request.text or len(request.text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Text must be at least 20 characters")
        
        detector = PlagiarismDetector()
        
        # Use detect_ai_generated_code for all content (works for text and code)
        ai_result = detector.detect_ai_generated_code(request.text, "quick_check.py")
        
        # Normalize confidence to 0-1 range if it's in 0-100 range
        confidence = ai_result.get('confidence', 0)
        if confidence > 1:
            confidence = confidence / 100.0
        
        originality_score = 100.0 - (confidence * 100)
        
        return TextResponse(
            success=True,
            data={
                'originality_score': round(originality_score, 1),
                'ai_detected': ai_result['is_ai_generated'],
                'ai_confidence': round(confidence * 100, 2),  # Display as percentage
                'risk_level': 'high' if ai_result['is_ai_generated'] else 'low',
                'summary': f"{'AI-generated content detected' if ai_result['is_ai_generated'] else 'No AI-generated content detected'}. Originality score: {originality_score:.1f}%",
                'note': 'This is a quick check. Full plagiarism detection includes comparison with other submissions.'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return TextResponse(success=False, error=str(e))


@router.get("/health")
async def health_check():
    try:
        groq_service = get_groq_ai_service()
        groq_available = True
    except:
        groq_available = False
    
    try:
        detector = PlagiarismDetector()
        detector_available = True
    except:
        detector_available = False
    
    return {
        "status": "healthy",
        "services": {
            "groq_ai_service": groq_available,
            "plagiarism_detector": detector_available
        },
        "tools": {
            "paraphraser": groq_available,
            "grammar_checker": groq_available,
            "ai_humanizer": groq_available,
            "ai_detector": detector_available,
            "plagiarism_checker": detector_available
        },
        "api_type": "HTTP NO SDK NO MUTEX LOCKS"
    }
