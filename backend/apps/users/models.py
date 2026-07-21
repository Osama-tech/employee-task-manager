from django.db import models
from django.contrib.auth.models import AbstractUser

from .choices import Role
from apps.departments.models import Department

class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username