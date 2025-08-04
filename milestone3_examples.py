"""
Example usage of Milestone 3: Chat System (RAG) 
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def login_and_get_token(username="testuser", password="TestPass123!"):
    """Helper function to login and get JWT token."""
    login_url = f"{BASE_URL}/auth/login"
    login_data = {"username": username, "password": password}
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Login failed:", response.json())
        return None

def check_user_points(token, user_id=1):
    """Check user's current points balance."""
    url = f"{BASE_URL}/users/{user_id}/points"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        points = response.json()["hasher_points"]
        print(f"Current points: {points}")
        return points
    else:
        print("Error getting points:", response.json())
        return 0

def example_chat_with_paper(token, paper_id=1):
    """Example: Start a chat session with a research paper."""
    print(f"\n🤖 Starting chat with paper {paper_id}...")
    
    url = f"{BASE_URL}/chat/{paper_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Example questions to ask about a research paper
    questions = [
        "What is the main research question addressed in this paper?",
        "What methodology did the authors use?",
        "What are the key findings and results?",
        "What are the limitations of this study?",
        "How does this work contribute to the field?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i} ---")
        print(f"Q: {question}")
        
        chat_data = {"query": question}
        response = requests.post(url, headers=headers, json=chat_data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Session ID: {result['session_id']}")
            print(f"Points deducted: {result['points_deducted']}")
            print(f"Remaining points: {result['remaining_points']}")
            print(f"Processing status: {result['processing_status']}")
            print(f"Relevant chunks: {result['relevant_chunks_count']}")
            print(f"A: {result['response'][:200]}...")  # First 200 chars
            
            # Return session ID for further use
            if i == 1:
                session_id = result['session_id']
                
        elif response.status_code == 402:
            print("❌ Insufficient points!")
            print("Error:", response.json())
            break
        elif response.status_code == 404:
            print("❌ Paper not found!")
            print("Error:", response.json())
            break
        else:
            print("❌ Error:", response.json())
            break
        
        # Small delay between questions
        import time
        time.sleep(1)
    
    return session_id if 'session_id' in locals() else None

def example_get_chat_sessions(token):
    """Example: Get all chat sessions for user."""
    print("\n📋 Getting user's chat sessions...")
    
    url = f"{BASE_URL}/chat/sessions"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"Found {len(sessions)} chat sessions:")
        
        for session in sessions:
            print(f"- Session: {session['session_id'][:8]}...")
            print(f"  Paper: {session['paper_title']}")
            print(f"  Messages: {session['message_count']}")
            print(f"  Last interaction: {session['last_interaction']}")
            print(f"  Chunks processed: {session['chunks_processed']}")
            print()
            
        return sessions
    else:
        print("Error:", response.json())
        return []

def example_get_chat_history(token, session_id):
    """Example: Get chat history for a specific session."""
    print(f"\n💬 Getting chat history for session {session_id[:8]}...")
    
    url = f"{BASE_URL}/chat/sessions/{session_id}/history"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        history = response.json()
        session_info = history['session']
        messages = history['messages']
        
        print(f"Paper: {session_info['paper_title']}")
        print(f"Total messages: {len(messages)}")
        print(f"Total points spent: {history['total_points_spent']}")
        print(f"Session created: {session_info['created_at']}")
        print()
        
        print("💬 Conversation History:")
        for msg in messages:
            timestamp = msg['timestamp'][:19]  # Remove microseconds
            if msg['message_type'] == 'user':
                print(f"[{timestamp}] 👤 User (cost: {msg['points_cost']} points):")
                print(f"    {msg['content']}")
            else:
                chunks_info = f" (used {msg['relevant_chunks_count']} chunks)" if msg['relevant_chunks_count'] > 0 else ""
                print(f"[{timestamp}] 🤖 Assistant{chunks_info}:")
                print(f"    {msg['content'][:150]}...")  # First 150 chars
            print()
            
        return history
    else:
        print("Error:", response.json())
        return None

