# Documentación de Mantenimiento — PupiStock (DJCSK)

> **Objetivo:** Guía completa para que un desarrollador junior pueda entender, mantener y extender este proyecto sin depender de conocimiento previo.

---

## 1. ¿Qué es este proyecto?

**PupiStock** es un sistema de gestión de inventario familiar/micro-negocio. Funciona 100% vía web, optimizado para celular (mobile-first), con diseño "cálido minimalista". Permite registrar **categorías**, **productos** y **compras**, con una lista de compras automática cuando un producto se queda sin stock.

- **Nombre del repo:** DJCSK
- **Nombre del proyecto:** PupiStock
- **Nombre en PRD:** "Sahara Inventory Management"
- **Stack:** Django 4.2 + PostgreSQL 15 + Tailwind CSS 3.4 (CDN) + Docker

---

## 2. Estructura de directorios

```
DJCSK/
├── .env.example              # Plantilla de variables de entorno
├── Dockerfile                 # Build multi-etapa (Node + Python)
├── docker-compose.yml         # 3 servicios: db, web, ngrok
├── manage.py                  # Script de gestión Django
├── requirements.txt           # Dependencias Python
├── package.json               # Dependencias Node (solo Tailwind build)
├── tailwind.config.js         # Configuración de Tailwind
├── postcss.config.js          # Configuración de PostCSS
├── import_products.py         # Script de importación CSV de productos
├── seed_categories.py         # Referencia de seed (no ejecutable)
├── wait-for-it.sh             # Script para esperar servicios TCP
├── wait_for_ngrok_url.sh      # Script para obtener URL pública de ngrok
├── print_ngrok_url.sh         # Script para imprimir URL de ngrok
├── README.md                  # Guía rápida (Ngrok-focused)
├── README-PRO.md              # Guía profesional (build/test/seed)
├── stock_project_prd.md       # Documento de requisitos (PRD)
│
├── pupistock/                 # Paquete Django del proyecto
│   ├── settings.py            # Configuración central
│   ├── urls.py                # Rutas raíz
│   ├── wsgi.py                # Entrada WSGI (producción)
│   └── asgi.py                # Entrada ASGI (no usado)
│
├── inventory/                 # App Django principal
│   ├── models.py              # Modelos: Category, Product, Purchase
│   ├── views.py               # Vistas CBV (CRUD + login + dashboard)
│   ├── apiviews.py            # API REST (ViewSets DRF)
│   ├── serializers.py         # Serializadores DRF
│   ├── apiurls.py             # Rutas de la API (router DRF)
│   ├── admin.py               # Configuración del admin de Django
│   ├── tests.py               # Tests unitarios (2 casos)
│   ├── apps.py                # Configuración de la app
│   ├── migrations/            # Migraciones de base de datos
│   │   └── 0001_initial.py    # Migración inicial (3 modelos)
│   ├── management/
│   │   └── commands/
│   │       └── seed_categories.py  # Comando Django: carga categorías semilla
│   └── templates/             # Templates HTML de la app
│       ├── base.html          # Layout base (sidebar, header, estilos)
│       ├── dashboard.html     # Página de bienvenida
│       ├── product_list.html  # Listado de productos
│       ├── product_form.html  # Formulario crear/editar producto
│       ├── purchase_list.html # Listado de compras
│       ├── purchase_form.html # Formulario crear/editar compra
│       ├── category_list.html # Listado de categorías
│       └── category_form.html # Formulario crear/editar categoría
│
├── templates/                 # Templates a nivel proyecto
│   └── registration/
│       └── login.html         # Página de login
│
├── vistas/                    # Prototipos HTML estáticos (mockups de diseño)
│   ├── login.html
│   ├── list-product.html
│   └── list-buy.html
│
├── import/                    # Datos CSV para importación
│   ├── Almacen.csv            # 80 productos de almacén
│   ├── Condimentos.csv        # 36 condimentos/especias
│   └── Limpieza.csv           # 30 productos de limpieza
│
├── static/                    # Archivos estáticos custom (vacío)
├── staticfiles/               # Archivos recolectados (collectstatic)
└── doc/                       # Documentación del proyecto
    ├── doc-proyect.md         # Este archivo
    └── backlog.md             # Issues y pendientes
```

