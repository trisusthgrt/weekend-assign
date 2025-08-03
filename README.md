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