# Pentulz Backend - Project Structure

> **Description**: Explanation of the repository layout and key modules

**Maintainer**: Pentulz Team · **Last updated**: 2025-09-05

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── agents.py
│   │       ├── health.py
│   │       ├── jobs.py
│   │       ├── protected_agents.py
│   │       ├── reports.py
│   │       └── system.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── response.py
│   ├── models/
│   │   ├── agents.py
│   │   ├── associations.py
│   │   ├── base.py
│   │   ├── jobs.py
│   │   └── reports.py
│   ├── schemas/
│   │   ├── agent_auth.py
│   │   ├── agents.py
│   │   ├── jobs.py
│   │   ├── reports.py
│   │   └── response_models.py
│   ├── services/
│   │   ├── agents.py
│   │   ├── jobs.py
│   │   ├── reports.py
│   │   └── tools/
│   │       ├── ffuf/
│   │       │   ├── parser.py
│   │       │   ├── sample.json
│   │       │   └── tool.py
│   │       ├── nmap/
│   │       │   ├── parser.py
│   │       │   ├── sample.xml
│   │       │   └── tool.py
│   │       ├── tshark/
│   │       │   ├── parser.py
│   │       │   ├── sample.json
│   │       │   └── tool.py
│   │       ├── tool_manager.py
│   │       ├── tool_parser.py
│   │       └── tool.py
│   ├── utils/
│   │   ├── auth.py
│   │   └── uuid.py
│   └── main.py
├── docs/
│   ├── 01_PROJECT_STRUCTURE.md
│   ├── 02_API_ROUTES.md
│   ├── 03_ADDING_NEW_TOOL.md
│   ├── 04_DEPLOYMENT.md
│   ├── 05_LIST_OF_TESTS.md
│   └── assets/
│       ├── DATABASE_UML.drawio
│       ├── DATABASE_UML.png
│       └── workflows.png
├── scripts/
│   ├── init-db.sql
│   └── seed-db.sql
├── tests/
│   ├── test_agents_routes.py
│   ├── test_command_validation.py
│   ├── test_job_creation.py
│   ├── test_jobs_routes.py
│   ├── test_report_parsers.py
│   ├── test_reports_routes.py
│   └── test_static_routes.py
└── ... (other files)
```

## Directory Descriptions

### `/app`

Main application package containing all the backend code.

### `/app/api/v1/`

REST API endpoints organized by version. Contains:

- **`agents.py`** - Agent management endpoints (CRUD operations)
- **`health.py`** - System health check endpoint
- **`jobs.py`** - Job management endpoints (CRUD operations)
- **`protected_agents.py`** - Protected agent endpoints (requires authentication)
- **`reports.py`** - Report management endpoints (CRUD operations)
- **`system.py`** - System tools and utilities endpoints

### `/app/core/`

Core application infrastructure:

- **`config.py`** - Application configuration, environment variables, and settings
- **`database.py`** - Database connection and session management
- **`exceptions.py`** - Custom exception classes for error handling
- **`response.py`** - Standardized response models and utilities

### `/app/models/`

SQLAlchemy ORM models defining the database schema:

- **`agents.py`** - Agent model (penetration testing probes)
- **`associations.py`** - Association tables for many-to-many relationships
- **`base.py`** - Base model class with common fields and methods
- **`jobs.py`** - Job model (scan tasks)
- **`reports.py`** - Report model (scan outputs and results)

### `/app/schemas/`

Pydantic models for API request/response validation and serialization:

- **`agent_auth.py`** - Authentication schemas for agents
- **`agents.py`** - Agent-related request/response schemas
- **`jobs.py`** - Job-related request/response schemas
- **`reports.py`** - Report-related request/response schemas
- **`response_models.py`** - Standardized response model schemas

### `/app/services/`

Business logic layer containing service classes:

- **`agents.py`** - Agent management service
- **`jobs.py`** - Job orchestration service
- **`reports.py`** - Report processing service

### `/app/services/tools/`

Pluggable system for penetration testing tools:

- **`ffuf/`** - FFuF web fuzzer tool implementation
- **`nmap/`** - Nmap network scanner tool implementation
- **`tshark/`** - TShark network protocol analyzer tool implementation
- **`tool_manager.py`** - Tool registry and management
- **`tool_parser.py`** - Generic tool output parser
- **`tool.py`** - Base tool interface and abstract classes

### `/app/utils/`

Utility functions and helpers:

- **`auth.py`** - Authentication utilities and token verification
- **`uuid.py`** - UUID validation and conversion utilities

### `/docs/`

Project documentation and guides:

- **`01_PROJECT_STRUCTURE.md`** - Project structure overview
- **`02_API_ROUTES.md`** - API endpoints documentation
- **`03_ADDING_NEW_TOOL.md`** - Guide for adding new penetration testing tools
- **`04_DEPLOYMENT.md`** - Deployment instructions
- **`05_LIST_OF_TESTS.md`** - Test suite documentation
- **`assets/`** - Documentation assets (diagrams, images)

### `/scripts/`

SQL scripts for database initialization and seeding:

- **`init-db.sql`** - Database initialization script
- **`seed-db.sql`** - Database seeding script

### `/tests/`

Test suite with unit and integration tests:

- **`test_agents_routes.py`** - Agent API endpoints tests
- **`test_command_validation.py`** - Command validation tests
- **`test_job_creation.py`** - Job creation tests
- **`test_jobs_routes.py`** - Job API endpoints tests
- **`test_report_parsers.py`** - Report parser tests
- **`test_reports_routes.py`** - Report API endpoints tests
- **`test_static_routes.py`** - Static routes tests

_More information in [05_LIST_OF_TESTS.md](./docs/05_LIST_OF_TESTS.md)_

---

Built with ❤️ by the Pentulz team. If you need help or find an issue, please open an issue in the repository.
