from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from extension import ma
from models.confirmation import SupplierConfirmationModel, ResellerConfirmationModel


class SupplierConfirmationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SupplierConfirmationModel
        load_only = ("supplier_id",)
        dump_only = ("id", "expire_at", "confirmed")
        include_fk = True
        load_instance = True
        
        
class ResellerConfirmationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ResellerConfirmationModel
        load_only = ("reseller_id",)
        dump_only = ("id", "expire_at", "confirmed")
        include_fk = True
        load_instance = True