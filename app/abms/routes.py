# from fcntl import F_SEAL_SEAL
# from genericpath import exists
# from itertools import product
import logging
# from math import fabs
# from operator import truediv
import os
#from types import TracebackType

from flask import render_template, redirect, url_for, request, current_app, abort, make_response
from flask.helpers import flash
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required, nocache, not_initial_status
from app.auth.models import Users
from app.models import Productos, Proveedores, Estados, Permisos, Personas, Roles
from . import abms_bp
from .forms import BusquedaForm, ProductosForm, ProveedoresForm, ProductosMasivosForm, AltaDatosPersonasForm, RolesForm, PermisosForm, PermisosSelectForm, EstadosForm, DatosPersonasForm
#from app.common.mail import send_email
from time import strftime, gmtime

from app.common.funciones import listar_endpoints
from rq import Worker


logger = logging.getLogger(__name__)

def proveedores_select(archivo_si_no = None):
    if archivo_si_no == None:
        proveedores = Proveedores.get_all()
    else:
        proveedores = Proveedores.get_by_archivo_si_no(archivo_si_no)

    select_proveedor =[( '','Seleccionar proveedor')]
    for rs in proveedores:
        sub_select_proveedor = (str(rs.id), rs.nombre)
        select_proveedor.append(sub_select_proveedor)
    return select_proveedor

def columnas_excel():
    select_excel =[( '','Seleccionar columna'),( 'A','A'),( 'B','B'),( 'C','C'),( 'D','D'),( 'E','E'),( 'F','F'),( 'G','G'),('H','H'),('I','I'),('J','J'),( 'K','K'),('L','L')]
    return select_excel

#creo una tupla para usar en el campo select del form que quiera que necesite los tipo de gestiones
def permisos_select(id_rol):
    permisos = Permisos.get_permisos_no_relacionadas_roles(id_rol)
    select_permisos =[( '','Seleccionar permiso')]
    for rs in permisos:
        sub_select_permisos = (str(rs.id), rs.descripcion)
        select_permisos.append(sub_select_permisos)
    return select_permisos

@abms_bp.route("/abms/altaindividual", methods = ['GET', 'POST'])
@login_required
@not_initial_status
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
                              usuario_alta = current_user.username,
                              usuario_modificacion = current_user.username
                              )
        
        producto.save()
        flash("Producto dado de alta correctamente", "alert-success")
        return redirect(url_for("public.index"))
    return render_template("abms/administracion_producto.html", form=form)

@abms_bp.route("/abms/busquedaproducto/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def busqueda_productos(criterio = ""):
    criterio = request.args.get('criterio','')

    form = BusquedaForm()
    lista_de_productos = []
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("abms.busqueda_productos", criterio = buscar))
    
    if criterio.isdigit() == True:
        lista_de_productos = Productos.get_by_codigo_de_barras(criterio)
    elif criterio == "":
        pass
    else:
        lista_de_productos = Productos.get_like_descripcion_all_paginated(criterio, page, per_page)
        if len(lista_de_productos.items) == 0:
            lista_de_productos =[] 
    return render_template("abms/busqueda_productos.html", form = form, lista_de_productos=lista_de_productos, criterio = criterio )

@abms_bp.route("/abms/modificacionproducto", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def modificacion_producto():
    id_producto = request.args.get('id_producto','')
    
    if id_producto == "":
        return redirect(url_for("abms.busqueda_productos"))
    producto = Productos.get_by_id(id_producto)
    print(producto.es_servicio)
    form=ProductosForm(obj=producto)
    form.id_proveedor.choices = proveedores_select()

    if form.validate_on_submit():
        form.populate_obj(producto)
        producto.id_ingreso = str(strftime('%d%m%y%H%m%s', gmtime()))
        producto.usuario_modificacion = current_user.username

        producto.save()
        flash("Producto actualizado correctamente", "alert-success")
        return redirect(url_for("public.index"))
    return render_template("abms/administracion_producto.html", form=form, producto = producto)

@abms_bp.route("/abms/eliminarproducto/<int:id_producto>", methods = ['GET', 'POST'])
@login_required
def eliminar_producto_id(id_producto):
    producto = Productos.get_by_id(id_producto)
    producto.delete()

    return redirect(url_for("abms.busqueda_productos"))

@abms_bp.route("/abms/altaproveedor", methods = ['GET', 'POST'])
@login_required
@not_initial_status
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
                                usuario_alta = current_user.username,
                                usuario_modificacion = current_user.username
                                )
            
        proveedor.save()
        flash("Proveedor dado de alta correctamente", "alert-success")
        return redirect(url_for("public.index"))

    return render_template("abms/administrcion_proveedor.html", form = form)

