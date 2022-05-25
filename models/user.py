from db import db

from flask import request, url_for
from requests import Response, post
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy import or_, and_
from uuid import uuid1

from libs.mailgun import MailGun
from models.confirmation import SubAdminConfirmationModel, ResellerConfirmationModel
        
  
class TimeMixin(object):
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    
class RemoteAddressMixin(object):
    ip_address = db.Column(db.String(15), nullable=False)
    
    
class SupplierModel(db.Model, TimeMixin, RemoteAddressMixin):
    __tablename__ = 'supplier'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid1().hex)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    address1 = db.Column(db.Text, nullable=False)
    address2 = db.Column(db.Text)
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(15), nullable=False)
    zipcode = db.Column(db.String(20), nullable=False)
    businessregistered = db.Column(db.Boolean, nullable=False)
    cacnumber = db.Column(db.BigInteger, unique=True, nullable=False)
    maincategory = db.Column(db.String(40), nullable=False)
    businesstype = db.Column(db.String(40), nullable=False)
    pricerange = db.Column(db.String(40), nullable=False)
    averagestock = db.Column(db.String(40), nullable=False)
    saleschannel = db.Column(db.String(40), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    subadmin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subadmin.id'))

    subadmin = db.relationship('SubAdminModel', back_populates='suppliers', uselist=False)
    bankaccount = db.relationship('SupplierBank', backref='supplier', lazy=True, uselist=False, cascade="all, delete-orphan")
    items = db.relationship('ItemModel', backref='supplier', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('OrderModel', back_populates='supplier')
    
    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address   
    
    @classmethod
    def find_by_name(cls, name: str) -> 'SupplierModel':
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def find_by_email(cls, email:str) -> 'SupplierModel':
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_id(cls, _id: int) -> 'SupplierModel':
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def find_by_cacnumber(cls, cacnumber: int) -> 'SupplierModel':
        return cls.query.filter_by(cacnumber=cacnumber).first()


    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit() 

         
    
class ResellerModel(db.Model, TimeMixin, RemoteAddressMixin):
    __tablename__ = 'reseller'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid1().hex)
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120))
    
    bankaccount = db.relationship('ResellerBank', backref='reseller', lazy=True, uselist=False, cascade="all, delete-orphan")
    confirmations = db.relationship('ResellerConfirmationModel', backref='reseller', lazy="dynamic", cascade="all, delete-orphan")
    shareditems = db.relationship('SharedItemModel', backref='reseller', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('OrderModel', back_populates='reseller')
    
    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address
    
    @classmethod
    def find_by_id(cls, _id: UUID) -> "ResellerModel":
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def find_by_email(cls, email: str) -> "ResellerModel":
        return cls.query.filter_by(email=email).first()
    
    @property
    def most_recent_confirmation(self) -> "ResellerConfirmationModel":
        return self.confirmations.order_by(db.desc(ResellerConfirmationModel.expire_at)).first()
    
    def send_confirmation_email(self):
        link = request.url_root[:-1] + url_for("resellerconfirmation", confirmation_id=self.most_recent_confirmation.id)
        subject = "Registration confirmation for your TruvShop account"
        text = f"Please follow this link to confirm registration, {link}"
        html = None #For now
        return MailGun.send_email(self.email, subject, text, html)
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
        
        
        
class BuyerModel(db.Model, TimeMixin, RemoteAddressMixin):
    __tablename__ = 'buyer'

    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid1().hex)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(50))
    phonenumber = db.Column(db.String(11))
    
    orders = db.relationship('OrderModel', back_populates='buyer')
    
    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address
    
    def set_email(self, email) -> None:
        self.email = email
        self.save_to_db()
        
    def set_phone(self, phonenumber) -> None:
        self.phonenumber = phonenumber
        self.save_to_db()
        
    def set_ip_address(self, ip_address) -> None:
        self.ip_address = ip_address
        self.save_to_db()
    
    @classmethod
    def find_by_id(cls, _id) -> "BuyerModel":
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def find_by_email(cls, email) -> "BuyerModel":
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_buyer(cls, firstname, lastname, address, city, state) -> "BuyerModel":
        return cls.query.filter(and_(cls.firstname==firstname, cls.lastname==lastname), 
                                and_(cls.address==address, cls.city==city), cls.state==state).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
        

        

class SubAdminModel(db.Model, TimeMixin, RemoteAddressMixin):
    __tablename__ = 'subadmin'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid1().hex)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    street = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(12), nullable=False)
    zipcode = db.Column(db.String(5), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    
    suppliers = db.relationship('SupplierModel', back_populates='subadmin')
    confirmations = db.relationship('SubAdminConfirmationModel', backref='subadmin', lazy="dynamic", cascade="all, delete-orphan")
    
    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address
    
    @validates('suppliers')
    def validate_supplier(self, key, address):
        if not len(address) < 10:
            raise ValueError("Cannot have more than 10 suppliers")
        return address
    
    @classmethod
    def find_by_id(cls, _id: str) -> "SubAdminModel":
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def find_by_email(cls, email: str) -> "SubAdminModel":
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_username(cls, username: str) -> "SubAdminModel":
        return cls.query.filter_by(username=username).first()
    
    @property
    def most_recent_confirmation(self) -> "SubAdminConfirmationModel":
        return self.confirmations.order_by(db.desc(SubAdminConfirmationModel.expire_at)).first()
    
    def send_confirmation_email(self):
        link = request.url_root[:-1] + url_for("subadminconfirmation", confirmation_id=self.most_recent_confirmation.id)
        subject = "Registration confirmation for your TruvShop subadmin account"
        text = f"Please follow this link to confirm registration, {link}"
        html = None #For now
        return MailGun.send_email(self.email, subject, text, html)
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
    