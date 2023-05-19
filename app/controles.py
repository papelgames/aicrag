from rq import Worker
from flask import current_app

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

