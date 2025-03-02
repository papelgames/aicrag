from flask import Blueprint

contable_bp = Blueprint('contable', __name__, template_folder='templates')

from . import routes
