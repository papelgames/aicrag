from fcntl import F_SEAL_SEAL
from genericpath import exists
from itertools import product
import logging
from math import fabs
from operator import truediv
import os
from types import TracebackType

from flask import render_template, redirect, url_for, abort, current_app
from flask.helpers import flash
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required
from app.auth.models import User
from app.models import Productos, Proveedores
from . import abms_bp
from .forms import BusquedaForm, ProductosForm, ProveedoresForm, ProductosMasivosForm, ProveedoresConsultaForm

from app.common.mail import send_email
from time import strftime, gmtime

logger = logging.getLogger(__name__)


def proveedores_select():
    proveedores = Proveedores.get_all()
    select_proveedor =[( '','Seleccionar proveedor')]
    for rs in proveedores:
        sub_select_proveedor = (str(rs.id), rs.nombre)
        select_proveedor.append(sub_select_proveedor)
    return select_proveedor


def columnas_excel():
    select_excel =[( '','Seleccionar columna'),( 'A','A'),( 'B','B'),( 'C','C'),( 'D','D'),( 'E','E'),( 'F','F'),( 'G','G'),('H','H'),('I','I'),('J','J'),( 'K','K'),('L','L')]
    return select_excel

@abms_bp.route("/abms/altaindividual", methods = ['GET', 'POST'])
@login_required
def alta_individual():
    form=ProductosForm()
    form.id_proveedor.choices = proveedores_select()
    
    if form.validate_on_submit():
        codigo_de_barras = form.codigo_de_barras.data
        id_proveedor = form.id_proveedor.data
        id_lista_proveedor = form.id_lista_proveedor.data
        descripcion = form.descripcion.data
        importe = form.importe.data
        utilidad = form.utilidad.data
        cantidad_presentacion = form.cantidad_presentacion.data
        es_servicio = form.es_servicio.data

        producto = Productos(codigo_de_barras=codigo_de_barras,
                              id_proveedor=id_proveedor,
                              id_lista_proveedor=id_lista_proveedor,
                              descripcion=descripcion,
                              importe=importe,
                              cantidad_presentacion=cantidad_presentacion,
                              id_ingreso = str(strftime('%d%m%y%H%m%s', gmtime())),
                              utilidad = utilidad,
                              es_servicio = bool(es_servicio),
                              usuario_alta = current_user.email,
                              usuario_modificacion = current_user.email
                              )
        
        producto.save()
        flash("Producto dado de alta correctamente", "alert-success")
        return redirect(url_for("public.index"))
    return render_template("abms/alta_individual.html", form=form)

@abms_bp.route("/abms/busquedaproducto/<criterio>", methods = ['GET', 'POST'])
@abms_bp.route("/abms/busquedaproducto/", methods = ['GET', 'POST'])
@login_required
def busqueda_productos(criterio = ""):
    form = BusquedaForm()
    lista_de_productos = []
    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("abms.busqueda_productos", criterio = buscar))
    
    if criterio.isdigit() == True:
        lista_de_productos = Productos.get_by_codigo_de_barras(criterio)
    elif criterio == "":
        pass
    else:
        lista_de_productos = Productos.get_like_descripcion(criterio)
        
    return render_template("abms/busqueda_productos.html", form = form, lista_de_productos=lista_de_productos )

@abms_bp.route("/abms/modificacionproducto/<int:id_producto>", methods = ['GET', 'POST'])
@abms_bp.route("/abms/modificacionproducto", methods = ['GET', 'POST'])
@login_required
def modificacion_producto(id_producto = ""):
    if id_producto == "":
        return redirect(url_for("abms.busqueda_productos"))

    form=ProductosForm()
    form.id_proveedor.choices = proveedores_select()
    
    producto = Productos.get_by_id(id_producto)

    if producto.es_servicio == True:
        producto.es_servicio = '1'
    else: 
        producto.es_servicio = '0'

    if form.validate_on_submit():

        
        producto.codigo_de_barras = form.codigo_de_barras.data
        producto.id_proveedor = form.id_proveedor.data
        producto.id_lista_proveedor = form.id_lista_proveedor.data
        producto.descripcion = form.descripcion.data
        producto.importe = form.importe.data
        producto.utilidad = form.utilidad.data
        producto.es_servicio = bool(form.es_servicio.data)
        producto.cantidad_presentacion = form.cantidad_presentacion.data
        producto.id_ingreso = str(strftime('%d%m%y%H%m%s', gmtime()))
        producto.usuario_modificacion = current_user.email

        producto.save()
        flash("Producto actualizado correctamente", "alert-success")
        return redirect(url_for("public.index"))
    return render_template("abms/modificacion_producto.html", form=form, producto = producto)

