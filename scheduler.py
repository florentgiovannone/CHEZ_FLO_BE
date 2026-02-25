import time
import logging
from datetime import datetime, timezone, timedelta
from application import app, db
from models.menus_model import MenusModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_scheduled_updates():
    """Check for and apply scheduled menu updates that are due"""
    with app.app_context():
        try:
            # Get current BST time (convert from UTC)
            utc_now = datetime.now(timezone.utc)
            bst_timezone = timezone(timedelta(hours=1))  # BST = UTC+1
            bst_now = utc_now.astimezone(bst_timezone).replace(
                tzinfo=None
            )  # Remove timezone for DB comparison

            # First, get all scheduled updates to show what we're tracking
            all_scheduled = MenusModel.query.filter(
                MenusModel.scheduled_at.isnot(None), MenusModel.applied == False
            ).all()

            # Find updates that are due (comparing BST times)
            due_scheduled = MenusModel.query.filter(
                MenusModel.scheduled_at <= bst_now,  # Database stores BST times
                MenusModel.applied == False,
                MenusModel.scheduled_at.isnot(None),
            ).all()

            # Improved logging - BST focused
            if all_scheduled:
                logger.info(
                    f"🕐 Current BST time: {bst_now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info(
                    f"📋 Tracking {len(all_scheduled)} pending scheduled updates:"
                )
                for menu in all_scheduled:
                    # Database stores BST times
                    time_diff = (menu.scheduled_at - bst_now).total_seconds()
                    if time_diff > 0:
                        minutes_left = int(time_diff / 60)
                        logger.info(
                            f"  - {menu.menus_type} menu: due in {minutes_left} minutes ({menu.scheduled_at.strftime('%H:%M BST')})"
                        )
                    else:
                        logger.info(
                            f"  - {menu.menus_type} menu: DUE NOW ({menu.scheduled_at.strftime('%H:%M BST')})"
                        )
            else:
                logger.info("📋 No scheduled updates pending")

            if not due_scheduled:
                logger.info("⏰ No scheduled updates due for application at this time")
                return

            logger.info(
                f"🚀 Found {len(due_scheduled)} scheduled updates ready to apply"
            )

            for menu in due_scheduled:
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
                        f"✅ Applied scheduled update for {menu.menus_type} menu (ID: {menu.id})"
                    )

                except Exception as e:
                    logger.error(
                        f"❌ Error applying scheduled update for menu {menu.id}: {str(e)}"
                    )
                    continue

            # Commit all changes
            db.session.commit()
            logger.info(
                f"🎉 Successfully applied {len(due_scheduled)} scheduled updates"
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"💥 Error in apply_scheduled_updates: {str(e)}")


def run_scheduler():
    """Run the scheduler that checks for updates every minute"""
    logger.info("🚀 Starting BST menu update scheduler...")

    while True:
        try:
            apply_scheduled_updates()
            time.sleep(60)  # Wait 60 seconds (1 minute)
        except KeyboardInterrupt:
            logger.info("⏹️  Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"💥 Unexpected error in scheduler: {str(e)}")
            time.sleep(60)  # Continue after error


if __name__ == "__main__":
    run_scheduler()
