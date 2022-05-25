import traceback, os, pypaystack
from flask_restful import Resource, request
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from marshmallow import ValidationError
from http import HTTPStatus

from libs.strings import gettext

from models.order import OrderModel
from models.payment import PaymentModel
from models.user import ResellerModel, BuyerModel
from schemas.payment import PaymentSchema
from transaction import transaction

payment_schema = PaymentSchema()



class PaymentResource(Resource):
    @classmethod
    def get(cls):
        
    
        reference = request.args.get("reference")
        payment = PaymentModel.find_by_reference(reference)
        response = transaction.verify(reference)
        order = OrderModel.find_by_id(str(payment.order_id))
        
        if order:
            buyer = BuyerModel.find_by_id(str(order.buyer_id))
            buyer.set_ip_address(response[3]["ip_address"])
        
            if response[3]["status"] == "success":
                status = "paid" 
                order.set_status(status)
                return {"message": gettext("payment_success"), "payment_id": payment.id, "payment": response}, HTTPStatus.OK
            
            elif response[3]["status"] == "failed":
                status = "unpaid" 
                order.set_status(status)
                return {"message": gettext("payment_failed"), "payment_id": payment.id, "payment": response}, HTTPStatus.OK
           
                
        
                
                    
        

            
            