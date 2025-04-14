from django.shortcuts import render
from .models import AsignacionEpp, DevolucionEpp, Trabajador, Producto
from .forms import AsignacionEppForm, DevolucionEppForm
from .models import Categoria
from .forms import CategoriaForm, ProductoForm, TrabajadorForm
from django.views.generic import TemplateView
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import letter
from datetime import date
from django.conf import settings
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.lib.units import inch
from .forms import LogoForm
from .models import Configuracion


# Create your views here.

def index(request):
    trabajador_id = request.GET.get('trabajador')
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')

    trabajadores = Trabajador.objects.all()
    asignaciones = AsignacionEpp.objects.all()
    devoluciones = DevolucionEpp.objects.all()

    # Filtro por trabajador solo si el trabajador_id está presente
    if trabajador_id:
        asignaciones = asignaciones.filter(trabajador__rut=trabajador_id)
        devoluciones = devoluciones.filter(asignacion__trabajador__rut=trabajador_id)

    # Filtro por fechas solo si 'desde' o 'hasta' están presentes
    if fecha_desde:
        asignaciones = asignaciones.filter(fecha_asignacion__gte=fecha_desde)
        devoluciones = devoluciones.filter(fecha_devolucion__gte=fecha_desde)

    if fecha_hasta:
        asignaciones = asignaciones.filter(fecha_asignacion__lte=fecha_hasta)
        devoluciones = devoluciones.filter(fecha_devolucion__lte=fecha_hasta)

    return render(request, 'home/index.html', {
        'asignaciones': asignaciones,
        'devoluciones': devoluciones,
        'trabajadores': trabajadores,
        'trabajador_id': trabajador_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
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



def cambiar_logo(request):
    if request.method == 'POST':
        form = LogoForm(request.POST, request.FILES)
        if form.is_valid():
            # Guarda el nuevo logo (si no existe, crea un nuevo objeto de configuración)
            configuracion, created = Configuracion.objects.get_or_create(id=1)
            configuracion.logo = form.cleaned_data['logo']
            configuracion.save()
            return redirect('home')
    else:
        form = LogoForm()

    return render(request, 'cambiar_logo.html', {'form': form})


def generar_pdf_trabajador(request, rut):
    # Validación: ¿Trabajador existe?
    try:
        trabajador = Trabajador.objects.get(rut=rut)
    except Trabajador.DoesNotExist:
        messages.error(request, 'Debe seleccionar un trabajador antes de generar el informe.')
        return redirect('home')

    # Obtener la imagen del logo
    configuracion = Configuracion.objects.first()
    if configuracion and configuracion.logo:
        logo_path = configuracion.logo.path
    else:
        # Si no hay logo cargado, usar el logo por defecto
        logo_path = settings.BASE_DIR / 'static' / 'image' / 'orpak-logo.png'

    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')

    # Filtrar asignaciones por trabajador
    asignaciones = AsignacionEpp.objects.filter(trabajador=trabajador)

    if fecha_desde:
        asignaciones = asignaciones.filter(fecha_asignacion__gte=fecha_desde)
    if fecha_hasta:
        asignaciones = asignaciones.filter(fecha_asignacion__lte=fecha_hasta)

    # Generación del PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="informe_{trabajador.rut}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Usar la imagen del logo (si está disponible)
    p.drawImage(logo_path, inch, height - 0.9 * inch, width=1.5 * inch, height=0.8 * inch)

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - inch, "Entrega y/o Cambio de EPP")

    p.setFont("Helvetica", 12)
    p.drawString(inch, height - 1.5 * inch, f"Nombre: {trabajador.nombre} {trabajador.apellido}")
    p.drawString(inch, height - 1.8 * inch, f"RUT: {trabajador.rut}")
    p.drawString(inch, height - 2.1 * inch, f"Fecha: {date.today().strftime('%d-%m-%Y')}")

    y = height - 2.6 * inch
    p.setFont("Helvetica-Bold", 10)
    p.drawString(inch, y, "Fecha")
    p.drawString(2 * inch, y, "Producto")
    p.drawString(3.8 * inch, y, "Talla")
    p.drawString(4.6 * inch, y, "Cantidad")
    p.drawString(5.4 * inch, y, "Categoría")
    p.drawString(6.8 * inch, y, "Firma")

    y -= 15
    p.setFont("Helvetica", 10)

    for a in asignaciones:
        if y < inch:
            p.showPage()
            y = height - inch
            p.setFont("Helvetica", 10)

        p.drawString(inch, y, a.fecha_asignacion.strftime('%d-%m-%Y'))
        p.drawString(2 * inch, y, str(a.producto.nombre))
        p.drawString(3.8 * inch, y, str(a.producto.talla))
        p.drawString(4.6 * inch, y, str(a.cantidad))
        p.drawString(5.4 * inch, y, str(a.producto.categoria.nombre))
        p.drawString(6.8 * inch, y, "______________")
        y -= 15

    p.showPage()
    p.save()
    return response
def AsignacionLogo(request):
    if request.method == 'POST':
        form = LogoForm(request.POST, request.FILES)
        if form.is_valid():
            configuracion, created = Configuracion.objects.get_or_create(id=1)
            configuracion.logo = form.cleaned_data['logo']
            configuracion.save()
            return redirect('home')
    else:
        form = LogoForm()

    return render(request, 'home/cambiar_logo.html', {'form': form})


