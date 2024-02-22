import os
from datetime import timedelta

DATABASE_URL = os.environ["DATABASE_URL"] if ("DATABASE_URL" in os.environ) else "localhost"


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{DATABASE_URL}/projekat"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
