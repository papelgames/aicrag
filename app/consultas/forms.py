
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, DateField,  SelectField)
from wtforms.fields.core import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Required


class AltaCompulsaForm(FlaskForm):
    bien = StringField('Descripción del bien', validators=[DataRequired(), Length(max=128)])
    siniestro = IntegerField('Número de siniestro', validators=[DataRequired('Debe completar el número de siniestro')])
    patente = StringField('Patente', validators=[DataRequired('Debe completar la patente')])
    fecha_inicio = DateField('Inicio de compulsa',format='%d/%m/%Y',validators=[Required('Debe completar la fecha de inicio')])
    fecha_vencimiento = DateField('Fin de compulsa',format='%d/%m/%Y', validators=[Required('Debe completar la fecha de vencimiento')])
    ubicacion = StringField('Ubicación del bien', validators=[DataRequired(), Length(max=128)])
    condiciones_generales = TextAreaField('Condiciones generales', validators=[DataRequired()])
    importe_base = FloatField('Importe base de la compulsa', validators=[DataRequired()])
    para_empleados = BooleanField('¿Es empleado?')
    tipo_bien = SelectField('Tipo de bien', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar un tipo de bien')])
    submit = SubmitField('Siguiente')


class ImagenesBienesForm(FlaskForm):
    imagenes_bienes = FileField('Imagen de bienes', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo se permiten imágenes')
    ])
    submit = SubmitField('Guardar')