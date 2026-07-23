from rest_framework import serializers
from apps.departments.serializers import DepartmentSerializer
from apps.departments.models import Department
from .models import Task



class TaskSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="department",
        write_only=True,
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "department",
            "department_id",
            "assigned_to",
            "created_at",
            "updated_at",
        )