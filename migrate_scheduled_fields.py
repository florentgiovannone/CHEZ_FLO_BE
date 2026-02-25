"""
Database migration script to add scheduled fields to menus table
Run this on production to add the new scheduled update fields
"""

from application import app, db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """Add scheduled fields to menus table"""
    with app.app_context():
        try:
            # Add the new columns to the menus table
            logger.info("Starting database migration...")

            migration_sql = """
            ALTER TABLE menus 
            ADD COLUMN IF NOT EXISTS scheduled_text TEXT,
            ADD COLUMN IF NOT EXISTS scheduled_url TEXT,
            ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS applied BOOLEAN DEFAULT TRUE;
            """

            # Execute the migration
            db.session.execute(db.text(migration_sql))
            db.session.commit()

            logger.info("Database migration completed successfully!")
            logger.info(
                "Added columns: scheduled_text, scheduled_url, scheduled_at, applied"
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"Migration failed: {str(e)}")
            raise


if __name__ == "__main__":
    migrate_database()