---

## 3. Cómo arrancar el proyecto

### 3.1 Con Docker (recomendado)

```bash
# 1. Clonar
git clone https://github.com/DIOLINK/djcsk.git
cd DJCSK

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores (ver sección 7)

# 3. Levantar todo
docker compose up --build

# 4. Acceder en http://localhost:8000
```

Al levantar, Docker Compose ejecuta automáticamente:
1. Espera a que PostgreSQL esté listo
2. Ejecuta migraciones (`python manage.py migrate`)
3. Recolecta archivos estáticos (`python manage.py collectstatic --noinput`)
4. Importa productos desde CSV (si `PRELOAD_IMPORT=True`)
5. Crea superusuario (desde variables de entorno)
6. Inicia Gunicorn en puerto 8000

### 3.2 Sin Docker (desarrollo local)

```bash
# Requisitos: Python 3.12, PostgreSQL 15, Node 20+

# 1. Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Node (solo si quieres compilar Tailwind localmente)
npm install

# 3. Configurar .env con DB_HOST=localhost

# 4. Migraciones y datos
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser

# 5. Correr
python manage.py runserver
```

---

## 4. Arranque en detalle (Docker)

### Servicios definidos en `docker-compose.yml`

| Servicio | Imagen | Puerto | Descripción |
|---|---|---|---|
| `db` | `postgres:15-alpine` | 5432 | Base de datos PostgreSQL |
| `web` | Build local | 8000 | Django + Gunicorn |
| `ngrok` | `ngrok/ngrok:latest` | 4040 | Túnel público para demos |

### Comandos útiles con Docker

```bash
# Ver logs
docker compose logs -f web

# Ejecutar un comando dentro del contenedor web
docker compose run web python manage.py seed_categories
docker compose run web python manage.py test
docker compose run web python manage.py createsuperuser

# Bajar todo
docker compose down

# Bajar y borrar datos de la BD
docker compose down -v

# Reconstruir imagen sin cache
docker compose build --no-cache
```

### URL pública con Ngrok

```bash
# Obtener la URL
./wait_for_ngrok_url.sh
# o
docker compose logs ngrok

# La URL cambia en cada reinicio de ngrok.
# Para evitar errores CSRF usa en .env:
# CSRF_TRUSTED_ORIGINS=https://*.ngrok-free.dev
```

---

## 5. Modelos de datos (base de datos)

### 5.1 Diagrama de relaciones

```
Category (Categoría)
  ├── id: BigAuto (PK)
  └── name: Char(100) único

Product (Producto)
  ├── id: BigAuto (PK)
  ├── name: Char(100)
  ├── category: FK → Category (SET_NULL)
  ├── unit: Char(32) default="Unidad"
  ├── quantity: Integer default=0
  ├── min_stock: Integer default=1
  ├── price: Decimal(8,2) default=0
  ├── active: Boolean default=True
  └── ordering: ['name'] (alfabético)

Purchase (Compra)
  ├── id: BigAuto (PK)
  ├── product: FK → Product (CASCADE)
  ├── user: FK → User (PROTECT)
  ├── date: Date (auto_now_add)
  ├── quantity: PositiveInteger
  ├── price: Decimal(8,2)
  └── store: Char(100) null/blank
```

### 5.2 Comportamiento de FK

- **Product → Category:** Si se borra una categoría, el producto queda con `category=NULL`.
- **Purchase → Product:** Si se borra un producto, se borran **todas** sus compras asociadas (CASCADE).
- **Purchase → User:** No se puede borrar un usuario que tenga compras (PROTECT).

### 5.3 Migraciones

