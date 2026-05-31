import os
import csv
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pupistock.settings')
application = get_wsgi_application()

from inventory.models import Product, Category

def main():
    preload = os.environ.get('PRELOAD_IMPORT', 'False') == 'True'
    import_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'import')
    if not preload:
        print("[PRELOAD_IMPORT is not enabled] Exiting without importing.")
        return
    if not os.path.isdir(import_folder):
        print(f"[IMPORT ERROR] Folder '{import_folder}' not found.")
        return
    files = [f for f in os.listdir(import_folder) if f.lower().endswith('.csv')]
    if not files:
        print("[IMPORT WARNING] No CSV files found in import folder.")
        return
    for file in files:
        category_name = os.path.splitext(file)[0]
        try:
            category = Category.objects.filter(name__iexact=category_name).first()
        except Exception as e:
            category = None
        with open(os.path.join(import_folder, file), 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            add_count = 0
            for row in reader:
                name = row.get('Producto')
                quantity = row.get('Cantidad', 0)
                if name is None:
                    print(f"  [SKIP] Row without 'Producto' field in {file}: {row}")
                    continue
                existing = Product.objects.filter(name=name, category=category).first()
                if existing:
                    print(f"  [SKIP] Product '{name}' in category '{category_name}' already exists.")
                    continue
                try:
                    p = Product.objects.create(
                        name=name,
                        quantity=quantity or 0,
                        category=category,
                    )
                    print(f"  [OK] Producto '{name}' importado en categoría '{category_name if category else '---'}'.")
                    add_count += 1
                except Exception as e:
                    print(f"  [ERR] Al crear producto '{name}': {e}")
            print(f"[INFO] {add_count} productos importados de '{file}'")
    print("[IMPORT DONE]")

if __name__ == "__main__":
    main()