@abms_bp.route("/abms/eliminarproducto/<int:id_producto>", methods = ['GET', 'POST'])
@login_required
def eliminar_producto_id(id_producto):
    producto = Productos.get_by_id(id_producto)
    producto.delete()

    return redirect(url_for("abms.busqueda_productos"))

@abms_bp.route("/abms/altaproveedor", methods = ['GET', 'POST'])
@login_required
def alta_proveedor():
    form = ProveedoresForm()
    form.columna_id_lista_proveedor.choices = columnas_excel()
    form.columna_codigo_de_barras.choices = columnas_excel()
    form.columna_descripcion.choices = columnas_excel()
    form.columna_importe.choices = columnas_excel()
    form.columna_utilidad.choices = columnas_excel()

    if form.validate_on_submit():
        nombre = form.nombre.data
        correo_electronico = form.correo_electronico.data
        archivo_si_no = form.archivo_si_no.data
        formato_id = form.formato_id.data
        columna_id_lista_proveedor = form.columna_id_lista_proveedor.data
        columna_codigo_de_barras = form.columna_codigo_de_barras.data
        columna_descripcion = form.columna_descripcion.data
        columna_importe = form.columna_importe.data
        columna_utilidad = form.columna_utilidad.data
        incluye_iva = form.incluye_iva.data

        proveedor = Proveedores(nombre=nombre, 
                                correo_electronico=correo_electronico, 
                                archivo_si_no=int(archivo_si_no), 
                                formato_id=formato_id,
                                columna_id_lista_proveedor=columna_id_lista_proveedor,
                                columna_codigo_de_barras=columna_codigo_de_barras,
                                columna_descripcion=columna_descripcion,
                                columna_importe=columna_importe,
                                columna_utilidad=columna_utilidad,
                                incluye_iva=int(incluye_iva),
                                usuario_alta = current_user.email,
                                usuario_modificacion = current_user.email
                                )
            
        proveedor.save()
        flash("Proveedor dado de alta correctamente", "alert-success")
        return redirect(url_for("public.index"))

    return render_template("abms/alta_proveedor.html", form = form)

@abms_bp.route("/abms/busquedaproveedor/", methods = ['GET', 'POST'])
@login_required
def busqueda_proveedores(criterio = ""):
  
    lista_de_proveedores = Proveedores.get_all()
     
    return render_template("abms/busqueda_proveedores.html", lista_de_proveedores=lista_de_proveedores )

@abms_bp.route("/abms/modificacionproveedor/<id_proveedor>", methods = ['GET', 'POST'])
@abms_bp.route("/abms/modificacionproveedor", methods = ['GET', 'POST'])
@login_required
def modificacion_proveedor(id_proveedor= ""):
    if id_proveedor == "":
        return redirect(url_for("abms.busqueda_proveedores"))

    form= ProveedoresForm()
    proveedor = Proveedores.get_by_id(id_proveedor)
    form.columna_id_lista_proveedor.choices = columnas_excel()
    form.columna_codigo_de_barras.choices = columnas_excel()
    form.columna_descripcion.choices = columnas_excel()
    form.columna_importe.choices = columnas_excel()
    form.columna_utilidad.choices = columnas_excel()

    #modifico los valores booleanos por int porque no me toma boolean para el selectfield
    if proveedor.archivo_si_no == True:
        proveedor.archivo_si_no = '1'
    elif proveedor.archivo_si_no == False:
        proveedor.archivo_si_no = '0'
    else:
        proveedor.archivo_si_no = ''

    if proveedor.incluye_iva == True:
        proveedor.incluye_iva = '1'
    elif proveedor.incluye_iva == False:
        proveedor.incluye_iva = '0'
    else:
        proveedor.incluye_iva = ''

    if form.validate_on_submit():
        proveedor.nombre = form.nombre.data
        proveedor.correo_electronico = form.correo_electronico.data
        proveedor.archivo_si_no = int(form.archivo_si_no.data)
        proveedor.formato_id = form.formato_id.data
        proveedor.columna_id_lista_proveedor = form.columna_id_lista_proveedor.data
        proveedor.columna_codigo_de_barras = form.columna_codigo_de_barras.data
        proveedor.columna_descripcion = form.columna_descripcion.data
        proveedor.columna_importe = form.columna_importe.data
        proveedor.columna_utilidad = form.columna_utilidad.data
        proveedor.incluye_iva = int(form.incluye_iva.data)
        proveedor.usuario_modificacion = current_user.email
        
        proveedor.save()
        flash("Proveedor actualizado correctamente", "alert-success")
        return redirect(url_for("public.index"))

    return render_template("abms/modificacion_proveedor.html", form = form, proveedor = proveedor)

