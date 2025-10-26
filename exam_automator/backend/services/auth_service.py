"""
Authentication Service
Handles user registration, login, JWT token generation, and password hashing
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId
import os

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class AuthService:
    """Authentication service for user management"""
    
    def __init__(self, database):
        self.db = database
        self.users_collection = database.users
    
    async def register_user(
        self,
        email: str,
        password: str,
        role: str,
        name: str,
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            email: User email address
            password: Plain text password
            role: "student" or "teacher"
            name: User's full name
            student_id: Student ID (required for students)
        
        Returns:
            User document
        
        Raises:
            ValueError: If email already exists or invalid data
        """
        # Validate role
        if role not in ["student", "teacher"]:
            raise ValueError("Role must be 'student' or 'teacher'")
        
        # Check if email already exists
        existing_user = await self.users_collection.find_one({"email": email})
        if existing_user:
            raise ValueError("Email already registered")
        
        # For students, check if student_id exists
        if role == "student":
            if not student_id:
                raise ValueError("Student ID is required for students")
            existing_student = await self.users_collection.find_one({"student_id": student_id})
            if existing_student:
                raise ValueError("Student ID already registered")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user document
        user_doc = {
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "name": name,
            "student_id": student_id if role == "student" else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "last_login": None
        }
        
        # Insert into database
        result = await self.users_collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        # Remove password hash from response
        user_doc.pop("password_hash")
        
        return user_doc
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate JWT token
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            Dict with user info and JWT token
        
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        user = await self.users_collection.find_one({"email": email})
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check if account is active
        if not user.get("is_active", True):
            raise ValueError("Account is deactivated")
        
        # Verify password
        if not self._verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email or password")
        
        # Update last login
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Generate JWT token
        token = self._generate_token(user)
        
        # Prepare user data (remove sensitive info)
        user_data = {
            "id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "name": user["name"],
            "student_id": user.get("student_id"),
            "created_at": user["created_at"]
        }
        
        return {
            "user": user_data,
            "token": token,
            "expires_in": JWT_EXPIRATION_HOURS * 3600  # seconds
        }
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return user data
        
        Args:
            token: JWT token string
        
        Returns:
            User data from token
        
        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            # Decode token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise ValueError("Token has expired")
            
            # Get user from database
            user_id = payload.get("user_id")
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                raise ValueError("User not found")
            
            if not user.get("is_active", True):
                raise ValueError("Account is deactivated")
            
            # Return user data
            return {
                "id": str(user["_id"]),
                "email": user["email"],
                "role": user["role"],
                "name": user["name"],
                "student_id": user.get("student_id")
            }
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                user.pop("_id")
                user.pop("password_hash", None)
                return user
            return None
        except Exception:
            return None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    def _generate_token(self, user: Dict[str, Any]) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        if not self._verify_password(old_password, user["password_hash"]):
            raise ValueError("Invalid current password")
        
        # Hash new password
        new_password_hash = self._hash_password(new_password)
        
        # Update password
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return True
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
