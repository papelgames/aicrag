from tarfile import PAX_NUMBER_FIELDS
from threading import activeCount
from flask_login import UserMixin
from jinja2 import PrefixLoader
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Personas, Permisos
from app import db

class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(162), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    id_estado = db.Column(db.Integer)
    persona = db.relationship('Personas', backref='users', uselist=False)
    permisos = db.relationship('Permisos', secondary='permisosporusuarios', back_populates='users')
    
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
