# Research Paper Management System - Milestones 1 & 2

This project implements Milestones 1 & 2 of the Research Paper Management System with user authentication, profile management, paper upload/download, and feedback system.

## Features Implemented

### Milestone 1: User Authentication and Profile Management

#### 1.1 Secure User Authentication
- ✅ User Registration with password complexity validation
- ✅ User Login with JWT tokens (1-hour expiry)
- ✅ Daily points system (10 points every 24 hours on login)
- ✅ Forgot Password functionality
- ✅ Password Reset functionality
- ✅ Logout with token invalidation

#### 1.2 User Profile Management
- ✅ Get user profile with role-based data
- ✅ Update user profile
- ✅ Get points balance
- ✅ Get transaction history

#### 1.3 User Roles and Permissions
- ✅ Member, Researcher, Admin roles
- ✅ Role-based access control
- ✅ JWT contains user role information

#### 1.4 Admin Role Management
- ✅ List users with pagination
- ✅ Get any user's profile
- ✅ Update user roles
- ✅ Add points to users

### Milestone 2: Upload, Download & Feedback Points

#### 2.1 Paper Upload (Researcher/Admin only)
- ✅ Secure file upload with validation (PDF only, 50MB max)
- ✅ Comprehensive metadata collection (title, authors, publication date, journal, abstract, keywords, citations, license)
- ✅ Author validation (must be active users in system)
- ✅ Publication date validation (cannot be future date)
- ✅ Admin uploads marked as "official"
- ✅ Researcher uploads reward all authors with 100 points each
- ✅ Separate storage for official vs researcher papers

#### 2.2 Feedback System
- ✅ Any authenticated user can provide feedback
- ✅ 5 points awarded for feedback (except admins)
- ✅ Prevents duplicate feedback from same user
- ✅ Rating system (1-5 stars)
- ✅ Feedback categorization (general, peer_review, etc.)

#### 2.3 Paper Download System
- ✅ Download costs 10 Hasher Points (except for admins)
- ✅ Balance check before download (402 error if insufficient funds)
- ✅ Two-step download process (authorize + download file)
- ✅ Download count tracking
- ✅ Secure file serving

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure PostgreSQL:**
   - Update the `DATABASE_URL` in `database.py` with your actual PostgreSQL connection string
   - Default dummy URL: `postgresql://dummy_user:dummy_password@localhost:5432/dummy_database`

