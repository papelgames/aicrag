import datetime
from typing import Text, Optional, List
from flask_login import UserMixin

from sqlalchemy import func, or_, cast, Date, String, Integer, Boolean, Float, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from decimal import Decimal
from app import db


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(162), nullable=False)
    is_admin: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    id_estado: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('estados.id'))
    persona: Mapped[Optional["Personas"]] = relationship('Personas', backref='users', uselist=False)
    permisos: Mapped[List["Permisos"]] = relationship('Permisos', secondary='permisosporusuarios', back_populates='users')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Users.query.get(id)

    @staticmethod
    def get_by_username(username):
        return Users.query.filter_by(username=username).first()

    @staticmethod
    def get_all():
        return Users.query.all()



class Base(db.Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=db.func.current_timestamp())
    modified: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=db.func.current_timestamp(),
                                                                   onupdate=db.func.current_timestamp())


class Proveedores(Base):
    __tablename__ = "proveedores"

    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    correo_electronico: Mapped[Optional[str]] = mapped_column(String(256))
    archivo_si_no: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    formato_id: Mapped[Optional[str]] = mapped_column(String(50))
    columna_id_lista_proveedor: Mapped[Optional[str]] = mapped_column(String(1))
    columna_codigo_de_barras: Mapped[Optional[str]] = mapped_column(String(1))
    columna_descripcion: Mapped[Optional[str]] = mapped_column(String(1))
    columna_importe: Mapped[Optional[str]] = mapped_column(String(1))
    columna_utilidad: Mapped[Optional[str]] = mapped_column(String(1))
    incluye_iva: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))
    producto: Mapped[List["Productos"]] = relationship('Productos', backref='productos', uselist=True)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Proveedores.query.all()

    @staticmethod
    def get_by_archivo_si_no(true_false):
        return Proveedores.query.filter_by(archivo_si_no=true_false).all()

    @staticmethod
    def get_by_id(id_proveedor):
        return Proveedores.query.filter_by(id=id_proveedor).first()


class Productos(Base):
    __tablename__ = "productos"

    codigo_de_barras: Mapped[Optional[str]] = mapped_column(String(256))
    id_proveedor: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('proveedores.id'))
    id_lista_proveedor: Mapped[Optional[str]] = mapped_column(String(256))
    descripcion: Mapped[Optional[str]] = mapped_column(String(256))
    importe: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=15, scale=2))
    cantidad_presentacion: Mapped[Optional[float]] = mapped_column(Float, default=1)
    id_ingreso: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))
    es_servicio: Mapped[Optional[bool]] = mapped_column(Boolean)
    utilidad: Mapped[Optional[float]] = mapped_column(Float)
    producto_presupuesto: Mapped[List["ProductosPresupuestos"]] = relationship('ProductosPresupuestos', backref='productos_en_presupuestos', uselist=True)

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
            .filter(or_(Productos.codigo_de_barras.is_(None),
                        Productos.codigo_de_barras == "",
                        Productos.codigo_de_barras == " ",
                        Productos.codigo_de_barras == "#N/A"))\
            .all()
        return query_str

    @staticmethod
    def get_all_precios_dbf():
        valor_calculado = ((((Productos.importe * Productos.utilidad) / 100) + Productos.importe) / Productos.cantidad_presentacion)
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
        valor_calculado = ((((Productos.importe * Productos.utilidad) / 100) + Productos.importe) / Productos.cantidad_presentacion)
        query_str = db.session.query(Productos.id, Productos.importe)\
            .filter(Productos.codigo_de_barras == codigo_barras)\
            .filter(valor_calculado == db.session.query(func.max(valor_calculado))
                    .filter(Productos.codigo_de_barras == codigo_barras))\
            .first()
        return query_str

    @staticmethod
    def get_by_codigo_de_barras(codigo_barras):
        valor_calculado = ((((Productos.importe * Productos.utilidad) / 100) + Productos.importe) / Productos.cantidad_presentacion)
        query_str = db.session.query(Productos, Proveedores, valor_calculado.label('importe_calculado'))\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.codigo_de_barras == codigo_barras)\
            .all()
        return query_str

    @staticmethod
    def get_by_id_completo(id_producto):
        valor_calculado = ((((Productos.importe * Productos.utilidad) / 100) + Productos.importe) / Productos.cantidad_presentacion)
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
        valor_calculado = ((((Productos.importe * Productos.utilidad) / 100) + Productos.importe) / Productos.cantidad_presentacion)
        query_str = db.session.query(Productos, Proveedores, valor_calculado.label('importe_calculado'))\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.descripcion.contains(descripcion_))\
            .all()
        return query_str

    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        descripcion_ = descripcion_.replace(' ', '%')
        valor_calculado = ((((Productos.importe * Productos.utilidad) / 100) + Productos.importe) / Productos.cantidad_presentacion)
        return db.session.query(Productos, Proveedores, valor_calculado.label('importe_calculado'))\
            .filter(Productos.id_proveedor == Proveedores.id)\
            .filter(Productos.descripcion.contains(descripcion_))\
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id_lista_proveedor(id_lista, id_proveedor):
        return Productos.query.filter_by(id_lista_proveedor=id_lista, id_proveedor=id_proveedor).first()

    @staticmethod
    def get_by_id(id_producto):
        return Productos.query.filter_by(id=id_producto).first()


