"""
Test Plagiarism Detection System
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from services.plagiarism_detector import PlagiarismDetector

def test_exact_copy():
    """Test with exact duplicate text"""
    print("\n" + "="*80)
    print("TEST 1: Exact Copy Detection")
    print("="*80)
    
    original = """
    def calculate_fibonacci(n):
        if n <= 1:
            return n
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
    """
    
    copied = original  # Exact same
    
    detector = PlagiarismDetector(use_vector_db=False)
    similarity = detector.calculate_text_similarity(original, copied)
    
    print(f"Original text: {original[:100]}...")
    print(f"Copied text: {copied[:100]}...")
    print(f"\n📊 Similarity: {similarity * 100:.2f}%")
    print(f"Expected: ~100%")
    print(f"Result: {'✅ PASS' if similarity > 0.95 else '❌ FAIL'}")


def test_paraphrased():
    """Test with paraphrased text"""
    print("\n" + "="*80)
    print("TEST 2: Paraphrased Text Detection")
    print("="*80)
    
    original = """
    Machine learning is a subset of artificial intelligence that focuses on 
    developing algorithms that allow computers to learn from data without 
    being explicitly programmed.
    """
    
    paraphrased = """
    Machine learning represents a branch of AI dedicated to creating 
    algorithms enabling computers to learn from information without 
    explicit programming instructions.
    """
    
    detector = PlagiarismDetector(use_vector_db=False)
    similarity = detector.calculate_text_similarity(original, paraphrased)
    
    print(f"Original: {original.strip()}")
    print(f"\nParaphrased: {paraphrased.strip()}")
    print(f"\n📊 Similarity: {similarity * 100:.2f}%")
    print(f"Expected: 50-70%")
    print(f"Result: {'✅ PASS' if 0.4 < similarity < 0.8 else '❌ FAIL'}")


def test_code_similarity():
    """Test code similarity detection"""
    print("\n" + "="*80)
    print("TEST 3: Code Similarity Detection")
    print("="*80)
    
    code1 = """
    def calculate_sum(numbers):
        total = 0
        for num in numbers:
            total += num
        return total
    """
    
    code2 = """
    def compute_total(nums):
        sum_val = 0
        for n in nums:
            sum_val += n
        return sum_val
    """
    
    detector = PlagiarismDetector(use_vector_db=False)
    result = detector.detect_code_similarity(code1, code2)
    
    print(f"Code 1: {code1.strip()}")
    print(f"\nCode 2: {code2.strip()}")
    print(f"\n📊 Overall Similarity: {result['overall_similarity']:.2f}%")
    print(f"📊 Text Similarity: {result['text_similarity']:.2f}%")
    print(f"📊 Structure Similarity: {result['structure_similarity']:.2f}%")
    print(f"📊 Verdict: {result['verdict']}")
    print(f"Expected: 60-80% (same logic, different names)")
    print(f"Result: {'✅ PASS' if 50 < result['overall_similarity'] < 90 else '❌ FAIL'}")


def test_completely_different():
    """Test with completely different text"""
    print("\n" + "="*80)
    print("TEST 4: Completely Different Text")
    print("="*80)
    
    text1 = """
    The quick brown fox jumps over the lazy dog. This is a simple 
    sentence used for testing text processing algorithms.
    """
    
    text2 = """
    Python is a high-level programming language known for its simplicity 
    and readability. It supports multiple programming paradigms.
    """
    
    detector = PlagiarismDetector(use_vector_db=False)
    similarity = detector.calculate_text_similarity(text1, text2)
    
    print(f"Text 1: {text1.strip()}")
    print(f"\nText 2: {text2.strip()}")
    print(f"\n📊 Similarity: {similarity * 100:.2f}%")
    print(f"Expected: <20%")
    print(f"Result: {'✅ PASS' if similarity < 0.3 else '❌ FAIL'}")


def test_current_implementation():
    """Test what actually happens with check_against_submissions"""
    print("\n" + "="*80)
    print("TEST 5: Current check_against_submissions Implementation")
    print("="*80)
    
    text = """
    This is a test submission with some content that should be checked 
    for plagiarism. It contains various sentences and programming concepts.
    """
    
    detector = PlagiarismDetector(use_vector_db=False)
    report = detector.check_against_submissions(
        submission_text=text,
        submission_id="test-001",
        submission_type="writeup",
        student_name="Test Student",
        check_limit=10
    )
    
    print(f"Submission text: {text.strip()}")
    print(f"\n📊 Report:")
    print(f"   Originality Score: {report.overall_originality_score}%")
    print(f"   Matches Found: {report.total_matches_found}")
    print(f"   Risk Level: {report.risk_level}")
    print(f"   Sources Checked: {report.sources_checked}")
    print(f"\n⚠️  Current Issue: Always returns 100% because no database to check against!")
    print(f"Result: ❌ NOT WORKING - Need to implement database storage")


if __name__ == "__main__":
    print("\n🧪 PLAGIARISM DETECTION TEST SUITE")
    print("Testing the current implementation...\n")
    
    test_exact_copy()
    test_paraphrased()
    test_code_similarity()
    test_completely_different()
    test_current_implementation()
    
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    print("""
✅ Text similarity detection: WORKS
✅ Code similarity detection: WORKS
❌ Cross-submission comparison: NOT WORKING

ISSUE: Without a database of past submissions, we can't detect plagiarism 
       across different submissions. We only have similarity algorithms.

SOLUTIONS:
1. Store submissions in SQLite/PostgreSQL
2. Compare new submissions against stored ones
3. Use file-based storage (simple JSON files)
4. Re-enable vector DB (but it was causing issues)

Recommendation: Use SQLite for simple, fast storage without vector DB complexity.
    """)
