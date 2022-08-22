import logging
import os

from flask import render_template, redirect, url_for, abort, current_app
from flask.helpers import flash
from flask_login import login_required, current_user
from rsa.key import PrivateKey
from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required
from app.auth.models import User
#from app.models import Compulsas, Imagenes, Ofrecimientos
from . import compras_bp
from .forms import InicioOfertaForm, OfertaForm

from app.common.mail import send_email
import rsa

from datetime import datetime, time

logger = logging.getLogger(__name__)

publicKey, privateKey = rsa.newkeys(512) 

def enc (cadena):
    return  rsa.encrypt(str(cadena).encode(),  
                         publicKey) 
def  denc (cadena):
    return  rsa.decrypt(cadena, privateKey).decode()


@compras_bp.route("/ofrecimiento/iniciar/<int:id_compulsa>", methods = ['GET', 'POST'])
def iniciar(id_compulsa):
    detalle = Compulsas.get_by_compulsa_id(id_compulsa)
    imagenes = Imagenes.get_by_imagenes_compulsa_id(id_compulsa)
    form = InicioOfertaForm()
    
    if form.validate_on_submit():
        nombre_apellido_rs = form.nombre_apellido_rs.data
        dni = form.dni.data
        correo_electronico = form.correo_electronico.data
        pin_temporal = form.pin_temporal.data

        inicio_ofrecimiento = Ofrecimientos(compulsa_id = id_compulsa, 
                                            nombre_apellido_rs = nombre_apellido_rs, 
                                            dni = dni,
                                            correo_electronico = correo_electronico)
        inicio_ofrecimiento.set_pin(pin_temporal)
        inicio_ofrecimiento.save()
        send_email(subject='Bienvenid@ al miniblog',
                       sender=current_app.config['DONT_REPLY_FROM_EMAIL'],
                       recipients=[correo_electronico, ],
                       text_body=f'Hola {nombre_apellido_rs}, bienvenid@ al miniblog de Flask',
                       html_body=f'<p>Hola <strong>{nombre_apellido_rs}</strong>, Para realizar la oferta debes ingresar a: http://127.0.0.1:5000/ofrecimiento/ofertar/{inicio_ofrecimiento.id}</p>')
        flash ("Se ha enviado un mensaje a su correo electrónico", "alert-primary")
        return redirect(url_for("compulsa.activas"))
    



    return render_template("ofrecimiento/iniciar.html", detalle = detalle, imagenes = imagenes, form= form)

@compras_bp.route("/ofrecimiento/ofertar/<int:id_oferta>", methods = ['GET', 'POST'])
def ofertar(id_oferta):
    
    #si ya tiene una oferta
        
    form = OfertaForm()
    detalle = Compulsas.get_by_ofrecimiento_id(id_oferta)
    for id_compulsa in detalle:
        imagenes = Imagenes.get_by_imagenes_compulsa_id(id_compulsa.Compulsas.id)
    dni = id_compulsa.Ofrecimientos.dni
    correo_electronico = id_compulsa.Ofrecimientos.correo_electronico
    datos_ofrecimiento = Ofrecimientos.get_ofrecimientos_id(id_oferta)
    
    diferencia = datetime.now() - datos_ofrecimiento.created
    horas = (diferencia.days *24) + (diferencia.seconds/3600)
    
    if horas > 2 :
        flash ("Su incio ha vencido. Debe volver a iniciar la oferta.","alert-warning")
        return redirect(url_for("compulsa.activas"))

    if form.validate_on_submit():
        
        if form.dni.data == dni and \
           form.correo_electronico.data == correo_electronico and \
           datos_ofrecimiento.check_pin(form.pin_temporal.data):
           importe_ofertado = enc(form.importe_a_ofertar.data)
          
           datos_ofrecimiento.importe_ofertado = importe_ofertado
           datos_ofrecimiento.status = "CON OFERTA"
           datos_ofrecimiento.save()
 
           flash ("Has realizado una oferta con exito si la misma resulta ganadora te lo informamos por mail.","alert-primary")
        else:

            flash ("Has mandado fruta con los datos.","alert-warning")
        return redirect(url_for("compulsa.activas"))
    return render_template("ofrecimiento/ofertar.html", form = form, detalle = detalle, imagenes= imagenes)

@compras_bp.route("/ofrecimiento/borrar_oferta/")
def borrar_oferta():
    return render_template("ofrecimiento/borrar_oferta.html")

@compras_bp.route("/ofrecimientos/resultados")
@login_required
def resultados():
    return render_template("ofrecimiento/resultados.html")

@compras_bp.route("/ofrecimiento/ganador")
def ganador():
    return render_template("ofrecimiento/ganador.html")
