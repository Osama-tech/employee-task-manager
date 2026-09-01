from rest_framework import status
from rest_framework.test import APITestCase

from apps.departments.models import Department
from apps.users.choices import Role
from apps.users.models import User

from .choices import TaskPriority, TaskStatus
from .models import Task


class TaskValidationTests(APITestCase):
    def test_assigned_user_must_belong_to_task_department(self):
        engineering = Department.objects.create(name="Engineering")
        sales = Department.objects.create(name="Sales")
        sales_employee = User.objects.create_user(
            username="salesrep",
            password="pass12345",
            role=Role.EMPLOYEE,
            department=sales,
        )

        task = Task(
            title="Mismatched task",
            department=engineering,
            assigned_to=sales_employee,
        )

        with self.assertRaises(Exception):
            task.save()

    def test_mismatched_assignment_via_api_returns_400_not_500(self):
        """Regression test: model-level full_clean() validation errors must
        surface as a clean 400 through the API, not an unhandled 500."""
        engineering = Department.objects.create(name="Engineering")
        sales = Department.objects.create(name="Sales")
        sales_employee = User.objects.create_user(
            username="salesrep",
            password="pass12345",
            role=Role.EMPLOYEE,
            department=sales,
        )
        manager = User.objects.create_user(
            username="mgr", password="pass12345", role=Role.MANAGER
        )
        self.client.force_authenticate(user=manager)

        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Mismatched task",
                "department_id": engineering.id,
                "assigned_to": sales_employee.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assigned_to", response.data)


class TaskPermissionAndScopingTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")
        self.manager = User.objects.create_user(
            username="mgr", password="pass12345", role=Role.MANAGER
        )
        self.alice = User.objects.create_user(
            username="alice",
            password="pass12345",
            role=Role.EMPLOYEE,
            department=self.department,
        )
        self.bob = User.objects.create_user(
            username="bob",
            password="pass12345",
            role=Role.EMPLOYEE,
            department=self.department,
        )
        self.alice_task = Task.objects.create(
            title="Alice's task",
            department=self.department,
            assigned_to=self.alice,
            status=TaskStatus.PENDING,
        )
        self.bob_task = Task.objects.create(
            title="Bob's task",
            department=self.department,
            assigned_to=self.bob,
            status=TaskStatus.PENDING,
        )

    def test_employee_only_sees_own_tasks_in_list(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.get("/api/tasks/")

        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Alice's task"])

    def test_employee_cannot_retrieve_coworkers_task(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.get(f"/api/tasks/{self.bob_task.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_employee_can_update_own_task_status(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.patch(
            f"/api/tasks/{self.alice_task.id}/",
            {"status": TaskStatus.IN_PROGRESS},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alice_task.refresh_from_db()
        self.assertEqual(self.alice_task.status, TaskStatus.IN_PROGRESS)

    def test_employee_cannot_update_other_fields(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.patch(
            f"/api/tasks/{self.alice_task.id}/",
            {"title": "Hacked title"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.alice_task.refresh_from_db()
        self.assertEqual(self.alice_task.title, "Alice's task")

    def test_employee_cannot_create_task(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.post(
            "/api/tasks/",
            {"title": "New task", "department_id": self.department.id},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_delete_task(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.delete(f"/api/tasks/{self.alice_task.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_sees_all_tasks(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get("/api/tasks/")

        titles = sorted(t["title"] for t in response.data["results"])
        self.assertEqual(titles, ["Alice's task", "Bob's task"])

    def test_manager_can_create_and_assign_task(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Set up laptop",
                "department_id": self.department.id,
                "assigned_to": self.alice.id,
                "priority": TaskPriority.HIGH,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_can_edit_any_field(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f"/api/tasks/{self.bob_task.id}/",
            {"title": "Retitled by manager"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskFilteringTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")
        self.manager = User.objects.create_user(
            username="mgr", password="pass12345", role=Role.MANAGER
        )
        Task.objects.create(
            title="Pending high priority",
            department=self.department,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
        )
        Task.objects.create(
            title="Completed low priority",
            department=self.department,
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.LOW,
        )
        self.client.force_authenticate(user=self.manager)

    def test_filter_by_status(self):
        response = self.client.get("/api/tasks/?status=COMPLETED")
        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Completed low priority"])

    def test_filter_by_priority(self):
        response = self.client.get("/api/tasks/?priority=HIGH")
        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Pending high priority"])

    def test_search_by_title(self):
        response = self.client.get("/api/tasks/?search=Completed")
        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Completed low priority"])