@abms_bp.route("/abms/altamasiva", methods = ['GET', 'POST'])
@login_required
def alta_masiva():
    form = ProductosMasivosForm()
    form.id_proveedor.choices = proveedores_select()

    if form.validate_on_submit():
        archivo = form.archivo.data
        if archivo:
            archivo_name = secure_filename(archivo.filename)
            archivo_dir = current_app.config['ARCHIVOS_DIR']
            os.makedirs(archivo_dir, exist_ok=True)
            file_path = os.path.join(archivo_dir, archivo_name)
            archivo.save(file_path)
        
        #falta validar que sea un proveedor que actualiza por archivo
        proveedor = Proveedores.get_by_id(form.id_proveedor.data)
        
        #abro documento excel
        import openpyxl 
        documento = openpyxl.load_workbook(os.path.abspath(file_path), data_only= True)
        ws = documento.active
        
        #traigo parametria del proveedor
        columnas = [proveedor.nombre,
                    proveedor.formato_id,
                    proveedor.columna_id_lista_proveedor, 
                    proveedor.columna_codigo_de_barras, 
                    proveedor.columna_descripcion,
                    proveedor.columna_importe,
                    proveedor.columna_utilidad ]
        
        #indico que al excel en que columnas el proveedor carga cada dato.
        rango_id_lista_proveedor =  ws[columnas[2]]
        rango_codigo_de_barras =  ws[columnas[3]]
        rango_descripcion =  ws[columnas[4]]
        rango_importe =  ws[columnas[5]]
        rango_utilidad = ws[columnas[6]]
        #falta armar el counter de cada caso.
        registros_nuevos = 0
        registros_repetidos = 0
        registros_total = 0
        #genero la matriz de datos.
        mat = list(zip(rango_id_lista_proveedor, rango_codigo_de_barras, rango_descripcion, rango_importe, rango_utilidad))
        
        secuencia = 0
        control_proveedor = False
        # controlo que el archivo corresponda al proveedor
        for id in rango_id_lista_proveedor:
            if secuencia == 15:
                break
            if id.value == columnas[1]:
                control_proveedor = True
                break
            secuencia +=1
        
        #genero un id unico por subida
        id_ingreso = str(strftime('%d%m%y%H%m%s', gmtime()))
       
        if control_proveedor == True:
        #inserto los registros que no existen
            producto_nuevo = Productos()
            for id in mat:
                if id[0].value != None and id[0].value != columnas[1]: 
                    producto_por_id = Productos.get_by_id_lista_proveedor(id[0].value)
                    if not producto_por_id:
                        if id[4].value == None:
                            utilidad_ = 100
                        else:
                            utilidad_ = id[4].value

                        producto_nuevo = Productos(codigo_de_barras = id[1].value,
                                                    id_proveedor = form.id_proveedor.data,
                                                    id_lista_proveedor = id[0].value,
                                                    descripcion = id[2].value,
                                                    importe = id[3].value,
                                                    utilidad = utilidad_,
                                                    cantidad_presentacion = 1,
                                                    id_ingreso = id_ingreso,
                                                    es_servicio = False,
                                                    usuario_alta = current_user.email,
                                                    usuario_modificacion = current_user.email
                                                    )
                        producto_nuevo.only_add()
                    
                    #actualizo productos que existe si es que tienen un ipmporte distinto al cargado.    
                    if producto_por_id:
                        if producto_por_id.importe != id[3].value:    
                            producto_por_id.importe = id[3].value
                            producto_por_id.usuario_modificacion = current_user.email
                            producto_por_id.id_ingreso = id_ingreso
                            producto_por_id.only_add()
            
            #commiteo las tablas
            if producto_por_id:
                producto_por_id.save()
            producto_nuevo.only_save()
            
            #mejorar un poco a donde redirigir
            flash ('El archivo de ' + columnas[0] + ' se proces?? correctamente', "alert-success")
            return redirect(url_for("public.index"))
        else:
            flash ('El archivo no pertenece a ' + columnas[0], "alert-warning")
            return redirect(url_for("public.index"))
 
    return render_template("abms/alta_masiva.html", form=form)
