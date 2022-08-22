
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, PasswordField, IntegerField)
from wtforms.fields.core import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email


class InicioOfertaForm(FlaskForm):
    nombre_apellido_rs = StringField('Nombre y apellido o Razón social', validators=[DataRequired()])
    dni = IntegerField('DNI o CUIT', validators=[DataRequired()])
    correo_electronico = StringField('Email', validators=[DataRequired(), Email()])
    pin_temporal = PasswordField('Pin temporal', validators=[DataRequired()])
    submit = SubmitField('Enviar')


class OfertaForm(FlaskForm):
    dni = IntegerField('DNI o CUIT', validators=[DataRequired()])
    correo_electronico = StringField('Email', validators=[DataRequired(), Email()])
    importe_a_ofertar = FloatField('Importe a ofertar', validators=[DataRequired()])
    pin_temporal = PasswordField('Pin temporal', validators=[DataRequired()])
    submit = SubmitField('Enviar')