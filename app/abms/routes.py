import logging
from math import fabs
import os

from flask import render_template, redirect, url_for, abort, current_app
from flask.helpers import flash
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required
from app.auth.models import User
from app.models import Productos, Proveedores
from . import abms_bp
from .forms import ProductosForm, ProveedoresForm

from app.common.mail import send_email
from time import strftime, gmtime

logger = logging.getLogger(__name__)

def proveedores_select():
    proveedores = Proveedores.get_all()
    select_proveedor =[( '','Seleccionar tipo de bien')]
    for rs in proveedores:
        sub_select_proveedor = (str(rs.id), rs.nombre)
        select_proveedor.append(sub_select_proveedor)
    return select_proveedor


def columnas_excel():
    select_excel =[( '','Seleccionar columna'),( '0','A'),( '1','B'),( '2','C'),( '3','D'),( '4','E'),( '5','F'),( '6','G'),('7','H'),('8','I'),('9','J'),( '10','K'),('11','L')]
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
        cantidad_presentacion = form.cantidad_presentacion.data

        producto = Productos(codigo_de_barras=codigo_de_barras,
                              id_proveedor=id_proveedor,
                              id_lista_proveedor=id_lista_proveedor,
                              descripcion=descripcion,
                              importe=importe,
                              cantidad_presentacion=cantidad_presentacion,
                              id_ingreso = str(strftime('%d%m%y%H%m%s', gmtime()))
                              )
        print (strftime('%d%m%y%H%m%s', gmtime()))
        producto.save()
        flash("Producto dado de alta correctamente", "alert-success")
        return redirect(url_for("public.index"))
    return render_template("abms/alta_individual.html", form=form)

@abms_bp.route("/abms/altaproveedor", methods = ['GET', 'POST'])
@login_required
def alta_proveedor():
    form = ProveedoresForm()
    form.columna_id_lista_proveedor.choices = columnas_excel()
    form.columna_codigo_de_barras.choices = columnas_excel()
    form.columna_descripcion.choices = columnas_excel()
    form.columna_importe.choices = columnas_excel()

    if form.validate_on_submit():
        nombre = form.nombre.data
        correo_electronico = form.correo_electronico.data
        archivo_si_no = form.archivo_si_no.data
        formato_id = form.formato_id.data
        columna_id_lista_proveedor = form.columna_id_lista_proveedor.data
        columna_codigo_de_barras = form.columna_codigo_de_barras.data
        columna_descripcion = form.columna_descripcion.data
        columna_importe = form.columna_importe.data
        incluye_iva = form.incluye_iva.data

        proveedor = Proveedores(nombre=nombre, 
                                correo_electronico=correo_electronico, 
                                archivo_si_no=int(archivo_si_no), 
                                formato_id=formato_id,
                                columna_id_lista_proveedor=columna_id_lista_proveedor,
                                columna_codigo_de_barras=columna_codigo_de_barras,
                                columna_descripcion=columna_descripcion,
                                columna_importe=columna_importe,
                                incluye_iva=int(incluye_iva)
                                )
            
        proveedor.save()
        flash("Proveedor dado de alta correctamente", "alert-success")
        return redirect(url_for("public.index"))

    return render_template("abms/alta_proveedor.html", form = form)