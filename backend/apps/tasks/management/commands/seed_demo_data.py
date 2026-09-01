from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.departments.models import Department
from apps.tasks.choices import TaskPriority, TaskStatus
from apps.tasks.models import Task
from apps.users.choices import Role
from apps.users.models import User

DEMO_PASSWORD = "DemoPass123!"

DEPARTMENT_NAMES = ["Engineering", "Sales", "Marketing", "Operations"]


class Command(BaseCommand):
    help = (
        "Populate the database with demo departments, a manager, an admin, "
        "several employees, and a spread of tasks across statuses, "
        "priorities, and due dates. Safe to re-run - departments/users are "
        "created with get_or_create, and demo tasks are cleared and "
        "recreated each run so the data always looks fresh."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        departments = self._seed_departments()
        admin, manager, employees = self._seed_users(departments)
        task_count = self._seed_tasks(departments, employees)

        self.stdout.write(self.style.SUCCESS("\nDemo data ready.\n"))
        self.stdout.write(f"  Departments: {len(departments)}")
        self.stdout.write(f"  Employees:   {len(employees)}")
        self.stdout.write(f"  Tasks:       {task_count}\n")
        self.stdout.write("Demo login credentials (all use the same password):")
        self.stdout.write(f"  Admin    - username: {admin.username}   password: {DEMO_PASSWORD}")
        self.stdout.write(f"  Manager  - username: {manager.username}   password: {DEMO_PASSWORD}")
        for employee in employees:
            self.stdout.write(
                f"  Employee - username: {employee.username:<10} password: {DEMO_PASSWORD}"
            )

    def _seed_departments(self):
        departments = {}
        for name in DEPARTMENT_NAMES:
            department, _ = Department.objects.get_or_create(name=name)
            departments[name] = department
        return departments

    def _seed_users(self, departments):
        hashed_password = make_password(DEMO_PASSWORD)

        admin, _ = User.objects.update_or_create(
            username="admin",
            defaults={
                "email": "admin@demo.local",
                "role": Role.ADMIN,
                "department": departments["Engineering"],
                "is_staff": True,
                "is_superuser": True,
                "password": hashed_password,
            },
        )

        manager, _ = User.objects.update_or_create(
            username="manager",
            defaults={
                "email": "manager@demo.local",
                "role": Role.MANAGER,
                "department": departments["Engineering"],
                "password": hashed_password,
            },
        )

        employee_specs = [
            ("alice", "Engineering"),
            ("bob", "Engineering"),
            ("carol", "Sales"),
            ("dave", "Marketing"),
            ("erin", "Operations"),
        ]

        employees = []
        for username, department_name in employee_specs:
            employee, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": f"{username}@demo.local",
                    "role": Role.EMPLOYEE,
                    "department": departments[department_name],
                    "password": hashed_password,
                },
            )
            employees.append(employee)

        return admin, manager, employees

    def _seed_tasks(self, departments, employees):
        # Clear only demo tasks (identified by belonging to a demo employee
        # or a demo department) so re-running this command doesn't pile up
        # duplicates, without touching unrelated data a user might have
        # created by hand.
        Task.objects.filter(department__in=departments.values()).delete()

        today = timezone.localdate()

        by_username = {employee.username: employee for employee in employees}

        task_specs = [
            # title, department, assigned_to, status, priority, due_date offset (days from today)
            ("Set up development environment", "Engineering", "alice", TaskStatus.COMPLETED, TaskPriority.HIGH, -5),
            ("Review pull request backlog", "Engineering", "alice", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 2),
            ("Fix login page responsiveness bug", "Engineering", "bob", TaskStatus.PENDING, TaskPriority.HIGH, -2),
            ("Write API documentation", "Engineering", "bob", TaskStatus.PENDING, TaskPriority.LOW, 10),
            ("Upgrade CI pipeline", "Engineering", None, TaskStatus.PENDING, TaskPriority.MEDIUM, 14),
            ("Prepare Q3 sales report", "Sales", "carol", TaskStatus.IN_PROGRESS, TaskPriority.HIGH, 1),
            ("Follow up with enterprise leads", "Sales", "carol", TaskStatus.PENDING, TaskPriority.HIGH, -1),
            ("Update CRM contact records", "Sales", "carol", TaskStatus.COMPLETED, TaskPriority.LOW, -7),
            ("Launch spring email campaign", "Marketing", "dave", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 3),
            ("Design new landing page banner", "Marketing", "dave", TaskStatus.PENDING, TaskPriority.MEDIUM, 6),
            ("Audit social media analytics", "Marketing", None, TaskStatus.COMPLETED, TaskPriority.LOW, -10),
            ("Renew office supply contract", "Operations", "erin", TaskStatus.PENDING, TaskPriority.LOW, 20),
            ("Schedule quarterly safety training", "Operations", "erin", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 4),
            ("Resolve overdue vendor invoice", "Operations", "erin", TaskStatus.PENDING, TaskPriority.HIGH, -3),
        ]

        tasks = []
        for title, department_name, username, status, priority, offset in task_specs:
            tasks.append(
                Task(
                    title=title,
                    description=f"Demo task seeded for the {department_name} department.",
                    department=departments[department_name],
                    assigned_to=by_username.get(username) if username else None,
                    status=status,
                    priority=priority,
                    due_date=today + timedelta(days=offset),
                )
            )

        Task.objects.bulk_create(tasks)
        return len(tasks)