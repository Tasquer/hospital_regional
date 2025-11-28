from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import (
    AltaForm,
    CasoClinicoForm,
    PacienteForm,
    RecienNacidoForm,
    PartoForm,
)
from .models import Alta, CasoClinico, Paciente, Parto, RecienNacido


class PacienteListView(LoginRequiredMixin, ListView):
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


class PacienteCreateView(LoginRequiredMixin, CreateView):
    model = Paciente
    template_name = "clinica/pacientes/formulario.html"
    form_class = PacienteForm
    success_url = reverse_lazy("clinica:paciente_list")

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.registrado_por = self.request.user
        return super().form_valid(form)


class PacienteUpdateView(PacienteCreateView, UpdateView):
    pass


class PacienteDetailView(LoginRequiredMixin, DetailView):
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


class CasoClinicoListView(LoginRequiredMixin, ListView):
    model = CasoClinico
    template_name = "clinica/casos/lista.html"
    context_object_name = "casos"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related("paciente", "medico_responsable")


class CasoClinicoCreateView(LoginRequiredMixin, CreateView):
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


class CasoClinicoDetailView(LoginRequiredMixin, DetailView):
    model = CasoClinico
    template_name = "clinica/casos/detalle.html"
    context_object_name = "caso"

    def get_queryset(self):
        return super().get_queryset().select_related("paciente", "medico_responsable")


class PacienteTrazabilidadDetailView(LoginRequiredMixin, DetailView):
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


class PartoListView(LoginRequiredMixin, ListView):
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


class PartoCreateView(LoginRequiredMixin, CreateView):
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


class PartoUpdateView(LoginRequiredMixin, UpdateView):
    model = Parto
    template_name = "clinica/partos/formulario.html"
    form_class = PartoForm
    success_url = reverse_lazy("clinica:parto_list")

    def get_success_url(self):
        return reverse("clinica:parto_detail", args=[self.object.pk])


class PartoDetailView(LoginRequiredMixin, DetailView):
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


class RecienNacidoListView(LoginRequiredMixin, ListView):
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


class RecienNacidoCreateView(LoginRequiredMixin, CreateView):
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


class RecienNacidoDetailView(LoginRequiredMixin, DetailView):
    model = RecienNacido
    template_name = "clinica/recien_nacidos/detalle.html"
    context_object_name = "rn"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("parto", "parto__paciente", "parto__alta")
        )


class AltaCreateView(LoginRequiredMixin, CreateView):
    model = Alta
    template_name = "clinica/altas/formulario.html"
    form_class = AltaForm

    def get_initial(self):
        initial = super().get_initial()
        # Modificado: Se soporta 'parto_id' (enviado por dashboard) o 'parto'
        parto_id = self.request.GET.get("parto_id") or self.request.GET.get("parto")
        if parto_id:
            try:
                # Se asigna el ID directamente
                initial["parto"] = Parto.objects.get(pk=parto_id)
            except Parto.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        # NOTA: Al estar el campo disabled, Django usa el valor inicial (get_initial)
        # o el valor de la instancia automáticamente.
        parto = form.cleaned_data.get("parto")
        
        # Si por alguna razón parto es None (edge case), intentamos recuperarlo del initial
        if not parto:
             try:
                 parto_id = self.get_initial().get('parto')
                 if parto_id:
                     parto = parto_id # Puede ser objeto o ID
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


class AltaUpdateView(LoginRequiredMixin, UpdateView):
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