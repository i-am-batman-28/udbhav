# 🚀 Authentication & FAISS Migration - Complete Setup Guide

## ✅ What's Been Implemented

### Backend (100% Complete)
- ✅ MongoDB integration with Motor (async)
- ✅ User authentication (bcrypt + JWT)
- ✅ Role-based access control (student/teacher)
- ✅ FAISS local vector store (replaces Pinecone)
- ✅ Authentication API endpoints
- ✅ JWT middleware for protected routes
- ✅ Updated requirements.txt and .env.example

### Cost Savings
- **Before**: $840/year (Pinecone) + API costs
- **After**: $0/year (100% free with MongoDB Atlas free tier + FAISS)

---

## 📦 Installation & Setup

### 1. Install Dependencies

```bash
cd exam_automator
pip install motor pymongo bcrypt pyjwt faiss-cpu sentence-transformers groq
```

Or update all dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### 2. Set Up MongoDB

#### Option A: Local MongoDB (Development)
```bash
# Install MongoDB (macOS)
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community
```

#### Option B: MongoDB Atlas (Recommended - Free Cloud)
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free cluster (512MB storage)
3. Create database user and password
4. Whitelist your IP (or use 0.0.0.0/0 for development)
5. Get connection string

### 3. Configure Environment Variables

Copy and update your `.env` file:

```bash
cd exam_automator/backend
cp .env.example .env
```

Edit `.env`:
```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017  # Local
# Or for MongoDB Atlas:
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/

DATABASE_NAME=proctoriq

# JWT Authentication (IMPORTANT: Change this!)
JWT_SECRET=your-super-secret-key-here-use-long-random-string-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Groq API (Free)
GROQ_API_KEY=your_groq_api_key_here

# FAISS Vector Store (Local)
FAISS_INDEX_PATH=data/faiss_index
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 4. Generate Strong JWT Secret

```bash
# Generate a secure random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output to your `JWT_SECRET` in `.env`.

---

## 🔐 Authentication System Usage

### API Endpoints

#### 1. Register a New User

```bash
# Register a student
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePassword123",
    "role": "student",
    "name": "John Doe",
    "student_id": "STU001"
  }'

# Register a teacher
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "SecurePassword123",
    "role": "teacher",
    "name": "Dr. Jane Smith"
  }'
```

#### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePassword123"
  }'
