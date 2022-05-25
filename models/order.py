import pypaystack

from db import db

from flask_sqlalchemy import Pagination
from uuid import uuid4
from sqlalchemy import asc, desc, or_
from sqlalchemy.dialects.postgresql import UUID
from time import time
from typing import List

EXPIRATION_TIME_DELTA = 172800 #2 days

CURRENCY = "naira"

class TimeMixin(object):
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    

class ItemsInOrder(db.Model):
    __tablename__ = 'items_in_order'

    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid4().hex)
    item_id = db.Column(UUID(as_uuid=False), db.ForeignKey("item.id"))
    order_id = db.Column(UUID(as_uuid=False), db.ForeignKey("order.id"))
    quantity = db.Column(db.Integer)
    amount = db.Column(db.BigInteger)
    total_amount = db.Column(db.BigInteger)
    margin = db.Column(db.Float(precision=3))
    
    def __init__(self, quantity: int, margin: int, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex
        self.quantity = quantity
        self.margin = margin


    item = db.relationship("ItemModel")
    order = db.relationship("OrderModel", back_populates="items")
    
    def set_amount(self) -> int:
        self.amount = int(self.quantity * (self.item.price * 100)) #returns initial amount in kobo of an item before margin is added
        self.save_to_db()
    
    def set_total_amount(self) -> int:
        self.total_amount = int(self.quantity * ((self.item.price * 100) + self.margin)) #returns total amount in kobo of the item after the margin is added
        self.save_to_db()
      
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    

class OrderModel(db.Model, TimeMixin):
    __tablename__ = 'order'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    reseller_amount = db.Column(db.Integer)
    supplier_amount = db.Column(db.Integer)
    status = db.Column(db.String(15), nullable=False)
    expire_at = db.Column(db.Integer, nullable=False, default=int(time())+EXPIRATION_TIME_DELTA)
     
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey("supplier.id"))
    reseller_id = db.Column(UUID(as_uuid=True), db.ForeignKey("reseller.id"))
    buyer_id = db.Column(UUID(as_uuid=True), db.ForeignKey("buyer.id"))
    
    supplier = db.relationship("SupplierModel", back_populates="orders")
    reseller = db.relationship("ResellerModel", back_populates="orders")
    buyer = db.relationship("BuyerModel", back_populates="orders")
    items = db.relationship("ItemsInOrder", back_populates="order")
    payment = db.relationship("PaymentModel", backref="order", lazy=True)
    
    def __init__(self, status: str, supplier_id: str, reseller_id: str, items: List, buyer_id: str, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex
        self.status = status
        self.supplier_id = supplier_id
        self.reseller_id = reseller_id
        self.items = items
        self.buyer_id = buyer_id
    
    
    @property
    def metadatas(self):
        """
        Generates a simple json representing this order, in the format of "5x chair, 2x table"
        """
        item_counts = [f"{i.quantity}x {i.item.name}" for i in self.items]
        meta_data_list = [
                {
                    "display_name": "Order ID",
                    "variable_name": "order_id",
                    "value": self.id
                },
                {
                    "display_name": "Cart Items",
                    "variable_name": "cart_items",
                    "value" : ",".join(item_counts)
                },
                {
                    "display_name": "Price",
                    "variable_name": "price",
                    "value" : self.reseller_amount
                }
            ]
        return {
            "custom_fields": meta_data_list
        }
    
    
    @classmethod
    def find_by_supplier_id(cls, supplier_id: str, page: int, per_page: int, sort: str, order: str) -> "Pagination":
        
        if order == 'asc':
            sort_logic = asc(getattr(cls, sort))
        else:
            sort_logic = desc(getattr(cls, sort))
            
        return cls.query.filter_by(supplier_id=supplier_id). \
            order_by(sort_logic).paginate(page=page, per_page=per_page)
            
    
    @classmethod
    def find_by_reseller_id(cls, reseller_id: str, page: int, per_page: int, sort: str, order: str) -> "Pagination":
        
        if order == 'asc':
            sort_logic = asc(getattr(cls, sort))
        else:
            sort_logic = desc(getattr(cls, sort))
            
        return cls.query.filter_by(reseller_id=reseller_id). \
            order_by(sort_logic).paginate(page=page, per_page=per_page)
 
    
    @property
    def expired(self) -> bool:
        return time() > self.expire_at
    
    def set_status(self, status: str):
        status_list = ("paid", "unpiad", "pending", "cancelled")
        if status in status_list:
            self.status = status
            self.save_to_db()
    
    def set_reseller_amount(self) -> None:
        self.reseller_amount = int(sum([itemdata.total_amount for itemdata in self.items]))
        self.save_to_db()
        
    def set_supplier_amount(self) -> None:
        self.supplier_amount = int(sum([itemdata.amount for itemdata in self.items]))
        self.save_to_db()
        
    @classmethod
    def find_by_id(cls, _id: str) -> "OrderModel":
        return cls.query.filter_by(id=_id).first()
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    

    