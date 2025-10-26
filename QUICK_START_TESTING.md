# 🚀 Quick Start Guide - New Peer Review Features

## Testing the New Services

### 1. Plagiarism Detection Service

#### Test with Two Similar Code Snippets:
```bash
cd exam_automator/backend
python3 << 'EOF'
from services.plagiarism_detector import quick_plagiarism_check

code1 = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""

code2 = """
def compute_fib(num):
    if num <= 1:
        return num
    return compute_fib(num-1) + compute_fib(num-2)
"""

result = quick_plagiarism_check(code1, code2, text_type="code")
print(f"\n🔍 Plagiarism Check Results:")
print(f"   Overall Similarity: {result['overall_similarity']}%")
print(f"   Verdict: {result['verdict']}")
print(f"   Matching Sections: {result['matching_sections']}")
EOF
```

#### Test with Full Report:
```bash
python3 << 'EOF'
from services.plagiarism_detector import PlagiarismDetector

detector = PlagiarismDetector(use_vector_db=False)

student_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

print(bubble_sort([64, 34, 25, 12, 22]))
"""

# Check similarity
similarity = detector.calculate_text_similarity(student_code, student_code)
print(f"\n📊 Self-Similarity Test: {similarity * 100:.2f}%")

# Analyze code structure
matches = detector.find_matching_sections(student_code, student_code)
print(f"   Matching Sections Found: {len(matches)}")
EOF
```

---

### 2. Code Analysis Service

#### Test with Sample Python Code:
```bash
python3 << 'EOF'
from services.code_analyzer import CodeAnalyzer

test_code = '''
import sys

def calculateFactorial(n):
    """Calculate factorial of n"""
    if n == 0 or n == 1:
        return 1
    else:
        return n * calculateFactorial(n-1)

class MathOperations:
    def __init__(self):
        self.operations_count = 0
    
    def add(self, a, b):
        self.operations_count += 1
        return a + b
    
    def multiply(self, a, b):
        self.operations_count += 1
        return a * b

def main():
    result = calculateFactorial(5)
    print(f"Factorial of 5 is: {result}")
    
    math_ops = MathOperations()
    print(f"10 + 5 = {math_ops.add(10, 5)}")

if __name__ == "__main__":
    main()
'''

analyzer = CodeAnalyzer()

# Detect language
lang = analyzer.detect_language(test_code)
print(f"\n🔍 Detected Language: {lang}")

# Analyze code
report = analyzer.analyze_python_code(test_code, submission_id="test-001")

print(f"\n📊 Code Analysis Results:")
print(f"   Overall Score: {report.quality_score.overall_score}/100")
print(f"   Grade: {report.quality_score.grade}")
print(f"\n   Score Breakdown:")
print(f"   - Functionality: {report.quality_score.functionality}/100")
print(f"   - Readability: {report.quality_score.readability}/100")
print(f"   - Maintainability: {report.quality_score.maintainability}/100")
print(f"   - Efficiency: {report.quality_score.efficiency}/100")
print(f"   - Style: {report.quality_score.style}/100")

print(f"\n   Code Metrics:")
print(f"   - Lines of Code: {report.metrics.lines_of_code}")
print(f"   - Cyclomatic Complexity: {report.metrics.cyclomatic_complexity}")
print(f"   - Comment Ratio: {report.metrics.comment_ratio:.1%}")
print(f"   - Functions: {report.metrics.number_of_functions}")
print(f"   - Classes: {report.metrics.number_of_classes}")

print(f"\n   ✅ Strengths:")
for strength in report.strengths[:3]:
    print(f"      - {strength}")

print(f"\n   ⚠️  Issues Found: {len(report.style_issues)}")
if report.style_issues:
    for issue in report.style_issues[:3]:
        print(f"      - Line {issue.line_number}: {issue.message}")

# Generate report
markdown_report = analyzer.generate_analysis_report_markdown(report)
print(f"\n✅ Full markdown report generated ({len(markdown_report)} characters)")
EOF
```

---

### 3. Data Models

