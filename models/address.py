from db import db
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid5


class SubadminAddressModel(db.Model):
    __tablename__ = 'subadminaddress'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid5().hex)
    street = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(bd.String(12), nullable=False)
    
    subadmin_id = db.Column(UUID(as_uuid=True), db.ForeignKey("subadmin.id"), nullable=False)