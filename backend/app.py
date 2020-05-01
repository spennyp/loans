from flask import Flask, Blueprint
from flask import render_template
from flask_restful import Api
import yaml
import endpoints
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # This is the magic
from auth import auth

clientDomain = "http://127.0.0.1:8000"

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": ["null", clientDomain]}}, supports_credentials=True) # Only allowing cors from localhost, will need to change when hosted to the client domain

# Must add secrets.yaml to run the application
secrets = yaml.load(open("secrets.yaml"), Loader=yaml.FullLoader)

# JWT configuration
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = secrets["jwtSecretKey"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 15*60 # Access token lasts 15mins before needing to be refreshed
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 1*60*60 # Refresh token lasts for 1 hour
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# app.config['JWT_COOKIE_DOMAIN'] = "localhost" # Leave blank for local host
app.config['JWT_COOKIE_SECURE'] = False # TODO: Set to True when out of dev, this makes sure JWT cookies can only be sent over https
app.config['JWT_COOKIE_CSRF_PROTECT'] = False # TODO: Set True and figure out I cant recieve the non httpOnly csft cookie on the front end
app.config['JWT_CSRF_METHODS'] = ["GET", 'POST', 'PUT', 'PATCH', 'DELETE']
app.config['JWT_COOKIE_SAMESITE'] = None



# Temporary homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

app.register_blueprint(auth)

# Exposing endpoints
api.add_resource(endpoints.User, "/user")
api.add_resource(endpoints.Loan, "/loan")
api.add_resource(endpoints.AcceptLoan, "/acceptLoan")
api.add_resource(endpoints.Test, "/test")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

