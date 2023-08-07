
## Funcionalidades del aicrag sistema de gestion


### Variables de entorno

Para que la app funcione debes crear las siguientes variables de entorno:

#### Linux/Mac

    export FLASK_APP="entrypoint"
    export FLASK_ENV="development"
    export APP_SETTINGS_MODULE="config.local"

#### Windows

    set "FLASK_APP=entrypoint"
    set "FLASK_ENV=development"
    set "APP_SETTINGS_MODULE=config.local"
    
> Mi recomendación para las pruebas es que añadas esas variables en el fichero "activate" o "activate.bat"
> si estás usando virtualenv
 
### Instalación de dependencias

En el proyecto se distribuye un fichero (requirements.txt) con todas las dependencias. Para instalarlas
basta con ejectuar:

    pip install -r requirements.txt

## Migraciones de bd
flask db init
flask db migrate -m "Initial database"
flask db upgrade

flask db stamp head solo para sqlite
## Ejecución con el servidor que trae Flask

Una vez que hayas descargado el proyecto, creado las variables de entorno e instalado las dependencias,
puedes arrancar el proyecto ejecutando:

    flask run


## parametrias iniciales
insert into parametros (descripcion, tabla, tipo_parametro) values ("","dias_vencimiento","10");
insert into parametros (descripcion, tabla, tipo_parametro) values ("","dias_actualizacion","15");
insert into parametros (descripcion, tabla, tipo_parametro) values ("Activo","estado_presupuesto","1");
insert into parametros (descripcion, tabla, tipo_parametro) values ("Vencido","estado_presupuesto","2");
insert into parametros (descripcion, tabla, tipo_parametro) values ("Anulado","estado_presupuesto","3");
insert into parametros (descripcion, tabla, tipo_parametro) values ("Iniciado","estado_presupuesto","4");

## Instalación de redis server (sistema debian, ubuntu o derivados)
sudo apt install redis-server 

## Iniciar worker para que comiencen las colas
rq worker aicrag-tareas
