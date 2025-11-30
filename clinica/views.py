from django.contrib import messages
# Eliminamos LoginRequiredMixin porque PermitsPositionMixin ya maneja la autenticación
from django.db.models import Prefetch, Q
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

# Importamos nuestro mixin personalizado
from core.mixins import PermitsPositionMixin

from .forms import (
    AltaForm,
    CasoClinicoForm,
    PacienteForm,
    RecienNacidoForm,
    PartoForm,
)
from .models import Alta, CasoClinico, Paciente, Parto, RecienNacido


# -----------------------------------------------------------------------------
# VISTAS DE PACIENTE
# -----------------------------------------------------------------------------

class PacienteListView(PermitsPositionMixin, ListView):
    # Todos pueden ver la lista (Clínicos y Administrativos)
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT', 'ADMINISTRATIVE']
    
    model = Paciente
    template_name = "clinica/pacientes/lista.html"
    context_object_name = "pacientes"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("registrado_por")
        query = self.request.GET.get("q", "").strip()
        estado = self.request.GET.get("estado_atencion", "")
        riesgo = self.request.GET.get("riesgo_obstetrico", "")

        if query:
            qs = qs.filter(
                Q(rut__icontains=query)
                | Q(nombres__icontains=query)
                | Q(apellido_paterno__icontains=query)
                | Q(apellido_materno__icontains=query)
            )
        if estado:
            qs = qs.filter(estado_atencion=estado)
        if riesgo:
            qs = qs.filter(riesgo_obstetrico=riesgo)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "q": self.request.GET.get("q", ""),
                "estado_actual": self.request.GET.get("estado_atencion", ""),
                "riesgo_actual": self.request.GET.get("riesgo_obstetrico", ""),
                "estado_choices": Paciente.EstadoAtencionChoices.choices,
                "riesgo_choices": Paciente.RiesgoObstetricoChoices.choices,
            }
        )
        return context


class PacienteCreateView(PermitsPositionMixin, CreateView):
    # Crear pacientes: Administrativos (Admisión) y Clínicos Full (Médicos/Matronas)
    permission_required = ['CLINICAL_FULL', 'ADMINISTRATIVE']
    
    model = Paciente
    template_name = "clinica/pacientes/formulario.html"
    form_class = PacienteForm
    success_url = reverse_lazy("clinica:paciente_list")

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.registrado_por = self.request.user
        return super().form_valid(form)


class PacienteUpdateView(PacienteCreateView, UpdateView):
    # Hereda permisos de PacienteCreateView
    pass


class PacienteDetailView(PermitsPositionMixin, DetailView):
    # Ver ficha completa: Solo personal clínico (TENS, Enfermeras, Médicos, Matronas)
    # Administrativos NO deberían ver detalles clínicos sensibles aquí
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT']

    model = Paciente
    template_name = "clinica/pacientes/detalle.html"
    context_object_name = "paciente"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "partos",
                    queryset=
                    Parto.objects.select_related("personal_responsable", "alta")
                    .prefetch_related("recien_nacidos"),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["casos_clinicos"] = (
            self.object.casos_clinicos.select_related("medico_responsable")
            .order_by("-fecha_creacion")
        )
        context["partos"] = self.object.partos.all()
        return context


class PacienteTrazabilidadDetailView(PermitsPositionMixin, DetailView):
    # Trazabilidad: Solo clínicos
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT']
    
    model = Paciente
    template_name = "clinica/paciente_trazabilidad_detail.html"
    context_object_name = "paciente"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "partos",
                    queryset=
                    Parto.objects.select_related("personal_responsable", "alta")
                    .prefetch_related("recien_nacidos"),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partos = self.object.partos.all()
        context["trazabilidad"] = partos
        context["partos"] = partos
        return context


# -----------------------------------------------------------------------------
# VISTAS DE CASOS CLÍNICOS
# -----------------------------------------------------------------------------

class CasoClinicoListView(PermitsPositionMixin, ListView):
    # Ver lista casos: Todo el personal clínico
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT']
    
    model = CasoClinico
    template_name = "clinica/casos/lista.html"
    context_object_name = "casos"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related("paciente", "medico_responsable")


class CasoClinicoCreateView(PermitsPositionMixin, CreateView):
    # Crear caso: Solo Médicos/Matronas (CLINICAL_FULL)
    permission_required = ['CLINICAL_FULL']
    
    model = CasoClinico
    template_name = "clinica/casos/formulario.html"
    form_class = CasoClinicoForm
    success_url = reverse_lazy("clinica:caso_list")

    def get_initial(self):
        initial = super().get_initial()
        paciente_id = self.request.GET.get("paciente")
        if paciente_id:
            initial["paciente"] = paciente_id
        return initial


class CasoClinicoUpdateView(CasoClinicoCreateView, UpdateView):
    pass


class CasoClinicoDetailView(PermitsPositionMixin, DetailView):
    # Ver detalle caso: Todo el personal clínico
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT']
    
    model = CasoClinico
    template_name = "clinica/casos/detalle.html"
    context_object_name = "caso"

    def get_queryset(self):
        return super().get_queryset().select_related("paciente", "medico_responsable")


# -----------------------------------------------------------------------------
# VISTAS DE PARTOS
# -----------------------------------------------------------------------------

class PartoListView(PermitsPositionMixin, ListView):
    # Ver lista partos: Todo el personal clínico
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT']
    
    model = Parto
    template_name = "clinica/partos/lista.html"
    context_object_name = "partos"
    paginate_by = 10

    def get_queryset(self):
        qs = (
            Parto.objects.select_related("paciente", "personal_responsable", "alta")
            .prefetch_related("recien_nacidos")
            .order_by("-fecha_hora")
        )
        return qs


