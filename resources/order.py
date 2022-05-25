import traceback, os
from collections import Counter
from flask import make_response
from flask_restful import Resource, request
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from marshmallow import ValidationError
from http import HTTPStatus
from webargs import fields
from webargs.flaskparser import use_kwargs

from libs.strings import gettext
from libs.utils import clear_cache

from models.order import OrderModel, ItemsInOrder
from models.item import ItemModel
from models.payment import PaymentModel
from models.user import SupplierModel, ResellerModel, BuyerModel, SubAdminModel
from schemas.order import OrderSchema, OrderPaginationSchema
from transaction import transaction

order_schema = OrderSchema()
order_list_schema = OrderSchema(many=True)
order_pagination_schema = OrderPaginationSchema()


class SupplierOrderResource(Resource):
    
    @classmethod
    @jwt_required
    def get(cls, supplier_id, order_id):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
            
            if SupplierModel.find_by_id(supplier_id):
                order = OrderModel.find_by_id(order_id)
                if order:
                    return order_schema.dump(order), HTTPStatus.OK
                return {"message": gettext("order_not_found")}, HTTPStatus.NOT_FOUND
                   
                    
        
        
    """
    This delete resource is for testing
    """
    @classmethod
    @jwt_required
    def delete(cls, supplier_id, order_id):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
        
            if SupplierModel.find_by_id(supplier_id):
                order = OrderModel.find_by_id(order_id)
                if order:
                        try:
                            order.delete_from_db()
                            return {"message": gettext("order_deleted")}, HTTPStatus.OK
                        except:
                            traceback.print_exc()
                            return {"message": gettext("order_delete_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
                else:
                    return {"message": gettext("order_not_found")}, HTTPStatus.NOT_FOUND



class SupplierOrderListResource(Resource):
    
    @classmethod
    @jwt_required
    @use_kwargs(
        {
            "page": fields.Int(missing=1), 
            "per_page": fields.Int(missing=10),
            "sort": fields.Str(missing="created_at"),
            "order": fields.Str(missing="desc")
        }
    )
    def get(cls, supplier_id: str, page: int, per_page: int, sort: str, order: str):
        
        subadmin_id = get_jwt_identity()
        subadmin = SubAdminModel.find_by_id(subadmin_id)
        supplier_ids = []
        if subadmin:
            for supplier in subadmin.suppliers:
                supplier_ids.append(supplier.id)
            if supplier_id not in supplier_ids:
                return {"message": gettext("account_access_denied")}, HTTPStatus.FORBIDDEN
        
            if sort not in ['created_at', 'status']:
                sort = 'created_at'
            
            if order not in ['asc', 'desc']:
                order = 'desc'
                
            pagination_order = OrderModel.find_by_supplier_id(supplier_id, page, per_page, sort, order)
            return order_pagination_schema.dump(pagination_order), HTTPStatus.OK
        
        
        
class ResellerOrderResource(Resource):
    
    @classmethod
    @jwt_required
    def get(cls, order_id):
        
        reseller_id = get_jwt_identity() 
            
        if ResellerModel.find_by_id(reseller_id):
            order = OrderModel.find_by_id(order_id)
            if order:
                if order.status != "paid" and order.expired:
                    status = "cancelled"
                    order.set_status(status)
                return order_schema.dump(order), HTTPStatus.OK
              
            return {"message": gettext("order_not_found")}, HTTPStatus.NOT_FOUND
        return {"message": gettext("access_forbidden")}, HTTPStatus.BAD_REQUEST



class ResellerOrderListResource(Resource):
    
    @classmethod
    @jwt_required
    @use_kwargs(
        {
            "page": fields.Int(missing=1), 
            "per_page": fields.Int(missing=10),
            "sort": fields.Str(missing="created_at"),
            "order": fields.Str(missing="desc")
        }
    )
    def get(cls, page: int, per_page: int, sort: str, order: str):
        
        reseller_id = get_jwt_identity()
        if ResellerModel.find_by_id(reseller_id):
            if sort not in ['created_at', 'status']:
                sort = 'created_at'
                
            if order not in ['asc', 'desc']:
                order = 'desc'
                    
            pagination_order = OrderModel.find_by_reseller_id(reseller_id, page, per_page, sort, order)
            return order_pagination_schema.dump(pagination_order), HTTPStatus.OK
        return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
        
        
        


class OrderCreationResource(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        
        reseller_id = get_jwt_identity()
        item_data = request.get_json() #list of item ids
        supplier_id = item_data["supplier_id"]
        items = []
        item_id_quantity = Counter(item_data["item_ids"])
        buyerfirstname = item_data["buyerfirstname"]
        buyerlastname = item_data["buyerlastname"]
        buyeraddress = item_data["buyeraddress"]
        buyercity = item_data["buyercity"]
        buyerstate = item_data["buyerstate"]
        
        
        
        buyer = BuyerModel.find_buyer(buyerfirstname, buyerlastname, buyeraddress, buyercity, buyerstate)
        if not buyer:
            buyer = BuyerModel(firstname=buyerfirstname, lastname=buyerlastname, address=buyeraddress, city=buyercity, state=buyerstate, ip_address=request.remote_addr)
            try:
                buyer.save_to_db()
            except:
                traceback.print_exc()
        
        for _id, count in item_id_quantity.most_common():
            item = ItemModel.find_by_id(_id)
            if not item:
                return {"message": gettext("order_item_not_found")}, HTTPStatus.NOT_FOUND
            
            if not item.quantity >= count:
                return {"message": "Item {} is remaining {}".format(item.name, item.quantity)}, HTTPStatus.NOT_ACCEPTABLE
            
            item.quantity -= count
            item_in_order = ItemsInOrder(item_id=_id, quantity=count, margin=item_data["margin"])
            item_in_order.save_to_db()
            item_in_order.set_amount()
            item_in_order.set_total_amount()
            items.append(item_in_order)
            
            print(item_in_order.amount)
            
        order = OrderModel(status="pending", supplier_id=supplier_id, reseller_id=reseller_id, items=items, buyer_id=buyer.id)
        
        try:
            order.save_to_db()
            clear_cache('/items')
            order.set_reseller_amount()
            order.set_supplier_amount()
            payment = PaymentModel(order_id=order.id, amount=order.reseller_amount)
            try:
                payment.save_to_db()
            except:
                traceback.print_exc()
            print(order.reseller_amount)
            return {"message": gettext("order_created"), "order": order_schema.dump(order)}, HTTPStatus.OK
        except:
            traceback.print_exc()
            return{"message": gettext("order_creation_error")}, HTTPStatus.INTERNAL_SERVER_ERROR
        
        


class OrderPaymentResource(Resource):
    
    @classmethod
    def post(cls, order_id: str):
        
        data = request.get_json()
        order = OrderModel.find_by_id(order_id) 
        
        if order:
            if order.expired:
                return {"message": gettext("link_expired")}
            
            buyer = BuyerModel.find_by_id(str(order.buyer_id))
            phonenumber = buyer.phonenumber
            email = buyer.email
            if email is None:
                buyer.set_email(data["email"])
            if phonenumber is None:
                buyer.set_phone(data["phonenumber"])
            
            email = buyer.email        
            init = transaction.initialize(email=email, amount=order.reseller_amount, metadata=order.metadatas)
            reference = init[3]["reference"]
            print(reference)
            payment = PaymentModel.find_by_order_id(order_id)
                    
            if payment:
                payment.reference = reference
                print(payment.reference)
                try:
                    payment.save_to_db()
                except:
                    traceback.print_exc()
                    return {"message": "error updating payment"}, HTTPStatus.INTERNAL_SERVER_ERROR
                        
                    
                return init, HTTPStatus.OK
            else:
                return {"message": gettext("order_not_found")}, HTTPStatus.NOT_FOUND
            


class OrderCancellationResource(Resource):
    
    @classmethod
    @jwt_required
    def post(cls, order_id: str):
        order = OrderModel.find_by_id(order_id)
        if order:
            if order.status == "pending" or order.status == "unpaid":
                order.status = "cancelled"
                for item in order.items:
                    item.item.quantity += item.quantity
                try:
                    order.save_to_db()
                except:
                    traceback.print_exc()
                    return {"message": "error cancelling order"}, HTTPStatus.INTERNAL_SERVER_ERROR
                return {"message": "order_cancelled"}, HTTPStatus.OK
            elif order.status == "paid":
                return {"message": "Can not cancel order, payment has been made already"}, HTTPStatus.BAD_REQUEST
        else:
            return {"message": gettext("order_not_found")}, HTTPStatus.NOT_FOUND