from flask import Blueprint, Response, request
from models import UserModel
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask import jsonify
import traceback

auth = Blueprint('auth', __name__)

@auth.route('/auth/login', methods=['POST'])
def login():
    try:
        payload = request.json
        email = payload["email"]
        pw = payload["password"].encode("utf-8")
        
        user = UserModel.getUserForEmail(email)
        if user is None:
            return "Error: Auth failed", 401 # Don't want to say no email for that account for security reasons

        validated = user.login(pw)

        if validated:
            accessToken = create_access_token(identity = user.id)
            refreshToken = create_refresh_token(identity = user.id)
            response = jsonify({"status": "success"})
            set_access_cookies(response, accessToken)
            set_refresh_cookies(response, refreshToken)
            return response, 200
        else:
            return "Error: Auth failed", 401
    except Exception as e:
        traceback.print_exc()
        return f"Error: {e}", 400


@auth.route('/auth/logout', methods=["GET"])
@jwt_required
def logout():
    try:
        jwtId = get_jwt_identity()
        user = UserModel.getUserForId(jwtId)
        if user is None:
            return "Error: Not logged in", 401

        response = jsonify({'logout': True})
        unset_jwt_cookies(response)
        user.logout()
        return response, 200
    except Exception as e:
        traceback.print_exc()
        return f"Error: {e}", 400


# class TokenRefresh(Resource):
#     @jwt_refresh_token_required
#     def post(self):
#         try:
#             payload = request.get_json()
#             email = payload["email"]
#             user = UserModel.getUserForEmail(email)

#             # Make sure it is the correct user
#             jwtId = get_jwt_identity()
#             if user is None or not user.verify(jwtId):
#                 return "Error: Unauthortized", 401

#             accessToken = create_access_token(identity = jwtId)
#             response = jsonify({'refresh': True})
#             set_access_cookies(response, accessToken)
#             return response, 200
#         except Exception as e:
#             return f"Error: {e}", 400