3. **Run the application:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/forgot-password` - Initiate password reset
- `POST /auth/reset-password` - Reset password
- `POST /auth/logout` - Logout user

### User Profile
- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user profile
- `GET /users/{user_id}/points` - Get points balance
- `GET /user/points-usage/{user_id}` - Get transaction history

### Admin
- `GET /admin/users` - List all users (paginated)
- `GET /admin/users/{user_id}` - Get any user's profile
- `PUT /admin/users/{user_id}` - Update user role
- `PUT /admin/add-points-to-user/{user_id}` - Add points to user

### Research Papers (Milestone 2)
- `POST /papers/upload` - Upload research paper (Researcher/Admin only)
- `GET /papers` - List all papers with pagination
- `GET /papers/{paper_id}` - Get paper details
- `POST /papers/download/{paper_id}` - Authorize paper download (costs 10 points)
- `GET /papers/download-file/{paper_id}` - Download paper file

### Feedback System (Milestone 2)
- `PUT /papers/feedback/{paper_id}/{user_id}` - Add feedback to paper (+5 points)
- `GET /papers/{paper_id}/feedback` - Get all feedback for a paper

## File Structure

- `main.py` - FastAPI application with all endpoints
- `models.py` - SQLAlchemy database models
- `schemas.py` - Pydantic models for request/response
- `auth.py` - Authentication utilities (JWT, password hashing)
- `dependencies.py` - FastAPI dependencies for auth/authorization
- `database.py` - Database configuration
- `file_utils.py` - File upload utilities and validation (Milestone 2)
- `openai_wrapper.py` - OpenAI API wrapper (as provided)
- `requirements.txt` - Python dependencies
- `example_usage.py` - Example API usage (Milestone 1)
- `milestone2_examples.py` - Example API usage (Milestone 2)
- `check_server.py` - Server health check utility

## Security Features

- Password complexity validation (8+ chars, uppercase, lowercase, digit, special char)
- JWT token authentication with 1-hour expiry
- Token invalidation on logout
- Role-based access control
- Password reset with secure tokens
- Daily points system with 24-hour cooldown

## User Roles

- **Member**: Can download papers, provide feedback, interact with LLM
- **Researcher**: Can upload docs, provide feedback, get points, access docs, interact with LLM
- **Admin**: Access to all features, no reward points, can manage users and add points

## File Storage (Milestone 2)

The system automatically creates upload directories:
- `uploads/official/` - Papers uploaded by admins
- `uploads/researcher/` - Papers uploaded by researchers

**File Upload Specifications:**
- **Supported format:** PDF only
- **Maximum size:** 50MB
- **Validation:** File type and size validation
- **Security:** Unique filename generation to prevent conflicts

## Points System

**Earning Points:**
- Daily login bonus: +10 points (once every 24 hours)
- Paper upload (researcher): +100 points per author
- Providing feedback: +5 points

**Spending Points:**
- Download paper: -10 points

**Admin Privileges:**
- Admins don't earn or spend points
- Admins have unlimited access to all features

## OpenAI Integration

The `openai_wrapper.py` file contains the provided OpenAI API wrapper that uses DNA tokens. Update the `DNA_TOKEN` variable with your actual token before using LLM features.

## Testing the System

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Check server status:**
   ```bash
   python check_server.py
   ```

3. **Run Milestone 1 examples:**
   ```bash
   python example_usage.py
   ```

4. **Run Milestone 2 examples:**
   ```bash
   python milestone2_examples.py
   ```

5. **Access API documentation:**
   - Visit: http://localhost:8000/docs

---

## 📁 **Complete Code Explanation**

### **File Structure Overview**

```
weekend-assign/
├── main.py                    # 🚀 Main FastAPI application
├── models.py                  # 🗃️ Database models (SQLAlchemy)
├── schemas.py                 # 📋 Request/Response models (Pydantic)
├── auth.py                    # 🔐 Authentication utilities
├── dependencies.py            # 🔗 FastAPI dependencies
├── database.py                # 💾 Database configuration
├── file_utils.py              # 📁 File upload utilities
├── openai_wrapper.py          # 🤖 OpenAI API wrapper
├── requirements.txt           # 📦 Python dependencies
├── example_usage.py           # 📖 Milestone 1 examples
├── milestone2_examples.py     # 📖 Milestone 2 examples
├── check_server.py            # 🏥 Health check utility
├── test_all_functionality.py  # 🧪 Comprehensive tests
├── reset_database.py          # 🔄 Database reset utility
└── README.md                  # 📚 Documentation
```

---

## 🗃️ **1. models.py - Database Models**

**🎯 Purpose:** Defines all database tables using SQLAlchemy ORM

### **Database Schema:**

#### **UserRole Enum**
```python
class UserRole(enum.Enum):
    MEMBER = "Member"        # Can download papers, give feedback
    RESEARCHER = "Researcher" # Can upload papers, earn points
    ADMIN = "Admin"          # Full access, no points system
