from django.shortcuts import render
from django.http import HttpResponse
from .models import MyModelName

def create_mymodelname(request):
    # Creación de un nuevo registro usando el constructor del modelo.
    a_record = MyModelName(my_field_name="Instancia #1")
    # Guardar el objeto en la base de datos.
    a_record.save()
    # Devuelve una respuesta HTTP
    return HttpResponse("MyModelName creado con éxito.")
