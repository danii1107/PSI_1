Para esta reentrega lo que hemos modificado ha sido:

I1:
	-Implementando que el settings extraiga las variables de entrono desde el sistema que ha desplegado la aplicación
	-Creado un .env donde se almacenen las variables de entorno recomendadas para el despliegue de la aplicación
	-Puesto el debug a False
	-Modificado las variables de entorno de render

I9:
	-Modificado la plantilla de libros prestados para mostrar la opción 'renew' en caso de tener los permisos necesario.
	-Modificado las vistas de author y book detail para que muestren la opción de eliminar o modificar un autor/libro según sus permisos y no solo si es staff o no.

I10:
	-Redesplegado la aplicación vaciando la BBDD.
	-Poblado la BBDD en el despliegue con populate_catalog.py