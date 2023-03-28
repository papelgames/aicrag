import logging
from operator import setitem
import os
from datetime import date, datetime, timedelta
from string import capwords

from flask import render_template, redirect, url_for, abort, current_app, flash, g
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required
from app.auth.models import User
from app.models import Productos, CabecerasPresupuestos, Presupuestos, Parametros, Proveedores
from . import consultas_bp 
from .forms import BusquedaForm, CabeceraPresupuestoForm, ProductosPresupuestoForm

logger = logging.getLogger(__name__)

def control_vencimiento (fecha):
    if fecha < datetime.now():
        return "VENCIDO"


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
    
    cantidad_dias_actualizacion = timedelta(days = int(Parametros.get_by_tabla("dias_actualizacion").tipo_parametro)) 
   
    fecha_tope = datetime.now() - cantidad_dias_actualizacion
    
    return render_template("consultas/consulta_productos.html", form = form, lista_de_productos=lista_de_productos, fecha_tope = fecha_tope )

@consultas_bp.route("/consultas/consultapresupuestos/<criterio>", methods = ['GET', 'POST'])
@consultas_bp.route("/consultas/consultapresupuestos/", methods = ['GET', 'POST'])
@login_required
def consulta_presupuestos(criterio=""):
    form = BusquedaForm()
    cabecera = CabecerasPresupuestos.get_all_estado("1")
    now = datetime.now()

    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("consultas.consulta_presupuestos", criterio = buscar))
    
    if criterio.isdigit() == True:
        cabecera = CabecerasPresupuestos.get_all_by_id(criterio)
    elif criterio == "":
        pass
    else:
        cabecera = CabecerasPresupuestos.get_like_descripcion(criterio)
     
   
    return render_template("consultas/consulta_presupuestos.html", form = form, cabecera = cabecera, now = now)

@consultas_bp.route("/consultas/presupuesto/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def presupuesto(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    productos = Presupuestos.get_by_id_presupuesto(id_presupuesto)
    vencimiento_si_no = control_vencimiento(cabecera.fecha_vencimiento)
    if vencimiento_si_no == "VENCIDO" and cabecera.estado == 1:
        cabecera.estado = 2
        cabecera.save()

    return render_template("consultas/presupuesto.html", cabecera = cabecera, productos = productos, vencimiento_si_no = vencimiento_si_no)


@consultas_bp.route("/consultas/altapresupuesto/", methods = ['GET', 'POST'])
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
        return redirect(url_for('consultas.modificacion_productos_presupuesto', id_presupuesto = cabecera.id))
    return render_template("consultas/alta_datos_cliente.html", form = form, vencimiento_estimado = vencimiento_estimado)
    

@consultas_bp.route("/consultas/modificaciondatoscliente/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def modificacion_datos_cliente(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    form = CabeceraPresupuestoForm()
    
    if cabecera.estado != 1:
        flash ("El presupuesto no se puede modificar", "alert-warning" )
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  

    if form.validate_on_submit():
        cabecera.correo_electronico = form.correo_electronico.data
        cabecera.fecha_vencimiento = form.fecha_vencimiento.data
        cabecera.nombre_cliente = form.nombre_cliente.data
        cabecera.usuario_modificacion = current_user.email

        if form.fecha_vencimiento.data < date.today():
                flash("La fecha de vencimiento no puede ser anterior a hoy", "alert-warning")
                return redirect(url_for("consultas.modificacion_datos_cliente", id_presupuesto = id_presupuesto))
        
        cabecera.save()
        
        flash("Se han actualizado los datos correctamente", "alert-success")            
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  

    return render_template("consultas/modificacion_datos_cliente.html", form = form, cabecera = cabecera)

  
@consultas_bp.route("/consultas/modificacionproductospresupuesto/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def modificacion_productos_presupuesto(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    producto = Presupuestos.get_by_id_presupuesto_paquete(id_presupuesto)
    form = ProductosPresupuestoForm()
    lista_productos_seleccion = []
    
    cantidad_dias_actualizacion = timedelta(days = int(Parametros.get_by_tabla("dias_actualizacion").tipo_parametro)) 
    fecha_tope = datetime.now() - cantidad_dias_actualizacion
    
    if cabecera.estado != 1 and cabecera.estado != 4:
        flash ("El presupuesto se no se puede modificar", "alert-warning" )
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
            cabecera.estado = 1
            cabecera.save()
            
            flash("Se han actualizado los datos correctamente", "alert-success")            
            return redirect(url_for("consultas.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))  
        elif form.condicion.data == "buscarproductos":
            buscar = form.buscar.data
            if buscar.isdigit() == True:
                lista_de_productos = Productos.get_by_codigo_de_barras(buscar)
                for registro in lista_de_productos:
                    lista_productos_seleccion.append([registro.Productos.id, registro.Productos.descripcion, registro.importe_calculado, registro.Proveedores.nombre, registro.Productos.modified])
            elif buscar == "":
                
                #corregir este mensaje cuando se graba vacio el nombre del clienete
                flash("Escriba el nombre de un producto", "alert-warning")
            else:
                
                lista_de_productos = Productos.get_like_descripcion(buscar)
                for registro in lista_de_productos:
                    lista_productos_seleccion.append([registro.Productos.id, registro.Productos.descripcion, registro.importe_calculado, registro.Proveedores.nombre, registro.Productos.modified])
            return render_template("consultas/modificacion_productos_presupuesto.html", form = form, cabecera = cabecera, producto = producto, lista_productos_seleccion = lista_productos_seleccion, fecha_tope = fecha_tope)
        
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
            return redirect(url_for("consultas.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))
        
    return render_template("consultas/modificacion_productos_presupuesto.html", form = form, cabecera = cabecera, producto = producto, lista_productos_seleccion = lista_productos_seleccion, fecha_tope = fecha_tope)

@consultas_bp.route("/consultas/eliminaprooductospresupuesto/<int:id_producto>", methods = ['GET', 'POST'])
@login_required
def elimina_productos_presupuesto(id_producto):
    producto = Presupuestos.get_by_id_producto(id_producto)
    id_presupuesto = producto.id_cabecera_presupuesto
    q_producto = Presupuestos.get_q_by_id_presupuesto(id_presupuesto)
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    if q_producto == 1:
        flash ("El presupuesto no puede quedar sin productos", "alert-danger") 
        return redirect(url_for("consultas.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))
    producto.delete()
    total_presupuesto = Presupuestos.get_importe_total_by_id_presupuesto(id_presupuesto)
    cabecera.importe_total = total_presupuesto[1]
    cabecera.save()
    return redirect(url_for("consultas.modificacion_productos_presupuesto", id_presupuesto = id_presupuesto))  


@consultas_bp.route("/consultas/anulapresupuesto/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def anula_presupuesto(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    if cabecera.estado == 2:
        flash ("El presupuesto ya está vencido no se puede anular", "alert-danger") 
        return redirect(url_for("consultas.consulta_presupuestos"))
    cabecera.estado = 3
    cabecera.save()
    
    return redirect(url_for("consultas.consulta_presupuestos"))  