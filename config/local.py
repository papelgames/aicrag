
from .default import *
import os

APP_ENV = APP_ENV_LOCAL
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.abspath("./database.db")
DEBUG = True

