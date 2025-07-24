import time
import logging
from datetime import datetime
from app import app, db
from models.menus_model import MenusModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_scheduled_updates():
    """Check for and apply scheduled menu updates that are due"""
    with app.app_context():
        try:
            now = datetime.now()

            # Find all scheduled updates that are due and not yet applied
            scheduled_menus = MenusModel.query.filter(
                MenusModel.scheduled_at <= now,
                MenusModel.applied == False,
                MenusModel.scheduled_at.isnot(None),
            ).all()

            if not scheduled_menus:
                logger.info("No scheduled updates to apply")
                return

            logger.info(f"Found {len(scheduled_menus)} scheduled updates to apply")

            for menu in scheduled_menus:
                try:
                    # Apply the scheduled changes
                    if menu.scheduled_text:
                        menu.menus_text = menu.scheduled_text
                    if menu.scheduled_url:
                        menu.menus_url = menu.scheduled_url

                    # Clear scheduled fields and mark as applied
                    menu.scheduled_text = None
                    menu.scheduled_url = None
                    menu.scheduled_at = None
                    menu.applied = True

                    logger.info(
                        f"Applied scheduled update for menu {menu.id} ({menu.menus_type})"
                    )

                except Exception as e:
                    logger.error(
                        f"Error applying scheduled update for menu {menu.id}: {str(e)}"
                    )
                    continue

            # Commit all changes
            db.session.commit()
            logger.info("All scheduled updates applied successfully")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in apply_scheduled_updates: {str(e)}")


def run_scheduler():
    """Run the scheduler that checks for updates every minute"""
    logger.info("Starting menu update scheduler...")

    while True:
        try:
            apply_scheduled_updates()
            time.sleep(60)  # Wait 60 seconds (1 minute)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in scheduler: {str(e)}")
            time.sleep(60)  # Continue after error


if __name__ == "__main__":
    run_scheduler()
