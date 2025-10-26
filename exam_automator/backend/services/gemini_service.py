"""
Gemini AI Service - Powers AI Writing Tools
Implements: Paraphraser, Grammar Checker, AI Humanizer
Each tool uses dedicated, intelligent prompts for optimal results
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional
from dotenv import load_dotenv
import threading

load_dotenv()

# Global lock for thread-safe initialization
_gemini_lock = threading.Lock()
_gemini_configured = False


class GeminiAIService:
    """AI-powered writing assistance tools using Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini API with thread-safe singleton pattern"""
        global _gemini_configured
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Thread-safe configuration - only configure once globally
        with _gemini_lock:
            if not _gemini_configured:
                genai.configure(api_key=api_key)
                _gemini_configured = True
        
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Generation config for consistent, high-quality output
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,
        }
    
    def paraphrase_text(self, text: str, style: str = "academic") -> Dict[str, any]:
        """
        Paraphrase text while maintaining meaning and improving clarity
        
        Args:
            text: Original text to paraphrase
            style: Writing style - "academic", "casual", "formal", "simple"
            
        Returns:
            {
                'original': str,
                'paraphrased': str,
                'changes_summary': str,
                'style_applied': str
            }
        """
        
        # Dedicated paraphraser prompt - intelligent, context-aware
        prompt = f"""You are an expert writing assistant specializing in paraphrasing. Your task is to rewrite the following text while:

1. **Preserving the original meaning completely**
2. **Using different sentence structures and vocabulary**
3. **Maintaining the {style} writing style**
4. **Improving clarity and readability**
5. **Avoiding plagiarism by substantial rewording**

