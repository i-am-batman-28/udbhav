"""
Test Universal AI Detection with Natural Text (Essay)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

# AI-generated essay (typical ChatGPT style)
ai_essay = '''
Climate Change: A Comprehensive Analysis

Climate change represents one of the most pressing challenges facing humanity in the 21st century. This phenomenon, characterized by long-term alterations in temperature, precipitation patterns, and other atmospheric conditions, has far-reaching implications for ecosystems, economies, and societies worldwide.

The primary driver of contemporary climate change is the increased concentration of greenhouse gases in the Earth's atmosphere. These gases, including carbon dioxide (CO2), methane (CH4), and nitrous oxide (N2O), trap heat and contribute to the greenhouse effect. Human activities, particularly the burning of fossil fuels, deforestation, and industrial processes, have significantly elevated greenhouse gas levels since the Industrial Revolution.

Scientific evidence for climate change is overwhelming and multifaceted. Temperature records demonstrate a clear warming trend, with the past decade being the warmest on record. Additionally, observable phenomena such as melting polar ice caps, rising sea levels, and shifting wildlife habitats provide tangible evidence of these changes. The Intergovernmental Panel on Climate Change (IPCC) has concluded with high confidence that human activities are the dominant cause of observed warming since the mid-20th century.

The impacts of climate change are diverse and interconnected. Rising temperatures lead to more frequent and severe weather events, including hurricanes, droughts, and heatwaves. These changes affect agricultural productivity, water resources, and human health. Coastal communities face increased risks from sea-level rise and storm surges, while ecosystems experience disruptions in species distribution and biodiversity loss.

Addressing climate change requires comprehensive, coordinated action at multiple levels. Mitigation strategies focus on reducing greenhouse gas emissions through renewable energy adoption, energy efficiency improvements, and sustainable land-use practices. Adaptation measures help communities prepare for and respond to climate impacts. International cooperation, exemplified by agreements such as the Paris Climate Accord, plays a crucial role in coordinating global efforts.

In conclusion, climate change represents a complex, multifaceted challenge that demands urgent attention and action. While the problem is daunting, solutions exist, and collective effort can make a meaningful difference. The transition to a sustainable, low-carbon future requires innovation, policy reform, and individual commitment to environmental stewardship.
'''

# Human-written essay (more natural, with quirks)
human_essay = '''
Climate Change Essay

Climate change is a really big problem today. I think its one of the most important things we need to deal with as a society. The earth is getting warmer and that's causing a lot of issues.

From what I learned in class, greenhouse gases like CO2 are the main cause. When we burn fossil fuels (coal, oil, gas, etc) we release tons of these gases into the air. Its been happening a lot more since factories started becoming common in the 1800s or so.

The evidence is pretty clear at this point - temperatures are rising, ice is melting at the poles, sea levels are going up. I saw a documentary about polar bears struggling to find ice to hunt on, which was pretty sad. Also extreme weather is becoming more common, like those crazy hurricanes we had last year.

There's lots of impacts too. Farming is getting harder in some places because of droughts. Some islands might actually disappear underwater. And people are getting sick from heat waves more often. Its not just an environmental issue, it affects everything.

So what can we do about it? Obviously we need to use less fossil fuels and switch to renewable energy like solar and wind. People can also help by driving less, recycling, eating less meat (apparently cows produce a lot of methane). Countries also signed the Paris Agreement to work together on this.

Overall, climate change is a huge challenge but I'm hopeful we can fix it if everyone works together. We have the technology, we just need the will to actually do something about it. Future generations are counting on us to not mess this up.
'''

print("=" * 100)
print("TESTING UNIVERSAL AI DETECTION WITH NATURAL TEXT")
print("=" * 100)

detector = PlagiarismDetector(use_vector_db=False)

# Test AI-generated essay
print("\n" + "=" * 100)
print("TEST 1: OBVIOUS AI-GENERATED ESSAY")
print("=" * 100)
print("\n📋 CHARACTERISTICS:")
print("   • Perfect grammar and punctuation")
print("   • Academic/formal tone throughout")
print("   • Structured with clear topic sentences")
print("   • No personal voice or informal language")
print("   • Generic phrases like 'comprehensive analysis', 'multifaceted'")

print("\n⏳ Running AI detection...")
result1 = detector.detect_ai_generated_code(ai_essay, language="english essay")

print(f"\n📊 RESULTS:")
print(f"   Is AI Generated: {result1.get('is_ai_generated', False)}")
print(f"   Verdict: {result1.get('verdict', 'N/A')}")
print(f"   Confidence: {result1.get('confidence', 0)}%")
print(f"   Explanation: {result1.get('detailed_explanation', 'N/A')[:200]}")

# Test human-written essay
print("\n" + "=" * 100)
print("TEST 2: HUMAN-WRITTEN ESSAY (with natural quirks)")
print("=" * 100)
print("\n📋 CHARACTERISTICS:")
print("   • Informal tone ('really big problem', 'pretty sad')")
print("   • Grammar errors ('its' vs 'it's')")
print("   • Personal anecdotes ('I saw a documentary')")
print("   • Contractions and casual language")
print("   • Less structured, more conversational")

print("\n⏳ Running AI detection...")
result2 = detector.detect_ai_generated_code(human_essay, language="english essay")

print(f"\n📊 RESULTS:")
print(f"   Is AI Generated: {result2.get('is_ai_generated', False)}")
print(f"   Verdict: {result2.get('verdict', 'N/A')}")
print(f"   Confidence: {result2.get('confidence', 0)}%")
print(f"   Explanation: {result2.get('detailed_explanation', 'N/A')[:200]}")

# Summary
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

ai_detected = result1.get('is_ai_generated', False) or result1.get('confidence', 0) >= 70
human_detected = not result2.get('is_ai_generated', False) or result2.get('confidence', 0) < 50

if ai_detected and human_detected:
    print("✅ SUCCESS: System correctly distinguishes AI from human text!")
    print(f"   AI Essay: {result1.get('confidence', 0)}% confidence")
    print(f"   Human Essay: {result2.get('confidence', 0)}% confidence")
elif ai_detected:
    print("⚠️  PARTIAL: Detected AI essay but may have issues with human text")
elif human_detected:
    print("⚠️  PARTIAL: Detected human essay but may have missed AI patterns")
else:
    print("❌ NEEDS IMPROVEMENT: Detection not working optimally")

print("=" * 100)
