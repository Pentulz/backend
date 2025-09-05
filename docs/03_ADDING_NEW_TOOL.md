# Pentulz Backend - Modular Tool System

> **Description**: Complete guide to understand and implement new tools in the Pentulz modular system.

**Maintainer**: Pentulz Team · **Last updated**: 2025-09-05

## Modular System Overview

The Pentulz modular system allows easy integration of new pentesting tools while maintaining a consistent and secure architecture. It consists of several layers:

### Main Components

1. **BaseTool** (in `app/services/tools/tool.py`): Abstract interface defining the tool contract
2. **ToolManager** (in `app/services/tools/tool_manager.py`): Central manager that orchestrates all tools
3. **BaseParser** (in `app/services/tools/tool_parser.py`): Interface for normalizing tool results
4. **CommandTemplate** (in `app/services/tools/tool.py`): Command validation and construction system

### Execution Flow

1. An **Agent** receives a **Job** with a specific action
2. The **ToolManager** validates the command and builds the complete command
3. The agent executes the tool and returns raw results
4. When a report is generated, the corresponding **Parser** normalizes results to standard format
5. Results are stored in the `Reports` table and can be consulted via the API

## Adding a New Tool

To add a new tool to the system, you need to:

1. Implement a tool class extending `BaseTool`
2. Implement a parser extending `BaseParser`
3. Register the tool in `ToolManager`
4. (Optional) Add a sample file for tests

## Result Format Contract

> [!IMPORTANT]
> **Standardized Output Format (Required)**

All parsers must return a dictionary with the following structure:

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

### Key Responsibilities of Parsers

**Vulnerability Classification**: Parsers are responsible for intelligently classifying vulnerabilities based on their content and context. This is crucial for:

- **Risk Assessment**: Proper severity levels help prioritize remediation efforts
- **Reporting**: Consistent classification across all tools enables meaningful reports
- **Automation**: Allows automated workflows based on severity levels

**Standardized Structure**: Every parser must transform raw tool output into this exact format:

- **`findings`**: Array of discovered vulnerabilities/issues
- **`statistics`**: Tool-specific metrics and counts
- **Consistent Fields**: All findings must have the same structure regardless of source tool

### Validation Rules

- **`findings`**: Non-empty list when meaningful data is present
- **`severity`**: Must be one of: `critical`, `high`, `medium`, `low`, `info`
- **`timestamp`**: ISO-8601 format (use `datetime.now().isoformat()`)
- **`statistics`**: Dictionary variable per tool (e.g., `open_ports`, `total_hosts`, `status_codes`, etc.)
  - Non-negative numeric values only
  - Nested dictionaries allowed

### Severity Classification Guidelines

**🔴 Critical**: Immediate security threats
- SQL injection, RCE, authentication bypass
- Sensitive data exposure
- Critical system vulnerabilities

**🟠 High**: Significant security risks
- Directory traversal, file inclusion
- Privilege escalation opportunities
- High-value information disclosure

**🟡 Medium**: Moderate security concerns
- Information disclosure, version detection
- Configuration issues
- Potential attack vectors

**🔵 Low**: Minor security observations
- Banner information, default pages
- Non-sensitive information disclosure
- Low-risk configuration issues

**⚪ Info**: Informational findings
- Service detection, port enumeration
- General reconnaissance data
- Non-security related information

Tests validate this contract. See `tests/test_report_parsers.py` for more details.

## Component Details

### 1. BaseTool - Tool Interface

Each tool must implement the `BaseTool` interface which defines:

- **Metadata**: name, description, base command
- **Command Templates**: definitions of authorized commands with validation
- **Export**: output format and arguments for standardization
- **Parsing**: delegation to specialized parser
- **Validation**: argument and command verification

### 2. CommandTemplate - Validation System

The template system allows to:

- **Define authorized commands** with placeholders (`{target}`, `{ports}`)
- **Validate arguments** before execution
- **Build complete commands** with provided arguments
- **Ensure security** by limiting possible commands

### 3. BaseParser - Result Normalization

Parsers are the **core intelligence** of the system, responsible for:

