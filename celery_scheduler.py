"""
Celery scheduler for applying scheduled menu updates
"""
from datetime import datetime
import logging
from celery import Celery
from sqlalchemy.exc import SQLAlchemyError
from application import app, db
from models.menus_model import MenusModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Celery
celery = Celery("menu_scheduler")
celery.conf.update(
    broker_url="redis://localhost:6379/0",  # Use Redis as broker
    result_backend="redis://localhost:6379/0",
    timezone="UTC",
    beat_schedule={
        "apply-scheduled-updates": {
            "task": "celery_scheduler.apply_scheduled_updates",
            "schedule": 60.0,  # Run every 60 seconds
        },
    },
)


@celery.task
def apply_scheduled_updates():
    """Celery task to check for and apply scheduled menu updates"""
    with app.app_context():
        try:
            now = datetime.now()

            # Find all scheduled updates that are due and not yet applied
            scheduled_menus = MenusModel.query.filter(
                MenusModel.scheduled_at <= now,
                MenusModel.applied.is_(False),
                MenusModel.scheduled_at.isnot(None),
            ).all()

            if not scheduled_menus:
                logger.info("No scheduled updates to apply")

            logger.info("Found %s scheduled updates to apply", len(scheduled_menus))

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
                        "Applied scheduled update for menu %s (%s)", menu.id, menu.menus_type
                    )

                except SQLAlchemyError as e:
                    logger.error(
                        "Error applying scheduled update for menu %s: %s", menu.id, str(e)
                    )
                    continue

            # Commit all changes
            db.session.commit()
            logger.info("All scheduled updates applied successfully")

        except Exception as e:
            db.session.rollback()
            logger.error("Error in apply_scheduled_updates: %s", str(e))
            raise


if __name__ == "__main__":
    celery.start()
