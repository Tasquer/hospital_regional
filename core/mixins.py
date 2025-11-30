from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied

class PermitsPositionMixin:
    """
    Mixin inteligente que verifica si el 'permission_code' del usuario 
    está en la lista 'permission_required' definida en la Vista.
    """
    redirect_url = reverse_lazy("Home")
    permission_required = [] # Aquí la vista define quién entra (ej: ['CLINICAL_FULL'])

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        # 1. Validación básica de login
        if not user.is_authenticated:
            return redirect(self.redirect_url)
            
        # 2. El Superusuario (Admin Django) siempre tiene llave maestra
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # 3. Verificar Cargo y Permisos
        try:
            # Obtener perfil de forma segura
            profile = getattr(user, "profile", None)
            if not profile:
                messages.error(request, "Tu usuario no tiene un perfil activo.")
                return redirect(self.redirect_url)

            position = getattr(profile, "position_FK", None)
            if not position:
                messages.error(request, "No tienes un cargo asignado en tu perfil.")
                return redirect(self.redirect_url)

            # Este es el código que tiene el usuario (ej: 'CLINICAL_FULL')
            user_perm_code = position.permission_code
            
            # ACCESO TOTAL (Director/Jefe) entra a todo
            if user_perm_code == 'TOTAL_ACCESS':
                return super().dispatch(request, *args, **kwargs)

            # LÓGICA CLAVE: ¿Está mi código en la lista de invitados de esta vista?
            if user_perm_code in self.permission_required:
                return super().dispatch(request, *args, **kwargs)
            
            # Si llegamos acá, tiene cargo pero no está invitado a esta vista
            messages.warning(request, "No tienes permisos para ver esta sección.")
            return redirect(self.redirect_url)

        except Exception as e:
            # Puedes descomentar el print para ver errores en la consola si algo falla
            # print(f"Error de permisos: {e}")
            messages.error(request, "Ocurrió un error verificando tus permisos.")
            return redirect(self.redirect_url)