from .default import *
import os

APP_ENV = APP_ENV_PRODUCTION

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}?auth_plugin=mysql_native_password".format(
    username = os.getenv('DB_USERNAME'),
    password = os.getenv('DB_PASSWORD'),
    hostname = os.getenv('DB_HOSTNAME'),
    databasename = os.getenv('DB_DATABASE')
)

SECRET_KEY = os.getenv('SECRET_KEY')
