from app import marshy
from models.content_model import ContentModel
from marshmallow import fields
from serializers.carousel_serializer import CarouselSerializer


class ContentSerializer(marshy.SQLAlchemyAutoSchema):
    carousels = fields.List(fields.Nested(CarouselSerializer))

    class Meta:
        model = ContentModel
        load_instance = True
