# Research Paper Management System - Milestone 1

This project implements Milestone 1 of the Research Paper Management System with user authentication and profile management.

## Features Implemented

### 1.1 Secure User Authentication
- ✅ User Registration with password complexity validation
- ✅ User Login with JWT tokens (1-hour expiry)
- ✅ Daily points system (10 points every 24 hours on login)
- ✅ Forgot Password functionality
- ✅ Password Reset functionality
- ✅ Logout with token invalidation

### 1.2 User Profile Management
- ✅ Get user profile with role-based data
- ✅ Update user profile
- ✅ Get points balance
- ✅ Get transaction history

### 1.3 User Roles and Permissions
- ✅ Member, Researcher, Admin roles
- ✅ Role-based access control
- ✅ JWT contains user role information

### 1.4 Admin Role Management
- ✅ List users with pagination
- ✅ Get any user's profile
- ✅ Update user roles
- ✅ Add points to users

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

## File Structure

- `main.py` - FastAPI application with all endpoints
- `models.py` - SQLAlchemy database models
- `schemas.py` - Pydantic models for request/response
- `auth.py` - Authentication utilities (JWT, password hashing)
- `dependencies.py` - FastAPI dependencies for auth/authorization
- `database.py` - Database configuration
- `openai_wrapper.py` - OpenAI API wrapper (as provided)
- `requirements.txt` - Python dependencies

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

## OpenAI Integration

The `openai_wrapper.py` file contains the provided OpenAI API wrapper that uses DNA tokens. Update the `DNA_TOKEN` variable with your actual token before using LLM features.