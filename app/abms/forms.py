
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, IntegerField, DateField, SelectField)
from wtforms.fields.core import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email


class TareasForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired('Complete la descripcion de la tarea')])
    vencimiento = IntegerField('Dias de vencimiento', validators=[DataRequired('Complete la cantidad días de vencimiento')])
    modulo_inicial = StringField('Módulo Inicial')

class AccionesForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired('Complete la descripciín de la acción')])
    estado_recupero = SelectField('Estado', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar un estado')])
    envia_correo = SelectField('Envia correo', choices =[], coerce = str,  validators=[DataRequired('Completar si o no')])
    id_tarea_siguiente = SelectField('Tarea siguiente', choices =[], coerce = str, default = None)
    programa = StringField('Programa que ejecuta la acción', validators=[DataRequired('Nombre del programa a ejecutar')])
    finaliza = BooleanField('Finaliza')

class TareasAccionesForm(FlaskForm):
    accion = SelectField('Accion', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar una acción')])
    tarea = SelectField('Tarea', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar una tarea ')])
