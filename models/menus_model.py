from app import db


class MenusModel(db.Model):
    __tablename__ = "menus"  # The name of the table in the database
    id = db.Column(db.Integer, primary_key=True, unique=True)
    menus_type = db.Column(
        db.Text, nullable=False
    )  # breakfast, lunch, dessert, winelist, cocktail
    menus_text = db.Column(db.Text, nullable=False)
    menus_url = db.Column(db.Text, nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)

    # Scheduled update fields
    scheduled_text = db.Column(db.Text, nullable=True)
    scheduled_url = db.Column(db.Text, nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=True)
    applied = db.Column(db.Boolean, default=True)

    def remove(self):
        db.session.delete(self)
        db.session.commit()
