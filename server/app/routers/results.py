from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from app.schema.user import AuthUser
from app.utils.dependency import get_current_user, require_teacher
from app.services.grading_service import GradingService

router = APIRouter(prefix="/results", tags=["results"])

@router.get("/my-results")
async def get_my_results(
    request: Request,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all grading results for current user"""
    try:
        grading_service = GradingService(request.state.access_token)
        results = await grading_service.get_user_results(current_user.user_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "results": results,
                "count": len(results)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch results: {str(e)}"
        )

@router.get("/result/{exam_session_id}")
async def get_detailed_result(
    request: Request,
    exam_session_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get detailed result for a specific exam session"""
    try:
        grading_service = GradingService(request.state.access_token)
        result = await grading_service.get_detailed_result(exam_session_id, current_user.user_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch detailed result: {str(e)}"
        )

@router.get("/class-analytics")
async def get_class_analytics(
    request: Request,
    exam_id: str,
    teacher: AuthUser = Depends(require_teacher)
):
    """Get analytics for a specific exam (teachers only)"""
    try:
        grading_service = GradingService(request.state.access_token)
        analytics = await grading_service.get_exam_analytics(exam_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=analytics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(e)}"
        )