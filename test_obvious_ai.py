"""
Test with VERY OBVIOUS AI-Generated Python Code
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

# EXTREMELY obvious AI-generated code - using raw string to avoid escaping issues
obvious_ai_code = '''def calculate_factorial(number: int) -> int:
    """
    Calculate the factorial of a given number.
    
    This function computes the factorial of a non-negative integer using
    an iterative approach for optimal performance and stack safety.
    
    Args:
        number (int): The non-negative integer to calculate factorial for.
        
    Returns:
        int: The factorial of the input number.
        
    Raises:
        ValueError: If the input number is negative.
        TypeError: If the input is not an integer.
        
    Examples:
        >>> calculate_factorial(5)
        120
        >>> calculate_factorial(0)
        1
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    # Input validation to ensure the number is an integer
    if not isinstance(number, int):
        raise TypeError("Input must be an integer")
    
    # Validate that the number is non-negative
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    
    # Base case: factorial of 0 is 1
    if number == 0:
        return 1
    
    # Initialize result variable to store the factorial
    result = 1
    
    # Iterate through all numbers from 1 to number (inclusive)
    for i in range(1, number + 1):
        # Multiply result by current number
        result *= i
    
    # Return the calculated factorial
    return result


def validate_input(value) -> bool:
    """
    Validate if the input value is appropriate for factorial calculation.
    
    This helper function performs comprehensive validation checks on the
    input value to ensure it meets all requirements for factorial computation.
    
    Args:
        value: The value to validate.
        
    Returns:
        bool: True if the value is valid, False otherwise.
    """
    # Check if value is None
    if value is None:
        return False
    
    # Verify value is an integer
    if not isinstance(value, int):
        return False
    
    # Ensure value is non-negative
    if value < 0:
        return False
    
    # All checks passed
    return True
'''

print("=" * 100)
print("TESTING WITH EXTREMELY OBVIOUS AI-GENERATED PYTHON CODE")
print("=" * 100)
print(f"\nAI INDICATORS:")
print("  ✓ Massive docstrings for simple function (30+ lines)")
print("  ✓ Type hints everywhere")
print("  ✓ Every possible exception documented")
print("  ✓ Time/Space complexity in docstring")
print("  ✓ Comment for EVERY SINGLE LINE")
print("  ✓ Perfect PEP 8 formatting")
print("  ✓ Validate function for trivial check")
print("  ✓ No shortcuts, no personal style")

detector = PlagiarismDetector(use_vector_db=False)

result = detector.detect_ai_generated_code(obvious_ai_code, language="python")

print(f"\n📊 DETECTION RESULTS:")
print(f"   Is AI Generated: {result.get('is_ai_generated', False)}")
print(f"   Verdict: {result.get('verdict', 'N/A')}")
print(f"   Confidence: {result.get('confidence', 0)}%")

if 'confidence_breakdown' in result:
    print(f"\n   📊 Confidence Breakdown:")
    for category, score in result.get('confidence_breakdown', {}).items():
        print(f"      • {category}: {score}")

print("\n" + "=" * 100)
if result.get('confidence', 0) >= 70:
    print("✅ SUCCESS: Correctly detected as AI-generated")
else:
    print("❌ FAILURE: Should have been flagged as AI!")
    print(f"   Only {result.get('confidence')}% confidence")
print("=" * 100)
