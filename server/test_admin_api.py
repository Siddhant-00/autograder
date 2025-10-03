import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Step 1: Login as teacher
print("1. Logging in as teacher...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "test.teacher32@example.com",
        "password": "teacher34",
        "user_type": "teacher"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"✓ Teacher logged in")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Create subject
print("\n2. Creating subject...")
subject_data = {
    "subject_code": "TESTCS102",
    "subject_name": "Advanced Computer Science",
    "department": "Computer Science",
    "credits": 4,
    "semester": 2
}

subject_response = requests.post(
    f"{BASE_URL}/subjects",
    headers=headers,
    json=subject_data
)

print(f"Subject creation status: {subject_response.status_code}")
if subject_response.status_code == 200:
    print(f"✓ Subject created: {subject_response.json()}")
elif subject_response.status_code == 400:
    print(f"Subject already exists (OK): {subject_response.json()}")
else:
    print(f"Subject creation failed: {subject_response.text}")

# Step 3: Create exam
print("\n3. Creating exam...")
exam_data = {
    "exam_code": "FINAL2024",
    "subject_code": "TESTCS102",  # ✓ Correct
    "exam_name": "Final Exam 2024",
    "exam_type": "final",
    "exam_date": "2024-12-20",
    "start_time": "14:00:00",  # Add seconds
    "duration_minutes": 180,
    "total_marks": 100,
    "passing_marks": 40
}

exam_response = requests.post(
    f"{BASE_URL}/exams",
    headers=headers,
    json=exam_data
)

print(f"Exam creation status: {exam_response.status_code}")
print(f"Response: {json.dumps(exam_response.json(), indent=2)}")

if exam_response.status_code == 200:
    exam_id = exam_response.json()["exam"]["id"]
    print(f"\n✓ Exam created successfully! ID: {exam_id}")
    
    # Step 4: Add questions
    print("\n4. Adding questions...")
    questions = [
        {
            "question_number": 1,
            "question_text": "Explain polymorphism in OOP",
            "max_marks": 10,
            "sample_answer": "Polymorphism allows objects of different classes to be treated as objects of a common parent class",
            "keywords": ["polymorphism", "inheritance", "objects"]
        },
        {
            "question_number": 2,
            "question_text": "What is encapsulation?",
            "max_marks": 10,
            "sample_answer": "Encapsulation is bundling data and methods together while hiding internal details",
            "keywords": ["encapsulation", "data hiding", "methods"]
        }
    ]
    
    questions_response = requests.post(
        f"{BASE_URL}/exams/{exam_id}/questions",
        headers=headers,
        json=questions
    )
    
    print(f"Questions status: {questions_response.status_code}")
    print(f"Response: {json.dumps(questions_response.json(), indent=2)}")
else:
    print(f"✗ Exam creation failed: {exam_response.text}")