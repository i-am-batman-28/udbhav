"""
Groq AI Service - Powers AI Writing Tools (FAST & NO MUTEX ISSUES!)
Implements: Paraphraser, Grammar Checker, AI Humanizer
Uses direct HTTP requests to Groq API - NO SDK to avoid mutex locks
"""

import os
import requests
from typing import Dict, List
from dotenv import load_dotenv
import re

load_dotenv()


class GroqAIService:
    """AI-powered writing assistance tools using Groq (Fast & Reliable)"""
    
    def __init__(self):
        """Initialize Groq API with direct HTTP calls"""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _call_groq_api(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Make direct HTTP call to Groq API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def paraphrase_text(self, text: str, style: str = "academic") -> Dict:
        """
        Paraphrase text while maintaining meaning
        
        Args:
            text: Original text to paraphrase
            style: Writing style - "academic", "casual", "formal", "simple"
            
        Returns:
            {
                'success': bool,
                'original': str,
                'paraphrased': str,
                'changes_summary': str,
                'style_applied': str,
                'word_count_original': int,
                'word_count_paraphrased': int
            }
        """
        
        style_prompts = {
            "academic": "scholarly and precise while maintaining clarity",
            "casual": "conversational and easy to understand",
            "formal": "professional and polished",
            "simple": "clear and straightforward for general audiences"
        }
        
        style_desc = style_prompts.get(style, style_prompts["academic"])
        
        prompt = f"""Paraphrase the following text while maintaining its core meaning and key information.

Style: Make it {style_desc}.

Original text:
{text}

Provide ONLY the paraphrased version. Do not add explanations, introductions, or meta-commentary. Just output the paraphrased text directly."""

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert writing assistant. Paraphrase text while preserving meaning. Output ONLY the paraphrased text, nothing else."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            paraphrased = self._call_groq_api(messages, temperature=0.7, max_tokens=2000).strip()
            
            # Calculate changes
            original_words = len(text.split())
            paraphrased_words = len(paraphrased.split())
            
            return {
                'success': True,
                'original': text,
                'paraphrased': paraphrased,
                'changes_summary': f"Text rewritten in {style} style",
                'style_applied': style,
                'word_count_original': original_words,
                'word_count_paraphrased': paraphrased_words
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }
    
    def check_grammar(self, text: str) -> Dict:
        """
        Check and correct grammar errors
        
        Args:
            text: Text to check for grammar errors
            
        Returns:
            {
                'success': bool,
                'original': str,
                'corrected': str,
                'errors_found': int,
                'error_count': int,
                'corrections': List[Dict],
                'overall_quality': str
            }
        """
        
        prompt = f"""Analyze this text for grammar, spelling, and punctuation errors. Provide corrections.

Text:
{text}

Respond in this EXACT format:

CORRECTED TEXT:
[Write the fully corrected version here]

ERRORS FOUND:
1. [Type] "[original phrase]" → "[corrected phrase]" - [Brief explanation]
2. [Type] "[original phrase]" → "[corrected phrase]" - [Brief explanation]
[Continue numbering if more errors]

QUALITY: [excellent/good/needs improvement/poor]"""

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert grammar checker. Identify and correct all grammar, spelling, and punctuation errors."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            result = self._call_groq_api(messages, temperature=0.3, max_tokens=2000)
            
            # Parse the response
            corrected_match = re.search(r'CORRECTED TEXT:\s*(.+?)(?=ERRORS FOUND:|$)', result, re.DOTALL)
            errors_match = re.search(r'ERRORS FOUND:\s*(.+?)(?=QUALITY:|$)', result, re.DOTALL)
            quality_match = re.search(r'QUALITY:\s*(.+?)$', result, re.DOTALL)
            
            corrected = corrected_match.group(1).strip() if corrected_match else text
            errors_text = errors_match.group(1).strip() if errors_match else ""
            quality = quality_match.group(1).strip().lower() if quality_match else "unknown"
            
            # Parse individual errors
            corrections = []
            if errors_text:
                error_lines = [line.strip() for line in errors_text.split('\n') if line.strip() and re.match(r'^\d+\.', line.strip())]
                for line in error_lines:
                    # Parse: 1. [Type] "original" → "corrected" - explanation
                    match = re.match(r'\d+\.\s*\[([^\]]+)\]\s*"([^"]+)"\s*→\s*"([^"]+)"\s*-\s*(.+)', line)
                    if match:
                        corrections.append({
                            'type': match.group(1),
                            'original': match.group(2),
                            'corrected': match.group(3),
                            'explanation': match.group(4)
                        })
            
            error_count = len(corrections)
            
            return {
                'success': True,
                'original': text,
                'corrected': corrected,
                'errors_found': error_count,
                'error_count': error_count,
                'corrections': corrections,
                'overall_quality': quality
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }
    
    def humanize_text(self, text: str, tone: str = "natural") -> Dict:
        """
        Convert AI-sounding text to more human-like writing
        
        Args:
            text: Text to humanize (typically AI-generated)
            tone: Desired tone - "natural", "casual", "conversational", "personal"
            
        Returns:
            {
                'success': bool,
                'original': str,
                'humanized': str,
                'ai_score_before': float (0-100),
                'ai_score_after': float (0-100),
                'changes_made': List[str],
                'tone_applied': str
            }
        """
        
        prompt = f"""Transform this text to sound more human and natural. Remove AI-typical patterns like:
- Overly formal language ("it is important to note", "furthermore", "moreover")
- Complex vocabulary where simpler words work better
- Perfect grammar that sounds robotic
- Lack of contractions
- Absence of personal voice

Make it sound like a real person wrote it naturally. Use a {tone} tone.

Text:
{text}

Respond in this EXACT format:

HUMANIZED TEXT:
[Write the humanized version here]

AI SCORE BEFORE: [0-100]
AI SCORE AFTER: [0-100]

KEY CHANGES:
- [Change 1]
- [Change 2]
- [Change 3]"""

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert at making AI-generated text sound human. Remove robotic patterns and add natural voice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            result = self._call_groq_api(messages, temperature=0.8, max_tokens=2000)
            
            # Parse the response
            humanized_match = re.search(r'HUMANIZED TEXT:\s*(.+?)(?=AI SCORE BEFORE:|$)', result, re.DOTALL)
            before_match = re.search(r'AI SCORE BEFORE:\s*(\d+)', result)
            after_match = re.search(r'AI SCORE AFTER:\s*(\d+)', result)
            changes_match = re.search(r'KEY CHANGES:\s*(.+?)$', result, re.DOTALL)
            
            humanized = humanized_match.group(1).strip() if humanized_match else text
            ai_score_before = float(before_match.group(1)) if before_match else 80.0
            ai_score_after = float(after_match.group(1)) if after_match else 20.0
            
            # Parse changes
            changes = []
            if changes_match:
                changes_text = changes_match.group(1).strip()
                changes = [line.strip('- ').strip() for line in changes_text.split('\n') if line.strip().startswith('-')]
            
            return {
                'success': True,
                'original': text,
                'humanized': humanized,
                'ai_score_before': ai_score_before,
                'ai_score_after': ai_score_after,
                'original_ai_score': ai_score_before,
                'humanized_ai_score': ai_score_after,
                'changes_made': changes,
                'tone_applied': tone
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }


# Singleton instance (no threading needed with HTTP requests)
_groq_ai_service = None


def get_groq_ai_service() -> GroqAIService:
    """Get or create the Groq AI service instance (simple singleton)"""
    global _groq_ai_service
    
    if _groq_ai_service is None:
        _groq_ai_service = GroqAIService()
    
    return _groq_ai_service


# Test function
if __name__ == "__main__":
    print("🧪 Testing Groq AI Service\n")
    
    service = get_groq_ai_service()
    
    # Test 1: Paraphraser
    print("=" * 60)
    print("TEST 1: PARAPHRASER")
    print("=" * 60)
    result = service.paraphrase_text(
        "Machine learning is revolutionizing data analysis.",
        style="academic"
    )
    if result['success']:
        print(f"✅ Original: {result['original']}")
        print(f"✅ Paraphrased: {result['paraphrased']}")
        print(f"📝 Style: {result['style_applied']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Test 2: Grammar Checker
    print("\n" + "=" * 60)
    print("TEST 2: GRAMMAR CHECKER")
    print("=" * 60)
    result = service.check_grammar("Their are many errors in this sentance and its important.")
    if result['success']:
        print(f"✅ Original: {result['original']}")
        print(f"✅ Corrected: {result['corrected']}")
        print(f"🔍 Errors found: {result['error_count']}")
        for i, error in enumerate(result['corrections'][:3], 1):
            print(f"  {i}. [{error['type']}] '{error['original']}' → '{error['corrected']}'")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Test 3: AI Humanizer
    print("\n" + "=" * 60)
    print("TEST 3: AI HUMANIZER")
    print("=" * 60)
    result = service.humanize_text(
        "It is important to note that artificial intelligence has revolutionized the multifaceted landscape.",
        tone="casual"
    )
    if result['success']:
        print(f"✅ Original (AI: {result['ai_score_before']:.0f}%): {result['original']}")
        print(f"✅ Humanized (AI: {result['ai_score_after']:.0f}%): {result['humanized']}")
        print(f"🔄 Changes: {', '.join(result['changes_made'][:2])}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests complete!")
    print("=" * 60)
