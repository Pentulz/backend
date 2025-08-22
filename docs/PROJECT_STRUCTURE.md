# Pentulz Backend - Project Structure

This document explains the organization of the Pentulz backend codebase.

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── health.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   └── tools/
│   └── main.py
├── docs/
├── tests/
└── ... (other files)
```

## Directory Descriptions

### `/app`

Main application package containing all the backend code.

### `/app/api/v1/`

REST API endpoints organized by version. Contains:

- **`health.py`** - System health check endpoint

### `/app/core/`

Core application infrastructure:

- **`config.py`** - Application configuration, environment variables, and settings

### `/app/models/`

SQLAlchemy ORM models defining the database schema for:

- Agents (penetration testing probes)
- Jobs (scan tasks)
- Results (scan outputs)

### `/app/schemas/`

Pydantic models for API request/response validation and serialization.

### `/app/services/`

Business logic layer containing service classes that handle:

- Agent management
- Job orchestration
- Result processing

### `/app/services/tools/`

Pluggable system for penetration testing tools:

- Tool implementations (nmap, gobuster, ffuf, etc.)
- Output parsers for normalizing scan results
- Registry pattern for easy tool registration

### `/docs/`

Project documentation and guides.

### `/tests/`

Test suite with unit and integration tests.
