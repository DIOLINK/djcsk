# PupiStock — Prueba de Concepto Django + Ngrok + Docker

## Despliegue rápido

Este proyecto te permite levantar una app Django completa con PostgreSQL y exponerla rápidamente a internet usando [ngrok](https://ngrok.com/) como túnel, **sin necesidad de dominio ni configuración extra**.

---

## Pasos para correr el proyecto

1. **Clona este repositorio**

   ```sh
   git clone https://github.com/DIOLINK/djcsk.git
   cd DJCSK
   ```

2. **Configura el archivo `.env`** (ya hay ejemplo funcionando)
   - Cambia las variables si lo deseas.
   - Agrega tu token de ngrok (regístrate gratis en [ngrok.com](https://ngrok.com/) y copia `NGROK_AUTHTOKEN`).
   - Cuando ngrok genere una URL nueva (~cada reinicio), cópiala tanto en `DJANGO_ALLOWED_HOSTS` como en `CSRF_TRUSTED_ORIGINS`:

     ```env
     DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,xxxxx.ngrok-free.dev
     CSRF_TRUSTED_ORIGINS=https://xxxxx.ngrok-free.dev
     NGROK_AUTHTOKEN=tu_authtoken_aklsjlkjasd
     ```

3. **Arranca los servicios**

   ```sh
   docker compose up -d
   ```

4. **Obtén tu URL pública de ngrok**

   ```sh
   ./wait_for_ngrok_url.sh
   # o mira logs manualmente:
   docker compose logs ngrok
   ```

   - Abre la URL en tu navegador.

5. **Si aparece error de HOST o CSRF:**
   1. Copia la nueva URL `xxxxx.ngrok-free.dev` en las dos variables del `.env`, como en el paso 2.
   2. Reinicia los contenedores:
      ```sh
      docker compose down
      docker compose up -d
      ```

---

## Scripts útiles

- `wait_for_ngrok_url.sh`: Espera y muestra la URL ngrok automáticamente.
- `print_ngrok_url.sh`: Imprime la URL actual (si ya está en logs).

---

## Notas

- Cada vez que se reinicia ngrok (o Docker Compose), la URL puede cambiar.
- Para pruebas puedes dejar:
  ```env
  CSRF_TRUSTED_ORIGINS=https://*.ngrok-free.dev
  ```
- **No usar así en producción.**

---

## Documentación

Para entender el proyecto a fondo (modelos, flujo, arquitectura, API), consultá la documentación para mantenimiento:

- **[doc/doc-proyect.md](doc/doc-proyect.md)** — Guía completa para developers
- **[doc/backlog.md](doc/backlog.md)** — Issues conocidos y pendientes

---

Eso es todo ¡Listo para pruebas o demos!
