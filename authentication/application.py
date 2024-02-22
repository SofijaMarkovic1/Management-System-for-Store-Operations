from flask import Flask
from configuration import Configuration
from models import database, Korisnik
from korisnik import korisnikBlueprint
from flask_jwt_extended import JWTManager
application = Flask(__name__)
application.config.from_object(Configuration)

application.register_blueprint(korisnikBlueprint, url_prefix="/")

jwt = JWTManager(application)

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
