from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExamBase(BaseModel):
    title: str
    subject: str
    total_marks: int
    marking_scheme: Dict[str, Any]

class ExamCreate(ExamBase):
    pass

class ExamResponse(ExamBase):
    id: str
    teacher_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class ExamSession(BaseModel):
    id: str
    exam_id: str
    student_id: str
    file_path: str
    status: str = "pending"
    created_at: datetime