class PartoCreateView(PermitsPositionMixin, CreateView):
    # REGISTRAR PARTO: Acción crítica. Solo Médicos/Matronas.
    permission_required = ['CLINICAL_FULL']
    
    model = Parto
    template_name = "clinica/partos/formulario.html"
    form_class = PartoForm
    success_url = reverse_lazy("clinica:parto_list")

    def get_initial(self):
        initial = super().get_initial()
        paciente_id = self.request.GET.get("paciente")
        if paciente_id:
            try:
                initial["paciente"] = Paciente.objects.get(pk=paciente_id)
            except Paciente.DoesNotExist:
                pass
        return initial

    def get_success_url(self):
        return reverse("clinica:parto_detail", args=[self.object.pk])


class PartoUpdateView(PermitsPositionMixin, UpdateView):
    # Editar parto: Solo Médicos/Matronas.
    permission_required = ['CLINICAL_FULL']
    
    model = Parto
    template_name = "clinica/partos/formulario.html"
    form_class = PartoForm
    success_url = reverse_lazy("clinica:parto_list")

    def get_success_url(self):
        return reverse("clinica:parto_detail", args=[self.object.pk])


class PartoDetailView(PermitsPositionMixin, DetailView):
    # Ver detalle parto: Todo el personal clínico
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT']
    
    model = Parto
    template_name = "clinica/partos/detalle.html"
    context_object_name = "parto"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("paciente", "personal_responsable", "alta")
            .prefetch_related("recien_nacidos")
        )


# -----------------------------------------------------------------------------
# VISTAS DE RECIÉN NACIDOS
# -----------------------------------------------------------------------------

class RecienNacidoListView(PermitsPositionMixin, ListView):
    # Ver lista RN: Todo el personal clínico
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT']
    
    model = RecienNacido
    template_name = "clinica/recien_nacidos/lista.html"
    context_object_name = "recien_nacidos"
    paginate_by = 20

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("parto", "parto__paciente")
            .order_by("-fecha_creacion")
        )


class RecienNacidoCreateView(PermitsPositionMixin, CreateView):
    # Registrar RN: Solo Médicos/Matronas/Neonatólogos
    permission_required = ['CLINICAL_FULL']
    
    model = RecienNacido
    template_name = "clinica/recien_nacidos/formulario.html"
    form_class = RecienNacidoForm
    success_url = reverse_lazy("clinica:recien_nacido_list")

    def get_initial(self):
        initial = super().get_initial()
        parto_id = self.request.GET.get("parto")
        if parto_id:
            try:
                initial["parto"] = Parto.objects.get(pk=parto_id)
            except Parto.DoesNotExist:
                pass
        return initial

    def get_success_url(self):
        return reverse("clinica:parto_detail", args=[self.object.parto_id])


class RecienNacidoUpdateView(RecienNacidoCreateView, UpdateView):
    pass


class RecienNacidoDetailView(PermitsPositionMixin, DetailView):
    # Ver detalle RN: Todo el personal clínico
    permission_required = ['CLINICAL_FULL', 'CLINICAL_SUPPORT']
    
    model = RecienNacido
    template_name = "clinica/recien_nacidos/detalle.html"
    context_object_name = "rn"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("parto", "parto__paciente", "parto__alta")
        )


# -----------------------------------------------------------------------------
# VISTAS DE ALTA
# -----------------------------------------------------------------------------

class AltaCreateView(PermitsPositionMixin, CreateView):
    # Dar de alta: Responsabilidad Médico-Legal exclusiva (CLINICAL_FULL)
    permission_required = ['CLINICAL_FULL']
    
    model = Alta
    template_name = "clinica/altas/formulario.html"
    form_class = AltaForm

    def get_initial(self):
        initial = super().get_initial()
        parto_id = self.request.GET.get("parto_id") or self.request.GET.get("parto")
        if parto_id:
            try:
                initial["parto"] = Parto.objects.get(pk=parto_id)
            except Parto.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        parto = form.cleaned_data.get("parto")
        
        if not parto:
             try:
                 parto_id = self.get_initial().get('parto')
                 if parto_id:
                     parto = parto_id 
                     form.instance.parto = parto
             except:
                 pass

        if not parto:
            form.add_error("parto", "Debes seleccionar un parto válido.")
            return self.form_invalid(form)

        if Alta.objects.filter(parto=parto).exists():
            form.add_error("parto", "Este parto ya cuenta con un alta registrada.")
            return self.form_invalid(form)

        if not parto.recien_nacidos.exists():
            form.add_error(None, "No se puede registrar un alta sin recién nacidos asociados.")
            return self.form_invalid(form)

        if not form.instance.profesional_responsable:
            form.instance.profesional_responsable = self.request.user

        messages.success(self.request, "Alta registrada correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("clinica:paciente_trazabilidad", args=[self.object.parto.paciente_id])


class AltaUpdateView(PermitsPositionMixin, UpdateView):
    # Editar alta: Responsabilidad Médico-Legal exclusiva (CLINICAL_FULL)
    permission_required = ['CLINICAL_FULL']
    
    model = Alta
    template_name = "clinica/altas/formulario.html"
    form_class = AltaForm

    def form_valid(self, form):
        parto = form.instance.parto
        if not parto.recien_nacidos.exists():
            form.add_error(None, "No se puede editar el alta porque el parto no tiene recién nacidos.")
            return self.form_invalid(form)

        if not form.instance.profesional_responsable:
            form.instance.profesional_responsable = self.request.user

        messages.success(self.request, "Alta actualizada correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("clinica:paciente_trazabilidad", args=[self.object.parto.paciente_id])