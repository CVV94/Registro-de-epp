from django.shortcuts import render
from django.shortcuts import redirect
from .models import AsignacionEpp, DevolucionEpp, Trabajador, Producto
from .forms import AsignacionEppForm, DevolucionEppForm
from .models import Categoria
from django.views.generic import TemplateView
from .forms import CategoriaForm, ProductoForm, TrabajadorForm
from django.views.generic import TemplateView

# Create your views here.

def index(request):
    trabajador_id = request.GET.get('trabajador')
    trabajadores = Trabajador.objects.all()

    if trabajador_id:
        asignaciones = AsignacionEpp.objects.filter(trabajador__rut=trabajador_id)
    else:
        asignaciones = AsignacionEpp.objects.all()

    devoluciones = DevolucionEpp.objects.all()

    return render(request, 'home/index.html', {
        'asignaciones': asignaciones,
        'devoluciones': devoluciones,
        'trabajadores': trabajadores,
        'trabajador_id': trabajador_id,
    })


def asignar_epp(request):
    if request.method == 'POST':
        form = AsignacionEppForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AsignacionEppForm()
    return render(request, 'home/asignar_epp.html', {'form': form})

def devolver_epp(request):
    if request.method == 'POST':
        form = DevolucionEppForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DevolucionEppForm()
    return render(request, 'home/devolver_epp.html', {'form': form})

def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoriaForm()
    return render(request, 'home/crear_categoria.html', {'form': form})

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductoForm()
    return render(request, 'home/crear_producto.html', {'form': form})

def crear_trabajador(request):
    if request.method == 'POST':
        form = TrabajadorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TrabajadorForm()
    return render(request, 'home/crear_trabajador.html', {'form': form})

def listado_productos(request):
    productos = Producto.objects.all()
    return render(request, 'home/lista_productos.html', {'productos': productos})

def eliminar_producto(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    return redirect('listado_productos')

def listado_trabajadores(request):
    trabajadores = Trabajador.objects.all()

    return render(request, 'home/listado_trabajadores.html', {'trabajadores': trabajadores})

def eliminar_trabajador(request, rut):
    trabajador = Trabajador.objects.get(rut=rut)
    trabajador.delete()
    return redirect('listado_trabajadores')

def listado_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'home/listado_categorias.html', {'categorias': categorias})
    
def eliminar_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.delete()
    return redirect('listado_categorias')


