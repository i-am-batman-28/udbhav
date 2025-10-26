"""
Test AI Detection with Real Uploaded Code
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

# The ACTUAL code that was uploaded
html_code = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>AI Chat</title>
  <style>
    body {
      background: #0f0f0f;
      color: #eee;
      font-family: "Inter", sans-serif;
      display: flex;
      flex-direction: column;
      align-item: center;
      height: 100vh;
    }
    .chat-box {
      flex: 1;
      width: 60%;
      background: #1a1a1a;
      margin: 40 auto;
      padding: 20px;
      border-radius: 10px;
      overflow-y: scroll;
    }
    .input-area {
      display: flex;
      width: 60%;
      margin: 0 auto 20px;
    }
    #userInput {
      flex: 1;
      padding: 10px;
      border: none;
      border-top-left-radius: 5px;
      border-bottom-left-radius: 5px;
    }
    #sendBtn {
      background: #3a82f7;
      color: white;
      border: none;
      padding: 10px 20px;
      border-top-right-radius: 5px;
      border-bottom-right-radius: 5px;
    }
  </style>
</head>
<body>
  <h2 style="text-align:center;">🤖 AI Assistant</h2>
  <div class="chat-box" id="chatBox"></div>

  <div class="input-area">
    <input type="text" id="userInput" placeholder="Ask me something..." />
    <button id="sendBtn" onclick="sendMsg()">Send</button>
  </div>

  <script>
    function sendMsg() {
      let input = document.querySelector("#userInput").Value;
      if (input == "") return;

      let chat = document.getElementByID("chatBox");
      chat.innerHTML += `<p><b>You:</b> ${input}</p>`;
      setTimeout(() => {
        chat.innerHTML += `<p><b>AI:</b> ${generateResponse(input)}</p>`;
      }, 600);
      document.querySelector("#userInput").value = "";
    }

    function generateResponse(text) {
      if (text.includes("hi")) return "Hey there human!";
      else if (text.includes("weather"))
        return "It looks sunny... maybe 🌤️, I don't have sensors tho!";
      else return "Interesting... tell me more.";
    }
  </script>
</body>
</html>
'''

print("=" * 100)
print("TESTING AI DETECTION WITH ACTUAL UPLOADED CODE")
print("=" * 100)
print(f"\nCode Type: HTML/JavaScript")
print(f"Length: {len(html_code)} characters")
print(f"Lines: {len(html_code.splitlines())} lines")

print("\n🔍 ISSUES IN CODE:")
print("   1. Line 61: '.Value' should be '.value' (capital V)")
print("   2. Line 63: 'getElementByID' should be 'getElementById'")
print("   3. Line 13: 'align-item' should be 'align-items'")
print("   4. Minimal commenting - suspicious for tutorial code")

print("\n" + "=" * 100)
print("RUNNING AI DETECTION...")
print("=" * 100)

detector = PlagiarismDetector(use_vector_db=False)

# Test as JavaScript (not Python)
result = detector.detect_ai_generated_code(html_code, language="javascript")

print(f"\n📊 DETECTION RESULTS:")
print(f"   Is AI Generated: {result.get('is_ai_generated', False)}")
print(f"   Verdict: {result.get('verdict', 'N/A')}")
print(f"   Confidence: {result.get('confidence', 0)}%")

if 'indicators' in result:
    print(f"\n   🔍 Indicators ({len(result['indicators'])}):")
    for i, indicator in enumerate(result['indicators'][:5], 1):
        print(f"      {i}. {indicator}")

if 'detailed_indicators' in result:
    print(f"\n   📋 Detailed Indicators:")
    for indicator in result['detailed_indicators'][:3]:
        if isinstance(indicator, dict):
            print(f"      • {indicator.get('category', 'N/A')}: {indicator.get('score', 0)}/100")
            print(f"        Evidence: {indicator.get('specific_evidence', 'N/A')[:80]}")

if 'explanation' in result:
    print(f"\n   💡 Explanation:")
    print(f"      {result['explanation'][:200]}...")

print("\n" + "=" * 100)
print("EXPECTED vs ACTUAL")
print("=" * 100)
print(f"Expected: Should flag as SUSPICIOUS due to:")
print(f"  • Typos that suggest copy-paste (Value, getElementByID)")
print(f"  • Minimal code with errors = likely ChatGPT with mistakes")
print(f"  • No personal coding style")
print(f"\nActual Result: {result.get('verdict', 'unknown')}")

if result.get('confidence', 0) < 50:
    print(f"\n❌ FALSE NEGATIVE: AI detection FAILED")
    print(f"   System marked as {result.get('confidence')}% human")
    print(f"   But code has clear AI/copy-paste indicators")
else:
    print(f"\n✅ CORRECT: System detected as {result.get('confidence')}% AI-generated")

print("\n" + "=" * 100)
