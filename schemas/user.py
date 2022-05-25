from extension import ma

from marshmallow import pre_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from models.user import SupplierModel, ResellerModel, SubAdminModel
from models.bank import SupplierBank, ResellerBank
from models.order import OrderModel
from models.item import ItemModel, SharedItemModel

from schemas.order import OrderSchema
from schemas.bank import SupplierBankSchema, ResellerBankSchema
from schemas.item import ItemSchema, SharedItemSchema


class SupplierSchema(ma.SQLAlchemyAutoSchema):
    bankaccount = ma.Nested(SupplierBankSchema)
    orders = ma.Nested(OrderSchema, many=True)
    items = ma.Nested(ItemSchema, many=True)
    class Meta:
        model = SupplierModel
        dump_only = ("id", "active", "bankaccount", "orders", "items")
        include_fk = True
        load_instance = True



class ResellerSchema(ma.SQLAlchemyAutoSchema):
    bankaccount = ma.Nested(ResellerBankSchema)
    orders = ma.Nested(OrderSchema, many=True)
    shareditems = ma.Nested(SharedItemSchema, many=True)
    class Meta:
        model = ResellerModel
        load_only = ("password",)
        dump_only = ("id", "confirmations", "bankaccount", "orders", "shareditems")
        include_fk = True
        load_instance = True

    @pre_dump
    def _pre_dump(self, user: ResellerModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user


class SubAdminSchema(ma.SQLAlchemyAutoSchema):
    suppliers = ma.Nested(SupplierSchema, many=True, 
                          exclude=('name', 'email', 'address1', 'address2', 'city', 
                                   'state', 'zipcode', 'businessregistered', 'cacnumber', 
                                   'maincategory', 'businesstype', 'pricerange', 'averagestock', 
                                   'saleschannel', 'active', 'subadmin_id', 'bankaccount', 'items', 'orders', 
                                   'updated_at', 'created_at', 'ip_address'))
    class Meta:
        model = SubAdminModel
        load_only = ("password",)
        dump_only = ("id", "suppliers")
        include_fk = True
        load_instance = True
    
    @pre_dump
    def _pre_dump(self, user: SubAdminModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user