Hay una sola migración (`0001_initial.py`) que crea las 3 tablas. Para crear nuevas migraciones:

```bash
docker compose run web python manage.py makemigrations
docker compose run web python manage.py migrate
```

---

## 6. URLs del sistema

### 6.1 Rutas web (frontend)

| URL | Vista | Nombre | Requiere login |
|---|---|---|---|
| `/` | DashboardView | `dashboard` | Sí |
| `/accounts/login/` | CustomLoginView | `login` | No |
| `/accounts/logout/` | CustomLogoutView | `logout` | No |
| `/categorias/` | CategoryListView | `category_list` | Sí |
| `/categorias/nueva/` | CategoryCreateView | `category_create` | Sí |
| `/categorias/<id>/editar/` | CategoryUpdateView | `category_update` | Sí |
| `/productos/` | ProductListView | `product_list` | Sí |
| `/productos/nuevo/` | ProductCreateView | `product_create` | Sí |
| `/productos/<id>/editar/` | ProductUpdateView | `product_update` | Sí |
| `/compras/` | PurchaseListView | `purchase_list` | Sí |
| `/compras/nueva/` | PurchaseCreateView | `purchase_create` | Sí |
| `/compras/<id>/editar/` | PurchaseUpdateView | `purchase_update` | Sí |
| `/admin/` | Django Admin | — | Staff |

### 6.2 API REST

Base: `/api/v1/`

| Método | Endpoint | Descripción | Autenticación |
|---|---|---|---|
| GET | `/categories/` | Listar categorías | Token/Sesión |
| POST | `/categories/` | Crear categoría | Token/Sesión |
| GET/PUT/DELETE | `/categories/{id}/` | CRUD categoría | Token/Sesión |
| GET | `/products/` | Listar productos | Token/Sesión |
| POST | `/products/` | Crear producto | Token/Sesión |
| GET/PUT/DELETE | `/products/{id}/` | CRUD producto | Token/Sesión |
| GET | `/purchases/` | Listar compras | Token/Sesión |
| POST | `/purchases/` | Crear compra | Token/Sesión |
| GET/PUT/DELETE | `/purchases/{id}/` | CRUD compra | Token/Sesión |

Archivos relevantes:
- `inventory/apiviews.py:6-19` — ViewSets
- `inventory/apiurls.py:4-9` — Router DRF
- `pupistock/urls.py:21` — Inclusión en rutas raíz

---

## 7. Variables de entorno (`.env`)

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `DEBUG` | Modo debug (1=on, 0=off) | `0` |
| `SECRET_KEY` | Clave secreta Django | — |
| `DB_NAME` | Nombre BD | `pupistock` |
| `DB_USER` | Usuario BD | `pupistock` |
| `DB_PASSWORD` | Contraseña BD | `pupipass` |
| `DB_HOST` | Host BD | `db` (en Docker) |
| `DB_PORT` | Puerto BD | `5432` |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF (separados por coma) | — |
| `LANGUAGE_CODE` | Idioma (`es`/`en`) | `es` |
| `SU_USERNAME` | Usuario admin automático | — |
| `SU_EMAIL` | Email admin automático | — |
| `SU_PASSWORD` | Contraseña admin automático | — |
| `PRELOAD_IMPORT` | Importar CSV al iniciar | `True` |
| `NGROK_AUTHTOKEN` | Token de ngrok | — |

---

## 8. Flujo de la aplicación

### 8.1 Arranque (Docker)

```
docker compose up
  → db (PostgreSQL) inicia
  → web espera a db con wait-for-it.sh
  → python manage.py migrate        (crea/actualiza tablas)
  → python manage.py collectstatic   (recolecta estáticos)
  → python import_products.py        (carga CSV si PRELOAD_IMPORT=True)
  → python manage.py createsuperuser (crea admin si no existe)
  → gunicorn pupistock.wsgi          (inicia servidor HTTP)
  → ngrok expone web:8000 públicamente
```

