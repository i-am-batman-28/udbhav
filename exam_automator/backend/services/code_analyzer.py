"""
Code Analysis Service
Analyzes code submissions for quality, complexity, style, and best practices
"""

import os
import re
import ast
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
import math

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


@dataclass
class CodeMetrics:
    """Code complexity and quality metrics"""
    lines_of_code: int
    lines_of_comments: int
    blank_lines: int
    cyclomatic_complexity: int
    maintainability_index: float
    comment_ratio: float
    average_function_length: float
    max_function_length: int
    number_of_functions: int
    number_of_classes: int


@dataclass
class StyleIssue:
    """Style violation or issue"""
    line_number: int
    severity: str  # "error", "warning", "info"
    category: str  # "naming", "spacing", "structure", etc.
    message: str
    suggestion: Optional[str] = None


@dataclass
class CodeQualityScore:
    """Overall code quality assessment"""
    functionality_score: float  # 0-100
    readability_score: float  # 0-100
    maintainability_score: float  # 0-100
    efficiency_score: float  # 0-100
    style_score: float  # 0-100
    overall_score: float  # Weighted average
    grade: str  # A, B, C, D, F


@dataclass
class CodeAnalysisReport:
    """Comprehensive code analysis report"""
    submission_id: str
    language: str
    metrics: CodeMetrics
    quality_score: CodeQualityScore
    style_issues: List[StyleIssue]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    best_practices_violations: List[str]
    security_concerns: List[str]
    ai_feedback: Optional[str] = None


