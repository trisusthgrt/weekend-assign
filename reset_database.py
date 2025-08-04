"""
Database reset script for Milestone 2 schema update
Run this script to reset your database with the correct schema
"""

import sys
from sqlalchemy import create_engine, text
from database import DATABASE_URL, create_tables
from models import Base

def reset_database():
    """Reset database with correct schema for Milestone 2"""
    
    print("🔄 Resetting database for Milestone 2...")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Drop all tables
        print("📥 Dropping existing tables...")
        with engine.connect() as conn:
            # Drop tables in correct order (foreign keys first)
            tables_to_drop = [
                'invalidated_tokens',
                'feedback', 
                'research_papers',
                'point_transactions',
                'users'
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"  ✅ Dropped table: {table}")
                except Exception as e:
                    print(f"  ⚠️ Could not drop {table}: {e}")
            
            conn.commit()
        
        # Create tables with new schema
        print("🏗️ Creating tables with new schema...")
        create_tables()
        print("  ✅ All tables created successfully")
        
        print("\n🎉 Database reset complete!")
        print("✅ Your database now has the correct Milestone 2 schema")
        print("🚀 You can now run: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        print("\n💡 Manual steps:")
        print("1. Connect to your PostgreSQL database")
        print("2. Drop all tables manually")
        print("3. Restart the server to recreate tables")
        return False

def check_database_connection():
    """Test database connection"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Check your DATABASE_URL in database.py")
        return False

if __name__ == "__main__":
    print("🔧 DATABASE RESET TOOL")
    print("=" * 50)
    
    # Check connection first
    if not check_database_connection():
        sys.exit(1)
    
    # Confirm reset
    response = input("\n⚠️ This will DELETE ALL DATA in your database. Continue? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = reset_database()
        sys.exit(0 if success else 1)
    else:
        print("❌ Database reset cancelled")
        sys.exit(0)