from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
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
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Employee information",
            {
                "fields": (
                    "role",
                    "department",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Employee information",
            {
                "fields": (
                    "role",
                    "department",
                )
            },
        ),
    )