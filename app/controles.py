from rq import Worker
from flask import current_app
from app.models import Personas
from wtforms.validators import DataRequired, Length, Email, ValidationError

def get_tarea_corriendo(tarea_nombre):
   todas_las_tareas = []
   queue = current_app.task_queue
   workers = Worker.all(queue=queue)
   worker = workers[0]   
   tareas_pendientes = queue.jobs
   if worker.state == 'busy':
      todas_las_tareas.append(worker.get_current_job().func_name)
      if tareas_pendientes:
         for tarea in tareas_pendientes:
            todas_las_tareas.append(tarea.func_name)
  
   if tarea_nombre in todas_las_tareas:
       return True

def validar_correo(self, field ):
    correo_persona = Personas.get_by_correo(field.data)
    datos_persona_actual = Personas.get_by_id(self.id.data)
    if datos_persona_actual:
        if field.data == correo_persona.correo_electronico and datos_persona_actual and datos_persona_actual.id != correo_persona.id:
            raise ValidationError('El correo electrónico ya está dado de alta en otra persona.')
    else:
        if correo_persona:
            raise ValidationError('El correo electrónico ya está dado de alta en otra persona.')

def validar_cuit(self, field ):
    cuit_persona = Personas.get_by_cuit(field.data)
    datos_persona_actual = Personas.get_by_id(self.id.data)

    if datos_persona_actual:
        if field.data == cuit_persona.cuit and datos_persona_actual and datos_persona_actual.id != cuit_persona.id:
            raise ValidationError('El CUIT ya está dado de alta en otra persona.')
    else:
        if cuit_persona:
            raise ValidationError('El CUIT ya está dado de alta en otra persona.')