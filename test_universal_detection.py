"""
Test Universal AI Detection with HTML/JavaScript Code
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

# REAL HTML/JavaScript code with obvious copy-paste errors
html_js_code = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-item: center;  /* TYPO: should be align-items */
            height: 100vh;
            margin: 0;
            background-color: #f4f4f4;
        }
        
        #chatContainer {
            width: 400px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            padding: 20px;
        }
        
        #chatBox {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 10px;
            background-color: #fafafa;
        }
        
        .message {
            padding: 8px;
            margin-bottom: 5px;
            border-radius: 4px;
        }
        
        .user {
            background-color: #d1e7ff;
            text-align: right;
        }
        
        .bot {
            background-color: #e1e1e1;
            text-align: left;
        }
    </style>
</head>
<body>
    <div id="chatContainer">
        <h2>Chat with Bot</h2>
        <div id="chatBox"></div>
        <input type="text" id="userInput" placeholder="Type a message...">
        <button onclick="sendMessage()">Send</button>
    </div>
    
    <script>
        function sendMessage() {
            const userInput = document.querySelector("#userInput").Value;  // TYPO: should be lowercase .value
            
            const chatBox = document.getElementByID("chatBox");  // TYPO: should be getElementById
            
            if (userInput.trim() === "") {
                return;
            }
            
            const userMessage = document.createElement("div");
            userMessage.className = "message user";
            userMessage.textContent = userInput;
            chatBox.appendChild(userMessage);
            
            document.querySelector("#userInput").value = "";
            
            setTimeout(() => {
                const botMessage = document.createElement("div");
                botMessage.className = "message bot";
                botMessage.textContent = "This is a bot response.";
                chatBox.appendChild(botMessage);
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 500);
        }
    </script>
</body>
</html>'''

print("=" * 100)
print("TESTING UNIVERSAL AI DETECTION WITH HTML/JAVASCRIPT")
print("=" * 100)
print("\n🔍 CODE ANALYSIS:")
print("   Language: HTML/JavaScript")
print("   Lines: 79")
print("\n⚠️  OBVIOUS COPY-PASTE ERRORS:")
print("   Line 13: 'align-item' (should be 'align-items')")
print("   Line 61: '.Value' (should be lowercase '.value')")
print("   Line 63: 'getElementByID' (should be 'getElementById')")
print("\n📋 CHARACTERISTICS:")
print("   • Zero comments or documentation")
print("   • Generic naming (chatBox, userInput, sendMessage)")
print("   • Textbook-level organization")
print("   • Mix of perfect structure + careless typos")

detector = PlagiarismDetector(use_vector_db=False)

print("\n⏳ Running AI detection...")
result = detector.detect_ai_generated_code(html_js_code, language="html/javascript")

print("\n" + "=" * 100)
print("📊 DETECTION RESULTS:")
print("=" * 100)
print(f"\n   Is AI Generated: {result.get('is_ai_generated', False)}")
print(f"   Verdict: {result.get('verdict', 'N/A')}")
print(f"   Confidence: {result.get('confidence', 0)}%")
print(f"   AI Tool Signature: {result.get('ai_tool_signature', 'unknown')}")

if 'confidence_breakdown' in result:
    print(f"\n   📊 Confidence Breakdown:")
    breakdown = result.get('confidence_breakdown', {})
    for category, score in breakdown.items():
        if category != 'overall_weighted':
            emoji = "🔴" if score >= 70 else "🟡" if score >= 40 else "🟢"
            print(f"      {emoji} {category}: {score}")

if 'detailed_indicators' in result:
    print(f"\n   🚩 AI Indicators Found:")
    for idx, indicator in enumerate(result.get('detailed_indicators', [])[:5], 1):
        severity = indicator.get('severity', 'unknown')
        evidence = indicator.get('specific_evidence', 'N/A')[:80]
        print(f"      {idx}. [{severity.upper()}] {evidence}")

if 'human_elements' in result:
    human_elems = result.get('human_elements', [])
    if human_elems:
        print(f"\n   ✅ Human Elements Found:")
        for idx, elem in enumerate(human_elems[:3], 1):
            evidence = elem.get('evidence', 'N/A')[:80]
            print(f"      {idx}. {evidence}")

print(f"\n   💬 Explanation: {result.get('detailed_explanation', 'N/A')}")
print(f"\n   📝 Recommendation: {result.get('recommendation', 'N/A')}")

print("\n" + "=" * 100)
if result.get('is_ai_generated', False) or result.get('confidence', 0) >= 60:
    print("✅ SUCCESS: Correctly identified suspicious patterns!")
    print("   The copy-paste errors and generic structure were detected.")
else:
    print("❌ STILL MISSING: Should flag copy-paste AI patterns")
    print(f"   Only {result.get('confidence', 0)}% confidence")
print("=" * 100)
