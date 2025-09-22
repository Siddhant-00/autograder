from fastapi import Request, Depends, HTTPException, status
from typing import Dict, Any
from app.schema.user import AuthUser

def get_current_user(request: Request) -> AuthUser:
    """Dependency to get current authenticated user"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user_data = request.state.user
    return AuthUser(
        user_id=user_data["user_id"],
        email=user_data["email"],
        role=request.state.user_role,
        user_metadata=user_data["user_metadata"],
        app_metadata=user_data["app_metadata"]
    )

def require_role(required_role: str):
    """Dependency factory to require specific role"""
    def role_checker(request: Request) -> AuthUser:
        user = get_current_user(request)
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return user
    return role_checker

# Specific role dependencies
def require_teacher(request: Request) -> AuthUser:
    return require_role("teacher")(request)

def require_student(request: Request) -> AuthUser:
    return require_role("student")(request)