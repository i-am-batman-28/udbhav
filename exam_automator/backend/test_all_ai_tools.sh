#!/bin/bash

echo "========================================"
echo "TESTING ALL 5 AI TOOLS"
echo "========================================"

echo ""
echo "=== TEST 1: PARAPHRASER ==="
curl -X POST http://localhost:8000/api/ai-tools/paraphrase \
  -H "Content-Type: application/json" \
  -d '{"text": "Machine learning is revolutionizing data analysis.", "style": "academic"}' \
  2>/dev/null | python3 -m json.tool
echo ""

echo ""
echo "=== TEST 2: GRAMMAR CHECKER ==="
curl -X POST http://localhost:8000/api/ai-tools/grammar-check \
  -H "Content-Type: application/json" \
  -d '{"text": "Their are many errors in this sentance."}' \
  2>/dev/null | python3 -m json.tool
echo ""

echo ""
echo "=== TEST 3: AI HUMANIZER ==="
curl -X POST http://localhost:8000/api/ai-tools/humanize \
  -H "Content-Type: application/json" \
  -d '{"text": "It is important to note that artificial intelligence has revolutionized technology.", "tone": "casual"}' \
  2>/dev/null | python3 -m json.tool
echo ""

echo ""
echo "=== TEST 4: AI DETECTOR ==="
curl -X POST http://localhost:8000/api/ai-tools/detect-ai \
  -H "Content-Type: application/json" \
  -d '{"text": "Machine learning algorithms process data through neural networks to identify patterns.", "submission_type": "writeup"}' \
  2>/dev/null | python3 -m json.tool
echo ""

echo ""
echo "=== TEST 5: PLAGIARISM CHECKER ==="
curl -X POST http://localhost:8000/api/ai-tools/check-plagiarism \
  -H "Content-Type: application/json" \
  -d '{"text": "Machine learning algorithms process data through neural networks to identify patterns.", "submission_type": "writeup"}' \
  2>/dev/null | python3 -m json.tool
echo ""

echo ""
echo "========================================"
echo "ALL TESTS COMPLETE!"
echo "========================================"
