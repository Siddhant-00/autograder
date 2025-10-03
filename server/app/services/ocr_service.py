import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List
import PyPDF2
import io

class OCRService:
    def __init__(self):
        self.confidence_threshold = 30

    async def extract_answers(self, file_path: str) -> Dict[str, str]:
        """Extract answers from exam copy"""
        
        if file_path.lower().endswith('.pdf'):
            return await self._extract_from_pdf(file_path)
        else:
            return await self._extract_from_image(file_path)

    async def _extract_from_image(self, image_path: str) -> Dict[str, str]:
        """Extract text from image using OCR"""
        
        # Load and preprocess image
        image = cv2.imread(image_path)
        processed_image = self._preprocess_image(image)
        
        # Extract text
        text = pytesseract.image_to_string(processed_image)
        
        # Parse text to extract question-wise answers
        return self._parse_answers(text)

    async def _extract_from_pdf(self, pdf_path: str) -> Dict[str, str]:
        """Extract text from PDF by converting to images first"""
    
        try:
            from pdf2image import convert_from_path
            import tempfile
        
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)
        
            all_text = ""
        
            # Process each page
            for page_num, image in enumerate(images, start=1):
                # Convert PIL image to numpy array for preprocessing
                image_np = np.array(image)
            
                # Preprocess
                processed_image = self._preprocess_image(image_np)
            
                # Extract text
                page_text = pytesseract.image_to_string(processed_image)
                all_text += f"\n--- Page {page_num} ---\n{page_text}"
        
            return self._parse_answers(all_text)
        
        except Exception as e:
            print(f"PDF OCR Error: {str(e)}")
            return {}

    def _preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold
        _, threshold = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return threshold

    def _parse_answers(self, text: str) -> Dict[str, str]:
        """Parse extracted text to identify question-wise answers"""
        
        answers = {}
        lines = text.split('\n')
        current_question = None
        current_answer = []
        
        for line in lines:
            line = line.strip()
            
            # Check if line contains question number
            if self._is_question_line(line):
                # Save previous question's answer
                if current_question:
                    answers[current_question] = ' '.join(current_answer)
                
                # Start new question
                current_question = self._extract_question_number(line)
                current_answer = []
            elif current_question and line:
                current_answer.append(line)
        
        # Save last question's answer
        if current_question:
            answers[current_question] = ' '.join(current_answer)
        
        return answers

    def _is_question_line(self, line: str) -> bool:
        """Check if line contains question number"""
        import re
        # Updated pattern to match "Question 1:" format
        pattern = r'^\s*(?:Q\.?|Question|Ans\.?|Answer)?\s*(\d+)[.:]?\s*$'
        return bool(re.match(pattern, line, re.IGNORECASE))

    def _extract_question_number(self, line: str) -> str:
        """Extract question number from line"""
        import re
        pattern = r'^\s*(?:Q\.?|Question|Ans\.?|Answer)?\s*(\d+)[.:]?\s*'
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            return f"question_{match.group(1)}"
        return "question_unknown"