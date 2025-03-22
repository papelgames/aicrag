
from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, IntegerField, DateField, SelectField, HiddenField)
from wtforms.fields import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from app.controles import validar_correo, validar_cuit

class EgresosForm(FlaskForm):
    descripcion = StringField('Nombre del proveedor',validators=[DataRequired('Complete una descripción')])
    importe = FloatField('Importe del producto', validators=[DataRequired('Ingrese el importe del egreso' )] )
    nota = TextAreaField('Nota', validators=[Length(max=256)])

class DiarioForm(FlaskForm):
    dia = DateField('Elije un día: ', validators=[DataRequired('Debe seleccionar un día')])