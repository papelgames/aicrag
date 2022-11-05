import logging
from operator import setitem
import os
from datetime import date, datetime
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
    #falta calcular la ganancia a aplicarle a cada producto.     
    return render_template("consultas/consulta_productos.html", form = form, lista_de_productos=lista_de_productos )

datos_cliente =[]
lista_productos_presupuesto = []

@consultas_bp.route("/consultas/consultapresupuestos/", methods = ['GET', 'POST'])
@login_required
def consulta_presupuestos():
    cabecera = CabecerasPresupuestos.get_all()
    now = datetime.now()
    print (now)
    return render_template("consultas/consulta_presupuestos.html", cabecera = cabecera, now = now)

@consultas_bp.route("/consultas/presupuesto/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def presupuesto(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    productos = Presupuestos.get_by_id(id_presupuesto)
    vencimiento_si_no = control_vencimiento(cabecera.fecha_vencimiento)
    if vencimiento_si_no == "VENCIDO" and cabecera.estado != 2:
        cabecera.estado = 2
        cabecera.save()

    return render_template("consultas/presupuesto.html", cabecera = cabecera, productos = productos, vencimiento_si_no = vencimiento_si_no)




@consultas_bp.route("/consultas/altapresupuesto/", methods = ['GET', 'POST'])
@login_required
def alta_presupuesto():
    form2 = CabeceraPresupuestoForm()
    form = ProductosPresupuestoForm()
    lista_productos_seleccion = []
    
    if len(datos_cliente) == 0:
       if form2.validate_on_submit():
            nombre_cliente = form2.nombre_cliente.data
            correo_electronico = form2.correo_electronico.data
            fecha_vencimiento = form2.fecha_vencimiento.data
            
            datos_cliente.append(nombre_cliente)
            datos_cliente.append(correo_electronico)
            datos_cliente.append(fecha_vencimiento)
            
            return render_template("consultas/alta_presupuesto.html", form2 = form2, form = form, datos_cliente=datos_cliente )            
                 
    if form.validate_on_submit(): 
        if form.condicion.data == "a":
            id = form.id.data
            descripcion = form.descripcion.data
            cantidad = form.cantidad.data
            importe = form.importe.data
            
            if id != None:
                lista_productos_presupuesto.append([id, descripcion, cantidad , importe ])
            return render_template("consultas/alta_presupuesto.html", form = form, form2 = form2, lista_productos_presupuesto=lista_productos_presupuesto, lista_productos_seleccion = lista_productos_seleccion , datos_cliente = datos_cliente )    
        
        elif form.condicion.data == "d":
            lista_productos_presupuesto.pop(int(form.registro.data)-1)
            return render_template("consultas/alta_presupuesto.html", form = form, form2 = form2, lista_productos_presupuesto=lista_productos_presupuesto, lista_productos_seleccion = lista_productos_seleccion , datos_cliente = datos_cliente )
        
        elif form.condicion.data == "s":
            #presupuesto = Presupuestos()
            
            suma_importe_total = 0 #falta la sumatoria

            fecha_vencimiento = datos_cliente[2]
            nombre_cliente = datos_cliente[0]
            correo_electronico = datos_cliente[1]
            importe_total = suma_importe_total
            
            cabecera = CabecerasPresupuestos(fecha_vencimiento = fecha_vencimiento,
                                             nombre_cliente = nombre_cliente,
                                             correo_electronico = correo_electronico,
                                             importe_total = importe_total,
                                             estado = 1,
                                             usuario_alta = current_user.email,
                                             usuario_modificacion = current_user.email
                                             )           
            
            cabecera.save()
            for registro in lista_productos_presupuesto:
                # id, 0 
                # descripcion, 1 
                # cantidad , 2
                # importe 3
                
                presupuesto = Presupuestos(id_cabecera_presupuesto = cabecera.id,
                                           id_producto = registro[0],
                                           cantidad = registro[2],
                                           descripcion = registro[1],
                                           importe = registro[3],
                                           usuario_alta = current_user.email,
                                           usuario_modificacion = current_user.email
                                           )
                presupuesto.save()
              
            datos_cliente.clear()
            lista_productos_presupuesto.clear() 
            flash("El presupuesto se ha grabado", "alert-success")
            return redirect(url_for("consultas.presupuesto", id_presupuesto = cabecera.id))
            
        elif form.condicion.data == "c":
            datos_cliente.clear()
            lista_productos_presupuesto.clear() 

            return redirect(url_for("consultas.consulta_presupuestos"))

        buscar = form.buscar.data
        if buscar.isdigit() == True:
            lista_de_productos = Productos.get_by_codigo_de_barras(buscar)
            for registro in lista_de_productos:
                lista_productos_seleccion.append([registro.Productos.id, registro.Productos.descripcion, registro.Productos.importe, registro.Proveedores.nombre])
        elif buscar == "":
            #corregir este mensaje cuando se graba vacio el nombre del clienete
            flash("Escriba el nombre de un producto", "alert-warning")
        else:
            lista_de_productos = Productos.get_like_descripcion(buscar)
            for registro in lista_de_productos:
                lista_productos_seleccion.append([registro.Productos.id, registro.Productos.descripcion, registro.Productos.importe, registro.Proveedores.nombre])
            return render_template("consultas/alta_presupuesto.html", form = form, form2 = form2, lista_productos_presupuesto=lista_productos_presupuesto, lista_productos_seleccion = lista_productos_seleccion , datos_cliente = datos_cliente )
    
    
            #falta calcular la ganancia a aplicarle a cada producto.     
    
    return render_template("consultas/alta_presupuesto.html", form = form, form2 = form2, lista_productos_presupuesto=lista_productos_presupuesto, lista_productos_seleccion = lista_productos_seleccion, datos_cliente = datos_cliente  )
             
@consultas_bp.route("/consultas/modificaciondatoscliente/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def modificacion_datos_cliente(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    
    form = CabeceraPresupuestoForm()
    
    if cabecera.estado == 2:
        flash ("El presupuesto se encuentra vencido", "alert-warning" )
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  

    if form.validate_on_submit():
        cabecera.correo_elecronico = form.correo_electronico.data
        cabecera.fecha_vencimiento = form.fecha_vencimiento.data
        cabecera.save()
        flash("Se han actualizado los datos correctamente", "alert-success")            
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  


    return render_template("consultas/modificacion_datos_cliente.html", form = form, cabecera = cabecera)

  
@consultas_bp.route("/consultas/modificacionproductospresupuesto/<int:id_presupuesto>", methods = ['GET', 'POST'])
@login_required
def modificacion_productos_presupuesto(id_presupuesto):
    cabecera = CabecerasPresupuestos.get_by_id(id_presupuesto)
    
    form = CabeceraPresupuestoForm()
    
    if cabecera.estado == 2:
        flash ("El presupuesto se encuentra vencido", "alert-warning" )
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  

    if form.validate_on_submit():
        cabecera.correo_elecronico = form.correo_electronico.data
        cabecera.fecha_vencimiento = form.fecha_vencimiento.data
        cabecera.save()
        flash("Se han actualizado los datos correctamente", "alert-success")            
        return redirect(url_for("consultas.presupuesto", id_presupuesto = id_presupuesto))  


    return render_template("consultas/modificacion_productos_presupuesto.html", form = form, cabecera = cabecera)

        