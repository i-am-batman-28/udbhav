# 🚀 Quick Start Guide - Peer Review Platform

## Prerequisites

Make sure you have all dependencies installed:

```bash
pip install -r ../requirements.txt
```

## Environment Setup

Create a `.env` file in the `backend/` directory with:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=exam-evaluator

# Application Settings
ENVIRONMENT=development
```

## Starting the Server

### Option 1: Direct Python
```bash
cd /Users/karthiksarma/Desktop/proctoriq\ 2/exam_automator/backend
python main.py
```

### Option 2: Uvicorn (Recommended for Development)
```bash
cd /Users/karthiksarma/Desktop/proctoriq\ 2/exam_automator/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on: **http://localhost:8000**

## Testing the API

### Interactive API Documentation
Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Automated Test Suite
Run the comprehensive test script:

```bash
cd /Users/karthiksarma/Desktop/proctoriq\ 2/exam_automator/backend
python test_api.py
```

This will test:
- ✅ Server health check
- ✅ System statistics
- ✅ Submission upload
- ✅ Code analysis
- ✅ Plagiarism detection
- ✅ Student dashboard
- ✅ All peer review endpoints

### Manual Testing with cURL

#### 1. Upload a Submission
```bash
curl -X POST "http://localhost:8000/api/v1/peer-review/submissions/upload" \
  -F "files=@your_code.py" \
  -F "student_id=student123" \
  -F "student_name=John Doe" \
  -F "student_email=john@example.com" \
  -F "submission_type=code" \
  -F "title=My Project" \
  -F "description=Test submission"
```

#### 2. Check Code Quality
```bash
curl -X POST "http://localhost:8000/api/v1/peer-review/submissions/{submission_id}/analyze-code"
```

#### 3. Check Plagiarism
```bash
curl -X POST "http://localhost:8000/api/v1/peer-review/submissions/{submission_id}/check-plagiarism"
```

#### 4. Get Student Dashboard
```bash
curl "http://localhost:8000/api/v1/peer-review/dashboard/student/{student_id}"
```

## API Endpoints Overview

### Submissions
- `POST /api/v1/peer-review/submissions/upload` - Upload new submission
- `GET /api/v1/peer-review/submissions/{id}` - Get submission details
- `GET /api/v1/peer-review/submissions/student/{student_id}` - Get all submissions by student
- `DELETE /api/v1/peer-review/submissions/{id}` - Delete submission

### Analysis
- `POST /api/v1/peer-review/submissions/{id}/analyze-code` - Run code quality analysis
- `POST /api/v1/peer-review/submissions/{id}/check-plagiarism` - Run plagiarism detection
- `POST /api/v1/peer-review/submissions/{id}/analyze-all` - Run both analyses

### Reviews
- `POST /api/v1/peer-review/submissions/{id}/reviews` - Submit a review
- `GET /api/v1/peer-review/submissions/{id}/reviews` - Get all reviews
- `PUT /api/v1/peer-review/reviews/{review_id}` - Update a review
- `DELETE /api/v1/peer-review/reviews/{review_id}` - Delete a review

### Dashboard & Stats
- `GET /api/v1/peer-review/dashboard/student/{student_id}` - Student dashboard
- `GET /api/v1/peer-review/stats/overview` - System statistics

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --reload --port 8001
```

### Missing Dependencies
```bash
pip install -r ../requirements.txt --upgrade
```

### API Key Issues
Make sure your `.env` file has valid API keys. The system will work with limited functionality if keys are missing:
- Without OpenAI key: No AI feedback in code analysis
- Without Pinecone key: Limited plagiarism detection (no semantic search)

### Import Errors
Make sure you're in the backend directory:
```bash
cd /Users/karthiksarma/Desktop/proctoriq\ 2/exam_automator/backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python main.py
```

## Next Steps

1. ✅ Start the server
2. ✅ Run `python test_api.py` to verify all endpoints
3. ✅ Check http://localhost:8000/docs for interactive testing
4. ⏭️ Update frontend to use new API endpoints
5. ⏭️ Create peer review UI components

## Server Logs

Watch the console for:
- 🟢 `Application startup complete` - Server is ready
- 🔵 `INFO` - Request logs
- 🟡 `WARNING` - Non-critical issues
- 🔴 `ERROR` - Errors that need attention

Happy coding! 🎉
