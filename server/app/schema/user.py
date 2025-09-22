from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    role: str = "student"

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    full_name: Optional[str] = None
    created_at: datetime
    user_metadata: Optional[Dict[str, Any]] = None

class AuthUser(BaseModel):
    user_id: str
    email: str
    role: str
    user_metadata: Dict[str, Any]
    app_metadata: Dict[str, Any]

# app/schemas/exam.py
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