class TiposVentas(Base):
    __tablename__ = "tiposventas"

    clave: Mapped[Optional[int]] = mapped_column(Integer)
    descripcion: Mapped[Optional[str]] = mapped_column(String(25))
    cabecera_presupuesto: Mapped[List["CabecerasPresupuestos"]] = relationship('CabecerasPresupuestos', backref='cabeceras_presupuestos', uselist=True)
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return TiposVentas.query.all()

    @staticmethod
    def get_first_by_clave_tabla(clave):
        return TiposVentas.query.filter_by(clave=clave).first()


class CabecerasPresupuestos(Base):
    __tablename__ = "cabeceraspresupuestos"

    fecha_vencimiento: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    nombre_cliente: Mapped[Optional[str]] = mapped_column(String(256))
    correo_electronico: Mapped[Optional[str]] = mapped_column(String(256))
    importe_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=15, scale=2))
    id_estado: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('estados.id'))
    id_tp_ventas: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('tiposventas.id'))
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))
    producto_presupuesto: Mapped[List["ProductosPresupuestos"]] = relationship('ProductosPresupuestos', backref='productos_presupuestos', uselist=True)

    def only_add(self):
        db.session.add(self)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_presupuesto):
        return CabecerasPresupuestos.query.filter_by(id=id_presupuesto).first()

    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        return CabecerasPresupuestos.query.filter(CabecerasPresupuestos.nombre_cliente.contains(descripcion_))\
            .order_by(CabecerasPresupuestos.fecha_vencimiento.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_fecha(fecha, id_tp_ventas, page=1, per_page=20):
        return CabecerasPresupuestos.query.filter(cast(CabecerasPresupuestos.created, Date) == fecha)\
            .filter(CabecerasPresupuestos.id_tp_ventas == id_tp_ventas)\
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_all():
        return db.session.query(CabecerasPresupuestos).order_by(CabecerasPresupuestos.fecha_vencimiento.desc()).all()

    @staticmethod
    def get_all_estado(id_estado, page=1, per_page=20):
        return CabecerasPresupuestos.query.filter_by(id_estado=id_estado)\
            .paginate(page=page, per_page=per_page, error_out=False)


class ProductosPresupuestos(Base):
    __tablename__ = "productospresupuestos"

    id_cabecera_presupuesto: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('cabeceraspresupuestos.id'))
    id_producto: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('productos.id'))
    cantidad: Mapped[Optional[int]] = mapped_column(Integer)
    descripcion: Mapped[Optional[str]] = mapped_column(String(256))
    importe: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=15, scale=2))
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))

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
        return ProductosPresupuestos.query.filter_by(id=id).first()

    @staticmethod
    def get_by_id_presupuesto(id_presupuesto):
        return ProductosPresupuestos.query.filter_by(id_cabecera_presupuesto=id_presupuesto).all()

    @staticmethod
    def get_q_by_id_presupuesto_q(id_presupuesto):
        return ProductosPresupuestos.query.filter_by(id_cabecera_presupuesto=id_presupuesto).count()

    @staticmethod
    def get_importe_total_by_id_presupuesto(id_presupuesto):
        return db.session.query(ProductosPresupuestos.id_cabecera_presupuesto, func.sum(ProductosPresupuestos.importe * ProductosPresupuestos.cantidad))\
            .filter(ProductosPresupuestos.id_cabecera_presupuesto == id_presupuesto).first()


