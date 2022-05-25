from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from extension import ma
from models.payment import PaymentModel


class ResellerPaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentModel
        dump_only = ("id",)
        include_fk = True



class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentModel
        dump_only = ("id",)
        include_fk = True
