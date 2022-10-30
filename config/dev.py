
from .default import *


APP_ENV = APP_ENV_DEVELOPMENT

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}?auth_plugin=mysql_native_password".format(
    username = "root",
    password = "112020Jo",
    hostname = "localhost:3306",
    databasename = "aicragdb"
)

DEBUG = True
SECRET_KEY = '5e04a4955d8878191923e86fe6a0dfb24edb226c87d6c7787f35ba4698afc86e95cae409aebd47f7'