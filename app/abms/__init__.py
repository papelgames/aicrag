from flask import Blueprint

abms_bp = Blueprint('abms', __name__, template_folder='templates')

from . import routes