```

#### **User Model (Main user table)**
**Core Features:**
- **Authentication:** `username`, `email`, `hashed_password`
- **Profile:** `first_name`, `last_name`, `interests`
- **Points System:** `hasher_points`, `last_points_credited`
- **Security:** `password_reset_token`, `is_active`
- **Relationships:** Links to transactions, papers, feedback

#### **PointTransaction Model (Transaction logging)**
**Purpose:** Complete audit trail for points system
- **Purpose:** What the points were for ("login", "feedback", "download")
- **Amounts:** `credited` (earned) vs `debited` (spent)
- **Balance:** Current balance after transaction
- **Timestamp:** When transaction occurred

#### **ResearchPaper Model (Paper metadata and files)**
**Features:**
- **Metadata:** `title`, `authors` (JSON), `publication_date`, `journal`
- **Content:** `abstract`, `keywords`, `citations`, `license`
- **File Info:** `file_path`, `file_name`, `file_size`
- **Classification:** `is_official` (admin upload vs researcher)
- **Analytics:** `download_count`, `upload_date`

#### **Feedback Model (User reviews)**
**Components:**
- **Content:** Text feedback and 1-5 star rating
- **Categorization:** `feedback_type` (general, peer_review, etc.)
- **Quality Control:** `is_helpful` flag
- **Timestamps:** Creation and update tracking

#### **InvalidatedToken Model (Security for logout)**
- Stores JWT tokens that have been invalidated
- Prevents token reuse after logout

---

## 💾 **2. database.py - Database Configuration**

**🎯 Purpose:** Manages database connectivity and session handling

### **Connection Setup**
```python
DATABASE_URL = "postgresql://dummy_user:dummy_password@localhost:5432/dummy_database"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Components:**
- **DATABASE_URL:** Connection string format: `postgresql://user:password@host:port/database`
- **engine:** Creates connection pool to PostgreSQL
- **SessionLocal:** Factory for database sessions with transaction control

### **Dependency Injection**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db      # Provides session to FastAPI endpoints
    finally:
        db.close()    # Always closes session (even if error)
```

**Usage in endpoints:**
```python
@app.get("/users")
def get_users(db: Session = Depends(get_db)):  # ← Automatic injection
    return db.query(User).all()                # ← Use database
```

### **Table Creation**
```python
def create_tables():
    Base.metadata.create_all(bind=engine)
```
- **Reads all models** from `models.py`
- **Creates tables** that don't exist
- **Safe to run multiple times**

---

## 🔐 **3. auth.py - Authentication System**

**🎯 Purpose:** Handles all authentication, JWT tokens, password security, and points logic

### **Security Configuration**
```python
SECRET_KEY = "your-secret-key-here-change-in-production"  # ⚠️ Change in production!
ALGORITHM = "HS256"                                       # JWT encoding
ACCESS_TOKEN_EXPIRE_HOURS = 1                            # Token expiration
pwd_context = CryptContext(schemes=["bcrypt"])           # Password hashing
```

### **Password Security**
```python
def validate_password_complexity(password: str) -> bool:
    # Requires: 8+ chars, uppercase, lowercase, digit, special char
```

**Password requirements:**
- ✅ Minimum 8 characters
- ✅ At least 1 uppercase letter
- ✅ At least 1 lowercase letter  
- ✅ At least 1 digit
- ✅ At least 1 special character

### **JWT Token System**
```python
def create_access_token(data: dict) -> str:
    # Creates JWT with user ID and role
    to_encode.update({"exp": expire})  # Auto-expiration
```

**Token contents:**
```json
{
  "sub": "user_id",
  "role": "Researcher", 
  "exp": 1705123456
}
```

### **Password Reset**
- `create_password_reset_token()` - Creates 24-hour reset token
- `verify_password_reset_token()` - Validates reset token and returns email

### **Daily Points Logic**
```python
def check_daily_points_eligibility(user_last_login, user_last_points_credited) -> bool:
    # Returns True if 24 hours passed since last credit
    return time_since_last_credit.total_seconds() >= 24 * 60 * 60
```

---

## 🔗 **4. dependencies.py - Access Control System**

**🎯 Purpose:** FastAPI dependencies for authentication and authorization

### **Core Authentication Flow**
```python
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
```

**Authentication Process:**
1. **Extract JWT token** from `Authorization: Bearer TOKEN`
2. **Check invalidated tokens** (logout protection)
3. **Verify JWT signature** and expiration
4. **Load user from database** 
5. **Validate user is active**

### **Access Control Layers**

**🔒 Basic Protection:**
```python
@app.get("/profile")
def get_profile(user: User = Depends(get_current_active_user)):
    # Only authenticated, active users
```

**🛡️ Admin Only:**
```python
@app.get("/admin/users") 
def list_users(admin: User = Depends(require_admin)):
    # Only admin role
```

**🎓 Researcher/Admin Only:**
```python
@app.post("/papers/upload")
def upload_paper(user: User = Depends(require_researcher_or_admin)):
    # Only researchers and admins can upload
