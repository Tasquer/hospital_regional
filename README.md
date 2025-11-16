# Proyecto Base + Módulo de Clínica

Este proyecto es un punto de partida en **Django 5 + Tailwind** que ya trae autenticación con `django-allauth`, MFA, control de sesiones, roles y layout responsive. Sobre esta base se añadió la app **`clinica`** para gestionar pacientes y casos clínicos.

## Cambios realizados

- Se creó la app `clinica` y se agregó a `LOCAL_APPS` (`core/settings.py`) con verbose name “Gestión clínica”.
- Nuevos modelos en `clinica/models.py`:
  - `Paciente`: RUT único, datos personales, estado activo/inactivo y fecha de creación.
  - `CasoClinico`: asociado a un paciente, incluye resumen, especialidad, prioridad, estado y médico responsable (`AUTH_USER_MODEL`).
- Registro en el admin (`clinica/admin.py`) con listados, filtros, búsqueda y `autocomplete_fields`.
- Vistas basadas en clases (`clinica/views.py`) para listar/crear/editar/ver pacientes y casos, usando `LoginRequiredMixin`.
- Rutas namespaced en `clinica/urls.py` y enlazadas desde `core/urls.py` bajo el prefijo `clinica/`.
- Templates Tailwind en `templates/clinica/...` que extienden `components/Layout/base_extendido.html`:
  - Pacientes: `lista.html`, `formulario.html`, `detalle.html`.
  - Casos clínicos: `lista.html`, `formulario.html`, `detalle.html`.
- Migración inicial `clinica/migrations/0001_initial.py`.
- Superusuario creado para administración rápida (`adminclinica`).

## Configuración y uso

1. **Activar entorno virtual**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. **Instalar dependencias**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Ejecutar migraciones del módulo de clínica**
   ```powershell
   python manage.py makemigrations clinica
   python manage.py migrate
   ```
4. **Iniciar el servidor de desarrollo**
   ```powershell
   python manage.py runserver
   ```

> **Nota:** si aparece un error por `django-environ`, asegúrate de instalarlo (ya está en `requirements.txt`).

## Acceso al panel de administración

| Campo      | Valor                         |
|------------|------------------------------|
| Usuario    | `adminclinica`               |
| Email      | `admin@hospitalregional.com` |
| Contraseña | `532518143239`               |

Una vez activo el servidor, accede a `http://localhost:8000/admin/` con esas credenciales. Se recomienda cambiar la contraseña y habilitar MFA tan pronto sea posible si el entorno es compartido.

## Próximos pasos sugeridos

- Añadir enlaces en el sidebar (`templates/components/navbar/`) apuntando a `clinica:paciente_list`.
- Crear tests para los modelos y vistas de la app.
- Configurar almacenamiento de imágenes o documentos clínicos si se necesitan adjuntar archivos.