- **Findings Extraction**: Parse raw output to identify vulnerabilities, open ports, services, etc.
- **Severity Classification**: **Critical responsibility** - intelligently classify each finding as critical/high/medium/low/info
- **Statistics Generation**: Create meaningful metrics and counts for analysis
- **Error Handling**: Robust parsing that handles malformed or unexpected outputs
- **Format Standardization**: Transform any tool output into the consistent `findings[]` + `statistics{}` format

**The parser's classification logic is what makes the system intelligent** - it determines how serious each vulnerability is, enabling proper risk prioritization and automated response workflows.

## Step-by-Step Implementation Guide

### Step 1: Minimal Structure

Create a new directory for your tool:

```
app/services/tools/<your_tool>/
  ├─ tool.py      # Tool definition (commands, validation, parsing entry point)
  ├─ parser.py    # Output parser to normalized findings/stats
  └─ sample.*     # Sample output file (xml/json/txt) for tests
```

### Concrete Example: "nikto" Tool

Let's say we want to add the Nikto tool for web auditing:

```
app/services/tools/nikto/
  ├─ tool.py      # NiktoTool class
  ├─ parser.py    # NiktoParser class  
  └─ sample.xml   # Nikto XML output example
```

### Step 2: Tool Class Implementation

File: `app/services/tools/nikto/tool.py`

```python
from typing import Any, Dict, List
from app.services.tools.tool import BaseTool, CommandTemplate, ArgumentDefinition


class NiktoTool(BaseTool):
    """Nikto tool implementation for web auditing"""
    
    @property
    def name(self) -> str:
        return "nikto"

    @property
    def description(self) -> str:
        return "Nikto web vulnerability scanner"

    @property
    def get_base_command(self) -> str:
        return "nikto"

    @property
    def get_version_arg(self) -> str:
        return "-Version"

    @property
    def export_format(self) -> str:
        return "xml"  # Nikto supports XML, JSON, CSV

    @property
    def export_arguments(self) -> List[str]:
        # Arguments to force XML export to stdout
        return ["-Format", "xml", "-output", "-"]

    @property
    def command_templates(self) -> List[CommandTemplate]:
        return [
            CommandTemplate(
                id="basic_scan",
                name="Basic Scan",
                base_command="nikto",
                arguments=["-h", "{target}"],
                description="Basic web vulnerability scan",
                argument_definitions=[
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target web URL or IP",
                        placeholder="https://example.com",
                    ),
                ],
            ),
            CommandTemplate(
                id="comprehensive_scan",
                name="Comprehensive Scan",
                base_command="nikto",
                arguments=["-h", "{target}", "-Tuning", "{tuning_options}"],
                description="Comprehensive scan with tuning options",
                argument_definitions=[
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target web URL or IP",
                        placeholder="https://example.com",
                    ),
                    ArgumentDefinition(
                        name="tuning_options",
                        type="string",
                        required=True,
                        description="Tuning options (0-9, comma-separated)",
                        placeholder="1,2,3,4,5",
                    ),
                ],
            ),
        ]

    def parse_results(self, raw_output: str, command_used: str, agent_id: str | None = None) -> Dict[str, Any]:
        from app.services.tools.nikto.parser import NiktoParser

        parser = NiktoParser()
        return parser.parse_single_result(raw_output, command_used, agent_id)

    def validate_command(self, command_args: List[str]) -> bool:
        # Reuse common validation logic
        return self._validate_command_common(command_args, "nikto")

    def _validate_placeholder(self, value: str, placeholder_name: str) -> bool:
        """Nikto-specific validation"""
        if not value or not value.strip():
            return False

        if placeholder_name == "target":
            # Basic URL/IP validation
            return bool(value.strip())
        elif placeholder_name == "tuning_options":
            # Tuning options validation (0-9)
            try:
                options = [int(x.strip()) for x in value.split(",")]
                return all(0 <= opt <= 9 for opt in options)
            except ValueError:
                return False
        
        return True
```

### Key Implementation Points

- **`command_templates`**: Defines authorized command forms with placeholders (`{target}`, `{tuning_options}`)
- **`export_arguments`**: Forces tool to print structured output (XML/JSON) to stdout
- **`validate_command`**: Calls `_validate_command_common(args, "<base>")` for basic validation
- **`parse_results`**: Must return normalized dict: `{ "findings": [...], "statistics": {...} }`
- **`_validate_placeholder`**: Custom argument validation (optional)

