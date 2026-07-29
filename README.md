# Employee Task Manager

A full-stack Employee Task Management system built using Django REST Framework, AngularJS, JWT Authentication, and SQLite (development).

## Features

- User Registration
- JWT Authentication
- Department Management
- Task CRUD Operations
- Pagination
- Filtering
- Role-based Permissions
- RESTful API
- AngularJS Frontend

## Tech Stack

### Backend
- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite (Development)
- Django Filters

### Frontend
- AngularJS
- HTML
- CSS
- JavaScript

## Project Structure

backend/
frontend/

## API Endpoints

POST /api/auth/login/

POST /api/auth/refresh/

GET /api/tasks/

POST /api/tasks/

PUT /api/tasks/{id}/

DELETE /api/tasks/{id}/

## Authentication

JWT Authentication

Access Token

Refresh Token

## Installation

```bash
git clone <repo>

cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver