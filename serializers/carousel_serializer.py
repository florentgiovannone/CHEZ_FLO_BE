from app import marshy
from models.carousel_model import CarouselModel
from marshmallow import fields


class CarouselSerializer(marshy.SQLAlchemyAutoSchema):

    class Meta:
        model = CarouselModel
        load_instance = True
