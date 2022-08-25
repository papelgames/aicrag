import logging
import os

from flask import render_template, redirect, url_for, abort, current_app
from flask.helpers import flash
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required
from app.auth.models import User
from app.models import Productos, Proveedores
from . import abms_bp
from .forms import TareasForm, AccionesForm, TareasAccionesForm

from app.common.mail import send_email

from datetime import datetime, time

logger = logging.getLogger(__name__)


def estados_select(tabla):
    estados = Estados.get_by_estado_tabla(tabla)
    select_estado =[( '','Seleccionar estado')]
    for rs in estados:
        sub_select_estado = (str(rs.id), rs.desc_estado)
        select_estado.append(sub_select_estado)
    return select_estado

def tareas_select():
    tareas = Tareas.get_all()
    select_tarea =[( '','Seleccionar tarea')]
    for rs in tareas:
        sub_select_tarea = (str(rs.id), rs.descripcion)
        select_tarea.append(sub_select_tarea)
    return select_tarea

def accion_select():
    acciones = Acciones.get_all()
    select_accion =[( '','Seleccionar acción')]
    for rs in acciones:
        sub_select_accion = (str(rs.id), rs.descripcion)
        select_accion.append(sub_select_accion)
    return select_accion

@abms_bp.route("/abms/altaindividual", methods = ['GET', 'POST'])
@login_required
def alta_individual():
        
    return render_template("abms/alta_individual.html")

