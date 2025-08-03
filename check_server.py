"""
Quick script to check if the FastAPI server is running
"""
import requests
import sys

def check_server():
    """Check if the FastAPI server is running"""
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is RUNNING!")
            print(f"   Status: {data.get('status')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            print("   API Docs: http://localhost:8000/docs")
            return True
        else:
            print(f"❌ Server responding but with error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is NOT running or not accessible")
        print("   Make sure you've run: python main.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Server is not responding (timeout)")
        return False
        
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("Checking FastAPI server status...")
    print("-" * 40)
    
    is_running = check_server()
    
    if not is_running:
        print("\n💡 To start the server:")
        print("   python main.py")
        print("   or")
        print("   uvicorn main:app --reload")
        
    sys.exit(0 if is_running else 1)