"""
COMPREHENSIVE PLAGIARISM DETECTION TEST SUITE
==============================================

Tests AI detection with realistic, long code files including:
- Obvious AI-generated code (over-documented, perfect formatting)
- Human-written code (minimal docs, practical approach)
- Mixed scenarios

Author: Test Suite
Date: 2025-10-26
"""

import sys
from pathlib import Path
import time

# Add backend to path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector


def read_file(filepath):
    """Read test file content"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return None


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 100)
    print(f"  {text}")
    print("=" * 100)


def print_results(report, test_name):
    """Print test results in formatted way"""
    print(f"\n📊 {test_name} RESULTS:")
    print("-" * 100)
    print(f"   Originality Score: {report.overall_originality_score:.1f}% / 100%")
    print(f"   Risk Level: {report.risk_level.upper()}")
    print(f"   Total Matches: {report.total_matches_found}")
    print(f"   Sources Checked: {report.sources_checked}")
    print(f"   Flagged Sections: {len(report.flagged_sections)}")
    
    if report.similarity_matches:
        print(f"\n   🔍 Matches Found:")
        for i, match in enumerate(report.similarity_matches, 1):
            print(f"      {i}. Type: {match.match_type}")
            print(f"         Similarity: {match.similarity_percentage:.1f}%")
            print(f"         Confidence: {match.confidence * 100:.1f}%")
            print(f"         Flagged: {'🚩 YES' if match.flagged else '✓ NO'}")
            if match.matching_sections:
                print(f"         Evidence: {len(match.matching_sections)} indicators")
    else:
        print(f"   ✅ No plagiarism detected")
    
    print(f"\n   📝 Recommendations:")
    for rec in report.recommendations:
        # Split by newlines and print each line with proper indentation
        lines = rec.split('\n')
        for line in lines:
            if line.strip():
                print(f"      {line}")


def test_ai_generated_long_file():
    """Test with long, obvious AI-generated file (Calculator)"""
    print_header("TEST 1: Long AI-Generated Code (300+ lines)")
    
    filepath = Path(__file__).parent / "test_cases" / "ai_generated_calculator.py"
    code = read_file(filepath)
    
    if not code:
        print("❌ Failed to load test file")
        return False
    
    print(f"   File: {filepath.name}")
    print(f"   Size: {len(code)} characters")
    print(f"   Lines: {len(code.splitlines())} lines")
    print(f"   Preview: {code[:200]}...")
    
    detector = PlagiarismDetector(use_vector_db=False)
    
    start = time.time()
    report = detector.check_against_submissions(
        submission_text=code,
        submission_id="test-ai-calc-001",
        submission_type="code",
        student_name="AI Test - Calculator",
        files_content=[{"filename": filepath.name, "content": code}]
    )
    elapsed = time.time() - start
    
    print_results(report, "AI-GENERATED CALCULATOR")
    print(f"\n   ⏱️  Analysis Time: {elapsed:.2f} seconds")
    
    # Validation
    success = report.overall_originality_score < 80  # Should detect AI
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n   {status}: AI detection {'worked' if success else 'FAILED'}")
    
    return success


def test_ai_generated_scraper():
    """Test with long AI-generated web scraper"""
    print_header("TEST 2: Long AI-Generated Code (Web Scraper - 400+ lines)")
    
    filepath = Path(__file__).parent / "test_cases" / "ai_generated_scraper.py"
    code = read_file(filepath)
    
    if not code:
        print("❌ Failed to load test file")
        return False
    
    print(f"   File: {filepath.name}")
    print(f"   Size: {len(code)} characters")
    print(f"   Lines: {len(code.splitlines())} lines")
    
    detector = PlagiarismDetector(use_vector_db=False)
    
    start = time.time()
    report = detector.check_against_submissions(
        submission_text=code,
        submission_id="test-ai-scraper-001",
        submission_type="code",
        student_name="AI Test - Scraper",
        files_content=[{"filename": filepath.name, "content": code}]
    )
    elapsed = time.time() - start
    
    print_results(report, "AI-GENERATED WEB SCRAPER")
    print(f"\n   ⏱️  Analysis Time: {elapsed:.2f} seconds")
    
    # Validation
    success = report.overall_originality_score < 80
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n   {status}: AI detection {'worked' if success else 'FAILED'}")
    
    return success


def test_human_written_code():
    """Test with human-written code (should NOT flag)"""
    print_header("TEST 3: Human-Written Code (Minimal docs)")
    
    filepath = Path(__file__).parent / "test_cases" / "human_written_processor.py"
    code = read_file(filepath)
    
    if not code:
        print("❌ Failed to load test file")
        return False
    
    print(f"   File: {filepath.name}")
    print(f"   Size: {len(code)} characters")
    print(f"   Lines: {len(code.splitlines())} lines")
    
    detector = PlagiarismDetector(use_vector_db=False)
    
    start = time.time()
    report = detector.check_against_submissions(
        submission_text=code,
        submission_id="test-human-001",
        submission_type="code",
        student_name="Human Test",
        files_content=[{"filename": filepath.name, "content": code}]
    )
    elapsed = time.time() - start
    
    print_results(report, "HUMAN-WRITTEN CODE")
    print(f"\n   ⏱️  Analysis Time: {elapsed:.2f} seconds")
    
    # Validation - should NOT detect as AI
    success = report.overall_originality_score >= 70
    status = "✅ PASS" if success else "❌ FAIL (False Positive)"
    print(f"\n   {status}: Human code {'correctly identified' if success else 'INCORRECTLY flagged as AI'}")
    
    return success


def test_short_snippet():
    """Test with short code snippet"""
    print_header("TEST 4: Short Code Snippet")
    
    code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

print(factorial(5))
"""
    
    print(f"   Code: {code.strip()}")
    
    detector = PlagiarismDetector(use_vector_db=False)
    
    start = time.time()
    report = detector.check_against_submissions(
        submission_text=code,
        submission_id="test-short-001",
        submission_type="code",
        student_name="Short Test",
        files_content=[{"filename": "factorial.py", "content": code}]
    )
    elapsed = time.time() - start
    
    print_results(report, "SHORT CODE SNIPPET")
    print(f"\n   ⏱️  Analysis Time: {elapsed:.2f} seconds")
    
    # Short code is ambiguous - any result is acceptable
    print(f"\n   ℹ️  Short code is ambiguous - originality: {report.overall_originality_score:.1f}%")
    
    return True  # Always pass for short code


