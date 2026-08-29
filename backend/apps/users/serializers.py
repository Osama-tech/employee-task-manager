from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .choices import Role
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Employee directory serializer, used by Manager/Admin to list,
    create, and edit employees. `password` is optional on write: omit it
    on update to leave the password unchanged."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "department",
            "is_active",
            "date_joined",
            "password",
        )
        read_only_fields = ("date_joined",)

    def validate_password(self, value):
        if value:
            validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """Public self-registration endpoint. Role is always forced to
    EMPLOYEE server-side - the client cannot request Manager/Admin here,
    which prevents privilege escalation through the public API. Elevated
    roles can only be granted by an existing Manager/Admin through the
    employee directory endpoint."""

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "department",
            "password",
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data, role=Role.EMPLOYEE)
        user.set_password(password)
        user.save()
        return user