from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CasoClinicoForm, PacienteForm
from .models import CasoClinico, Paciente


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

# Create your views here.
