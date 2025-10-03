# debug_exam.py
import requests

BASE_URL = "http://localhost:8000/api/v1"

teacher_login = {
    "email": "test.teacher@example.com",
    "password": "teacher123",
    "user_type": "teacher"
}

response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test exam creation
exam_data = {
    "exam_code": "CS101-MID-2024",
    "subject_code": "CS101",
    "exam_name": "Computer Science Midterm",
    "exam_type": "midterm",
    "exam_date": "2024-12-15",
    "start_time": "10:00",
    "duration_minutes": 180,
    "total_marks": 100,
    "passing_marks": 40,
    "instructions": "Answer all questions clearly"
}

response = requests.post(f"{BASE_URL}/exams", json=exam_data, headers=headers)
print("Exam creation status:", response.status_code)
print("Exam response:", response.text)