from django.db import models
from django.contrib.auth.models import AbstractUser
from .choices import Role

class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )
    
    def __str__(self):
        return self.username