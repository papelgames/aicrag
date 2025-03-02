
import datetime
from email.policy import default
from itertools import product
from types import ClassMethodDescriptorType
from typing import Text

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
#from .models import Users
import locale

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
    columna_utilidad = db.Column(db.String(1))
    incluye_iva = db.Column(db.Boolean, default=False)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    producto = db.relationship('Productos', backref='productos', uselist=True)


    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Proveedores.query.all()

    @staticmethod
    def get_by_archivo_si_no(true_false):
        return Proveedores.query.filter_by(archivo_si_no = true_false).all()

    @staticmethod
    def get_by_id(id_proveedor):
        return Proveedores.query.filter_by(id = id_proveedor).first()
    
class Productos (Base):
    __tablename__ = "productos"
    codigo_de_barras = db.Column(db.String(256))
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    id_lista_proveedor = db.Column(db.String(256))
    descripcion = db.Column(db.String(256))
    importe = db.Column(db.Numeric(precision=15, scale=2))
    cantidad_presentacion = db.Column(db.Float, default=1) # pasar a float
    id_ingreso = db.Column(db.String(256))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    es_servicio = db.Column(db.Boolean)
    utilidad = db.Column(db.Float)
    producto_presupuesto = db.relationship('ProductosPresupuestos', backref='productos_en_presupuestos', uselist=True)

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
        query_str = db.session.query(Productos, Proveedores)\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .all()
        return query_str

    @staticmethod
    def get_all_productos_sin_codigo_de_barras():
        query_str = db.session.query(Productos.codigo_de_barras, Productos.id_lista_proveedor, Productos.descripcion, Productos.importe, Proveedores.nombre)\
        .filter(Productos.id_proveedor == Proveedores.id)\
        .filter(or_(Productos.codigo_de_barras.is_(None), \
            Productos.codigo_de_barras == "",\
            Productos.codigo_de_barras == " ",\
            Productos.codigo_de_barras == "#N/A"))\
        .all()
        return query_str

    @staticmethod
    def get_all_precios_dbf():
        valor_calculado = ((((Productos.importe * Productos.utilidad)/100) + Productos.importe) / Productos.cantidad_presentacion)
        subquery = db.session.query(
        Productos.codigo_de_barras,
        func.max(valor_calculado).label('max_precio'))\
        .filter(Productos.codigo_de_barras.isnot(None))\
        .filter(Productos.codigo_de_barras != "")\
        .filter(Productos.codigo_de_barras != " ")\
        .filter(Productos.codigo_de_barras != "#N/A")\
        .group_by(Productos.codigo_de_barras).subquery()

        query_str = db.session.query(
        subquery.c.codigo_de_barras,
        Productos.descripcion,
        subquery.c.max_precio
    ).join(
        Productos,
        (subquery.c.codigo_de_barras == Productos.codigo_de_barras) & (subquery.c.max_precio == valor_calculado)
    ).distinct().all()
        return query_str

    @staticmethod
    def get_by_codigo_de_barras_caro(codigo_barras):
        valor_calculado = ((((Productos.importe * Productos.utilidad)/100) + Productos.importe) / Productos.cantidad_presentacion)
        query_str = db.session.query(Productos.id, Productos.importe)\
            .filter(Productos.codigo_de_barras == codigo_barras)\
            .filter(valor_calculado == db.session.query(func.max(valor_calculado))\
                .filter(Productos.codigo_de_barras == codigo_barras))\
                .first()    
        return query_str
    
    @staticmethod
    def get_by_codigo_de_barras(codigo_barras):
        valor_calculado =  ((((Productos.importe * Productos.utilidad)/100) + Productos.importe) / Productos.cantidad_presentacion)
        query_str = db.session.query(Productos, Proveedores, valor_calculado.label('importe_calculado'))\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.codigo_de_barras == codigo_barras)\
            .all()
        return query_str
    
    @staticmethod
    def get_by_id_completo(id_producto):
        valor_calculado =  ((((Productos.importe * Productos.utilidad)/100) + Productos.importe) / Productos.cantidad_presentacion)
        query_str = db.session.query(Productos, Proveedores, valor_calculado.label('importe_calculado'))\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.id == id_producto)\
            .all()
        return query_str

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_like_descripcion(descripcion_):
        valor_calculado =  ((((Productos.importe * Productos.utilidad)/100) + Productos.importe) / Productos.cantidad_presentacion)
        query_str = db.session.query(Productos, Proveedores, valor_calculado.label('importe_calculado'))\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.descripcion.contains(descripcion_))\
            .all()
        return query_str

    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        descripcion_ = descripcion_.replace(' ','%')
        valor_calculado =  ((((Productos.importe * Productos.utilidad)/100) + Productos.importe) / Productos.cantidad_presentacion)
        return db.session.query(Productos, Proveedores, valor_calculado.label('importe_calculado'))\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.descripcion.contains(descripcion_))\
            .paginate(page=page, per_page=per_page, error_out=False)
 
    @staticmethod
    def get_by_id_lista_proveedor(id_lista, id_proveedor):
        return Productos.query.filter_by(id_lista_proveedor = id_lista, id_proveedor = id_proveedor).first()

    @staticmethod
    def get_by_id(id_producto):
        return Productos.query.filter_by(id = id_producto).first()

