<p align="center">
  <a href="https://github.com/Pentulz/Pentulz">
    <img src="https://github.com/Pentulz/.github/blob/main/public/images/logo.png?raw=true" alt="Pentulz" width="200">
  </a>
</p>
<h1 align="center">BACKEND</h1>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.116.x-009688?logo=fastapi&logoColor=white" />
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-13%2B-4169E1?logo=postgresql&logoColor=white" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" />
</p>

<p align="center">
  <a href="#introduction">Introduction</a>
  ·
  <a href="#features">Features</a>
  ·
  <a href="#documentation">Documentation</a>
  ·
  <a href="#database-uml">Database UML</a>
  ·
  <a href="#tech-stack">Tech Stack</a>
  ·
  <a href="#getting-started">Getting Started</a>
  ·
  <a href="#testing">Testing</a>
  ·
  <a href="#linting">Linting</a>
</p>

<p align="center">
  Penetration testing orchestration: jobs, agents, and unified parsing.
</p>

## Introduction

Pentulz Backend is a penetration-testing orchestration API built with FastAPI. It manages scan jobs, agents, and parsing of tool outputs (e.g., Nmap, FFUF, Tshark) into a unified data model. It is the backbone of the communication between the Pentulz Frontend and the Pentulz Agent.

Important links: 

- Official website: [https://pentulz.xyz](https://pentulz.xyz)
- Official repository: [https://github.com/Pentulz/Pentulz](https://github.com/Pentulz/Pentulz)
- Frontend repository: [https://github.com/Pentulz/Frontend](https://github.com/Pentulz/Pentulz-Frontend)
- Agent repository: [https://github.com/Pentulz/Agent](https://github.com/Pentulz/Pentulz-Agent)

> [!NOTE]
> This repository is part of the Pentulz project. To see the full project, please visit the [Pentulz repository](https://github.com/Pentulz/Pentulz).

## Features

- Orchestrated job management with queued/running/completed states
- Agent management
- Tool execution model with pluggable parsers (Nmap, FFUF, Tshark)
- PostgreSQL via SQLAlchemy 2.x (async)
- Typed request/response models with Pydantic
- Consistent API error handling
- OpenAPI docs at `/docs` and `/redoc`
- Tests with `pytest`

## Documentation

- Project structure: [01_PROJECT_STRUCTURE.md](./docs/01_PROJECT_STRUCTURE.md)
- API routes: [02_API_ROUTES.md](./docs/02_API_ROUTES.md)
- Adding a new tool: [03_ADDING_NEW_TOOL.md](./docs/03_ADDING_NEW_TOOL.md)
- Deployment guide: [04_DEPLOYMENT.md](./docs/04_DEPLOYMENT.md)
- List of tests: [05_LIST_OF_TESTS.md](./docs/05_LIST_OF_TESTS.md)

## Database UML

The current database schema is illustrated below. The source diagram is available as a Draw.io file.

![Database UML](./docs/assets/DATABASE_UML.png)

- Source: [here](./docs/assets/DATABASE_UML.drawio)
- SQL schema: [here](./scripts/SQL_SCHEMA.sql)

## Tech Stack

- FastAPI, Starlette
- SQLAlchemy 2.x, PostgreSQL, asyncpg
- Pydantic, pydantic-settings
- Alembic
- Uvicorn
- Pytest, httpx

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Optional: Poetry (recommended) or pip + virtualenv

### Configuration

Environment variables are read via `pydantic-settings`. Common variables include:

- `ENVIRONMENT` (dev|prod)
- `DATABASE_URL` (e.g., postgres://user:pass@localhost:5432/pentulz)
- `CORS_ALLOW_ORIGINS` (CSV of origins)

Create a `.env` in the project root if needed.

### Installation

Using Poetry:

```bash
poetry install
```

Using pip:

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Database

You can initialize and seed the database using the provided SQL scripts in `scripts/`.

```bash
# Example with psql
psql "$env:DATABASE_URL" -f scripts/init-db.sql
psql "$env:DATABASE_URL" -f scripts/seed-db.sql
```

### Docker

To run with Docker Compose:

```bash
docker compose --profile dev up --build
```

_When building the services for the first time, the database will be initialized and seeded with the provided SQL scripts._

## Testing

Run tests and coverage:

```bash
pytest -q --cov=app --cov-report=term-missing
```

## Linting

Run linting:

```bash
pylint app tests
```

## Project Structure

See [01_PROJECT_STRUCTURE.md](./docs/01_PROJECT_STRUCTURE.md) for details. At a glance:

- `app/main.py`: FastAPI app, middleware, routers, error handlers
- `app/api/v1/*`: API routers for system, health, jobs, reports, agents
- `app/services/*`: Business logic, tool orchestration and parsers
- `app/models/*`: SQLAlchemy models and ORM base
- `app/schemas/*`: Pydantic models
- `app/core/*`: configuration, database, response helpers
- `docs/*`: documentation and database UML
- `tests/*`: unit and integration tests

## Useful Links

- FastAPI documentation: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- Pydantic documentation: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)
- SQLAlchemy documentation: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)

---

Made with ❤️ by the Pentulz team.
