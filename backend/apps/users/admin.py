from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "department",
        "is_active",
    )
    search_fields = (
        "username",
        "email",
    )

    list_filter = (
        "role",
        "department",
        "is_active",
    )

    ordering = (
        "username",
    )