import logging
# from operator import setitem
import os
from time import ctime
from datetime import date, datetime, timedelta
# from string import capwords

from flask import render_template, redirect, url_for, current_app, flash, send_file, request #, make_response, abort
from flask_login import login_required, current_user
# from werkzeug.utils import secure_filename

from app.controles import get_tarea_corriendo
# from app.auth.decorators import admin_required
from app.auth.models import User
from app.models import Productos, CabecerasPresupuestos, Presupuestos, Parametros #, Proveedores
from . import gestiones_bp 
from .forms import CabeceraPresupuestoForm, ProductosPresupuestoForm #, BusquedaForm 
# from app.funciones import to_precios_dbf
logger = logging.getLogger(__name__)

def control_vencimiento (fecha):
    if fecha < datetime.now():
        return "VENCIDO"

@gestiones_bp.route("/gestiones/altapresupuesto/", methods = ['GET', 'POST'])
@login_required
def alta_presupuesto():
    form = CabeceraPresupuestoForm()
    dias_a_vancer = timedelta(days = int(Parametros.get_by_tabla("dias_vencimiento").tipo_parametro))
    vencimiento_estimado = datetime.now() + dias_a_vancer

    if form.validate_on_submit():
        fecha_vencimiento = form.fecha_vencimiento.data
        nombre_cliente = form.nombre_cliente.data
        correo_electronico = form.correo_electronico.data
        
        cabecera = CabecerasPresupuestos(fecha_vencimiento = fecha_vencimiento,
                                            nombre_cliente = nombre_cliente,
                                            correo_electronico = correo_electronico,
                                            estado = 4,
                                            importe_total = 0.00,
                                            usuario_alta = current_user.email,
                                            usuario_modificacion = current_user.email
                                            )           
        cabecera.save()
        return redirect(url_for('gestiones.modificacion_productos_presupuesto', id_presupuesto = cabecera.id))
    if get_tarea_corriendo('app.tareas.in_lista_masiva'):
        flash('Los precios se están actualizando', 'alert-warning')
    return render_template("gestiones/alta_datos_cliente.html", form = form, vencimiento_estimado = vencimiento_estimado)
   
@gestiones_bp.route("/gestiones/modificaciondatoscliente/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def modificacion_datos_cliente(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    form = CabeceraPresupuestoForm()
    
    if cabecera.estado != 1 and cabecera.estado != 4:
        flash ("El presupuesto no se puede modificar", "alert-warning" )
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  

    if form.validate_on_submit():
        cabecera.correo_electronico = form.correo_electronico.data
        cabecera.fecha_vencimiento = form.fecha_vencimiento.data
        cabecera.nombre_cliente = form.nombre_cliente.data
        cabecera.usuario_modificacion = current_user.email

        if form.fecha_vencimiento.data < date.today():
                flash("La fecha de vencimiento no puede ser anterior a hoy", "alert-warning")
                return redirect(url_for("gestiones.modificacion_datos_cliente", id_presupuesto = id_presupuesto))
        
        cabecera.save()
        flash("Se han actualizado los datos correctamente", "alert-success")            
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  
    return render_template("gestiones/modificacion_datos_cliente.html", form = form, cabecera = cabecera)
  
@gestiones_bp.route("/gestiones/modificacionproductospresupuesto/<int:id_presupuesto>/<criterio>", methods = ['GET', 'POST'])
@gestiones_bp.route("/gestiones/modificacionproductospresupuesto/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def modificacion_productos_presupuesto(id_presupuesto, criterio = ""):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    producto = Presupuestos.get_by_id_presupuesto_paquete(id_presupuesto)
    form = ProductosPresupuestoForm()
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
     
    cantidad_dias_actualizacion = timedelta(days = int(Parametros.get_by_tabla("dias_actualizacion").tipo_parametro)) 
    fecha_tope = datetime.now() - cantidad_dias_actualizacion
    
    if criterio.isdigit() == True:
        producto_caro = Productos.get_by_codigo_de_barras_caro(criterio)
        if producto_caro: 
            lista_productos_seleccion = Productos.get_by_id_completo(producto_caro.id)
        else:
            lista_productos_seleccion = []
    elif criterio == "":
        lista_productos_seleccion = []
    else:
        lista_productos_seleccion = Productos.get_like_descripcion_all_paginated(criterio, page, per_page)
        if len(lista_productos_seleccion.items) == 0:
            lista_productos_seleccion =[]
            
    if cabecera.estado != 1 and cabecera.estado != 4:
        flash ("El presupuesto no se puede modificar", "alert-warning" )
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  

    if form.validate_on_submit():
        if form.condicion.data == "modificarproducto":
            productos_presupuesto = Presupuestos.get_by_id_producto(form.id.data)
            productos_presupuesto.cantidad = form.cantidad.data
            productos_presupuesto.importe = form.importe.data
            productos_presupuesto.usuario_modificacion = current_user.email        
            productos_presupuesto.save()
            total_presupuesto = Presupuestos.get_importe_total_by_id_presupuesto(id_presupuesto)
            cabecera.importe_total = total_presupuesto[1]
            cabecera.save()
             
            flash("Se han actualizado los datos correctamente", "alert-success")            
            return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))  
        
        elif form.condicion.data == "buscarproductos":
            buscar = form.buscar.data
            if buscar:
                return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto, criterio =  buscar)) 
               
        elif form.condicion.data == "agregarproducto":
            nuevo_producto = Presupuestos(id_cabecera_presupuesto = cabecera.id,
                                          id_producto = form.id.data, 
                                          cantidad = form.cantidad.data,
                                          descripcion = form.descripcion.data, 
                                          importe = form.importe.data,
                                          usuario_alta = current_user.email,
                                          usuario_modificacion = current_user.email) 
            nuevo_producto.save()
            total_presupuesto = Presupuestos.get_importe_total_by_id_presupuesto(id_presupuesto)
            cabecera.importe_total = total_presupuesto[1]
            cabecera.estado = 1
            cabecera.save()     
            flash ("Se incorporó un nuevo producto", "alert-success")
            return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))
    if get_tarea_corriendo('app.tareas.in_lista_masiva'):
        flash('Los precios se están actualizando', 'alert-warning')
    
    return render_template("gestiones/modificacion_productos_presupuesto.html", form = form, cabecera = cabecera, producto = producto, lista_productos_seleccion = lista_productos_seleccion, fecha_tope = fecha_tope, criterio = criterio)

