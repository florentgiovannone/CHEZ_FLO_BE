from app import app, db
from models.menus_model import MenusModel
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_scheduler_time():
    """Debug the scheduler's time comparison logic"""
    with app.app_context():
        try:
            now = datetime.now()
            logger.info(f"Scheduler current time: {now}")
            logger.info(f"Scheduler current time ISO: {now.isoformat()}")

            # Get all scheduled tasks
            all_scheduled = MenusModel.query.filter(
                MenusModel.scheduled_at.isnot(None)
            ).all()
            logger.info(f"Found {len(all_scheduled)} total scheduled tasks")

            for task in all_scheduled:
                logger.info(f"Task {task.id} ({task.menus_type}):")
                logger.info(f"  scheduled_at: {task.scheduled_at}")
                logger.info(f"  scheduled_at type: {type(task.scheduled_at)}")
                logger.info(f"  applied: {task.applied}")
                logger.info(
                    f"  is due? {task.scheduled_at <= now if task.scheduled_at else 'N/A'}"
                )
                logger.info(
                    f"  time diff: {(task.scheduled_at - now).total_seconds() if task.scheduled_at else 'N/A'} seconds"
                )
                logger.info("---")

            # Use the exact same query as the scheduler
            due_tasks = MenusModel.query.filter(
                MenusModel.scheduled_at <= now,
                MenusModel.applied == False,
                MenusModel.scheduled_at.isnot(None),
            ).all()

            logger.info(f"Tasks due according to scheduler query: {len(due_tasks)}")
            for task in due_tasks:
                logger.info(
                    f"Due task: {task.id} ({task.menus_type}) - {task.scheduled_at}"
                )

        except Exception as e:
            logger.error(f"Debug error: {str(e)}")


if __name__ == "__main__":
    debug_scheduler_time()
