from flask import url_for, request
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from extension import ma
from models.order import OrderModel
from models.item import ItemModel, SharedItemModel
from models.payment import PaymentModel
from schemas.item import ItemSchema, SharedItemSchema
from schemas.pagination import PaginationSchema


class OrderSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True, exclude=('image_url', ))
    payment_api_url = fields.Method(serialize="dump_payment_link")
    class Meta:
        model = OrderModel
        load_only = ("supplier_id", "reseller_id")
        dump_only = ("id")
        include_fk = True
        load_instance = True
    
    def dump_payment_link(self, order: OrderModel, **kwargs):
        link = request.url_root[:-1] + url_for("orderpaymentresource", order_id=order.id)
        return link
        

class OrderPaginationSchema(PaginationSchema):
    data = fields.Nested(OrderSchema, attribute='items', many=True)




"""     
class ResellerOrderSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(SharedItemSchema, many=True)
    payment = ma.Nested(PaymentModel)
    class Meta:
        model = OrderModel
        load_only = ("reseller_id",)
        dump_only = ("id", "items")
        include_fk = True
        load_instance = True
"""