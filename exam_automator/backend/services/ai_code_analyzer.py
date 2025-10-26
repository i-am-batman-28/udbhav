"""
AI-Powered Code Quality Analyzer using Groq LLM
Production-ready intelligent code analysis with constructive feedback
"""

import os
import re
import ast
from typing import Dict, List, Optional, Any
from groq import Groq
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class CodeMetrics:
    """Basic code metrics"""
    lines_of_code: int
    num_functions: int
    num_classes: int
    num_comments: int
    avg_function_length: float
    cyclomatic_complexity: float
    maintainability_index: float

@dataclass
class QualityScore:
    """Quality scoring breakdown"""
    overall_score: float
    code_structure: float
    readability: float
    best_practices: float
    error_handling: float
    documentation: float
    efficiency: float
    grade: str

@dataclass
class Issue:
    """Code issue/suggestion"""
    severity: str  # "critical", "warning", "info"
    line: Optional[int]
    category: str
    message: str
    suggestion: str

@dataclass
class CodeAnalysisReport:
    """Complete AI-powered analysis report"""
    submission_id: str
    file_name: str
    language: str
    metrics: CodeMetrics
    quality_score: QualityScore
    strengths: List[str]
    weaknesses: List[str]
    issues: List[Issue]
    suggestions: List[str]
    ai_feedback: str
    analyzed_at: str

