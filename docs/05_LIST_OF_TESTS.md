# Pentulz Backend - List of Tests

> **Description**: List of tests for the Pentulz backend

**Maintainer**: Pentulz Team · **Last updated**: 2025-09-02

## Tests

>[!NOTE]
> **56 tests in total**

| Test name | Description | Reason |
| --- | --- | --- |
| `tests/test_static_routes.py` | Verifies root route metadata, `/api/v1/health` status, and `/api/v1/tools` JSON:API shape (type/id/attributes/variants). | Ensure basic availability and stable public contract for static/system endpoints. |
| `tests/test_agents_routes.py` | Mocks service to test `/api/v1/agents` list response conforms to JSON:API and key attributes. | Validate API surface without DB dependency; catch regressions in response formatting. |
| `tests/test_jobs_routes.py` | Mocks service to test `/api/v1/jobs` list response, including `action` structure (`cmd`, `variant`, `args`). | Guarantee job listing format for UI/orchestrator consumers without DB. |
| `tests/test_reports_routes.py` | Mocks service to test `/api/v1/reports` list response and minimal attributes (`name`, `results`). | Keep reports contract stable and decoupled from persistence. |
| `tests/test_report_parsers.py` | Validates parsing of tool outputs (e.g., Nmap, Tshark, FFUF) into normalized JSON. | Ensure parsers produce consistent, consumable structures for reporting/analysis. |
| `tests/test_job_creation.py` | Exercises job creation and related flows around command building/validation. | Prevent invalid job payloads and command assembly regressions. |
| `tests/test_command_validation.py` | Validates tool command templates, arguments, and allowed command generation/validation. | Protect against unsafe or malformed command executions. |

---

Built with ❤️ by Pentulz team. If you need help or find an issue, please open an issue in the repository.