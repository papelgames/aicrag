from functools import wraps

from flask import abort, make_response, redirect, url_for

from flask_login import current_user
from app.models import Estados

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        is_admin = getattr(current_user, 'is_admin', False)
        if not is_admin:
            abort(401)
        return f(*args, **kws)
    return decorated_function


def not_initial_status(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        estado = Estados.get_first_by_clave_tabla(1,'users')
        if current_user.id_estado ==estado.id:
            return redirect(url_for('auth.change_password'))
        return f(*args, **kws)
    return decorated_function

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache