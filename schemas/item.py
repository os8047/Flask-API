from flask import url_for
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields

from extension import ma
from models.item import ItemModel, SharedItemModel
from models.category import Category
from models.image import ImageModel

from schemas.pagination import PaginationSchema


class ItemSchema(ma.SQLAlchemyAutoSchema):
    image_url = fields.Method(serialize='dump_image_url', many=True)
    class Meta:
        model = ItemModel
        load_only = ("category",)
        dump_only = ("id",)
        include_fk = True
        load_instance = True
    
    
    def dump_image_url(self, item: ItemModel, **kwargs):
        
        url = []
        if item.item_images is None:
            return url_for('static', filename='images/assets/default_thumbnail.svg', _external=True)
        for image in item.item_images:
            url.append(url_for('static', filename='images/{}/{}/{}'.format(item.supplier_id, item.id, image.name), _external=True))
        return url
        
                
    
        

class SharedItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SharedItemModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True
        
        
class ItemPaginationSchema(PaginationSchema):
    data = fields.Nested(ItemSchema, attribute='items', many=True)
    

class SharedItemPaginationSchema(PaginationSchema):
    data = fields.Nested(SharedItemSchema, attribute='items', many=True)