class Compras(Base):
    __tablename__ = "compras"

    id_cierre: Mapped[Optional[int]] = mapped_column(Integer)
    id_proveedor: Mapped[Optional[int]] = mapped_column(Integer)
    id_producto: Mapped[Optional[int]] = mapped_column(Integer)
    codigo_de_barras: Mapped[Optional[str]] = mapped_column(String(256))
    cantidad: Mapped[Optional[int]] = mapped_column(Integer)
    importe: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=15, scale=2))
    fecha_cierre: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    estado: Mapped[Optional[int]] = mapped_column(Integer)
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))


class Parametros(Base):
    __tablename__ = "parametros"

    descripcion: Mapped[Optional[str]] = mapped_column(String(50))
    tabla: Mapped[Optional[str]] = mapped_column(String(50))
    tipo_parametro: Mapped[Optional[str]] = mapped_column(String(50))

    @staticmethod
    def get_by_tabla(tabla):
        return Parametros.query.filter_by(tabla=tabla).first()


class Personas(Base):
    __tablename__ = "personas"

    descripcion_nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    cuit: Mapped[str] = mapped_column(String(11), nullable=False)
    correo_electronico: Mapped[Optional[str]] = mapped_column(String(256))
    telefono: Mapped[Optional[str]] = mapped_column(String(256))
    tipo_persona: Mapped[Optional[str]] = mapped_column(String(50))
    id_estado: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('estados.id'))
    nota: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))
    id_usuario: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Personas.query.all()

    @staticmethod
    def get_by_id(id_persona):
        return Personas.query.filter_by(id=id_persona).first()

    @staticmethod
    def get_by_cuit(cuit):
        return Personas.query.filter_by(cuit=cuit).first()

    @staticmethod
    def get_by_correo(correo):
        return Personas.query.filter_by(correo_electronico=correo).first()

    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        descripcion_ = f"%{descripcion_}%"
        return db.session.query(Personas)\
            .filter(Personas.descripcion_nombre.contains(descripcion_))\
            .paginate(page=page, per_page=per_page, error_out=False)


class Estados(Base):
    __tablename__ = "estados"

    clave: Mapped[Optional[int]] = mapped_column(Integer)
    descripcion: Mapped[Optional[str]] = mapped_column(String(50))
    tabla: Mapped[Optional[str]] = mapped_column(String(50))
    inicial: Mapped[Optional[bool]] = mapped_column(Boolean)
    final: Mapped[Optional[bool]] = mapped_column(Boolean)
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))
    cabecera_presupuesto: Mapped[List["CabecerasPresupuestos"]] = relationship('CabecerasPresupuestos', backref='estado_presupuestos', uselist=True)
    persona: Mapped[List["Personas"]] = relationship('Personas', backref='estado_personas', uselist=True)
    user: Mapped[List["Users"]] = relationship('Users', backref='estado_users', uselist=True)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Estados.query.all()

    @staticmethod
    def get_first_by_clave_tabla(clave, tabla):
        return Estados.query.filter_by(clave=clave, tabla=tabla).first()


