"""
Migration script to add status column to users table.
Run this once to add the column to existing database.
"""

from sqlalchemy import text
from app.core.database import engine

def add_status_column():
    """Add status column to users table if it doesn't exist."""
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='status'
                )
            """)
        )
        column_exists = result.scalar()
        
        if not column_exists:
            print("Adding status column to users table...")
            conn.execute(
                text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active' NOT NULL")
            )
            conn.commit()
            print("✓ Status column added successfully")
        else:
            print("✓ Status column already exists")

if __name__ == "__main__":
    add_status_column()
