"""
Authentication API Routes
Handles user registration, login, logout, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.auth_service import AuthService
from middleware.auth_middleware import auth_middleware, security, get_auth_service


router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # "student" or "teacher"
    name: str
    student_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class AuthResponse(BaseModel):
    user: dict
    token: str
    expires_in: int


class MessageResponse(BaseModel):
    message: str


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user (student or teacher)
    
    - **email**: Valid email address
    - **password**: Password (min 8 characters recommended)
    - **role**: "student" or "teacher"
    - **name**: Full name
    - **student_id**: Required for students (unique identifier)
    """
    try:
        user = await auth_service.register_user(
            email=request.email,
            password=request.password,
            role=request.role,
            name=request.name,
            student_id=request.student_id
        )
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "role": user["role"],
                "name": user["name"],
                "student_id": user.get("student_id")
            }
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with email and password
    
    Returns JWT token for authentication
    Also sets HttpOnly cookies for enhanced security
    """
    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password
        )
        
        # Set HttpOnly cookie for JWT token (more secure)
        response.set_cookie(
            key="auth_token",
            value=result["token"],
            max_age=86400,  # 24 hours (matches JWT expiry)
            httponly=True,  # Prevents JavaScript access (XSS protection)
            secure=False,   # Set to True in production with HTTPS
            samesite="strict",  # CSRF protection
            path="/"
        )
        
        # Also set user data cookie (can be read by frontend)
        import json
        response.set_cookie(
            key="user",
            value=json.dumps({
                "id": result["user"]["id"],
                "email": result["user"]["email"],
                "name": result["user"]["name"],
                "role": result["user"]["role"],
                "student_id": result["user"].get("student_id")
            }),
            max_age=86400,
            httponly=False,  # Frontend needs to read this
            secure=False,
            samesite="strict",
            path="/"
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Get current user information
    
    Requires valid JWT token in Authorization header
    """
    user = await auth_middleware.get_current_user(credentials)
    return {"user": user}


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change user password
    
    Requires current password and new password
    """
    user = await auth_middleware.get_current_user(credentials)
    
    try:
        await auth_service.change_password(
            user_id=user["id"],
            old_password=request.old_password,
            new_password=request.new_password
        )
        
        return {"message": "Password changed successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    """
    Logout user
    
    Clears authentication cookies on the server side
    Client should also clear cookies locally
    """
    # Clear authentication cookies
    response.delete_cookie(key="auth_token", path="/")
    response.delete_cookie(key="user", path="/")
    
    return {
        "message": "Logged out successfully. Cookies cleared."
    }


@router.get("/verify-token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify if JWT token is valid
    
    Returns user data if token is valid
    """
    user = await auth_middleware.get_current_user(credentials)
    return {
        "valid": True,
        "user": user
    }


# Role-specific test endpoints
@router.get("/student-only")
async def student_only_route(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Test endpoint - Students only"""
    user = await auth_middleware.require_student(credentials)
    return {
        "message": "Welcome, student!",
        "user": user
    }


@router.get("/teacher-only")
async def teacher_only_route(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Test endpoint - Teachers only"""
    user = await auth_middleware.require_teacher(credentials)
    return {
        "message": "Welcome, teacher!",
        "user": user
    }