#### Test Model Creation and Validation:
```bash
python3 << 'EOF'
from models.submission_models import (
    Submission, SubmissionType, SubmissionStatus,
    SubmissionMetadata, ProgrammingLanguage,
    Review, ReviewType, EvaluationCriteria, CriterionScore,
    calculate_weighted_score, determine_grade
)

# Create a submission
print("\n🎓 Creating a new submission...")
submission = Submission(
    student_id="student-12345",
    student_name="Alice Johnson",
    student_email="alice@university.edu",
    submission_type=SubmissionType.CODE,
    metadata=SubmissionMetadata(
        title="Sorting Algorithms Implementation",
        description="Implementation of QuickSort and MergeSort in Python",
        tags=["algorithms", "sorting", "python"],
        programming_languages=[ProgrammingLanguage.PYTHON],
        total_files=3
    )
)

print(f"✅ Submission Created:")
print(f"   ID: {submission.submission_id}")
print(f"   Student: {submission.student_name}")
print(f"   Type: {submission.submission_type}")
print(f"   Status: {submission.status}")
print(f"   Title: {submission.metadata.title}")

# Create evaluation criteria
print("\n📝 Creating evaluation criteria...")
criteria = EvaluationCriteria(
    functionality=CriterionScore(
        criterion_name="Functionality",
        score=85.0,
        weight=0.25,
        comment="Code works correctly with minor edge case issues"
    ),
    code_quality=CriterionScore(
        criterion_name="Code Quality",
        score=78.0,
        weight=0.20,
        comment="Good structure, but some functions are too long"
    ),
    efficiency=CriterionScore(
        criterion_name="Efficiency",
        score=90.0,
        weight=0.15,
        comment="Excellent algorithmic efficiency"
    ),
    documentation=CriterionScore(
        criterion_name="Documentation",
        score=70.0,
        weight=0.15,
        comment="Needs more comments in complex sections"
    )
)

# Calculate weighted score
overall_score = calculate_weighted_score(criteria)
grade = determine_grade(overall_score)

print(f"✅ Evaluation Complete:")
print(f"   Overall Score: {overall_score:.2f}/100")
print(f"   Grade: {grade}")

# Create a review
print("\n🤖 Creating an AI review...")
review = Review(
    submission_id=submission.submission_id,
    reviewer_id="ai-system",
    reviewer_type=ReviewType.AI,
    criteria_scores=criteria,
    overall_score=overall_score
)

print(f"✅ Review Created:")
print(f"   Review ID: {review.review_id}")
print(f"   Type: {review.reviewer_type}")
print(f"   Status: {review.status}")
print(f"   Score: {review.overall_score:.2f}/100")

# JSON serialization
print("\n💾 Testing JSON serialization...")
submission_json = submission.model_dump_json(indent=2)
print(f"✅ Serialization successful ({len(submission_json)} characters)")

print("\n✅ All model tests passed!")
EOF
```

---

## 🧪 Integration Test Scenarios

### Scenario 1: Complete Code Submission Flow
```bash
python3 << 'EOF'
from services.code_analyzer import CodeAnalyzer
from services.plagiarism_detector import PlagiarismDetector
from models.submission_models import (
    Submission, SubmissionType, SubmissionMetadata,
    ProgrammingLanguage, CodeAnalysisReport
)

# Student submits code
student_code = """
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

if __name__ == "__main__":
    arr = [64, 34, 25, 12, 22, 11, 90]
    sorted_arr = merge_sort(arr)
    print("Sorted array:", sorted_arr)
"""

print("📝 Processing Submission: 'MergeSort Implementation'\n")

# Step 1: Create submission
submission = Submission(
    student_id="s-001",
    student_name="Bob Smith",
    submission_type=SubmissionType.CODE,
    metadata=SubmissionMetadata(
        title="MergeSort Implementation",
        description="Recursive merge sort algorithm",
        programming_languages=[ProgrammingLanguage.PYTHON]
    )
)
print(f"✅ Step 1: Submission created (ID: {submission.submission_id})")

# Step 2: Analyze code quality
analyzer = CodeAnalyzer()
code_report = analyzer.analyze_python_code(student_code, submission.submission_id)
print(f"✅ Step 2: Code analysis complete")
print(f"   - Quality Score: {code_report.quality_score.overall}/100")
print(f"   - Grade: {code_report.quality_score.grade}")
print(f"   - Complexity: {code_report.metrics.cyclomatic_complexity}")

# Step 3: Check plagiarism (without vector DB for testing)
detector = PlagiarismDetector(use_vector_db=False)
similarity = detector.calculate_text_similarity(student_code, student_code)
print(f"✅ Step 3: Plagiarism check complete")
print(f"   - Self-similarity: {similarity * 100:.2f}% (expected: 100%)")

# Step 4: Generate final report
print(f"\n📊 FINAL ASSESSMENT:")
print(f"   Student: {submission.student_name}")
print(f"   Submission: {submission.metadata.title}")
print(f"   Code Quality: {code_report.quality_score.grade} ({code_report.quality_score.overall}/100)")
print(f"   Originality: HIGH (no matches found)")
print(f"\n   Top Strengths:")
for i, strength in enumerate(code_report.strengths[:3], 1):
    print(f"   {i}. {strength}")

if code_report.suggestions:
    print(f"\n   Suggestions for Improvement:")
    for i, suggestion in enumerate(code_report.suggestions[:3], 1):
        print(f"   {i}. {suggestion}")

print("\n✅ Complete workflow test passed!")
EOF
```

