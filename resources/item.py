import traceback, os
from flask_restful import Resource, request
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from flask_uploads import UploadNotAllowed
from marshmallow import ValidationError
from http import HTTPStatus
from webargs import fields
from webargs.flaskparser import use_kwargs

from extension import cache, limiter
from libs.strings import gettext
from libs import img_helper
from libs.utils import clear_cache

from models.item import ItemModel, SharedItemModel
from models.image import ImageModel
from models.user import SupplierModel, ResellerModel, SubAdminModel
from schemas.item import ItemSchema, SharedItemSchema, ItemPaginationSchema, SharedItemPaginationSchema
from schemas.image import ImageSchema, ImageModelSchema

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)
item_pagination_schema = ItemPaginationSchema()
image_schema = ImageSchema()



"""
Item Resource is a supplier resource
"""
class SupplierItemResource(Resource):
    
    @classmethod
    @jwt_required
    def post(cls, supplier_id: str, name: str):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            if SupplierModel.find_by_id(supplier_id):
                try:
                    item_json = request.get_json()
                    item_json["name"] = name
                    item_json["supplier_id"] = supplier_id
                    item = item_schema.load(item_json)
                except ValidationError as err:
                    return err.messages, HTTPStatus.BAD_REQUEST
                    
                if ItemModel.find_by_name(name):
                    return {"message": gettext("item_already_exist")}, HTTPStatus.BAD_REQUEST
                    
                try:
                    item.save_to_db()
                    clear_cache("/items")
                    return {"message": gettext("item_created")}, HTTPStatus.CREATED
                except:
                    traceback.print_exc()
                    item.delete_from_db()
                    return {"message": gettext("item_creation_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
            
        
        
        
    @classmethod
    @jwt_required
    def get(cls, supplier_id: str, name: str):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            item = ItemModel.find_by_name(name)
            if item:
                return item_schema.dump(item), HTTPStatus.OK
            return {"message": gettext("item_not_found")}, HTTPStatus.NOT_FOUND
    
    @classmethod
    @jwt_required
    def patch(cls, supplier_id: str, name: str):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            item_json = request.get_json()
            item_json["name"] = name
            
            if SupplierModel.find_by_id(supplier_id):
                item = ItemModel.find_by_name(name)
            
                if item:
                    item.name = item_json.get("name") or item.name
                    item.price = item_json.get("price") or item.price
                    item.description = item_json.get("description") or item.description
                    if item_json.get("quantity") is not None:
                        item.quantity = item.quantity + item_json.get("quantity")
        
                        
                    try:
                        item.save_to_db()
                        clear_cache("/items")
                        return {"message": gettext("item_updated")}, HTTPStatus.OK
                    except:
                        traceback.print_exc()
                        item.delete_from_db()
                        return {"message": gettext("item_update_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
                else:
                    return {"message": gettext("item_bad_parameter")}, HTTPStatus.BAD_REQUEST
                
            
    @classmethod
    @jwt_required
    def delete(cls, supplier_id: str, name: str):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            if SupplierModel.find_by_id(supplier_id):
                item = ItemModel.find_by_name(name)
                if item:
                    try:
                        item.delete_from_db()
                        return {"message": gettext("item_deleted")}, HTTPStatus.OK
                    except:
                        traceback.print_exc()
                        return {"message": gettext("item_delete_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
        


class SupplierItemListResource(Resource):
    
    decorators = [limiter.limit('10 per minute', methods=['GET'], error_message='Too Many Requests')]
    @classmethod
    @jwt_required
    @use_kwargs(
        {
            "keyword": fields.Str(missing=""), 
            "page": fields.Int(missing=1), 
            "per_page": fields.Int(missing=10),
            "sort": fields.Str(missing="created_at"),
            "order": fields.Str(missing="desc")
        }
    )
    @cache.cached(timeout=60, query_string=True)
    def get(cls, supplier_id:str, keyword: str, page: int, per_page: int, sort: str, order: str):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
    
        
            if sort not in ['created_at', 'name']:
                sort = 'created_at'
            
            if order not in ['asc', 'desc']:
                order = 'desc'
            
            
            if not SupplierModel.find_by_id(supplier_id):
                return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
            paginated_item = ItemModel.find_by_supplier(supplier_id, page, per_page, sort, order)
            print(paginated_item.__dict__)
            return item_pagination_schema.dump(paginated_item), HTTPStatus.OK
            
        
    
            
class ItemImageUploadResource(Resource):
    
    @classmethod
    @jwt_required
    def post(cls, supplier_id:str, name: str):
        
        data = image_schema.load(request.files)
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            if SupplierModel.find_by_id(supplier_id):
                item = ItemModel.find_by_name(name)
                item.image_count += 1
                item.file_image_count += 1
                count = item.file_image_count
                folder = f"{supplier_id}/{item.id}"
                filename = f"{item.id}_{count}"
                item_image_path = img_helper.find_image_any_format(filename, folder)
                
                try:
                    extension = img_helper.get_extension(data["image"])
                    image_name = filename + extension
                    image_path = img_helper.save_image(data["image"], folder=folder, name=image_name)
                    image = ImageModel(image_name, item.id)
                    try:
                        image.save_to_db()
                        item.image_count = count
                        item.save_to_db()
                        return {"message": gettext("item_image_uploaded")}, HTTPStatus.OK
                    except:
                        traceback.print_exc()
                        return {"message": gettext("item_image_save_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
                except UploadNotAllowed:
                    return {"message": gettext("item_image_illegal_extension").format(extension)}, HTTPStatus.BAD_REQUEST
                
        
            
class ItemImageDeleteResource(Resource):
    
    @classmethod
    @jwt_required
    def delete(cls, supplier_id: str, filename: str):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            if SupplierModel.find_by_id(supplier_id):
                image = ImageModel.find_by_name(filename)
                item_id = image.item_id
                folder = f"{supplier_id}/{item_id}"
                if not img_helper.is_filename_safe(filename):
                    return {"message": gettext("item_image_illegal_filename").format(filename)}, HTTPStatus.BAD_REQUEST
                try:
                    item = ItemModel.find_by_id(str(item_id))
                    os.remove(img_helper.get_path(filename, folder=folder))
                    item.image_count -= 1
                    try:
                        item.save_to_db()
                        image.delete_from_db()
                    except:
                        traceback.print_exc()
                        return {"message": gettext("item_update_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
                    return {"message": gettext("item_image_deleted")}, HTTPStatus.OK
                except FileNotFoundError:
                    return {"message": gettext("item_image_not_found")}, HTTPStatus.NOT_FOUND
                except:
                    traceback.print_exc()
                    return {"message": gettext("item_image_delete_failed")}, HTTPStatus.INTERNAL_SERVER_ERROR
            
            
            
"""
Reseller Endpoint
"""

class ResellerItemResource(Resource):
    
    @classmethod
    @jwt_optional
    def get(cls, name: str):
        
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), HTTPStatus.OK
        return {"message": gettext("item_not_found")}, HTTPStatus.NOT_FOUND
    
    
    
class ResellerItemListResource(Resource):
    
    decorators = [limiter.limit('10 per minute', methods=['GET'], error_message='Too Many Requests')]
    @classmethod
    @jwt_optional
    @use_kwargs(
        {
            "keyword": fields.Str(missing=""), 
            "page": fields.Int(missing=1), 
            "per_page": fields.Int(missing=10),
            "sort": fields.Str(missing="created_at"),
            "order": fields.Str(missing="desc")
        }
    )
    @cache.cached(timeout=60, query_string=True)
    def get(cls,keyword: str, page: int, per_page: int, sort: str, order: str):
        
        if sort not in ['created_at', 'name']:
            sort = 'created_at'
            
        if order not in ['asc', 'desc']:
            order = 'desc'
        
        paginated_item = ItemModel.find_all(keyword, page, per_page, sort, order)
        return item_pagination_schema.dump(paginated_item), HTTPStatus.OK         
    
    
    

class SharedItemResource(Resource):
    
    @classmethod
    @jwt_required
    def post(cls, name: str):
        
        reseller_id = get_jwt_identity()
        reseller = ResellerModel.find_by_id(reseller_id)
        
        if reseller:
            item = ItemModel.find_by_name(name)
            if item:
                shared_item = SharedItemModel(reseller_id, item=item)
                

                    
                