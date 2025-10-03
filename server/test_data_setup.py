import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def setup_test_data():
    print("🔧 Setting up test data...")
    
    # First, authenticate as teacher
    teacher_login = {
        "email": "test.teacher@example.com",
        "password": "teacher123",
        "user_type": "teacher"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
    if response.status_code != 200:
        print("❌ Teacher login failed. Run test_auth.py first.")
        return False
    
    teacher_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Create a subject
    subject_data = {
        "subject_code": "CS101",
        "subject_name": "Introduction to Computer Science",
        "department": "Computer Science",
        "credits": 3,
        "semester": 1
    }
    
    response = requests.post(f"{BASE_URL}/subjects", json=subject_data, headers=headers)
    if response.status_code == 200:
        print("✅ Test subject created")
    else:
        print(f"⚠️  Subject creation: {response.status_code}")
    
    # Create an exam
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
    if response.status_code == 200:
        exam_id = response.json()["exam"]["id"]
        print(f"✅ Test exam created: {exam_id}")
        
        # Add questions to the exam
        questions = [
            {
                "question_number": 1,
                "question_text": "What is object-oriented programming?",
                "max_marks": 10,
                "sample_answer": "Object-oriented programming is a programming paradigm that uses objects and classes.",
                "keywords": ["object", "class", "encapsulation", "inheritance"]
            },
            {
                "question_number": 2,
                "question_text": "Explain the concept of inheritance in programming.",
                "max_marks": 15,
                "sample_answer": "Inheritance allows a class to inherit properties and methods from another class.",
                "keywords": ["inheritance", "parent class", "child class", "extends"]
            }
        ]
        
        response = requests.post(f"{BASE_URL}/exams/{exam_id}/questions", json=questions, headers=headers)
        if response.status_code == 200:
            print("✅ Test questions added")
            return exam_id
        else:
            print(f"⚠️  Questions creation: {response.status_code}")
    else:
        print(f"⚠️  Exam creation: {response.status_code}")
    
    return None

if __name__ == "__main__":
    exam_id = setup_test_data()
    if exam_id:
        print(f"🎉 Test data setup complete! Exam ID: {exam_id}")
        print("You can now run the comprehensive tests.")
    else:
        print("❌ Test data setup failed.")