@gestiones_bp.route("/gestiones/eliminaprooductospresupuesto/<int:id_producto>", methods = ['GET', 'POST'])
@login_required
def elimina_productos_presupuesto(id_producto):
    producto = Presupuestos.get_by_id_producto(id_producto)
    id_presupuesto = producto.id_cabecera_presupuesto
    q_producto = Presupuestos.get_q_by_id_presupuesto(id_presupuesto)
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    if q_producto == 1:
        flash ("El presupuesto no puede quedar sin productos", "alert-danger") 
        return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))
    producto.delete()
    total_presupuesto = Presupuestos.get_importe_total_by_id_presupuesto(id_presupuesto)
    cabecera.importe_total = total_presupuesto[1]
    cabecera.save()
    return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))  

@gestiones_bp.route("/gestiones/anulapresupuesto/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def anula_presupuesto(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    if cabecera.estado == 2:
        flash ("El presupuesto ya está vencido no se puede anular", "alert-danger") 
        return redirect(url_for("consultas.consulta_presupuestos"))
    cabecera.estado = 3
    cabecera.save()
    return redirect(url_for("consultas.consulta_presupuestos"))

@gestiones_bp.route("/gestiones/exportardatos")
@login_required
def exportar_datos():
    archivo_dir = current_app.config['ARCHIVOS_PARA_DESCARGA']
    archivos = os.listdir(archivo_dir)
    archivos_dict = {}
    for datos in archivos: 
        archivos_dict[datos] =  ctime(os.path.getmtime(archivo_dir + '/' + datos))

    print (archivos_dict) 
    return render_template("gestiones/exportar.html", archivos_dict = archivos_dict, archivo_dir = archivo_dir)

@gestiones_bp.route("/gestiones/exportarprecios")
@login_required
def exportar_precios():
    job = current_app.task_queue.enqueue("app.tareas.to_precios_dbf", job_timeout = 3600)
    job.get_id()

    flash("Ha iniciado la generación del archivo precios.dbf", "alert-success")
    return redirect(url_for("abms.agenda"))

@gestiones_bp.route("/gestiones/exportarcodigosbarrasfaltante")
@login_required
def exportar_codigos_de_barra_faltantes():
    job = current_app.task_queue.enqueue("app.tareas.sin_codigo_barras_to_excel", job_timeout = 3600)
    job.get_id()

    flash("Ha iniciado la generación del archivo precios.dbf", "alert-success")
    return redirect(url_for("abms.agenda"))

@gestiones_bp.route("/gestiones/descargararchivos/<archivo>")
@login_required
def descarga_archivo(archivo):
    archivo_dir = current_app.config['ARCHIVOS_PARA_DESCARGA']
    archivos = os.listdir(archivo_dir)
    if archivo not in archivos:
        flash('El archivo no existe', 'alert-warning')
        return redirect(url_for("gestiones.exportar_datos"))
    return send_file(archivo_dir + '/' + archivo, as_attachment=True)