class CodeAnalyzer:
    """
    Advanced code analysis supporting multiple programming languages
    Currently focuses on Python with extensibility for other languages
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize code analyzer
        
        Args:
            openai_api_key: API key for AI-powered analysis (uses Groq now, much faster!)
        """
        # Try Groq first (faster and free), fallback to OpenAI
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
            self.model = "llama-3.3-70b-versatile"
            print("✅ Code analyzer initialized with Groq (10-20x faster!)")
        elif self.openai_api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_api_key)
            self.model = "gpt-4o-mini"
            print("✅ Code analyzer initialized with OpenAI")
        else:
            self.client = None
            self.model = None
            print("⚠️ No AI API key found. AI-powered analysis disabled.")
        
        # Language detection patterns
        self.language_patterns = {
            'python': [r'def\s+\w+', r'import\s+\w+', r'class\s+\w+', r'if\s+__name__\s*=='],
            'java': [r'public\s+class', r'public\s+static\s+void\s+main', r'System\.out\.println'],
            'javascript': [r'function\s+\w+', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'=>'],
            'cpp': [r'#include\s*<', r'int\s+main\s*\(', r'std::', r'cout\s*<<'],
            'c': [r'#include\s*<', r'int\s+main\s*\(', r'printf\s*\('],
        }
    
    def detect_language(self, code: str) -> str:
        """
        Detect programming language from code
        
        Args:
            code: Source code string
            
        Returns:
            Detected language name
        """
        scores = defaultdict(int)
        
        for language, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code):
                    scores[language] += 1
        
        if not scores:
            return "unknown"
        
        # Return language with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def analyze_python_code(self, code: str, submission_id: str = "unknown") -> CodeAnalysisReport:
        """
        Comprehensive analysis of Python code
        
        Args:
            code: Python source code
            submission_id: Unique submission identifier
            
        Returns:
            CodeAnalysisReport with detailed analysis
        """
        print(f"🔍 Analyzing Python code for submission: {submission_id}")
        
        # Calculate metrics
        metrics = self._calculate_python_metrics(code)
        
        # Detect style issues
        style_issues = self._detect_python_style_issues(code)
        
        # Calculate quality scores
        quality_score = self._calculate_quality_scores(metrics, style_issues, code)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(
            metrics, quality_score, style_issues
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(weaknesses, style_issues, code)
        
        # Check for best practices violations
        bp_violations = self._check_best_practices(code)
        
        # Security analysis
        security_concerns = self._check_security_issues(code)
        
        # AI-powered feedback (if available)
        ai_feedback = None
        if self.client:
            try:
                ai_feedback = self._get_ai_feedback(code, metrics, quality_score)
            except Exception as e:
                print(f"⚠️ AI feedback generation failed: {e}")
        
        report = CodeAnalysisReport(
            submission_id=submission_id,
            language="python",
            metrics=metrics,
            quality_score=quality_score,
            style_issues=style_issues[:20],  # Top 20 issues
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            best_practices_violations=bp_violations,
            security_concerns=security_concerns,
            ai_feedback=ai_feedback
        )
        
        print(f"✅ Analysis complete: Overall Score = {quality_score.overall_score:.1f}/100 (Grade: {quality_score.grade})")
        
        return report
    
    def _calculate_python_metrics(self, code: str) -> CodeMetrics:
        """Calculate code metrics for Python code"""
        lines = code.split('\n')
        
        # Count different line types
        loc = 0  # Lines of code
        comments = 0
        blanks = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blanks += 1
            elif stripped.startswith('#'):
                comments += 1
            else:
                loc += 1
                # Count inline comments
                if '#' in line:
                    comments += 0.5
        
        # Parse AST for more detailed analysis
        try:
            tree = ast.parse(code)
            
            # Count functions and classes
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            num_functions = len(functions)
            num_classes = len(classes)
            
            # Calculate function lengths
            function_lengths = []
            for func in functions:
                func_start = func.lineno
                func_end = func.end_lineno if hasattr(func, 'end_lineno') else func_start + 10
                func_length = func_end - func_start + 1
                function_lengths.append(func_length)
            
            avg_func_length = sum(function_lengths) / len(function_lengths) if function_lengths else 0
            max_func_length = max(function_lengths) if function_lengths else 0
            
            # Cyclomatic complexity (simplified)
            complexity = self._calculate_cyclomatic_complexity(tree)
            
        except SyntaxError:
            num_functions = len(re.findall(r'def\s+\w+', code))
            num_classes = len(re.findall(r'class\s+\w+', code))
            avg_func_length = loc / max(num_functions, 1)
            max_func_length = int(avg_func_length * 1.5)
            complexity = self._estimate_complexity(code)
        
        # Calculate ratios and indices
        total_lines = loc + comments + blanks
        comment_ratio = comments / max(total_lines, 1)
        
        # Maintainability Index (simplified Microsoft formula)
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # Simplified version
        volume = loc * math.log(max(loc, 1))
        maintainability = max(0, 171 - 5.2 * math.log(max(volume, 1)) - 0.23 * complexity - 16.2 * math.log(max(loc, 1)))
        maintainability = min(100, maintainability)  # Cap at 100
        
        return CodeMetrics(
            lines_of_code=loc,
            lines_of_comments=int(comments),
            blank_lines=blanks,
            cyclomatic_complexity=complexity,
            maintainability_index=round(maintainability, 2),
            comment_ratio=round(comment_ratio, 3),
            average_function_length=round(avg_func_length, 1),
            max_function_length=max_func_length,
            number_of_functions=num_functions,
            number_of_classes=num_classes
        )
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity from AST"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Count decision points
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate complexity from code text (fallback)"""
        complexity = 1
        
        # Count control structures
        complexity += len(re.findall(r'\bif\b', code))
        complexity += len(re.findall(r'\bfor\b', code))
        complexity += len(re.findall(r'\bwhile\b', code))
        complexity += len(re.findall(r'\btry\b', code))
        complexity += len(re.findall(r'\band\b|\bor\b', code))
        
        return complexity
    
    def _detect_python_style_issues(self, code: str) -> List[StyleIssue]:
        """Detect Python style issues (PEP 8 violations)"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 79:
                issues.append(StyleIssue(
                    line_number=i,
                    severity="warning",
                    category="line_length",
                    message=f"Line exceeds 79 characters ({len(line)} chars)",
                    suggestion="Break into multiple lines or refactor"
                ))
            
            # Check for multiple statements on one line
            if ';' in line and not line.strip().startswith('#'):
                issues.append(StyleIssue(
                    line_number=i,
                    severity="warning",
                    category="structure",
                    message="Multiple statements on one line",
                    suggestion="Use separate lines for each statement"
                ))
            
            # Check naming conventions
            # Function names should be lowercase with underscores
            func_match = re.search(r'def\s+([A-Z]\w+)', line)
            if func_match:
                issues.append(StyleIssue(
                    line_number=i,
                    severity="warning",
                    category="naming",
                    message=f"Function name '{func_match.group(1)}' should be lowercase with underscores",
                    suggestion=f"Rename to '{self._to_snake_case(func_match.group(1))}'"
                ))
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(StyleIssue(
                    line_number=i,
                    severity="info",
                    category="whitespace",
                    message="Trailing whitespace",
                    suggestion="Remove trailing spaces"
                ))
            
            # Check for missing whitespace around operators
            if re.search(r'\w+[+\-*/%]=\w+', line):
                issues.append(StyleIssue(
                    line_number=i,
                    severity="info",
                    category="spacing",
                    message="Missing whitespace around operator",
                    suggestion="Add spaces around operators"
                ))
        
        # Check for missing docstrings
        if not re.search(r'""".*?"""', code, re.DOTALL) and not re.search(r"'''.*?'''", code, re.DOTALL):
            if re.search(r'def\s+\w+', code) or re.search(r'class\s+\w+', code):
                issues.append(StyleIssue(
                    line_number=1,
                    severity="warning",
                    category="documentation",
                    message="Missing module docstring",
                    suggestion="Add docstring at the beginning of the file"
                ))
        
        return issues
    
    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case"""
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    
    def _calculate_quality_scores(self, metrics: CodeMetrics, 
                                  style_issues: List[StyleIssue],
                                  code: str) -> CodeQualityScore:
        """Calculate quality scores based on metrics and issues"""
        
        # Readability score (based on metrics and style)
        readability = 100
        readability -= len([i for i in style_issues if i.severity == "error"]) * 5
        readability -= len([i for i in style_issues if i.severity == "warning"]) * 2
        readability -= len([i for i in style_issues if i.severity == "info"]) * 0.5
        readability -= max(0, (metrics.average_function_length - 20) * 2)  # Penalize long functions
        readability += metrics.comment_ratio * 20  # Reward good commenting
        readability = max(0, min(100, readability))
        
        # Maintainability score (based on complexity and structure)
        maintainability = metrics.maintainability_index
        if metrics.cyclomatic_complexity > 10:
            maintainability -= (metrics.cyclomatic_complexity - 10) * 3
        maintainability = max(0, min(100, maintainability))
        
        # Style score (based on style issues)
        style = 100
        style -= len([i for i in style_issues if i.severity == "error"]) * 10
        style -= len([i for i in style_issues if i.severity == "warning"]) * 3
        style -= len([i for i in style_issues if i.severity == "info"]) * 1
        style = max(0, min(100, style))
        
        # Efficiency score (based on complexity and code structure)
        efficiency = 100
        if metrics.cyclomatic_complexity > 15:
            efficiency -= 20
        elif metrics.cyclomatic_complexity > 10:
            efficiency -= 10
        if metrics.average_function_length > 50:
            efficiency -= 15
        # Check for common inefficiencies
        if re.search(r'\.append\s*\([^)]+\)\s*\.append', code):
            efficiency -= 5  # Multiple appends could be optimized
        efficiency = max(0, min(100, efficiency))
        
        # Functionality score (based on code completeness)
        functionality = 85  # Base score
        if metrics.number_of_functions > 0:
            functionality += 5
        if metrics.number_of_classes > 0:
            functionality += 5
        if re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', code):
            functionality += 5
        functionality = min(100, functionality)
        
        # Overall score (weighted average)
        overall = (
            functionality * 0.25 +
            readability * 0.25 +
            maintainability * 0.20 +
            efficiency * 0.15 +
            style * 0.15
        )
        
        # Assign grade
        if overall >= 90:
            grade = "A"
        elif overall >= 80:
            grade = "B"
        elif overall >= 70:
            grade = "C"
        elif overall >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return CodeQualityScore(
            functionality_score=round(functionality, 1),
            readability_score=round(readability, 1),
            maintainability_score=round(maintainability, 1),
            efficiency_score=round(efficiency, 1),
            style_score=round(style, 1),
            overall_score=round(overall, 1),
            grade=grade
        )
    
    def _identify_strengths_weaknesses(self, metrics: CodeMetrics,
                                      quality: CodeQualityScore,
                                      issues: List[StyleIssue]) -> Tuple[List[str], List[str]]:
        """Identify code strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Analyze strengths
        if quality.overall_score >= 85:
            strengths.append("Excellent overall code quality")
        if metrics.comment_ratio >= 0.15:
            strengths.append("Well-documented code with good comments")
        if metrics.cyclomatic_complexity <= 10:
            strengths.append("Good code complexity - easy to understand and maintain")
        if metrics.average_function_length <= 25:
            strengths.append("Functions are well-sized and focused")
        if quality.style_score >= 90:
            strengths.append("Follows style guidelines consistently")
        if metrics.number_of_classes > 0:
            strengths.append("Uses object-oriented programming principles")
        
        # Analyze weaknesses
        if quality.overall_score < 70:
            weaknesses.append("Overall code quality needs improvement")
        if metrics.comment_ratio < 0.05:
            weaknesses.append("Insufficient code documentation and comments")
        if metrics.cyclomatic_complexity > 15:
            weaknesses.append("High code complexity - consider refactoring")
        if metrics.average_function_length > 40:
            weaknesses.append("Functions are too long - consider breaking them down")
        if len([i for i in issues if i.severity == "error"]) > 0:
            weaknesses.append("Contains syntax or critical style errors")
        if metrics.max_function_length > 100:
            weaknesses.append("Some functions are excessively long")
        
        return strengths, weaknesses
    
    def _generate_suggestions(self, weaknesses: List[str], 
                            issues: List[StyleIssue],
                            code: str) -> List[str]:
        """Generate actionable suggestions for improvement"""
        suggestions = []
        
        # Based on weaknesses
        if any("complexity" in w.lower() for w in weaknesses):
            suggestions.append("💡 Break down complex functions into smaller, focused functions")
            suggestions.append("💡 Reduce nested loops and conditionals where possible")
        
        if any("documentation" in w.lower() or "comments" in w.lower() for w in weaknesses):
            suggestions.append("📝 Add docstrings to all functions and classes")
            suggestions.append("📝 Include inline comments for complex logic")
        
        if any("long" in w.lower() for w in weaknesses):
            suggestions.append("✂️ Split long functions into smaller helper functions")
            suggestions.append("✂️ Follow the Single Responsibility Principle")
        
        # Based on style issues
        if any(i.category == "naming" for i in issues):
            suggestions.append("🏷️ Follow PEP 8 naming conventions (snake_case for functions/variables)")
        
        if any(i.category == "line_length" for i in issues):
            suggestions.append("📏 Keep lines under 79 characters for better readability")
        
        # General suggestions
        suggestions.append("✅ Run a linter (pylint, flake8) to catch style issues automatically")
        suggestions.append("🧪 Add unit tests to verify functionality")
        suggestions.append("📚 Consider adding type hints for better code clarity")
        
        return suggestions[:8]  # Return top 8 suggestions
    
    def _check_best_practices(self, code: str) -> List[str]:
        """Check for common best practices violations"""
        violations = []
        
        # Check for bare except clauses
        if re.search(r'except\s*:', code):
            violations.append("❌ Bare 'except:' clause found - catch specific exceptions instead")
        
        # Check for global variables
        if re.search(r'^[A-Z_]+\s*=', code, re.MULTILINE):
            global_vars = len(re.findall(r'^[A-Z_]+\s*=', code, re.MULTILINE))
            if global_vars > 3:
                violations.append(f"⚠️ {global_vars} global variables found - consider reducing")
        
        # Check for print statements (should use logging)
        print_count = len(re.findall(r'\bprint\s*\(', code))
        if print_count > 5:
            violations.append(f"⚠️ {print_count} print statements - consider using logging module")
        
        # Check for hardcoded credentials or paths
        if re.search(r'password\s*=\s*["\']', code, re.IGNORECASE):
            violations.append("🔒 Hardcoded password detected - use environment variables")
        
        # Check for missing main guard
        if not re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', code):
            if len(code) > 500:  # Only flag for longer scripts
                violations.append("⚠️ Missing if __name__ == '__main__' guard")
        
        return violations
    
    def _check_security_issues(self, code: str) -> List[str]:
        """Check for potential security issues"""
        concerns = []
        
        # Check for eval/exec usage
        if re.search(r'\beval\s*\(', code) or re.search(r'\bexec\s*\(', code):
            concerns.append("🚨 Use of eval() or exec() detected - potential security risk")
        
        # Check for SQL injection risks
        if re.search(r'execute\s*\([^)]*%s', code) or re.search(r'execute\s*\([^)]*\+', code):
            concerns.append("🚨 Potential SQL injection risk - use parameterized queries")
        
        # Check for pickle usage
        if 'import pickle' in code or 'from pickle import' in code:
            concerns.append("⚠️ Pickle usage detected - can be unsafe with untrusted data")
        
        # Check for shell command injection
        if re.search(r'os\.system\s*\(', code) or re.search(r'subprocess.*shell\s*=\s*True', code):
            concerns.append("⚠️ Shell command execution with shell=True - injection risk")
        
        return concerns
    
    def _get_ai_feedback(self, code: str, metrics: CodeMetrics, 
                        quality: CodeQualityScore) -> str:
        """Get AI-powered feedback from GPT"""
        if not self.client:
            return None
        
        prompt = f"""
You are an expert code reviewer. Analyze this Python code and provide constructive feedback.

Code Metrics:
- Lines of Code: {metrics.lines_of_code}
- Cyclomatic Complexity: {metrics.cyclomatic_complexity}
- Comment Ratio: {metrics.comment_ratio:.2%}
- Functions: {metrics.number_of_functions}

Quality Scores:
- Overall: {quality.overall_score}/100 (Grade: {quality.grade})
- Readability: {quality.readability_score}/100
- Maintainability: {quality.maintainability_score}/100

Code:
```python
{code[:1500]}  # First 1500 characters
```

Provide brief, actionable feedback focusing on:
1. What the code does well
2. Key areas for improvement
3. One specific refactoring suggestion

Keep response under 200 words.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,  # Use Groq or OpenAI model
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer providing constructive feedback."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ AI feedback generation error: {e}")
            return None
    
    def generate_analysis_report_markdown(self, report: CodeAnalysisReport) -> str:
        """Generate a markdown-formatted code analysis report"""
        md = f"""# Code Analysis Report

**Submission ID**: {report.submission_id}
**Language**: {report.language.upper()}

---

## Quality Score: {report.quality_score.overall_score}/100 (Grade: {report.quality_score.grade})

### Score Breakdown
| Metric | Score |
|--------|-------|
| Functionality | {report.quality_score.functionality_score}/100 |
| Readability | {report.quality_score.readability_score}/100 |
| Maintainability | {report.quality_score.maintainability_score}/100 |
| Efficiency | {report.quality_score.efficiency_score}/100 |
| Style | {report.quality_score.style_score}/100 |

---

## Code Metrics

- **Lines of Code**: {report.metrics.lines_of_code}
- **Lines of Comments**: {report.metrics.lines_of_comments} ({report.metrics.comment_ratio:.1%})
- **Blank Lines**: {report.metrics.blank_lines}
- **Cyclomatic Complexity**: {report.metrics.cyclomatic_complexity}
- **Maintainability Index**: {report.metrics.maintainability_index:.1f}/100
- **Functions**: {report.metrics.number_of_functions}
- **Classes**: {report.metrics.number_of_classes}
- **Avg Function Length**: {report.metrics.average_function_length:.1f} lines
- **Max Function Length**: {report.metrics.max_function_length} lines

---

## Strengths ✅

"""
        for strength in report.strengths:
            md += f"- {strength}\n"
        
        md += "\n## Areas for Improvement ⚠️\n\n"
        for weakness in report.weaknesses:
            md += f"- {weakness}\n"
        
        md += "\n## Suggestions 💡\n\n"
        for suggestion in report.suggestions:
            md += f"- {suggestion}\n"
        
        if report.style_issues:
            md += f"\n## Style Issues ({len(report.style_issues)} found)\n\n"
            
            # Group by severity
            errors = [i for i in report.style_issues if i.severity == "error"]
            warnings = [i for i in report.style_issues if i.severity == "warning"]
            info = [i for i in report.style_issues if i.severity == "info"]
            
            if errors:
                md += f"### Errors ({len(errors)})\n"
                for issue in errors[:5]:
                    md += f"- Line {issue.line_number}: {issue.message}\n"
            
            if warnings:
                md += f"\n### Warnings ({len(warnings)})\n"
                for issue in warnings[:5]:
                    md += f"- Line {issue.line_number}: {issue.message}\n"
        
        if report.best_practices_violations:
            md += "\n## Best Practices Violations\n\n"
            for violation in report.best_practices_violations:
                md += f"- {violation}\n"
        
        if report.security_concerns:
            md += "\n## Security Concerns 🔒\n\n"
            for concern in report.security_concerns:
                md += f"- {concern}\n"
        
        if report.ai_feedback:
            md += f"\n## AI Expert Feedback 🤖\n\n{report.ai_feedback}\n"
        
        md += "\n---\n\n*Generated by ProctorIQ Code Analyzer*\n"
        
        return md


if __name__ == "__main__":
    # Test the code analyzer
    print("🧪 Testing Code Analyzer...\n")
    
    test_code = """
import os
import sys

def calculateSum(numbers):
    \"\"\"Calculate sum of numbers\"\"\"
    total = 0
    for num in numbers:
        if num > 0:
            total += num
    return total

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process(self):
        for item in self.data:
            print(item)

def main():
    nums = [1, 2, 3, 4, 5]
    result = calculateSum(nums)
    print(f"Sum: {result}")

if __name__ == "__main__":
    main()
"""
    
    analyzer = CodeAnalyzer()
    
    # Detect language
    lang = analyzer.detect_language(test_code)
    print(f"Detected Language: {lang}\n")
    
    # Analyze code
    report = analyzer.analyze_python_code(test_code, submission_id="test-001")
    
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    print(f"\nOverall Score: {report.quality_score.overall_score}/100 (Grade: {report.quality_score.grade})")
    print(f"Cyclomatic Complexity: {report.metrics.cyclomatic_complexity}")
    print(f"Lines of Code: {report.metrics.lines_of_code}")
    print(f"Comment Ratio: {report.metrics.comment_ratio:.1%}")
    print(f"Style Issues: {len(report.style_issues)}")
    
    print("\n✅ Code Analyzer tests complete!")
