from app.models import Productos, Proveedores
from flask import current_app
from app import create_app
import os
from werkzeug.utils import secure_filename
from time import strftime, gmtime
import locale
from dotenv import load_dotenv

load_dotenv()
settings_module = os.getenv('APP_SETTINGS_MODULE')
app = create_app(settings_module)

app.app_context().push()

def to_precios_dbf():
   # Filtrar y preparar los datos para la inserción
   archivo_dir = current_app.config['ARCHIVOS_PARA_DESCARGA']
   productos_precios = Productos.get_all_precios_dbf()
   table = [(f'CODIGO,C,13\tDETALLE,C,56\tPRECIOVP,N,10,4')]
   errores = []
   locale.setlocale(locale.LC_ALL, '')
   
   #recorro la tabla y si ha precios que no concuerdan con el tipo de precio que soporta el dbf armo un archivo txt
   #para que el usuario pueda revisar esos productos y corregirlos. 

   for row in productos_precios:
      if len(str(round(row[2]))) > 10:
         errores.append(f'{row[0][:13]}\t{row[1][:56]}\t{row[2]}')
      else:
         table.append(f'{row[0][:13]}\t{row[1][:56]}\t{locale.format("%.2f", row[2], grouping=True, monetary=True)}')
   # Inserto los importes no soportados en el archivo precios_elevados.txt siempre y cuando haya.
   if errores:
      with open(archivo_dir + '/precios_elevados.txt', 'w') as errores_file:
         errores_file.write('\n'.join(errores))
   
   # Inserto los datos en el archivo .dbf
   with open(archivo_dir + '/Precios.dbf', 'w') as precios_file:
      precios_file.write('\n'.join(table))
   
def in_lista_masiva(file_path, id_proveedor, email):
   proveedor = Proveedores.get_by_id(id_proveedor)

   #abro documento excel
   import openpyxl 
   documento = openpyxl.load_workbook(os.path.abspath(file_path), data_only= True)
   ws = documento.active
   
   #traigo parametria del proveedor
   columnas = [proveedor.nombre,
               proveedor.formato_id,
               proveedor.columna_id_lista_proveedor, 
               proveedor.columna_codigo_de_barras, 
               proveedor.columna_descripcion,
               proveedor.columna_importe,
               proveedor.columna_utilidad ]
   
   #indico que al excel en que columnas el proveedor carga cada dato.
   rango_id_lista_proveedor =  ws[columnas[2]]
   rango_codigo_de_barras =  ws[columnas[3]]
   rango_descripcion =  ws[columnas[4]]
   rango_importe =  ws[columnas[5]]
   rango_utilidad = ws[columnas[6]]
   #incremental de cada caso
   registros_nuevos = 0
   registros_actualizados = 0
   registros_total = 0
   registros_ignorados = 0
   #genero un id unico por subida para cada registro
   id_ingreso = str(strftime('%d%m%y%H%m%s', gmtime()))
   #creo una matriz con los datos del excel para luego iterarla.   
   mat = list(zip(rango_id_lista_proveedor, rango_codigo_de_barras, rango_descripcion, rango_importe, rango_utilidad))
   #inserto los registros que no existen
   producto_nuevo = Productos()
   for id in mat:
      if id[0].value != None and str(id[0].value).upper() != str(columnas[1]).upper(): 
         producto_por_id = Productos.get_by_id_lista_proveedor(id[0].value)
         registros_total += 1
         if not producto_por_id:
            if id[4].value == None:
                  utilidad_ = 100
            else:
                  utilidad_ = id[4].value
            #antes de grabar chequeo si el proveedor guarda con iva o no
            if proveedor.incluye_iva == True:
                  producto_nuevo = Productos(codigo_de_barras = id[1].value,
                                          id_proveedor = id_proveedor,
                                          id_lista_proveedor = id[0].value,
                                          descripcion = id[2].value,
                                          importe = round(id[3].value,2),
                                          utilidad = utilidad_,
                                          cantidad_presentacion = 1,
                                          id_ingreso = id_ingreso,
                                          es_servicio = False,
                                          usuario_alta = email,
                                          usuario_modificacion = email
                                          )
                  registros_nuevos += 1 
            else:
                  producto_nuevo = Productos(codigo_de_barras = id[1].value,
                                             id_proveedor = id_proveedor,
                                             id_lista_proveedor = id[0].value,
                                             descripcion = id[2].value,
                                             importe = round(id[3].value * 1.21 ,2),
                                             utilidad = utilidad_,
                                             cantidad_presentacion = 1,
                                             id_ingreso = id_ingreso,
                                             es_servicio = False,
                                             usuario_alta = email,
                                             usuario_modificacion = email
                                             )
                  registros_nuevos += 1
            producto_nuevo.only_add()
         
         #actualizo productos que existe si es que tienen un importe distinto al cargado.    
         if producto_por_id:
            if proveedor.incluye_iva == True:
               if float(producto_por_id.importe) != round(id[3].value,2):    
                  producto_por_id.importe = round(id[3].value,2)
                  producto_por_id.usuario_modificacion = email
                  producto_por_id.id_ingreso = id_ingreso
                  registros_actualizados += 1   
                  producto_por_id.only_add()
               else:
                  registros_ignorados += 1 
            else:
               if float(producto_por_id.importe) != round(id[3].value * 1.21 ,2):
                  producto_por_id.importe = round(id[3].value * 1.21 ,2)
                  producto_por_id.usuario_modificacion = email
                  producto_por_id.id_ingreso = id_ingreso 
                  registros_actualizados += 1
                  producto_por_id.only_add()
               else:
                  registros_ignorados += 1
               
   #commiteo las tablas
   if producto_por_id:
         producto_por_id.save()
   producto_nuevo.only_save()
