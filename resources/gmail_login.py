import requests
from flask import g, request, url_for, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token

from oauth import google

from models.user import ResellerModel


class GmailLoginResource(Resource):
    
    @classmethod
    def get(cls):
        return google.authorize(url_for("gmail.authorize", _external=True))
    

class GmailAuthorizeResource(Resource):
    
    @classmethod
    def get(cls):
        
        resp = google.authorized_response()
        if resp is None or resp.get('access_token') is None:
            error_response = {
                "error": request.args["error"],
                "error_description": request.args["error_description"]
            }
            return error_response
        g.access_token = resp['access_token']
        gmail_user = google.get("userinfo")
        reseller_email = gmail_user.data["email"]
        ip_address = request.remote_addr
        
        reseller = ResellerModel.find_by_email(reseller_email)
        if not reseller:
            reseller = ResellerModel(firstname=gmail_user.data["given_name"], lastname=gmail_user.data["family_name"], 
                                     email=reseller_email, password=None, ip_address=ip_address)
            reseller.save_to_db()
        access_token = create_access_token(reseller.id, fresh=True)
        refresh_token = create_refresh_token(reseller.id)
        
        
        return {"reseller_access_token": access_token, "reseller_refresh_token": refresh_token}