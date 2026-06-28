from django.db import models
from django.contrib.auth import get_user_model

class Category(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField("Nombre", max_length=100)
    category = models.ForeignKey(Category, verbose_name="Categoría", on_delete=models.SET_NULL, null=True, related_name="products")
    unit = models.CharField("Unidad", max_length=32, default="Unidad")
    quantity = models.IntegerField("Cantidad", default=0)
    min_stock = models.IntegerField("Stock mínimo", default=1)
    price = models.DecimalField("Precio", max_digits=8, decimal_places=2, default=0)
    active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Purchase(models.Model):
    product = models.ForeignKey(Product, verbose_name="Producto", on_delete=models.CASCADE, related_name="purchases")
    user = models.ForeignKey(get_user_model(), verbose_name="Usuario", on_delete=models.PROTECT, related_name="purchases")
    date = models.DateField("Fecha", auto_now_add=True)
    quantity = models.PositiveIntegerField("Cantidad")
    price = models.DecimalField("Precio", max_digits=8, decimal_places=2)
    store = models.CharField("Tienda", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.product} ({self.quantity}) @ {self.price}"