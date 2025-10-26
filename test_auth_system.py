"""
Quick Test Script for Authentication & FAISS
Tests all major functionality to ensure everything is working
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "exam_automator" / "backend"))


async def test_authentication():
    """Test authentication system"""
    print("\n🔐 Testing Authentication System...")
    
    from db.mongodb import connect_to_mongo, get_database
    from services.auth_service import AuthService
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        database = get_database()
        
        auth_service = AuthService(database)
        
        # Test 1: Register a test user
        print("   ✓ Registering test student...")
        try:
            user = await auth_service.register_user(
                email="test_student@example.com",
                password="TestPassword123",
                role="student",
                name="Test Student",
                student_id="TEST001"
            )
            print(f"   ✓ User registered: {user['email']}")
        except ValueError as e:
            if "already registered" in str(e):
                print(f"   ✓ User already exists (that's ok)")
            else:
                raise
        
        # Test 2: Login
        print("   ✓ Testing login...")
        login_result = await auth_service.login(
            email="test_student@example.com",
            password="TestPassword123"
        )
        
        token = login_result["token"]
        print(f"   ✓ Login successful, token: {token[:30]}...")
        
        # Test 3: Verify token
        print("   ✓ Verifying JWT token...")
        user_data = await auth_service.verify_token(token)
        print(f"   ✓ Token valid for user: {user_data['email']}")
        
        print("✅ Authentication tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}\n")
        return False


def test_faiss_vector_store():
    """Test FAISS vector store"""
    print("💾 Testing FAISS Vector Store...")
    
    try:
        from db.faiss_store import FAISSVectorStore
        
        # Initialize vector store
        print("   ✓ Initializing FAISS...")
        vector_store = FAISSVectorStore(index_path="data/test_faiss_index")
        
        # Test 1: Add submission
        print("   ✓ Adding test submission...")
        vector_store.add_submission(
            submission_id="test-sub-001",
            text="def calculate_sum(a, b): return a + b",
            user_id="test-user-001",
            file_name="calculator.py",
            metadata={"language": "python"}
        )
        
        # Test 2: Search for similar
        print("   ✓ Searching for similar submissions...")
        results = vector_store.search_similar(
            text="def add_numbers(x, y): return x + y",
            k=5
        )
        
        if results:
            print(f"   ✓ Found {len(results)} similar submissions")
            print(f"   ✓ Top match: {results[0]['file_name']} ({results[0]['similarity']:.2%} similar)")
        
        # Test 3: Get stats
        stats = vector_store.get_stats()
        print(f"   ✓ Vector store stats: {stats['total_submissions']} submissions")
        
        print("✅ FAISS tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ FAISS test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_full_flow():
    """Test complete flow: register -> login -> add submission -> search"""
    print("\n🔄 Testing Complete Flow...")
    
    from db.mongodb import connect_to_mongo, get_database
    from services.auth_service import AuthService
    from db.faiss_store import get_vector_store
    
    try:
        # Connect
        await connect_to_mongo()
        database = get_database()
        auth_service = AuthService(database)
        vector_store = get_vector_store()
        
        # Step 1: Register teacher
        print("   1. Registering teacher...")
        try:
            teacher = await auth_service.register_user(
                email="teacher@test.com",
                password="Teacher123",
                role="teacher",
                name="Test Teacher"
            )
            print(f"   ✓ Teacher registered: {teacher['email']}")
        except ValueError:
            print("   ✓ Teacher already exists")
            teacher = await database.users.find_one({"email": "teacher@test.com"})
        
        # Step 2: Register two students
        print("   2. Registering students...")
        students = []
        for i in range(2):
            try:
                student = await auth_service.register_user(
                    email=f"student{i}@test.com",
                    password="Student123",
                    role="student",
                    name=f"Student {i}",
                    student_id=f"STU00{i}"
                )
                students.append(student)
                print(f"   ✓ Student {i} registered")
            except ValueError:
                print(f"   ✓ Student {i} already exists")
                student = await database.users.find_one({"email": f"student{i}@test.com"})
                students.append(student)
        
        # Step 3: Add submissions
        print("   3. Adding student submissions...")
        
        # Student 0 - Original work
        vector_store.add_submission(
            submission_id="flow-test-001",
            text="""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
            """,
            user_id=str(students[0]["_id"]),
            file_name="fibonacci.py"
        )
        print("   ✓ Student 0 submitted fibonacci.py")
        
        # Student 1 - Similar work (potential plagiarism)
        vector_store.add_submission(
            submission_id="flow-test-002",
            text="""
def fib(num):
    if num <= 1:
        return num
    return fib(num-1) + fib(num-2)
            """,
            user_id=str(students[1]["_id"]),
            file_name="fib.py"
        )
        print("   ✓ Student 1 submitted fib.py")
        
        # Step 4: Check for cross-student plagiarism
        print("   4. Checking for plagiarism...")
        matches = vector_store.search_similar(
            text="""
def fib(num):
    if num <= 1:
        return num
    return fib(num-1) + fib(num-2)
            """,
            k=5,
            exclude_user_id=str(students[1]["_id"])
        )
        
        if matches:
            print(f"   ⚠️  Found {len(matches)} similar submissions:")
            for match in matches:
                print(f"      - {match['file_name']}: {match['similarity']:.2%} similar")
        else:
            print("   ✓ No plagiarism detected")
        
        # Step 5: Teacher login
        print("   5. Testing teacher access...")
        teacher_login = await auth_service.login(
            email="teacher@test.com",
            password="Teacher123"
        )
        print(f"   ✓ Teacher logged in, role: {teacher_login['user']['role']}")
        
        print("✅ Complete flow test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Flow test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 ProctorIQ System Tests")
    print("="*80)
    
    results = []
    
    # Test 1: Authentication
    results.append(await test_authentication())
    
    # Test 2: FAISS
    results.append(test_faiss_vector_store())
    
    # Test 3: Complete Flow
    results.append(await test_full_flow())
    
    # Summary
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Start the server: python exam_automator/backend/main.py")
        print("2. Test API at: http://localhost:8000/docs")
        print("3. Implement frontend authentication")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("See AUTH_AND_FAISS_SETUP.md for troubleshooting.")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
