import traceback
from flask_restful import Resource, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    fresh_jwt_required
)
from marshmallow import ValidationError
from http import HTTPStatus

from models.user import SupplierModel, ResellerModel, SubAdminModel
from models.confirmation import SupplierConfirmationModel, ResellerConfirmationModel, SubAdminConfirmationModel
from schemas.user import SupplierSchema, ResellerSchema, SubAdminSchema

from blacklist import BLACKLIST
from libs.utils import hash_password, check_password, validate_password
from libs.strings import gettext
from libs.mailgun import MailGunException

reseller_schema = ResellerSchema()
supplier_schema = SupplierSchema()
subadmin_schema = SubAdminSchema()


"""
SUBADMIN RESOURCE
"""

class SubAdminRegisterResource(Resource):
    
    @classmethod
    def post(cls):
        try:
            subadmin_data = request.get_json()
            if not validate_password(subadmin_data["password"]):
                return {"message": gettext("password_not_secure")}
            
            subadmin_data["password"] = hash_password(subadmin_data["password"])
            subadmin_data["ip_address"] = request.remote_addr
            subadmin = subadmin_schema.load(subadmin_data)
        except ValidationError as err:
            return err.messages, HTTPStatus.BAD_REQUEST
        
        if SubAdminModel.find_by_email(subadmin.email):
            return {"message": gettext("user_email_exist").format(subadmin.email)}, HTTPStatus.BAD_REQUEST
        if SubAdminModel.find_by_username(subadmin.username):
            return {"message": gettext("user_username_exist").format(subadmin.username)}, HTTPStatus.BAD_REQUEST
        
        try:
            subadmin.save_to_db()
            confirmation = SubAdminConfirmationModel(subadmin.id)
            confirmation.save_to_db()
            subadmin.send_confirmation_email()
            return {"message": gettext("user Registered")}, HTTPStatus.CREATED
        except MailGunException as err:
            return {"message": str(err)}, HTTPStatus.INTERNAL_SERVER_ERROR
        except:
            traceback.print_exc()
            subadmin.delete_from_db()
            return {"message": gettext("user_error_creating")}, HTTPStatus.INTERNAL_SERVER_ERROR
        
        

class SubAdminLoginResource(Resource):
    
    @classmethod
    def post(cls):
        subadmin_json = request.get_json()
        subadmin_data = subadmin_schema.load(subadmin_json, partial=("firstname", "lastname", "email", "ip_address", "street", "city", "state", "zipcode"))
        
        subadmin = SubAdminModel.find_by_username(subadmin_data.username)
        
        if subadmin and check_password(subadmin_data.password, subadmin.password):
            confirmation = subadmin.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=subadmin.id, fresh=True)
                refresh_token = create_refresh_token(subadmin.id)
                return {"subadmin_access_token": access_token, "subadmin_refresh_token": refresh_token}, HTTPStatus.CREATED
            return {"message": gettext("user_not_confirmed")}, HTTPStatus.BAD_REQUEST
        return {"message": gettext("user_invalid_credentials")}, HTTPStatus.UNAUTHORIZED
    
    

class SubAdminLogoutResource(Resource):
    
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]
        BLACKLIST.add(jti)
        return {"message": gettext("user_logged_out")}, HTTPStatus.OK
    
    

class SubAdminResource(Resource):
    
    @classmethod
    @jwt_required
    def get(cls):
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        if subadmin:
            return subadmin_schema.dump(subadmin), HTTPStatus.OK
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
    
    @classmethod
    @fresh_jwt_required
    def patch(cls):
        
        subadmin_json = request.get_json()
            
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        
        if subadmin:
            subadmin.firstname = subadmin_json.get("firstname") or subadmin.firstname
            subadmin.lastname = subadmin_json.get("lastname") or subadmin.lastname
            subadmin.username = subadmin_json.get("username") or subadmin.username
            subadmin.email = subadmin_json.get("email") or subadmin.email
            subadmin.password = subadmin_json.get("password") or subadmin.password
            
            try:
                subadmin.save_to_db()
            except:
                traceback.print_exc
                return {"message": gettext("error_saving")}, HTTPStatus.INTERNAL_SERVER_ERROR
                
            return subadmin_schema.dump(subadmin), HTTPStatus.OK             
        else:
            return {"message": gettext("user_bad_parameter")}, HTTPStatus.BAD_REQUEST
                
    
    @classmethod
    @jwt_required
    def delete(cls):
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        if subadmin:
            subadmin.delete_from_db()
            return {"message": gettext("user_deleted")}, HTTPStatus.OK
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
    