> [!TIP]
> See `app/services/tools/nmap/tool.py` for a complete example with advanced validation.

### Step 3: Parser Implementation

File: `app/services/tools/nikto/parser.py`

```python
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from app.services.tools.tool_parser import BaseParser


class NiktoParser(BaseParser):
    """Parser for Nikto XML output"""

    def parse_single_result(self, raw_output: str, command_used: str, agent_id: str | None = None) -> Dict:
        """
        Parse Nikto XML output to standard format
        Returns: {
            'findings': [Finding...],
            'statistics': {...}
        }
        """
        try:
            # Parse XML
            root = ET.fromstring(raw_output)
            return self._parse_xml_output(root, command_used, agent_id)
        except ET.ParseError:
            # Fallback to text parsing if XML fails
            return self._parse_text_output(raw_output, command_used, agent_id)

    def _parse_xml_output(self, root: ET.Element, command_used: str, agent_id: str | None = None) -> Dict:
        """Parse Nikto XML output"""
        findings = []
        
        # Parse detected vulnerabilities
        for item in root.findall(".//item"):
            finding = self._parse_vulnerability_item(item, agent_id)
            if finding:
                findings.append(finding)

        # Parse statistics
        stats = self._parse_scan_statistics(root)

        return {"findings": findings, "statistics": stats}

    def _parse_vulnerability_item(self, item: ET.Element, agent_id: str | None = None) -> Optional[Dict]:
        """Parse individual vulnerability item"""
        # Extract basic data
        id_elem = item.find("id")
        description_elem = item.find("description")
        url_elem = item.find("uri")
        
        if not id_elem or not description_elem:
            return None

        vuln_id = id_elem.text or "unknown"
        description = description_elem.text or ""
        url = url_elem.text if url_elem is not None else ""

        # Determine severity based on vulnerability ID
        severity = self._determine_vulnerability_severity(vuln_id, description)

        return self._create_finding(
            id=f"nikto_{vuln_id}",
            title=f"Web vulnerability detected: {vuln_id}",
            description=description,
            target=url,
            severity=severity,
            agent_id=agent_id,
        )

    def _determine_vulnerability_severity(self, vuln_id: str, description: str) -> str:
        """
        CRITICAL: This method determines vulnerability severity
        This is where the parser's intelligence lives - it must classify
        each finding based on its potential security impact.
        """
        # Critical keywords - immediate security threats
        critical_keywords = ["sql", "injection", "xss", "rce", "remote code execution", 
                           "authentication bypass", "privilege escalation", "command injection"]
        
        # High keywords - significant security risks  
        high_keywords = ["directory", "file", "backup", "config", "admin", "traversal",
                        "inclusion", "upload", "sensitive", "credential", "password"]
        
        # Medium keywords - moderate security concerns
        medium_keywords = ["information", "disclosure", "version", "banner", "debug",
                          "error", "stack trace", "path", "directory listing"]
        
        # Low keywords - minor security observations
        low_keywords = ["default", "test", "demo", "sample", "example", "placeholder"]

        description_lower = description.lower()
        
        # Classification logic - this is the parser's intelligence
        if any(keyword in description_lower for keyword in critical_keywords):
            return "critical"  # 🔴 Immediate threat
        elif any(keyword in description_lower for keyword in high_keywords):
            return "high"      # 🟠 Significant risk
        elif any(keyword in description_lower for keyword in medium_keywords):
            return "medium"    # 🟡 Moderate concern
        elif any(keyword in description_lower for keyword in low_keywords):
            return "low"       # 🔵 Minor observation
        else:
            return "info"      # ⚪ Informational

    def _parse_scan_statistics(self, root: ET.Element) -> Dict:
        """Parse scan statistics"""
        stats = {
            "total_vulnerabilities": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "scan_duration": "unknown",
        }

        # Count vulnerabilities by severity
        for item in root.findall(".//item"):
            id_elem = item.find("id")
            description_elem = item.find("description")
            
            if id_elem and description_elem:
                severity = self._determine_vulnerability_severity(
                    id_elem.text or "", 
                    description_elem.text or ""
                )
                stats["total_vulnerabilities"] += 1
                stats[f"{severity}_count"] += 1

        return stats

    def _parse_text_output(self, raw_output: str, command_used: str, agent_id: str | None = None) -> Dict:
        """Fallback parser for text output"""
        findings = []
        lines = raw_output.split("\n")

        for line in lines:
            line = line.strip()
            if not line or not line.startswith("-"):
                continue

            # Parse vulnerability lines (format: - ID: Description)
            if ": " in line:
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    vuln_id = parts[0].replace("-", "").strip()
                    description = parts[1].strip()
                    
                    severity = self._determine_vulnerability_severity(vuln_id, description)
                    
                    findings.append(self._create_finding(
                        id=f"nikto_text_{vuln_id}",
                        title=f"Web vulnerability: {vuln_id}",
                        description=description,
                        target="Unknown",
                        severity=severity,
                        agent_id=agent_id,
                    ))

        return {
            "findings": findings,
            "statistics": {
                "total_vulnerabilities": len(findings),
                "critical_count": len([f for f in findings if f.get("severity") == "critical"]),
                "high_count": len([f for f in findings if f.get("severity") == "high"]),
                "medium_count": len([f for f in findings if f.get("severity") == "medium"]),
                "low_count": len([f for f in findings if f.get("severity") == "low"]),
                "scan_duration": "unknown",
            },
        }
```

