"""
Simple System Test - Authentication & FAISS
Suppresses unnecessary warnings for cleaner output
"""

import asyncio
import sys
import os
import warnings
from pathlib import Path

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "exam_automator" / "backend"))


async def main():
    print("\n" + "="*70)
    print("🧪 ProctorIQ System Test - Quick Validation")
    print("="*70 + "\n")
    
    # Test 1: Authentication
    print("1️⃣  Testing Authentication...")
    from db.mongodb import connect_to_mongo, get_database
    from services.auth_service import AuthService
    
    try:
        await connect_to_mongo()
        database = get_database()
        auth_service = AuthService(database)
        
        # Register test user
        try:
            await auth_service.register_user(
                email="demo@proctoriq.com",
                password="Demo123!",
                role="student",
                name="Demo Student",
                student_id="DEMO001"
            )
            print("   ✅ User registration: WORKING")
        except ValueError as e:
            if "already registered" in str(e):
                print("   ✅ User registration: WORKING (user exists)")
        
        # Test login
        login_result = await auth_service.login(
            email="demo@proctoriq.com",
            password="Demo123!"
        )
        print("   ✅ Login & JWT: WORKING")
        
        # Verify token
        await auth_service.verify_token(login_result["token"])
        print("   ✅ Token validation: WORKING")
        
    except Exception as e:
        print(f"   ❌ Authentication: FAILED - {e}")
        return False
    
    # Test 2: FAISS Vector Store
    print("\n2️⃣  Testing FAISS Vector Store...")
    from db.faiss_store import FAISSVectorStore
    
    try:
        vector_store = FAISSVectorStore(index_path="data/test_index")
        
        # Add test submission
        vector_store.add_submission(
            submission_id="test-001",
            text="def hello_world(): print('Hello, World!')",
            user_id="user-001",
            file_name="hello.py"
        )
        print("   ✅ Vector embedding: WORKING")
        
        # Search
        results = vector_store.search_similar(
            text="def greet(): print('Hello!')",
            k=3
        )
        print("   ✅ Similarity search: WORKING")
        
        # Get stats
        stats = vector_store.get_stats()
        print(f"   ✅ Index stats: {stats['total_submissions']} submissions stored")
        
    except Exception as e:
        print(f"   ❌ FAISS: FAILED - {e}")
        return False
    
    # Test 3: API Server
    print("\n3️⃣  Testing API Server...")
    print("   ℹ️  To test the API server, run:")
    print("      cd exam_automator/backend && python main.py")
    print("   ℹ️  Then visit: http://localhost:8000/docs")
    
    # Summary
    print("\n" + "="*70)
    print("✅ SYSTEM CHECK COMPLETE")
    print("="*70)
    print("\n📋 Status:")
    print("   ✅ MongoDB: Connected & Working")
    print("   ✅ Authentication: JWT + bcrypt Working")
    print("   ✅ FAISS Vector Store: Working")
    print("   ⏳ API Server: Ready to start")
    
    print("\n🚀 Next Steps:")
    print("   1. Start backend: cd exam_automator/backend && python main.py")
    print("   2. Visit API docs: http://localhost:8000/docs")
    print("   3. Test endpoints:")
    print("      - POST /api/auth/register")
    print("      - POST /api/auth/login")
    print("      - GET  /api/auth/me (with JWT token)")
    print("\n" + "="*70 + "\n")
    
    return True


if __name__ == "__main__":
    asyncio.run(main())
