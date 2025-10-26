"""
Intelligent Recommendations Generator
Uses Groq API (HTTP) to generate real-time, context-aware recommendations
based on actual plagiarism findings - NO SDK, NO MUTEX LOCKS!
"""

import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class IntelligentRecommendationGenerator:
    """Generate intelligent, context-aware recommendations using Groq API (HTTP)"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.model = "llama-3.3-70b-versatile"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def _call_groq_api(self, messages: List[Dict], temperature: float = 0.7) -> Dict:
        """Make direct HTTP call to Groq API (avoids SDK mutex issues)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def generate_recommendations(
        self,
        originality_score: float,
        matches: List[Dict[str, Any]],
        submission_type: str,
        student_name: str
    ) -> str:
        """
        Generate intelligent recommendations based on actual findings
        
        Args:
            originality_score: 0-100, higher is more original
            matches: List of similarity matches with details
            submission_type: "code", "writeup", or "mixed"
            student_name: Name of the student
            
        Returns:
            Formatted recommendation text
        """
        
        # Prepare findings summary
        findings_summary = self._prepare_findings_summary(
            originality_score, matches, submission_type
        )
        
        # Generate recommendations using Groq
        prompt = self._create_recommendation_prompt(
            findings_summary, student_name, submission_type
        )
        
        try:
            response = self._call_groq_api(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert academic integrity advisor helping instructors "
                            "understand plagiarism detection results. Generate clear, actionable, "
                            "professional recommendations based on the findings. Be constructive, "
                            "fair, and educational. Format using markdown with clear sections. "
                            "NO EMOJIS. Use professional academic language."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )
            
            recommendations = response['choices'][0]['message']['content']
            return recommendations.strip()
            
        except Exception as e:
            print(f"Error generating intelligent recommendations: {e}")
            return self._generate_fallback_recommendations(
                originality_score, matches, submission_type
            )
    
    def _prepare_findings_summary(
        self,
        originality_score: float,
        matches: List[Dict[str, Any]],
        submission_type: str
    ) -> str:
        """Prepare a detailed summary of findings for the LLM"""
        
        summary = f"**Originality Score**: {originality_score:.1f}%\n"
        summary += f"**Submission Type**: {submission_type}\n"
        summary += f"**Total Matches**: {len(matches)}\n\n"
        
        if not matches:
            summary += "No significant similarity matches detected.\n"
            return summary
        
        # Categorize matches
        ai_generated = [m for m in matches if m.get('match_type') == 'ai_generated']
        internal_copies = [m for m in matches if m.get('match_type') == 'internal_copy']
        exact_matches = [m for m in matches if m.get('match_type') == 'exact']
        paraphrased = [m for m in matches if m.get('match_type') == 'paraphrased']
        
        # Add detailed findings
        if ai_generated:
            summary += f"**AI-Generated Content**: {len(ai_generated)} detections\n"
            for match in ai_generated[:3]:  # Top 3
                summary += f"  - File: {match.get('submission_id', 'Unknown')}\n"
                summary += f"    Confidence: {match.get('confidence', 0)*100:.1f}%\n"
                if match.get('matching_sections'):
                    sections = match['matching_sections'][:2]
                    for section in sections:
                        summary += f"    Sample: {section.get('source', '')[:100]}...\n"
            summary += "\n"
        
        if internal_copies:
            summary += f"**Internal Duplication**: {len(internal_copies)} matches\n"
            for match in internal_copies[:3]:
                summary += f"  - Similarity: {match.get('similarity_percentage', 0):.1f}%\n"
                summary += f"    With: {match.get('submission_id', 'Unknown')}\n"
                if match.get('matching_sections'):
                    section = match['matching_sections'][0]
                    summary += f"    Sample: {section.get('source', '')[:100]}...\n"
            summary += "\n"
        
        if exact_matches:
            summary += f"**Exact Matches**: {len(exact_matches)} found\n"
            for match in exact_matches[:2]:
                if match.get('matching_sections'):
                    section = match['matching_sections'][0]
                    summary += f"  - Exact text: {section.get('source', '')[:150]}...\n"
            summary += "\n"
        
        if paraphrased:
            summary += f"**Paraphrased Content**: {len(paraphrased)} instances\n"
            for match in paraphrased[:2]:
                summary += f"  - Similarity: {match.get('similarity_percentage', 0):.1f}%\n"
            summary += "\n"
        
        return summary
    
    def _create_recommendation_prompt(
        self,
        findings_summary: str,
        student_name: str,
        submission_type: str
    ) -> str:
        """Create a detailed prompt for the LLM"""
        
        return f"""Analyze the following plagiarism detection results and provide professional, actionable recommendations for the instructor.

{findings_summary}

**Student**: {student_name}

Please provide:

1. **ASSESSMENT**: A clear, professional assessment of the severity (use terms like EXCELLENT ORIGINALITY, MINOR CONCERNS, MODERATE RISK, HIGH RISK, or CRITICAL)

2. **DETAILED FINDINGS**: Break down what was detected by category (AI-Generated, Internal Duplication, Exact Matches, Paraphrasing). For each category with findings:
   - Explain what it means in context
   - Cite specific examples from the findings
   - Note confidence levels and severity

3. **REQUIRED ACTIONS**: Numbered list of specific, actionable steps the instructor should take. Be specific to the actual findings, not generic templates.

4. **BEST PRACTICES**: Provide 3-4 contextual best practices relevant to this specific case and submission type ({submission_type}).

5. **RECOMMENDED NEXT STEPS**: If the originality score is concerning, provide a clear 5-step action plan for addressing the situation.

**Important**: 
- Be specific to the actual findings provided, not generic
- NO EMOJIS
- Use professional academic language
- Be constructive and educational
- Consider that similar code/algorithms can be acceptable if independently implemented
- Balance fairness with academic integrity
- Format with clear markdown sections
"""
    
    def _generate_fallback_recommendations(
        self,
        originality_score: float,
        matches: List[Dict[str, Any]],
        submission_type: str
    ) -> str:
        """Generate basic recommendations if LLM fails"""
        
        recommendations = []
        
        # Overall assessment
        if originality_score >= 90:
            recommendations.append("**ASSESSMENT: EXCELLENT ORIGINALITY**\n")
            recommendations.append("Content demonstrates strong original work with minimal integrity concerns.\n")
        elif originality_score >= 70:
            recommendations.append("**ASSESSMENT: MINOR CONCERNS**\n")
            recommendations.append("Some similarities detected that warrant further review.\n")
        elif originality_score >= 50:
            recommendations.append("**ASSESSMENT: MODERATE RISK**\n")
            recommendations.append("Significant similarities found. Manual review and student interview required.\n")
        else:
            recommendations.append("**ASSESSMENT: HIGH RISK**\n")
            recommendations.append("Substantial plagiarism indicators detected. Immediate investigation recommended.\n")
        
        # Add basic match counts
        if matches:
            ai_count = len([m for m in matches if m.get('match_type') == 'ai_generated'])
            if ai_count > 0:
                recommendations.append(f"\n**AI-GENERATED CONTENT DETECTED**: {ai_count} detection(s)\n")
            
            internal_count = len([m for m in matches if m.get('match_type') == 'internal_copy'])
            if internal_count > 0:
                recommendations.append(f"**INTERNAL DUPLICATION**: {internal_count} match(es)\n")
        
        recommendations.append("\n**Note**: Enhanced recommendations temporarily unavailable. Please review findings manually.\n")
        
        return "".join(recommendations)


# Singleton instance
_recommendation_generator = None

def get_recommendation_generator() -> IntelligentRecommendationGenerator:
    """Get or create the recommendation generator instance"""
    global _recommendation_generator
    if _recommendation_generator is None:
        _recommendation_generator = IntelligentRecommendationGenerator()
    return _recommendation_generator
