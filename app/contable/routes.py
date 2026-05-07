
import logging
import os

from flask import render_template, redirect, url_for, request, current_app, abort, make_response
from flask.helpers import flash
from flask_login import login_required, current_user

from app.auth.decorators import admin_required, nocache, not_initial_status
from app.models import Egresos, CabecerasPresupuestos, TiposVentas
from . import contable_bp
from .forms import EgresosForm, DiarioForm


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

    tipo_venta=TiposVentas.get_first_by_clave_tabla(2)
    egresos=Egresos.get_by_fecha(dia, page_e, per_page)
    ventas=CabecerasPresupuestos.get_by_fecha(dia, tipo_venta.id, page_v, per_page)
    egresos_totales = Egresos.get_all_by_fecha(dia)
    modalidades=dict(EgresosForm.modalidad_pago.kwargs['choices'])
    
    total_egresos = sum(suma.importe for suma in egresos_totales)
    
    total_egresos_abiertos = {}
    for egreso in egresos_totales:
        modalidad = egreso.modalidad_pago
        importe = egreso.importe or 0
        total_egresos_abiertos[modalidad] = total_egresos_abiertos.get(modalidad, 0) + importe
    total_ventas_abiertos = {}
    total_ventas = sum(suma.importe_total for suma in ventas)
    
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
                           total_resultado_abiertos=total_resultado_abiertos)
