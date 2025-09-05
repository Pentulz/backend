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
  ·
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  Penetration testing orchestration: jobs, agents, and unified parsing.
</p>

## Introduction

Pentulz Backend is a penetration-testing orchestration API built with FastAPI. It provides a modular system for managing security scan jobs, remote agents, and intelligent parsing of tool outputs (Nmap, FFUF, Tshark) into a unified, classified data model. 


Important links: 

- Official website: [https://pentulz.xyz](https://pentulz.xyz)
- Official repository: [https://github.com/Pentulz/Pentulz](https://github.com/Pentulz/Pentulz)
- Frontend repository: [https://github.com/Pentulz/Frontend](https://github.com/Pentulz/frontend)
- Agent repository: [https://github.com/Pentulz/Agent](https://github.com/Pentulz/agent)

> [!NOTE]
> This repository is part of the Pentulz project. To see the full project, please visit the [Pentulz repository](https://github.com/Pentulz/Pentulz).

## Features

- **Job Orchestration**: Queue-based job management with queued/running/completed states
- **Agent Management**: Remote agent registration and communication
- **Modular Tool System**: Pluggable parsers for security tools (Nmap, FFUF, Tshark)
- **Intelligent Classification**: Automatic vulnerability severity classification (critical/high/medium/low/info)
- **Unified Reporting**: Standardized findings format across all tools
- **Async Database**: PostgreSQL via SQLAlchemy 2.x with async support
- **Type Safety**: Typed request/response models with Pydantic
- **API Documentation**: Interactive OpenAPI docs at `/docs` and `/redoc`
- **Comprehensive Testing**: Full test suite with `pytest`

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

- FastAPI
- SQLAlchemy 2.x, PostgreSQL, asyncpg
- Pydantic
- Alembic
- Uvicorn

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Optional: Poetry (recommended) or pip + virtualenv

### Quick Start with Docker (Recommended)

The easiest way to get started is with Docker Compose, which automatically handles database initialization:

```bash
docker compose --profile dev up --build
```

**What happens automatically:**
- PostgreSQL database is created and started
- Database schema is automatically initialized
- Application connects to the database
- API is available at `http://localhost:8000`
- Interactive API docs at `http://localhost:8000/docs`

### Manual Setup (Development)

#### Configuration

Environment variables are read via `pydantic-settings`. Common variables include:

- `ENVIRONMENT` (dev|prod)
- `DATABASE_URL` (e.g., postgres://user:pass@localhost:5432/pentulz)
- `CORS_ALLOW_ORIGINS` (CSV of origins)

Create a `.env` in the project root if needed.

#### Installation

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

#### Database Setup

**Option 1: Automatic initialization (recommended)**
The application will automatically create the database schema on first run if it doesn't exist, if you use the Docker Compose file.

> [!IMPORTANT]
> The seeding of the database is not done automatically, you need to do it manually.

**Option 2: Manual initialization**
You can manually initialize and seed the database using the provided SQL scripts:

```bash
# Initialize database schema
psql "$env:DATABASE_URL" -f scripts/init-db.sql

# Seed with sample data (optional)
psql "$env:DATABASE_URL" -f scripts/seed-db.sql
```

#### Running the Application

```bash
# With Poetry
poetry run uvicorn app.main:app --reload

# With pip
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

>[!IMPORTANT]
> We advice to use the Docker Compose file to start the application.

## Testing

Run tests and coverage:

```bash
pytest -q --cov=app
```

## Linting

Run linting:

```bash
pylint app tests
```

_The linting is considered as failed if the score is below 8.0._

## Project Structure

See [01_PROJECT_STRUCTURE.md](./docs/01_PROJECT_STRUCTURE.md) for details. At a glance:

- `app/main.py`: FastAPI app, middleware, routers, error handlers
- `app/api/v1/*`: API routers for system, health, jobs, reports, agents
- `app/services/*`: Business logic, tool orchestration and intelligent parsers
- `app/services/tools/*`: Modular tool system with BaseTool, ToolManager, and parsers
- `app/models/*`: SQLAlchemy models and ORM base
- `app/schemas/*`: Pydantic models for request/response validation
- `app/core/*`: Configuration, database, response helpers
- `docs/*`: Comprehensive documentation and database UML
- `tests/*`: Unit and integration tests with coverage reporting

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

>[!NOTE]
> To have a better understanding of the project, you can read the documentation in the [docs](./docs) folder. (How to add a new tool, how to deploy, project structure, etc.)

---

Made with ❤️ by the Pentulz team.
