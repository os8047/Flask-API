from db import db

from uuid import uuid1
from sqlalchemy.dialects.postgresql import UUID
from typing import List

class Category(db.Model):
    __tablename__ = 'category'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True)
    
    items = db.relationship('ItemModel', back_populates='category', lazy="dynamic")
    
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid1().hex
        self.name = name
        
    @classmethod
    def find_by_id(cls, _id: str) -> "Category":
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def find_by_name(cls, name: str) -> "Category":
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def find_all(cls) -> List["Category"]:
        return cls.query.all()
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    
            
    