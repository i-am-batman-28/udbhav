# Intelligent Real-Time Recommendations System

## 🎯 Overview
Replaced **template-based** plagiarism recommendations with **AI-powered real-time analysis** using Groq LLM. The system now generates contextual, specific recommendations based on actual submission findings, not generic templates.

---

## ❌ Previous Problem

**Template-Based Recommendations** (Static & Generic):
```python
if ai_generated:
    recommendations.append(
        f"**AI-GENERATED CONTENT DETECTED** ({len(ai_generated)} detections):\n"
        f"   • Generic template message\n"
        f"   • Same text for all cases\n"
        f"   • No context-specific analysis"
    )
```

**Issues**:
- ❌ Same recommendations for different situations
- ❌ No analysis of actual code/content
- ❌ Generic action items not specific to findings
- ❌ No consideration of context or severity
- ❌ Felt robotic and pre-made

---

## ✅ New Solution: Intelligent Recommendations

### Architecture

```
Plagiarism Findings
        ↓
IntelligentRecommendationGenerator
        ↓
Groq LLM (llama-3.3-70b-versatile)
        ↓
Real-Time Context-Aware Recommendations
```

### Key Components

**1. `intelligent_recommendations.py`** (New Service)
- `IntelligentRecommendationGenerator` class
- Uses Groq LLM to analyze findings
- Generates contextual recommendations
- Includes fallback for reliability

**2. Updated `plagiarism_detector.py`**
- Integrates intelligent generator
- Converts match data for LLM
- Falls back gracefully on errors

---

## 🔥 Key Features

### 1. **Context-Aware Analysis**
The LLM receives:
- Actual originality score
- Real match data with excerpts
- Submission type (code/writeup)
- Confidence levels
- Sample content from matches

### 2. **Dynamic Content Generation**
Example findings sent to LLM:
```
**Originality Score**: 45.0%
**Submission Type**: code
**Total Matches**: 2

**AI-Generated Content**: 1 detections
  - File: StudentWork.py
    Confidence: 85.0%
    Sample: def calculate_grade(score):
            if score >= 90:
                return "A"
            ...

**Internal Duplication**: 1 matches
  - Similarity: 88.0%
    With: utils.py
    Sample: class DataProcessor:
            def __init__(self):
            ...
```

### 3. **Structured Output**
The LLM generates:

1. **ASSESSMENT** - Risk level with reasoning
2. **DETAILED FINDINGS** - Analysis by category with specific examples
3. **REQUIRED ACTIONS** - Numbered, context-specific steps
4. **BEST PRACTICES** - Relevant to submission type and findings
5. **RECOMMENDED NEXT STEPS** - 5-step action plan for concerning cases

---

## 📊 Example Output

### Sample Input
- Originality: 45%
- AI-Generated detection in `StudentWork.py` (85% confidence)
- Internal duplication with `utils.py` (88% similarity)

### Generated Recommendations

```markdown
### ASSESSMENT
The originality score of 45.0% indicates a HIGH RISK of plagiarism and academic 
integrity concerns. The presence of AI-generated content and internal duplication 
suggests that the student's submission may not be entirely their own work.

### DETAILED FINDINGS
* **AI-Generated Content**: The detection of AI-generated content in the 
  `StudentWork.py` file with a confidence level of 85.0% suggests that the 
  student may have used artificial intelligence tools to generate parts of 
  their code. The sample provided, `def calculate_grade(score):`, is a common 
  algorithm that could be independently implemented, but the high confidence 
  level indicates a strong likelihood of AI-generated content.

* **Internal Duplication**: The similarity of 88.0% between the submitted code 
  and `utils.py` indicates a high degree of duplication. The sample provided, 
  `class DataProcessor:`, suggests that the student may have copied and pasted 
  code from another source or reused their own code without proper citation.

### REQUIRED ACTIONS
1. Review the `StudentWork.py` file to determine the extent of AI-generated 
   content and assess whether it is acceptable in the context of the assignment.
2. Investigate the similarity between the submitted code and `utils.py` to 
   determine whether the duplication is due to legitimate reuse of code or 
   plagiarism.
3. Meet with the student to discuss the findings and determine whether they 
   understand the implications of AI-generated content and internal duplication.
4. Consider re-evaluating the assignment to ensure that it is clear what 
   constitutes acceptable use of external resources and code reuse.

### BEST PRACTICES
1. Provide clear guidelines on acceptable use of external resources, including 
   AI-generated content and code reuse, in the assignment instructions.
2. Encourage students to properly cite any reused code or algorithms, even if 
   they are independently implemented.
3. Use plagiarism detection tools to monitor submissions and address any 
   concerns promptly.
4. Offer resources and support to help students understand the importance of 
   academic integrity and proper citation practices.

### RECOMMENDED NEXT STEPS
1. **Review the assignment instructions** to ensure they are clear and concise 
   regarding acceptable use of external resources and code reuse.
2. **Meet with the student** to discuss the findings and determine whether they 
   understand the implications of AI-generated content and internal duplication.
3. **Re-evaluate the submission** to assess whether the AI-generated content 
   and internal duplication are acceptable in the context of the assignment.
4. **Develop a plan to prevent similar incidents** in the future, including 
   providing additional resources and support to students on academic integrity.
5. **Document the incident** and any subsequent actions taken, including 
   meetings with the student and any changes made to the assignment instructions.
```

