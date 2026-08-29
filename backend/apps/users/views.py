from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import User
from .permissions import IsStaffOrReadOnly
from .serializers import RegisterSerializer, UserSerializer


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "role": request.user.role,
            "department": request.user.department_id,
        })


class RegisterAPIView(APIView):
    """Public self-registration. Always creates an EMPLOYEE account -
    see RegisterSerializer for why the role can't be chosen by the caller."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class EmployeeViewSet(ModelViewSet):
    """Employee directory. Any authenticated user can browse it (needed to
    assign tasks to teammates); only Manager/Admin can create, edit, or
    deactivate employees."""

    queryset = User.objects.select_related("department").order_by("username")
    serializer_class = UserSerializer
    permission_classes = [IsStaffOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["role", "department", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "date_joined", "role"]
    ordering = ["username"]