class TiposVentas(Base):
    __tablename__ ="tiposventas"
    clave = db.Column(db.Integer)
    descripcion = db.Column(db.String(25))
    cabecera_presupuesto = db.relationship('CabecerasPresupuestos', backref='cabeceras_presupuestos', uselist=True)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return TiposVentas.query.all()
    
    @staticmethod
    def get_first_by_clave_tabla(clave):
        return TiposVentas.query.filter_by(clave = clave).first()

class CabecerasPresupuestos (Base):
    __tablename__ = "cabeceraspresupuestos"
    fecha_vencimiento = db.Column(db.DateTime, nullable = False)
    nombre_cliente = db.Column(db.String(256))
    correo_electronico = db.Column(db.String(256))
    importe_total = db.Column(db.Numeric(precision=15, scale=2))
    id_estado = db.Column(db.Integer, db.ForeignKey('estados.id'))
    id_tp_ventas = db.Column(db.Integer, db.ForeignKey('tiposventas.id'))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    producto_presupuesto = db.relationship('ProductosPresupuestos', backref='productos_presupuestos', uselist=True)
    
    def only_add(self):
        db.session.add(self)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_presupuesto):
        return CabecerasPresupuestos.query.filter_by(id = id_presupuesto).first()

    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        return CabecerasPresupuestos.query.filter(CabecerasPresupuestos.nombre_cliente.contains(descripcion_))\
                                                           .order_by(CabecerasPresupuestos.fecha_vencimiento.desc())\
                                                           .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_all():
        return db.session.query(CabecerasPresupuestos).order_by(CabecerasPresupuestos.fecha_vencimiento.desc()).all()

    @staticmethod
    def get_all_estado(id_estado, page=1, per_page=20):
        return CabecerasPresupuestos.query.filter_by(id_estado = id_estado)\
            .paginate(page=page, per_page=per_page, error_out=False)

class ProductosPresupuestos (Base):
    __tablename__ = "productospresupuestos"
    id_cabecera_presupuesto = db.Column(db.Integer, db.ForeignKey('cabeceraspresupuestos.id'))
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer)
    descripcion = db.Column(db.String(256))
    importe = db.Column(db.Numeric(precision=15, scale=2))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def only_add(self):
        db.session.add(self)
        
    def only_save(self):
        db.session.commit()
 
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id_producto(id):
        return ProductosPresupuestos.query.filter_by(id = id).first()

    @staticmethod
    def get_by_id_presupuesto(id_presupuesto):
        return ProductosPresupuestos.query.filter_by(id_cabecera_presupuesto = id_presupuesto).all()

    @staticmethod
    def get_q_by_id_presupuesto(id_presupuesto):
        return ProductosPresupuestos.query.filter_by(id_cabecera_presupuesto = id_presupuesto).count()
    
    @staticmethod
    def get_importe_total_by_id_presupuesto(id_presupuesto):
        return db.session.query(ProductosPresupuestos.id_cabecera_presupuesto, func.sum(ProductosPresupuestos.importe * ProductosPresupuestos.cantidad)).\
            filter(ProductosPresupuestos.id_cabecera_presupuesto == id_presupuesto).first()
            
    @staticmethod
    def get_by_id_producto(id):
        return ProductosPresupuestos.query.filter_by(id= id).first()

class Compras (Base):
    __tablename__ = "compras"
    id_cierre = db.Column(db.Integer)
    id_proveedor = db.Column(db.Integer)
    id_producto = db.Column(db.Integer)
    codigo_de_barras = db.Column(db.String(256))
    cantidad = db.Column(db.Integer)
    importe = db.Column(db.Numeric(precision=15, scale=2))
    fecha_cierre = db.Column(db.DateTime)
    estado = db.Column(db.Integer)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

