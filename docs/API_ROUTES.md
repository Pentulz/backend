# API Routes Documentation

This document describes the REST API endpoints available in the Pentulz backend.

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

**GET** `/agents/{agent_id}/jobs` - Get jobs for specific agent
- Parameters: `agent_id` (UUID)
- Query params: `completed` (boolean) - filter by completion status
- Returns: List of jobs for the agent

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

### System Tools

**GET** `/tools` - Get available penetration testing tools
- Returns: List of supported tools

## Response Format

All endpoints return responses in a consistent format using the standardized response schemas defined in `app/schemas/response.py`.

You can see examples of the responses in [API_RESPONSES.md](./API_RESPONSES.md)

## Error Handling

- **400** - Bad Request (invalid input)
- **404** - Not Found (resource not found)
- **500** - Internal Server Error