import csv
import os
from django.core.management.base import BaseCommand
from inventory.models import Product, Category


class Command(BaseCommand):
    help = 'Importa productos desde archivos CSV en la carpeta import/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Actualiza productos existentes en vez de saltarlos',
        )

    def handle(self, *args, **options):
        force = options['force']
        import_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'import'
        )

        if not os.path.isdir(import_folder):
            self.stderr.write(self.style.ERROR(
                f"Carpeta '{import_folder}' no encontrada."
            ))
            return

        files = [f for f in os.listdir(import_folder) if f.lower().endswith('.csv')]
        if not files:
            self.stdout.write(self.style.WARNING(
                "No se encontraron archivos CSV en la carpeta import/."
            ))
            return

        for file in sorted(files):
            category_name = os.path.splitext(file)[0]
            category = Category.objects.filter(name__iexact=category_name).first()

            filepath = os.path.join(import_folder, file)
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                created, skipped, updated, errors = 0, 0, 0, 0
                for row in reader:
                    name = row.get('Producto')
                    if not name:
                        self.stderr.write(
                            f"  [SKIP] Fila sin 'Producto' en {file}: {row}"
                        )
                        skipped += 1
                        continue

                    quantity = self._parse_int(row.get('Cantidad', 0))
                    price = self._parse_decimal(row.get('Precio', 0))

                    existing = Product.objects.filter(
                        name=name, category=category
                    ).first()

                    if existing:
                        if force:
                            existing.quantity = quantity
                            existing.price = price
                            existing.save()
                            self.stdout.write(
                                f"  [UPD] '{name}' actualizado en '{category_name}'."
                            )
                            updated += 1
                        else:
                            self.stdout.write(
                                f"  [SKIP] '{name}' ya existe en '{category_name}'."
                            )
                            skipped += 1
                        continue

                    try:
                        Product.objects.create(
                            name=name,
                            quantity=quantity,
                            price=price,
                            category=category,
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  [OK] '{name}' importado en '{category_name}'."
                            )
                        )
                        created += 1
                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(
                                f"  [ERR] '{name}': {e}"
                            )
                        )
                        errors += 1

                    self.stdout.write(
                        f"[{file}] OK={created} SKIP={skipped} UPD={updated} ERR={errors}"
                    )

        self.stdout.write(self.style.SUCCESS("[IMPORT DONE]"))

    def _parse_int(self, value):
        try:
            return int(str(value).strip()) if str(value).strip() else 0
        except (ValueError, TypeError):
            return 0

    def _parse_decimal(self, value):
        try:
            return float(str(value).strip()) if str(value).strip() else 0
        except (ValueError, TypeError):
            return 0
