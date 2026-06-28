# Backlog — PupiStock (DJCSK)

> **Objetivo:** Issues conocidos, cosas que no se entienden o faltan por desarrollar. Usar como referencia antes de hacer cambios en el proyecto.

---

## 1. Issues encontrados en el código

### 1.1 Dockerfile: etapa `nodebuild` es innecesaria (CDN decidido)

**Archivo:** `Dockerfile:10-11`  
**Severidad:** Media

La etapa `nodebuild` del Dockerfile copia `./pupistock/static_src` y ejecuta:

```
COPY ./pupistock/static_src ./static_src
RUN npx tailwindcss -c tailwind.config.js -i ./static_src/input.css -o ./static/css/tailwind.css --minify
```

El directorio `pupistock/static_src` y el archivo `input.css` **no existen**. Además, la etapa `final` del Dockerfile **no copia** el output de `nodebuild`, así que el CSS compilado nunca llega a la imagen final.

**Decisión:** Tailwind se usará solo vía CDN (ver Q5 en §3). La etapa `nodebuild` no tiene razón de existir.

**Solución sugerida:** Eliminar la etapa `nodebuild` completa del Dockerfile.

### 1.2 npm script `build:css` es innecesario (CDN decidido)

**Archivo:** `package.json`  
**Severidad:** Baja

El script `build:css` y las dependencias de Tailwind en `package.json` existen para compilar CSS localmente, pero la decisión es usar Tailwind solo vía CDN (ver Q5 en §3).

**Solución sugerida:** Eliminar el script `build:css` y las dependencias `tailwindcss` del `package.json`. Si no quedan otras dependencias npm, eliminar también `package.json` y `package-lock.json`.

### 1.3 CSRF_TRUSTED_ORIGINS usa `os.environ` en lugar de `django-environ`

**Archivo:** `pupistock/settings.py:176-178`  
**Severidad:** Baja (inconsistencia de estilo)

Todas las variables de entorno se leen usando `django-environ` (`env(...)`), excepto `CSRF_TRUSTED_ORIGINS` que usa `os.environ.get(...)` directamente:

```python
# Línea 176-178
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]
```

**Solución sugerida:** Declarar `CSRF_TRUSTED_ORIGINS` en la sección `env = environ.Env(...)` y leerla con `env('CSRF_TRUSTED_ORIGINS')`.

### 1.4 Archivo `seed_categories.py` en raíz es redundante

**Archivo:** `seed_categories.py` (raíz)  
**Severidad:** Baja (confusión)

Existe un archivo `seed_categories.py` en la raíz que es una **referencia/documentación** de cómo crear el comando de Django. El comando real está en `inventory/management/commands/seed_categories.py`. Tener ambos puede confundir.

**Solución sugerida:** Eliminar `seed_categories.py` de la raíz o renombrarlo a `seed_categories_reference.py` para indicar claramente que no es ejecutable.

### 1.5 ~~PurchaseListView crea compras en GET~~ ✅ RESUELTO

La vista `PurchaseListView` ya no crea compras automáticamente. Ahora solo muestra productos con `quantity <= 0` directamente desde el modelo `Product`. La lógica de creación automática fue eliminada.

### 1.6 No hay `LOGIN_URL` configurado explícitamente

**Archivo:** `pupistock/settings.py`  
**Severidad:** Baja

`settings.py` no define `LOGIN_URL`. Django usa por defecto `/accounts/login/` lo cual coincide con la ruta configurada, pero es frágil. Si alguien cambia la ruta de login, `LoginRequiredMixin` dejará de redirigir correctamente.

**Solución sugerida:** Agregar `LOGIN_URL = 'login'` en `settings.py`.

### 1.7 ~~SECRET_KEY hardcodeada con valor inseguro~~ ✅ RESUELTO

El `SECRET_KEY` ahora es `None` por defecto (línea 27) y se lee de `.env` vía `env('SECRET_KEY')` (línea 99). Si `.env` no está configurado, Django fallará al iniciar, lo cual es seguro.

