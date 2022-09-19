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
from .forms import BusquedaForm

logger = logging.getLogger(__name__)

@consultas_bp.route("/consultas/consultaproducto/<criterio>", methods = ['GET', 'POST'])
@consultas_bp.route("/consultas/consultaproducto/", methods = ['GET', 'POST'])
@login_required
def consulta_productos(criterio = ""):
    form = BusquedaForm()
    lista_de_productos = []
    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("consultas.consulta_productos", criterio = buscar))
    
    if criterio.isdigit() == True:
        lista_de_productos = Productos.get_by_codigo_de_barras(criterio)
    elif criterio == "":
        pass
    else:
        lista_de_productos = Productos.get_like_descripcion(criterio)
    #falta calcular la ganancia a aplicarle a cada producto.     
    return render_template("consultas/consulta_productos.html", form = form, lista_de_productos=lista_de_productos )
