from app import marshy
from models.content_model import ContentModel
from marshmallow import fields
from serializers.carousel_serializer import CarouselSerializer
from serializers.menus_serializer import MenusSerializer
from serializers.grid_serializer import GridSerializer

class ContentSerializer(marshy.SQLAlchemyAutoSchema):
    carousels = fields.List(fields.Nested(CarouselSerializer))
    menus = fields.List(fields.Nested(MenusSerializer))
    grid = fields.List(fields.Nested(GridSerializer))

    class Meta:
        model = ContentModel
        load_instance = True