### 8.2 Login

1. Usuario accede a cualquier URL → `LoginRequiredMixin` redirige a `/accounts/login/`
2. `CustomLoginView` renderiza `templates/registration/login.html`
3. Django autentica usuario/password contra la tabla `auth_user`
4. Al autenticar, redirige a `/` (dashboard)
5. `DashboardView` renderiza `inventory/templates/dashboard.html`

### 8.3 Flujo de productos

1. Usuario accede a `/productos/` → `ProductListView`
2. Productos se muestran en **orden alfabético** (por `name`)
3. Filtros por nombre, categoría, stock mínimo/máximo con botón **×** para limpiar cada campo
4. Precios se muestran en formato **ARS** (`$ 1.250,00`) usando el filtro `|ars`
5. Botón "Nuevo Producto" → `/productos/nuevo/` → `ProductCreateView`
6. Al guardar, muestra **toast de éxito** y redirige a lista de productos
7. Botón "Editar" → `/productos/<id>/editar/` → `ProductUpdateView`
8. El input de precio al recibir foco selecciona todo el contenido automáticamente
9. Si se accede desde compras con `?next=/compras/`, al guardar redirige de vuelta a compras

### 8.4 Flujo de compras

La lista de compras muestra productos con stock agotado (`quantity <= 0`):

1. Usuario accede a `/compras/` → `PurchaseListView`
2. El `get_queryset()` filtra productos con `quantity__lte=0`
3. Filtros por nombre y categoría, con botón **×** para limpiar
4. Botón **Reponer** → redirige a editar producto con `?next=/compras/`
5. Al guardar la edición, vuelve automáticamente a `/compras/` para seguir reponiendo
6. Si la búsqueda no encuentra resultados, **verifica si el producto existe con stock**:
   - Si existe: muestra lista de coincidencias con link "Ir al producto"
   - Si no existe: muestra botón "+ Agregar producto" que redirige a crear producto y vuelve a compras

> **Importante:** La vista ya no crea compras automáticamente en GET. La lista refleja directamente productos con `quantity <= 0`.

### 8.5 CRUD de categorías

Similar al flujo de productos pero más simple:
- `/categorias/` → lista
- `/categorias/nueva/` → crear
- `/categorias/<id>/editar/` → editar

---

## 9. Sistema de diseño (CSS / Tailwind)

### 9.1 Cómo se cargan los estilos

El proyecto **no usa Tailwind compilado**. En su lugar, carga Tailwind vía CDN en `base.html:22`:

```html
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
```

La configuración de la paleta de colores y tipografía se define en un `<script>` inline (`base.html:23-95`). Los estilos adicionales están en un bloque `<style>` (`base.html:96-207`).

### 9.2 Paleta de colores principal

| Nombre | Hex | Uso |
|---|---|---|
| Primary | `#c2652a` | Botones, acentos, título |
| Background | `#faf5ee` | Fondo general |
| Surface | `#faf5ee` | Superficie de tarjetas |
| On-surface | `#3a302a` | Texto principal |
| Error | `#c0392b` | Errores |

### 9.3 Tipografía

- **Headings:** EB Garamond (serif)
- **Body:** Manrope (sans-serif)
- **Íconos:** Material Symbols (Google Fonts CDN)

### 9.4 Layout

- **Sidebar:** Fixed a la izquierda (260px), con drawer en móvil
- **Header:** Sticky top con botón hamburguesa en móvil
- **Contenido:** `ml-64` en desktop, ocupa todo el ancho en móvil
- **Footer:** "PupiStock Systems © 2026"

La sidebar usa CSS transitions para abrir/cerrar en móvil (clase `drawer-open` y `scrim-active`).

---

## 10. Sistema de notificaciones (Toast)

### 10.1 Toast flotantes

Las notificaciones al usuario se muestran como toasts flotantes en la esquina superior derecha:

