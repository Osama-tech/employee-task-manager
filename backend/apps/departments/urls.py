from django.urls import path

from .views import DepartmentListAPIView, DepartmentDetailAPIView

urlpatterns = [
    path(
        "",
        DepartmentListAPIView.as_view(),
        name="department-list",
    ),
    path(
        "<int:pk>/",
        DepartmentDetailAPIView.as_view(),
        name="department-detail",

    ),
]