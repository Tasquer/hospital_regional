# Proyecto Base + Módulo de Clínica

Este proyecto es un punto de partida en **Django 5 + Tailwind** que ya trae autenticación con `django-allauth`, MFA, control de sesiones, roles y layout responsive. Sobre esta base se añadió la app **`clinica`** para gestionar pacientes y casos clínicos.

## Cambios realizados

- **App `clinica` integrada al dashboard**: añadida a `LOCAL_APPS` con verbose name “Gestión clínica”. El sidebar incluye ahora los accesos a **Pacientes**, **Casos clínicos** y **Partos**, todos con los mismos iconos, estados hover y estilos activos del layout principal.
- **Modelos clínicos** (`clinica/models.py`):
  - `Paciente`: RUT único, datos personales, estado activo/inactivo y tracking de creación.
  - `CasoClinico`: enlazado a un paciente y a un médico responsable (`AUTH_USER_MODEL`), con especialidad, prioridad y estado.
  - `Parto`: vinculado a la madre (`Paciente`), registra tipo de parto, sala, complicaciones, duración del trabajo de parto y profesional responsable.
  - `RecienNacido`: asociado a un parto, contempla identificador (RN1, RN2…), sexo, peso, talla, APGAR, condición inicial y derivación.
  - `Alta`: registro uno a uno con cada parto que deja constancia de fecha, tipo de alta, profesional, estado al egreso, seguimiento y próxima cita.
- **Admin** (`clinica/admin.py`): cada modelo cuenta con listados personalizados con filtros, búsqueda y `autocomplete_fields` (paciente, médico, partos, recién nacidos y altas) para facilitar la carga de datos.
- **Vistas + URLs** (namespace `clinica`):
  - Pacientes: `PacienteListView`, `PacienteCreateView`, `PacienteUpdateView`, `PacienteDetailView`.
  - Casos clínicos: `CasoClinicoListView`, `CasoClinicoCreateView`, `CasoClinicoUpdateView`, `CasoClinicoDetailView`.
  - Partos: `PartoListView`, `PartoCreateView`.
  - Trazabilidad: `PacienteTrazabilidadDetailView` muestra en una sola ficha la madre, sus partos, recién nacidos y altas clínicas.
- **Formularios reutilizables** (`clinica/forms.py`): `BaseClinicaForm`, `PacienteForm` y `CasoClinicoForm` aplican automáticamente las clases Tailwind usadas en el dashboard, validaciones coherentes y placeholders descriptivos.
- **Templates consistentes**:
  - Listas (`templates/clinica/*/lista.html`): tablas oscuras con la misma estructura que “Últimos usuarios conectados”, badges por estado/prioridad, paginador y botón “Nuevo” con estilo morado. La lista de pacientes incorpora un enlace directo a la trazabilidad.
  - Formularios (`templates/clinica/*/formulario.html`): tarjetas centradas (`rounded-3xl` + `bg-slate-900/70`) con inputs blancos, mensajes de error destacados y botones indigo. Incluye el formulario de Partos y los formularios ya existentes de Pacientes/Casos clínicos.
  - Detalles y trazabilidad: tarjetas modulares con resúmenes, chips de estado y tabs (por ejemplo, ficha de paciente, detalle de caso, nueva ficha de trazabilidad madre–RN).
- **Migraciones** (`clinica/migrations/0001_initial.py` + posteriores) listas para ejecutar.
- **Usuario demo** `adminclinica` creado para pruebas rápidas.

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

- Añadir filtros/búsqueda específicos en las listas (ej. partos por fecha, pacientes por RUT, casos por prioridad).
- Cubrir modelos y vistas con tests unitarios/funcionales.
- Definir carga de archivos clínicos (imágenes u otros adjuntos) si el flujo lo requiere.
- Evaluar permisos específicos por rol para restringir acciones dentro del módulo clínico (ej. quién puede crear partos o registrar altas).