"""
Do not expose this endpoint
"""
class SupplierAddToSubAdmin(Resource):
    
    @classmethod
    def post(cls):
        data = request.get_json()
        supplier_id = data["supplier_id"]
        subadmin_id = data["subadmin_id"]
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        if subadmin:
            supplier = SupplierModel.find_by_id(supplier_id)
            if supplier:
                supplier.subadmin_id = subadmin_id
                try:
                    supplier.save_to_db()
                    return {"message": "Supplier Successfully added to Admin"}, HTTPStatus.OK
                except:
                    return {"message": "Error adding supplier to admin"}, HTTPStatus.INTERNAL_SERVER_ERROR
            else:
                return {"message": gettext("account_not_exist")}, HTTPStatus.NOT_FOUND
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
           
        


"""
SUPPLIER RESOURCE

"""

class SupplierRegister(Resource):
    
    @classmethod
    def post(cls):
        try:
            user_data = request.get_json()
            user_data["ip_address"] = request.remote_addr
            user = supplier_schema.load(user_data)
        except ValidationError as err:
            return err.messages, HTTPStatus.BAD_REQUEST
        
        if SupplierModel.find_by_name(user.name):
            return {"message": gettext("user_name_exist").format(user.name)}, HTTPStatus.BAD_REQUEST
        
        if SupplierModel.find_by_email(user.email):
            return {"message": gettext("user_email_exist").format(user.email)}, HTTPStatus.BAD_REQUEST
        
        if SupplierModel.find_by_cacnumber(user.cacnumber):
            return {"message": gettext("user_cacnumber_exist").format(user.cacnumber)}, HTTPStatus.BAD_REQUEST
        
        try:
            user.save_to_db()
            return {"message": gettext("user Registered"), "id": user.id}, HTTPStatus.CREATED
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": gettext("user_error_creating")}, HTTPStatus.INTERNAL_SERVER_ERROR
        
    
"""
This resource requires subadmin authentication
"""   
class Supplier(Resource):
    
    """
    @classmethod
    @jwt_required
    def post(cls):
        supplier_data = request.get_json()
        supplier_id = supplier_data["supplier_id"]
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        if subadmin:
            supplier = SupplierModel.find_by_id(supplier_id)
            if supplier:
                supplier.subadmin_id = subadmin_id
                try:
                    supplier.save_to_db()
                    return {"message": "Supplier Successfully added to Admin"}, HTTPStatus.OK
                except:
                    return {"message": "Error adding supplier to admin"}, HTTPStatus.INTERNAL_SERVER_ERROR
            else:
                return {"message": gettext("account_not_exist")}, HTTPStatus.NOT_FOUND
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
    """
    
    @classmethod
    @jwt_required
    def get(cls, supplier_id):
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            supplier = SupplierModel.find_by_id(supplier_id)
            if supplier:
                return supplier_schema.dump(supplier), HTTPStatus.OK
            else:
                return {"message": gettext("account_not_exist")}, HTTPStatus.NOT_FOUND
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
    
    @classmethod
    @fresh_jwt_required
    def patch(cls, supplier_id):
        
        data_json = request.get_json()
            
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            supplier = SupplierModel.find_by_id(supplier_id)
            if not supplier:
                return {"message": gettext("user_bad_parameter")}, HTTPStatus.BAD_REQUEST
            
            supplier.address1 = data_json.get("address1") or supplier.address1
            supplier.city = data_json.get("city") or supplier.city
            supplier.state = data_json.get("state") or supplier.state
            supplier.email = data_json.get("email") or supplier.email
            try:
                supplier.save_to_db()
            except:
                traceback.print_exc
                return {"message": gettext("error_saving")}, HTTPStatus.INTERNAL_SERVER_ERROR   
            return supplier_schema.dump(supplier), HTTPStatus.OK
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND         
       
            
                
    
    @classmethod
    @jwt_required
    def delete(cls, supplier_id):
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            supplier = SupplierModel.find_by_id(supplier_id)
            supplier.delete_from_db()
            return {"message": gettext("user_deleted")}, HTTPStatus.OK
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
    

