import traceback
from flask_restful import Resource, request
from marshmallow import ValidationError
from http import HTTPStatus

from libs.strings import gettext

from models.category import Category
from schemas.category import CategorySchema

category_schema = CategorySchema()
category_list_schema = CategorySchema(many=True)


class CategoryResource(Resource):
    
    """
    This post and delete endpoint should not be exposed to the internet
    """
    @classmethod
    def post(cls, name: str):
        
        try:
            data_json = {}
            data_json["name"] = name
            category = category_schema.load(data_json)
        except ValidationError as err:
            return err.messages, HTTPStatus.BAD_REQUEST
        
        if Category.find_by_name(category.name):
            return {"message": gettext("category_already_exist")}, HTTPStatus.BAD_REQUEST
        
        try:
            category.save_to_db()
            return {"message": gettext("category_created")}, HTTPStatus.CREATED
        except:
            traceback.print_exc()
            category.delete_from_db()
            return {"message": gettext("category_creation_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
        
    @classmethod
    def get(cls, name: str):
        
        category = Category.find_by_name(name)
        if category:
            return category_schema.dump(category), HTTPStatus.OK
        return {"message": gettext("category_not_found")}, HTTPStatus.NOT_FOUND
    
    @classmethod
    def delete(cls, name: str):
        
        category = Category.find_by_name(name)
        if category:
            try:
                category.delete_from_db()
                return {"message": gettext("category_deleted")}, HTTPStatus.OK
            except:
                traceback.print_exc()
                return {"message": gettext("category_deletion_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
            
            

class CategoryListResource(Resource):
    @classmethod
    def get(cls):
        return {"categories": category_list_schema.dump(Category.find_all())}, HTTPStatus.OK