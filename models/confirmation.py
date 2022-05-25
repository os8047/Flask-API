from db import db

from uuid import uuid4
from typing import List
from time import time
from sqlalchemy.dialects.postgresql import UUID

CONFIRMATION_EXPIRATION_DELTA = 1800 #30 mins


class SubAdminConfirmationModel(db.Model):
    __tablename__ = 'subadminrconfirmation'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    
    subadmin_id = db.Column(UUID(as_uuid=True), db.ForeignKey("subadmin.id"), nullable=False)
    
    
    def __init__(self, subadmin_id: str, **kwargs):
        super().__init__(**kwargs)
        self.subadmin_id = subadmin_id
        self.id = uuid4().hex
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        
    @classmethod
    def find_all(cls, subadmin_id: str) -> List["SubAdminConfirmationModel"]:
        return cls.query.filter_by(subadmin_id=subadmin_id).all()
    
    @classmethod
    def find_by_id(cls, _id: str) -> "SubAdminConfirmationModel":
        return cls.query.filter_by(id=_id).first()
    
    @property
    def expired(self) -> bool:
        return time() > self.expire_at
    
    def force_to_expire(self) -> None:
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()  


class SupplierConfirmationModel(db.Model):
    __tablename__ = 'supplierconfirmation'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey("supplier.id"), nullable=False)
    
    
    def __init__(self, supplier_id: str, **kwargs):
        super().__init__(**kwargs)
        self.supplier_id = supplier_id
        self.id = uuid4().hex
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        
    @classmethod
    def find_all(cls, supplier_id: str) -> List["SupplierConfirmationModel"]:
        return cls.query.filter_by(supplier_id=supplier_id).all()
    
    @classmethod
    def find_by_id(cls, _id: str) -> "SupplierConfirmationModel":
        return cls.query.filter_by(id=_id).first()
    
    @property
    def expired(self) -> bool:
        return time() > self.expire_at
    
    def force_to_expire(self) -> None:
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    
    
    
class ResellerConfirmationModel(db.Model):
    __tablename__ = 'resellerconfirmation'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    
    reseller_id = db.Column(UUID(as_uuid=True), db.ForeignKey("reseller.id"), nullable=False)
    
    def __init__(self, reseller_id: str, **kwargs):
        super().__init__(**kwargs)
        self.reseller_id = reseller_id
        self.id = uuid4().hex
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        
    @classmethod
    def find_all(cls, reseller_id: str) -> List["ResellerConfirmationModel"]:
        return cls.query.filter_by(reseller_id=reseller_id).all()
    
    @classmethod
    def find_by_id(cls, _id: str) -> "ResellerConfirmationModel":
        return cls.query.filter_by(id=_id).first()
    
    @property
    def expired(self) -> bool:
        return time() > self.expire_at
    
    def force_to_expire(self) -> None:
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    