
from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, IntegerField, DateField, SelectField)
from wtforms.fields.core import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email


class ProveedoresForm(FlaskForm):
    nombre = StringField('Nombre del proveedor',validators=[DataRequired('Complete el nombre del proveedor')])
    correo_electronico = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    archivo_si_no = SelectField('¿Actualiza por archivo?', choices =[( '' ,'Seleccionar acción'),( '1','Si'),( '0','NO')],coerce = str,  validators=[DataRequired('Completar si o no')])
    formato_id = StringField('Formato de ID del proveedor', validators=[DataRequired('Complete el formato del ID del proveedor')])
    columna_id_lista_proveedor = SelectField('Código del proveedor', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar una una columna')])
    columna_codigo_de_barras = SelectField('Código de barras', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar una una columna')])
    columna_descripcion = SelectField('Descripción del producto', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar una una columna')])
    columna_importe = SelectField('Importe', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar una una columna')])
    columna_utilidad = SelectField('Utilidad', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar una una columna')])
    incluye_iva = SelectField('¿Lista con iva?', choices =[( '','Seleccionar acción'),( '1','Si'),( '0','NO')], coerce = str, default = None, validators=[DataRequired('Completar si o no')])

class ProveedoresConsultaForm(FlaskForm):
    id_proveedor = SelectField('Código del proveedor', choices =[], coerce = str, default = None)

class ProductosForm(FlaskForm):
    codigo_de_barras = IntegerField('Código de barras')
    id_proveedor = SelectField('Código del proveedor', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar un proveedor')])
    id_lista_proveedor = StringField('Id del producto del proveedor')
    descripcion = StringField('Descripcion del producto',validators=[DataRequired('Complete la descripcion del producto' )])
    importe = FloatField('Importe del producto', validators=[DataRequired('Ingrese el importe del producto sin iva' )] )
    utilidad = FloatField('Porcentaje de utilidad', validators=[DataRequired('Ingrese el porcentaje que quiere cargarle al producto/servicio' )] ) # validar que si es servicio se se pueda grabar en cero 
    cantidad_presentacion = FloatField('Cantidad de productos por presentación')
    es_servicio = SelectField('¿Es servicio?', choices =[( '','Seleccionar acción'),( "1",'Si'),( "0",'NO')], coerce = str, default = None, validators=[DataRequired('Completar si o no')])

class ProductosMasivosForm(FlaskForm):
    id_proveedor = SelectField('Código del proveedor', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar un proveedor')])
    archivo = FileField('Archivo de alta', validators=[
              DataRequired('Debe seleccionar un archivo' ),
              FileAllowed(['xls', 'xlsx', 'xltm'], 'No es un archivo permitido')
              ])

class BusquedaForm(FlaskForm):
    buscar = StringField('Buscar', validators=[DataRequired('Escriba la descripción de un producto o su código de barras' )])
 