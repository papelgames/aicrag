import logging
import os

from flask import render_template, redirect, url_for, abort, current_app
from flask.helpers import flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required
from app.auth.models import Users
from app.models import Compras
from . import compras_bp
from .forms import InicioOfertaForm, OfertaForm

from app.common.mail import send_email

from datetime import datetime, time

logger = logging.getLogger(__name__)

@compras_bp.route("/compras/productospendientes", methods = ['GET', 'POST'])
def productos_pendientes():
    productos = Compras.get_all()
    
    return render_template("compras/productos_pendientes.html", productos = productos)

