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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.conf import settings
from .models import Trabajador, AsignacionEpp, Configuracion
from django.contrib import messages
from datetime import date
from reportlab.lib.units import inch


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
    # Validación del trabajador
    try:
        trabajador = Trabajador.objects.get(rut=rut)
    except Trabajador.DoesNotExist:
        messages.error(request, 'Debe seleccionar un trabajador antes de generar el informe.')
        return redirect('home')

    # Ruta del logo
    configuracion = Configuracion.objects.first()
    logo_path = configuracion.logo.path if configuracion and configuracion.logo else settings.BASE_DIR / 'static' / 'image' / 'orpak-logo.png'

    # Fechas
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')

    # Filtrar asignaciones
    asignaciones = AsignacionEpp.objects.filter(trabajador=trabajador)
    if fecha_desde:
        asignaciones = asignaciones.filter(fecha_asignacion__gte=fecha_desde)
    if fecha_hasta:
        asignaciones = asignaciones.filter(fecha_asignacion__lte=fecha_hasta)

    # Preparar respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="informe_{trabajador.rut}.pdf"'

    # Documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    # Encabezado: Logo + Título en una fila
    logo = Image(str(logo_path), width=80, height=40)
    titulo = Paragraph("<b>REGISTRO ENTREGA Y/O CAMBIO DE EPP</b>", styles['Title'])

    encabezado = Table([[logo, titulo]], colWidths=[100, 400])
    encabezado.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(encabezado)
    elements.append(Spacer(1, 12))

    # Datos del trabajador
    elements.append(Paragraph(f"<b>NOMBRE:</b> {trabajador.nombre} {trabajador.apellido}", styles['Normal']))
    elements.append(Paragraph(f"<b>RUT:</b> {trabajador.rut}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Encabezados de tabla
    data = [
        ["CANTIDAD", "ELEMENTO ENTREGADO", "MARCA", "MODELO", "FECHA ENTREGA", "FIRMA"]
    ]

    # Llenado de la tabla
    for asignacion in asignaciones:
        producto = asignacion.producto
        data.append([
            str(asignacion.cantidad),
            producto.nombre,
            getattr(producto, 'marca', ''),  # En caso de que no tenga marca o modelo definidos
            getattr(producto, 'modelo', ''),
            asignacion.fecha_asignacion.strftime('%d-%m-%Y'),
            " " * 20  # Espacio para firma
        ])

    # Tabla de entregas
    table = Table(data, colWidths=[1*inch, 2*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)

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


