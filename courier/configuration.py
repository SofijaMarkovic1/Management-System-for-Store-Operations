import os
from datetime import timedelta

DATABASE_URL = "prodavnicaDatabase" if ("PRODUCTION" in os.environ) else "localhost"
DATABASE_PORT = "3306" if ("PRODUCTION" in os.environ) else "3307"


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{DATABASE_URL}:{DATABASE_PORT}/prodavnica"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
