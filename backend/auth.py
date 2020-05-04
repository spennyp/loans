from flask import Blueprint, Response, request, jsonify
from models import UserModel
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from errors import *
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
            raise(UnauthorizedError)

        validated = user.login(pw)

        if validated:
            accessToken = create_access_token(identity = user.id)
            refreshToken = create_refresh_token(identity = user.id)
            response = jsonify({"success": True, "msg": "sucessfully logged in", "firstName": user.firstName})
            set_access_cookies(response, accessToken)
            set_refresh_cookies(response, refreshToken)
            return response, 200
        else:
            raise(UnauthorizedError)
    except UnauthorizedError:
        raise UnauthorizedError
    except Exception as e:
        raise InternalServerError(e)


# TODO: This is not revoking cookies
@auth.route('/auth/logout', methods=["POST"])
@jwt_required
def logout():
    try:
        jwtId = get_jwt_identity()
        user = UserModel.getUserForId(jwtId)
        if user is None:
            raise(UnauthorizedError)
        
        response = jsonify({'success': True, "msg": "logged out"})
        unset_jwt_cookies(response)
        user.logout()
        return response, 200
    except UnauthorizedError:
        raise UnauthorizedError
    except Exception as e:
        raise(InternalServerError(e))


@auth.route('/auth/refresh', methods=["POST"])
@jwt_refresh_token_required
def refreshToken():
    try:
        jwtId = get_jwt_identity()
        accessToken = create_access_token(identity = jwtId)
        response = jsonify({"success": True, "msg": "token refreshed"})
        set_access_cookies(response, accessToken)
        return response, 200
    except Exception as e:
        raise InternalServerError(e)


@auth.route('/auth/isLoggedIn', methods=["GET"])
@jwt_required
def isLoggedIn():
    try:
        response = jsonify({"success": True, "msg": "already logged in"})
        return response, 200
    except Exception as e:
        raise InternalServerError(e)