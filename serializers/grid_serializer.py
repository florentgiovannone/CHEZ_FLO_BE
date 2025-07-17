from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.grid_model import GridModel


class GridSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = GridModel
        load_instance = True
        include_fk = True
