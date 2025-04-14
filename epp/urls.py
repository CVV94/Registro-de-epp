from django.urls import path
from . import views
from .views import asignar_epp, devolver_epp, index
from .views import crear_categoria, crear_producto, crear_trabajador,listado_productos

urlpatterns = [
    path('', views.index, name='home'),
    path('asignar/', asignar_epp, name='asignar_epp'),
    path('devolver/', devolver_epp, name='devolver_epp'),
    path('crear/categoria/', crear_categoria, name='crear_categoria'),
    path('crear/producto/', crear_producto, name='crear_producto'),
    path('crear/trabajador/', crear_trabajador, name='crear_trabajador'),
    path('productos/', listado_productos, name='listado_productos'),
    path('trabajadores/', views.listado_trabajadores, name='listado_trabajadores'), 
    path('eliminar/<str:rut>/', views.eliminar_trabajador, name='eliminar_trabajador'),
    path('eliminar_producto/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('listado_categorias/', views.listado_categorias, name='listado_categorias'),
    path('eliminar_categoria/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('informe/trabajador/<str:rut>/', views.generar_pdf_trabajador, name='informe_trabajador'),

]
