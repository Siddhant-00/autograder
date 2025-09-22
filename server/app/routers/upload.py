from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import List
import aiofiles
import os
from datetime import datetime
import uuid
from app.schema.user import AuthUser
from app.utils.dependency import get_current_user
from app.database.session import DatabaseSession

router = APIRouter(prefix="/upload", tags=["upload"])

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

@router.post("/exam-copy")
async def upload_exam_copy(
    request: Request,
    file: UploadFile = File(...),
    exam_id: str = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Upload exam copy for grading"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and PDF files are allowed"
        )
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{unique_filename}"
    
    try:
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create exam session record
        db_session = DatabaseSession(request.state.access_token)
        exam_session_data = {
            "exam_id": exam_id,
            "student_id": current_user.user_id,
            "file_path": file_path,
            "status": "uploaded",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        exam_session = await db_session.create_exam_session(exam_session_data)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "File uploaded successfully",
                "exam_session_id": exam_session["id"],
                "file_path": file_path,
                "status": "uploaded"
            }
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/exam-sessions")
async def get_user_exam_sessions(
    request: Request,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all exam sessions for current user"""
    try:
        db_session = DatabaseSession(request.state.access_token)
        sessions = await db_session.get_user_exams(current_user.user_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "exam_sessions": sessions,
                "count": len(sessions)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch exam sessions: {str(e)}"
        )