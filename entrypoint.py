
import os

from flask import send_from_directory, request, redirect, url_for, session, current_app, abort
from flask_login import current_user

from app import create_app

from dotenv import load_dotenv

load_dotenv()

settings_module = os.getenv('APP_SETTINGS_MODULE')
app = create_app(settings_module)


@app.route('/media/posts/<filename>')
def media_posts(filename):
    dir_path = os.path.join(
        app.config['MEDIA_DIR'],
        app.config['POSTS_IMAGES_DIR'])
    return send_from_directory(dir_path, filename)

@app.before_request
def verificar_permisos():
    ignorar_endpoint = ['static', 'auth.logout']#, 'auth.login', 'public.index']
   
    # Obtener el endpoint actual
    endpoint = request.endpoint
    
    # Ignorar la verificación de permisos para los endpoints en ignorar_endpoint
    if endpoint in ignorar_endpoint:
        return

    # Verificar si ya hemos almacenado los permisos en la sesión
    if current_user.is_authenticated and 'permisos_del_usuario' not in session:
        session['permisos_del_usuario'] = [permiso.descripcion for permiso in current_user.permisos]
    
    # Verificar si el endpoint actual está en la lista de permisos del usuario no sos admin
    if current_user.is_authenticated and endpoint not in session['permisos_del_usuario'] and not current_user.is_admin:
        return abort(403)  # Prohibido