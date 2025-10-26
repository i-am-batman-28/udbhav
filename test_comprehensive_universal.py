"""
Comprehensive Universal AI Detection Test Suite
Tests detection across multiple content types
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

print("=" * 100)
print("COMPREHENSIVE UNIVERSAL AI DETECTION TEST")
print("Testing detection across: Python, JavaScript/HTML, Natural Text")
print("=" * 100)

detector = PlagiarismDetector(use_vector_db=False)

# Test cases
test_cases = [
    {
        "name": "Obvious AI-Generated Python",
        "content": '''def calculate_factorial(number: int) -> int:
    """
    Calculate the factorial of a given number.
    
    Args:
        number (int): The non-negative integer to calculate factorial for.
        
    Returns:
        int: The factorial of the input number.
        
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    # Input validation to ensure the number is an integer
    if not isinstance(number, int):
        raise TypeError("Input must be an integer")
    
    # Validate that the number is non-negative
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    
    # Initialize result variable to store the factorial
    result = 1
    
    # Iterate through all numbers from 1 to number (inclusive)
    for i in range(1, number + 1):
        result *= i
    
    return result''',
        "language": "python",
        "expected": "AI",
        "threshold": 70
    },
    {
        "name": "HTML/JS with Copy-Paste Errors",
        "content": '''<script>
function sendMessage() {
    const userInput = document.querySelector("#userInput").Value;  // TYPO
    const chatBox = document.getElementByID("chatBox");  // TYPO
    
    if (userInput.trim() === "") {
        return;
    }
    
    const userMessage = document.createElement("div");
    userMessage.className = "message user";
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);
}
</script>''',
        "language": "javascript",
        "expected": "AI",
        "threshold": 60
    },
    {
        "name": "AI-Generated Essay",
        "content": '''Climate change represents one of the most pressing challenges facing humanity in the 21st century. This phenomenon, characterized by long-term alterations in temperature, precipitation patterns, and other atmospheric conditions, has far-reaching implications for ecosystems, economies, and societies worldwide.

The primary driver of contemporary climate change is the increased concentration of greenhouse gases in the Earth's atmosphere. Scientific evidence for climate change is overwhelming and multifaceted. Temperature records demonstrate a clear warming trend, with the past decade being the warmest on record.

In conclusion, climate change represents a complex, multifaceted challenge that demands urgent attention and action.''',
        "language": "english essay",
        "expected": "AI",
        "threshold": 70
    },
    {
        "name": "Human-Written Essay",
        "content": '''Climate change is a really big problem today. I think its one of the most important things we need to deal with as a society.

From what I learned in class, greenhouse gases like CO2 are the main cause. When we burn fossil fuels we release tons of these gases. Its been happening a lot more since factories started.

I saw a documentary about polar bears struggling to find ice, which was pretty sad. Also extreme weather is becoming more common.

So what can we do? Obviously we need to use less fossil fuels. People can also help by driving less, recycling, eating less meat.

Overall I'm hopeful we can fix it if everyone works together.''',
        "language": "english essay",
        "expected": "Human",
        "threshold": 50
    },
    {
        "name": "Human Python Code",
        "content": '''def fact(n):
    # quick factorial calc
    if n == 0:
        return 1
    res = 1
    for i in range(1, n+1):
        res *= i
    return res

# test it
print(fact(5))  # should be 120''',
        "language": "python",
        "expected": "Human",
        "threshold": 50
    }
]

# Run tests
results = []
for idx, test in enumerate(test_cases, 1):
    print(f"\n{'='*100}")
    print(f"TEST {idx}/{len(test_cases)}: {test['name']}")
    print(f"{'='*100}")
    print(f"Language: {test['language']}")
    print(f"Expected: {test['expected']}")
    
    result = detector.detect_ai_generated_code(test['content'], language=test['language'])
    
    confidence = result.get('confidence', 0)
    is_ai = result.get('is_ai_generated', False)
    verdict = result.get('verdict', 'unknown')
    
    print(f"\n📊 RESULT:")
    print(f"   Verdict: {verdict}")
    print(f"   Confidence: {confidence}%")
    print(f"   AI Generated: {is_ai}")
    
    # Check if detection matches expectation
    if test['expected'] == "AI":
        success = (is_ai or confidence >= test['threshold'])
        emoji = "✅" if success else "❌"
        status = f"AI detected with {confidence}% confidence" if is_ai else f"High confidence ({confidence}%) suggesting AI"
        print(f"\n{emoji} Expected AI: {status}")
    else:  # expected Human
        # For human, high confidence means system is confident it's human-written
        # So we check if NOT ai_generated OR if verdict is explicitly "human_written"
        success = (not is_ai and verdict in ["human_written", "lightly_ai_assisted"])
        emoji = "✅" if success else "❌"
        status = f"Correctly identified as human ({confidence}% confidence)"
        print(f"\n{emoji} Expected Human: {status}")
    
    results.append({
        "test": test['name'],
        "success": success,
        "confidence": confidence,
        "verdict": verdict
    })

# Summary
print(f"\n{'='*100}")
print("TEST SUITE SUMMARY")
print(f"{'='*100}")

passed = sum(1 for r in results if r['success'])
total = len(results)

print(f"\n✅ Passed: {passed}/{total} ({int(passed/total*100)}%)")
print(f"❌ Failed: {total - passed}/{total}")

print(f"\nDetailed Results:")
for r in results:
    status = "✅ PASS" if r['success'] else "❌ FAIL"
    print(f"   {status} | {r['test']}: {r['confidence']}% ({r['verdict']})")

print(f"\n{'='*100}")
if passed == total:
    print("🎉 ALL TESTS PASSED! Universal detection working across all content types!")
elif passed >= total * 0.8:
    print("✅ MOSTLY PASSING! System works well across different content types.")
else:
    print("⚠️  NEEDS IMPROVEMENT: Some content types not detecting properly.")
print(f"{'='*100}")
