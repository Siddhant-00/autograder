from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import aiofiles
import os
from uuid import uuid4
from app.database.connection import get_supabase
from app.core.config import settings
from app.services.ocr_service import OCRService
import asyncio
from app.routers.auth import get_current_user

router = APIRouter()
ocr_service = OCRService()

@router.post("/upload/{exam_id}")
async def upload_exam_paper(
    exam_id: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """Upload and process exam paper"""
    
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can upload exam papers")
    
    student_id = current_user["user_id"]
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS.split(','):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    existing_upload = supabase_client.table("exam_uploads").select("*").eq("student_id", student_id).eq("exam_id", exam_id).execute()
    if existing_upload.data:
        raise HTTPException(status_code=400, detail="You have already uploaded an answer for this exam")
    
    try:
        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = f"{settings.UPLOAD_PATH}{exam_id}/{student_id}/{unique_filename}"
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        upload_data = {
            "exam_id": exam_id,
            "student_id": student_id,
            "file_name": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "file_type": file_extension,
            "processing_status": "uploaded"
        }
        
        from app.database.connection import get_supabase_admin
        supabase_admin = get_supabase_admin()
        result = supabase_admin.table("exam_uploads").insert(upload_data).execute()
        upload_id = result.data[0]["id"]
        
        asyncio.create_task(process_upload_async(upload_id, file_path, file_extension))
        
        return {
            "upload_id": upload_id,
            "message": "File uploaded successfully",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/uploads/student")
async def get_student_uploads(
    current_user = Depends(get_current_user),
):
    """Get all uploads for current student"""
    
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")
    
    student_id = current_user["user_id"]
    
    from app.database.connection import get_supabase_admin
    supabase_admin = get_supabase_admin()
    
    uploads = supabase_admin.table("exam_uploads").select("*").eq("student_id", student_id).execute()
    
    return {"uploads": uploads.data}

@router.post("/validate-file")
async def validate_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Validate uploaded file"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS.split(','):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    return {
        "valid": True,
        "file_name": file.filename,
        "file_size": len(content),
        "file_type": file_extension
    }

@router.get("/upload/status/{upload_id}")
async def get_upload_status(
    upload_id: str, 
    current_user = Depends(get_current_user),
    # supabase_client = Depends(get_supabase)
):
    """Get upload processing status"""
    
    from app.database.connection import get_supabase_admin
    supabase_admin = get_supabase_admin()
    
    result = supabase_admin.table("exam_uploads").select("*").eq("id", upload_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload = result.data[0]
    
    # Verify access rights
    if current_user["user_type"] == "student" and upload["student_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return result.data[0]


async def process_upload_async(upload_id: str, file_path: str, file_extension: str):
    """Background task to process uploaded file with OCR and AI grading"""
    from app.database.connection import get_supabase_admin
    
    supabase_admin = get_supabase_admin()
    
    try:
        supabase_admin.table("exam_uploads").update({
            "processing_status": "processing"
        }).eq("id", upload_id).execute()
        
        async with aiofiles.open(file_path, 'rb') as f:
            file_content = await f.read()
        
        extracted_answers = await ocr_service.extract_answers(file_path)

        ocr_result = {
            "status": "success" if extracted_answers else "error",
            "text": "\n".join([f"Q{k.replace('question_', '')}: {v}" for k, v in extracted_answers.items()]),
            "confidence": 0.80,
            "error": None if extracted_answers else "No text extracted"
        }
        
        update_data = {
            "processing_status": "processed" if ocr_result["status"] == "success" else "failed",
            "ocr_extracted_text": ocr_result["text"],
            "confidence_score": ocr_result["confidence"],
            "processed_at": "now()"
        }
        
        if ocr_result["status"] == "error":
            update_data["error_message"] = ocr_result.get("error", "Unknown error")
        
        supabase_admin.table("exam_uploads").update(update_data).eq("id", upload_id).execute()
        
        upload_result = supabase_admin.table("exam_uploads").select("*").eq("id", upload_id).execute()
        upload = upload_result.data[0]
        
        await create_student_answers(upload_id, ocr_result["text"], supabase_admin)
        
        # AI Grading
        try:
            from app.services.ai_service import AIGradingService
            ai_service = AIGradingService()
            
            questions_result = supabase_admin.table("questions").select("*").eq("exam_id", upload["exam_id"]).execute()
            
            for question in questions_result.data:
                answer_result = supabase_admin.table("student_answers").select("*").eq(
                    "upload_id", upload_id
                ).eq("question_id", question["id"]).single().execute()
                
                if answer_result.data and answer_result.data.get("extracted_answer"):
                    question_data = {
                        "question": question["question_text"],
                        "model_answer": question.get("sample_answer", ""),
                        "marks": question["max_marks"],
                        "question_number": question["question_number"],
                        "keywords": question.get("keywords", [])
                    }
                    
                    result = await ai_service.grade_question(question_data, answer_result.data["extracted_answer"])
                    
                    grading_data = {
                        "question_id": question["id"],
                        "student_id": upload["student_id"],
                        "exam_id": upload["exam_id"],
                        # "upload_id": upload_id,
                        "student_answer_id": answer_result.data["id"],
                        "ai_assigned_marks": result.marks_obtained,
                        "final_marks": result.marks_obtained,
                        "ai_feedback": result.feedback,
                        "ai_confidence": result.confidence_score,
                        "similarity_score": result.confidence_score,
                        "is_reviewed_by_teacher": False
                    }
                    
                    supabase_admin.table("grading_results").insert(grading_data).execute()
        
        except Exception as grading_error:
            print(f"Grading error: {str(grading_error)}")
        
    except Exception as e:
        supabase_admin.table("exam_uploads").update({
            "processing_status": "failed",
            "error_message": str(e)
        }).eq("id", upload_id).execute()

async def create_student_answers(upload_id: str, extracted_text: str, supabase_admin):
    """Create student_answers records for each question"""
    
    upload_result = supabase_admin.table("exam_uploads").select("*").eq("id", upload_id).execute()
    upload = upload_result.data[0]
    
    questions_result = supabase_admin.table("questions").select("*").eq("exam_id", upload["exam_id"]).order("question_number").execute()
    
    lines = extracted_text.split('\n')
    answers_dict = {}
    
    for line in lines:
        if line.strip().startswith('Q'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                q_num = parts[0].strip().replace('Q', '')
                answer = parts[1].strip()
                answers_dict[int(q_num)] = answer
    
    for question in questions_result.data:
        q_num = question["question_number"]
        student_answer = answers_dict.get(q_num, "")
        
        answer_data = {
            "upload_id": upload_id,
            "question_id": question["id"],
            "student_id": upload["student_id"],
            "extracted_answer": student_answer,
            "raw_image_path": upload["file_path"],
            "confidence_score": 0.8,
            "processing_notes": f"Extracted from question {q_num}"
        }
        
        supabase_admin.table("student_answers").insert(answer_data).execute()