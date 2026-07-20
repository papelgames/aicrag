
import logging
import os

from flask import render_template, redirect, url_for, request, current_app, abort, make_response
from flask.helpers import flash
from flask_login import login_required, current_user

from app.auth.decorators import admin_required, nocache, not_initial_status
from app.models import Egresos, CabecerasPresupuestos, Estados, CajasDiarias
from . import contable_bp
from .forms import EgresosForm, DiarioForm, AbrirCajaDiariaForm


from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)

@contable_bp.route("/contable/altaegreso", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def alta_egreso():
    form=EgresosForm()

    if form.validate_on_submit():
        descripcion = form.descripcion.data
        importe = form.importe.data
        nota = form.nota.data
        modalidad_pago = form.modalidad_pago.data

        egreso = Egresos(descripcion = descripcion,
                             importe = importe,
                             nota = nota,
                             modalidad_pago = modalidad_pago,
                             usuario_alta = current_user.username,
                             usuario_modificacion = current_user.username
                        )
        
        egreso.save()
        flash("Nuevo egreso ingresado", "alert-success")
        return redirect(url_for("contable.alta_egreso"))
    return render_template("contable/alta_egreso.html", form=form)

@contable_bp.route("/contable/diario", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def diario():
    form= DiarioForm()
    
    dia=datetime.strptime(request.args.get('dia', str(date.today())), '%Y-%m-%d')
    page_e=int(request.args.get('page_e', 1))
    page_v=int(request.args.get('page_v', 1))
    per_page=current_app.config['ITEMS_PER_PAGE']

    #valido si hay una caja abierta
    estado_abierto = Estados.get_first_by_clave_tabla(1,'cajasdiarias')

    saldo_inicial = 0
    estado_caja = {}
    caja_abierta = CajasDiarias.get_by_id_estado(estado_abierto.id)
    caja_diaria = CajasDiarias.get_by_fecha(dia)
    if not caja_abierta and not caja_diaria:
        flash('Primero debes abrir la caja', 'alert-warning')
        return redirect(url_for("contable.abrir_caja_diaria"))
    
    #capturo el saldo inicial de la caja diara segun la fecha
    caja_diaria = CajasDiarias.get_by_fecha(dia)
    if caja_diaria:
        saldo_inicial = caja_diaria.saldo_inicial

        estado_caja = {caja_diaria.estado_cajas_diarias.clave : caja_diaria.estado_cajas_diarias.descripcion}
         

    egresos=Egresos.get_by_fecha(dia, page_e, per_page)
    # ventas=CabecerasPresupuestos.get_by_fecha(dia, tipo_venta.id, page_v, per_page)
    ventas=CabecerasPresupuestos.get_by_fecha(dia, page_v, per_page) 

    egresos_totales = Egresos.get_all_by_fecha(dia)
    modalidades=dict(EgresosForm.modalidad_pago.kwargs['choices'])
    
    total_egresos = sum(suma.importe for suma in egresos_totales)
    
    total_egresos_abiertos = {}
    for egreso in egresos_totales:
        modalidad = egreso.modalidad_pago
        importe = egreso.importe or 0
        total_egresos_abiertos[modalidad] = total_egresos_abiertos.get(modalidad, 0) + importe
    
    ingresos_totales = CabecerasPresupuestos.get_all_by_fecha(dia)
    total_ventas_abiertos = {}
    for ingreso in ingresos_totales:
        modalidad = ingreso.modalidad_cobro
        importe = ingreso.importe_total or 0
        total_ventas_abiertos[modalidad] = total_ventas_abiertos.get(modalidad, 0) + importe
    total_ventas = sum(suma.importe_total for suma in ingresos_totales)
    
    todas_modalidades = set(total_ventas_abiertos.keys()) | set(total_egresos_abiertos.keys())
    total_resultado_abiertos = {
    m: total_ventas_abiertos.get(m, 0) - total_egresos_abiertos.get(m, 0)
    for m in todas_modalidades
    }
    
    if form.validate_on_submit():
        dia=form.dia.data
        return redirect(url_for("contable.diario", dia=dia))
    return render_template("contable/diario.html", 
                           egresos=egresos, 
                           ventas=ventas, 
                           total_ventas=total_ventas, 
                           total_egresos=total_egresos, 
                           page_e=page_e, 
                           page_v=page_v, 
                           form=form, 
                           dia=dia,
                           modalidades=modalidades,
                           total_egresos_abiertos=total_egresos_abiertos,
                           total_ventas_abiertos=total_ventas_abiertos,
                           total_resultado_abiertos=total_resultado_abiertos,
                           saldo_inicial=saldo_inicial,
                           estado_caja=estado_caja)

@contable_bp.route("/contable/abrircajadiaria", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def abrir_caja_diaria():
    form = AbrirCajaDiariaForm()
    dia_actual =  datetime.now()
    estado_caja = Estados.get_first_by_clave_tabla(1,'cajasdiarias') 
    caja_abierta = CajasDiarias.get_by_id_estado(estado_caja.id)
    ultimo_saldo = CajasDiarias.get_ultima_caja().saldo_real
    
    if caja_abierta:
        return redirect(url_for("contable.diario"))
    if form.validate_on_submit():
        saldo_inicial=form.saldo_inicial.data
        fecha_caja= form.fecha_caja.data
        caja_diaria = CajasDiarias.get_by_fecha(fecha_caja)
        if caja_diaria:
            flash('Ya hay una caja para ese dia. Seleccione la caja y editela.', 'alert-success' )
            return redirect(url_for("consultas.consulta_cajas"))
        else:
            nueva_caja_diaria = CajasDiarias(saldo_inicial=saldo_inicial, 
                                            fecha_caja=fecha_caja, 
                                            usuario_alta = current_user.username)
            estado_caja.cajas_diarias.append(nueva_caja_diaria)
            estado_caja.save()
            flash('La caja ha sido abierta correctamente', 'alert-success')
            return redirect(url_for("contable.diario"))
    return render_template("contable/abrir_caja_diaria.html", 
                           form=form,
                           dia_actual=dia_actual,
                           ultimo_saldo=ultimo_saldo)

@contable_bp.route("/contable/cerrarcajadiaria", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def cerrar_caja_diaria():
    saldo_real = request.args.get('saldo_real',0)
    estado_abierto = Estados.get_first_by_clave_tabla(1,'cajasdiarias')
    estado_cerrado = Estados.get_first_by_clave_tabla(2,'cajasdiarias')
    caja_abierta = CajasDiarias.get_by_id_estado(estado_abierto.id)
    
    caja_abierta.estado_cajas_diarias = estado_cerrado
    caja_abierta.saldo_real = saldo_real
    caja_abierta.fecha_cierre = datetime.now()
    caja_abierta.usuario_modificacion = current_user.username
    caja_abierta.save()

    flash('La caja ha sido cerrada correctamente', 'alert-success')
    return redirect(url_for("contable.diario"))