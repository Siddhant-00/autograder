from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import uuid
from app.core.config import settings
from app.database.connection import get_supabase_admin

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash (truncate to 72 bytes)"""
        safe_password = plain_password[:72]
        return pwd_context.verify(safe_password, hashed_password)

    
    def get_password_hash(self, password: str) -> str:
        """Hash password (truncate to 72 bytes)"""
        safe_password = password[:72]
        return pwd_context.hash(safe_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with proper claims"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        # Add required JWT claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "sub": data.get("user_id", str(uuid.uuid4())),  # Subject claim - required by Supabase
            "aud": "authenticated",  # Audience claim
            "iss": "your-app-name"  # Issuer claim
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token has expired
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}"
            )

auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    
    token = credentials.credentials
    
    try:
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")  # Use sub claim as user_id
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user from database
        supabase_admin = get_supabase_admin()
        
        # Try students table first
        student_result = supabase_admin.table("students").select("*").eq("id", user_id).execute()
        if student_result.data:
            return {"user": student_result.data[0], "role": "student"}
        
        # Try teachers table
        teacher_result = supabase_admin.table("teachers").select("*").eq("id", user_id).execute()
        if teacher_result.data:
            return {"user": teacher_result.data[0], "role": "teacher"}
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
