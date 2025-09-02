# Pentulz Backend - Adding a New Tool

> **Description**: How to implement, register, and validate a new tool integration.

**Maintainer**: Pentulz Team · **Last updated**: 2025-09-02

#### Overview

- Implement a tool class extending `BaseTool`
- Implement a parser extending `BaseParser`
- Register the tool in `ToolManager`
- (Optional) Add a sample output file for tests

> [!IMPORTANT]
> **Result format contract (must comply)**

Every parser must return a dict with the following shape:

```json
{
  "findings": [
    {
      "id": "string",
      "severity": "critical|high|medium|low|info",
      "title": "string",
      "description": "string",
      "target": "string",
      "agent_id": "string",
      "timestamp": "ISO-8601 string"
    }
  ],
  "statistics": { "any": "non-negative numbers or nested dicts" }
}
```

- `findings` is a non-empty list when meaningful data is present; each finding must include all fields above.
- `severity` must be one of: `critical`, `high`, `medium`, `low`, `info`.
- `timestamp` should be ISO-8601 (use `datetime.now().isoformat()`).
- `statistics` must be a dict and may vary per tool (e.g., `open_ports`, `total_hosts`, `status_codes`, etc.). Use non-negative numeric values; nested dicts are allowed.

Tests assert this contract. See `tests/test_report_parsers.py` for details.

### 1. Minimal structure

Create a new directory for your tool:

```
app/services/tools/<your_tool>/
  ├─ tool.py      # Tool definition (commands, validation, parse entrypoint)
  ├─ parser.py    # Output parser to normalized findings/stats
  └─ sample.*     # Optional sample output (xml/json/txt) for tests
```

### 2. Implement the Tool class

File: `app/services/tools/<your_tool>/tool.py`

```python
from typing import Any, Dict, List
from app.services.tools.tool import BaseTool, CommandTemplate, ArgumentDefinition


class MyTool(BaseTool):
    @property
    def name(self) -> str:
        return "mytool"

    @property
    def description(self) -> str:
        return "MyTool integration"

    @property
    def get_base_command(self) -> str:
        return "mytool"

    @property
    def get_version_arg(self) -> str:
        return "--version"

    @property
    def export_format(self) -> str:
        # e.g., "json" | "xml" | "txt"
        return "json"

    @property
    def export_arguments(self) -> List[str]:
        # Arguments to force export to stdout in the chosen format
        return ["--output", "-"]

    @property
    def command_templates(self) -> List[CommandTemplate]:
        return [
            CommandTemplate(
                id="default",
                name="Default Scan",
                base_command="mytool",
                arguments=["scan", "{target}"],
                description="Run default scan on a target",
                argument_definitions=[
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target host or URL",
                        placeholder="example.com",
                    ),
                ],
            ),
        ]

    def parse_results(self, raw_output: str, command_used: str, agent_id: str | None = None) -> Dict[str, Any]:
        from app.services.tools.mytool.parser import MyToolParser

        parser = MyToolParser()
        return parser.parse_single_result(raw_output, command_used, agent_id)

    def validate_command(self, command_args: List[str]) -> bool:
        # Reuse shared validation logic; ensure base command matches
        return self._validate_command_common(command_args, "mytool")

    # Optional: override placeholder validation for stricter checks
    # def _validate_placeholder(self, value: str, placeholder_name: str) -> bool:
    #     return True
```

Key points:

- `command_templates` define allowed shapes of commands with placeholders like `{target}`
- `export_arguments` must direct the tool to print the structured output (XML/JSON) to stdout
- `validate_command` should call `_validate_command_common(args, "<base>")`
- `parse_results` must return a normalized dict: `{ "findings": [...], "statistics": {...} }`

> [!TIP]
> See `app/services/tools/nmap/tool.py` for a complete example.

### 3. Implement the Parser

File: `app/services/tools/<your_tool>/parser.py`

```python
from typing import Dict
from app.services.tools.tool_parser import BaseParser


class MyToolParser(BaseParser):
    def parse_single_result(self, raw_output: str, command_used: str, agent_id: str | None = None) -> Dict:
        # 1) Parse raw_output (json/xml/txt)
        # 2) Build findings via self._create_finding(...)
        # 3) Summarize stats via self._count_by_severity or custom logic
        findings = []
        # ... parse and append findings ...

        return {
            "findings": findings,
            "statistics": {
                "open_ports": 0,  # example
            },
        }
```

Helpers available on `BaseParser`:

- `_create_finding(id=..., title=..., description=..., severity=..., target=..., agent_id=..., timestamp=...)`
- `_count_by_severity(findings)` returns a dict of counts per severity

> [!TIP]
> See `app/services/tools/nmap/parser.py` for a production-ready implementation.

### 4. Register the Tool

Add your tool to `ToolManager._register_default_tools()` so it is discoverable by name and variants:

```python
from app.services.tools.mytool.tool import MyTool
self.tools["mytool"] = MyTool()
```

File: `app/services/tools/tool_manager.py`

This powers:

- Listing tools and variants (`get_available_tools`)
- Validating commands (`validate_command`)
- Parsing results (`parse_results`)
- Building variant commands (`build_command_from_variant`)

### 5. Validating and building commands

- Validation checks that the provided args match a `CommandTemplate`
- Use `build_command_from_variant(tool, variant_id, custom_args)` to render placeholders to actual args

Example:

```python
manager.build_command_from_variant(
    "mytool",
    "default",
    {"target": "example.com"}
)
# => ["scan", "example.com"]
```

### 6. Testing locally

- Put a `sample.json` or `sample.xml` in your tool folder
- Write tests similar to `tests/test_report_parsers.py`
- Manual check: instantiate `ToolManager()` and call `parse_results("mytool", sample_output, "mytool ...")`

#### Security and reliability notes

- Keep command templates strict; avoid passing arbitrary flags that could be unsafe
- Validate placeholders (IPs, ports, URLs) by overriding `_validate_placeholder` when needed
- Ensure parsers are resilient to malformed outputs; handle exceptions and return consistent structures

---

Built with ❤️ by the Pentulz team. If you need help or find an issue, please open an issue in the repository.


