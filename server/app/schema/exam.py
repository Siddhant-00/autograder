from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time

class SubjectCreate(BaseModel):
    subject_code: str
    subject_name: str
    description: Optional[str] = None
    credits: Optional[int] = 3
    semester: Optional[int] = None
    course: Optional[str] = None

class SubjectResponse(BaseModel):
    id: str
    subject_code: str
    subject_name: str
    description: Optional[str]
    credits: int
    semester: Optional[int]
    course: Optional[str]
    is_active: bool
    created_at: datetime

class ExamCreate(BaseModel):
    exam_code: str
    subject_id: str
    exam_name: str
    exam_type: str
    exam_date: date
    start_time: time
    duration_minutes: int
    total_marks: int
    passing_marks: Optional[int] = None
    instructions: Optional[str] = None
    is_auto_grading_enabled: Optional[bool] = True

class ExamResponse(BaseModel):
    id: str
    exam_code: str
    subject_id: str
    exam_name: str
    exam_type: str
    exam_date: date
    start_time: time
    duration_minutes: int
    total_marks: int
    passing_marks: Optional[int]
    instructions: Optional[str]
    is_auto_grading_enabled: bool
    status: str
    created_by: Optional[str]
    created_at: datetime

class QuestionCreate(BaseModel):
    exam_id: str
    question_number: int
    question_text: str
    question_type: Optional[str] = "descriptive"
    max_marks: float
    marking_scheme: Optional[str] = None
    sample_answer: Optional[str] = None
    keywords: Optional[Dict[str, Any]] = None

class QuestionResponse(BaseModel):
    id: str
    exam_id: str
    question_number: int
    question_text: str
    question_type: str
    max_marks: float
    marking_scheme: Optional[str]
    sample_answer: Optional[str]
    keywords: Optional[Dict[str, Any]]
    created_at: datetime

class MarkingSchemeCreate(BaseModel):
    question_id: str
    criteria_name: str
    criteria_description: Optional[str] = None
    max_points: float
    keywords: Optional[Dict[str, Any]] = None
    weight_percentage: Optional[float] = None
    is_mandatory: Optional[bool] = False

class StudentEnrollmentCreate(BaseModel):
    student_id: str
    exam_id: str
    seat_number: Optional[str] = None

class TeacherAssignmentCreate(BaseModel):
    teacher_id: str
    exam_id: str
    role: Optional[str] = "primary"
    assigned_by: str
