from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings
import json

class JWTHandler:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM

    def verify_supabase_token(self, token: str) -> Dict[str, Any]:
        """Verify Supabase JWT token and extract user data"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_aud": False}  # Supabase tokens might not have standard aud
            )
            
            # Extract user information from Supabase token
            user_id = payload.get("sub")
            email = payload.get("email")
            role = payload.get("role", "authenticated")
            user_metadata = payload.get("user_metadata", {})
            app_metadata = payload.get("app_metadata", {})
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )
            
            return {
                "user_id": user_id,
                "email": email,
                "role": role,
                "user_metadata": user_metadata,
                "app_metadata": app_metadata,
                "full_payload": payload
            }
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )

    def extract_user_role(self, user_data: Dict[str, Any]) -> str:
        """Extract user role from token data"""
        # Check app_metadata first (where custom roles are usually stored)
        app_metadata = user_data.get("app_metadata", {})
        if "role" in app_metadata:
            return app_metadata["role"]
        
        # Check user_metadata
        user_metadata = user_data.get("user_metadata", {})
        if "role" in user_metadata:
            return user_metadata["role"]
        
        # Default role
        return "student"

jwt_handler = JWTHandler()