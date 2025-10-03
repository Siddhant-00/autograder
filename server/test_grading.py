import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"  # Added /api/v1
EXAM_ID = "58221809-aff9-4cd3-ab82-2ec2284498a5"

# Step 1: Login as a student
print("1. Logging in as student...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "test.student01564@example.com",
        "password": "student15352",
        "user_type": "student"  # Added user_type
    }
)
print(f"Login status: {login_response.status_code}")

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
student_id = login_response.json()["user"]["id"]
print(f"✓ Logged in successfully. Student ID: {student_id}")

# Step 2: Create a simple test PDF
print("\n2. Creating test answer sheet...")
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

pdf_path = "test_answer_sheet.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)
c.setFont("Helvetica", 12)

# Write some answers
c.drawString(100, 750, f"Exam ID: {EXAM_ID}")
c.drawString(100, 730, f"Student ID: {student_id}")
c.drawString(100, 700, "Question 1:")
c.drawString(100, 680, "Python is a high-level programming language known for its simplicity.")
c.drawString(100, 660, "It is widely used for web development, data science, and automation.")
c.drawString(100, 620, "Question 2:")
c.drawString(100, 600, "Object-oriented programming is a paradigm based on objects and classes.")

c.save()
print(f"✓ Created test PDF: {pdf_path}")

# Step 3: Upload the answer sheet
print("\n3. Uploading answer sheet...")
headers = {"Authorization": f"Bearer {token}"}

with open(pdf_path, "rb") as f:
    files = {"file": ("test_answer.pdf", f, "application/pdf")}
    
    upload_response = requests.post(
        f"{BASE_URL}/upload/{EXAM_ID}",  # Changed endpoint format
        headers=headers,
        files=files
    )

print(f"Upload status: {upload_response.status_code}")
print(f"Response: {json.dumps(upload_response.json(), indent=2)}")

if upload_response.status_code == 200:
    upload_data = upload_response.json()
    upload_id = upload_data.get("upload_id")
    print(f"\n✓ Upload successful! Upload ID: {upload_id}")
    
    # Step 4: Check upload status
    print("\n4. Checking upload status...")
    status_response = requests.get(
        f"{BASE_URL}/uploads/student",  # Changed endpoint
        headers=headers
    )
    print(f"Status: {status_response.status_code}")
    print(f"Uploads: {json.dumps(status_response.json(), indent=2)}")
    
    # Step 5: Wait and check for results
    import time
    print("\n5. Waiting for grading to complete (15 seconds)...")
    time.sleep(15)
    
    results_response = requests.get(
        f"{BASE_URL}/results/student",  # Changed endpoint
        headers=headers
    )
    print(f"\nResults status: {results_response.status_code}")
    print(f"Results: {json.dumps(results_response.json(), indent=2)}")
else:
    print(f"✗ Upload failed: {upload_response.text}")