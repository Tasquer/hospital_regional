from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CasoClinicoForm, PacienteForm, RecienNacidoForm, PartoForm
from .models import CasoClinico, Paciente, Parto, RecienNacido


class PacienteListView(LoginRequiredMixin, ListView):
    model = Paciente
    template_name = "clinica/pacientes/lista.html"
    context_object_name = "pacientes"
    paginate_by = 20


class PacienteCreateView(LoginRequiredMixin, CreateView):
    model = Paciente
    template_name = "clinica/pacientes/formulario.html"
    form_class = PacienteForm
    success_url = reverse_lazy("clinica:paciente_list")


class PacienteUpdateView(PacienteCreateView, UpdateView):
    pass


class PacienteDetailView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = "clinica/pacientes/detalle.html"
    context_object_name = "paciente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["casos_clinicos"] = (
            self.object.casos_clinicos.select_related("medico_responsable")
            .order_by("-fecha_creacion")
        )
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.object
        partos = paciente.partos.select_related("personal_responsable").all()

        trazabilidad = []
        for parto in partos:
            recien_nacidos = list(parto.recien_nacidos.all())
            alta = getattr(parto, "alta", None)
            trazabilidad.append(
                {
                    "parto": parto,
                    "recien_nacidos": recien_nacidos,
                    "alta": alta,
                }
            )

        context["trazabilidad"] = trazabilidad
        return context


class PartoListView(LoginRequiredMixin, ListView):
    model = Parto
    template_name = "clinica/partos/lista.html"
    context_object_name = "partos"
    paginate_by = 10

    def get_queryset(self):
        qs = (
            Parto.objects.select_related("paciente", "personal_responsable")
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
    
class PartoUpdateView(LoginRequiredMixin, UpdateView):
    model = Parto
    template_name = "clinica/partos/formulario.html"
    form_class = PartoForm
    success_url = reverse_lazy("clinica:parto_list")

    

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
            initial["parto"] = parto_id
        return initial


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
            .select_related("parto", "parto__paciente")
        )


# Create your views here.
