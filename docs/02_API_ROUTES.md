# Pentulz Backend - API Routes

> **Description**: Overview of all REST API endpoints exposed by the Pentulz backend

**Maintainer**: Pentulz Team · **Last updated**: 2025-09-05

## Base URL

All API endpoints are prefixed with `/api/v1/` (configurable in the [config.py](../app/core/config.py) file)

## Endpoints

### Health

**GET** `/health` - System health check
- Returns: `{"status": "ok"}`

### Agents

**GET** `/agents` - Get all agents with their jobs
- Returns: List of agents with associated jobs

**POST** `/agents` - Create a new agent
- Body: `AgentCreate` schema
- Returns: Created agent data

**GET** `/agents/{agent_id}` - Get specific agent by ID
- Parameters: `agent_id` (UUID)
- Returns: Agent data with jobs

**PATCH** `/agents/{agent_id}` - Update an agent
- Parameters: `agent_id` (UUID)
- Body: `AgentUpdate` schema
- Returns: Updated agent data

**DELETE** `/agents/{agent_id}` - Delete an agent
- Parameters: `agent_id` (UUID)
- Returns: Deletion confirmation


### Jobs

**GET** `/jobs` - Get all jobs
- Returns: List of all jobs

**POST** `/jobs` - Create a new job
- Body: `JobCreate` schema
- Returns: Created job data

**GET** `/jobs/{job_id}` - Get specific job by ID
- Parameters: `job_id` (UUID)
- Returns: Job data

**PATCH** `/jobs/{job_id}` - Update a job
- Parameters: `job_id` (UUID)
- Body: `JobUpdate` schema
- Returns: Updated job data

**DELETE** `/jobs/{job_id}` - Delete a job
- Parameters: `job_id` (UUID)
- Returns: Deletion confirmation

### Reports

**GET** `/reports` - Get all reports
- Returns: List of all reports

**POST** `/reports` - Create a new report
- Body: `ReportCreate` schema
- Returns: Created report data

**GET** `/reports/{report_id}` - Get specific report by ID
- Parameters: `report_id` (UUID)
- Returns: Report data

**PATCH** `/reports/{report_id}` - Update a report
- Parameters: `report_id` (UUID)
- Body: `ReportUpdate` schema
- Returns: Updated report data

**DELETE** `/reports/{report_id}` - Delete a report
- Parameters: `report_id` (UUID)
- Returns: Deletion confirmation

### Protected Agent Endpoints (only for agents, with token verification)

**GET** `/protected/self` - Get current agent information
- Headers: `Authorization: Bearer <agent_token>`
- Returns: Current agent data

**PATCH** `/protected/self` - Update current agent
- Headers: `Authorization: Bearer <agent_token>`
- Body: `AgentUpdate` schema
- Returns: Updated agent data

**GET** `/protected/jobs` - Get jobs for current agent
- Headers: `Authorization: Bearer <agent_token>`
- Returns: List of jobs for the authenticated agent

**PATCH** `/protected/jobs/{job_id}` - Update a job (agent-protected)
- Headers: `Authorization: Bearer <agent_token>`
- Parameters: `job_id` (UUID)
- Body: `JobUpdate` schema
- Returns: Updated job data

### System Tools

**GET** `/tools` - Get available penetration testing tools
- Returns: List of supported tools by Pentulz

## Response Format

All endpoints return responses in a consistent format using the standardized response schemas defined in `app/schemas/response.py`.

You can also see the response format using OpenAPI documentation at `/docs` and `/redoc`, after starting the server (`docker compose --profile dev up`).

## Authentication

Some endpoints (protected ones) require agent authentication using a Bearer token in the Authorization header:
- Format: `Authorization: Bearer <agent_token>`
- These endpoints are marked as "Protected Agent Endpoints" above

## Error Handling

- **400** - Bad Request (invalid input)
- **401** - Unauthorized (invalid or missing token)
- **404** - Not Found (resource not found)
- **422** - Unprocessable Entity (validation error)
- **500** - Internal Server Error

---

Built with ❤️ by the Pentulz team. If you need help or find an issue, please open an issue in the repository.