- **Posición:** `fixed` top-right, no empuja el contenido
- **Animación:** slide-in desde la derecha al aparecer, fade-out + slide-out al desaparecer
- **Duración:** 2 segundos, luego auto-dismiss
- **Cierre manual:** botón **×** (ícono `close`) en cada toast
- **Tipos:** `success` (verde), `error` (rojo), `info` (azul)
- **Móvil:** ancho al 85% de la pantalla, texto con wrap automático

### 10.2 Disparar toasts desde el backend

Usar el sistema de mensajes de Django:

```python
from django.contrib import messages

messages.success(request, 'Producto creado correctamente.')
messages.error(request, 'No se puede eliminar la categoría.')
```

Todas las vistas CRUD (`CreateView` y `UpdateView`) ya disparan toast de éxito.

### 10.3 Disparar toasts desde JavaScript

Función global disponible en todas las páginas:

```javascript
showToast('Error al guardar', 'error');
showToast('Operación exitosa', 'success');
showToast('Información', 'info');
```

### 10.4 Filtro de precios (`|ars`)

Template filter en `inventory/templatetags/price_filters.py`:

```django
{% load price_filters %}
{{ producto.price|ars }}
```

Formato peso argentino: `$ 1.250,00` (punto para miles, coma para decimales).

---
## 11. APIs y cómo extenderlas

Si necesitas agregar un endpoint nuevo:

1. Define el modelo en `inventory/models.py`
2. Crea migración: `python manage.py makemigrations`
3. Crea serializador en `inventory/serializers.py`
4. Crea ViewSet en `inventory/apiviews.py`
5. Registra en el router en `inventory/apiurls.py`

Ejemplo para un modelo nuevo `Supplier`:

```python
# serializers.py
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

# apiviews.py
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

# apiurls.py
router.register(r'suppliers', SupplierViewSet)
```

---

## 12. Cómo crear una nueva página web

1. Crea el template HTML en `inventory/templates/`
2. Extiende `base.html`: `{% extends "base.html" %}`
3. Crea la vista en `inventory/views.py` (usar `LoginRequiredMixin`)
4. Agrega la ruta en `pupistock/urls.py`
5. Opcional: agrega el enlace en la sidebar de `base.html`

---

## 13. Tests

### Ejecutar tests

```bash
# Docker
docker compose run web python manage.py test

# Local
python manage.py test
```

### Tests existentes

Archivo: `inventory/tests.py`

1. `CategoryTest.test_seed_category` — Verifica que se puede crear una categoría
2. `ProductTest.test_create_product` — Verifica que se puede crear un producto con categoría

### Cómo agregar tests

Usa `django.test.TestCase`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Category, Product, Purchase

class PurchaseTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('test', password='pass')
        self.cat = Category.objects.create(name="Test")
        self.prod = Product.objects.create(name="Test P", category=self.cat, quantity=5)

    def test_create_purchase(self):
        p = Purchase.objects.create(
            product=self.prod, user=self.user, quantity=2, price=10.50
        )
        self.assertEqual(p.price, 10.50)
