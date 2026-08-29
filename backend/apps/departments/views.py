from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsStaffOrReadOnly

from .models import Department
from .serializers import DepartmentSerializer

class DepartmentListAPIView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsStaffOrReadOnly]


class DepartmentDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsStaffOrReadOnly]