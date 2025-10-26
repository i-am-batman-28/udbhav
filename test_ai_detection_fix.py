"""
Test AI Detection Fix

This script tests if the plagiarism detector properly detects AI-generated code
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

# AI-generated looking code (very clean, over-commented)
ai_code = """
def calculate_factorial(n: int) -> int:
    \"\"\"
    Calculate the factorial of a given number.
    
    Args:
        n (int): The number to calculate factorial for.
        
    Returns:
        int: The factorial of the number.
        
    Raises:
        ValueError: If the input is negative.
    \"\"\"
    # Validate input to ensure it's non-negative
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    
    # Base case: factorial of 0 is 1
    if n == 0:
        return 1
    
    # Initialize result variable
    result = 1
    
    # Calculate factorial using iterative approach
    for i in range(1, n + 1):
        result *= i
    
    # Return the calculated factorial
    return result
"""

# Human-written code (messy, minimal comments)
human_code = """
def calc_fact(num):
    if num < 0:
        return None
    res = 1
    for x in range(1, num + 1):
        res = res * x
    return res
"""

print("=" * 80)
print("TESTING AI DETECTION FIX")
print("=" * 80)

detector = PlagiarismDetector(use_vector_db=False)

print("\n\n1. Testing with OBVIOUS AI-GENERATED code:")
print("-" * 80)
report1 = detector.check_against_submissions(
    submission_text=ai_code,
    submission_id="test-ai-001",
    submission_type="code",
    student_name="AI Test",
    files_content=[{"filename": "factorial.py", "content": ai_code}]
)

print(f"\n📊 RESULTS:")
print(f"   Originality Score: {report1.overall_originality_score}%")
print(f"   Matches Found: {report1.total_matches_found}")
print(f"   Risk Level: {report1.risk_level}")
print(f"   Flagged: {len(report1.flagged_sections)} sections")

if report1.total_matches_found > 0:
    for match in report1.similarity_matches:
        print(f"\n   Match: {match.match_type}")
        print(f"   Confidence: {match.confidence * 100:.1f}%")
        print(f"   Similarity: {match.similarity_percentage:.1f}%")
else:
    print("   ❌ NO MATCHES FOUND - AI detection failed!")

print("\n\n2. Testing with HUMAN-WRITTEN code:")
print("-" * 80)
report2 = detector.check_against_submissions(
    submission_text=human_code,
    submission_id="test-human-001",
    submission_type="code",
    student_name="Human Test",
    files_content=[{"filename": "factorial.py", "content": human_code}]
)

print(f"\n📊 RESULTS:")
print(f"   Originality Score: {report2.overall_originality_score}%")
print(f"   Matches Found: {report2.total_matches_found}")
print(f"   Risk Level: {report2.risk_level}")
print(f"   Flagged: {len(report2.flagged_sections)} sections")

print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if report1.total_matches_found > 0 and report1.overall_originality_score < 100:
    print("✅ AI detection is WORKING!")
    print(f"   - Detected AI code with {report1.overall_originality_score}% originality")
else:
    print("❌ AI detection is NOT WORKING!")
    print("   - AI code showed 100% originality (should be much lower)")

if report2.overall_originality_score >= 90:
    print("✅ Human code is correctly identified!")
else:
    print("⚠️  Human code has low originality score (may be false positive)")
