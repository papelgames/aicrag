
import datetime
from email.policy import default
from itertools import product
from types import ClassMethodDescriptorType
from typing import Text

from slugify import slugify
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth.models import User

from app import db

class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, default=db.func.current_timestamp(),\
                     onupdate=db.func.current_timestamp())

class Proveedores (Base):
    __tablename__ = "proveedores"
    nombre = db.Column(db.String(50), nullable = False)
    correo_electronico = db.Column(db.String(256))
    archivo_si_no = db.Column(db.Boolean, default=False)
    formato_id = db.Column(db.String(50))
    columna_id_lista_proveedor = db.Column(db.String(1))
    columna_codigo_de_barras = db.Column(db.String(1))
    columna_descripcion = db.Column(db.String(1))
    columna_importe = db.Column(db.String(1))
    incluye_iva = db.Column(db.Boolean, default=False)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Proveedores.query.all()
    
    @staticmethod
    def get_by_id(id_proveedor):
        return Proveedores.query.filter_by(id = id_proveedor).first()
    
class Productos (Base):
    __tablename__ = "productos"
    codigo_de_barras = db.Column(db.String(256))
    id_proveedor = db.Column(db.Integer)
    id_lista_proveedor = db.Column(db.String(256))
    descripcion = db.Column(db.String(256))
    importe = db.Column(db.Float)
    cantidad_presentacion = db.Column(db.Integer, default=1)
    id_ingreso = db.Column(db.String(256))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
       
    def only_add(self):
        db.session.add(self)
        
    def only_save(self):
        db.session.commit()
               
    @staticmethod
    def get_all():
        query_str = db.session.query(Productos, User, Proveedores)\
            .filter(Productos.usuario_alta == User.email)\
            .filter(Productos.usuario_modificacion == User.email)\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .all()
        return query_str

    @staticmethod
    def get_by_codigo_de_barras(codigo_barras):
        query_str = db.session.query(Productos, User, Proveedores)\
            .filter(Productos.usuario_alta == User.email)\
            .filter(Productos.usuario_modificacion == User.email)\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.codigo_de_barras == codigo_barras)\
            .all()
        return query_str

    @staticmethod
    def get_like_descripcion(descripcion_):
        query_str = db.session.query(Productos, User, Proveedores)\
            .filter(Productos.usuario_alta == User.email)\
            .filter(Productos.usuario_modificacion == User.email)\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.descripcion.contains(descripcion_))\
            .all()
        return query_str

    @staticmethod
    def get_by_id_lista_proveedor(id_lista):
        return Productos.query.filter_by(id_lista_proveedor = id_lista).first()

    @staticmethod
    def get_by_id(id_producto):
        return Productos.query.filter_by(id = id_producto).first()


    '''
    
    Session.query(User,Document,DocumentPermissions)
        .filter(User.email == Document.author)
        .filter(Document.name == DocumentPermissions.document)
        .filter(User.email == 'someemail')
        .all()
'''


class CabecerasPresupuestos (Base):
    __tablename__ = "cabeceraspresupuestos"
    fecha_vencimiento = db.Column(db.DateTime, nullable = False)
    nombre_cliente = db.Column(db.String(256), nullable = False)
    correo_electronico = db.Column(db.String(256))
    importe_total = db.Column(db.Float)
    estado = db.Column(db.Integer)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

class Presupuestos (Base):
    __tablename__ = "presupuestos"
    id_cabecera_presupuesto = db.Column(db.Integer)
    id_producto = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    importe = db.Column(db.Float)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

class Compras (Base):
    __tablename__ = "compras"
    id_cierre = db.Column(db.Integer)
    id_proveedor = db.Column(db.Integer)
    id_producto = db.Column(db.Integer)
    codigo_de_barras = db.Column(db.String(256))
    cantidad = db.Column(db.Integer)
    importe = db.Column(db.Float)
    fecha_cierre = db.Column(db.DateTime)
    estado = db.Column(db.Integer)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

class Parametros (Base):
    __tablename__ = "parametros"
    descripcion = db.Column(db.String(50))
    tabla = db.Column(db.String(50))
    tipo_parametro = db.Column(db.String(50))

