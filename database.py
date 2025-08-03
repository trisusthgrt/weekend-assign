from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Dummy PostgreSQL URL - replace with actual database URL
DATABASE_URL = "postgresql://dummy_user:dummy_password@localhost:5432/dummy_database"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)