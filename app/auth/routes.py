from flask import (render_template, redirect, url_for,
                   request, current_app, session)
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import true
#from werkzeug.urls import url_parse
from urllib.parse import urlparse 
from flask.helpers import flash

from app import login_manager
from app.common.mail import send_email
from . import auth_bp
from .forms import SignupForm, LoginForm, ChangePasswordForm, UsernameForm, FindUserForm
from .models import Users
from app.models import Personas
from time import strftime, gmtime
from app.auth.decorators import admin_required, not_initial_status, nocache

 
@auth_bp.route("/signup/", methods=["GET", "POST"])
@login_required
@admin_required
@not_initial_status
@nocache
def show_signup_form():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        cuit = form.cuit.data
        correo_electronico = form.correo_electronico.data
        new_password = 'aicrag' + str(strftime('%d%m%y%H%m%s', gmtime()))
        is_admin = form.is_admin.data
        
        # Comprobamos que no hay ya un usuario con ese nombre de usuario
        user = Users.get_by_username(username)
        check_correo = Personas.get_by_correo(correo_electronico)
        if user is not None:
            flash ("El nombre de usuario elegido ya existe","alert-warning")
        elif check_correo and check_correo.id_usuario != None:

            flash ("Ya existe un usuario con ese correo " + check_correo.descripcion_nombre,"alert-warning")
        else:
            # Creamos el usuario y la persona relacionada al usuario y lo guardamos
            user = Users(username=username, 
                        id_estado=1, 
                        is_admin=is_admin
                        )
            
            user.set_password(new_password)
            
            #valido si la persona y si ya tiene usuario.
            check_persona = Personas.get_by_cuit(cuit)

            if check_persona and check_persona.id_usuario == None:
                user.check_persona = check_persona
                user.save()
                check_persona.id_usuario = user.id
                check_persona.save()
            elif check_persona and check_persona.id_usuario != None:
                flash("La persona elegida ya tiene usuario.", "alert-warning")
                return redirect(url_for('admin.list_users'))
            else:
                persona = Personas(descripcion_nombre=name,
                                cuit=cuit,
                                correo_electronico=correo_electronico,
                                usuario_alta = current_user.username)
                user.persona = persona
                user.save()
            # Enviamos un email de bienvenida
            send_email(subject='Bienvenid@ AICRAG',
                        sender=(current_app.config['DONT_REPLY_FROM_EMAIL'], 
                                current_app.config['MAIL_USERNAME'] ),
                        recipients=[correo_electronico, ],
                        text_body=f'Hola {name}, eres nuevo usuairo de aicrag',
                        html_body=f'<p>Hola <strong>{name}</strong>, ya tienes usuario en aicrag: <br>Usuario: <strong>{username}</strong> <br>Contraseña: <strong>{new_password}</strong></p>')
           
            flash("El usuario ha sido creado correctamente.", "alert-success")
            return redirect(url_for('admin.list_users'))
    return render_template("auth/signup_form.html", form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.get_by_username(form.username.data)
        if user is not None and user.check_password(form.password.data):
            print (user.id_estado)
            login_user(user, remember=form.remember_me.data)
            # if user.id_estado == 1:
            #     return redirect(url_for('auth.change_password'))
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('public.index')
            return redirect(next_page)
    return render_template('auth/login_form.html', form=form)

@auth_bp.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    user = Users.get_by_username(current_user.username)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        
        password_actual = user.check_password(form.password_actual.data)
        if password_actual:
            user.set_password(form.password_nuevo.data)
            user.id_estado = 2
            user.save()
            flash('La contraseña ha sido actualizada correctamente','alert-success')
            return redirect(url_for('public.index'))
        else:
            flash('El password actual no es correcto','alert-warning')
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    form = UsernameForm()
    if form.validate_on_submit():
        user = Users.get_by_username(form.username.data)
        
        if user:
            new_password = 'aicrag' + str(strftime('%d%m%y%H%m%s', gmtime()))
            user.set_password(new_password)
            user.id_estado = 1
            user.save()

            correo_electronico = user.persona.correo_electronico        
            name = user.persona.descripcion_nombre
            url_login = url_for('auth.login', _external=True)

            send_email(subject='Aicrag | Blanqueo de contraseña',
                        sender=(current_app.config['MAIL_DEFAULT_SENDER'], 
                                current_app.config['MAIL_USERNAME'] ),
                        recipients=[correo_electronico, ],
                        text_body=f'Hola {name}, te enviamos un correo para poder blanquear la contraseña',
                        html_body=f'<p>Hola <strong>{name}</strong>, ingresando al siguiente link podrás generar una nueva contraseña <a href="{url_login}">Link</a> tu contraseña temporal es: <br><strong>{new_password}</strong> </p>')
            
            flash('Se ha enviado una notificación a su correo para generar una nueva contraseña','alert-success')
            return redirect(url_for('auth.login'))
        else:
            flash('El el usuario no es correcto','alert-warning')
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/forgotpasswordbyadmin', methods=['GET', 'POST'])
def forgot_password_by_admin():
    username = request.args.get('username','')
    user = Users.get_by_username(username)
    
    if user:
        new_password = 'aicrag' + str(strftime('%d%m%y%H%m%s', gmtime()))
        user.set_password(new_password)
        user.id_estado = 1
        user.save()

        correo_electronico = user.persona.correo_electronico        
        name = user.persona.descripcion_nombre
        url_login = url_for('auth.login', _external=True)

        send_email(subject='Aicrag | Blanqueo de contraseña',
                    sender=(current_app.config['MAIL_DEFAULT_SENDER'], 
                            current_app.config['MAIL_USERNAME'] ),
                    recipients=[correo_electronico, ],
                    text_body=f'Hola {name}, te enviamos un correo para poder blanquear la contraseña',
                    html_body=f'<p>Hola <strong>{name}</strong>, ingresando al siguiente link podrás generar una nueva contraseña <a href="{url_login}">Link</a> tu contraseña temporal es: <br><strong>{new_password}</strong> </p>')
        
        flash('Se ha enviado una notificación al correo del usuario para generar una nueva contraseña','alert-success')
        return redirect(url_for('admin.update_user_form', user_id = user.id))
    
@auth_bp.route('/forgotusername', methods=['GET', 'POST'])
def forgot_username():
    form = FindUserForm()
    if form.validate_on_submit():
        persona = Personas.get_by_correo(form.correo_electronico.data)
        if persona:
            user = Users.get_by_id(persona.id_usuario)
            if user:
                correo_electronico = persona.correo_electronico        
                name = persona.descripcion_nombre
                username = user.username 
                url_login = url_for('auth.login', _external=True)

                send_email(subject='Aicrag | Usuario',
                            sender=(current_app.config['MAIL_DEFAULT_SENDER'], 
                                    current_app.config['MAIL_USERNAME'] ),
                            recipients=[correo_electronico, ],
                            text_body=f'Hola {name}, te enviamos un correo para poder informarte tu nombre de usuario',
                            html_body=f'<p>Hola <strong>{name}</strong>, su nombre de usuario es: <strong>{username}</strong>. Puede ingresar <a href="{url_login}">Link</a></p>')
                
                flash('Se ha enviado una notificación a su correo con el nombre de usuario','alert-success')
                return redirect(url_for('auth.login'))
        else:
            flash('Comuniquese con el administrador de Aicrag','alert-warning')

    return render_template('auth/forgot_username.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('public.index'))

@login_manager.user_loader
def load_user(user_id):
    return Users.get_by_id(int(user_id))

@auth_bp.route('/firstin')
def firstin():
    #si ya está loguedo alguien significa que no corre esto y va index
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    #creamos el usuario admin que será con el que se va a poder crear un usuario válido para iniciar
    #el sistema en esta función podemos ir agregando todo lo que necesitamos que esté en la bdd y no 
    #hacer commits por fuera del sistema. 

    username = "admin"        
    user = Users.get_by_username(username)
    
    if user is not None:
        flash ("El administrador ya fue creado","alert-warning")
        
    else:
        # Creamos el usuario admin
        user = Users(username=username, 
                    id_estado=1, 
                    is_admin=True
                    )
        password = "Aicrag"
        user.set_password(password)
        
        user.save()
    return redirect(url_for('auth.show_signup_form'))
