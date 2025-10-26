#!/bin/bash

echo "======================================"
echo "🧪 TESTING AI ENDPOINTS"
echo "======================================"

echo -e "\n1️⃣ Testing Paraphraser..."
curl -s -X POST "http://localhost:8000/api/ai-tools/paraphrase" \
  -H "Content-Type: application/json" \
  -d '{"text": "Machine learning is revolutionizing data analysis."}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Original:', data['original'][:50]); print('✅ Paraphrased:', data['paraphrased'][:50])" 2>/dev/null || echo "❌ Paraphraser failed"

echo -e "\n2️⃣ Testing Grammar Checker..."
curl -s -X POST "http://localhost:8000/api/ai-tools/grammar" \
  -H "Content-Type: application/json" \
  -d '{"text": "Their are many errors in this sentance."}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Original:', data['original']); print('✅ Corrected:', data['corrected']); print('✅ Errors found:', data['error_count'])" 2>/dev/null || echo "❌ Grammar checker failed"

echo -e "\n3️⃣ Testing AI Humanizer..."
curl -s -X POST "http://localhost:8000/api/ai-tools/humanize" \
  -H "Content-Type: application/json" \
  -d '{"text": "It is important to note that artificial intelligence has revolutionized the multifaceted landscape."}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Original AI score:', data['original_ai_score']); print('✅ Humanized AI score:', data['humanized_ai_score']); print('✅ Humanized text:', data['humanized'][:60])" 2>/dev/null || echo "❌ Humanizer failed"

echo -e "\n======================================"
echo "✅ All AI endpoint tests complete!"
echo "======================================"
