import dbf
from datetime import datetime
from app.models import Productos
from flask import current_app
from app import create_app
import os

from dotenv import load_dotenv

load_dotenv()
settings_module = os.getenv('APP_SETTINGS_MODULE')
app = create_app(settings_module)

app.app_context().push()

def to_precios_dbf():
   print ("Empieza")
   print (datetime.now())
   archivo_dir = current_app.config['ARCHIVOS_DIR']
   table = dbf.Table(archivo_dir + '/precios.dbf', 'CODIGO C(13); DETALLE C(56); PRECIOVP N(15,4)', codepage='cp1252', dbf_type='db3')
   table.open(mode=dbf.READ_WRITE)
   productos_precios = Productos.get_all_precios_dbf()
   
   # Agregamos algunas filas de ejemplo
   for row in productos_precios:
      
      table.append((row[0][:13],row[1][:56],round(row[2],2)))

   # Guardamos la tabla y cerramos el archivo
   table.pack()
   table.close()
   print ("termina")
   print (datetime.now())