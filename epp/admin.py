from django.contrib import admin
from .models import Categoria, Producto, Trabajador, AsignacionEpp, DevolucionEpp

# Register your models here.
registered_models = [Categoria, Producto, Trabajador, AsignacionEpp, DevolucionEpp]
for model in registered_models:
    admin.site.register(model)
