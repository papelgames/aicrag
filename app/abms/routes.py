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
from .forms import ProductosForm, ProveedoresForm, ProductosMasivosForm

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
    #select_excel =[( '','Seleccionar columna'),( '0','A'),( '1','B'),( '2','C'),( '3','D'),( '4','E'),( '5','F'),( '6','G'),('7','H'),('8','I'),('9','J'),( '10','K'),('11','L')]
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
                              id_ingreso = str(strftime('%d%m%y%H%m%s', gmtime())),
                              usuario_alta = current_user.email,
                              usuario_modificacion = current_user.email
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
                                incluye_iva=int(incluye_iva),
                                usuario_alta = current_user.email,
                                usuario_modificacion = current_user.email
                                )
            
        proveedor.save()
        flash("Proveedor dado de alta correctamente", "alert-success")
        return redirect(url_for("public.index"))

    return render_template("abms/alta_proveedor.html", form = form)


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
        
        proveedor = Proveedores.get_by_id(form.id_proveedor.data)

        import openpyxl 
        documento = openpyxl.load_workbook(os.path.abspath(file_path), data_only= True)
        ws = documento.active
        
        columnas = [proveedor.nombre,
                    proveedor.formato_id,
                    proveedor.columna_id_lista_proveedor, 
                    proveedor.columna_codigo_de_barras, 
                    proveedor.columna_descripcion,
                    proveedor.columna_importe ]
        
        rango_id_lista_proveedor =  ws[columnas[2]]
        rango_codigo_de_barras =  ws[columnas[3]]
        rango_descripcion =  ws[columnas[4]]
        rango_importe =  ws[columnas[5]]
        registros_nuevos = 0
        registros_repetidos = 0
        registros_total = 0
        '''falta grabar si no existe el registro en la base de datos y actualizar si existe y hay cambios
        '''
        #armo la matriz mat 
        mat = []
        for registro in rango_id_lista_proveedor:
            mat.append([registro.value])
        len_mat = len(mat)
        secuencia = 0
        for registro in rango_codigo_de_barras:
            if secuencia != len_mat :
                mat[secuencia].append(registro.value)
                secuencia += 1
        secuencia = 0 
        for registro in rango_descripcion:
            if secuencia != len_mat :
                mat[secuencia].append(registro.value)
                secuencia += 1
        secuencia = 0 
        for registro in rango_importe:
            if secuencia != len_mat :
                mat[secuencia].append(registro.value)
                secuencia += 1
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
        id_ingreso = str(strftime('%d%m%y%H%m%s', gmtime()))
        if control_proveedor == True:
            ##hacer  update, etc
        #inserto los registros que no existen
            for id in mat:
                # pass
                if id[0] != None and id[0] != columnas[1]: 
                    producto = Productos(codigo_de_barras = id[1],
                                        id_proveedor = form.id_proveedor.data,
                                        id_lista_proveedor = id[0],
                                        descripcion = id[2],
                                        importe = id[3],
                                        cantidad_presentacion = 1,
                                        id_ingreso = id_ingreso,
                                        usuario_alta = current_user.email,
                                        usuario_modificacion = current_user.email
                                        )
                    #ver como hacer un add y un solo commit
                    producto.save()
            flash ('El archivo de ' + columnas[0] + ' se procesó correctamente', "alert-success")
            return redirect(url_for("public.index"))
        else:
            flash ('El archivo no pertenece a ' + columnas[0], "alert-warning")
            return redirect(url_for("public.index"))
        
        '''
           registros_total +=1
            if Recuperos.query.filter_by (rama = campo[0].value).first() and \
                Recuperos.query.filter_by (siniestro = campo[1].value).first():
                registros_repetidos += 1
                continue
            rama = campo[0].value 
            siniestro = campo[1].value
            desc_siniestro = campo[2].value
            fe_ocurrencia = campo[3].value
            importe_pagado = campo[4].value
            estado = 1
            
            registro_recupero = Recuperos(rama = rama,\
                                            siniestro = siniestro,\
                                            desc_siniestro = desc_siniestro,\
                                            fe_ocurrencia = fe_ocurrencia,\
                                            importe_pagado =importe_pagado,\
                                            estado = estado)
            db.session.add(registro_recupero)
            registros_nuevos += 1
        db.session.commit()
        '''
    return render_template("abms/alta_masiva.html", form=form)
