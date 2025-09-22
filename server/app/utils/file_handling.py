import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import UploadFile, HTTPException


class FileHandler:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    async def save_upload_file(
        self,
        upload_file: UploadFile,
        destination: Optional[str] = None
    ) -> str:
        """Save uploaded file and return the file path"""

        if destination is None:
            # Generate unique filename
            file_extension = (
                upload_file.filename.split(".")[-1] if upload_file.filename else "tmp"
            )
            destination = f"{uuid.uuid4()}.{file_extension}"

        file_path = self.upload_dir / destination

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        finally:
            upload_file.file.close()

        return str(file_path)

    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information"""
        if not os.path.exists(file_path):
            return None

        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "extension": Path(file_path).suffix,
        }


