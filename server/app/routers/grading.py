from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.database.connection import get_supabase, get_supabase_admin
from app.services.grading_service import GradingService
from app.schema.grading import GradingRequest, GradingResponse
import asyncio
from app.schema.exam import (
    SubjectCreate, 
    ExamCreate, 
    QuestionCreate, 
    MarkingSchemeCreate,
    StudentEnrollmentCreate,
    TeacherAssignmentCreate
)

router = APIRouter()
grading_service = GradingService()

@router.post("/grade/{upload_id}")
async def start_grading(
    upload_id: str,
    background_tasks: BackgroundTasks,
    supabase_client = Depends(get_supabase)
):
    """Start grading process for an upload"""
    
    # Verify upload exists and is processed
    upload_result = supabase_client.table("exam_uploads").select("*").eq("id", upload_id).execute()
    
    if not upload_result.data:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload = upload_result.data[0]
    
    if upload["processing_status"] != "processed":
        raise HTTPException(status_code=400, detail="Upload not ready for grading")
    
    # Start grading in background
    background_tasks.add_task(grade_upload_async, upload_id)
    
    return {
        "message": "Grading started",
        "upload_id": upload_id,
        "status": "grading_in_progress"
    }

async def grade_upload_async(upload_id: str):
    """Enhanced grading with proper schema alignment"""
    supabase_admin = get_supabase_admin()
    
    try:
        # Get all student answers for this upload
        answers_result = supabase_admin.table("student_answers").select("""
            *,
            questions (
                id,
                question_number,
                question_text,
                max_marks,
                marking_scheme,
                sample_answer,
                keywords
            )
        """).eq("upload_id", upload_id).execute()
        
        if not answers_result.data:
            print(f"No student answers found for upload {upload_id}")
            return
        
        # Get upload info for exam and student details
        upload_result = supabase_admin.table("exam_uploads").select("*").eq("id", upload_id).execute()
        upload = upload_result.data[0]
        
        # Grade each answer
        for answer in answers_result.data:
            question = answer["questions"]
            
            if not answer["extracted_answer"] or not answer["extracted_answer"].strip():
                # Create record for unanswered question
                grading_data = {
                    "student_answer_id": answer["id"],
                    "exam_id": upload["exam_id"],
                    "student_id": upload["student_id"],
                    "question_id": question["id"],
                    "ai_assigned_marks": 0,
                    "final_marks": 0,
                    "ai_feedback": "No answer provided",
                    "similarity_score": 0.0,
                    "ai_confidence": 1.0
                }
                supabase_admin.table("grading_results").insert(grading_data).execute()
                continue
            
            # Grade the answer using AI
            marks, feedback, confidence = await grading_service.grade_answer(
                question["question_text"],
                answer["extracted_answer"],
                question.get("sample_answer", ""),
                question.get("keywords", {}) if question.get("keywords") else {},
                float(question["max_marks"])
            )
            
            # Calculate similarity score (this would be done in grading service)
            similarity_score = grading_service._calculate_similarity(
                answer["extracted_answer"], 
                question.get("sample_answer", "")
            )
            
            # Create grading result record
            grading_data = {
                "student_answer_id": answer["id"],
                "exam_id": upload["exam_id"],
                "student_id": upload["student_id"],
                "question_id": question["id"],
                "ai_assigned_marks": float(marks),
                "final_marks": float(marks),  # Initially same as AI marks
                "ai_feedback": feedback,
                "similarity_score": similarity_score,
                "ai_confidence": float(confidence),
                "grading_criteria_met": {
                    "keywords_found": grading_service._check_keywords(
                        answer["extracted_answer"], 
                        question.get("keywords", {}).get("required", []) if question.get("keywords") else []
                    ),
                    "length_appropriate": len(answer["extracted_answer"].split()) > 10
                }
            }
            
            supabase_admin.table("grading_results").insert(grading_data).execute()
        
        print(f"Grading completed for upload {upload_id}")
        
    except Exception as e:
        print(f"Grading failed for upload {upload_id}: {str(e)}")

# =====================================================
# Additional CRUD routes for the schema entities
# =====================================================

@router.post("/subjects")
async def create_subject(
    subject_data: SubjectCreate,
    supabase_client = Depends(get_supabase)
):
    """Create a new subject"""
    try:
        result = supabase_client.table("subjects").insert(subject_data.dict()).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create subject: {str(e)}")

@router.post("/exams")
async def create_exam(
    exam_data: ExamCreate,
    supabase_client = Depends(get_supabase)
):
    """Create a new exam"""
    try:
        result = supabase_client.table("exams").insert(exam_data.dict()).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create exam: {str(e)}")

@router.post("/questions")
async def create_question(
    question_data: QuestionCreate,
    supabase_client = Depends(get_supabase)
):
    """Create a new question"""
    try:
        result = supabase_client.table("questions").insert(question_data.dict()).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create question: {str(e)}")

@router.post("/marking-schemes")
async def create_marking_scheme(
    scheme_data: MarkingSchemeCreate,
    supabase_client = Depends(get_supabase)
):
    """Create a marking scheme"""
    try:
        result = supabase_client.table("marking_schemes").insert(scheme_data.dict()).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create marking scheme: {str(e)}")

@router.post("/student-enrollments")
async def enroll_student(
    enrollment_data: StudentEnrollmentCreate,
    supabase_client = Depends(get_supabase)
):
    """Enroll student in exam"""
    try:
        result = supabase_client.table("student_exam_enrollments").insert(enrollment_data.dict()).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to enroll student: {str(e)}")

@router.post("/teacher-assignments")
async def assign_teacher(
    assignment_data: TeacherAssignmentCreate,
    supabase_client = Depends(get_supabase)
):
    """Assign teacher to exam"""
    try:
        result = supabase_client.table("teacher_exam_assignments").insert(assignment_data.dict()).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to assign teacher: {str(e)}")
