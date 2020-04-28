from flask import Flask, request
from flask import render_template
from flask_restful import Resource, Api
import yaml
import endpoints
from flask_jwt_extended import JWTManager

app = Flask(__name__)
api = Api(app)

# Must add secrets.yaml to run the application
secrets = yaml.load(open("secrets.yaml"), Loader=yaml.FullLoader)

# JWT configuration
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = secrets["jwtSecretKey"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 15*60 # Access token lasts 15mins before needing to be refreshed
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 1*60*60 # Refresh token lasts for 1 hour

# Temporary homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# Exposing endpoints
api.add_resource(endpoints.User, "/user")
api.add_resource(endpoints.Login, "/login")
api.add_resource(endpoints.Logout, "/logout")
api.add_resource(endpoints.TokenRefresh, "/refreshToken")
api.add_resource(endpoints.Loan, "/loan")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     dbSession.remove()