# Backlog — PupiStock (DJCSK)

> **Objetivo:** Issues conocidos, cosas que no se entienden o faltan por desarrollar. Usar como referencia antes de hacer cambios en el proyecto.

---

## 1. Issues encontrados en el código

### 1.1 Dockerfile: falta `static_src/input.css`

**Archivo:** `Dockerfile:10-11`  
**Severidad:** Media

La etapa `nodebuild` del Dockerfile copia `./pupistock/static_src` y ejecuta:

```
COPY ./pupistock/static_src ./static_src
RUN npx tailwindcss -c tailwind.config.js -i ./static_src/input.css -o ./static/css/tailwind.css --minify
```

El directorio `pupistock/static_src` y el archivo `input.css` **no existen**. El paso `npm ci` también falla si no existen las dependencias instaladas (aunque `package-lock.json` sí existe).

**Impacto:** El build de Docker falla en la etapa `nodebuild`. Sin embargo, la etapa `final` del Dockerfile **no copia** el output de la etapa `nodebuild` (falta `COPY --from=nodebuild`), así que el CSS compilado nunca llega a la imagen final. El proyecto actualmente funciona porque Tailwind se carga vía CDN en `base.html`.

**Solución sugerida:**
- Opción A: Eliminar la etapa `nodebuild` del Dockerfile (no se usa)
- Opción B: Crear `pupistock/static_src/input.css` con las directivas de Tailwind y agregar `COPY --from=nodebuild /app/static/css/tailwind.css ./static/css/tailwind.css` en la etapa final

### 1.2 npm script `build:css` referencia archivo inexistente

**Archivo:** `package.json:6`  
**Severidad:** Baja

El script `build:css` referencia `./static_src/input.css` que no existe:

```json
"build:css": "tailwindcss -c tailwind.config.js -i ./static_src/input.css -o ./static/css/tailwind.css --minify"
```

Si se intenta ejecutar `npm run build:css` localmente, fallará.

**Solución sugerida:** Crear `static_src/input.css` con:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

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

### 1.5 PurchaseListView crea compras en GET (efecto secundario)

**Archivo:** `inventory/views.py:97-111`  
**Severidad:** Alta (decisión de diseño)

El método `get()` de `PurchaseListView` **crea registros en la base de datos** cada vez que se visita la página. Esto es técnicamente un efecto secundario en una petición GET, lo cual viola la semántica HTTP (GET debería ser idempotente y seguro).

```python
def get(self, request, *args, **kwargs):
    # Crea Purchase records automáticamente para productos con quantity=0
    faltantes = Product.objects.filter(quantity=0)
    for prod in faltantes:
        if not Purchase.objects.filter(product=prod, quantity=0).exists():
            Purchase.objects.create(product=prod, quantity=0, price=0, ...)
    return super().get(request, *args, **kwargs)
```

**Impacto:** Si no hay un usuario en la BD (ej: primer arranque antes de crear superusuario y sin auto-creación), la línea `User.objects.filter(is_superuser=True).first() or User.objects.first()` puede devolver `None` y se imprimirá un error pero no se creará la compra.

**Solución sugerida:** Mover la lógica de creación de compras a una acción POST, un comando de management, o un signal de Django.

### 1.6 No hay `LOGIN_URL` configurado explícitamente

**Archivo:** `pupistock/settings.py`  
**Severidad:** Baja

`settings.py` no define `LOGIN_URL`. Django usa por defecto `/accounts/login/` lo cual coincide con la ruta configurada, pero es frágil. Si alguien cambia la ruta de login, `LoginRequiredMixin` dejará de redirigir correctamente.

**Solución sugerida:** Agregar `LOGIN_URL = 'login'` en `settings.py`.

### 1.7 SECRET_KEY hardcodeada con valor inseguro

**Archivo:** `pupistock/settings.py:26`  
**Severidad:** Alta (seguridad)

La línea 26 tiene un `SECRET_KEY` hardcodeado:

