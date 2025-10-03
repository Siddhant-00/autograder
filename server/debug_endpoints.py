# debug_endpoints.py
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login first
teacher_login = {
    "email": "test.teacher@example.com",
    "password": "teacher123", 
    "user_type": "teacher"
}

response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
print("Login status:", response.status_code)
if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test subject creation
    subject_data = {"subject_code": "TEST101", "subject_name": "Test Subject"}
    response = requests.post(f"{BASE_URL}/subjects", json=subject_data, headers=headers)
    print("Subject creation status:", response.status_code)
    print("Subject response:", response.text)