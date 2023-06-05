from flask import (render_template, redirect, url_for,
                   request, current_app)
from flask_login import current_user, login_user, logout_user
from sqlalchemy import true
from werkzeug.urls import url_parse
from flask.helpers import flash

from app import login_manager
from app.common.mail import send_email
from . import auth_bp
from .forms import SignupForm, LoginForm
from .models import User


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    form = SignupForm()
    

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        
        # Comprobamos que no hay ya un usuario con ese email
        user = User.get_by_email(email)
        if user is not None:
            flash ("El correo electrónico seleccionado ya ha sido usado","alert-warning")
        else:
            # Creamos el usuario y lo guardamos
            
            user = User(name=name, 
                        email=email, 
                        activo=True
                        )
            user.set_password(password)
            user.save()
            # Enviamos un email de bienvenida
            send_email(subject='Bienvenid@ al miniblog',
                       sender=current_app.config['DONT_REPLY_FROM_EMAIL'],
                       recipients=[email, ],
                       text_body=f'Hola {name}, bienvenid@ al miniblog de Flask',
                       html_body=f'<p>Hola <strong>{name}</strong>, bienvenid@ al miniblog de Flask</p>')
            # Dejamos al usuario logueado
            login_user(user, remember=False)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('public.index')
            return redirect(next_page)
    return render_template("auth/signup_form.html", form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('public.index')
            return redirect(next_page)
    return render_template('auth/login_form.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))