class PermisosPorUsuarios(Base):
    __tablename__ = "permisosporusuarios"

    id_permiso: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('permisos.id'))
    id_usuario: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'))


class Roles(Base):
    __tablename__ = "roles"

    descripcion: Mapped[Optional[str]] = mapped_column(String(50))
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))
    permisos: Mapped[List["Permisos"]] = relationship('Permisos', secondary='permisosenroles', back_populates='roles')

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
        return Roles.query.filter_by(id=id).all()

    @staticmethod
    def get_all():
        return Roles.query.all()

    @staticmethod
    def get_all_descripcion_agrupada():
        return db.session.query(Roles.descripcion.label('nombre_rol')).distinct().all()


class PermisosEnRoles(Base):
    __tablename__ = "permisosenroles"

    id_permiso: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('permisos.id'))
    id_roles: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('roles.id'))


class Permisos(Base):
    __tablename__ = "permisos"

    descripcion: Mapped[Optional[str]] = mapped_column(String(50))
    roles: Mapped[List["Roles"]] = relationship('Roles', secondary='permisosenroles', back_populates='permisos')
    users: Mapped[List["Users"]] = relationship('Users', secondary='permisosporusuarios', back_populates='permisos')
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))

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
        return Permisos.query.filter_by(id=id_permiso).first()

    @staticmethod
    def get_by_descripcion(descripcion):
        return Permisos.query.filter_by(descripcion=descripcion).first()

    @staticmethod
    def get_permisos_no_relacionadas_roles(id_rol):
        return Permisos.query.filter(~Permisos.roles.any(id=id_rol)).all()

    @staticmethod
    def get_permisos_no_relacionadas_personas(id_persona):
        return Permisos.query.filter(~Permisos.users.any(id=id_persona)).all()


class Egresos(Base):
    __tablename__ = "egresos"

    descripcion: Mapped[str] = mapped_column(String(100), nullable=False)
    importe: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=15, scale=2))
    nota: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    usuario_modificacion: Mapped[Optional[str]] = mapped_column(String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_fecha(fecha, page=1, per_page=20):
        return Egresos.query.filter(cast(Egresos.created, Date) == fecha)\
            .paginate(page=page, per_page=per_page, error_out=False)


class TareasSistema(Base):
    __tablename__ = "tareassistema"

    id_rq: Mapped[str] = mapped_column(String(36))
    name: Mapped[str] = mapped_column(String(128), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(128))
    complete: Mapped[bool] = mapped_column(default=False)
    usuario_alta: Mapped[Optional[str]] = mapped_column(String(256))
    error: Mapped[bool] = mapped_column(default=False)
    

    #user: Mapped[Users] = relationship(back_populates='tasks')

    # def get_rq_job(self):
    #     try:
    #         rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
    #     except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
    #         return None
    #     return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
    
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()


    def get_tasks_in_progress(self):
        query = self.select().where(TareasSistema.complete == False)
        return db.session.scalars(query)

    def get_task_in_progress(self, name):
        query = self.select().where(TareasSistema.name == name,
                                          TareasSistema.complete == False)
        return db.session.scalar(query)
    

class MensajesSistema(Base):
    __tablename__ = "mensajessistema"

    asunto: Mapped[str] = mapped_column(String(60))
    cuerpo: Mapped[str] = mapped_column(String(140))
    leido: Mapped[bool] = mapped_column(default=False)
    alerta: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return '<Message {}>'.format(self.cuerpo)
    
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return MensajesSistema.query.all()
    
    @staticmethod
    def get_mensaje_by_id(id):

        return MensajesSistema.query.get(id)

    @staticmethod
    def get_count_sin_leer():
        return MensajesSistema.query.filter_by(leido=False).count()