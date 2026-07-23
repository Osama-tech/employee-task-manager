from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.departments.models import Department

from .choices import TaskPriority, TaskStatus


class Task(models.Model):
    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )

    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="tasks",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if (
            self.assigned_to
            and self.assigned_to.department_id != self.department_id
        ):
            raise ValidationError(
                {
                    "assigned_to": (
                        "Assigned user must belong to the selected department."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title