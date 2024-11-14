from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, SelectField)
from wtforms.validators import DataRequired, Length


class UserAdminForm(FlaskForm):
    is_admin = BooleanField('Administrador')
    submit = SubmitField('Guardar')
    
class PermisosUserForm(FlaskForm):
    id_permiso = SelectField('Permiso', choices =[], coerce = str, default = None, validators=[DataRequired('Seleccione un permiso')])

class RolesUserForm(FlaskForm):
    rol = SelectField('Rol', choices =[], coerce = str, default = None, validators=[DataRequired('Seleccione un rol')])