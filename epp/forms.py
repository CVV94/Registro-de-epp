from django import forms
from .models import Categoria, Producto, Trabajador, AsignacionEpp, DevolucionEpp

class AsignacionEppForm(forms.ModelForm):
    class Meta:
        model = AsignacionEpp
        fields = ['trabajador', 'producto', 'cantidad']

class DevolucionEppForm(forms.ModelForm):
    class Meta:
        model = DevolucionEpp
        fields = ['asignacion', 'cantidad']

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'stock', 'talla', 'categoria']

class TrabajadorForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = ['rut', 'nombre', 'apellido']

class AsignacionEppForm(forms.ModelForm):
    class Meta:
        model = AsignacionEpp
        fields = ['trabajador', 'producto', 'cantidad', 'fecha_asignacion']
        widgets = {
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_asignacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

