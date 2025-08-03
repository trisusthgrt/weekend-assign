"""
Example usage of Milestone 2: Upload, download & feedback points
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def example_paper_upload():
    """Example: Upload a research paper (Researcher or Admin only)"""
    
    # First, login to get token
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "username": "researcher_user",  # Must be a researcher or admin
        "password": "TestPass123!"
    }
    
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code != 200:
        print("Login failed:", login_response.json())
        return None
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload paper
    upload_url = f"{BASE_URL}/papers/upload"
    
    # Prepare multipart form data
    files = {
        'file': ('research_paper.pdf', open('sample_paper.pdf', 'rb'), 'application/pdf')
    }
    
    # Publication date (not in future)
    pub_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    data = {
        'title': 'Advanced Machine Learning Techniques in Healthcare',
        'authors': json.dumps([1, 2]),  # User IDs of authors (must exist in system)
        'publication_date': pub_date,
        'journal': 'Journal of AI in Medicine',
        'abstract': 'This paper explores advanced ML techniques for healthcare applications...',
        'keywords': 'machine learning, healthcare, AI, medical diagnosis',
        'citations': '10',
        'license': 'CC BY 4.0'
    }
    
    response = requests.post(upload_url, headers=headers, files=files, data=data)
    print("Upload Response:", response.status_code)
    if response.status_code == 201:
        print(json.dumps(response.json(), indent=2))
        return response.json()["id"]  # Return paper ID
    else:
        print("Error:", response.json())
        return None

def example_add_feedback(paper_id, user_id, token):
    """Example: Add feedback to a paper"""
    
    url = f"{BASE_URL}/papers/feedback/{paper_id}/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    feedback_data = {
        "content": "This is an excellent paper with great insights into ML applications in healthcare. The methodology is sound and results are convincing.",
        "rating": 5,
        "feedback_type": "peer_review"
    }
    
    response = requests.put(url, headers=headers, json=feedback_data)
    print("Feedback Response:", response.status_code)
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error:", response.json())

def example_download_paper(paper_id, token):
    """Example: Download a paper (costs 10 points)"""
    
    # Step 1: Authorize download (deducts points)
    url = f"{BASE_URL}/papers/download/{paper_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, headers=headers)
    print("Download Authorization Response:", response.status_code)
    
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
        
        # Step 2: Actually download the file
        file_url = f"{BASE_URL}/papers/download-file/{paper_id}"
        file_response = requests.get(file_url, headers=headers)
        
        if file_response.status_code == 200:
            # Save file
            with open(f'downloaded_paper_{paper_id}.pdf', 'wb') as f:
                f.write(file_response.content)
            print(f"File downloaded successfully as 'downloaded_paper_{paper_id}.pdf'")
        else:
            print("File download failed:", file_response.status_code)
    
    elif response.status_code == 402:
        print("Insufficient points!")
        print("Error:", response.json())
    else:
        print("Error:", response.json())

def example_list_papers(token):
    """Example: List all papers"""
    
    url = f"{BASE_URL}/papers"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print("List Papers Response:", response.status_code)
    if response.status_code == 200:
        papers = response.json()
        print(f"Found {len(papers)} papers:")
        for paper in papers:
            print(f"- ID: {paper['id']}, Title: {paper['title']}")
    else:
        print("Error:", response.json())

def example_get_paper_details(paper_id, token):
    """Example: Get paper details"""
    
    url = f"{BASE_URL}/papers/{paper_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print("Paper Details Response:", response.status_code)
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error:", response.json())

def example_get_paper_feedback(paper_id, token):
    """Example: Get all feedback for a paper"""
    
    url = f"{BASE_URL}/papers/{paper_id}/feedback"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print("Paper Feedback Response:", response.status_code)
    if response.status_code == 200:
        feedback_list = response.json()
        print(f"Found {len(feedback_list)} feedback entries:")
        for feedback in feedback_list:
            print(f"- Rating: {feedback['rating']}, Content: {feedback['content'][:50]}...")
    else:
        print("Error:", response.json())

def get_user_points(user_id, token):
    """Helper: Get user's current points"""
    
    url = f"{BASE_URL}/users/{user_id}/points"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        points_data = response.json()
        print(f"Current points: {points_data['hasher_points']}")
        return points_data['hasher_points']
    else:
        print("Error getting points:", response.json())
        return 0

if __name__ == "__main__":
    print("=== Milestone 2: Upload, download & feedback points Examples ===\n")
    
    # You'll need to create these first:
    # 1. A researcher user account
    # 2. A sample PDF file named 'sample_paper.pdf'
    
    print("Prerequisites:")
    print("1. Create a researcher account first")
    print("2. Have a sample PDF file ready")
    print("3. Make sure the server is running\n")
    
    # Example 1: Upload a paper
    print("1. Paper Upload (Researcher/Admin only):")
    # paper_id = example_paper_upload()
    print("Uncomment example_paper_upload() and ensure you have a researcher account")
    paper_id = 1  # Assume paper ID 1 for examples
    print(f"Using paper ID: {paper_id}\n")
    
    print("="*50 + "\n")
    
    # Login for other examples
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "username": "testuser",  # Any user for feedback/download
        "password": "TestPass123!"
    }
    
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        user_id = 1  # Assume user ID 1
        
        # Example 2: Check points before operations
        print("2. Check Current Points:")
        initial_points = get_user_points(user_id, token)
        print("\n" + "="*50 + "\n")
        
        # Example 3: Add feedback (earns 5 points)
        print("3. Add Feedback (+5 points):")
        example_add_feedback(paper_id, user_id, token)
        print("\n" + "="*50 + "\n")
        
        # Example 4: Check points after feedback
        print("4. Points After Feedback:")
        get_user_points(user_id, token)
        print("\n" + "="*50 + "\n")
        
        # Example 5: List papers
        print("5. List All Papers:")
        example_list_papers(token)
        print("\n" + "="*50 + "\n")
        
        # Example 6: Get paper details
        print("6. Paper Details:")
        example_get_paper_details(paper_id, token)
        print("\n" + "="*50 + "\n")
        
        # Example 7: Download paper (costs 10 points)
        print("7. Download Paper (-10 points):")
        example_download_paper(paper_id, token)
        print("\n" + "="*50 + "\n")
        
        # Example 8: Check final points
        print("8. Final Points Balance:")
        get_user_points(user_id, token)
        print("\n" + "="*50 + "\n")
        
        # Example 9: Get paper feedback
        print("9. View Paper Feedback:")
        example_get_paper_feedback(paper_id, token)
        
    else:
        print("Login failed. Make sure you have a user account created.")
    
    print("\nExamples complete!")
    print("\nPoint System Summary:")
    print("- Daily login: +10 points")
    print("- Paper upload (researcher): +100 points per author")
    print("- Feedback: +5 points")
    print("- Download: -10 points")
    print("- Admins: No points awarded/deducted")