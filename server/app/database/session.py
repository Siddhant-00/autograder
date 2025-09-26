from typing import Dict, Any, Optional
from app.database.connection import supabase_manager
from fastapi import HTTPException, status

class DatabaseSession:
    def __init__(self, user_token: str = None):
        """Initialize database session with appropriate client"""
        from app.core.config import settings
    
        # If no user token provided or if token is the service role key, use service client
        if not user_token or user_token == settings.SUPABASE_SERVICE_ROLE_KEY:
            self.client = supabase_manager.service_client
        else:
            # Use user client for actual user tokens
            self.client = supabase_manager.get_user_client(user_token)

    async def create_exam_session(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new exam session"""
        try:
            result = self.client.table("exam_sessions").insert(exam_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    async def get_user_exams(self, user_id: str) -> list:
        """Get all exams for a user"""
        try:
            result = self.client.table("exam_sessions").select("*").eq("user_id", user_id).execute()
            return result.data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    async def save_grading_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save grading results"""
        try:
            result = self.client.table("grading_results").insert(result_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )