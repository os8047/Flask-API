import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_restful import Api
from marshmallow import ValidationError
from flask_uploads import configure_uploads, patch_request_class
from dotenv import load_dotenv
from http import HTTPStatus

from resources.bank import SupplierBankResource, ResellerBankResource
from resources.category import CategoryResource, CategoryListResource
from resources.confirmation import SubAdminConfirmation, SubAminConfirmationByUser, ResellerConfirmation, ResellerConfirmationByUser
from resources.gmail_login import GmailLoginResource, GmailAuthorizeResource
from resources.item import (
    SupplierItemResource, 
    SupplierItemListResource,
    ResellerItemResource,
    ResellerItemListResource,
    ItemImageUploadResource, 
    ItemImageDeleteResource
)
from resources.order import (
    OrderCreationResource, 
    OrderPaymentResource,
    OrderCancellationResource,
    SupplierOrderResource, 
    SupplierOrderListResource, 
    ResellerOrderResource, 
    ResellerOrderListResource
)

from resources.payment import PaymentResource
from resources.user import (
    SupplierRegister, 
    Supplier, 
    RefreshToken,
    ResellerRegister,
    ResellerLogin,
    ResellerLogout,
    Reseller,
    SubAdminRegisterResource,
    SubAdminLoginResource,
    SubAdminLogoutResource,
    SubAdminResource,
    SupplierAddToSubAdmin
)

from db import db
from extension import ma, jwt, cache, limiter
from blacklist import BLACKLIST
from default_config import DefaultConfig
from oauth import oauth

from libs.img_helper import IMAGE_SET


app = Flask(__name__)
load_dotenv('.env', verbose=True)
app.config.from_object(DefaultConfig)
app.config.from_envvar('APPLICATION_SETTINGS')
configure_uploads(app, IMAGE_SET)
patch_request_class(app, 5 * 1024 * 1024)
db.init_app(app)
jwt.init_app(app)
ma.init_app(app)
oauth.init_app(app)
api = Api(app)
migrate = Migrate(app, db)
cache.init_app(app)
limiter.init_app(app)

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST

#This following methods is a callback that customize jwt response and error messages
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), HTTPStatus.UNAUTHORIZED


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        HTTPStatus.UNAUTHORIZED,
    )
    
@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        HTTPStatus.UNAUTHORIZED,
    )
    
@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        HTTPStatus.UNAUTHORIZED,
    )
    
@jwt.revoked_token_loader
def revoked_token_callback():
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        HTTPStatus.UNAUTHORIZED,
    )
    
# end of callback methods 

@app.errorhandler(ValidationError)
def handle_marshmallow_error(err):
    return jsonify(err.messages), HTTPStatus.BAD_REQUEST

with app.app_context():
    from models.category import Category
    

@limiter.request_filter
    def ip_whitelist():
        return request.remote_addr == '127.0.0.1'
    

@app.before_first_request
def create_tables():
    #db.drop_all()
    db.create_all()


"""
private endpoint
"""
api.add_resource(SupplierAddToSubAdmin, '/admin/add')

"""
Subadmin account resources
"""
api.add_resource(SubAdminRegisterResource, '/subadmin/register')
api.add_resource(SubAdminConfirmation, '/subadmin/activate/<string:confirmation_id>')
api.add_resource(SubAminConfirmationByUser, '/subadmin/activate/<string:subadmin_id>')
api.add_resource(SubAdminLoginResource, '/subadmin/login')
api.add_resource(SubAdminLogoutResource, '/subadmin/logout')
api.add_resource(SubAdminResource, '/subadmin')


"""
Supplier account resources 
"""
api.add_resource(SupplierRegister, '/supplier/register')
api.add_resource(Supplier, '/subadmin/supplier/<string:supplier_id>')
api.add_resource(SupplierBankResource, '/supplier/<string:supplier_id>/bank_details')

"""
Reseller account resources 
"""

api.add_resource(ResellerRegister, '/reseller/register')
api.add_resource(ResellerConfirmation, '/reseller/activate/<string:confirmation_id>')
api.add_resource(ResellerConfirmationByUser, '/reseller/activate/<string:reseller_id>')
api.add_resource(ResellerLogin, '/reseller/login')
api.add_resource(ResellerLogout, '/reseller/logout')
api.add_resource(Reseller, '/reseller')
api.add_resource(ResellerBankResource, '/reseller/bank_details')

"""
Reseller gmail login and register
"""
api.add_resource(GmailLoginResource, '/login/gmail')
api.add_resource(GmailAuthorizeResource, '/login/gmail/authorized', endpoint='gmail.authorize')

"""
Category resources
"""
api.add_resource(CategoryResource, '/category/<string:name>')
api.add_resource(CategoryListResource, '/categories')
api.add_resource(RefreshToken, '/refresh_token')

"""
Supplier Item resources
"""
api.add_resource(SupplierItemResource, '/<string:supplier_id>/item/<string:name>')
api.add_resource(SupplierItemListResource, '/<string:supplier_id>/items')
api.add_resource(ItemImageUploadResource, '/<string:supplier_id>/item/upload/<string:name>')
api.add_resource(ItemImageDeleteResource, '/<string:supplier_id>/item/delete/<string:filename>')

"""
Reseller Item resources
"""
api.add_resource(ResellerItemResource, '/item/<string:name>')
api.add_resource(ResellerItemListResource, '/items')

"""
Supplier order resource
"""
api.add_resource(SupplierOrderResource, '/<string:supplier_id>/order/<string:order_id>')
api.add_resource(SupplierOrderListResource, '/<string:supplier_id>/orders')


"""
Reseller order Resource
"""
api.add_resource(OrderCreationResource, '/order/create')
api.add_resource(OrderPaymentResource, '/order/payment/<string:order_id>')
api.add_resource(OrderCancellationResource, '/order/<string:order_id>/cancel')
api.add_resource(ResellerOrderResource, '/order/<string:order_id>')
api.add_resource(ResellerOrderListResource, '/orders')

"""
Payment Resource
"""
api.add_resource(PaymentResource, '/payment')

if __name__ == "__main__":
    app.run(port=5000, debug=True)