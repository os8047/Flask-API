from db import db

from uuid import uuid1
from sqlalchemy.dialects.postgresql import UUID


class ImageModel(db.Model):
    __tablename__ = 'image'
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    item_id = db.Column(UUID(as_uuid=True), db.ForeignKey("item.id"), nullable=False)
    
    def __init__(self, name: str, item_id: int, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid1().hex
        self.name = name
        self.item_id = item_id
        
    @classmethod
    def find_by_name(cls, name: str) -> "ImageModel":
        return cls.query.filter_by(name=name).first()
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    
         
         
    