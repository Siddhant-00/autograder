from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ExamSession(Base):
    tablename = "exam_sessions"
    
    id = Column(String, primary_key=True)
    exam_id = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="uploaded")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime, nullable=True)

class GradingResults(Base):
    tablename = "grading_results"
    
    id = Column(String, primary_key=True)
    exam_session_id = Column(String, nullable=False)
    total_marks = Column(Float, nullable=False)
    max_marks = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    question_results = Column(JSON, nullable=False)
    overall_feedback = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    graded_at = Column(DateTime, default=datetime.utcnow)

class Exams(Base):
    tablename = "exams"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    teacher_id = Column(String, nullable=False)
    total_marks = Column(Integer, nullable=False)
    marking_scheme = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)