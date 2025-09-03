# Pentulz Backend - Project Structure

> **Description**: Explanation of the repository layout and key modules

**Maintainer**: Pentulz Team · **Last updated**: 2025-09-02

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
│   │       └── <tool_name>/
│   │           └── tool.py
│   │           └── parser.py
│   │           └── sample.*
│   │       └── ...
│   │       └── tool_manager.py
│   │       └── tool_parser.py
│   │       └── tool.py
│   └── utils/
│   └── main.py
├── docs/
│   └── assets/
│   └── ...
├── scripts/
│   └── init-db.sql
│   └── seed-db.sql
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

### `/app/utils/`

Utility functions and helpers.

### `/docs/`

Project documentation and guides.

### `/scripts/`

SQL scripts for database initialization and seeding.

### `/tests/`

Test suite with unit and integration tests.

---

Built with ❤️ by the Pentulz team. If you need help or find an issue, please open an issue in the repository.
