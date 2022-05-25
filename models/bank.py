from db import db

from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import or_, and_



class SupplierBank(db.Model):
    __tablename__ = 'supplierbankdetails'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    bankname = db.Column(db.String(120), nullable=False)
    accountname = db.Column(db.String(120), nullable=False)
    accountnumber = db.Column(db.String(10), nullable=False)
    accounttype = db.Column(db.String(10), nullable=False)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('supplier.id'), nullable=False)

    def __init__(self, supplier_id: str, bankname: str, accountname: str, accountnumber: str, accounttype: str, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex
        self.supplier_id = supplier_id
        self.bankname = bankname
        self.accountname = accountname
        self.accountnumber = accountnumber
        self.accounttype = accounttype
        
    @classmethod
    def find_by_supplier(cls, supplier_id: str) -> "SupplierBank":
        return cls.query.filter_by(supplier_id=supplier_id).first()
        
    @classmethod
    def find_bank_details(cls, bankname: str, accountnumber: str) -> "SupplierBank":
        return cls.query.filter(and_(bankname==bankname, accountnumber==accountnumber)).first()
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    
        
        
class ResellerBank(db.Model):
    __tablename__ = 'resellerbankdetails'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True)
    bankname = db.Column(db.String(120), nullable=False)
    accountname = db.Column(db.String(120), nullable=False)
    accountnumber = db.Column(db.String(10), unique=True, nullable=False)
    accounttype = db.Column(db.String(10), nullable=False)
    reseller_id = db.Column(UUID(as_uuid=True), db.ForeignKey("reseller.id"), nullable=False)
    
    def __init__(self, reseller_id: int, bankname: str, accountname: str, accountnumber: str, accounttype: str, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex
        self.reseller_id = reseller_id
        self.bankname = bankname
        self.accountname = accountname
        self.accountnumber = accountnumber
        self.accounttype = accounttype
        
    @classmethod
    def find_by_reseller(cls, reseller_id: str) -> "ResellerBank":
        return cls.query.filter_by(reseller_id=reseller_id).first()
        
    @classmethod
    def find_bank_details(cls, bankname: str, accountnumber: str) -> "ResellerBank":
        return cls.query.filter(and_(bankname==bankname, accountnumber==accountnumber)).first()
        
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    
    
    