---

## 🎯 Benefits

### For Instructors
✅ **Specific & Actionable** - References actual files and code samples
✅ **Context-Aware** - Considers submission type and severity
✅ **Professional** - Academic language, no emojis
✅ **Balanced** - Fair assessment considering legitimate use cases
✅ **Educational** - Constructive feedback, not just punitive

### For Students (Indirect)
✅ Better-informed decisions from instructors
✅ More accurate assessment of their work
✅ Clearer understanding of academic integrity expectations

---

## 🔧 Technical Details

### LLM Configuration
```python
model = "llama-3.3-70b-versatile"
temperature = 0.3  # Low for consistency
max_tokens = 1500  # Comprehensive recommendations
```

### System Prompt
```
You are an expert academic integrity advisor helping instructors understand 
plagiarism detection results. Generate clear, actionable, professional 
recommendations based on the findings. Be constructive, fair, and educational. 
Format using markdown with clear sections. NO EMOJIS. Use professional 
academic language.
```

### Fallback Strategy
If Groq API fails:
1. Catches exception
2. Falls back to `_generate_basic_recommendations()`
3. Provides simplified but structured output
4. Ensures system always returns recommendations

---

## 🧪 Testing

### Test Script
```bash
cd /Users/karthiksarma/Desktop/proctoriq\ 2/exam_automator/backend
python3 services/intelligent_recommendations.py
```

### Integration Test
Upload a submission → Trigger plagiarism check → View recommendations

---

## 📁 Files Modified

### New Files
- `services/intelligent_recommendations.py` (240 lines)
  - `IntelligentRecommendationGenerator` class
  - `generate_recommendations()` method
  - `_prepare_findings_summary()` helper
  - `_create_recommendation_prompt()` helper
  - `_generate_fallback_recommendations()` method
  - Singleton pattern with `get_recommendation_generator()`

### Modified Files
- `services/plagiarism_detector.py`
  - Imported `get_recommendation_generator()`
  - Updated `_generate_recommendations()` to use intelligent system
  - Kept original logic as `_generate_basic_recommendations()` fallback

---

## 🚀 Next Steps

### Immediate
1. ✅ Test with real submissions
2. ✅ Verify recommendations are context-specific
3. ✅ Check fallback behavior

### Future Enhancements
- [ ] Cache common recommendation patterns
- [ ] Track recommendation quality metrics
- [ ] Add instructor feedback loop
- [ ] Multi-language support for recommendations
- [ ] Integration with grading rubrics

---

## 💡 Key Takeaway

> **Before**: "Your submission has 1 AI-generated detection. Take action."
> 
> **After**: "The `StudentWork.py` file shows 85% confidence of AI-generated content in the `calculate_grade()` function. While this algorithm could be independently implemented, the high confidence level combined with perfect formatting and generic naming patterns suggests AI assistance. Review the specific function and interview the student about their development process."

The recommendations are now **truly intelligent**, analyzing actual content and providing **actionable, context-aware guidance** rather than generic templates.
