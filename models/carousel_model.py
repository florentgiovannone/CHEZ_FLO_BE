from app import db


class CarouselModel(db.Model):
    __tablename__ = "carousel"  # The name of the table in the database
    id = db.Column(db.Integer, primary_key=True, unique=True)
    carousel_url = db.Column(db.Text, nullable=False)
    content_id = db.Column(
        db.Integer, db.ForeignKey("content.id"), nullable=False
    ) 

    def remove(self):
        db.session.delete(self)
        db.session.commit()
