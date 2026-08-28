# ProjectPulse AI Project/Task Backend

FastAPI APIs for projects, project members, tasks, milestones, dependencies, and dashboards. Authentication remains owned by the authentication backend.

## Run with Docker

docker compose up --build
```powershell
Copy-Item .env.example .env
# Use projectpulse-db (the current shared container name) or the final shared DB service name.
# Do not use localhost inside the API container.
docker compose up --build
```

This Compose file starts only the `project-api` service. It does not create PostgreSQL, publish port 5432, or run a second database. It joins the existing external Docker network `authentication_default`, currently used by `projectpulse-auth-api` and `projectpulse-db`. The API exposes container port 8000 for internal network access and publishes no host port, so it cannot collide with authentication on host port 8000.

## Run locally

Use Python 3.12+, the existing shared PostgreSQL database, and a `.env` containing a PostgreSQL `DATABASE_URL`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger and ReDoc are available at `/docs` and `/redoc`.

## Authentication integration

Protected routes require `Authorization: Bearer <JWT>`. `app.core.auth.get_current_user` is an integration adapter that decodes the same JWT claims as the sibling authentication service (`sub` and `role`). It does not accept `X-User-ID`, create users, or implement a second authentication system. In the merged deployment, this adapter can be replaced with a direct import of the authentication team's provider while retaining the same `CurrentUser` contract.

The project/task migration assumes the authentication migration has already created `users(id)`. It deliberately does not create a second users table. This repository cannot inspect or verify the external authentication schema directly, so integration must confirm that the existing table exposes an integer-compatible `users.id` before running the migration.

`DATABASE_URL` must use the shared PostgreSQL Docker service/container name, not `localhost`, when this API runs in Docker. The `.env.example` value `db` is only a placeholder; with the currently running network use `projectpulse-db`, or use the final database service name after the Compose files are combined. `JWT_SECRET_KEY` and `JWT_ALGORITHM` must exactly match the authentication backend because that backend issues the tokens and this backend only verifies `sub` and `role`.

## API groups

- Projects: `/api/projects`
- Project Members: `/api/projects/{project_id}/members`
- Tasks: `/api/projects/{project_id}/tasks` and `/api/tasks/{task_id}`
- Milestones: `/api/projects/{project_id}/milestones` and `/api/milestones/{milestone_id}`
- Dependencies: `/api/tasks/{task_id}/dependencies`
- Dashboard: `/api/projects/{project_id}/dashboard`

Roles are `ADMIN`, `PROJECT_MANAGER`, `TEAM_MEMBER`, and `VIEWER`. Admins and project managers can manage projects; team members can work within projects they belong to; viewers have read-only access to projects they belong to.

## Migrations

```powershell
alembic upgrade head
alembic downgrade -1
```

Migration `001_project_task_schema` creates `projects`, `project_members`, `milestones`, `tasks`, and `dependencies`, with foreign keys to the authentication-owned `users` table.

## Tests

Tests use a PostgreSQL test database configured through `TEST_DATABASE_URL` (or `DATABASE_URL`). Production and Docker configuration also require PostgreSQL.

```powershell
python -m pytest -q
```

The test suite covers project lifecycle, membership conflicts, task and milestone operations, dependency validation, dashboard calculations, authentication failures, and viewer restrictions.

Never commit `.env`, `.venv`, `__pycache__`, or `.pytest_cache`.
