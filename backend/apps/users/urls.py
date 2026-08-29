from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, MeAPIView, RegisterAPIView

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")

urlpatterns = [
    path("me/", MeAPIView.as_view(), name="me"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    *router.urls,
]