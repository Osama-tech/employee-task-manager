from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.test import APITestCase

from apps.tasks.models import Task
from apps.users.choices import Role
from apps.users.models import User

from .models import Department


class DepartmentPermissionTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")
        self.employee = User.objects.create_user(
            username="emp", password="pass12345", role=Role.EMPLOYEE
        )
        self.manager = User.objects.create_user(
            username="mgr", password="pass12345", role=Role.MANAGER
        )

    def test_unauthenticated_user_cannot_read_departments(self):
        response = self.client.get("/api/departments/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_can_read_but_not_create_departments(self):
        self.client.force_authenticate(user=self.employee)

        list_response = self.client.get("/api/departments/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        create_response = self.client.post("/api/departments/", {"name": "Sales"})
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_and_edit_departments(self):
        self.client.force_authenticate(user=self.manager)

        create_response = self.client.post("/api/departments/", {"name": "Sales"})
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        dept_id = create_response.data["id"]
        edit_response = self.client.patch(
            f"/api/departments/{dept_id}/", {"name": "Sales & Marketing"}
        )
        self.assertEqual(edit_response.status_code, status.HTTP_200_OK)
        self.assertEqual(edit_response.data["name"], "Sales & Marketing")

    def test_department_name_must_be_unique(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post("/api/departments/", {"name": "Engineering"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DepartmentIntegrityTests(APITestCase):
    """A department that still has employees or tasks attached to it must
    not be deletable - the FK uses on_delete=PROTECT, this confirms that
    behavior holds through the API, not just at the DB layer."""

    def setUp(self):
        self.department = Department.objects.create(name="Engineering")
        self.manager = User.objects.create_user(
            username="mgr", password="pass12345", role=Role.MANAGER
        )

    def test_cannot_delete_department_with_employees(self):
        User.objects.create_user(
            username="emp",
            password="pass12345",
            role=Role.EMPLOYEE,
            department=self.department,
        )

        with self.assertRaises(ProtectedError):
            self.department.delete()

    def test_cannot_delete_department_with_tasks(self):
        Task.objects.create(title="Some task", department=self.department)

        with self.assertRaises(ProtectedError):
            self.department.delete()

    def test_can_delete_empty_department(self):
        empty_department = Department.objects.create(name="Unused")
        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(f"/api/departments/{empty_department.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deleting_protected_department_via_api_returns_400_not_500(self):
        """Regression test: ProtectedError must surface as a clean 400
        through the API, not an unhandled 500."""
        User.objects.create_user(
            username="emp",
            password="pass12345",
            role=Role.EMPLOYEE,
            department=self.department,
        )
        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(f"/api/departments/{self.department.id}/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)