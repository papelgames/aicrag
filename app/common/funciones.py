from app.models import Estados
from flask_login import current_user


def listar_endpoints(app):
    """
    Lista todos los endpoints registrados en la aplicación Flask.
    """
    endpoints = []

    for rule in app.url_map.iter_rules():
        endpoints.append({'descripcion' :rule.endpoint, 
                            'usuario_alta':current_user.username})
    return endpoints
