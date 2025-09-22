from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from app.schema.user import AuthUser
from app.schema.grading import GradingRequest, GradingResponse
from app.utils.dependency import get_current_user
from app.services.grading_service import GradingService

router = APIRouter(prefix="/grading", tags=["grading"])

@router.post("/start", response_model=GradingResponse)
async def start_grading(
    request: Request,
    grading_request: GradingRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Start the grading process for an exam session"""
    try:
        grading_service = GradingService(request.state.access_token)
        result = await grading_service.grade_exam_session(
            grading_request.exam_session_id,
            grading_request.marking_scheme,
            current_user.user_id
        )
        
        return GradingResponse(
            success=True,
            result=result,
            message="Grading completed successfully"
        )
        
    except Exception as e:
        return GradingResponse(
            success=False,
            result=None,
            message=f"Grading failed: {str(e)}"
        )

@router.get("/status/{exam_session_id}")
async def get_grading_status(
    request: Request,
    exam_session_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get grading status for an exam session"""
    try:
        grading_service = GradingService(request.state.access_token)
        status_info = await grading_service.get_grading_status(exam_session_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=status_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get grading status: {str(e)}"
        )