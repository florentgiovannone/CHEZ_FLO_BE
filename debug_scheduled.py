from application import app, db
from models.menus_model import MenusModel
from datetime import datetime


def debug_scheduled_tasks():
    """Debug script to check scheduled tasks in database"""
    with app.app_context():
        # Check all scheduled tasks
        all_scheduled = MenusModel.query.filter(
            MenusModel.scheduled_at.isnot(None)
        ).all()
        print(f"=== Found {len(all_scheduled)} total scheduled tasks ===")

        for task in all_scheduled:
            print(f"Task {task.id}: {task.menus_type}")
            print(f"  scheduled_at: {task.scheduled_at}")
            print(f"  applied: {task.applied}")
            print(f"  scheduled_text: {task.scheduled_text}")
            print(f"  scheduled_url: {task.scheduled_url}")
            print("---")

        # Check tasks due now
        now = datetime.now()
        due_tasks = MenusModel.query.filter(
            MenusModel.scheduled_at <= now,
            MenusModel.applied == False,
            MenusModel.scheduled_at.isnot(None),
        ).all()
        print(f"\n=== Found {len(due_tasks)} tasks due now (current time: {now}) ===")

        for task in due_tasks:
            print(
                f"Due Task {task.id}: {task.menus_type}, scheduled for {task.scheduled_at}"
            )

        # Check all menus to see their applied status
        all_menus = MenusModel.query.all()
        print(f"\n=== All menus and their applied status ===")
        for menu in all_menus:
            print(
                f"Menu {menu.id} ({menu.menus_type}): applied={getattr(menu, 'applied', 'NOT SET')}"
            )


if __name__ == "__main__":
    debug_scheduled_tasks()
