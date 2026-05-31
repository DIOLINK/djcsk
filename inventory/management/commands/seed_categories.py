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
