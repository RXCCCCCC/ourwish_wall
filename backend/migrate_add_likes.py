"""
Add likes column to comments table and create comment_likes table
"""
from sqlalchemy import text
from models import db
from app import create_app

def migrate():
    app = create_app()
    
    with app.app_context():
        # Add likes column to comments table
        try:
            with db.engine.connect() as conn:
                # Check if column exists
                result = conn.execute(text(
                    "SELECT COUNT(*) as count FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() "
                    "AND TABLE_NAME = 'comments' "
                    "AND COLUMN_NAME = 'likes'"
                ))
                exists = result.fetchone()[0] > 0
                
                if not exists:
                    print("Adding 'likes' column to comments table...")
                    conn.execute(text('ALTER TABLE comments ADD COLUMN likes INT DEFAULT 0 NOT NULL'))
                    conn.commit()
                    print("✓ Column 'likes' added successfully")
                else:
                    print("✓ Column 'likes' already exists")
        except Exception as e:
            print(f"Error adding likes column: {e}")
            return False
        
        # Create comment_likes table if not exists
        try:
            print("Creating comment_likes table...")
            db.create_all()
            print("✓ Tables created/verified successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
        
        print("\n✅ Migration completed successfully!")
        return True

if __name__ == '__main__':
    migrate()
