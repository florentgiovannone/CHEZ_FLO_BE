from app import db


class GridModel(db.Model):
    __tablename__ = "grid"  # The name of the table in the database
    id = db.Column(db.Integer, primary_key=True, unique=True)
    grid_url = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)

    def remove(self):
        db.session.delete(self)
        db.session.commit()
