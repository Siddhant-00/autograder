from fastapi import APIRouter, HTTPException, Depends
from app.database.connection import get_supabase
from app.routers.auth import get_current_user  # ADD THIS IMPORT
from typing import List, Dict, Any

router = APIRouter()

@router.get("/results/student")
async def get_current_student_results(
    current_user = Depends(get_current_user),
):
    """Get results for current authenticated student"""
    
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Use admin client to bypass RLS
    from app.database.connection import get_supabase_admin
    supabase_admin = get_supabase_admin()
    
    student_id = current_user["user_id"]
    
    # Query grading_results directly with nested relations
    results = supabase_admin.table("grading_results").select("""
        *,
        exams (
            exam_name, 
            exam_type, 
            exam_date, 
            total_marks
        ),
        questions (
            question_number, 
            question_text, 
            max_marks
        )
    """).eq("student_id", student_id).execute()
    
    if not results.data:
        return {"student_id": student_id, "exams": []}
    
    # Group results by exam...
    exams_dict = {}
    for result in results.data:
        exam_info = result.get("exams")
        if not exam_info:
            continue  # Skip if exam info missing
        
        exam_id = result["exam_id"]
        if exam_id not in exams_dict:
            exams_dict[exam_id] = {
                "exam_id": exam_id,
                "exam_name": exam_info["exam_name"],
                "exam_type": exam_info["exam_type"],
                "exam_date": exam_info["exam_date"],
                "total_marks": exam_info["total_marks"],
                "obtained_marks": 0,
                "questions": []
            }
        
        exams_dict[exam_id]["obtained_marks"] += float(result["final_marks"] or 0)
        exams_dict[exam_id]["questions"].append({
            "question_number": result["questions"]["question_number"],
            "obtained_marks": result["final_marks"],
        })
    
    return {
        "student_id": student_id,
        "exams": list(exams_dict.values())
    }

@router.get("/results/student/{student_id}")
async def get_student_results(student_id: str, supabase_client = Depends(get_supabase)):
    """Get all results for a student with enhanced schema support"""
    
    results = supabase_client.table("grading_results").select("""
        *,
        exams (
            exam_name, 
            exam_type, 
            exam_date, 
            total_marks,
            subjects (subject_name, subject_code)
        ),
        questions (question_number, question_text, max_marks),
        student_answers (extracted_answer, confidence_score)
    """).eq("student_id", student_id).execute()
    
    if not results.data:
        return {"student_id": student_id, "exams": []}
    
    # Group results by exam with enhanced data
    exams_dict = {}
    for result in results.data:
        exam_info = result.get("exams")
        if not exam_info:
            continue  # Skip if exam info missing

        exam_id = result["exam_id"]
        if exam_id not in exams_dict:
            exams_dict[exam_id] = {
                "exam_id": exam_id,
                "exam_name": exam_info["exam_name"],
                "exam_type": exam_info["exam_type"],
                "exam_date": exam_info["exam_date"],
                "total_marks": exam_info["total_marks"],
                "subject_name": exam_info["subjects"]["subject_name"],
                "subject_code": exam_info["subjects"]["subject_code"],
                "obtained_marks": 0,
                "ai_confidence_avg": 0,
                "questions": []
            }
        
        obtained_marks = float(result["final_marks"] or 0)
        exams_dict[exam_id]["obtained_marks"] += obtained_marks
        
        # Calculate average confidence
        confidence_scores = [q.get("ai_confidence", 0) for q in exams_dict[exam_id]["questions"]]
        confidence_scores.append(float(result["ai_confidence"] or 0))
        exams_dict[exam_id]["ai_confidence_avg"] = sum(confidence_scores) / len(confidence_scores)
        
        exams_dict[exam_id]["questions"].append({
            "question_number": result["questions"]["question_number"],
            "question_text": result["questions"]["question_text"],
            "max_marks": result["questions"]["max_marks"],
            "obtained_marks": result["final_marks"],
            "ai_assigned_marks": result["ai_assigned_marks"],
            "teacher_assigned_marks": result["teacher_assigned_marks"],
            "ai_feedback": result["ai_feedback"],
            "teacher_feedback": result["teacher_feedback"],
            "is_reviewed": result["is_reviewed_by_teacher"],
            "is_disputed": result["is_disputed"],
            "similarity_score": result["similarity_score"],
            "ai_confidence": result["ai_confidence"],
            "student_answer": result["student_answers"]["extracted_answer"],
            "extraction_confidence": result["student_answers"]["confidence_score"]
        })
    
    # Calculate percentages and grades
    for exam in exams_dict.values():
        total = exam["total_marks"]
        obtained = exam["obtained_marks"]
        exam["percentage"] = round((obtained / total * 100), 2) if total > 0 else 0
        exam["grade"] = calculate_grade(exam["percentage"])
    
    return {
        "student_id": student_id,
        "exams": list(exams_dict.values())
    }

@router.get("/results/exam/{exam_id}/summary")
async def get_exam_summary(exam_id: str, supabase_client = Depends(get_supabase)):
    """Get comprehensive exam summary with statistics"""
    
    # Get basic exam info
    exam_result = supabase_client.table("exams").select("""
        *,
        subjects (subject_name, subject_code)
    """).eq("id", exam_id).execute()
    
    if not exam_result.data:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam = exam_result.data[0]
    
    # Get all results for this exam
    results = supabase_client.table("grading_results").select("""
        *,
        student_answers (
            students (student_id, full_name)
        )
    """).eq("exam_id", exam_id).execute()
    
    # Calculate statistics
    total_students = len(set([r["student_id"] for r in results.data]))
    total_questions = len(set([r["question_id"] for r in results.data]))
    
    # Grade distribution
    student_totals = {}
    for result in results.data:
        student_id = result["student_id"]
        if student_id not in student_totals:
            student_totals[student_id] = {
                "student_name": result["student_answers"]["students"]["full_name"],
                "total_marks": 0,
                "needs_review": 0
            }
        
        student_totals[student_id]["total_marks"] += float(result["final_marks"] or 0)
        if result["ai_confidence"] < 0.7 or result["is_disputed"]:
            student_totals[student_id]["needs_review"] += 1
    
    # Calculate grade distribution
    grade_distribution = {"A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "F": 0}
    for student_data in student_totals.values():
        percentage = (student_data["total_marks"] / exam["total_marks"]) * 100
        grade = calculate_grade(percentage)
        grade_distribution[grade] += 1
    
    return {
        "exam_info": {
            "exam_id": exam_id,
            "exam_name": exam["exam_name"],
            "exam_type": exam["exam_type"],
            "subject_name": exam["subjects"]["subject_name"],
            "total_marks": exam["total_marks"],
            "total_students": total_students,
            "total_questions": total_questions
        },
        "statistics": {
            "grade_distribution": grade_distribution,
            "average_score": sum([s["total_marks"] for s in student_totals.values()]) / len(student_totals) if student_totals else 0,
            "students_needing_review": sum([1 for s in student_totals.values() if s["needs_review"] > 0])
        },
        "students": list(student_totals.values())
    }

def calculate_grade(percentage: float) -> str:
    """Calculate letter grade from percentage"""
    if percentage >= 85:
        return "A+"
    elif percentage >= 75:
        return "A"
    elif percentage >= 65:
        return "B+"
    elif percentage >= 55:
        return "B"
    elif percentage >= 45:
        return "C"
    else:
        return "F"
