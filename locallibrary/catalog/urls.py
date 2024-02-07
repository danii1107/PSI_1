from django.urls import path
from . import views

urlpatterns = [
	path('create_mymodelname/', views.create_mymodelname, name='create_mymodelname'),
]