```

Response:
```json
{
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "student@example.com",
    "role": "student",
    "name": "John Doe",
    "student_id": "STU001"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

#### 3. Access Protected Routes

```bash
# Use the token in Authorization header
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

#### 4. Student-Only Route (Example)

```bash
curl -X GET http://localhost:8000/api/auth/student-only \
  -H "Authorization: Bearer STUDENT_TOKEN"
```

#### 5. Teacher-Only Route (Example)

```bash
curl -X GET http://localhost:8000/api/auth/teacher-only \
  -H "Authorization: Bearer TEACHER_TOKEN"
```

---

## 💾 FAISS Vector Store Usage

### Adding Submissions to Vector Store

```python
from db.faiss_store import get_vector_store

# Get vector store instance
vector_store = get_vector_store()

# Add a submission
vector_store.add_submission(
    submission_id="uuid-here",
    text="Code or text content",
    user_id="user_id_from_mongodb",
    file_name="main.py",
    metadata={"language": "python", "timestamp": "2025-10-26"}
)
```

### Searching for Similar Submissions

```python
# Search for similar code (cross-student plagiarism check)
results = vector_store.search_similar(
    text="Student's submitted code",
    k=5,  # Top 5 matches
    exclude_user_id="current_user_id"  # Don't match their own submissions
)

for result in results:
    print(f"Match: {result['file_name']}")
    print(f"User: {result['user_id']}")
    print(f"Similarity: {result['similarity']:.2%}")
```

### Vector Store Statistics

```python
stats = vector_store.get_stats()
print(stats)
# Output:
# {
#   "total_submissions": 150,
#   "index_dimension": 384,
#   "index_type": "IndexFlatL2",
#   "index_size_mb": 2.3,
#   "unique_users": 45
# }
```

---

## 🗄️ MongoDB Collections

### Users Collection
```javascript
{
  "_id": ObjectId("..."),
  "email": "student@example.com",
  "password_hash": "$2b$12$...",  // bcrypt hash
  "role": "student",  // or "teacher"
  "name": "John Doe",
  "student_id": "STU001",  // unique, only for students
  "created_at": ISODate("2025-10-26T..."),
  "updated_at": ISODate("2025-10-26T..."),
  "is_active": true,
  "last_login": ISODate("2025-10-26T...")
}
```

### Submissions Collection
```javascript
{
  "_id": ObjectId("..."),
  "submission_id": "uuid-here",
  "user_id": ObjectId("..."),  // Reference to users collection
  "file_name": "main.py",
  "file_path": "/uploads/uuid/main.py",
  "file_type": "text/x-python",
  "file_size": 1024,
  "content": "def hello():\n    print('Hello')",
  "created_at": ISODate("2025-10-26T..."),
  "status": "completed"
}
```

### Analysis Results Collection
```javascript
{
  "_id": ObjectId("..."),
  "submission_id": "uuid-here",
  "user_id": ObjectId("..."),
  "ai_detection": {
    "classification": "human_written",
    "confidence": 0.85,
    "reasoning": "Natural coding patterns...",
    "patterns_detected": ["casual_comments", "abbreviations"]
  },
  "plagiarism": {
    "originality_score": 92.5,
    "risk_level": "low",
    "matches": [],
    "cross_submission_matches": [
      {
        "submission_id": "other-uuid",
        "similarity": 0.45,
        "user_id": "other-user-id"
      }
    ]
  },
  "created_at": ISODate("2025-10-26T...")
}
```

---

## 🧪 Testing the System

### 1. Start the Backend

```bash
cd exam_automator/backend
python main.py
```

You should see:
```
🚀 Starting ProctorIQ API...
✅ Connected to MongoDB: proctoriq
✅ Database indexes created
✅ FAISS vector store initialized with 0 vectors
✅ All services initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test Authentication

```bash
# Register a test student
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@student.com",
    "password": "Test123!",
    "role": "student",
    "name": "Test Student",
    "student_id": "TEST001"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@student.com",
    "password": "Test123!"
  }'

# Save the token from response and test protected route
TOKEN="paste_token_here"
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test FAISS Vector Store

```python
# In Python REPL
from db.faiss_store import get_vector_store

vector_store = get_vector_store()

# Add test submission
vector_store.add_submission(
    submission_id="test-001",
    text="def hello(): print('Hello world')",
    user_id="user123",
    file_name="test.py"
)

# Search
results = vector_store.search_similar(
    text="def hello(): print('Hello world')",
    k=5
)
print(results)
```

---

## 🔄 Migrating Existing Submissions to FAISS

If you have existing submissions in Pinecone or local storage:

```python
import asyncio
from db.mongodb import connect_to_mongo, get_database
from db.faiss_store import get_vector_store
from pathlib import Path
import json

async def migrate_submissions():
    # Connect to MongoDB
    await connect_to_mongo()
    db = get_database()
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Migrate from local submissions
    submissions_dir = Path("submissions")
    
    for submission_dir in submissions_dir.iterdir():
        if not submission_dir.is_dir():
            continue
        
        submission_id = submission_dir.name
        
        # Find Python/text files
        for file in submission_dir.glob("*.py"):
            content = file.read_text()
            
            # Add to FAISS
            vector_store.add_submission(
                submission_id=submission_id,
                text=content,
                user_id="migrated",  # Update with actual user_id from DB
                file_name=file.name,
                metadata={"migrated": True}
            )
            
            print(f"✅ Migrated: {file.name}")
    
    print(f"\n✅ Migration complete: {len(vector_store.metadata)} submissions")

# Run migration
asyncio.run(migrate_submissions())
```

---

## 📊 Monitoring & Debugging

### Check MongoDB Connection

```python
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_mongodb():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

asyncio.run(test_mongodb())
```

### Check FAISS Index

```bash
# Check if index files exist
ls -lh data/faiss_index/

# Expected output:
# faiss.index     # Binary FAISS index
# metadata.pkl    # Submission metadata
```

### View MongoDB Data

```bash
# Using MongoDB shell
mongosh
use proctoriq
db.users.find().pretty()
db.submissions.find().pretty()
```

---

## 🚨 Troubleshooting

### Issue: MongoDB Connection Failed

```bash
# Check if MongoDB is running
brew services list | grep mongodb

# Start MongoDB if not running
brew services start mongodb-community

# Check MongoDB logs
tail -f /opt/homebrew/var/log/mongodb/mongo.log
```

### Issue: JWT Token Invalid

- Check `JWT_SECRET` is set in `.env`
- Verify token hasn't expired (24 hours by default)
- Use online JWT decoder to inspect token: https://jwt.io

### Issue: FAISS Import Error

```bash
# Reinstall FAISS
pip uninstall faiss-cpu
pip install faiss-cpu

# For Apple Silicon Macs, you may need:
pip install faiss-cpu --no-cache-dir
```

### Issue: bcrypt Not Working

```bash
# Reinstall bcrypt
pip uninstall bcrypt
pip install bcrypt --no-binary bcrypt
```

---

## 🎯 Next Steps

### For Backend:
1. ✅ Authentication system (DONE)
2. ✅ FAISS vector store (DONE)
3. 🔄 Update existing routes to require authentication
4. 🔄 Add user_id tracking to all submissions
5. 🔄 Implement teacher analytics dashboard

### For Frontend:
1. Create Login/Register pages
2. Implement AuthContext with JWT storage
3. Add axios interceptors for auth tokens
4. Build role-based dashboards
5. Add protected route wrappers

---

## 📚 Documentation

- **MongoDB Motor Docs**: https://motor.readthedocs.io/
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **FAISS Documentation**: https://github.com/facebookresearch/faiss
- **JWT.io**: https://jwt.io/
- **bcrypt**: https://github.com/pyca/bcrypt/

---

## 💡 Tips

1. **JWT Secret**: Use a long, random string (32+ characters)
2. **Password Policy**: Enforce min 8 chars, mix of letters/numbers
3. **Rate Limiting**: Add rate limiting to login/register endpoints
4. **HTTPS**: Use HTTPS in production for JWT tokens
5. **FAISS Backups**: Regularly backup `data/faiss_index/` directory
6. **MongoDB Backups**: Use MongoDB Atlas automated backups

---

## ✅ Completion Checklist

- [x] MongoDB connection working
- [x] User registration working
- [x] Login returns JWT token
- [x] Protected routes validate JWT
- [x] FAISS index created
- [x] Can add submissions to FAISS
- [x] Can search similar submissions
- [ ] Frontend login page created
- [ ] Frontend stores JWT tokens
- [ ] Role-based dashboards working

---

**🎉 Congratulations! Your authentication and FAISS vector store are ready to use!**

For questions or issues, check the troubleshooting section above.
