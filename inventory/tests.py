from django.test import TestCase
from .models import Category, Product

class CategoryTest(TestCase):
    def test_seed_category(self):
        Category.objects.create(name="Lácteos")
        self.assertEqual(Category.objects.count(), 1)

class ProductTest(TestCase):
    def test_create_product(self):
        c = Category.objects.create(name="Bebidas")
        Product.objects.create(name="Agua", category=c, quantity=12)
        self.assertEqual(Product.objects.first().category.name, "Bebidas")
