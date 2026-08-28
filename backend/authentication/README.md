# ProjectPulse AI Authentication Backend

This repository contains the backend authentication, user, and team management module for ProjectPulse AI.

## Requirements

- Python 3.12+
- Docker Desktop
- PostgreSQL (if running without Docker)
- Git

## Project Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── db/
│   │   ├── database.py
│   │   └── base.py
│   ├── models/
│   │   ├── user.py
│   │   ├── team.py
│   │   └── team_member.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── team.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── teams.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── team_service.py
│   └── utils/
│       └── validators.py
├── alembic/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup with Docker

1. Clone the repository.
2. Create a `.env` file from `.env.example`.
3. Run:

```bash
git clone <repo-url>
cd backend/authentication
docker compose up --build
```

This starts:

- FastAPI on http://localhost:8000
- PostgreSQL on localhost:5432

## Environment Variables

Copy `.env.example` to `.env` and update the values:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/projectpulse
JWT_SECRET_KEY=CHANGE_THIS_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
POSTGRES_DB=projectpulse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
```

Do not commit `.env` to GitHub.

## Database Migration

Run migrations with:

```bash
alembic upgrade head
```

To roll back one revision:

```bash
alembic downgrade -1
```

## API Documentation

FastAPI Swagger UI is available at:

```text
http://localhost:8000/docs
```

Alternative docs at:

```text
http://localhost:8000/redoc
```

## Authentication Flow

```text
Register
   ↓
Hash Password
   ↓
PostgreSQL
   ↓
Login
   ↓
JWT
   ↓
Protected API
   ↓
Role Authorization
```

## API Endpoints

### Authentication

- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### User APIs

- GET /api/users/me
- GET /api/users/{user_id}
- GET /api/users
- PUT /api/users/me

### Team APIs

- POST /api/teams
- GET /api/teams
- GET /api/teams/{team_id}
- PUT /api/teams/{team_id}
- DELETE /api/teams/{team_id}
- POST /api/teams/{team_id}/members/{user_id}
- GET /api/teams/{team_id}/members
- DELETE /api/teams/{team_id}/members/{user_id}

## Postman Testing Sequence

1. Register
2. Login
3. Copy JWT
4. GET /api/auth/me
5. Create Team
6. Add User
7. Get Team Members
8. Test unauthorized access

Example register request:

```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "Teja",
  "email": "teja@example.com",
  "password": "StrongPassword123",
  "role": "TEAM_MEMBER"
}
```

Example login request:

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=teja@example.com&password=StrongPassword123
```

Example bearer token header:

```http
Authorization: Bearer <jwt-token>
```

## Backend Integration Contract

The authentication module is the single source of truth for users.

### User table

```text
users.id
users.name
users.email
users.role
```

The Project/Task module can safely reference:

```text
users.id
```

Example:

```text
tasks.assigned_to -> users.id
projects.created_by -> users.id
```

Do not create duplicate user records in the Project/Task module.

## Security Notes

- Passwords are never stored in plain text.
- Password hashes are never returned by API responses.
- JWT secrets are kept in environment variables.
- Authorization is checked on the backend for every protected request.

## Local Run (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# On Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn backend.app.main:app --reload
```

## Running Tests

```bash
pytest
```

## Git Commit Recommendations

```bash
feat: initialize authentication backend
feat: add PostgreSQL database configuration
feat: add user model and migration
feat: implement password hashing
feat: implement user registration
feat: implement JWT login
feat: implement role based authorization
feat: add team management
feat: add authentication tests
feat: add Docker development environment
docs: add authentication setup guide
```
