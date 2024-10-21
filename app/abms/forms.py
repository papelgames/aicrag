
from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, IntegerField, DateField, SelectField)
from wtforms.fields import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError


class ProveedoresForm(FlaskForm):
    nombre = StringField('Nombre del proveedor',validators=[DataRequired('Complete el nombre del proveedor')])
    correo_electronico = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    archivo_si_no = SelectField('¿Actualiza por archivo?', choices =[( '' ,'Seleccionar acción'),( '1','Si'),( '0','NO')],coerce = str,  validators=[DataRequired('Completar si o no')])
    formato_id = StringField('Formato de ID del proveedor')
    columna_id_lista_proveedor = SelectField('Código del proveedor', choices =[], coerce = str, default = None)
    columna_codigo_de_barras = SelectField('Código de barras', choices =[], coerce = str, default = None)
    columna_descripcion = SelectField('Descripción del producto', choices =[], coerce = str, default = None)
    columna_importe = SelectField('Importe', choices =[], coerce = str, default = None)
    columna_utilidad = SelectField('Utilidad', choices =[], coerce = str, default = None)
    incluye_iva = SelectField('¿Lista con iva?', choices =[( '','Seleccionar acción'),( '1','Si'),( '0','NO')], coerce = str, default = None, validators=[DataRequired('Completar si o no')])

    def validate_formato_id(self, formato_id):
        if self.archivo_si_no.data == "1" and not formato_id.data:
            raise ValidationError('Complete el formato del ID del proveedor.')
    
    def validate_columna_id_lista_proveedor(self, columna_id_lista_proveedor):
        if self.archivo_si_no.data == "1" and not columna_id_lista_proveedor.data:
            raise ValidationError('Debe seleccionar una columna.')

    def validate_columna_codigo_de_barras(self, columna_codigo_de_barras):
        if self.archivo_si_no.data == "1" and not columna_codigo_de_barras.data:
            raise ValidationError('Debe seleccionar una columna.')

    def validate_columna_descripcion(self, columna_descripcion):
        if self.archivo_si_no.data == "1" and not columna_descripcion.data:
            raise ValidationError('Debe seleccionar una columna.')

    def validate_columna_importe(self, columna_importe):
        if self.archivo_si_no.data == "1" and not columna_importe.data:
            raise ValidationError('Debe seleccionar una columna.')

    def validate_columna_utilidad(self, columna_utilidad):
        if self.archivo_si_no.data == "1" and not columna_utilidad.data:
            raise ValidationError('Debe seleccionar una columna.')


class ProveedoresConsultaForm(FlaskForm):
    id_proveedor = SelectField('Código del proveedor', choices =[], coerce = str, default = None)

class ProductosForm(FlaskForm):
    codigo_de_barras = IntegerField('Código de barras')
    id_proveedor = SelectField('Código del proveedor', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar un proveedor')])
    id_lista_proveedor = StringField('Id del producto del proveedor')
    descripcion = StringField('Descripcion del producto',validators=[DataRequired('Complete la descripcion del producto' )])
    importe = FloatField('Importe del producto', validators=[DataRequired('Ingrese el importe del producto sin iva' )] )
    utilidad = StringField('Porcentaje de utilidad', default = 0 )
    cantidad_presentacion = FloatField('Cantidad de productos por presentación')
    es_servicio = SelectField('¿Es servicio?', choices =[( '','Seleccionar acción'),( "1",'Si'),( "0",'NO')], coerce = str, default = None, validators=[DataRequired('Completar si o no')])

    def validate_utilidad(self, utilidad):
        if self.es_servicio.data == "0" and utilidad.data == "0":
            raise ValidationError('Debe cargar la utilidad del producto.')

class ProductosMasivosForm(FlaskForm):
    id_proveedor = SelectField('Código del proveedor', choices =[], coerce = str, default = None, validators=[DataRequired('Debe seleccionar un proveedor')])
    archivo = FileField('Archivo de alta', validators=[
              DataRequired('Debe seleccionar un archivo' ),
              FileAllowed(['xlsx'], 'No es un archivo permitido')
              ])

class BusquedaForm(FlaskForm):
    buscar = StringField('Buscar', validators=[DataRequired('Escriba la descripción de un producto o su código de barras' )])
 