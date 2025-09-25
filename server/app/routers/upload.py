from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import aiofiles
import os
from uuid import uuid4
from app.database.connection import get_supabase
from app.core.config import settings
from app.services.ocr_service import OCRService
import asyncio

router = APIRouter()
ocr_service = OCRService()

@router.post("/upload/{exam_id}/{student_id}")
async def upload_exam_paper(
    exam_id: str,
    student_id: str,
    file: UploadFile = File(...),
    supabase_client = Depends(get_supabase)
):
    """Upload and process exam paper"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS.split(','):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Verify student enrollment
    enrollment_check = supabase_client.table("student_exam_enrollments").select("*").eq("student_id", student_id).eq("exam_id", exam_id).eq("enrollment_status", "enrolled").execute()
    
    if not enrollment_check.data:
        raise HTTPException(status_code=403, detail="Student not enrolled in this exam")
    
    try:
        # Generate unique filename
        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = f"{settings.UPLOAD_PATH}{exam_id}/{student_id}/{unique_filename}"
        
        # Create directory
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Create upload record with all schema fields
        upload_data = {
            "exam_id": exam_id,
            "student_id": student_id,
            "file_name": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "file_type": file_extension,
            "processing_status": "uploaded"
        }
        
        result = supabase_client.table("exam_uploads").insert(upload_data).execute()
        upload_id = result.data[0]["id"]
        
        # Start OCR processing in background
        asyncio.create_task(process_upload_async(upload_id, file_path, file_extension))
        
        return {
            "upload_id": upload_id,
            "message": "File uploaded successfully",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_upload_async(upload_id: str, file_path: str, file_extension: str):
    """Background task to process uploaded file with proper schema alignment"""
    from app.database.connection import get_supabase_admin
    
    supabase_admin = get_supabase_admin()
    
    try:
        # Update status
        supabase_admin.table("exam_uploads").update({
            "processing_status": "processing"
        }).eq("id", upload_id).execute()
        
        # Read file
        async with aiofiles.open(file_path, 'rb') as f:
            file_content = await f.read()
        
        # Process based on file type
        if file_extension == 'pdf':
            ocr_result = await ocr_service.extract_text_from_pdf(file_content)
        else:
            ocr_result = await ocr_service.extract_text_from_image(file_content)
        
        # Update record with OCR results
        update_data = {
            "processing_status": "processed" if ocr_result["status"] == "success" else "failed",
            "ocr_extracted_text": ocr_result["text"],
            "confidence_score": ocr_result["confidence"],
            "processed_at": "now()"
        }
        
        if ocr_result["status"] == "error":
            update_data["error_message"] = ocr_result.get("error", "Unknown error")
        
        supabase_admin.table("exam_uploads").update(update_data).eq("id", upload_id).execute()
        
        # Create student answers records for each question
        await create_student_answers(upload_id, ocr_result["text"], supabase_admin)
        
    except Exception as e:
        # Update with error status
        supabase_admin.table("exam_uploads").update({
            "processing_status": "failed",
            "error_message": str(e)
        }).eq("id", upload_id).execute()

async def create_student_answers(upload_id: str, extracted_text: str, supabase_admin):
    """Create student_answers records for each question"""
    
    # Get upload details
    upload_result = supabase_admin.table("exam_uploads").select("*").eq("id", upload_id).execute()
    upload = upload_result.data[0]
    
    # Get exam questions
    questions_result = supabase_admin.table("questions").select("*").eq("exam_id", upload["exam_id"]).order("question_number").execute()
    
    for question in questions_result.data:
        # Extract answer for this specific question
        student_answer = extract_answer_for_question(extracted_text, question["question_number"])
        
        # Create student answer record
        answer_data = {
            "upload_id": upload_id,
            "question_id": question["id"],
            "student_id": upload["student_id"],
            "extracted_answer": student_answer if student_answer else "",
            "raw_image_path": upload["file_path"],
            "confidence_score": 0.8,  # This would come from OCR per question
            "processing_notes": f"Extracted from question {question['question_number']}"
        }
        
        supabase_admin.table("student_answers").insert(answer_data).execute()

def extract_answer_for_question(full_text: str, question_number: int) -> str:
    """Enhanced answer extraction with better parsing"""
    if not full_text:
        return ""
    
    lines = full_text.split('\n')
    answer_lines = []
    capturing = False
    
    question_patterns = [
        f"{question_number}.",
        f"Q{question_number}",
        f"Question {question_number}",
        f"{question_number})",
        f"({question_number})"
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line contains the target question
        if any(pattern in line for pattern in question_patterns):
            capturing = True
            # Skip the question line itself if it contains the question text
            if len(line) > 20:  # Likely contains question text
                continue
        
        # Stop capturing at next question (but not the current one)
        elif capturing:
            # Check if this is the start of another question
            next_question_found = False
            for i in range(1, 21):  # Check questions 1-20
                if i != question_number:
                    next_patterns = [f"{i}.", f"Q{i}", f"Question {i}", f"{i})", f"({i})"]
                    if any(pattern in line for pattern in next_patterns):
                        next_question_found = True
                        break
            
            if next_question_found:
                break
        
        if capturing and line:
            answer_lines.append(line)
    
    return ' '.join(answer_lines).strip()
