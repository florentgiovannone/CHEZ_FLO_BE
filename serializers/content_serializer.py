from app import marshy
from models.content_model import ContentModel 


class ContentSerializer(marshy.SQLAlchemySchema):
    class Meta:
        model = ContentModel
        load_instance = True

    id = marshy.auto_field()
    about_title = marshy.auto_field()
    about_text = marshy.auto_field()
    breakfast_menus_text = marshy.auto_field()
    breakfast_menus_file = marshy.auto_field()
    lunch_menus_text = marshy.auto_field()
    lunch_menus_file = marshy.auto_field()
    dinner_menus_text = marshy.auto_field()
    dinner_menus_file = marshy.auto_field()
    winelist_menus_text = marshy.auto_field()
    winelist_menus_file = marshy.auto_field()
    cocktail_menus_text = marshy.auto_field()
    cocktail_menus_file = marshy.auto_field()
    image_one = marshy.auto_field()
    image_two = marshy.auto_field()
    image_three = marshy.auto_field()
    image_four = marshy.auto_field()
    image_five = marshy.auto_field()
    image_six = marshy.auto_field()
    reservation_title = marshy.auto_field()
    reservation_text = marshy.auto_field()
    breakfast_timing_title = marshy.auto_field()
    breakfast_timing_mtof = marshy.auto_field()
    breakfast_timing_sands = marshy.auto_field()
    lunch_timing_title = marshy.auto_field()
    lunch_timing_mtos = marshy.auto_field()
    lunch_timing_sun = marshy.auto_field()
    dinner_timing_title = marshy.auto_field()
    dinner_timing_mtos = marshy.auto_field()
    dinner_timing_sun = marshy.auto_field()
    reservation_line_one = marshy.auto_field()
    reservation_line_two = marshy.auto_field()
    phone = marshy.Function(lambda obj: f"+{obj.phone}")    
    email = marshy.auto_field()
    contact_title = marshy.auto_field()
    contact_adress_one = marshy.auto_field()
    contact_adress_two = marshy.auto_field()
    contact_opening_mtof = marshy.auto_field()
    contact_opening_sat = marshy.auto_field()
    contact_opening_sun = marshy.auto_field()
