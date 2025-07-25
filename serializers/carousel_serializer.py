from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.carousel_model import CarouselModel


class CarouselSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = CarouselModel
        load_instance = True
        include_fk = True
