from django.contrib.auth.password_validation import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from apps.departments.models import Department

from .choices import Role
from .models import User


class RegistrationTests(APITestCase):
    def test_registration_creates_employee_account(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "username": "newhire",
                "email": "newhire@example.com",
                "password": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="newhire")
        self.assertEqual(user.role, Role.EMPLOYEE)
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_registration_cannot_escalate_role(self):
        """A client cannot register themselves in as ADMIN or MANAGER by
        including a role in the request body - the server must ignore it."""
        response = self.client.post(
            "/api/users/register/",
            {
                "username": "sneaky",
                "email": "sneaky@example.com",
                "password": "StrongPass123!",
                "role": "ADMIN",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="sneaky")
        self.assertEqual(user.role, Role.EMPLOYEE)

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "username": "weakpass",
                "email": "weak@example.com",
                "password": "12345678",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="weakpass").exists())


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice", password="pass12345", role=Role.EMPLOYEE
        )

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "alice", "password": "pass12345"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "alice", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_issues_new_access_token(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "alice", "password": "pass12345"},
        )
        refresh_token = login.data["refresh"]

        response = self.client.post(
            "/api/auth/refresh/", {"refresh": refresh_token}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_endpoint_requires_authentication(self):
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_returns_current_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "alice")
        self.assertEqual(response.data["role"], Role.EMPLOYEE)


class EmployeeDirectoryPermissionTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")
        self.employee = User.objects.create_user(
            username="emp", password="pass12345", role=Role.EMPLOYEE
        )
        self.manager = User.objects.create_user(
            username="mgr", password="pass12345", role=Role.MANAGER
        )
        self.admin = User.objects.create_user(
            username="admin", password="pass12345", role=Role.ADMIN
        )

    def test_unauthenticated_user_cannot_list_employees(self):
        response = self.client.get("/api/users/employees/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_can_list_but_not_create(self):
        self.client.force_authenticate(user=self.employee)

        list_response = self.client.get("/api/users/employees/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        create_response = self.client.post(
            "/api/users/employees/",
            {"username": "shouldfail", "role": Role.EMPLOYEE},
        )
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_employee(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            "/api/users/employees/",
            {
                "username": "createdbymanager",
                "email": "cbm@example.com",
                "password": "AnotherPass123!",
                "role": Role.EMPLOYEE,
                "department": self.department.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="createdbymanager").exists())

    def test_admin_can_deactivate_employee(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/users/employees/{self.employee.id}/",
            {"is_active": False},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertFalse(self.employee.is_active)