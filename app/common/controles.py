from rq import Worker
from flask import current_app
from app.models import Personas, TareasSistema
from wtforms.validators import DataRequired, Length, Email, ValidationError

def get_tarea_corriendo():
    queue = current_app.task_queue
    workers = Worker.all(queue=queue)
    for worker in workers:
        if worker.state == 'busy':
            job = worker.get_current_job()
            id_rq = job.id
            tarea=TareasSistema.get_by_id_rq(id_rq)
            if tarea.name == 'Alta masiva de productos':
                return tarea.get_progress()


def validar_correo(self, field ):
    correo_persona = Personas.get_by_correo(field.data)
    datos_persona_actual = Personas.get_by_id(self.id.data)
    if datos_persona_actual:
        if correo_persona and field.data == correo_persona.correo_electronico and datos_persona_actual and datos_persona_actual.id != correo_persona.id:
            raise ValidationError('El correo electrónico ya está dado de alta en otra persona.')
    else:
        if correo_persona:
            raise ValidationError('El correo electrónico ya está dado de alta en otra persona.')

def validar_cuit(self, field ):
    cuit_persona = Personas.get_by_cuit(field.data)
    datos_persona_actual = Personas.get_by_id(self.id.data)

    if datos_persona_actual:
        if cuit_persona and field.data == cuit_persona.cuit and datos_persona_actual and datos_persona_actual.id != cuit_persona.id:
            raise ValidationError('El CUIT ya está dado de alta en otra persona.')
    else:
        if cuit_persona:
            raise ValidationError('El CUIT ya está dado de alta en otra persona.')