def test_internal_plagiarism():
    """Test internal plagiarism detection (duplicate files)"""
    print_header("TEST 5: Internal Plagiarism (Duplicate Files)")
    
    code1 = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = calculate_sum([1, 2, 3, 4, 5])
print(f"Sum: {result}")
"""
    
    code2 = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = calculate_sum([10, 20, 30])
print(f"Total: {result}")
"""
    
    print(f"   File 1 (sum.py): {len(code1)} characters")
    print(f"   File 2 (total.py): {len(code2)} characters")
    print(f"   Expected: HIGH similarity (copied function)")
    
    detector = PlagiarismDetector(use_vector_db=False)
    
    start = time.time()
    report = detector.check_against_submissions(
        submission_text=code1 + "\n\n" + code2,
        submission_id="test-internal-001",
        submission_type="code",
        student_name="Internal Test",
        files_content=[
            {"filename": "sum.py", "content": code1},
            {"filename": "total.py", "content": code2}
        ]
    )
    elapsed = time.time() - start
    
    print_results(report, "INTERNAL PLAGIARISM")
    print(f"\n   ⏱️  Analysis Time: {elapsed:.2f} seconds")
    
    # Should detect internal copying
    has_internal = any(m.match_type == "internal_copy" for m in report.similarity_matches)
    success = has_internal
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n   {status}: Internal plagiarism {'detected' if success else 'NOT detected'}")
    
    return success


def run_all_tests():
    """Run all test cases"""
    print("\n\n")
    print("╔" + "═" * 98 + "╗")
    print("║" + " " * 20 + "🧪 COMPREHENSIVE PLAGIARISM DETECTION TEST SUITE" + " " * 30 + "║")
    print("╚" + "═" * 98 + "╝")
    
    results = {}
    
    # Run tests
    results['AI Calculator'] = test_ai_generated_long_file()
    results['AI Scraper'] = test_ai_generated_scraper()
    results['Human Code'] = test_human_written_code()
    results['Short Snippet'] = test_short_snippet()
    results['Internal Plagiarism'] = test_internal_plagiarism()
    
    # Summary
    print_header("TEST SUITE SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\n   📊 Overall Results:")
    print(f"      Total Tests: {total}")
    print(f"      Passed: {passed} ✅")
    print(f"      Failed: {failed} ❌")
    print(f"      Success Rate: {(passed/total)*100:.1f}%")
    
    print(f"\n   📋 Individual Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"      {status}  {test_name}")
    
    print("\n" + "=" * 100)
    
    if failed == 0:
        print("   🎉 ALL TESTS PASSED! Plagiarism detection is working correctly.")
    else:
        print(f"   ⚠️  {failed} test(s) failed. Review the system configuration.")
    
    print("=" * 100 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
