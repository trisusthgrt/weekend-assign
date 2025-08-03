"""
Example usage of the Research Paper Management System API
"""

import requests
import json
from openai_wrapper import generate_openai_response

# API base URL
BASE_URL = "http://localhost:8000"

def example_user_registration():
    """Example: Register a new user"""
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "interests": "AI, Machine Learning"
    }
    
    response = requests.post(url, json=data)
    print("Registration Response:", response.status_code)
    if response.status_code == 201:
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error:", response.json())

def example_user_login():
    """Example: Login user"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "testuser",
        "password": "TestPass123!"
    }
    
    response = requests.post(url, json=data)
    print("Login Response:", response.status_code)
    if response.status_code == 200:
        token_data = response.json()
        print(json.dumps(token_data, indent=2))
        return token_data["access_token"]
    else:
        print("Error:", response.json())
        return None

def example_get_profile(token, user_id):
    """Example: Get user profile"""
    url = f"{BASE_URL}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print("Profile Response:", response.status_code)
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error:", response.json())

def example_openai_integration():
    """Example: Using OpenAI wrapper for research assistance"""
    system_prompt = """
    You are a research assistant that helps users analyze research papers and provide insights.
    """
    
    user_prompt = """
    Can you help me understand the key points I should look for when reviewing a machine learning research paper?
    """
    
    print("OpenAI Response:")
    generate_openai_response(system_prompt, user_prompt)

if __name__ == "__main__":
    print("=== Research Paper Management System Examples ===\n")
    
    # Example 1: User Registration
    print("1. User Registration:")
    example_user_registration()
    print("\n" + "="*50 + "\n")
    
    # Example 2: User Login
    print("2. User Login:")
    token = example_user_login()
    print("\n" + "="*50 + "\n")
    
    # Example 3: Get Profile (if login successful)
    if token:
        print("3. Get User Profile:")
        example_get_profile(token, 1)  # Assuming user ID 1
        print("\n" + "="*50 + "\n")
    
    # Example 4: OpenAI Integration
    print("4. OpenAI Integration (requires DNA_TOKEN):")
    # Uncomment the line below if you have a valid DNA_TOKEN
    # example_openai_integration()
    print("Set DNA_TOKEN in openai_wrapper.py to use this feature")
    
    print("\nExample complete!")