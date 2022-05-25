from db import db

from flask_sqlalchemy import Pagination
from uuid import uuid4
from sqlalchemy import or_, asc, desc, and_
from sqlalchemy.dialects.postgresql import UUID

from models.image import ImageModel


class TimeMixin(object):
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())


class SharedItemModel(db.Model, TimeMixin):
    __tablename__ = 'shareditems'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid4().hex)
    reseller_id = db.Column(UUID(as_uuid=True), db.ForeignKey("reseller.id"), nullable=False)
    item_id = db.Column(UUID(as_uuid=True), db.ForeignKey("item.id"), nullable=False)
    asking_price = db.Column(db.Float(precision=3))
    
    item = db.relationship("ItemModel", backref=db.backref("shareditems", lazy=True))
        
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    

class ItemModel(db.Model, TimeMixin):
    __tablename__ = 'item'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    price = db.Column(db.Float(precision=3), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_count = db.Column(db.Integer)
    file_image_count = db.Column(db.Integer)#This image count is for image file name
    
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('category.id'), nullable=False)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey("supplier.id"), nullable=False)
    
    category = db.relationship("Category")
    
    item_images = db.relationship("ImageModel", backref="item", lazy="dynamic", cascade="all, delete-orphan")
    
    def __init__(self, supplier_id: str, category_id: int, name: str, price: float, description: int, **kwargs):
        super().__init__(**kwargs)
        self.supplier_id = supplier_id
        self.category_id = category_id
        self.id = uuid4().hex
        self.name = name
        self.price = price
        self.description = description
        self.image_count = 0
        self.file_image_count = 0
    
    @classmethod
    def find_by_id(cls, _id: str) -> "ItemModel":
        return cls.query.filter_by(id=_id).first()
        
    @classmethod
    def find_by_name(cls, name: str) -> "ItemModel":
        return cls.query.filter_by(name=name).first()
        
    @classmethod
    def find_by_supplier(cls, supplier_id: str, page: int, per_page: int, sort: str, order: str) -> "Pagination":
        
        if order == 'asc':
            sort_logic = asc(getattr(cls, sort))
        else:
            sort_logic = desc(getattr(cls, sort))
            
        return cls.query.filter_by(supplier_id=supplier_id, quantity>0). \
            order_by(sort_logic).paginate(page=page, per_page=per_page)
    
    @classmethod
    def find_all(cls, keyword: str, page: int, per_page: int, sort: str, order: str) -> "Pagination":
        keyword = "%{}%".format(keyword)
        
        if order == 'asc':
            sort_logic = asc(getattr(cls, sort))
        else:
            sort_logic = desc(getattr(cls, sort))
            
        return cls.query.filter(
            and_(or_(cls.name.ilike(keyword), 
                cls.description.ilike(keyword)), quantity>0)). \
                    order_by(sort_logic).paginate(page=page, per_page=per_page)
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    
    