### 1.8 ~~`DEBUG = True` hardcodeado~~ ✅ RESUELTO

`DEBUG` ahora es `False` por defecto (línea 28) y se lee de `.env` vía `env('DEBUG')` (línea 100). El default seguro evita fugas de información en producción.

### 1.9 README.md tiene URL de ngrok hardcodeada y rota

**Archivo:** `README.md:1`  
**Severidad:** Baja (documentación)

El título del README contiene un link a una URL de ngrok que ya no funciona:

```markdown
# [DJCSK](https://coherent-lividly-unclaimed.ngrok-free.dev/accounts/login/#) - Prueba de Concepto Django + Ngrok + Docker
```

**Solución sugerida:** Eliminar el link o cambiarlo por el link al repo de GitHub.

---

## 2. Cosas que faltan por desarrollar

### 2.1 No hay sistema de registro de usuarios

No existe una página de registro. Los usuarios solo se pueden crear desde el admin de Django (`/admin/`) o con `createsuperuser`.

### 2.2 No hay "olvidé mi contraseña"

El link "¿Olvidaste tu contraseña?" en el login (`login.html:44`) apunta a `#` y no hace nada.

### 2.3 "Contacta a Administración" no funciona

El link "Contacta a Administración" en el login (`login.html:93`) apunta a `#`.

### 2.4 No hay página de perfil de usuario

No hay forma de que el usuario cambie su contraseña o vea su perfil.

### 2.5 ~~No hay botón de eliminar en el frontend~~ ✅ PARCIAL

- Productos: ya tienen botón de eliminar en `product_list.html`
- Categorías: ya tienen botón de eliminar en `category_list.html`
- Compras: pendiente (no tiene botón de eliminar en el frontend)

### 2.6 Falta DELETE en la API REST

Los ViewSets (`ModelViewSet`) incluyen DELETE por defecto, pero no está documentado ni probado.

### 2.7 ~~No hay validación de stock al crear compra~~ ✅ RESUELTO

`PurchaseCreateView.form_valid()` ahora actualiza automáticamente `product.quantity += form.cleaned_data['quantity']` y guarda el producto. `PurchaseUpdateView` también maneja el delta de cantidad correctamente al cambiar de producto o cantidad.

### 2.8 No hay búsqueda/filtro en la API REST

Los ViewSets no tienen `SearchFilter`, `OrderingFilter` ni `DjangoFilterBackend`. La API devuelve todos los registros sin paginación por defecto (DRF usa `PAGE_SIZE` de settings, que no está configurado).

### 2.9 No hay manejo de imágenes de producto

El modelo `Product` no tiene campo para imagen. Los mockups en `vistas/` muestran imágenes de producto.

### 2.10 Los prototipos en `vistas/` usan nombre "Sahara"

Los mockups HTML en `vistas/` usan el nombre "Sahara". El nombre definitivo del proyecto es **PupiStock** (ver Q1 en §3). Hay que actualizar los mockups.

### 2.11 No hay CI/CD

No existe `.github/workflows/` ni ningún pipeline de integración continua. Si se agrega, debería ejecutar migraciones y tests.

### 2.12 Cobertura de tests insuficiente

Solo hay 2 tests unitarios. Faltan tests de:
- Vistas (login, CRUD, dashboard)
- API (endpoints REST)
- Lógica de negocio (creación automática de compras)
- Validación de formularios
- Edge cases (usuario sin permisos, categorías vacías, etc.)

### 2.13 El sidebar no tiene link al dashboard

En `base.html`, los links de navegación son Categorías, Productos y Compras. No hay un link para volver al dashboard `/`.

### 2.14 `stock_project_prd.md` describe funcionalidades no implementadas

El PRD menciona:
- Búsqueda por SKU (no existe campo SKU)
- Filtro "Low Stock", "Out of Stock"
- Imágenes de producto
- Floating Action Button (FAB)
- Bulk actions
- Collapsed mode del sidebar

