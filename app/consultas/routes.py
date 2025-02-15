import logging
# from operator import setitem
# import os
# import dbf 
from datetime import date, datetime, timedelta
# from string import capwords

from flask import render_template, redirect, url_for, abort, current_app, flash, request
from flask_login import login_required, current_user
#from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required, not_initial_status, nocache
from app.auth.models import Users
from app.models import Productos, CabecerasPresupuestos, Presupuestos, Parametros, Estados, Personas #, Proveedores
from app.controles import get_tarea_corriendo

from . import consultas_bp 
from .forms import BusquedaForm


logger = logging.getLogger(__name__)

def control_vencimiento (fecha):
    if fecha < datetime.now():
        return "VENCIDO"

@consultas_bp.route("/consultas/consultaproducto/<criterio>", methods = ['GET', 'POST'])
@consultas_bp.route("/consultas/consultaproducto/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def consulta_productos(criterio = ""):
    form = BusquedaForm()
    lista_de_productos = []
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("consultas.consulta_productos", criterio = buscar))
    
    if criterio.isdigit() == True:
        producto_caro = Productos.get_by_codigo_de_barras_caro(criterio)
        if producto_caro: 
            lista_de_productos = Productos.get_by_id_completo(producto_caro.id)
            # print(lista_de_productos)
    elif criterio == "":
        pass
    else:
        lista_de_productos = Productos.get_like_descripcion_all_paginated(criterio,page, per_page)
        if len(lista_de_productos.items) == 0:
            lista_de_productos =[]
          
    cantidad_dias_actualizacion = timedelta(days = int(Parametros.get_by_tabla("dias_actualizacion").tipo_parametro)) 
    fecha_tope = datetime.now() - cantidad_dias_actualizacion
    if get_tarea_corriendo('app.tareas.in_lista_masiva'):
        flash('Los precios se están actualizando', 'alert-warning')
    return render_template("consultas/consulta_productos.html", form = form, lista_de_productos=lista_de_productos, criterio = criterio, fecha_tope = fecha_tope )

@consultas_bp.route("/consultas/consultapresupuestos/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def consulta_presupuestos():
    criterio = request.args.get('criterio','')
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    form = BusquedaForm()

    estado_pendiente = Estados.get_first_by_clave_tabla(1,"estado_presupuesto")

    cabecera = CabecerasPresupuestos.get_all_estado(estado_pendiente.id, page, per_page)
    
    if len(cabecera.items) == 0:
            cabecera =[]
    now = datetime.now()

    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("consultas.consulta_presupuestos", criterio = buscar))
    
    if criterio.isdigit() == True:
        cabecera = CabecerasPresupuestos.get_by_id(criterio)
    elif criterio == "":
        pass
    else:
        cabecera = CabecerasPresupuestos.get_like_descripcion_all_paginated(criterio, page, per_page)
        if len(cabecera.items) == 0:
            cabecera =[]
    return render_template("consultas/consulta_presupuestos.html", form = form, cabecera = cabecera, now = now)

@consultas_bp.route("/consultas/presupuesto/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def presupuesto():
    id_presupuesto = request.args.get('id_presupuesto','')
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    productos = Presupuestos.get_by_id_presupuesto(id_presupuesto)
    vencimiento_si_no = control_vencimiento(cabecera.fecha_vencimiento)
    estado_pendiente = Estados.get_first_by_clave_tabla(1,"estado_presupuesto")
    estado_vencido = Estados.get_first_by_clave_tabla(2,"estado_presupuesto")
    
    if vencimiento_si_no == 'VENCIDO'and cabecera.id_estado == estado_pendiente.id:
        cabecera.id_estado = estado_vencido.id
        cabecera.save()
    return render_template("consultas/presupuesto.html", cabecera = cabecera, productos = productos, vencimiento_si_no = vencimiento_si_no)

@consultas_bp.route("/consultas/consultapersonas/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def consulta_personas():
    criterio = request.args.get('criterio','')
    form = BusquedaForm()
    lista_de_personas = []
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("consultas.consulta_personas", criterio = buscar))
    if criterio.isdigit() == True:
        lista_de_personas = Personas.get_by_cuit(criterio)
    elif criterio == "":
        pass
    else:
        lista_de_personas = Personas.get_like_descripcion_all_paginated(criterio, page, per_page)
        if len(lista_de_personas.items) == 0:
            lista_de_personas =[]

    return render_template("consultas/consulta_personas.html", form = form, criterio = criterio, lista_de_personas= lista_de_personas )
