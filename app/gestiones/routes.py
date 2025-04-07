import logging
# from operator import setitem
import os
from time import ctime
from datetime import date, datetime, timedelta
# from string import capwords

from flask import render_template, redirect, url_for, current_app, flash, send_file, request #, make_response, abort
from flask_login import login_required, current_user
# from werkzeug.utils import secure_filename

from app.common.controles import get_tarea_corriendo
from app.auth.decorators import admin_required, nocache, not_initial_status
from app.auth.models import Users
from app.models import Productos, CabecerasPresupuestos, ProductosPresupuestos, Parametros, Estados, TiposVentas #, Proveedores
from . import gestiones_bp 
from .forms import CabeceraPresupuestoForm, ProductosPresupuestoForm #, BusquedaForm 
# from app.funciones import to_precios_dbf
logger = logging.getLogger(__name__)

def control_vencimiento (fecha):
    if fecha < datetime.now():
        return "VENCIDO"

@gestiones_bp.route("/gestiones/altapresupuesto/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def alta_presupuesto():
    form = CabeceraPresupuestoForm()
    dias_a_vancer = timedelta(days = int(Parametros.get_by_tabla("dias_vencimiento").tipo_parametro))
    vencimiento_estimado = datetime.now() + dias_a_vancer

    if form.validate_on_submit():
        estado_iniciado = Estados.get_first_by_clave_tabla(4,'estado_presupuesto') #es el estado inicial que toma un presupuesto
        tipo_venta = TiposVentas.get_first_by_clave_tabla(1) #1 es presupuesto
        fecha_vencimiento = form.fecha_vencimiento.data
        nombre_cliente = form.nombre_cliente.data
        correo_electronico = form.correo_electronico.data
        
        cabecera = CabecerasPresupuestos(fecha_vencimiento = fecha_vencimiento,
                                            nombre_cliente = nombre_cliente,
                                            correo_electronico = correo_electronico,
                                            importe_total = 0.00,
                                            usuario_alta = current_user.username,
                                            usuario_modificacion = current_user.username
                                            )           
        estado_iniciado.cabecera_presupuesto.append(cabecera)
        tipo_venta.cabecera_presupuesto.append(cabecera)
        estado_iniciado.save()
        tipo_venta.save()

        return redirect(url_for('gestiones.modificacion_productos_presupuesto', id_presupuesto = cabecera.id))
    if get_tarea_corriendo('app.tareas.in_lista_masiva'):
        flash('Los precios se están actualizando', 'alert-warning')
    return render_template("gestiones/alta_datos_cliente.html", form = form, vencimiento_estimado = vencimiento_estimado)


@gestiones_bp.route("/gestiones/altaventa/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def alta_venta():
    id_venta = request.args.get('id_venta','')
    criterio = request.args.get('criterio','')

    form = ProductosPresupuestoForm()
    vencimiento_estimado = datetime.now()
    
    lista_productos_seleccion = []
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
    if not id_venta: #sino tiene id_venta le creo uno diccionario con los valores basicos del objeto cabecera para pasarselo al template
        cabecera = {'nombre_cliente': 'Consumidor final', 'fecha_vencimiento': vencimiento_estimado, 'created': vencimiento_estimado, 'importe_total' : 0.00}
    else:
        cabecera = CabecerasPresupuestos.get_by_id(id_venta)   
        if cabecera.cabeceras_presupuestos.clave == 1:
            return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_venta))

    if form.validate_on_submit(): 
        if not id_venta and form.condicion.data == "agregarproducto": #si no tiene cabecera se la creo.
            estado_iniciado = Estados.get_first_by_clave_tabla(1,'estado_presupuesto') #inicia como activo 
            tipo_venta = TiposVentas.get_first_by_clave_tabla(2) #2 es venta
            #creo el objeto cabecera nueva para insertar en la tabla cabeceraspresupuestos
            cabecera_nueva_venta = CabecerasPresupuestos(fecha_vencimiento = cabecera['fecha_vencimiento'],
                                                nombre_cliente = cabecera['nombre_cliente'],
                                                importe_total = 0.00,
                                                id_tp_ventas = 1,
                                                usuario_alta = current_user.username,
                                                usuario_modificacion = current_user.username
                                                )           
            #creo el objeto nuevo producto para insertar en la tabla productospresupuestos
            nuevo_producto = ProductosPresupuestos(id_producto = form.id.data, 
                                          cantidad = form.cantidad.data,
                                          descripcion = form.descripcion.data, 
                                          importe = form.importe.data,
                                          usuario_alta = current_user.username,
                                          usuario_modificacion = current_user.username)
            cabecera_nueva_venta.producto_presupuesto.append(nuevo_producto)
            estado_iniciado.cabecera_presupuesto.append(cabecera_nueva_venta)
            tipo_venta.cabecera_presupuesto.append(cabecera_nueva_venta)
            #sumo el importe de todos los productos y actualizo el valor en la tabla cabeceraspresupuestos
            total_presupuesto = ProductosPresupuestos.get_importe_total_by_id_presupuesto(cabecera_nueva_venta.id)
            cabecera_nueva_venta.importe_total = total_presupuesto[1]
            estado_iniciado.save()
            tipo_venta.save()
            return redirect(url_for('gestiones.alta_venta', id_venta = cabecera_nueva_venta.id))
        elif form.condicion.data == "agregarproducto": #agrego productos a una cabecera ya existente con el objeto nuevo producto
            nuevo_producto = ProductosPresupuestos(id_producto = form.id.data, 
                                          cantidad = form.cantidad.data,
                                          descripcion = form.descripcion.data, 
                                          importe = form.importe.data,
                                          usuario_alta = current_user.username,
                                          usuario_modificacion = current_user.username) 
            cabecera.producto_presupuesto.append(nuevo_producto)
            total_presupuesto = ProductosPresupuestos.get_importe_total_by_id_presupuesto(id_venta)
            cabecera.importe_total = total_presupuesto[1]
            cabecera.save()    
            return redirect(url_for('gestiones.alta_venta', id_venta = cabecera.id))
        elif form.condicion.data == "buscarproductos":
            buscar = form.buscar.data
            if buscar:
                return redirect(url_for("gestiones.alta_venta", id_venta = id_venta, criterio =  buscar)) 
        elif form.condicion.data == "modificarproducto":
            productos_presupuesto = ProductosPresupuestos.get_by_id_producto(form.id.data)
            productos_presupuesto.cantidad = form.cantidad.data
            productos_presupuesto.importe = form.importe.data
            productos_presupuesto.usuario_modificacion = current_user.username        
            total_presupuesto = ProductosPresupuestos.get_importe_total_by_id_presupuesto(id_venta)
            cabecera.importe_total = total_presupuesto[1]
            cabecera.producto_presupuesto.append(productos_presupuesto)
            cabecera.save()
             
            flash("Se han actualizado los datos correctamente", "alert-success")            
            return redirect(url_for("gestiones.alta_venta", id_venta = id_venta))
            
    if get_tarea_corriendo('app.tareas.in_lista_masiva'):
        flash('Los precios se están actualizando', 'alert-warning')
    return render_template("gestiones/modificacion_productos_presupuesto.html", form = form, 
                           cabecera = cabecera, 
                           vencimiento_estimado = vencimiento_estimado, 
                           lista_productos_seleccion = lista_productos_seleccion, 
                           fecha_tope= fecha_tope)

