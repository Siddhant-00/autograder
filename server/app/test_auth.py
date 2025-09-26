import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_registration():
    """Test user registration"""
    print("Testing Student Registration...")
    
    student_data = {
        "email": "john.doe@example.com",
        "password": "securepassword123",
        "full_name": "John Doe",
        "user_type": "student",
        "student_id": "ST001",
        "phone": "+1234567890",
        "course": "Computer Science"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
    
    if response.status_code == 200:
        print("✅ Student registration successful!")
        print(json.dumps(response.json(), indent=2))
        return response.json()["access_token"]
    else:
        print("❌ Student registration failed:")
        print(f"Status Code: {response.status_code}")
        print(response.text)
        return None

def test_login():
    """Test user login"""
    print("\nTesting Student Login...")
    
    login_data = {
        "email": "john.doe@example.com",
        "password": "securepassword123",
        "user_type": "student"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Student login successful!")
        print(json.dumps(response.json(), indent=2))
        return response.json()["access_token"]
    else:
        print("❌ Student login failed:")
        print(f"Status Code: {response.status_code}")
        print(response.text)
        return None

def test_protected_route(token):
    """Test accessing protected route"""
    print("\nTesting Protected Route...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ Protected route access successful!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ Protected route access failed:")
        print(f"Status Code: {response.status_code}")
        print(response.text)

def test_teacher_registration():
    """Test teacher registration"""
    print("\nTesting Teacher Registration...")
    
    teacher_data = {
        "email": "prof.smith@example.com",
        "password": "teacherpassword123",
        "full_name": "Prof. John Smith",
        "user_type": "teacher",
        "teacher_id": "T001",
        "phone": "+1234567891",
        "department": "Computer Science"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=teacher_data)
    
    if response.status_code == 200:
        print("✅ Teacher registration successful!")
        print(json.dumps(response.json(), indent=2))
        return response.json()["access_token"]
    else:
        print("❌ Teacher registration failed:")
        print(f"Status Code: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🚀 Starting Authentication System Tests")
    print("=" * 50)
    
    # Test student registration
    student_token = test_registration()
    
    if student_token:
        # Test protected route with registration token
        test_protected_route(student_token)
    
    # Test student login
    login_token = test_login()
    
    if login_token:
        # Test protected route with login token
        test_protected_route(login_token)
    
    # Test teacher registration
    teacher_token = test_teacher_registration()
    
    if teacher_token:
        # Test protected route with teacher token
        test_protected_route(teacher_token)

if __name__ == "__main__":
    main()