```

**👤 Self/Admin Access:**
```python
@app.get("/users/{user_id}")
def get_user(user_id: int, user: User = Depends(check_user_access)):
    # Users can only access their own data (admins can access anyone's)
```

### **Security Features:**
- ✅ **Token Invalidation:** Checks logout tokens
- ✅ **Account Status:** Validates active users only
- ✅ **Role Hierarchy:** Admin > Researcher > Member
- ✅ **Privacy Protection:** Users can't access others' data

---

## 📋 **5. schemas.py - Data Validation**

**🎯 Purpose:** Pydantic models for data validation, serialization, and API documentation

### **Model Categories:**

**User Management:**
- `UserRegister` - New user signup data
- `UserLogin` - Login credentials  
- `UserResponse` - User profile output
- `UserUpdate` - Profile modification
- `UserRoleUpdate` - Admin role changes

**Authentication:**
- `Token` - JWT token response
- `ForgotPassword` - Password reset request
- `ResetPassword` - Password reset confirmation

**Points System:**
- `PointsBalance` - Current points balance
- `PointTransaction` - Transaction history
- `AddPointsRequest` - Admin point addition

**Paper Management:**
- `PaperUpload` - Paper upload form data
- `ResearchPaperResponse` - Paper details output
- `PaperDownloadResponse` - Download authorization

**Feedback System:**
- `FeedbackCreate` - New feedback input
- `FeedbackResponse` - Feedback details output  
- `FeedbackCreateResponse` - Feedback creation result

### **Key Validation Examples:**

**Password Complexity:**
```python
@validator('username')
def username_must_be_valid(cls, v):
    if len(v) < 3 or len(v) > 50:
        raise ValueError('Username must be between 3 and 50 characters')
```

**Future Date Prevention:**
```python
@validator('publication_date')
def publication_date_not_future(cls, v):
    if v > datetime.now():
        raise ValueError('Publication date cannot be in the future')
```

**Points Validation:**
```python
@validator('points')
def points_must_be_positive(cls, v):
    if v <= 0:
        raise ValueError('Points must be positive')
```

---

## 📁 **6. file_utils.py - File Management System**

**🎯 Purpose:** Handles PDF uploads, validation, and storage for research papers

### **Directory Structure**
```python
OFFICIAL_DIR = "uploads/official"      # Admin uploads
RESEARCHER_DIR = "uploads/researcher"  # Researcher uploads
MAX_FILE_SIZE = 50 * 1024 * 1024      # 50MB limit
ALLOWED_EXTENSIONS = {".pdf"}          # PDF only
```

**Auto-created folders:**
```
uploads/
├── official/     # Admin papers (official publications)
└── researcher/   # User-contributed papers
```

### **Security Features**

**File Type Validation:**
```python
def validate_file(file: UploadFile) -> None:
    # Only .pdf files allowed
    # Size limit enforced
```

**Unique Filename Generation:**
```python
def generate_unique_filename(original_filename: str) -> str:
    # Uses UUID to prevent filename conflicts
    return f"{uuid.uuid4()}.pdf"
```

### **Async Upload Process**

**save_uploaded_file() function:**
1. **Validates** file type and size
2. **Creates** directory structure
3. **Generates** unique filename
4. **Streams** file in 8KB chunks (memory efficient)
5. **Monitors** size during upload
6. **Cleans up** if upload fails

**Returns:** `(file_path, filename, file_size)`

### **Safety Mechanisms:**
- ✅ **Type filtering:** PDF only
- ✅ **Size limits:** 50MB maximum
- ✅ **Conflict prevention:** UUID filenames
- ✅ **Memory efficiency:** Chunked uploads
- ✅ **Error cleanup:** Removes partial files
- ✅ **Path separation:** Admin vs researcher storage

---

## 🚀 **7. main.py - The Main Application (750 lines)**

**🎯 Purpose:** Main application orchestrating all features for Milestones 1 & 2

### **Application Setup**

**Imports & Dependencies:**
```python
from fastapi import FastAPI, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse  # For file downloads
```

**App Initialization:**
```python
app = FastAPI(title="Research Paper Management System", version="1.0.0")

