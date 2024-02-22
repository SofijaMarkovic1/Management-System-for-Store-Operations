from flask import Flask
from configuration import Configuration
from models import database
from vlasnik import vlasnikBlueprint
from flask_jwt_extended import JWTManager
application = Flask(__name__)
application.config.from_object(Configuration)

application.register_blueprint(vlasnikBlueprint, url_prefix="/")

jwt = JWTManager(application)

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