class Parametros (Base):
    __tablename__ = "parametros"
    descripcion = db.Column(db.String(50))
    tabla = db.Column(db.String(50))
    tipo_parametro = db.Column(db.String(50))

    @staticmethod
    def get_by_tabla(tabla):
        return Parametros.query.filter_by(tabla = tabla).first()

class Personas (Base):
    __tablename__ = "personas"
    descripcion_nombre = db.Column(db.String(50), nullable = False)
    cuit = db.Column(db.String(11), nullable = False)
    correo_electronico = db.Column(db.String(256))
    telefono = db.Column(db.String(256))
    tipo_persona = db.Column(db.String(50))
    id_estado = db.Column(db.Integer, db.ForeignKey('estados.id')) #revisar integridad en bdd
    nota = db.Column(db.String(256))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Personas.query.all()
    
    @staticmethod
    def get_by_id(id_persona):
        return Personas.query.filter_by(id = id_persona).first()
    
    @staticmethod
    def get_by_cuit(cuit):
        return Personas.query.filter_by(cuit = cuit).first()

    @staticmethod
    def get_by_correo(correo):
        return Personas.query.filter_by(correo_electronico = correo).first()
        
    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        descripcion_ = f"%{descripcion_}%"
        return db.session.query(Personas)\
            .filter(Personas.descripcion_nombre.contains(descripcion_))\
            .paginate(page=page, per_page=per_page, error_out=False)

class Estados(Base):
    __tablename__ = "estados"
    clave = db.Column(db.Integer)
    descripcion = db.Column(db.String(50))
    tabla = db.Column(db.String(50))
    inicial = db.Column(db.Boolean)
    final = db.Column(db.Boolean)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    cabecera_presupuesto = db.relationship('CabecerasPresupuestos', backref='estado_presupuestos', uselist=True)
    persona = db.relationship('Personas', backref='estado_personas', uselist=True)
    user = db.relationship('Users', backref='estado_users', uselist=True)
   
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Estados.query.all()
    
    @staticmethod
    def get_first_by_clave_tabla(clave, tabla):
        return Estados.query.filter_by(clave = clave, tabla = tabla).first()

class PermisosPorUsuarios(Base):
    __tablename__ = "permisosporusuarios"
    id_permiso = db.Column(db.Integer, db.ForeignKey('permisos.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'))

class Roles(Base):
    __tablename__ = "roles"
    descripcion = db.Column(db.String(50))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    permisos = db.relationship('Permisos', secondary='permisosenroles', back_populates='roles')

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_by_id(id):
        return Roles.query.get(id)

    @staticmethod
    def get_all_by_id(id):
        return Roles.query.filter_by(id = id).all()
    
    @staticmethod
    def get_all():
        return Roles.query.all()

    @staticmethod
    def get_all_descripcion_agrupada():
        return db.session.query(Roles.descripcion.label('nombre_rol')).distinct().all()

class PermisosEnRoles(Base):
    __tablename__ = "permisosenroles"
    id_permiso = db.Column(db.Integer, db.ForeignKey('permisos.id'))
    id_roles =db.Column(db.Integer, db.ForeignKey('roles.id'))

class Permisos(Base):
    __tablename__ = "permisos"
    descripcion = db.Column(db.String(50))
    roles = db.relationship('Roles', secondary='permisosenroles', back_populates='permisos')
    users = db.relationship('Users', secondary='permisosporusuarios', back_populates='permisos')
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def save_masivo(self, lista):
        db.session.bulk_save_objects(lista)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Permisos.query.all()

    @staticmethod
    def get_by_id(id_permiso):
        return Permisos.query.filter_by(id = id_permiso).first()
   
    @staticmethod
    def get_by_descripcion(descripcion):
        return Permisos.query.filter_by(descripcion = descripcion).first()

    @staticmethod
    def get_permisos_no_relacionadas_roles(id_rol): 
        return  Permisos.query.filter(~Permisos.roles.any(id = id_rol)).all()
    
    @staticmethod
    def get_permisos_no_relacionadas_personas(id_persona): 
        return  Permisos.query.filter(~Permisos.users.any(id = id_persona)).all()
    
class Egresos (Base):
    __tablename__ = "egresos"
    descripcion = db.Column(db.String(100), nullable = False)
    importe = db.Column(db.Numeric(precision=15, scale=2))
    nota = db.Column(db.String(256))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()