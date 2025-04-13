# Modelos Django para asignación de EPP con control de stock

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    TALLAS = [
        ("N/A", "N/A"), ("XS", "XS"), ("S", "S"), ("M", "M"), ("L", "L"), ("XL", "XL"), ("XXL", "XXL"),
        ("32", "32"), ("34", "34"), ("36", "36"), ("38", "38"), ("40", "40"), ("42", "42"), ("44", "44"),
        ("46", "46"), ("48", "48"), ("50", "50"), ("52", "52"), ("54", "54"), ("56", "56"), ("58", "58"),
    ]

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    stock = models.IntegerField()
    talla = models.CharField(max_length=4, choices=TALLAS, default="N/A")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - Talla {self.talla}"

class Trabajador(models.Model):
    rut = models.CharField(max_length=256, primary_key=True)
    nombre = models.CharField(max_length=256)
    apellido = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class AsignacionEpp(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_asignacion = models.DateField(default=timezone.now)

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")

        # Si es una nueva asignación
        if not self.pk and self.producto.stock < self.cantidad:
            raise ValidationError(f"No hay suficiente stock disponible. Stock actual: {self.producto.stock}")

        # Si es una edición y aumentó la cantidad
        elif self.pk:
            original = AsignacionEpp.objects.get(pk=self.pk)
            diferencia = self.cantidad - original.cantidad
            if diferencia > self.producto.stock:
                raise ValidationError(f"No hay suficiente stock para aumentar la cantidad. Stock actual: {self.producto.stock}")

    def save(self, *args, **kwargs):
        self.clean()  # Ejecuta validaciones

        with transaction.atomic():
            if self.pk:
                # Estamos actualizando
                original = AsignacionEpp.objects.get(pk=self.pk)
                diferencia = self.cantidad - original.cantidad
                self.producto.stock -= diferencia
            else:
                # Es una nueva asignación
                self.producto.stock -= self.cantidad

            if self.producto.stock < 0:
                raise ValidationError("Stock insuficiente para realizar la asignación.")

            self.producto.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} de {self.producto} a {self.trabajador}"

class DevolucionEpp(models.Model):
    asignacion = models.ForeignKey(AsignacionEpp, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_devolucion = models.DateField(default=timezone.now)

    def clean(self):
        # Sumar todas las devoluciones previas para esta asignación
        devoluciones_previas = DevolucionEpp.objects.filter(asignacion=self.asignacion)
        if self.pk:
            # Si es actualización, excluir la instancia actual
            devoluciones_previas = devoluciones_previas.exclude(pk=self.pk)
        total_devueltas = sum(d.cantidad for d in devoluciones_previas)
        if total_devueltas + self.cantidad > self.asignacion.cantidad:
            raise ValidationError("La suma de devoluciones excede la cantidad asignada.")

    def save(self, *args, **kwargs):
        # Guardamos el valor anterior para calcular la diferencia en caso de actualización
        diferencia = self.cantidad
        if self.pk:
            # Recuperamos la instancia original
            orig = DevolucionEpp.objects.get(pk=self.pk)
            diferencia = self.cantidad - orig.cantidad

        # Ejecutamos la validación
        self.clean()

        with transaction.atomic():
            # Actualizamos el stock solo con la diferencia
            if diferencia:
                self.asignacion.producto.stock += diferencia
                self.asignacion.producto.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Devolución de {self.cantidad} de {self.asignacion.producto}"