from application import db
from models.content_model import ContentModel
from models.menus_model import MenusModel
from models.carousel_model import CarouselModel
from models.grid_model import GridModel

# This ensures all models are loaded before relationships are established
__all__ = ["ContentModel", "MenusModel", "CarouselModel", "GridModel"]