### Helpers available in `BaseParser`

- **`_create_finding(...)`**: Creates a standardized finding with all required fields
- **`_count_by_severity(findings)`**: Returns a dict of counts per severity

### Key Parsing Points

1. **Intelligent Classification**: **Most Important** - The parser must intelligently classify each vulnerability based on its content and potential impact. This classification drives the entire risk assessment workflow.

2. **Robust Error Handling**: Fallback to text parsing if XML fails, handle malformed outputs gracefully

3. **Meaningful Statistics**: Generate counts by severity and tool-specific metrics that provide actionable insights

4. **Standardized Format**: Transform any tool output into the consistent `findings[]` + `statistics{}` structure

5. **Context Awareness**: Consider the tool type, target environment, and vulnerability context when classifying severity

**The parser's classification logic is the system's brain** - it determines how serious each finding is, enabling proper risk prioritization and automated response workflows.

> [!TIP]
> See `app/services/tools/nmap/parser.py` for a complete production implementation.

### Step 4: Tool Registration

Add your tool to `ToolManager._register_default_tools()` so it's discoverable by name and variants:

```python
from app.services.tools.nikto.tool import NiktoTool
self.tools["nikto"] = NiktoTool()
```

File: `app/services/tools/tool_manager.py`

This step enables:

- **Listing tools and variants** (`get_available_tools`)
- **Validating commands** (`validate_command`)
- **Parsing results** (`parse_results`)
- **Building commands** (`build_command_from_variant`)

### Step 5: Command Validation and Construction

- **Validation**: Checks that provided arguments match a `CommandTemplate`
- **Construction**: Uses `build_command_from_variant(tool, variant_id, custom_args)` to replace placeholders

Example:

```python
manager = ToolManager()
command = manager.build_command_from_variant(
    "nikto",
    "basic_scan", 
    {"target": "https://example.com"}
)
# => ["-h", "https://example.com", "-Format", "xml", "-output", "-"]
```

### Step 6: Local Testing

1. **Sample file**: Place a `sample.xml` or `sample.json` in your tool folder
2. **Unit tests**: Write tests similar to `tests/test_report_parsers.py`
3. **Manual test**: Instantiate `ToolManager()` and call `parse_results("nikto", sample_output, "nikto ...")`

Test example:

```python
def test_nikto_parser():
    parser = NiktoParser()
    
    with open("app/services/tools/nikto/sample.xml", "r") as f:
        sample_xml = f.read()
    
    result = parser.parse_single_result(
        sample_xml, 
        "nikto -h https://example.com -Format xml -output -"
    )
    
    assert "findings" in result
    assert "statistics" in result
    assert len(result["findings"]) > 0
```

---

Built with ❤️ by the Pentulz team. If you need help or find an issue, please open an issue in the repository.