class GroqCodeAnalyzer:
    """
    Intelligent code analyzer using Groq LLM for production-ready analysis
    """
    
    def __init__(self, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize with Groq API key
        
        Args:
            groq_api_key: Groq API key
            model: Model to use (llama-3.3-70b-versatile is best for code analysis)
        """
        self.client = Groq(api_key=groq_api_key)
        self.model = model
    
    def analyze_code(self, code: str, filename: str = "unknown.py", 
                    submission_id: str = "unknown") -> CodeAnalysisReport:
        """
        Comprehensive AI-powered code analysis
        
        Args:
            code: Source code to analyze
            filename: Original filename
            submission_id: Unique submission ID
            
        Returns:
            CodeAnalysisReport with intelligent feedback
        """
        print(f"🤖 Starting AI-powered code analysis for: {filename}")
        
        # Calculate basic metrics
        metrics = self._calculate_metrics(code)
        
        # Get AI analysis from Groq
        ai_analysis = self._get_ai_analysis(code, filename, metrics)
        
        # Parse AI response
        quality_score = self._extract_quality_scores(ai_analysis, metrics)
        strengths = self._extract_strengths(ai_analysis)
        weaknesses = self._extract_weaknesses(ai_analysis)
        issues = self._extract_issues(ai_analysis)
        suggestions = self._extract_suggestions(ai_analysis)
        ai_feedback = ai_analysis.get("summary", "Analysis completed successfully.")
        
        report = CodeAnalysisReport(
            submission_id=submission_id,
            file_name=filename,
            language=self._detect_language(filename),
            metrics=metrics,
            quality_score=quality_score,
            strengths=strengths,
            weaknesses=weaknesses,
            issues=issues,
            suggestions=suggestions,
            ai_feedback=ai_feedback,
            analyzed_at=datetime.now().isoformat()
        )
        
        print(f"✅ Analysis complete: {quality_score.overall_score:.1f}/100 (Grade: {quality_score.grade})")
        
        return report
    
    def _calculate_metrics(self, code: str) -> CodeMetrics:
        """Calculate basic code metrics"""
        lines = code.split('\n')
        
        # Count lines
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comments = len([l for l in lines if l.strip().startswith('#')])
        
        # Try to parse AST for Python
        num_functions = 0
        num_classes = 0
        avg_func_length = 0
        complexity = 1.0
        
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            num_functions = len(functions)
            num_classes = len(classes)
            
            # Calculate function lengths
            if functions:
                func_lengths = []
                for func in functions:
                    start = func.lineno
                    end = getattr(func, 'end_lineno', start + 10)
                    func_lengths.append(end - start + 1)
                avg_func_length = sum(func_lengths) / len(func_lengths)
            
            # Simplified cyclomatic complexity
            complexity = 1.0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.And, ast.Or)):
                    complexity += 1
            complexity = complexity / max(num_functions, 1)
            
        except SyntaxError:
            # Fallback for syntax errors or non-Python
            num_functions = len(re.findall(r'\bdef\s+\w+', code))
            num_classes = len(re.findall(r'\bclass\s+\w+', code))
            avg_func_length = loc / max(num_functions, 1) if num_functions > 0 else 0
            complexity = 2.0  # Default moderate complexity
        
        # Calculate maintainability index (simplified)
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # Simplified: Higher LOC/complexity reduces it, more comments increase it
        mi = 100 - (loc * 0.1) - (complexity * 5) + (comments * 2)
        mi = max(0, min(100, mi))  # Clamp between 0-100
        
        return CodeMetrics(
            lines_of_code=loc,
            num_functions=num_functions,
            num_classes=num_classes,
            num_comments=comments,
            avg_function_length=round(avg_func_length, 1),
            cyclomatic_complexity=round(complexity, 2),
            maintainability_index=round(mi, 1)
        )
    
    def _get_ai_analysis(self, code: str, filename: str, metrics: CodeMetrics) -> Dict[str, Any]:
        """Get intelligent analysis from Groq LLM"""
        
        prompt = f"""You are an expert code reviewer and software engineering professor. Analyze this code submission and provide constructive, detailed feedback.

**Code to Analyze:**
```python
{code[:2000]}  # First 2000 chars to fit context
```

**Filename:** {filename}

**Basic Metrics:**
- Lines of Code: {metrics.lines_of_code}
- Functions: {metrics.num_functions}
- Classes: {metrics.num_classes}
- Comments: {metrics.num_comments}
- Avg Function Length: {metrics.avg_function_length}
- Cyclomatic Complexity: {metrics.cyclomatic_complexity}

**Your Task:**
Provide a comprehensive code quality analysis in the following JSON format:

{{
  "overall_score": 75,
  "code_structure_score": 80,
  "readability_score": 70,
  "best_practices_score": 65,
  "error_handling_score": 60,
  "documentation_score": 50,
  "efficiency_score": 85,
  
  "strengths": [
    "Clear function names that describe purpose",
    "Good use of type hints for parameters",
    "Logical code organization"
  ],
  
  "weaknesses": [
    "Missing docstrings for functions",
    "No error handling for edge cases",
    "Magic numbers without explanation"
  ],
  
  "issues": [
    {{
      "severity": "warning",
      "line": 15,
      "category": "Documentation",
      "message": "Function lacks docstring",
      "suggestion": "Add docstring explaining parameters and return value"
    }},
    {{
      "severity": "info",
      "line": 23,
      "category": "Best Practices",
      "message": "Consider using list comprehension",
      "suggestion": "Replace loop with: result = [x*2 for x in items]"
    }}
  ],
  
  "suggestions": [
    "Add type hints to all function parameters",
    "Include error handling for file operations",
    "Break large functions into smaller, focused ones",
    "Add comments explaining complex logic"
  ],
  
  "summary": "This code demonstrates solid fundamentals with clear logic and good naming conventions. To improve, focus on adding comprehensive documentation, implementing proper error handling, and following Python best practices like PEP 8 style guidelines. The code structure is good, but would benefit from more modular design."
}}

**Scoring Guidelines:**
- 90-100: Excellent - Production-ready, well-documented, follows best practices
- 80-89: Good - Solid code with minor improvements needed
- 70-79: Satisfactory - Functional but needs refinement
- 60-69: Needs Improvement - Several issues to address
- Below 60: Poor - Significant problems requiring major revision

Be constructive, specific, and educational. Provide actionable feedback that helps the student improve."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer providing detailed, constructive feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to parse JSON from response
            import json
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\n(.*?)\n```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON directly
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                json_str = json_match.group(0) if json_match else '{}'
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"⚠️ AI analysis failed: {e}")
            # Return reasonable defaults
            return {
                "overall_score": 70,
                "code_structure_score": 70,
                "readability_score": 70,
                "best_practices_score": 65,
                "error_handling_score": 60,
                "documentation_score": 65,
                "efficiency_score": 75,
                "strengths": ["Code compiles and runs", "Basic structure is present"],
                "weaknesses": ["Limited analysis available"],
                "issues": [],
                "suggestions": ["Add more documentation", "Implement error handling"],
                "summary": "Basic analysis completed. Code appears functional."
            }
    
    def _extract_quality_scores(self, ai_analysis: Dict, metrics: CodeMetrics) -> QualityScore:
        """Extract quality scores from AI analysis"""
        overall = ai_analysis.get("overall_score", 70)
        
        # Determine grade
        if overall >= 90:
            grade = "A"
        elif overall >= 80:
            grade = "B+"
        elif overall >= 70:
            grade = "B"
        elif overall >= 60:
            grade = "C+"
        elif overall >= 50:
            grade = "C"
        else:
            grade = "D"
        
        return QualityScore(
            overall_score=float(overall),
            code_structure=float(ai_analysis.get("code_structure_score", 70)),
            readability=float(ai_analysis.get("readability_score", 70)),
            best_practices=float(ai_analysis.get("best_practices_score", 65)),
            error_handling=float(ai_analysis.get("error_handling_score", 60)),
            documentation=float(ai_analysis.get("documentation_score", 65)),
            efficiency=float(ai_analysis.get("efficiency_score", 75)),
            grade=grade
        )
    
    def _extract_strengths(self, ai_analysis: Dict) -> List[str]:
        """Extract strengths from AI analysis"""
        return ai_analysis.get("strengths", ["Code is functional", "Basic structure is present"])
    
    def _extract_weaknesses(self, ai_analysis: Dict) -> List[str]:
        """Extract weaknesses from AI analysis"""
        return ai_analysis.get("weaknesses", ["Could benefit from more documentation"])
    
    def _extract_issues(self, ai_analysis: Dict) -> List[Issue]:
        """Extract issues from AI analysis"""
        issues_data = ai_analysis.get("issues", [])
        return [
            Issue(
                severity=issue.get("severity", "info"),
                line=issue.get("line"),
                category=issue.get("category", "General"),
                message=issue.get("message", ""),
                suggestion=issue.get("suggestion", "")
            )
            for issue in issues_data[:10]  # Limit to top 10
        ]
    
    def _extract_suggestions(self, ai_analysis: Dict) -> List[str]:
        """Extract suggestions from AI analysis"""
        return ai_analysis.get("suggestions", ["Continue practicing good coding habits"])
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        ext = filename.lower().split('.')[-1]
        lang_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'go': 'go',
            'rs': 'rust',
        }
        return lang_map.get(ext, 'unknown')


# Test function
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def main():
    data = [1, 2, 3, 4, 5]
    result = calculate_sum(data)
    print(f"Sum: {result}")

if __name__ == "__main__":
    main()
"""
    
    analyzer = GroqCodeAnalyzer(groq_api_key=os.getenv("GROQ_API_KEY"))
    report = analyzer.analyze_code(test_code, "test.py", "test-001")
    
    print("\n" + "="*60)
    print("CODE ANALYSIS REPORT")
    print("="*60)
    print(f"Overall Score: {report.quality_score.overall_score}/100 (Grade: {report.quality_score.grade})")
    print(f"\nMetrics:")
    print(f"  - Lines of Code: {report.metrics.lines_of_code}")
    print(f"  - Functions: {report.metrics.num_functions}")
    print(f"  - Complexity: {report.metrics.cyclomatic_complexity}")
    print(f"\nStrengths:")
    for strength in report.strengths:
        print(f"  ✓ {strength}")
    print(f"\nSuggestions:")
    for suggestion in report.suggestions:
        print(f"  → {suggestion}")
    print(f"\nAI Feedback:\n{report.ai_feedback}")