@gestiones_bp.route("/gestiones/modificaciondatoscliente/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def modificacion_datos_cliente():
    id_presupuesto = request.args.get('id_presupuesto','')
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    form = CabeceraPresupuestoForm()
    
    if cabecera.estado_presupuestos.clave != 1 and cabecera.estado_presupuestos.clave != 4:
        flash ("El presupuesto no se puede modificar", "alert-warning" )
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  

    if form.validate_on_submit():
        cabecera.correo_electronico = form.correo_electronico.data
        cabecera.fecha_vencimiento = form.fecha_vencimiento.data
        cabecera.nombre_cliente = form.nombre_cliente.data
        cabecera.usuario_modificacion = current_user.username

        if form.fecha_vencimiento.data < date.today():
                flash("La fecha de vencimiento no puede ser anterior a hoy", "alert-warning")
                return redirect(url_for("gestiones.modificacion_datos_cliente", id_presupuesto = id_presupuesto))
        
        cabecera.save()
        flash("Se han actualizado los datos correctamente", "alert-success")            
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  
    return render_template("gestiones/modificacion_datos_cliente.html", form = form, cabecera = cabecera)
  
@gestiones_bp.route("/gestiones/modificacionproductospresupuesto/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def modificacion_productos_presupuesto():
    id_presupuesto = request.args.get('id_presupuesto','')
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    criterio = request.args.get('criterio','')
    
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

    if cabecera.cabeceras_presupuestos.clave == 2:
        return redirect(url_for("gestiones.alta_venta", id_venta=id_presupuesto ))        
    
    if cabecera.estado_presupuestos.clave != 1 and cabecera.estado_presupuestos.clave != 4:
        flash ("El presupuesto no se puede modificar", "alert-warning" )
        return redirect(url_for("consultas.presupuesto", id_presupuesto=id_presupuesto))  
    
    if form.validate_on_submit():
        if form.condicion.data == "modificarproducto":
            productos_presupuesto = ProductosPresupuestos.get_by_id_producto(form.id.data)
            productos_presupuesto.cantidad = form.cantidad.data
            productos_presupuesto.importe = form.importe.data
            productos_presupuesto.usuario_modificacion = current_user.username        
            total_presupuesto = ProductosPresupuestos.get_importe_total_by_id_presupuesto(id_presupuesto)
            cabecera.importe_total = total_presupuesto[1]
            cabecera.producto_presupuesto.append(productos_presupuesto)
            cabecera.save()
             
            flash("Se han actualizado los datos correctamente", "alert-success")            
            return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))  
        
        elif form.condicion.data == "buscarproductos":
            buscar = form.buscar.data
            if buscar:
                return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto, criterio =  buscar)) 
               
        elif form.condicion.data == "agregarproducto":
            estado_pendiente = Estados.get_first_by_clave_tabla(1,"estado_presupuesto")
            nuevo_producto = ProductosPresupuestos(id_producto = form.id.data, 
                                          cantidad = form.cantidad.data,
                                          descripcion = form.descripcion.data, 
                                          importe = form.importe.data,
                                          usuario_alta = current_user.username,
                                          usuario_modificacion = current_user.username) 
            cabecera.producto_presupuesto.append(nuevo_producto)
            total_presupuesto = ProductosPresupuestos.get_importe_total_by_id_presupuesto(id_presupuesto)
            cabecera.importe_total = total_presupuesto[1]
            estado_pendiente.cabecera_presupuesto.append(cabecera) #actualizo el estado.
            estado_pendiente.save()

            flash ("Se incorporó un nuevo producto", "alert-success")
            return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))
    if get_tarea_corriendo('app.tareas.in_lista_masiva'):
        flash('Los precios se están actualizando', 'alert-warning')
    return render_template("gestiones/modificacion_productos_presupuesto.html", form = form, 
                           cabecera = cabecera, 
                           lista_productos_seleccion = lista_productos_seleccion, 
                           fecha_tope = fecha_tope, 
                           criterio = criterio)