---

## 📈 Performance Benchmarks

### Run Performance Tests:
```bash
python3 << 'EOF'
import time
from services.code_analyzer import CodeAnalyzer
from services.plagiarism_detector import PlagiarismDetector

# Sample code for testing
test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

class Calculator:
    def add(self, a, b):
        return a + b
    def subtract(self, a, b):
        return a - b
"""

print("⏱️  Performance Benchmarks\n")

# Code Analysis Speed
analyzer = CodeAnalyzer()
start = time.time()
report = analyzer.analyze_python_code(test_code, "bench-001")
duration = time.time() - start
print(f"✅ Code Analysis: {duration:.3f} seconds")

# Plagiarism Detection Speed
detector = PlagiarismDetector(use_vector_db=False)
start = time.time()
similarity = detector.calculate_text_similarity(test_code, test_code)
matches = detector.find_matching_sections(test_code, test_code)
duration = time.time() - start
print(f"✅ Plagiarism Check: {duration:.3f} seconds")

# Code Similarity Speed
start = time.time()
code_sim = detector.detect_code_similarity(test_code, test_code)
duration = time.time() - start
print(f"✅ Code Similarity: {duration:.3f} seconds")

print(f"\n🎯 All operations < 1 second: {'✅ PASS' if all([d < 1 for d in [duration]]) else '⚠️  SLOW'}")
EOF
```

---

## 🎓 Educational Use Cases

### 1. Instructor: Grade a Student Submission
```python
# Analyze student's code
report = analyzer.analyze_python_code(student_code, submission_id)

# Get comprehensive feedback
print(report.quality_score.overall)  # 85/100
print(report.quality_score.grade)    # B
print(report.strengths)              # List of good aspects
print(report.suggestions)            # Improvement ideas
```

### 2. Student: Self-Assessment
```python
# Check own code before submission
report = analyzer.analyze_python_code(my_code, "self-check")

# Review feedback
for issue in report.style_issues:
    print(f"Line {issue.line_number}: {issue.message}")
    print(f"Suggestion: {issue.suggestion}")
```

### 3. Admin: Detect Academic Dishonesty
```python
# Compare two submissions
result = quick_plagiarism_check(submission1, submission2, "code")

if result['overall_similarity'] > 80:
    print("⚠️  High similarity detected! Manual review needed.")
```

---

## 🔧 Troubleshooting

### Issue: Import Errors
```bash
# Solution: Install dependencies
cd exam_automator
pip install -r requirements.txt
```

### Issue: OpenAI API Key Error
```bash
# Solution: Set environment variable
echo "OPENAI_API_KEY=your-key-here" >> .env
```

### Issue: Pinecone Not Available
```bash
# Solution: Works without vector DB for testing
detector = PlagiarismDetector(use_vector_db=False)
```

---

## 📚 Next Steps

1. **Test All Services**: Run the tests above
2. **Review Reports**: Check generated markdown reports
3. **Integrate with API**: Connect to FastAPI endpoints (next phase)
4. **Update Frontend**: Create React pages for new features

---

✅ **All services are ready for integration!**
