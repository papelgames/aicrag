from flask import Blueprint

gestiones_bp = Blueprint('gestiones', __name__, template_folder='templates')

from . import routes
