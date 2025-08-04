from fastapi import FastAPI, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Optional
import secrets
import json

from database import get_db, create_tables
from models import User, UserRole, PointTransaction, InvalidatedToken, ResearchPaper, Feedback
from schemas import (
    UserRegister, UserLogin, UserResponse, UserUpdate, UserRoleUpdate,
    Token, ForgotPassword, ResetPassword, PointsBalance, PointTransaction as PointTransactionSchema,
    AddPointsRequest, UserList, PaperUpload, ResearchPaperResponse, PaperDownloadResponse,
    FeedbackCreate, FeedbackResponse, FeedbackCreateResponse
)
from auth import (
    verify_password, get_password_hash, validate_password_complexity,
    create_access_token, verify_token, create_password_reset_token,
    verify_password_reset_token, check_daily_points_eligibility
)
from dependencies import (
    get_current_user, get_current_active_user, require_admin,
    require_researcher_or_admin, check_user_access, security
)
from file_utils import save_uploaded_file, ensure_file_exists, create_upload_directories

app = FastAPI(title="Research Paper Management System", version="1.0.0")

# Create tables and directories on startup
@app.on_event("startup")
def startup_event():
    create_tables()
    create_upload_directories()

# 1.1 Secure User Authentication

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    
    # Validate password complexity
    if not validate_password_complexity(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        interests=user_data.interests,
        hasher_points=0.0,
        role=UserRole.MEMBER,
        last_points_credited=None
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    
    # Find user by username
    user = db.query(User).filter(User.username == user_credentials.username).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Check if user is eligible for daily points (24 hours since last credit)
    current_time = datetime.utcnow()
    if check_daily_points_eligibility(user.last_login, user.last_points_credited):
        # Credit 10 points
        user.hasher_points += 10.0
        user.last_points_credited = current_time
        
        # Create point transaction record
        transaction = PointTransaction(
            user_id=user.id,
            purpose="Daily login bonus",
            credited=10.0,
            debited=0.0,
            balance_points=user.hasher_points
        )
        db.add(transaction)
    
    # Update last login
    user.last_login = current_time
    db.commit()
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/forgot-password")
def forgot_password(request: ForgotPassword, db: Session = Depends(get_db)):
    """Initiate password reset process."""
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = create_password_reset_token(user.email)
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
    
    db.commit()
    
    # In production, send email with reset link
    # For now, just return success message
    return {"message": "If the email exists, a reset link has been sent"}

@app.post("/auth/reset-password")
def reset_password(request: ResetPassword, db: Session = Depends(get_db)):
    """Reset user password using token."""
    
    # Verify reset token
    email = verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user by email and validate token
    user = db.query(User).filter(
        and_(
            User.email == email,
            User.password_reset_token == request.token,
            User.password_reset_expires > datetime.utcnow()
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate new password
    if not validate_password_complexity(request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    
    db.commit()
    
    return {"message": "Password reset successful"}

@app.post("/auth/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout user by invalidating JWT token."""
    
    token = credentials.credentials
    
    # Add token to invalidated tokens
    invalidated_token = InvalidatedToken(token=token)
    db.add(invalidated_token)
    db.commit()
    
    return {"message": "Successfully logged out"}

# 1.2 User Profile Management

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_profile(
    user_id: int,
    current_user: User = Depends(check_user_access),
    db: Session = Depends(get_db)
):
    """Get user profile data."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If user is researcher, fetch contributions
    if user.role == UserRole.RESEARCHER:
        research_papers = db.query(ResearchPaper).filter(ResearchPaper.uploader_id == user.id).all()
        feedback_given = db.query(Feedback).filter(Feedback.reviewer_id == user.id).all()
        user.uploaded_papers = research_papers
        user.feedback_given = feedback_given
    
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(check_user_access),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.first_name is not None:
        user.first_name = user_update.first_name
    if user_update.last_name is not None:
        user.last_name = user_update.last_name
    if user_update.interests is not None:
        user.interests = user_update.interests
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user

@app.get("/users/{user_id}/points", response_model=PointsBalance)
def get_points_balance(
    user_id: int,
    current_user: User = Depends(check_user_access),
    db: Session = Depends(get_db)
):
    """Get user's Hasher Points balance."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"hasher_points": user.hasher_points}

@app.get("/user/points-usage/{user_id}", response_model=List[PointTransactionSchema])
def get_points_transactions(
    user_id: int,
    current_user: User = Depends(check_user_access),
    db: Session = Depends(get_db)
):
    """Get user's point transaction history."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    transactions = db.query(PointTransaction).filter(
        PointTransaction.user_id == user_id
    ).order_by(PointTransaction.timestamp.desc()).all()
    
    return transactions

# 1.4 Admin Role Management

@app.get("/admin/users", response_model=UserList)
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users with pagination (Admin only)."""
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get users with pagination
    users = db.query(User).offset(offset).limit(per_page).all()
    total_users = db.query(User).count()
    
    return {
        "users": users,
        "total": total_users,
        "page": page,
        "per_page": per_page
    }

@app.get("/admin/users/{user_id}", response_model=UserResponse)
def get_user_profile_admin(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get any user's profile (Admin only)."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If user is researcher, fetch contributions
    if user.role == UserRole.RESEARCHER:
        research_papers = db.query(ResearchPaper).filter(ResearchPaper.uploader_id == user.id).all()
        feedback_given = db.query(Feedback).filter(Feedback.reviewer_id == user.id).all()
        user.uploaded_papers = research_papers
        user.feedback_given = feedback_given
    
    return user

@app.put("/admin/users/{user_id}", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user role (Admin only)."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = role_update.role
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user

@app.put("/admin/add-points-to-user/{user_id}")
def add_points_to_user(
    user_id: int,
    points_request: AddPointsRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Add points to user (Admin only)."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Add points
    user.hasher_points += points_request.points
    
    # Create transaction record
    transaction = PointTransaction(
        user_id=user.id,
        purpose=f"Admin credit by {current_user.username}",
        credited=points_request.points,
        debited=0.0,
        balance_points=user.hasher_points
    )
    
    db.add(transaction)
    db.commit()
    
    return {
        "message": f"Successfully added {points_request.points} points to user {user.username}",
        "new_balance": user.hasher_points
    }

# Milestone 2: Upload, download & feedback points

@app.post("/papers/upload", response_model=ResearchPaperResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile = File(...),
    title: str = Form(...),
    authors: str = Form(...),  # JSON string of author IDs
    publication_date: str = Form(...),
    journal: Optional[str] = Form(None),
    abstract: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),
    citations: Optional[str] = Form(None),
    license: Optional[str] = Form(None),
    current_user: User = Depends(require_researcher_or_admin),
    db: Session = Depends(get_db)
):
    """Upload a research paper (Researcher or Admin only)."""
    
    try:
        # Parse authors JSON
        authors_list = json.loads(authors)
        if not isinstance(authors_list, list) or not authors_list:
            raise ValueError("Authors must be a non-empty list")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authors format. Must be a JSON list of user IDs."
        )
    
    # Parse publication date
    try:
        pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
        if pub_date > datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Publication date cannot be in the future"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid publication date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    # Validate all authors exist and are active
    for author_id in authors_list:
        author = db.query(User).filter(User.id == author_id, User.is_active == True).first()
        if not author:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Author with ID {author_id} not found or inactive"
            )
    
    # Validate title
    if len(title.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be at least 5 characters"
        )
    
    # Save uploaded file
    is_official = current_user.role == UserRole.ADMIN
    try:
        file_path, filename, file_size = await save_uploaded_file(file, is_official=is_official)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Create research paper record
    paper = ResearchPaper(
        title=title.strip(),
        authors=json.dumps(authors_list),
        publication_date=pub_date,
        journal=journal,
        abstract=abstract,
        keywords=keywords,
        citations=citations,
        license=license,
        uploader_id=current_user.id,
        file_path=file_path,
        file_name=filename,
        file_size=file_size,
        is_official=is_official
    )
    
    db.add(paper)
    db.flush()  # Get the paper ID
    
    # Award points to authors (only for researcher uploads, not admin)
    if current_user.role == UserRole.RESEARCHER:
        for author_id in authors_list:
            # Get author
            author = db.query(User).filter(User.id == author_id).first()
            if author and author.role != UserRole.ADMIN:  # Don't award points to admins
                # Award 100 points
                author.hasher_points += 100.0
                
                # Create transaction record
                transaction = PointTransaction(
                    user_id=author.id,
                    purpose="earned",
                    credited=100.0,
                    debited=0.0,
                    balance_points=author.hasher_points
                )
                db.add(transaction)
    
    db.commit()
    db.refresh(paper)
    
    return paper

@app.put("/papers/feedback/{paper_id}/{user_id}", response_model=FeedbackCreateResponse)
def add_feedback(
    paper_id: int,
    user_id: int,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add feedback to a research paper."""
    
    # Check if paper exists
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    # Validate user_id matches current user (or admin can add feedback for others)
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add feedback for yourself"
        )
    
    # Get the target user
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user already provided feedback for this paper
    existing_feedback = db.query(Feedback).filter(
        Feedback.paper_id == paper_id,
        Feedback.reviewer_id == user_id
    ).first()
    
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User has already provided feedback for this paper"
        )
    
    # Create feedback
    feedback = Feedback(
        paper_id=paper_id,
        reviewer_id=user_id,
        content=feedback_data.content,
        rating=feedback_data.rating,
        feedback_type=feedback_data.feedback_type
    )
    
    db.add(feedback)
    db.flush()  # Get the feedback ID
    
    # Award 5 points to the reviewer (only if not admin)
    if target_user.role != UserRole.ADMIN:
        target_user.hasher_points += 5.0
        
        # Create transaction record
        transaction = PointTransaction(
            user_id=target_user.id,
            purpose="feedback",
            credited=5.0,
            debited=0.0,
            balance_points=target_user.hasher_points
        )
        db.add(transaction)
    
    db.commit()
    db.refresh(feedback)
    
    return {
        "message": "Feedback added successfully",
        "feedback": feedback,
        "points_awarded": 5.0 if target_user.role != UserRole.ADMIN else 0.0,
        "new_balance": target_user.hasher_points
    }

@app.post("/papers/download/{paper_id}", response_model=PaperDownloadResponse)
def download_paper(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a research paper (costs 10 Hasher Points)."""
    
    # Check if paper exists
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    # Check if file exists
    if not paper.file_path or not ensure_file_exists(paper.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper file not found on server"
        )
    
    # Check if user has enough points (only charge non-admins)
    download_cost = 10.0
    if current_user.role != UserRole.ADMIN:
        if current_user.hasher_points < download_cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient points. You have {current_user.hasher_points} points, but need {download_cost} points to download."
            )
        
        # Deduct points
        current_user.hasher_points -= download_cost
        
        # Create transaction record
        transaction = PointTransaction(
            user_id=current_user.id,
            purpose="download",
            credited=0.0,
            debited=download_cost,
            balance_points=current_user.hasher_points
        )
        db.add(transaction)
    
    # Increment download count
    paper.download_count += 1
    
    db.commit()
    
    return {
        "message": "Paper download authorized",
        "file_path": paper.file_path,
        "points_deducted": download_cost if current_user.role != UserRole.ADMIN else 0.0,
        "remaining_points": current_user.hasher_points
    }

@app.get("/papers/download-file/{paper_id}")
def download_paper_file(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actually download the paper file (use after /papers/download/{paper_id})."""
    
    # Check if paper exists
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    # Check if file exists
    if not paper.file_path or not ensure_file_exists(paper.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper file not found on server"
        )
    
    # Return file for download
    return FileResponse(
        path=paper.file_path,
        media_type='application/pdf',
        filename=paper.file_name or f"paper_{paper.id}.pdf"
    )

@app.get("/papers", response_model=List[ResearchPaperResponse])
def list_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all research papers with pagination."""
    
    papers = db.query(ResearchPaper).offset(skip).limit(limit).all()
    return papers

@app.get("/papers/{paper_id}", response_model=ResearchPaperResponse)
def get_paper(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific research paper."""
    
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    return paper

@app.get("/papers/{paper_id}/feedback", response_model=List[FeedbackResponse])
def get_paper_feedback(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all feedback for a specific paper."""
    
    # Check if paper exists
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    feedback = db.query(Feedback).filter(Feedback.paper_id == paper_id).all()
    return feedback

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)