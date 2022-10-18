
from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, DateField,  SelectField, HiddenField)
from wtforms.fields.core import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Required, Email



class BusquedaForm(FlaskForm):
    buscar = StringField('Buscar')

class CabeceraPresupuesto(FlaskForm):
    nombre_cliente = StringField("Cliente", validators=[DataRequired('Debe cargar el nombre del cliente' )])
    correo_electronico = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    fecha_vencimiento = DateField('Fecha de vencimiento',format='%d/%m/%Y', validators=[DataRequired('El vencimiento no puede estar vacío' )])

class ProductosPresupuesto (FlaskForm):
    id = HiddenField()
    descripcion = HiddenField()
    cantidad = IntegerField()
    importe = FloatField()