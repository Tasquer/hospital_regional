from django.shortcuts import redirect
from django.urls import reverse_lazy


class PermitsPositionMixin:
    """
    Mixin para comprobar si el usuario tiene los permisos adecuados según su cargo.
    Redirecciona a 'Inicio' si el usuario no está permitido.
    """

    redirect_url = reverse_lazy("Home")

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser or (
            hasattr(user, "profile")
            and getattr(user.profile, "position_FK", None)
            and user.profile.position_FK.permission_code != "RESTRICTED"
        ):
            return super().dispatch(request, *args, **kwargs)
        return redirect(self.redirect_url)