Guidelines:
- Change sentence structure significantly (don't just swap synonyms)
- Use varied vocabulary while keeping technical terms when necessary
- Maintain the same tone and formality level
- Keep the same length (±20%)
- Ensure natural flow and coherence

**Original Text:**
{text}

**Task:** Provide ONLY the paraphrased version without any explanations, prefixes, or formatting. Just return the rewritten text directly.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            paraphrased = response.text.strip()
            
            # Generate a summary of changes
            changes_prompt = f"""Briefly summarize (in 1-2 sentences) the key changes made when paraphrasing this text:

Original: {text[:200]}...
Paraphrased: {paraphrased[:200]}...

Provide a concise summary of structural and vocabulary changes."""

            changes_response = self.model.generate_content(changes_prompt)
            changes_summary = changes_response.text.strip()
            
            return {
                'success': True,
                'original': text,
                'paraphrased': paraphrased,
                'changes_summary': changes_summary,
                'style_applied': style,
                'original_length': len(text.split()),
                'paraphrased_length': len(paraphrased.split())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }
    
    def check_grammar(self, text: str) -> Dict[str, any]:
        """
        Check grammar and provide corrections with explanations
        
        Args:
            text: Text to check for grammar issues
            
        Returns:
            {
                'original': str,
                'corrected': str,
                'errors_found': int,
                'corrections': List[Dict],
                'overall_quality': str
            }
        """
        
        # Dedicated grammar checker prompt - detailed analysis
        prompt = f"""You are an expert grammar and writing quality checker. Analyze the following text for:

1. **Grammar errors** (subject-verb agreement, tenses, articles)
2. **Punctuation issues** (commas, periods, apostrophes)
3. **Spelling mistakes** (typos, wrong word usage)
4. **Style improvements** (clarity, conciseness, word choice)
5. **Sentence structure** (fragments, run-ons, awkward phrasing)

**Text to analyze:**
{text}

**Instructions:**
Provide your response in this exact JSON format (no markdown, no code blocks):
{{
    "corrected_text": "The fully corrected version of the text",
    "errors": [
        {{
            "type": "grammar/punctuation/spelling/style",
            "original": "the incorrect phrase",
            "corrected": "the corrected phrase",
            "explanation": "Brief explanation of the error",
            "severity": "low/medium/high"
        }}
    ],
    "overall_quality": "excellent/good/fair/needs improvement",
    "summary": "One sentence summary of overall writing quality"
}}

Return ONLY the JSON, nothing else."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    **self.generation_config,
                    'temperature': 0.3  # Lower temperature for more precise corrections
                }
            )
            
            # Parse the JSON response
            import json
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            return {
                'success': True,
                'original': text,
                'corrected': result.get('corrected_text', text),
                'errors_found': len(result.get('errors', [])),
                'corrections': result.get('errors', []),
                'overall_quality': result.get('overall_quality', 'unknown'),
                'summary': result.get('summary', 'Analysis complete'),
                'has_errors': len(result.get('errors', [])) > 0
            }
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return {
                'success': True,
                'original': text,
                'corrected': response.text.strip(),
                'errors_found': 0,
                'corrections': [],
                'overall_quality': 'unknown',
                'summary': 'Grammar check complete (detailed analysis unavailable)',
                'has_errors': False,
                'note': 'Simplified response due to parsing error'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }
    
    def humanize_text(self, text: str, tone: str = "natural") -> Dict[str, any]:
        """
        Make AI-generated text sound more human and natural
        
        Args:
            text: AI-generated text to humanize
            tone: Desired tone - "natural", "conversational", "professional", "friendly"
            
        Returns:
            {
                'original': str,
                'humanized': str,
                'changes_made': List[str],
                'tone_applied': str
            }
        """
        
        # Dedicated humanizer prompt - removes AI patterns
        prompt = f"""You are an expert at making AI-generated text sound more human and natural. Transform the following text to:

1. **Remove AI telltale signs:**
   - Overly formal or perfect language
   - Repetitive sentence structures
   - Generic phrases like "delve into", "tapestry", "multifaceted"
   - Excessive use of transition words
   - Perfect grammar that sounds robotic

2. **Add human elements:**
   - Natural variation in sentence length
   - Conversational flow with contractions (when appropriate)
   - Occasional minor imperfections that humans make
   - Personal voice and natural phrasing
   - Varied vocabulary without being overly sophisticated

3. **Maintain {tone} tone while being authentic**

4. **Keep the same core message and key information**

**Text to humanize:**
{text}

**Task:** Provide ONLY the humanized version. No explanations, no markdown, just the rewritten text that sounds naturally human-written.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            humanized = response.text.strip()
            
            # Analyze what changes were made
            analysis_prompt = f"""List 3-5 key changes made to humanize this text (be specific and concise):

Original: {text[:200]}...
Humanized: {humanized[:200]}...

Provide bullet points of the main improvements."""

            analysis_response = self.model.generate_content(analysis_prompt)
            changes_text = analysis_response.text.strip()
            
            # Parse changes into list
            changes_made = [
                line.strip('- •*').strip() 
                for line in changes_text.split('\n') 
                if line.strip() and not line.strip().startswith('Changes')
            ][:5]
            
            return {
                'success': True,
                'original': text,
                'humanized': humanized,
                'changes_made': changes_made,
                'tone_applied': tone,
                'ai_score_before': self._estimate_ai_score(text),
                'ai_score_after': self._estimate_ai_score(humanized)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }
    
    def _estimate_ai_score(self, text: str) -> float:
        """
        Estimate likelihood of text being AI-generated (0-100)
        Quick heuristic based on common AI patterns
        """
        score = 0
        text_lower = text.lower()
        
        # AI red flags
        ai_phrases = [
            'delve into', 'multifaceted', 'tapestry', 'realm', 'landscape',
            'it is important to note', 'in conclusion', 'furthermore',
            'additionally', 'moreover', 'consequently'
        ]
        
        for phrase in ai_phrases:
            if phrase in text_lower:
                score += 15
        
        # Perfect punctuation (AI tends to be perfect)
        sentences = text.split('.')
        if len(sentences) > 3:
            perfect_sentences = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
            if perfect_sentences / len(sentences) > 0.95:
                score += 20
        
        # Very consistent sentence length (AI pattern)
        words_per_sentence = [len(s.split()) for s in sentences if s.strip()]
        if words_per_sentence:
            import statistics
            if len(words_per_sentence) > 3:
                std_dev = statistics.stdev(words_per_sentence)
                if std_dev < 5:  # Very consistent
                    score += 15
        
        return min(score, 100)


# Singleton instance with thread safety
_gemini_service = None
_gemini_service_lock = threading.Lock()


def get_gemini_service() -> GeminiAIService:
    """Get or create the Gemini AI service instance (thread-safe singleton)"""
    global _gemini_service
    
    if _gemini_service is None:
        with _gemini_service_lock:
            # Double-check locking pattern
            if _gemini_service is None:
                _gemini_service = GeminiAIService()
    
    return _gemini_service


# Test function
if __name__ == "__main__":
    print("🧪 Testing Gemini AI Service\n")
    
    service = get_gemini_service()
    
    # Test 1: Paraphraser
    print("=" * 60)
    print("TEST 1: PARAPHRASER")
    print("=" * 60)
    test_text = """
    Artificial intelligence has revolutionized the way we process information.
    Machine learning algorithms can now analyze vast amounts of data and identify
    patterns that would be impossible for humans to detect manually.
    """
    
    result = service.paraphrase_text(test_text.strip(), style="academic")
    if result['success']:
        print(f"✅ Original ({result['original_length']} words):")
        print(result['original'])
        print(f"\n✅ Paraphrased ({result['paraphrased_length']} words):")
        print(result['paraphrased'])
        print(f"\n📝 Changes: {result['changes_summary']}\n")
    else:
        print(f"❌ Error: {result['error']}\n")
    
    # Test 2: Grammar Checker
    print("=" * 60)
    print("TEST 2: GRAMMAR CHECKER")
    print("=" * 60)
    test_text = """
    Their are many student's who doesnt understand grammer rules.
    Its important to learn this, because you writing will improve alot.
    """
    
    result = service.check_grammar(test_text.strip())
    if result['success']:
        print(f"✅ Original:")
        print(result['original'])
        print(f"\n✅ Corrected:")
        print(result['corrected'])
        print(f"\n🔍 Errors found: {result['errors_found']}")
        print(f"📊 Quality: {result['overall_quality']}")
        for i, error in enumerate(result['corrections'][:3], 1):
            print(f"\n  {i}. {error['type'].upper()}: '{error['original']}' → '{error['corrected']}'")
            print(f"     {error['explanation']}")
    else:
        print(f"❌ Error: {result['error']}\n")
    
    # Test 3: AI Humanizer
    print("\n" + "=" * 60)
    print("TEST 3: AI HUMANIZER")
    print("=" * 60)
    test_text = """
    It is important to note that machine learning algorithms have revolutionized
    the multifaceted landscape of data analysis. Furthermore, these sophisticated
    systems delve into the intricate tapestry of patterns within vast datasets.
    Moreover, the realm of artificial intelligence continues to expand exponentially.
    """
    
    result = service.humanize_text(test_text.strip(), tone="natural")
    if result['success']:
        print(f"✅ Original (AI Score: {result['ai_score_before']:.0f}%):")
        print(result['original'])
        print(f"\n✅ Humanized (AI Score: {result['ai_score_after']:.0f}%):")
        print(result['humanized'])
        print(f"\n🔄 Key changes:")
        for change in result['changes_made']:
            print(f"  • {change}")
    else:
        print(f"❌ Error: {result['error']}\n")
    
    print("\n" + "=" * 60)
    print("✅ All tests complete!")
    print("=" * 60)

