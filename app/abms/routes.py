import logging
import os

from flask import render_template, redirect, url_for, abort, current_app
from flask.helpers import flash
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required
from app.auth.models import User
from app.models import Compras, Productos, CabecerasPresupuestos, Presupuestos, Parametros, Proveedores
from . import abms_bp
from .forms import TareasForm, AccionesForm, TareasAccionesForm

from app.common.mail import send_email

from datetime import datetime, time

logger = logging.getLogger(__name__)


def estados_select(tabla):
    estados = Estados.get_by_estado_tabla(tabla)
    select_estado =[( '','Seleccionar estado')]
    for rs in estados:
        sub_select_estado = (str(rs.id), rs.desc_estado)
        select_estado.append(sub_select_estado)
    return select_estado

def tareas_select():
    tareas = Tareas.get_all()
    select_tarea =[( '','Seleccionar tarea')]
    for rs in tareas:
        sub_select_tarea = (str(rs.id), rs.descripcion)
        select_tarea.append(sub_select_tarea)
    return select_tarea

def accion_select():
    acciones = Acciones.get_all()
    select_accion =[( '','Seleccionar acción')]
    for rs in acciones:
        sub_select_accion = (str(rs.id), rs.descripcion)
        select_accion.append(sub_select_accion)
    return select_accion

@abms_bp.route("/abms/tareas/alta", methods = ['GET', 'POST'])
@login_required
def alta_tareas():
    form = TareasForm()

    if form.validate_on_submit():
        descripcion = form.descripcion.data
        vencimiento = form.vencimiento.data
        modulo_inicial = form.modulo_inicial.data

        alta = Tareas(descripcion = descripcion,
                      vencimiento = vencimiento,
                      modulo_inicial = modulo_inicial
        )
        alta.save()
        flash ("Se ha guardado correctamente", "alert-success")
        return redirect(url_for("abms.tareas"))
        
    return render_template("abms/alta_tarea.html", form = form)



@abms_bp.route("/abms/tareas", methods = ['GET', 'POST'])
@login_required
def tareas():
    tareas = Tareas.get_all()
    
    return render_template("abms/tareas.html", tareas = tareas)

@abms_bp.route("/abms/tareas/modificacion/<int:id_tarea>", methods = ['GET', 'POST'])
@login_required
def modificacion_tareas(id_tarea):
    tarea = Tareas.get_by_id(id_tarea)
    form = TareasForm()

    if form.validate_on_submit():
        tarea.descripcion = form.descripcion.data
        tarea.vencimiento = form.vencimiento.data
        tarea.modulo_inicial = form.modulo_inicial.data

        tarea.save()
        flash ("Se ha guardado correctamente", "alert-success")
        return redirect(url_for("abms.tareas"))


    return render_template("abms/modificacion_tarea.html", tarea = tarea, form = form)

@abms_bp.route("/abms/tareas/eliminar/<int:id_tarea>", methods = ['GET', 'POST'])
@login_required
def eliminar_tareas(id_tarea):
    tarea = Tareas.get_by_id(id_tarea)

    tarea.delete()

    return redirect(url_for("abms.tareas"))


@abms_bp.route("/abms/acciones/alta", methods = ['GET', 'POST'])
@login_required
def alta_acciones():
    form = AccionesForm()
    form.estado_recupero.choices = estados_select("acciones")
    form.id_tarea_siguiente.choices = tareas_select()
    form.envia_correo.choices = [('', 'Selecciona si envia correo o no'),('SI', 'Si'),('NO', 'No') ]
   
    if form.validate_on_submit():
        descripcion = form.descripcion.data
        estado_recupero =  form.estado_recupero.data
        envia_correo =  form.envia_correo.data
        id_tarea_siguiente = form.id_tarea_siguiente.data
        programa =  form.programa.data
        finaliza = form.finaliza.data
        
        alta = Acciones(descripcion = descripcion,
                        estado_recupero = estado_recupero,
                        envia_correo = envia_correo,
                        id_tarea_siguiente = id_tarea_siguiente,
                        programa = programa,
                        finaliza = finaliza
        )
        alta.save()
        flash ("Se ha guardado correctamente", "alert-success")
        return redirect(url_for("abms.acciones"))
        
    return render_template("abms/alta_accion.html", form = form)

@abms_bp.route("/abms/acciones/modificacion/<int:id_accion>", methods = ['GET', 'POST'])
@login_required
def modificacion_acciones(id_accion):
    accion = Acciones.get_by_id(id_accion)
    form = AccionesForm()
    form.estado_recupero.choices = estados_select("acciones")
    form.id_tarea_siguiente.choices = tareas_select()
    form.envia_correo.choices = [('', 'Selecciona si envia correo o no'),('SI', 'Si'),('NO', 'No') ]
    
    if form.validate_on_submit():
        accion.descripcion = form.descripcion.data
        accion.estado_recupero =  form.estado_recupero.data
        accion.envia_correo =  form.envia_correo.data
        accion.id_tarea_siguiente = form.id_tarea_siguiente.data
        accion.programa =  form.programa.data
        accion.finaliza = form.finaliza.data
        
        accion.save()
        flash ("Se ha guardado correctamente", "alert-success")
        return redirect(url_for("abms.acciones"))


    return render_template("abms/modificacion_accion.html", accion = accion, form = form)

@abms_bp.route("/abms/acciones", methods = ['GET', 'POST'])
@login_required
def acciones():
    acciones = Acciones.get_all()
    
    return render_template("abms/acciones.html", acciones = acciones)

@abms_bp.route("/abms/acciones/eliminar/<int:id_accion>", methods = ['GET', 'POST'])
@login_required
def eliminar_acciones(id_accion):
    accion = Acciones.get_by_id(id_accion)

    accion.delete()

    return redirect(url_for("abms.acciones"))

@abms_bp.route("/abms/tareasacciones", methods = ['GET', 'POST'])
@login_required
def alta_tareasacciones():
    
    form = TareasAccionesForm()
    form.accion.choices = accion_select()
    form.tarea.choices = tareas_select()
 
    if form.validate_on_submit():
        accion = form.accion.data
        tarea = form.tarea.data

        alta = TareasAcciones(id_accion = accion,
                              id_tarea = tarea
                             )
        alta.save()
        flash ("Se ha guardado correctamente", "alert-success")
        return redirect(url_for("abms.acciones"))


    return render_template("abms/alta_tareasacciones.html", form = form)
