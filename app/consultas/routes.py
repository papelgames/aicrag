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
from .forms import BusquedaForm, CabeceraPresupuesto, ProductosPresupuesto

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


datos_cliente =[]
lista_productos_presupuesto = []

@consultas_bp.route("/consultas/altapresupuesto/", methods = ['GET', 'POST'])
@login_required
def alta_presupuesto():
    form = BusquedaForm()
    form2 = CabeceraPresupuesto()
    form3 = ProductosPresupuesto()
    # print (g.lista_productos_seleccion)
    
    lista_productos_seleccion = []
    
    if len(datos_cliente) == 0:
        print ("entro")
        if form2.validate_on_submit():
            nombre_cliente = form2.nombre_cliente.data
            correo_electronico = form2.correo_electronico.data
            fecha_vencimiento = form2.fecha_vencimiento.data
            
            datos_cliente.append(nombre_cliente)
            datos_cliente.append(correo_electronico)
            datos_cliente.append(fecha_vencimiento)

            
            return render_template("consultas/alta_presupuesto.html", form2 = form2, form = form, datos_cliente=datos_cliente )
    else:
        if form.validate_on_submit():
            buscar = form.buscar.data
            if buscar.isdigit() == True:
                lista_de_productos = Productos.get_by_codigo_de_barras(buscar)
                for registro in lista_de_productos:
                    lista_productos_seleccion.append([registro.Productos.id, registro.Productos.descripcion, registro.Productos.importe, registro.Proveedores.nombre])

            elif buscar == "":
                pass
            else:
                lista_de_productos = Productos.get_like_descripcion(buscar)
                for registro in lista_de_productos:
                    lista_productos_seleccion.append([registro.Productos.id, registro.Productos.descripcion, registro.Productos.importe, registro.Proveedores.nombre])
                print (lista_productos_seleccion)
            return render_template("consultas/alta_presupuesto.html", form = form, form2 = form2, form3 = form3, lista_productos_seleccion = lista_productos_seleccion , datos_cliente = datos_cliente )
        if form3.validate_on_submit():
            print("entro qa")
            id = form3.id.data
            descripcion = form3.descripcion.data
            cantidad = form3.cantidad.data
            importe = form3.importe.data
            print (cantidad)
            lista_productos_presupuesto.append([id, descripcion, cantidad , importe ])
           
            return render_template("consultas/alta_presupuesto.html", form = form, form2 = form2, form3 = form3, lista_productos_seleccion = lista_productos_seleccion , datos_cliente = datos_cliente )
                    
        
            #falta calcular la ganancia a aplicarle a cada producto.     
        
    return render_template("consultas/alta_presupuesto.html", form = form, form2 = form2, form3 = form3, lista_productos_seleccion=lista_productos_seleccion , datos_cliente = datos_cliente )
             

