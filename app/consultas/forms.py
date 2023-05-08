
from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, DateField,  SelectField, HiddenField)
from wtforms.fields.core import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Required, Email, NumberRange


class BusquedaForm(FlaskForm):
    buscar = StringField('Buscar')
