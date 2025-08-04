from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    MEMBER = "Member"
    RESEARCHER = "Researcher"
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    interests = Column(Text)
    hasher_points = Column(Float, default=0.0)
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    last_points_credited = Column(DateTime)
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    point_transactions = relationship("PointTransaction", back_populates="user")
    uploaded_papers = relationship("ResearchPaper", back_populates="uploader")
    feedback_given = relationship("Feedback", foreign_keys="Feedback.reviewer_id", back_populates="reviewer")

class PointTransaction(Base):
    __tablename__ = "point_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    purpose = Column(String(255), nullable=False)
    credited = Column(Float, default=0.0)
    debited = Column(Float, default=0.0)
    balance_points = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="point_transactions")

class ResearchPaper(Base):
    __tablename__ = "research_papers"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=False)  # JSON string of author user IDs
    publication_date = Column(DateTime, nullable=False)
    journal = Column(String(255))
    abstract = Column(Text)
    keywords = Column(Text)  # Comma-separated keywords
    citations = Column(Text)
    license = Column(String(100))
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)  # Size in bytes
    is_official = Column(Boolean, default=False)  # True if uploaded by admin
    upload_date = Column(DateTime, default=func.now())
    download_count = Column(Integer, default=0)
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_papers")
    feedback = relationship("Feedback", back_populates="paper")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer)  # 1-5 rating
    feedback_type = Column(String(50), default="general")  # general, peer_review, etc.
    is_helpful = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    paper = relationship("ResearchPaper", back_populates="feedback")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="feedback_given")

class InvalidatedToken(Base):
    __tablename__ = "invalidated_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, nullable=False)
    invalidated_at = Column(DateTime, default=func.now())

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)  # UUID for session
    is_active = Column(Boolean, default=True)
    chunks_processed = Column(Boolean, default=False)  # If paper has been chunked
    created_at = Column(DateTime, default=func.now())
    last_interaction = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")
    paper = relationship("ResearchPaper")
    messages = relationship("ChatMessage", back_populates="session")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    content = Column(Text, nullable=False)  # Actual text content
    embedding = Column(Text)  # JSON string of embedding vector
    chunk_size = Column(Integer)  # Size of chunk in characters
    overlap_size = Column(Integer, default=0)  # Overlap with adjacent chunks
    metadata = Column(Text)  # JSON string for additional metadata
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    paper = relationship("ResearchPaper")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    relevant_chunks = Column(Text)  # JSON string of chunk IDs used for response
    points_cost = Column(Float, default=0.0)  # Points deducted for this message
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")