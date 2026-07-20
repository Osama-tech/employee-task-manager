from django.db import models


class Role(models.TextChoices):
    EMPLOYEE = "EMPLOYEE", "Employee"
    MANAGER = "MANAGER", "Manager"
    ADMIN = "ADMIN", "Admin"