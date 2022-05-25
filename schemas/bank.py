from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from extension import ma
from models.bank import ResellerBank, SupplierBank



class SupplierBankSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SupplierBank
        dump_only = ("id",)
        include_fk = True
        load_instance = True


class ResellerBankSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ResellerBank
        dump_only = ("id",)
        include_fk = True
        load_instance = True


