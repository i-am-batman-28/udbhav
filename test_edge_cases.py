"""
Edge Case Testing: Advanced Scenarios
Tests challenging cases and mixed content
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

print("=" * 100)
print("EDGE CASE TESTING: ADVANCED AI DETECTION SCENARIOS")
print("=" * 100)

detector = PlagiarismDetector(use_vector_db=False)

# Test Case 1: Mixed AI and Human (AI refined by human)
mixed_code = '''import React, { useState } from 'react';

// My custom hook for form handling
function useFormData(initialValues) {
    const [formData, setFormData] = useState(initialValues);
    
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };
    
    return [formData, handleChange];
}

// Quick login component I made
const LoginForm = () => {
    const [form, handleInputChange] = useFormData({
        email: '',
        password: ''
    });
    
    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('submitting...', form);
        // TODO: add actual API call
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input 
                name="email" 
                value={form.email} 
                onChange={handleInputChange}
                placeholder="Email"
            />
            <input 
                type="password"
                name="password" 
                value={form.password} 
                onChange={handleInputChange}
            />
            <button type="submit">Login</button>
        </form>
    );
};

export default LoginForm;'''

print("\n" + "=" * 100)
print("TEST 1: MIXED AI/HUMAN CODE (AI base + human modifications)")
print("=" * 100)
print("Characteristics:")
print("  • Clean structure (AI-like)")
print("  • Personal comments ('My custom hook', 'Quick login component I made')")
print("  • TODO notes (human)")
print("  • Mix of styles")

result1 = detector.detect_ai_generated_code(mixed_code, language="javascript")
print(f"\n📊 RESULT:")
print(f"   Verdict: {result1.get('verdict')}")
print(f"   Confidence: {result1.get('confidence')}%")
print(f"   Expected: Should detect as 'lightly_ai_assisted' or 'heavily_ai_assisted'")

# Test Case 2: Beginner Code (naturally imperfect)
beginner_code = '''# my first python program for calculating grades

def calc_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

# test
score1 = 85
grade = calc_grade(score1)
print("Grade is:", grade)

score2 = 92
print("Grade is:", calc_grade(score2))

# another test
print(calc_grade(55))'''

print("\n" + "=" * 100)
print("TEST 2: BEGINNER CODE (naturally simple and imperfect)")
print("=" * 100)
print("Characteristics:")
print("  • Simple, straightforward approach")
print("  • No docstrings or type hints")
print("  • Informal comments")
print("  • Repetitive test code")
print("  • No error handling")

result2 = detector.detect_ai_generated_code(beginner_code, language="python")
print(f"\n📊 RESULT:")
print(f"   Verdict: {result2.get('verdict')}")
print(f"   Confidence: {result2.get('confidence')}%")
print(f"   Expected: Should detect as 'human_written'")

# Test Case 3: ChatGPT-style explanation text
chatgpt_text = '''To implement a binary search algorithm, follow these steps:

First, ensure that the input array is sorted. This is a prerequisite for binary search to function correctly.

Next, initialize two pointers: left and right. The left pointer should start at index 0, while the right pointer should start at the last index of the array.

Then, enter a while loop that continues as long as left is less than or equal to right. Within this loop, calculate the middle index using the formula: mid = left + (right - left) // 2.

Compare the element at the middle index with the target value. If they are equal, return the middle index. If the middle element is less than the target, update the left pointer to mid + 1. Otherwise, update the right pointer to mid - 1.

If the loop completes without finding the target, return -1 to indicate that the element is not present in the array.

This algorithm achieves O(log n) time complexity, making it highly efficient for large datasets.'''

print("\n" + "=" * 100)
print("TEST 3: CHATGPT-STYLE INSTRUCTIONAL TEXT")
print("=" * 100)
print("Characteristics:")
print("  • Step-by-step instructions")
print("  • Formal, educational tone")
print("  • Perfect grammar and structure")
print("  • Generic phrasing")
print("  • No personal voice")

result3 = detector.detect_ai_generated_code(chatgpt_text, language="instructional text")
print(f"\n📊 RESULT:")
print(f"   Verdict: {result3.get('verdict')}")
print(f"   Confidence: {result3.get('confidence')}%")
print(f"   Expected: Should detect as 'ai_generated'")

# Test Case 4: CSS with copy-paste errors
css_code = '''/* Main container styles */
.container {
    display: flex;
    justify-content: center;
    align-item: center;  /* TYPO: should be align-items */
    height: 100vh;
    background-color: #f0f0f0;
}

.card {
    padding: 20px;
    border-raduis: 8px;  /* TYPO: should be border-radius */
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    background-color: white;
}

.button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    curor: pointer;  /* TYPO: should be cursor */
    font-size: 14px;
}

.button:hover {
    background-color: #0056b3;
    tranform: scale(1.05);  /* TYPO: should be transform */
}'''

print("\n" + "=" * 100)
print("TEST 4: CSS WITH MULTIPLE COPY-PASTE ERRORS")
print("=" * 100)
print("Characteristics:")
print("  • Perfect structure")
print("  • Multiple typos: align-item, border-raduis, curor, tranform")
print("  • Generic class names")
print("  • Professional organization")

result4 = detector.detect_ai_generated_code(css_code, language="css")
print(f"\n📊 RESULT:")
print(f"   Verdict: {result4.get('verdict')}")
print(f"   Confidence: {result4.get('confidence')}%")
print(f"   Expected: Should detect copy-paste patterns")

# Test Case 5: Code with personal quirks (definitely human)
quirky_code = '''# my quick & dirty solution for parsing dates
# yeah i know there are libraries but whatever

def parse_date(date_str):
    # assuming format is mm/dd/yyyy cuz thats what i got
    parts = date_str.split('/')
    if len(parts) != 3:
        return None  # meh, invalid
    
    m, d, y = parts
    
    # convert to ints, hope it works lol
    try:
        month = int(m)
        day = int(d)
        year = int(y)
    except:
        return None  # whatever
    
    # basic checks i guess
    if month < 1 or month > 12:
        return None
    if day < 1 or day > 31:  # close enough
        return None
    
    return {'month': month, 'day': day, 'year': year}

# testing
print(parse_date("12/25/2024"))
print(parse_date("invalid"))  # should be None'''

print("\n" + "=" * 100)
print("TEST 5: CODE WITH STRONG PERSONAL STYLE")
print("=" * 100)
print("Characteristics:")
print("  • Informal comments ('lol', 'whatever', 'meh')")
print("  • Casual language ('quick & dirty', 'hope it works')")
print("  • Bare except clause (bad practice)")
print("  • Personal shortcuts and assumptions")
print("  • Conversational tone throughout")

result5 = detector.detect_ai_generated_code(quirky_code, language="python")
print(f"\n📊 RESULT:")
print(f"   Verdict: {result5.get('verdict')}")
print(f"   Confidence: {result5.get('confidence')}%")
print(f"   Expected: Should strongly detect as 'human_written'")

# Summary
print("\n" + "=" * 100)
print("EDGE CASE TEST SUMMARY")
print("=" * 100)

results = [
    ("Mixed AI/Human", result1, "lightly_ai_assisted or heavily_ai_assisted"),
    ("Beginner Code", result2, "human_written"),
    ("ChatGPT Instructions", result3, "ai_generated"),
    ("CSS with Typos", result4, "heavily_ai_assisted"),
    ("Quirky Human Code", result5, "human_written")
]

print("\nResults:")
for name, result, expected in results:
    verdict = result.get('verdict', 'unknown')
    confidence = result.get('confidence', 0)
    matches = verdict in expected
    emoji = "✅" if matches else "⚠️"
    print(f"   {emoji} {name}: {verdict} ({confidence}%)")
    print(f"      Expected: {expected}")

print("=" * 100)
