import traceback
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity, fresh_jwt_required
from marshmallow import ValidationError
from http import HTTPStatus

from libs.strings import gettext

from models.bank import SupplierBank, ResellerBank
from schemas.bank import SupplierBankSchema, ResellerBankSchema

supplier_bank_schema = SupplierBankSchema()
reseller_bank_schema = ResellerBankSchema()


class SupplierBankResource(Resource):
    
    @classmethod
    @jwt_required
    def get(cls, supplier_id: str):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
        bank_details = SupplierBank.find_by_supplier(supplier_id)
        if bank_details:
            return supplier_bank_schema.dump(bank_details), HTTPStatus.OK
        return {"message": gettext("bank_not_found")}, HTTPStatus.NOT_FOUND
    
    @classmethod
    def post(cls, supplier_id: str):
        
        try:
            bank_json = request.get_json()
            bank_json["supplier_id"] = supplier_id
            bank_details = supplier_bank_schema.load(bank_json)
        except ValidationError as err:
            return err.messages, HTTPStatus.BAD_REQUEST
        
        try:
            #print(bank_details)
            bank_details.save_to_db()
            return {"message": gettext("bank_created")}, HTTPStatus.CREATED
        except:
            traceback.print_exc()
            return {"message": gettext("bank_creation_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
        
    @classmethod
    @fresh_jwt_required
    def patch(cls, supplier_id: str):
        
        bank_json = request.get_json()
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
        bank_details = SupplierBank.find_by_supplier(supplier_id)
        
        if bank_details:
            try:
                bank_details.bankname = bank_json.get("bankname") or bank_details.bankname
                bank_details.accountname = bank_json.get("accountname") or bank_details.accountname
                bank_details.accountnumber = bank_json.get("accountnumber") or bank_details.accountnumber
                bank_details.accounttype = bank_json.get("accounttype") or bank_details.accounttype
            except:
                return {"message": gettext("bank_bad_parameter")}, HTTPStatus.BAD_REQUEST
            
        try:
            bank_details.save_to_db()
            return supplier_bank_schema.dump(bank_details), HTTPStatus.OK
        except:
            traceback.print_exc()
            bank_details.delete_from_db()
            return {"message": gettext("bank_update_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
            
            
    @classmethod
    @jwt_required
    def delete(cls, supplier_id: str):
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
        bank_details = SupplierBank.find_by_supplier(supplier_id)
        if bank_details:
            try:
                bank_details.delete_from_db()
                return {"message": gettext("bank_deleted")}, HTTPStatus.OK
            except:
                traceback.print_exc()
                return {"message": gettext("bank_delete_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {"message": gettext("bank_not_found")}, HTTPStatus.NOT_FOUND
                
                

class ResellerBankResource(Resource):
    
    @classmethod
    @jwt_required
    def get(cls):
        
        reseller_id = get_jwt_identity()
        bank_details = ResellerBank.find_by_reseller(reseller_id)
        if bank_details:
            return reseller_bank_schema.dump(bank_details), HTTPStatus.OK
        return {"message": gettext("bank_not_found")}, HTTPStatus.NOT_FOUND
    
    @classmethod
    @jwt_required
    def post(cls):
        
        reseller_id = get_jwt_identity()
        try:
            bank_json = request.get_json()
            bank_json["reseller_id"] = reseller_id
            bank_details = reseller_bank_schema.load(bank_json)
        except ValidationError as err:
            return err.messages, HTTPStatus.BAD_REQUEST
        
        try:
            bank_details.save_to_db()
            return {"message": gettext("bank_created")}, HTTPStatus.CREATED
        except:
            traceback.print_exc()
            return {"message": gettext("bank_creation_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
        
    @classmethod
    @fresh_jwt_required
    def patch(cls):
        
        bank_json = request.get_json()
        
        reseller_id = get_jwt_identity()
        bank_details = ResellerBank.find_by_reseller(reseller_id)
        
        if bank_details:
            try:
                bank_details.bankname = bank_json.get("bankname") or bank_details.bankname
                bank_details.accountname = bank_json.get("accountname") or bank_details.accountname
                bank_details.accountnumber = bank_json.get("accountnumber") or bank_details.accountnumber
                bank_details.accounttype = bank_json.get("accounttype") or bank_details.accounttype
            except:
                return {"message": gettext("bank_bad_parameter")}, HTTPStatus.BAD_REQUEST
        try:
            bank_details.save_to_db()
            return reseller_bank_schema.dump(bank_details), HTTPStatus.OK
        except:
            traceback.print_exc()
            bank_details.delete_from_db()
            return {"message": gettext("bank_update_error")}, HTTPStatus.INTERNAL_SERVER_ERROR    
            
        
    @classmethod
    @jwt_required
    def delete(cls):
        reseller_id = get_jwt_identity()
        
        bank_details = ResellerBank.find_by_reseller(reseller_id)
        if bank_details:
            try:
                bank_details.delete_from_db()
                return {"message": gettext("bank_deleted")}, HTTPStatus.OK
            except:
                traceback.print_exc()
                return {"message": gettext("bank_delete_error")}, HTTPStatus.INTERNAL_SERVER_ERROR 
        return {"message": gettext("bank_not_found")}, HTTPStatus.NOT_FOUND  