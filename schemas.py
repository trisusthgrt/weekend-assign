from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from models import UserRole

# User schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    interests: Optional[str] = None

    @validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    interests: Optional[str]
    hasher_points: float
    role: UserRole
    last_login: Optional[datetime]
    created_at: datetime
    research_papers: Optional[List['ResearchPaperResponse']] = []
    feedback_given: Optional[List['FeedbackResponse']] = []

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    interests: Optional[str] = None

class UserRoleUpdate(BaseModel):
    role: UserRole

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

# Points schemas
class PointsBalance(BaseModel):
    hasher_points: float

class PointTransaction(BaseModel):
    id: int
    purpose: str
    credited: float
    debited: float
    balance_points: float
    timestamp: datetime

    class Config:
        from_attributes = True

class AddPointsRequest(BaseModel):
    points: float

    @validator('points')
    def points_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Points must be positive')
        return v

# Admin schemas
class UserList(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

# Research Paper schemas
class PaperUpload(BaseModel):
    title: str
    authors: List[int]  # List of user IDs who are authors
    publication_date: datetime
    journal: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    citations: Optional[str] = None
    license: Optional[str] = None

    @validator('title')
    def title_must_be_valid(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters')
        return v.strip()

    @validator('publication_date')
    def publication_date_not_future(cls, v):
        if v > datetime.now():
            raise ValueError('Publication date cannot be in the future')
        return v

    @validator('authors')
    def authors_must_not_be_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one author is required')
        return v

class ResearchPaperResponse(BaseModel):
    id: int
    title: str
    authors: str  # JSON string of author IDs
    publication_date: datetime
    journal: Optional[str]
    abstract: Optional[str]
    keywords: Optional[str]
    citations: Optional[str]
    license: Optional[str]
    uploader_id: int
    file_name: Optional[str]
    file_size: Optional[int]
    is_official: bool
    upload_date: datetime
    download_count: int

    class Config:
        from_attributes = True

class PaperDownloadResponse(BaseModel):
    message: str
    file_path: str
    points_deducted: float
    remaining_points: float

# Feedback schemas
class FeedbackCreate(BaseModel):
    content: str
    rating: Optional[int] = None
    feedback_type: Optional[str] = "general"

    @validator('content')
    def content_must_be_valid(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Feedback must be at least 10 characters')
        return v.strip()

    @validator('rating')
    def rating_must_be_valid(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v

class FeedbackResponse(BaseModel):
    id: int
    paper_id: int
    reviewer_id: int
    content: str
    rating: Optional[int]
    feedback_type: str
    is_helpful: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FeedbackCreateResponse(BaseModel):
    message: str
    feedback: FeedbackResponse
    points_awarded: float
    new_balance: float

# Update forward references
UserResponse.model_rebuild()