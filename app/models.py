
import datetime
from email.policy import default
from types import ClassMethodDescriptorType
from typing import Text

from slugify import slugify
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


from app import db

class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, default=db.func.current_timestamp(),\
                     onupdate=db.func.current_timestamp())

class Proveedores (Base):
    nombre = db.Column(db.String(50), nullable = False)
    correo_electronico = db.Column(db.String(256))
    archivo_si_no = db.Column(db.Boolean, default=False)
    formato_id = db.Column(db.String(50))
    columna_id_lista_proveedor = db.Column(db.Integer)
    columna_codigo_de_barras = db.Column(db.Integer)
    columna_descripcion = db.Column(db.Integer)
    columna_importe = db.Column(db.Integer)
    incluye_iva = db.Column(db.Boolean, default=False)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Proveedores.query.all()
    
class Productos (Base):
    codigo_de_barras = db.Column(db.String(256))
    id_proveedor = db.Column(db.Integer)
    id_lista_proveedor = db.Column(db.String(256))
    descripcion = db.Column(db.String(256))
    importe = db.Column(db.Float)
    cantidad_presentacion = db.Column(db.Integer, default=1)
    id_ingreso = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()


class CabecerasPresupuestos (Base):
    fecha_vencimiento = db.Column(db.DateTime, nullable = False)
    nombre_cliente = db.Column(db.String(256), nullable = False)
    correo_electronico = db.Column(db.String(256))
    importe_total = db.Column(db.Float)
    estado = db.Column(db.Integer)


class Presupuestos (Base):
    id_cabecera_presupuesto = db.Column(db.Integer)
    id_producto = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    importe = db.Column(db.Float)

class Compras (Base):
    id_cierre = db.Column(db.Integer)
    id_proveedor = db.Column(db.Integer)
    id_producto = db.Column(db.Integer)
    codigo_de_barras = db.Column(db.String(256))
    cantidad = db.Column(db.Integer)
    importe = db.Column(db.Float)
    fecha_cierre = db.Column(db.DateTime)
    estado = db.Column(db.Integer)

class Parametros (Base):
    descripcion = db.Column(db.String(50))
    tabla = db.Column(db.String(50))
    tipo_parametro = db.Column(db.String(50))

