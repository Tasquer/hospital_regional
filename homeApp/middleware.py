from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings
from django.urls import resolve


class UpdateLastActivityMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Exclude admin views from this middleware
        if resolve(request.path_info).app_name == "admin":
            return None

        if request.user.is_authenticated:
            try:
                profile = request.user.profile
            except AttributeError:
                # If the user profile does not exist, skip updating last activity
                return None

            # Update the last activity timestamp
            profile.update_last_activity()

            # Extend the session if the last activity is within the session age limit
            session_age_limit = now() - timedelta(seconds=settings.SESSION_COOKIE_AGE)
            if profile.last_activity and profile.last_activity > session_age_limit:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)

        return None