def example_deactivate_session(token, session_id):
    """Example: Deactivate a chat session."""
    print(f"\n🗑️ Deactivating session {session_id[:8]}...")
    
    url = f"{BASE_URL}/chat/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Session deactivated successfully")
        print(response.json())
    else:
        print("Error:", response.json())

def example_insufficient_points_scenario(token):
    """Example: Test behavior when user has insufficient points."""
    print("\n💸 Testing insufficient points scenario...")
    
    # First, let's spend all points by asking many questions
    url = f"{BASE_URL}/chat/1"  # Assuming paper ID 1 exists
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ask questions until we run out of points
    question_count = 0
    while True:
        chat_data = {"query": f"Test question number {question_count + 1}"}
        response = requests.post(url, headers=headers, json=chat_data)
        
        if response.status_code == 402:
            print(f"✅ Ran out of points after {question_count} questions")
            print("Error response:", response.json())
            break
        elif response.status_code == 200:
            result = response.json()
            print(f"Question {question_count + 1}: {result['remaining_points']} points left")
            question_count += 1
            
            if question_count > 20:  # Safety break
                print("⚠️ Stopping after 20 questions to prevent infinite loop")
                break
        else:
            print("Unexpected error:", response.json())
            break

def run_comprehensive_chat_demo():
    """Run a comprehensive demo of the chat system."""
    print("🚀 MILESTONE 3: CHAT SYSTEM (RAG) DEMO")
    print("=" * 60)
    
    # Login
    print("1. Logging in...")
    token = login_and_get_token()
    if not token:
        print("❌ Could not login. Make sure you have a user account.")
        return
    
    # Check initial points
    print("\n2. Checking initial points...")
    initial_points = check_user_points(token)
    
    # Start chat with paper
    print("\n3. Starting chat with research paper...")
    session_id = example_chat_with_paper(token, paper_id=1)
    
    # Check points after chat
    print("\n4. Checking points after chat...")
    remaining_points = check_user_points(token)
    points_spent = initial_points - remaining_points
    print(f"Points spent on chat: {points_spent}")
    
    # Get chat sessions
    print("\n5. Getting all chat sessions...")
    sessions = example_get_chat_sessions(token)
    
    # Get chat history
    if session_id and sessions:
        print("\n6. Getting chat history...")
        history = example_get_chat_history(token, session_id)
    
    # Demonstrate points management
    if remaining_points < 10:
        print("\n7. Testing insufficient points scenario...")
        example_insufficient_points_scenario(token)
    
    print("\n" + "=" * 60)
    print("✅ Chat system demo completed!")
    print("\n💡 Key Features Demonstrated:")
    print("- RAG-based question answering")
    print("- Points deduction system (2 points per query)")
    print("- Chat session management")
    print("- Document processing and chunking")
    print("- Vector similarity search")
    print("- Chat history tracking")
    print("- Insufficient points handling")

if __name__ == "__main__":
    print("🤖 RAG CHAT SYSTEM EXAMPLES")
    print("=" * 40)
    
    print("\nPrerequisites:")
    print("1. Server must be running (python main.py)")
    print("2. You need a user account with some points")
    print("3. At least one research paper must be uploaded")
    print("4. Install RAG dependencies: pip install -r requirements.txt")
    print()
    
    # Check if user wants to run the full demo
    response = input("Run comprehensive chat demo? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        run_comprehensive_chat_demo()
    else:
        print("Demo cancelled. You can run individual functions:")
        print("- login_and_get_token()")
        print("- example_chat_with_paper(token, paper_id)")
        print("- example_get_chat_sessions(token)")
        print("- example_get_chat_history(token, session_id)")
        
    print("\n📚 For more details, check the API documentation at:")
    print("http://localhost:8000/docs")
    
    print("\n🎯 RAG Chat Endpoints:")
    print("- POST /chat/{paper_id} - Chat with a paper")
    print("- GET /chat/sessions - Get user's chat sessions")
    print("- GET /chat/sessions/{session_id}/history - Get chat history")
    print("- DELETE /chat/sessions/{session_id} - Deactivate session")