### 2.15 No hay soporte multi-tienda

**Derivado de Q4 en §3.** El modelo actual asume una sola tienda. Se necesita modelar tiendas (`Store`) como entidad independiente y relacionar productos, compras y usuarios a una tienda.

**Requerimientos:**
- Modelo `Store` con campos: nombre, dirección, tipo (supermercado, bodega, etc.)
- Relación `Product` → `Store` (un producto puede existir en múltiples tiendas con distintos precios)
- Relación `Purchase` → `Store`
- Usuario puede pertenecer a una o varias tiendas

### 2.16 No hay gráficos de gastos (dashboard analytics)

**Derivado de Q4 en §3.** El dashboard actual (`/`) solo muestra contadores. Se necesita visualización de datos:

- Gráfico de gastos por tienda (comparativa)
- Gráfico de gastos en el tiempo (línea de tiempo)
- Gráfico de distribución por categoría
- Top productos más comprados

**Sugerencia técnica:** Evaluar Chart.js (vía CDN, consistente con la decisión de CDN para Tailwind) o Alpine.js + SVG.

### 2.17 No hay comparación de precios entre tiendas

**Derivado de Q4 en §3.** El usuario debe poder ver, al momento de comprar, en qué tienda está más barato un producto.

**Requerimientos:**
- Vista de comparación de precios: dado un producto, mostrar precio en cada tienda
- Destacar la tienda más barata
- Posibilidad de registrar el precio pagado en la compra (para datos reales vs. precios de referencia)

---

## 3. Preguntas sin resolver

1. **~~¿Cuál es el nombre definitivo del proyecto?~~** ✅ Resuelto. El nombre definitivo es **PupiStock**. El repo sigue siendo "DJCSK". Queda pendiente actualizar los mockups en `vistas/` que usan "Sahara" (ver 2.10).

2. **~~¿Debe el campo `quantity` de Product actualizarse con las compras?~~** ✅ Resuelto. `PurchaseCreateView` y `PurchaseUpdateView` ahora incrementan/decrementan `product.quantity` automáticamente.

3. **~~¿La importación CSV es solo para setup inicial o debe soportar actualizaciones?~~** ✅ Resuelto. Solo para kick-off inicial. El script `import_products.py` salta productos existentes, no los actualiza.

4. **~~¿Se planea tener múltiples tenants/tiendas?~~** ✅ Resuelto. Sí, se planea soportar múltiples tiendas. El usuario podrá crear gráficos de gastos y validar en qué tienda es más barato al momento de comprar. → Ver nuevas issues 2.15, 2.16, 2.17.

5. **~~¿Se usará el Tailwind compilado o se mantendrá solo CDN?~~** ✅ Resuelto. Se mantendrá **solo CDN**. La etapa `nodebuild` del Dockerfile y el script `build:css` de npm deben eliminarse (ver 1.1 y 1.2 actualizados).

---

## 4. Mejoras sugeridas (quick wins)

| Prioridad | Tarea | Esfuerzo |
|---|---|---|
| Alta | ~~Eliminar `SECRET_KEY` y `DEBUG` hardcodeados~~ ✅ | — |
| Media | Agregar `LOGIN_URL = 'login'` en settings | 1 min |
| Media | ~~Mover creación de compras fuera del GET~~ ✅ | — |
| Media | Eliminar o renombrar `seed_categories.py` raíz | 1 min |
| Baja | Eliminar etapa `nodebuild` del Dockerfile y script `build:css` de npm | 15 min |
| Baja | Corregir `CSRF_TRUSTED_ORIGINS` para usar `django-environ` | 5 min |
| Baja | Agregar filtros a la API REST | 30 min |
| Baja | Agregar más tests unitarios | 1-3 h |

---

*Backlog generado con el análisis del proyecto. Actualizar al resolver cada item.*
