from flask import Flask, Blueprint
from flask import render_template
from flask_restful import Api
import endpoints
from flask_cors import CORS  # This is the magic
from auth import auth
from errors import errors
from jwtConfig import (jwt, jwtConfig)

clientDomain = "http://0.0.0.0:8000"

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": ["null", clientDomain]}}, supports_credentials=True) # Only allowing cors from localhost, will need to change when hosted to the client domain

# JWT configuration
jwt.init_app(app)
app.config.from_mapping(jwtConfig)

# Registering blueprints
app.register_blueprint(auth)
app.register_blueprint(errors)

# Exposing endpoints
api.add_resource(endpoints.User, "/user")
api.add_resource(endpoints.Loan, "/loan")
api.add_resource(endpoints.AcceptLoan, "/acceptLoan")
api.add_resource(endpoints.Test, "/test")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

