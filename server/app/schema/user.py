from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class StudentCreate(BaseModel):
    student_id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[int] = None
    batch_year: Optional[int] = None

class StudentResponse(BaseModel):
    id: str
    student_id: str
    full_name: str
    email: str
    phone: Optional[str]
    course: Optional[str]
    semester: Optional[int]
    batch_year: Optional[int]
    status: str
    created_at: datetime

class TeacherCreate(BaseModel):
    teacher_id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None

class TeacherResponse(BaseModel):
    id: str
    teacher_id: str
    full_name: str
    email: str
    department: Optional[str]
    designation: Optional[str]
    status: str