```

---

## 14. Seed data (datos iniciales)

### Categorías semilla

```bash
docker compose run web python manage.py seed_categories
```

Crea 9 categorías si no existen: Lácteos, Abarrotes, Verduras y Frutas, Carnes y Pescados, Panificados, Limpieza, Bebidas, Higiene Personal, Mascotas.

### Productos desde CSV

Los archivos en `import/` se cargan automáticamente al arrancar si `PRELOAD_IMPORT=True`. El script `import_products.py`:
- Lee cada CSV en `import/`
- El nombre del archivo (sin extensión) se usa como nombre de categoría
- Si la categoría ya existe, asocia los productos a ella
- Si un producto ya existe (mismo nombre + misma categoría), lo salta

---

## 15. Configuración de Django (settings.py)

Archivo: `pupistock/settings.py`

### Puntos clave

- **Base de datos:** PostgreSQL configurado vía variables de entorno
- **DEBUG:** Controlado por `DEBUG` en `.env`
- **ALLOWED_HOSTS:** Leído de `DJANGO_ALLOWED_HOSTS` (separado por coma)
- **CSRF_TRUSTED_ORIGINS:** Leído de `CSRF_TRUSTED_ORIGINS` (separado por coma)
- **Idioma:** `LANGUAGE_CODE` en `.env` (por defecto `es`)
- **Estáticos:** WhiteNoise para servir en producción (sin nginx)
- **Media:** Configurado pero no usado actualmente
- **LOGIN_REDIRECT_URL:** `/` (dashboard)

### Middleware instalado

1. `SecurityMiddleware`
2. `WhiteNoiseMiddleware` (insertado manualmente en posición 1)
3. `SessionMiddleware`
4. `CommonMiddleware`
5. `CsrfViewMiddleware`
6. `AuthenticationMiddleware`
7. `MessageMiddleware`
8. `XFrameOptionsMiddleware`

---

## 16. Dockerfile (multi-etapa)

El Dockerfile tiene 3 etapas:

1. **base** — Python 3.12 slim
2. **nodebuild** — Node 20 slim, compila Tailwind CSS
3. **final** — Imagen final con Python + Gunicorn

**Atención:** La etapa `nodebuild` copia `./pupistock/static_src` y espera un archivo `input.css` que **no existe** en el repositorio. Esto no rompe el build porque la etapa final no copia el output de nodebuild, pero sí falla el paso de `npm ci` y `npx tailwindcss`. Ver `backlog.md`.

---

## 17. Dependencias

### Python (`requirements.txt`)

| Paquete | Propósito |
|---|---|
| `Django>=4.2,<5` | Framework web |
| `psycopg2-binary` | Conector PostgreSQL |
| `django-environ` | Variables de entorno |
| `djangorestframework` | API REST |
| `gunicorn` | Servidor WSGI (producción) |
| `whitenoise` | Servir estáticos (producción) |

### Node (`package.json`)

| Paquete | Propósito |
|---|---|
| `tailwindcss ^3.4.0` | Framework CSS |
| `postcss ^8.4.24` | Post-procesador CSS |
| `autoprefixer ^10.4.13` | Prefijos de navegador |

---

## 18. Preguntas frecuentes

### Q: ¿Por qué no se ven mis cambios de CSS?

Los estilos se cargan vía CDN en `base.html`. Cualquier estilo custom va en el bloque `<style>` de `base.html`. Si necesitas Tailwind compilado localmente, crea el archivo `static_src/input.css` (ver `backlog.md`).

### Q: No puedo iniciar sesión

¿Creaste el superusuario? En Docker, el `.env` debe tener `SU_USERNAME` y `SU_PASSWORD`. Si ya existe, el `createsuperuser --noinput` falla silenciosamente (`|| true`). Usa `docker compose run web python manage.py createsuperuser` manualmente.

### Q: Error "DisallowedHost" o CSRF

Actualiza `DJANGO_ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` en `.env` con la URL actual de ngrok.

### Q: La lista de compras está vacía

La lista de compras solo muestra productos con `quantity=0`. Si todos los productos tienen stock > 0, la lista estará vacía.

### Q: Error "relation does not exist" al arrancar

Las migraciones no se ejecutaron. Corre `python manage.py migrate`.

---

## 19. Contacto y referencias

- **Repo:** `https://github.com/DIOLINK/djcsk`
- **Documentación adicional:** `doc/backlog.md` (issues conocidos y pendientes)
- **PRD:** `stock_project_prd.md` (requisitos y diseño)
- **README rápido:** `README.md` (despliegue con Ngrok)
- **README profesional:** `README-PRO.md` (build, test, seed)
- **Prototipos:** `vistas/` (mockups HTML estáticos)

---

*Documentación generada para mantenimiento del proyecto. Última actualización: junio 2026.*
