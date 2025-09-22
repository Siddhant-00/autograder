from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class GradingRequest(BaseModel):
    exam_session_id: str
    marking_scheme: Dict[str, Any]

class QuestionResult(BaseModel):
    question_number: int
    extracted_answer: str
    marks_obtained: float
    max_marks: float
    feedback: Optional[str] = None
    confidence_score: float

class GradingResult(BaseModel):
    exam_session_id: str
    total_marks: float
    max_marks: float
    percentage: float
    question_results: List[QuestionResult]
    overall_feedback: Optional[str] = None
    graded_at: datetime

class GradingResponse(BaseModel):
    success: bool
    result: Optional[GradingResult] = None
    message: str