@app.on_event("startup")
def startup_event():
    create_tables()              # Create database tables
    create_upload_directories()  # Create file storage folders
```

### **API Endpoint Categories**

**🔐 Authentication Endpoints (Milestone 1):**
- `POST /auth/register` - User registration with validation
- `POST /auth/login` - Login with daily points bonus
- `POST /auth/forgot-password` - Password reset initiation
- `POST /auth/reset-password` - Password reset completion
- `POST /auth/logout` - Token invalidation

**👤 Profile Management (Milestone 1):**
- `GET /users/{user_id}` - Get user profile + contributions
- `PUT /users/{user_id}` - Update profile information
- `GET /users/{user_id}/points` - Check points balance
- `GET /user/points-usage/{user_id}` - Transaction history

**⚙️ Admin Functions (Milestone 1):**
- `GET /admin/users` - List all users (paginated)
- `GET /admin/users/{user_id}` - Get any user's profile
- `PUT /admin/users/{user_id}` - Change user roles
- `PUT /admin/add-points-to-user/{user_id}` - Award points

**📄 Paper Management (Milestone 2):**
- `POST /papers/upload` - Upload research papers (Researcher/Admin)
- `GET /papers` - List papers with pagination
- `GET /papers/{paper_id}` - Paper details and metadata
- `POST /papers/download/{paper_id}` - Authorize download (-10 points)
- `GET /papers/download-file/{paper_id}` - Actual file download

**💬 Feedback System (Milestone 2):**
- `PUT /papers/feedback/{paper_id}/{user_id}` - Add feedback (+5 points)
- `GET /papers/{paper_id}/feedback` - View all paper feedback

### **Key Application Features:**

**Points Economy Integration:**
```python
# Login bonus (daily)
if check_daily_points_eligibility(user.last_login, user.last_points_credited):
    user.hasher_points += 10.0
    # Log transaction...

# Upload rewards (per author)
author.hasher_points += 100.0

# Download costs
if current_user.hasher_points < download_cost:
    raise HTTPException(status_code=402, detail="Insufficient points")
```

**Role-Based Security:**
```python
@app.post("/papers/upload")
async def upload_paper(current_user: User = Depends(require_researcher_or_admin)):
    # Only researchers and admins can upload

@app.get("/admin/users")  
def list_users(current_user: User = Depends(require_admin)):
    # Admin-only functionality
```

**File Upload Processing:**
```python
# Validate authors exist
for author_id in authors_list:
    author = db.query(User).filter(User.id == author_id, User.is_active == True).first()
    if not author:
        raise HTTPException(400, detail=f"Author {author_id} not found")

# Save file with security
file_path, filename, file_size = await save_uploaded_file(file, is_official=is_official)
```

---

## 🤖 **8. openai_wrapper.py - LLM Integration**

**🎯 Purpose:** Custom wrapper for OpenAI GPT-4 API using DNA token authentication

### **Authentication Setup**
```python
DNA_TOKEN = ""  # Your custom DNA token goes here
OPENAI_API_WRAPPER = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"

OPENAI_API_HEADERS = {
    'x-api-token': DNA_TOKEN,           # Custom token auth
    'Content-Type': 'application/json',
    'Cookie': 'csrftoken=...'          # CSRF protection
}
```

### **GPT-4 Configuration**
```python
def get_request_payload(systemprompt, userprompt):
    payload = {
        "messages": [
            {"role": "system", "content": systemprompt},    # AI behavior
            {"role": "user", "content": userprompt}         # User request
        ],
        "max_tokens": "2000",   # Response length limit
        "model": "gpt-4",       # GPT-4 model
        "temperature": "0",     # Deterministic responses
        "top_p": "1"           # Sampling parameter
    }
```

### **Usage Example (Built-in)**
**Meeting Minutes Generator:**
- **System Prompt:** Defines AI as meeting secretary
- **User Prompt:** Provides meeting transcript
- **Output:** Structured meeting minutes with participants, key points, next steps

### **Integration Potential**

**For Research Paper System:**
```python
# Paper Analysis
systemprompt = "You analyze research papers for key insights..."
userprompt = f"Analyze this paper: {paper_abstract}"

