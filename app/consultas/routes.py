import logging
from operator import setitem
import os
from datetime import date, datetime
from string import capwords

from flask import render_template, redirect, url_for, abort, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required
from app.auth.models import User
from app.models import Productos, CabecerasPresupuestos, Presupuestos, Parametros, Proveedores
from . import consultas_bp 
from .forms import AltaCompulsaForm, ImagenesBienesForm

logger = logging.getLogger(__name__)

@consultas_bp.route("/consultaproductos/")
@login_required
#@admin_required
def consulta_productos():

    return render_template("consultas/consulta_productos.html")

