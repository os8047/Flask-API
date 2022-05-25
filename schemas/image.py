from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from werkzeug.datastructures import FileStorage

from extension import ma


class FileStorageField(fields.Field):
    default_error_messages = {
        "invalid": "not a valid image"
    }
    def _deserialize(self, value, attr, data, partial) -> FileStorage:
        if value is None:
            return None
        
        if not isinstance(value, FileStorage):
            return self.fail("invalid")
        
        return value
    
class ImageSchema(Schema):
    image = FileStorageField(required=True)
    

class ImageModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        dump_only = ("id",)
        include_fk = True
        load_instance = True
        
        