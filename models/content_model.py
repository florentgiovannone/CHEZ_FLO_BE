from app import db

class ContentModel(db.Model):
    __tablename__ = "content"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    about_title = db.Column(db.Text, nullable=False)
    about_text = db.Column(db.Text, nullable=False)
    breakfast_menus_text = db.Column(db.Text, nullable=False)
    breakfast_menus_file = db.Column(db.Text, nullable=False)
    lunch_menus_text = db.Column(db.Text, nullable=False)
    lunch_menus_file = db.Column(db.Text, nullable=False)
    dessert_menus_text = db.Column(db.Text, nullable=False)
    dessert_menus_file = db.Column(db.Text, nullable=False)
    winelist_menus_text = db.Column(db.Text, nullable=False)
    winelist_menus_file = db.Column(db.Text, nullable=False)
    cocktail_menus_text = db.Column(db.Text, nullable=False)
    cocktail_menus_file = db.Column(db.Text, nullable=False)
    image_one = db.Column(db.Text, nullable=False)
    image_two = db.Column(db.Text, nullable=False)
    image_three = db.Column(db.Text, nullable=False)
    image_four = db.Column(db.Text, nullable=False)
    image_five = db.Column(db.Text, nullable=False)
    image_six = db.Column(db.Text, nullable=False)
    reservation_title = db.Column(db.Text, nullable=False)
    reservation_text = db.Column(db.Text, nullable=False)
    breakfast_timing_day_one = db.Column(db.Text, nullable=False)
    breakfast_timing_hours_one = db.Column(db.Text, nullable=False)
    breakfast_timing_day_two = db.Column(db.Text, nullable=False)
    breakfast_timing_hours_two = db.Column(db.Text, nullable=False)
    lunch_timing_day_one = db.Column(db.Text, nullable=False)
    lunch_timing_hours_one = db.Column(db.Text, nullable=False)
    lunch_timing_day_two = db.Column(db.Text, nullable=False)
    lunch_timing_hours_two = db.Column(db.Text, nullable=False)
    dinner_timing_day_one = db.Column(db.Text, nullable=False)
    dinner_timing_hours_one = db.Column(db.Text, nullable=False)
    dinner_timing_day_two = db.Column(db.Text, nullable=False)
    dinner_timing_hours_two = db.Column(db.Text, nullable=False)
    reservation_line_one = db.Column(db.Text, nullable=False)
    reservation_line_two = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    contact_title = db.Column(db.Text, nullable=False)
    contact_adress_one = db.Column(db.Text, nullable=False)
    contact_adress_two = db.Column(db.Text, nullable=False)
    contact_opening_day_one = db.Column(db.Text, nullable=False)
    contact_opening_hours_one = db.Column(db.Text, nullable=False)
    contact_opening_day_two = db.Column(db.Text, nullable=False)
    contact_opening_hours_two = db.Column(db.Text, nullable=False)
    contact_opening_day_three = db.Column(db.Text, nullable=False)
    contact_opening_hours_three = db.Column(db.Text, nullable=False)
    contact_opening_hours_three = db.Column(db.Text, nullable=False)
    map= db.Column(db.Text, nullable=False)
    carousels = db.relationship("CarouselModel", backref="content", lazy="joined")

    def remove(self):
        db.session.delete(self)
        db.session.commit()
