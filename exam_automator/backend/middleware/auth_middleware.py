"""
Authentication Middleware
JWT token validation and role-based access control for protected routes
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from services.auth_service import AuthService
from db.mongodb import get_database


security = HTTPBearer()


class AuthMiddleware:
    """Middleware for JWT authentication and authorization"""
    
    def __init__(self):
        self.auth_service = None
    
    def initialize(self, database):
        """Initialize auth service with database"""
        self.auth_service = AuthService(database)
    
    async def verify_token(
        self,
        credentials: HTTPAuthorizationCredentials
    ) -> dict:
        """
        Verify JWT token from Authorization header
        
        Args:
            credentials: HTTP Bearer credentials
        
        Returns:
            User data from token
        
        Raises:
            HTTPException: If token is invalid
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        try:
            user_data = await self.auth_service.verify_token(token)
            return user_data
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def require_role(
        self,
        user: dict,
        allowed_roles: List[str]
    ):
        """
        Check if user has required role
        
        Args:
            user: User data from token
            allowed_roles: List of allowed roles
        
        Raises:
            HTTPException: If user doesn't have required role
        """
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials
    ) -> dict:
        """
        Get current authenticated user
        
        This is a dependency that can be used in route handlers
        to get the current user from the JWT token
        
        Usage:
            @app.get("/protected")
            async def protected_route(user = Depends(auth_middleware.get_current_user)):
                return {"user": user}
        """
        return await self.verify_token(credentials)
    
    async def require_student(
        self,
        credentials: HTTPAuthorizationCredentials
    ) -> dict:
        """Require student role"""
        user = await self.verify_token(credentials)
        await self.require_role(user, ["student"])
        return user
    
    async def require_teacher(
        self,
        credentials: HTTPAuthorizationCredentials
    ) -> dict:
        """Require teacher role"""
        user = await self.verify_token(credentials)
        await self.require_role(user, ["teacher"])
        return user
    
    async def require_any_role(
        self,
        credentials: HTTPAuthorizationCredentials
    ) -> dict:
        """Require any authenticated user (student or teacher)"""
        return await self.verify_token(credentials)


# Global middleware instance
auth_middleware = AuthMiddleware()


def get_auth_service():
    """Dependency to get auth service"""
    database = get_database()
    return AuthService(database)
