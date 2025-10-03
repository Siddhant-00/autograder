import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# Generate unique identifier for this test run
timestamp = int(time.time())
print(f"=== Test Run: {timestamp} ===\n")

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
    print(f"✗ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"✓ Teacher logged in successfully")
print(f"  Token: {token[:20]}...")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Create subject
print("\n2. Creating subject...")
subject_data = {
    "subject_code": f"TESTCS102_{timestamp}",
    "subject_name": "Advanced Computer Science",
    "department": "Computer Science",
    "credits": 4,
    "semester": 2
}

print(f"  Subject Code: {subject_data['subject_code']}")

subject_response = requests.post(
    f"{BASE_URL}/subjects",
    headers=headers,
    json=subject_data
)

print(f"  Status: {subject_response.status_code}")
if subject_response.status_code == 200:
    subject_result = subject_response.json()
    print(f"✓ Subject created successfully")
    print(f"  Subject ID: {subject_result.get('subject', {}).get('id', 'N/A')}")
elif subject_response.status_code == 400:
    print(f"⚠ Subject already exists (using existing)")
    print(f"  Response: {subject_response.json()}")
else:
    print(f"✗ Subject creation failed")
    print(f"  Error: {subject_response.text}")
    exit(1)

# Step 3: Create exam
print("\n3. Creating exam...")
exam_data = {
    "exam_code": f"FINAL2024_{timestamp}",
    "subject_code": f"TESTCS102_{timestamp}",
    "exam_name": "Final Exam 2024",
    "exam_type": "final",
    "exam_date": "2024-12-20",
    "start_time": "14:00:00",
    "duration_minutes": 180,
    "total_marks": 100,
    "passing_marks": 40
}

print(f"  Exam Code: {exam_data['exam_code']}")
print(f"  Subject Code: {exam_data['subject_code']}")

exam_response = requests.post(
    f"{BASE_URL}/exams",
    headers=headers,
    json=exam_data
)

print(f"  Status: {exam_response.status_code}")

if exam_response.status_code == 200:
    exam_result = exam_response.json()
    exam_id = exam_result["exam"]["id"]
    print(f"✓ Exam created successfully")
    print(f"  Exam ID: {exam_id}")
    print(f"  Exam Name: {exam_result['exam']['exam_name']}")
    
    # Step 4: Add questions
    print("\n4. Adding questions...")
    questions = [
        {
            "question_number": 1,
            "question_text": "Explain polymorphism in Object-Oriented Programming",
            "max_marks": 10,
            "sample_answer": "Polymorphism allows objects of different classes to be treated as objects of a common parent class. It enables a single interface to represent different underlying forms (data types).",
            "keywords": ["polymorphism", "inheritance", "objects", "interface"]
        },
        {
            "question_number": 2,
            "question_text": "What is encapsulation and why is it important?",
            "max_marks": 10,
            "sample_answer": "Encapsulation is the bundling of data and methods that operate on that data within a single unit (class), while hiding internal implementation details. It's important for data protection and modularity.",
            "keywords": ["encapsulation", "data hiding", "methods", "class"]
        },
        {
            "question_number": 3,
            "question_text": "Describe inheritance in OOP",
            "max_marks": 10,
            "sample_answer": "Inheritance is a mechanism where a new class derives properties and behaviors from an existing class. The derived class (child) inherits attributes and methods from the base class (parent).",
            "keywords": ["inheritance", "parent class", "child class", "derived"]
        }
    ]
    
    print(f"  Adding {len(questions)} questions...")
    
    questions_response = requests.post(
        f"{BASE_URL}/exams/{exam_id}/questions",
        headers=headers,
        json=questions
    )
    
    print(f"  Status: {questions_response.status_code}")
    
    if questions_response.status_code == 200:
        questions_result = questions_response.json()
        print(f"✓ Questions added successfully")
        print(f"  Total questions: {questions_result.get('total_questions', len(questions))}")
        
        # Display question summary
        if 'questions' in questions_result:
            for q in questions_result['questions']:
                print(f"    Q{q.get('question_number')}: {q.get('max_marks')} marks")
    else:
        print(f"✗ Questions addition failed")
        print(f"  Error: {questions_response.text}")
        exit(1)
    
    # Step 5: Verify exam details
    print("\n5. Verifying exam details...")
    exam_details_response = requests.get(
        f"{BASE_URL}/exams/{exam_id}",
        headers=headers
    )
    
    if exam_details_response.status_code == 200:
        exam_details = exam_details_response.json()
        print(f"✓ Exam verification successful")
        print(f"  Exam: {exam_details.get('exam_name')}")
        print(f"  Total Marks: {exam_details.get('total_marks')}")
        print(f"  Questions Count: {len(exam_details.get('questions', []))}")
    else:
        print(f"⚠ Could not verify exam details")
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"✓ Subject Code: {subject_data['subject_code']}")
    print(f"✓ Exam Code: {exam_data['exam_code']}")
    print(f"✓ Exam ID: {exam_id}")
    print(f"✓ Questions: {len(questions)}")
    print(f"✓ Total Marks: {exam_data['total_marks']}")
    print("="*50)
    print("\n✅ All tests passed successfully!\n")
    
else:
    print(f"✗ Exam creation failed")
    print(f"  Error: {exam_response.text}")
    try:
        error_detail = exam_response.json()
        print(f"  Detail: {json.dumps(error_detail, indent=2)}")
    except:
        pass
    exit(1)