@abms_bp.route("/abms/busquedaproveedor/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def busqueda_proveedores(criterio = ""):
  
    lista_de_proveedores = Proveedores.get_all()
     
    return render_template("abms/busqueda_proveedores.html", lista_de_proveedores=lista_de_proveedores )

@abms_bp.route("/abms/modificacionproveedor", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def modificacion_proveedor():
    id_proveedor = request.args.get('id_proveedor','')

    if id_proveedor == "":
        return redirect(url_for("abms.busqueda_proveedores"))
    proveedor = Proveedores.get_by_id(id_proveedor)
    form= ProveedoresForm(obj=proveedor)
    form.columna_id_lista_proveedor.choices = columnas_excel()
    form.columna_codigo_de_barras.choices = columnas_excel()
    form.columna_descripcion.choices = columnas_excel()
    form.columna_importe.choices = columnas_excel()
    form.columna_utilidad.choices = columnas_excel()

    if form.validate_on_submit():
        form.populate_obj(proveedor)
        proveedor.usuario_modificacion = current_user.username
        proveedor.save()
        flash("Proveedor actualizado correctamente", "alert-success")
        return redirect(url_for("public.index"))

    return render_template("abms/administrcion_proveedor.html", form = form, proveedor = proveedor)

@abms_bp.route("/abms/altamasiva", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def alta_masiva():
    form = ProductosMasivosForm()
    form.id_proveedor.choices = proveedores_select(True)

    if form.validate_on_submit():
        archivo = form.archivo.data
        id_proveedor = form.id_proveedor.data
        #falta validar que sea un proveedor que actualiza por archivo
        proveedor = Proveedores.get_by_id(id_proveedor)
        if archivo:
            archivo_name = secure_filename(proveedor.nombre +".xlsx")
            archivo_dir = current_app.config['ARCHIVOS_DIR']
            os.makedirs(archivo_dir, exist_ok=True)
            file_path = os.path.join(archivo_dir, archivo_name )
            archivo.save(file_path)

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

            secuencia = 0
            control_proveedor = False
            # controlo que el archivo corresponda al proveedor
            for id in rango_id_lista_proveedor:
                if secuencia == 15:
                        break
                if str(id.value).upper() == str(columnas[1]).upper():
                        control_proveedor = True
                        break
                secuencia +=1
            if control_proveedor == True:
                email = current_user.username
                job = current_app.task_queue.enqueue('app.tareas.in_lista_masiva', file_path = file_path, id_proveedor = id_proveedor, email= email, job_timeout = 3600)
                job.get_id()
                
                flash("Ha iniciado la actualización masiva de precios de: " + proveedor.nombre , "alert-success")
                return redirect(url_for("public.index"))
            else:
                flash("El archivo seleccionado no corresponde al proveedor: " + proveedor.nombre , "alert-warning")
    return render_template("abms/alta_masiva.html", form=form)

@abms_bp.route("/abms/agenda", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def agenda():
    queue = current_app.task_queue
    
    workers = Worker.all(queue=queue)
    worker = workers[0]
    if worker.state == 'busy':
        tarea_actual = worker.get_current_job()
    else:
        tarea_actual = 'inactiva'
        flash("Sin tareas pendientes", "alert-success")
    tareas_pendientes = queue.jobs
    
    return render_template("abms/agenda.html", tarea_actual=tarea_actual, tareas_pendientes=tareas_pendientes)


@abms_bp.route("/abms/altapersonas/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def alta_persona():
    form = AltaDatosPersonasForm()                                                                                                                   

    if form.validate_on_submit():
        descripcion_nombre = form.descripcion_nombre.data
        correo_electronico = form.correo_electronico.data
        telefono = form.telefono.data
        cuit = form.cuit.data
        tipo_persona = form.tipo_persona.data 
        nota = form.nota.data
        persona_por_cuit = Personas.get_by_cuit(cuit)
        if persona_por_cuit:
            flash ("Ya existe la persona","alert-warning")
            return redirect(url_for('public.index'))

        persona = Personas(descripcion_nombre= descripcion_nombre,
                           correo_electronico = correo_electronico,
                           telefono = telefono,
                           cuit = cuit,
                           tipo_persona = tipo_persona,
                           nota = nota,
                           usuario_alta = current_user.username)
        persona.save()
        flash("Se ha creado la persona correctamente.", "alert-success")
        return redirect(url_for('consultas.consulta_personas'))
    return render_template("abms/datos_persona.html", form = form)


@abms_bp.route("/abms/actualizacionpersona/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def actualizacion_persona():
    id_persona = request.args.get('id_persona','')
    persona = Personas.get_by_id(id_persona)
    form=DatosPersonasForm(obj=persona)
    persona_original =persona.cuit
    if form.validate_on_submit():
        persona_por_cuit = Personas.get_by_cuit(form.cuit.data)
        form.populate_obj(persona)
        persona.usuario_modificacion = current_user.username
        if persona_por_cuit and persona_por_cuit.cuit != persona_original:
            flash ("Ya existe la persona","alert-warning")
            return redirect(url_for('public.index'))
        persona.save()
        flash("Se ha actualizado la persona correctamente.", "alert-success")
        return redirect(url_for('consultas.consulta_personas'))
    
    for campo in list(request.form.items())[1:]:
        data_campo = getattr(form,campo[0]).data
        setattr(persona,campo[0], data_campo)
    return render_template("abms/datos_persona.html", form=form, persona = persona)


@abms_bp.route("/abms/altapermisos/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_permiso():
    form = PermisosForm()
    permisos = Permisos.get_all()
    if form.validate_on_submit():
        permisos_obj = []
        
        for item in listar_endpoints(current_app):
            check_permiso = Permisos.get_by_descripcion(item.get('descripcion'))
            if not check_permiso:
                permiso = Permisos(**item)
                permisos_obj.append(permiso)
        if permisos_obj:
            q_altas = len(permisos_obj)
            permiso.save_masivo(permisos_obj)
            flash(f"Se han creado {q_altas} permisos", "alert-success")
        else:
            flash(f"No hay nuevos permisos", "alert-warning")
        return redirect(url_for('abms.alta_permiso'))

    return render_template("abms/alta_permisos.html", form=form, permisos=permisos)

@abms_bp.route("/abms/crearroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def crear_roles():
    form = RolesForm()
    
    todos_los_roles = Roles.get_all()

    if form.validate_on_submit():
        rol = Roles(descripcion = form.descripcion.data.upper(),
                    usuario_alta = current_user.username
        )
        rol.save() 
        
        flash ('Rol creado correctamente', 'alert-success')
        return redirect(url_for('abms.crear_roles'))
    return render_template("abms/alta_roles.html", form=form, todos_los_roles=todos_los_roles)

@abms_bp.route("/abms/asignarpermisosroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignar_permisos_roles():
    id_rol = request.args.get('id_rol','')
    permisos_en_rol = Roles.get_by_id(id_rol)
    
    form = PermisosSelectForm()
    form.id_permiso.choices=permisos_select(id_rol)
    
    if form.validate_on_submit():
        permiso = Permisos.get_by_id(form.id_permiso.data)
        for permiso_en_rol in permisos_en_rol.permisos:
            if permiso_en_rol.id == int(form.id_permiso.data):
                flash ('El rol ya tiene el permiso', 'alert-warning')
                return redirect(url_for('abms.asignar_permisos_roles', id_rol = id_rol))    
        
        permisos_en_rol.permisos.append(permiso)
        permisos_en_rol.save()

        flash ('Permiso asignado correctamente del rol', 'alert-success')
        return redirect(url_for('abms.asignar_permisos_roles', id_rol = id_rol))
    return render_template("abms/alta_permisos_en_roles.html", form=form, permisos_en_rol=permisos_en_rol)

@abms_bp.route("/abms/eliminarpermisosroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permisos_roles():
    id_rol = request.args.get('id_rol','')
    id_permiso = request.args.get('id_permiso','')
    rol = Roles.get_by_id(id_rol)
    permiso = Permisos.get_by_id(id_permiso)
    rol.permisos.remove(permiso)
    rol.save()  
    
    flash ('Permiso eliminado correctamente del rol', 'alert-success')
    return redirect(url_for('abms.asignar_permisos_roles', id_rol = id_rol))

@abms_bp.route("/abms/eliminarpermisos/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permiso():
    id_permiso = request.args.get('id_permiso','')
    permiso = Permisos.get_by_id(id_permiso)
    permiso.delete()
    
    flash ('Permiso eliminado correctamente', 'alert-success')
    return redirect(url_for('abms.alta_permiso'))

@abms_bp.route("/abms/altaestados/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_estados():
    form = EstadosForm()
    
    if form.validate_on_submit():
        clave = form.clave.data
        descripcion = form.descripcion.data
        tabla = form.tabla.data
        inicial = form.inicial.data
        final = form.final.data
        
        estado = Estados(clave=clave,
                         descripcion=descripcion,
                         tabla=tabla,
                         inicial=inicial,
                         final=final,
                         usuario_alta=current_user.username)
        
        estado.save()
        flash("Nuevo estado creado", "alert-success")
        return redirect(url_for('abms.alta_estados'))
    #falta paginar tareas
    estados = Estados.get_all()    
    return render_template("abms/alta_estados.html", form=form, estados=estados)