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

# Research Paper schemas (for profile response)
class ResearchPaperResponse(BaseModel):
    id: int
    title: str
    upload_date: datetime

    class Config:
        from_attributes = True

# Feedback schemas (for profile response)
class FeedbackResponse(BaseModel):
    id: int
    paper_id: int
    content: str
    rating: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# Update forward references
UserResponse.model_rebuild()