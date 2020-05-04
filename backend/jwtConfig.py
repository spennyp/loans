from flask_jwt_extended import JWTManager
from flask import jsonify
import yaml

# Must add secrets.yaml to run the application
secrets = yaml.load(open("secrets.yaml"), Loader=yaml.FullLoader)

jwt = JWTManager()
jwtConfig = {}

jwtConfig["JWT_SECRET_KEY"] = secrets["jwtSecretKey"]
jwtConfig["JWT_ACCESS_TOKEN_EXPIRES"] = 15*60 # Access token lasts 15mins before needing to be refreshed
jwtConfig["JWT_REFRESH_TOKEN_EXPIRES"] = 1*60*60 # Refresh token lasts for 1 hour
jwtConfig['JWT_TOKEN_LOCATION'] = ['cookies']
#jwtConfig['JWT_COOKIE_DOMAIN'] = "localhost" # Leave blank for local host
jwtConfig['JWT_COOKIE_SECURE'] = False # TODO: Set to True when out of dev, this makes sure JWT cookies can only be sent over https
jwtConfig['JWT_COOKIE_CSRF_PROTECT'] = False # TODO: Set True and figure out I cant recieve the non httpOnly csft cookie on the front end
jwtConfig['JWT_CSRF_METHODS'] = ["GET", 'POST', 'PUT', 'PATCH', 'DELETE']
jwtConfig['JWT_COOKIE_SAMESITE'] = None

@jwt.expired_token_loader
def expiredTokenCallback(expiredToken):
    tokenType = expiredToken['type']
    return jsonify({
        "success": False,
        "error": "expiredToken",
        "msg": f"The {tokenType} token has expired"
    }), 401

@jwt.invalid_token_loader
def invalidTokenCallback(invalidToken):
    tokenType = invalidToken['type']
    return jsonify({
        "success": False,
        "error": "invalidToken",
        "msg": f"The {tokenType} token is invalid"
    }), 401

@jwt.needs_fresh_token_loader
def nonRefreshTokenCallback(nonRefreshToken):
    tokenType = nonRefreshToken['type']
    return jsonify({
        "success": False,
        "error": "nonRefreshToken",
        "msg": f"The {tokenType} token is not a refresh token"
    }), 401

@jwt.unauthorized_loader
def unauthorized(_):
    return jsonify({
        "success": False,
        "error": "noJWT",
        "msg": "missing access token cookie"
    }), 401