# Feedback Enhancement  
systemprompt = "You help improve research paper feedback..."
userprompt = f"Enhance this feedback: {user_feedback}"

# Paper Summarization
systemprompt = "You create concise summaries of research papers..."
userprompt = f"Summarize: {paper_content}"
```

---

## 📦 **9. requirements.txt - Dependencies**

**🎯 Purpose:** Lists all Python packages needed for the system

### **Dependencies Breakdown:**

**🌐 Web Framework & Server:**
```
fastapi==0.104.1           # Main web framework with auto-docs
uvicorn[standard]==0.24.0  # ASGI server with WebSocket support
```

**🗃️ Database & ORM:**
```
sqlalchemy==2.0.23         # Object-Relational Mapping (ORM)
psycopg2-binary==2.9.9     # PostgreSQL database adapter
```

**🔐 Security & Authentication:**
```
python-jose[cryptography]==3.3.0  # JWT token encoding/decoding
passlib[bcrypt]==1.7.4            # Password hashing with bcrypt
```

**📁 File Handling & Validation:**
```
python-multipart==0.0.6    # File upload support for FastAPI
aiofiles==23.2.0           # Async file operations (Milestone 2)
email-validator==2.1.0     # Email format validation
pydantic[email]==2.5.0     # Data validation with email support
```

**🌍 External Integrations:**
```
requests==2.31.0           # HTTP client for OpenAI wrapper
python-json-logger==2.0.7  # Structured logging
```

### **Installation:**
```bash
pip install -r requirements.txt
```

### **Feature Mapping:**
- **Milestone 1:** `fastapi`, `sqlalchemy`, `psycopg2-binary`, `python-jose`, `passlib`, `email-validator`, `pydantic`
- **Milestone 2:** Added `python-multipart`, `aiofiles`
- **OpenAI Integration:** `requests`
- **Production:** `uvicorn`, `python-json-logger`

---

## 🧪 **10. Utility & Testing Files**

### **check_server.py - Health Monitor**
**Purpose:** Quick server status verification
```python
# Tests /health endpoint
# Provides clear success/failure status
# Includes troubleshooting suggestions
```

### **test_all_functionality.py - Comprehensive Testing**
**Purpose:** Automated testing for all features
- ✅ Tests 8 core functionalities
- ✅ Milestone 1 & 2 coverage
- ✅ Automated pass/fail reporting

### **example_usage.py - Milestone 1 Examples**
**Purpose:** Working code examples for authentication & profiles

### **milestone2_examples.py - Milestone 2 Examples**  
**Purpose:** Working code examples for papers & feedback

### **reset_database.py - Database Management**
**Purpose:** Safe database schema reset for migrations
- ⚠️ Drops all tables
- ✅ Recreates with correct schema
- 🔒 Requires user confirmation

---

## 🔗 **How All Files Work Together**

```mermaid
graph TD
    A[main.py<br/>FastAPI App] --> B[models.py<br/>Database Schema]
    A --> C[schemas.py<br/>Data Validation]
    A --> D[auth.py<br/>Security]
    A --> E[dependencies.py<br/>Access Control]
    A --> F[file_utils.py<br/>File Management]
    
    B --> G[database.py<br/>DB Connection]
    D --> E
    
    H[openai_wrapper.py<br/>LLM Integration] -.-> A
    
    I[requirements.txt<br/>Dependencies] --> A
    
    J[Test Files] --> A
    K[Example Files] --> A
    L[Utility Files] --> A
```

### **Request Flow:**
1. **Request arrives** at `main.py` endpoint
2. **Dependencies** (`dependencies.py`) validate authentication
3. **Auth utils** (`auth.py`) verify JWT tokens
4. **Database** (`database.py`) provides session
5. **Models** (`models.py`) define data structure
6. **Schemas** (`schemas.py`) validate input/output
7. **File utils** (`file_utils.py`) handle uploads (Milestone 2)
8. **Response** sent back to client

### **Result:** 
A complete, production-ready research paper management system with user authentication, role-based access control, points economy, file management, and feedback system!