```python
SECRET_KEY = 'django-insecure-)xlu=#a4ny%kw)yek7#bxn%b#qzbt8!ud58%njlw1@-erbp*y4'
```

Aunque la línea 99 lo sobreescribe con `env('SECRET_KEY')`, el valor inseguro queda en el código y será usado si `.env` no está configurado.

**Solución sugerida:** Eliminar el valor hardcodeado o cambiarlo por un placeholder que claramente indique que debe configurarse.

### 1.8 `DEBUG = True` hardcodeado

**Archivo:** `pupistock/settings.py:29`  
**Severidad:** Media (seguridad)

Igual que con `SECRET_KEY`, línea 29 tiene `DEBUG = True` hardcodeado. La línea 100 lo sobreescribe con `env('DEBUG')`, pero el valor por defecto inseguro permanece.

**Solución sugerida:** Cambiar a `DEBUG = False` como default más seguro, o usar solo la lectura del env.

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

### 2.5 No hay botón de eliminar en el frontend

Los modelos tienen eliminación vía admin y API, pero las vistas HTML no incluyen opción de borrar categorías, productos o compras.

### 2.6 Falta DELETE en la API REST

Los ViewSets (`ModelViewSet`) incluyen DELETE por defecto, pero no está documentado ni probado.

### 2.7 No hay validación de stock al crear compra

Al registrar una compra, no se actualiza automáticamente el `quantity` del producto relacionado. El campo `quantity` en `Product` es estático y no se ajusta con las compras.

### 2.8 No hay búsqueda/filtro en la API REST

Los ViewSets no tienen `SearchFilter`, `OrderingFilter` ni `DjangoFilterBackend`. La API devuelve todos los registros sin paginación por defecto (DRF usa `PAGE_SIZE` de settings, que no está configurado).

### 2.9 No hay manejo de imágenes de producto

El modelo `Product` no tiene campo para imagen. Los mockups en `vistas/` muestran imágenes de producto.

### 2.10 Los prototipos en `vistas/` usan nombre "Sahara"

Los mockups HTML en `vistas/` usan el nombre "Sahara", mientras que el proyecto real se llama "PupiStock". Conviene decidir un nombre definitivo.

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

---

## 3. Preguntas sin resolver

1. **¿Cuál es el nombre definitivo del proyecto?** El PRD dice "Sahara", el código dice "PupiStock", el repo es "DJCSK".

2. **¿Debe el campo `quantity` de Product actualizarse con las compras?** Actualmente son independientes. La lógica de "lista de compras" depende de `quantity=0`, pero nunca se incrementa al comprar.

3. **¿La importación CSV es solo para setup inicial o debe soportar actualizaciones?** El script `import_products.py` salta productos existentes, no los actualiza.

4. **¿Se planea tener múltiples tenants/tiendas?** No hay indicio en el código de multi-tenancy.

5. **¿Se usará el Tailwind compilado o se mantendrá solo CDN?** La infraestructura de build está a medias. O se completa (crear `input.css`, conectar etapas del Dockerfile) o se elimina.

---

## 4. Mejoras sugeridas (quick wins)

| Prioridad | Tarea | Esfuerzo |
|---|---|---|
| Alta | Eliminar `SECRET_KEY` y `DEBUG` hardcodeados | 5 min |
| Media | Agregar `LOGIN_URL = 'login'` en settings | 1 min |
| Media | Mover creación de compras fuera del GET | 1-2 h |
| Media | Eliminar o renombrar `seed_categories.py` raíz | 1 min |
| Baja | Crear `static_src/input.css` o eliminar etapa nodebuild | 15 min |
| Baja | Corregir `CSRF_TRUSTED_ORIGINS` para usar `django-environ` | 5 min |
| Baja | Agregar filtros a la API REST | 30 min |
| Baja | Agregar más tests unitarios | 1-3 h |

---

*Backlog generado con el análisis del proyecto. Actualizar al resolver cada item.*
