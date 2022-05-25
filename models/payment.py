from db import db
from uuid import uuid1

from sqlalchemy.dialects.postgresql import UUID

class TimeMixin(object):
    created_at = db.Column(db.DateTime(), server_default=db.func.now())


class PaymentModel(db.Model, TimeMixin):
    __tablename__ = 'payment'
    
    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid1().hex)
    amount = db.Column(db.Float(precision=2), nullable=False)
    reference = db.Column(db.String(100))
    
    order_id = db.Column(UUID(as_uuid=False), db.ForeignKey("order.id"), nullable=False)

    @classmethod
    def find_by_order_id(cls, order_id: str) -> "PaymentModel":
        return cls.query.filter_by(order_id=order_id).order_by(db.desc(cls.created_at)).first()
    
    @classmethod
    def find_by_reference(cls, reference: str) -> "PaymentModel":
        return cls.query.filter_by(reference=reference).first()
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()    