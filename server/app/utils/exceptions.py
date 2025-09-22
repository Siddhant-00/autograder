from fastapi import HTTPException, status

class AuthenticationError(HTTPException):
    def init(self, detail: str = "Authentication failed"):
        super().init(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class AuthorizationError(HTTPException):
    def init(self, detail: str = "Access denied"):
        super().init(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class ValidationError(HTTPException):
    def init(self, detail: str = "Validation failed"):
        super().init(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class DatabaseError(HTTPException):
    def init(self, detail: str = "Database operation failed"):
        super().init(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class ProcessingError(HTTPException):
    def init(self, detail: str = "Processing failed"):
        super().init(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

# app/utils/validators.py
from typing import List, Dict, Any
from fastapi import HTTPException, status
import mimetypes

class FileValidator:
    ALLOWED_MIME_TYPES = [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "application/pdf"
    ]
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @classmethod
    def validate_file_type(cls, filename: str, content_type: str) -> bool:
        """Validate file type"""
        if content_type not in cls.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(cls.ALLOWED_MIME_TYPES)}"
            )
        return True

    @classmethod
    def validate_file_size(cls, file_size: int) -> bool:
        """Validate file size"""
        if file_size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {cls.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        return True

class MarkingSchemeValidator:
    @classmethod
    def validate_marking_scheme(cls, marking_scheme: Dict[str, Any]) -> bool:
        """Validate marking scheme structure"""
        required_fields = ["question", "model_answer", "marks"]
        
        for question_key, question_data in marking_scheme.items():
            if not question_key.startswith("question_"):
                continue
                
            if not isinstance(question_data, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid structure for {question_key}"
                )
            
            for field in required_fields:
                if field not in question_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Missing {field} in {question_key}"
                    )
            
            # Validate marks is a number
            if not isinstance(question_data["marks"], (int, float)) or question_data["marks"] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid marks value in {question_key}"
                )
        
        return True