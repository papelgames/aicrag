
from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, DateField,  SelectField, HiddenField)
from wtforms.fields import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange


class BusquedaForm(FlaskForm):
    buscar = StringField('Buscar')

class CabeceraPresupuestoForm(FlaskForm):
    nombre_cliente = StringField("Cliente", validators=[DataRequired('Debe cargar el nombre del cliente' )])
    correo_electronico = StringField('Correo electrónico', validators=[Email()])
    fecha_vencimiento = DateField('Fecha de vencimiento',validators=[DataRequired('El vencimiento no puede estar vacío')])
    
    
class ProductosPresupuestoForm(FlaskForm):
    buscar = StringField('Buscar')
    id = IntegerField()
    descripcion = StringField()
    cantidad = IntegerField()
    importe = FloatField()
    condicion = StringField()
    registro = StringField()
