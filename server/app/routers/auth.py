from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from app.database.connection import get_supabase_admin
from app.core.auth import auth_service, get_current_user
from datetime import timedelta
from typing import Optional

student_id: Optional[str] = None


router = APIRouter()

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    user_type: str  # "student" or "teacher"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    user_type: str
    student_id: Optional[str] = None  # Required for students
    teacher_id: Optional[str] = None  # Required for teachers
    phone: Optional[str] = None
    course: Optional[str] = None  # For students
    department: Optional[str] = None  # For teachers

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/register", response_model=Token)
async def register_user(user_data: UserRegister):
    """Register new user"""
    
    supabase_admin = get_supabase_admin()
    
    try:
        # Hash password
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        # Check if user already exists
        existing_user = None
        if user_data.user_type == "student":
            existing_user = supabase_admin.table("students").select("*").eq("email", user_data.email).execute()
        else:
            existing_user = supabase_admin.table("teachers").select("*").eq("email", user_data.email).execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user record
        if user_data.user_type == "student":
            if not user_data.student_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student ID is required for students"
                )
            
            user_record = {
                "student_id": user_data.student_id,
                "full_name": user_data.full_name,
                "email": user_data.email,
                "password_hash": hashed_password,
                "phone": user_data.phone,
                "course": user_data.course,
                "status": "active"
            }
            
            result = supabase_admin.table("students").insert(user_record).execute()
            
        else:  # teacher
            if not user_data.teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Teacher ID is required for teachers"
                )
            
            user_record = {
                "teacher_id": user_data.teacher_id,
                "full_name": user_data.full_name,
                "email": user_data.email,
                "password_hash": hashed_password,
                "phone": user_data.phone,
                "department": user_data.department,
                "status": "active"
            }
            
            result = supabase_admin.table("teachers").insert(user_record).execute()
        
        created_user = result.data[0]
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={
                "user_id": created_user["id"],
                "email": created_user["email"],
                "user_type": user_data.user_type 
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": created_user["id"],
                "email": created_user["email"],
                "full_name": created_user["full_name"],
                "role": user_data.user_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Authenticate user and return token"""
    
    supabase_admin = get_supabase_admin()
    
    try:
        # Get user from appropriate table
        if user_credentials.user_type == "student":
            result = supabase_admin.table("students").select("*").eq("email", user_credentials.email).execute()
        else:
            result = supabase_admin.table("teachers").select("*").eq("email", user_credentials.email).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = result.data[0]
        
        # Verify password
        if not auth_service.verify_password(user_credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if user.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={
                "user_id": user["id"],
                "email": user["email"],
                "user_type": user_credentials.user_type
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user_credentials.user_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}
