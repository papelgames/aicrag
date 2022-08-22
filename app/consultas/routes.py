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
#from app.models import Recuperos, Tareas, TareasPendientes
from . import consultas_bp 
from .forms import AltaCompulsaForm, ImagenesBienesForm

logger = logging.getLogger(__name__)

@consultas_bp.route("/gestion/")
@login_required
#@admin_required
def gestion():
    pendientes = Tareas.get_all()
    
    capsula_pendientes = [zip( tablas.tareas_pendientes, tablas.recuperos) for tablas in pendientes]
    # capsula_pendientes = [] pendientes,
    # for tablas in lista_tablas:
    #     for i in tablas:
    #         capsula_pendientes.append(i)
    # # print(capsula_pendientes)
    # # for t in capsula_pendientes:
    # #     # print(t[0])
    # #     for g in t:
    # #          print(g)
    # for oo in lista_tablas:
    #     print(oo)
    #     for x in oo:
    #         print (x[0])

    return render_template("gestion/gestion.html", pendientes=pendientes, capsula_pendientes = capsula_pendientes)

