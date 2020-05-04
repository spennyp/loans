from flask import Blueprint, Response, request
from models import UserModel
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask import jsonify
import traceback
from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)

class UnauthorizedError(Exception):
    statusCode = 401

    def payload(self):
        payload = {
            "success": False,
            "error": self.__class__.__name__,
            "msg": f"Unauthorized"
        }
        return jsonify(payload)

@errors.app_errorhandler(UnauthorizedError)
def handleUnauthorized(error):
    response = error.payload()
    response.status_code = error.statusCode
    return response


class InternalServerError(Exception):
    statusCode = 500
    msg = ""

    def __init__(self, msg=""):
        self.msg = msg

    def payload(self):
        payload = {
            "success": False,
            "error": self.__class__.__name__,
            "msg": f"An internal server error has occured: {self.msg}"
        }
        return jsonify(payload)

@errors.app_errorhandler(InternalServerError)
def handleInternalServerError(error):
    response = error.payload()
    response.status_code = error.statusCode
    return response