"""
RESELLER RESOURCE

"""

class ResellerRegister(Resource):
    
    @classmethod
    def post(cls):
        try:
            user_data = request.get_json()
            if validate_password(user_data["password"]):
                user_data["password"] = hash_password(user_data["password"])
            else:
                return {"message": gettext("password_not_secure")}
            user_data["ip_address"] = request.remote_addr
            user = reseller_schema.load(user_data)
        except ValidationError as err:
            return err.messages, HTTPStatus.BAD_REQUEST
        
        if ResellerModel.find_by_email(user.email):
            return {"message": gettext("user_email_exist").format(user.email)}, HTTPStatus.BAD_REQUEST
        
        try:
            user.save_to_db()
            confirmation = ResellerConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("user Registered")}, HTTPStatus.CREATED
        except MailGunException as err:
            return {"message": str(err)}, HTTPStatus.INTERNAL_SERVER_ERROR
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": gettext("user_error_creating")}, HTTPStatus.INTERNAL_SERVER_ERROR
        
   
        
class ResellerLogin(Resource):
    
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = reseller_schema.load(user_json, partial=("firstname", "lastname", "ip_address"))
        
        user = ResellerModel.find_by_email(user_data.email)
        
        if user and check_password(user_data.password, user.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"reseller_access_token": access_token, "reseller_refresh_token": refresh_token}, HTTPStatus.CREATED
            return {"message": gettext("user_not_confirmed")}, HTTPStatus.BAD_REQUEST
        return {"message": gettext("user_invalid_credentials")}, HTTPStatus.UNAUTHORIZED
    
    
class ResellerLogout(Resource):
    
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]
        BLACKLIST.add(jti)
        return {"message": gettext("user_logged_out")}, HTTPStatus.OK
        
        

class Reseller(Resource):
    
    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        user = ResellerModel.find_by_id(user_id)
        if user:
            return reseller_schema.dump(user), HTTPStatus.OK
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
    
    @classmethod
    @fresh_jwt_required
    def patch(cls):
        
        user_json = request.get_json()
            
        user_id = get_jwt_identity()
        user = ResellerModel.find_by_id(user_id)
        
        if user:
            user.firstname = user_json.get("firstname") or user.firstname
            user.lastname = user_json.get("lastname") or user.lastname
            user.email = user_json.get("email") or user.email
            user.password = user_json.get("password") or user.password
            
            try:
                user.save_to_db()
            except:
                traceback.print_exc
                return {"message": gettext("error_saving")}, HTTPStatus.INTERNAL_SERVER_ERROR
                
            return reseller_schema.dump(user), HTTPStatus.OK             
        else:
            return {"message": gettext("user_bad_parameter")}, HTTPStatus.BAD_REQUEST
                
    
    @classmethod
    @jwt_required
    def delete(cls):
        user_id = get_jwt_identity()
        user = ResellerModel.find_by_id(user_id)
        if user:
            user.delete_from_db()
            return {"message": gettext("user_deleted")}, HTTPStatus.OK
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
    
        
                   
"""
Resource to generate new access token
"""
class RefreshToken(Resource):
    
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, HTTPStatus.CREATED
        