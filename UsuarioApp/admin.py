from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, Position

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user_FK",)


admin.site.register(Profile, ProfileAdmin)


class PositionAdmin(admin.ModelAdmin):
    list_display = ("user_position",)


admin.site.register(Position, PositionAdmin)
