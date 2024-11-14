import logging
import os

from flask import render_template, redirect, url_for, abort, current_app, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required, not_initial_status
from app.auth.models import Users
from app.models import Roles, Permisos
from . import admin_bp
from .forms import UserAdminForm, PermisosUserForm, RolesUserForm

logger = logging.getLogger(__name__)

#creo una tupla para usar en el campo select del form que quiera que necesite los permisos
def permisos_select(user_id):
    permisos = Permisos.get_permisos_no_relacionadas_personas(user_id)
    select_permisos =[( '','Seleccionar permiso')]
    for rs in permisos:
        sub_select_permisos = (str(rs.id), rs.descripcion)
        select_permisos.append(sub_select_permisos)
    return select_permisos

#creo una tupla para usar en el campo select del form que quiera que necesite los roles
def roles_select():
    roles = Roles.get_all()
    select_rol =[( '','Seleccionar rol')]
    for rs in roles:
        sub_select_rol = (str(rs.id), rs.descripcion)
        select_rol.append(sub_select_rol)
    return select_rol

@admin_bp.route("/admin/")
@login_required
@admin_required
def index():
    return render_template("admin/index.html")

@admin_bp.route("/admin/users/")
@login_required
@admin_required
def list_users():
    users = Users.get_all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/admin/user/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def update_user_form():
    user_id = request.args.get('user_id','')
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    if user is None:
        logger.info(f'El usuario {user_id} no existe')
        abort(404)
    # Crea un formulario inicializando los campos con
    # los valores del usuario.
    form = UserAdminForm(obj=user)
    if form.validate_on_submit():
        # Actualiza los campos del usuario existente
        # user.is_admin = form.is_admin.data
        # user.es_dibujante = form.es_dibujante.data
        form.populate_obj(user)
        user.save()
        logger.info(f'Guardando el usuario {user_id}')
        return redirect(url_for('admin.list_users'))
    return render_template("admin/user_form.html", form=form, user=user)

@admin_bp.route("/admin/user/delete/<int:user_id>/", methods=['POST', ])
@login_required
@admin_required
def delete_user(user_id):
    logger.info(f'Se va a eliminar al usuario {user_id}')
    user = Users.get_by_id(user_id)
    if user is None:
        logger.info(f'El usuario {user_id} no existe')
        abort(404)
    user.delete()
    logger.info(f'El usuario {user_id} ha sido eliminado')
    return redirect(url_for('admin.list_users'))

@admin_bp.route("/admin/asignacionpermisos/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignacion_permisos():
    user_id = request.args.get('user_id','')
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    form = PermisosUserForm()
    form.id_permiso.choices = permisos_select(user_id)
    
    if form.validate_on_submit():
        permiso = Permisos.get_by_id(form.id_permiso.data)
        for permiso_en_user in user.permisos:
            if permiso_en_user.id == int(form.id_permiso.data):
                flash ('El usuario ya tiene el permiso', 'alert-warning')
                return redirect(url_for('admin.asignacion_permisos', user_id = user_id))
        user.permisos.append(permiso)

        user.save()
        
        flash ('Permiso asignado correctamente', 'alert-success')
        return redirect(url_for('admin.asignacion_permisos', user_id = user_id))
    return render_template("admin/permisos_usuarios.html", form=form, user=user)


@admin_bp.route("/admin/asignacionroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignacion_roles():
    user_id = request.args.get('user_id','')
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    form = RolesUserForm()
    form.rol.choices = roles_select()
    
    if form.validate_on_submit():
        permisos_de_roles = Roles.get_by_id(form.rol.data)
        for permiso in permisos_de_roles.permisos:
            control = True
            for permiso_en_user in user.permisos:
                if permiso_en_user.id == permiso.id:
                    control = False
                
            if control:
                user.permisos.append(permiso)
              
        user.save()

        flash ('Permiso asignado correctamente', 'alert-success')
        return redirect(url_for('admin.asignacion_roles', user_id = user_id))
    return render_template("admin/roles_usuarios.html", form=form, user=user)


@admin_bp.route("/admin/eliminarpermisousuario/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permiso_usuario():
    user_id = request.args.get('user_id','')
    id_permiso = request.args.get('id_permiso','')
    user = Users.get_by_id(user_id)
    permiso = Permisos.get_by_id(id_permiso)
    
    user.permisos.remove(permiso)
    user.save()
    flash ('Permiso eliminado correctamente', 'alert-success')
    return redirect(url_for('admin.asignacion_permisos', user_id = user_id))