from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from extension import ma
from models.category import Category
from models.item import ItemModel
from schemas.item import ItemSchema


class CategorySchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True)
    class Meta:
        model = Category
        dump_only = ("id", "items")
        load_instance = True
