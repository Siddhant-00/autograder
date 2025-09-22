from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException, status

from app.database.session import DatabaseSession
from app.services.ocr_service import OCRService
from app.services.ai_service import AIGradingService
from app.schema.grading import GradingResult, QuestionResult


class GradingService:
    def __init__(self, access_token: str):
        self.db_session = DatabaseSession(access_token)
        self.ocr_service = OCRService()
        self.ai_service = AIGradingService()

    async def grade_exam_session(
        self,
        exam_session_id: str,
        marking_scheme: Dict[str, Any],
        user_id: str,
    ) -> GradingResult:
        """Grade an exam session"""

        # Get exam session details
        session_data = await self._get_exam_session(exam_session_id, user_id)

        # Extract answers using OCR
        extracted_answers = await self.ocr_service.extract_answers(
            session_data["file_path"]
        )

        # Grade each question
        question_results = []
        total_marks = 0
        max_total_marks = 0

        for question_num, question_data in marking_scheme.items():
            if question_num.startswith("question_"):
                extracted_answer = extracted_answers.get(question_num, "")

                # Grade this question
                question_result = await self.ai_service.grade_question(
                    question_data, extracted_answer
                )

                question_results.append(question_result)
                total_marks += question_result.marks_obtained
                max_total_marks += question_result.max_marks

        # Calculate percentage
        percentage = (total_marks / max_total_marks * 100) if max_total_marks > 0 else 0

        # Create grading result
        grading_result = GradingResult(
            exam_session_id=exam_session_id,
            total_marks=total_marks,
            max_marks=max_total_marks,
            percentage=percentage,
            question_results=question_results,
            overall_feedback=await self.ai_service.generate_overall_feedback(
                question_results, percentage
            ),
            graded_at=datetime.utcnow(),
        )

        # Save to database
        await self._save_grading_result(grading_result)

        # Update exam session status
        await self._update_exam_session_status(exam_session_id, "graded")

        return grading_result

    async def get_grading_status(self, exam_session_id: str) -> Dict[str, Any]:
        """Get grading status for an exam session"""
        try:
            result = (
                self.db_session.client.table("exam_sessions")
                .select("id,status,graded_at")
                .eq("id", exam_session_id)
                .execute()
            )

            if not result.data:
                raise HTTPException(status_code=404, detail="Exam session not found")

            return result.data[0]

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get grading status: {str(e)}"
            )

    async def get_user_results(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all results for a user"""
        try:
            result = (
                self.db_session.client.table("grading_results")
                .select("*")
                .eq("student_id", user_id)
                .order("graded_at", desc=True)
                .execute()
            )

            return result.data or []

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get user results: {str(e)}"
            )

    async def get_detailed_result(
        self, exam_session_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Get detailed result for an exam session"""
        try:
            result = (
                self.db_session.client.table("grading_results")
                .select("*")
                .eq("exam_session_id", exam_session_id)
                .eq("student_id", user_id)
                .single()
                .execute()
            )

            if not result.data:
                raise HTTPException(
                    status_code=404, detail="Grading result not found"
                )

            return result.data

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get detailed result: {str(e)}"
            )

    async def get_exam_analytics(self, exam_id: str) -> Dict[str, Any]:
        """Get analytics for an exam"""
        try:
            sessions = (
                self.db_session.client.table("exam_sessions")
                .select("id,status,total_marks,max_marks")
                .eq("exam_id", exam_id)
                .execute()
            )

            if not sessions.data:
                return {}

            total_submissions = len(sessions.data)
            graded_count = sum(1 for s in sessions.data if s["status"] == "graded")
            all_scores = [s["total_marks"] for s in sessions.data if s["status"] == "graded"]

            question_analytics: Dict[str, Dict[str, Any]] = {}
            for session in sessions.data:
                if session["status"] == "graded":
                    # Assume detailed results stored in grading_results
                    result = (
                        self.db_session.client.table("grading_results")
                        .select("question_results")
                        .eq("exam_session_id", session["id"])
                        .single()
                        .execute()
                    )
                    if result.data and "question_results" in result.data:
                        for q in result.data["question_results"]:
                            q_num = q["question_num"]
                            if q_num not in question_analytics:
                                question_analytics[q_num] = {
                                    "count": 0,
                                    "total_marks": 0,
                                    "max_marks": q["max_marks"],
                                    "average_score": 0,
                                    "average_percentage": 0,
                                }
                            question_analytics[q_num]["count"] += 1
                            question_analytics[q_num]["total_marks"] += q[
                                "marks_obtained"
                            ]

            # Calculate averages
            for q_num in question_analytics:
                if question_analytics[q_num]["count"] > 0:
                    question_analytics[q_num]["average_score"] = (
                        question_analytics[q_num]["total_marks"]
                        / question_analytics[q_num]["count"]
                    )
                    question_analytics[q_num]["average_percentage"] = (
                        question_analytics[q_num]["average_score"]
                        / question_analytics[q_num]["max_marks"]
                        * 100
                        if question_analytics[q_num]["max_marks"] > 0
                        else 0
                    )

            analytics = {
                "exam_id": exam_id,
                "total_submissions": total_submissions,
                "graded_submissions": graded_count,
                "average_score": sum(all_scores) / len(all_scores)
                if all_scores
                else 0,
                "highest_score": max(all_scores) if all_scores else 0,
                "lowest_score": min(all_scores) if all_scores else 0,
                "question_analytics": question_analytics,
                "score_distribution": self._calculate_score_distribution(all_scores),
            }

            return analytics

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get exam analytics: {str(e)}"
            )

    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution by grade bands"""
        distribution = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "50-59": 0,
            "below-50": 0,
        }

        for score in scores:
            if score >= 90:
                distribution["90-100"] += 1
            elif score >= 80:
                distribution["80-89"] += 1
            elif score >= 70:
                distribution["70-79"] += 1
            elif score >= 60:
                distribution["60-69"] += 1
            elif score >= 50:
                distribution["50-59"] += 1
            else:
                distribution["below-50"] += 1

        return distribution

    async def _get_exam_session(self, exam_session_id: str, user_id: str) -> Dict[str, Any]:
        """Get exam session data"""
        try:
            result = (
                self.db_session.client.table("exam_sessions")
                .select("*")
                .eq("id", exam_session_id)
                .eq("student_id", user_id)
                .execute()
            )

            if not result.data:
                raise HTTPException(
                    status_code=404, detail="Exam session not found or access denied"
                )

            return result.data[0]

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get exam session: {str(e)}"
            )

    async def _save_grading_result(self, result: GradingResult) -> None:
        """Save grading result to database"""
        result_data = result.dict()
        await self.db_session.save_grading_result(result_data)

    async def _update_exam_session_status(self, exam_session_id: str, status: str) -> None:
        """Update exam session status"""
        try:
            update_data = {
                "status": status,
                "graded_at": datetime.utcnow().isoformat() if status == "graded" else None,
            }

            self.db_session.client.table("exam_sessions").update(update_data).eq(
                "id", exam_session_id
            ).execute()

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update exam session status: {str(e)}",
            )