@gestiones_bp.route("/gestiones/eliminaprooductospresupuesto/<int:id_producto>", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def elimina_productos_presupuesto(id_producto):
    producto = ProductosPresupuestos.get_by_id_producto(id_producto)
    id_presupuesto = producto.id_cabecera_presupuesto
    q_producto = ProductosPresupuestos.get_q_by_id_presupuesto(id_presupuesto)
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    if q_producto == 1:
        flash ("El presupuesto no puede quedar sin productos", "alert-danger") 
        return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))
    cabecera.producto_presupuesto.remove(producto)
    total_presupuesto = ProductosPresupuestos.get_importe_total_by_id_presupuesto(id_presupuesto)
    cabecera.importe_total = total_presupuesto[1]
    cabecera.save()
    return redirect(url_for("gestiones.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))  

@gestiones_bp.route("/gestiones/anulapresupuesto/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def anula_presupuesto():
    id_presupuesto = request.args.get('id_presupuesto','')
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    if cabecera.estado_presupuestos.clave == 2:
        flash ("El presupuesto ya está vencido no se puede anular", "alert-danger") 
        return redirect(url_for("consultas.consulta_presupuestos"))
    estado_anulado = Estados.get_first_by_clave_tabla(3,'estado_presupuesto')
    estado_anulado.cabecera_presupuesto.append(cabecera)
    estado_anulado.save()
    return redirect(url_for("consultas.consulta_presupuestos"))

@gestiones_bp.route("/gestiones/exportardatos")
@login_required
@not_initial_status
def exportar_datos():
    archivo_dir = current_app.config['ARCHIVOS_PARA_DESCARGA']
    archivos = os.listdir(archivo_dir)
    archivos_dict = {}
    for datos in archivos: 
        archivos_dict[datos] =  ctime(os.path.getmtime(archivo_dir + '/' + datos))
    return render_template("gestiones/exportar.html", archivos_dict = archivos_dict, archivo_dir = archivo_dir)

@gestiones_bp.route("/gestiones/exportarprecios")
@login_required
@not_initial_status
def exportar_precios():
    job = current_app.task_queue.enqueue("app.tareas.to_precios_dbf", job_timeout = 3600)
    job.get_id()

    flash("Ha iniciado la generación del archivo precios.dbf", "alert-success")
    return redirect(url_for("abms.agenda"))

@gestiones_bp.route("/gestiones/exportarcodigosbarrasfaltante")
@login_required
@not_initial_status
def exportar_codigos_de_barra_faltantes():
    job = current_app.task_queue.enqueue("app.tareas.sin_codigo_barras_to_excel", job_timeout = 3600)
    job.get_id()

    flash("Ha iniciado la generación del archivo precios.dbf", "alert-success")
    return redirect(url_for("abms.agenda"))

@gestiones_bp.route("/gestiones/descargararchivos/<archivo>")
@login_required
@not_initial_status
def descarga_archivo(archivo):
    archivo_dir = current_app.config['ARCHIVOS_PARA_DESCARGA']
    archivos = os.listdir(archivo_dir)
    if archivo not in archivos:
        flash('El archivo no existe', 'alert-warning')
        return redirect(url_for("gestiones.exportar_datos"))
    return send_file(archivo_dir + '/' + archivo, as_attachment=True)