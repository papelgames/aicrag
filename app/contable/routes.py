
import logging
import os

from flask import render_template, redirect, url_for, request, current_app, abort, make_response
from flask.helpers import flash
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required, nocache, not_initial_status
from app.auth.models import Users
from app.models import Egresos
from . import contable_bp
from .forms import EgresosForm
from time import strftime, gmtime

from app.common.funciones import listar_endpoints
from rq import Worker


logger = logging.getLogger(__name__)

@contable_bp.route("/contable/altaegreso", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def alta_egreso():
    form=EgresosForm()
    
    if form.validate_on_submit():
        descripcion = form.descripcion.data
        importe = form.importe.data
        nota = form.nota.data
        
        egreso = Egresos(descripcion = descripcion,
                             importe = importe,
                             nota = nota,
                             usuario_alta = current_user.username,
                             usuario_modificacion = current_user.username
                        )
        
        egreso.save()
        flash("Nuevo egreso ingresado", "alert-success")
        return redirect(url_for("contable.alta_egreso"))
    return render_template("contable/alta_egreso.html", form=form)

