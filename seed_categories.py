#!/usr/bin/env python3
"""
Este script requiere ejecutarse dentro de Django, o bien luego se convierte en un Django management command,
pero sirve como referencia para 'cargar categorías seed' en PupiStock.
"""

CATEGORIES = [
    "Lácteos",
    "Abarrotes",
    "Verduras y Frutas",
    "Carnes y Pescados",
    "Panificados",
    "Limpieza",
    "Bebidas",
    "Higiene Personal",
    "Mascotas",
]

# Cómo convertir esto en Django command:
# 1. Crear carpeta inventory/management/commands si no existe
# 2. Guardar como seed_categories.py
# 3. Usar el siguiente código:

DJANGO_COMMAND = '''
from django.core.management.base import BaseCommand
from inventory.models import Category

class Command(BaseCommand):
    help = 'Carga categorías seed típicas si no existen'

    def handle(self, *args, **kwargs):
        seeds = [
            "Lácteos",
            "Abarrotes",
            "Verduras y Frutas",
            "Carnes y Pescados",
            "Panificados",
            "Limpieza",
            "Bebidas",
            "Higiene Personal",
            "Mascotas",
        ]
        created, skipped = 0, 0
        for n in seeds:
            obj, was_created = Category.objects.get_or_create(name=n)
            if was_created:
                self.stdout.write(self.style.SUCCESS(f"Creada: {n}"))
                created += 1
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(f"Total creadas: {created}, ya existían: {skipped}"))
'''

print("Agrega esta lógica a inventory/management/commands/seed_categories.py según estructura de tu app.")