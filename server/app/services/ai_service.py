# app/services/ai_service.py
from typing import Dict, Any, List
import asyncio
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.schema.grading import QuestionResult
import re

class AIGradingService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.7

    async def grade_question(
        self, 
        question_data: Dict[str, Any], 
        student_answer: str
    ) -> QuestionResult:
        """Grade a single question using AI"""
        question_text = question_data.get("question", "")
        model_answer = question_data.get("model_answer", "")
        max_marks = question_data.get("marks", 0)
        question_number = question_data.get("question_number", 0)
        
        if not student_answer.strip():
            return QuestionResult(
                question_number=question_number,
                extracted_answer=student_answer,
                marks_obtained=0,
                max_marks=max_marks,
                feedback="No answer provided",
                confidence_score=1.0
            )
        
        # Calculate semantic similarity asynchronously
        similarity_score = await self._calculate_similarity(model_answer, student_answer)
        
        # Calculate marks and feedback
        marks_obtained, feedback, confidence = await self._calculate_marks(
            question_data, student_answer, model_answer, similarity_score
        )
        
        return QuestionResult(
            question_number=question_number,
            extracted_answer=student_answer,
            marks_obtained=round(marks_obtained, 2),
            max_marks=max_marks,
            feedback=feedback,
            confidence_score=round(confidence, 2)
        )

    async def _calculate_similarity(self, model_answer: str, student_answer: str) -> float:
        """Calculate semantic similarity between model and student answers asynchronously"""
        loop = asyncio.get_running_loop()
        model_embedding = await loop.run_in_executor(None, self.embedding_model.encode, [model_answer])
        student_embedding = await loop.run_in_executor(None, self.embedding_model.encode, [student_answer])
        similarity = cosine_similarity(model_embedding, student_embedding)[0][0]
        return float(similarity)
    
    async def _calculate_marks(
        self, 
        question_data: Dict[str, Any], 
        student_answer: str, 
        model_answer: str, 
        similarity_score: float
    ) -> tuple:
        """Calculate marks, feedback, and confidence"""
        max_marks = question_data.get("marks", 0)
        question_type = question_data.get("type", "descriptive")
        keywords = question_data.get("keywords", [])
        
        # Base scoring based on similarity
        if similarity_score >= 0.9:
            marks_ratio = 1.0
            feedback = "Excellent answer"
        elif similarity_score >= 0.7:
            marks_ratio = 0.8
            feedback = "Good answer with minor gaps"
        elif similarity_score >= 0.5:
            marks_ratio = 0.6
            feedback = "Partial answer, missing key points"
        elif similarity_score >= 0.3:
            marks_ratio = 0.4
            feedback = "Basic understanding shown, needs improvement"
        else:
            marks_ratio = 0.2
            feedback = "Answer needs significant improvement"
        
        # Adjust for keywords
        if keywords:
            keyword_score = await self._check_keywords(student_answer, keywords)
            marks_ratio = (marks_ratio * 0.7) + (keyword_score * 0.3)
            if keyword_score > 0.8:
                feedback += " - Contains most key terms"
            elif keyword_score > 0.5:
                feedback += " - Contains some key terms"
            else:
                feedback += " - Missing important key terms"
        
        # Question type adjustments
        if question_type == "numerical":
            marks_ratio = await self._grade_numerical_answer(student_answer, model_answer, marks_ratio)
        elif question_type == "mcq":
            marks_ratio = 1.0 if similarity_score > 0.8 else 0.0
            feedback = "Correct" if marks_ratio == 1.0 else "Incorrect"
        
        marks_obtained = max_marks * marks_ratio
        confidence = max(0.1, min(0.9, similarity_score + 0.1))
        
        return marks_obtained, feedback, confidence

    async def _check_keywords(self, student_answer: str, keywords: List[str]) -> float:
        """Check for presence of keywords in student answer"""
        student_answer_lower = student_answer.lower()
        found_keywords = sum(1 for keyword in keywords if keyword.lower() in student_answer_lower)
        return found_keywords / len(keywords) if keywords else 0

    async def _grade_numerical_answer(self, student_answer: str, model_answer: str, base_ratio: float) -> float:
        """Grade numerical answers with tolerance"""
        try:
            student_nums = self._extract_numbers(student_answer)
            model_nums = self._extract_numbers(model_answer)
            if not student_nums or not model_nums:
                return base_ratio

            student_primary = student_nums[-1]
            model_primary = model_nums[-1]

            if model_primary != 0:
                percentage_diff = abs(student_primary - model_primary) / abs(model_primary)
                if percentage_diff <= 0.01:
                    return 1.0
                elif percentage_diff <= 0.05:
                    return 0.9
                elif percentage_diff <= 0.1:
                    return 0.7
                else:
                    return 0.3
            else:
                return 1.0 if student_primary == model_primary else 0.0
        except Exception:
            return base_ratio

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numbers from text"""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        return numbers

    async def generate_overall_feedback(self, question_results: List[QuestionResult], percentage: float) -> str:
        """Generate overall feedback for the exam"""
        if percentage >= 90:
            grade = "Excellent"
            feedback = "Outstanding performance! You have demonstrated comprehensive understanding."
        elif percentage >= 80:
            grade = "Very Good"
            feedback = "Very good work! Minor areas for improvement identified."
        elif percentage >= 70:
            grade = "Good"
            feedback = "Good performance with some areas needing attention."
        elif percentage >= 60:
            grade = "Satisfactory"
            feedback = "Satisfactory work, but significant improvement needed in several areas."
        elif percentage >= 50:
            grade = "Pass"
            feedback = "Basic understanding shown, but major gaps need to be addressed."
        else:
            grade = "Needs Improvement"
            feedback = "Significant study and practice required to improve performance."

        low_scoring_questions = [qr for qr in question_results if (qr.marks_obtained / qr.max_marks) < 0.6]
        if low_scoring_questions:
            feedback += f" Focus on improving questions {', '.join([str(qr.question_number) for qr in low_scoring_questions[:3]])}."

        return f"{grade}: {feedback}"
