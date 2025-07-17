from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.menus_model import MenusModel


class MenusSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = MenusModel
        load_instance = True
        include_fk = True
