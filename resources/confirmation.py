import traceback
from time import time
from http import HTTPStatus

from flask import make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.confirmation import SupplierConfirmationModel, ResellerConfirmationModel, SubAdminConfirmationModel
from models.user import SupplierModel, ResellerModel, SubAdminModel
#from schemas.confirmation import SupplierConfirmationSchema, ResellerConfirmationSchema

from libs.mailgun import MailGun, MailGunException
from libs.strings import gettext

#supplier_confirmation_schema = SupplierConfirmationSchema()

"""
Subadmin Confirmation Resources
"""
class SubAdminConfirmation(Resource):
    
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = SubAdminConfirmationModel.find_by_id(confirmation_id)
        
        if not confirmation:
            return {"message": "Confirmation does not exist"}, HTTPStatus.OK
        
        if confirmation.expired:
            return {"message": "Link is already expired"}, HTTPStatus.OK
        
        if confirmation.confirmed:
            return {"message": f"Your email {user_email} is already confirmed"}, HTTPStatus.OK
        
        confirmation.confirmed = True
        confirmation.save_to_db()
        return {"message": "Thank you for confirming your email"}
    
    
class SubAminConfirmationByUser(Resource):
    
    @classmethod
    def post(cls, subadmin_id: str):

        user = SubAdminConfirmationModel.find_by_id(supplier_id)
        
        if user:
            try:
                confirmation = user.most_recent_confirmation
                if confirmation.confirmed:
                    return {"message": gettext("confirmation_already_confirmed")}, HTTPStatus.BAD_REQUEST
                confirmation.force_to_expire()
                new_confirmation = SubAdminConfirmationModel(user_id)
                new_confirmation.save_to_db()
                user.send_confirmation_email()
                return {"message": gettext("confirmation_resend_successful")}, HTTPStatus.CREATED
            except MailGunException as err:
                return {"message": str(err)}, HTTPStatus.INTERNAL_SERVER_ERROR
            except:
                traceback.print_exc()
                return {"message": gettext("confirmation_resend_fail")}, HTTPStatus.INTERNAL_SERVER_ERROR



"""
class SupplierConfirmation(Resource):
    
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = SupplierConfirmationModel.find_by_id(confirmation_id)
        
        if not confirmation:
            return {"message": "Confirmation does not exist"}, HTTPStatus.OK
        
        if confirmation.expired:
            return {"message": "Link is already expired"}, HTTPStatus.OK
        
        if confirmation.confirmed:
            return {"message": f"Your email {user_email} is already confirmed"}, HTTPStatus.OK
        
        confirmation.confirmed = True
        confirmation.save_to_db()
        return {"message": "Thank you for confirming your email"}
    
    
class SupplierConfirmationByUser(Resource):
    
    @classmethod
    def post(cls, supplier_id: str):

        user = SupplierModel.find_by_id(supplier_id)
        
        if user:
            try:
                confirmation = user.most_recent_confirmation
                if confirmation.confirmed:
                    return {"message": gettext("confirmation_already_confirmed")}, HTTPStatus.BAD_REQUEST
                confirmation.force_to_expire()
                new_confirmation = SupplierConfirmationModel(user_id)
                new_confirmation.save_to_db()
                user.send_confirmation_email()
                return {"message": gettext("confirmation_resend_successful")}, HTTPStatus.CREATED
            except MailGunException as err:
                return {"message": str(err)}, HTTPStatus.INTERNAL_SERVER_ERROR
            except:
                traceback.print_exc()
                return {"message": gettext("confirmation_resend_fail")}, HTTPStatus.INTERNAL_SERVER_ERROR
"""                

"""
Reseller Confirmation Resources
"""

class ResellerConfirmation(Resource):
    
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ResellerConfirmationModel.find_by_id(confirmation_id)
        
        if not confirmation:
            return {"message": "Confirmation does not exist"}, HTTPStatus.OK
        
        if confirmation.expired:
            return {"message": "Link is already expired"}, HTTPStatus.OK
        
        if confirmation.confirmed:
            return {"message": f"Your email {user_email} is already confirmed"}, HTTPStatus.OK
        
        confirmation.confirmed = True
        confirmation.save_to_db()
        return {"message": "Thank you for confirming your email"}


class ResellerConfirmationByUser(Resource):
    
    @classmethod
    def post(cls, reseller_id: str):

        user = ResellerConfirmationModel.find_by_id(reseller_id)
        
        if user:
            try:
                confirmation = user.most_recent_confirmation
                if confirmation.confirmed:
                    return {"message": gettext("confirmation_already_confirmed")}, HTTPStatus.BAD_REQUEST
                confirmation.force_to_expire()
                new_confirmation = ResellerConfirmationModel(user_id)
                new_confirmation.save_to_db()
                user.send_confirmation_email()
                return {"message": gettext("confirmation_resend_successful")}, HTTPStatus.CREATED
            except MailGunException as err:
                return {"message": str(err)}, HTTPStatus.INTERNAL_SERVER_ERROR
            except:
                traceback.print_exc()
                return {"message": gettext("confirmation_resend_fail")}, HTTPStatus.INTERNAL_SERVER_ERROR