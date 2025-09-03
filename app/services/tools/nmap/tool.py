import json
import re
from typing import Any, Dict, List

from app.services.tools.tool import ArgumentDefinition, BaseTool, CommandTemplate
from app.services.tools.tool_manager import ToolManager


class NmapTool(BaseTool):
    """Nmap tool implementation"""

    @property
    def name(self) -> str:
        return "nmap"

    @property
    def description(self) -> str:
        return "Nmap tool implementation"

    @property
    def get_base_command(self) -> str:
        return "nmap"

    @property
    def get_version_arg(self) -> str:
        return "--version"

    @property
    def export_format(self) -> str:
        return "xml"

    @property
    def export_arguments(self) -> List[str]:
        """Always export XML to stdout for consistent parsing"""
        return ["-oX", "-"]

    @property
    def command_templates(self) -> List[CommandTemplate]:
        return [
            CommandTemplate(
                id="list_scan",
                name="List Scan",
                base_command="nmap",
                arguments=["-sL", "{target}"],
                description="List scan - just list targets",
                argument_definitions=[
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target host or network to scan",
                        placeholder="192.168.1.0/24",
                    )
                ],
            ),
            CommandTemplate(
                id="tcp_connect_scan",
                name="TCP Connect Scan",
                base_command="nmap",
                arguments=["-sT", "-p", "{ports}", "{target}"],
                description="TCP connect scan on specific ports",
                argument_definitions=[
                    ArgumentDefinition(
                        name="ports",
                        type="string",
                        required=True,
                        description="Ports to scan (single port, range, or comma-separated)",
                        placeholder="80,443,8080-8090",
                    ),
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target host to scan",
                        placeholder="192.168.1.1",
                    ),
                ],
            ),
            CommandTemplate(
                id="tcp_syn_scan",
                name="TCP SYN Scan",
                base_command="nmap",
                arguments=["-sS", "-p", "{ports}", "{target}"],
                description="TCP SYN scan on specific ports",
                argument_definitions=[
                    ArgumentDefinition(
                        name="ports",
                        type="string",
                        required=True,
                        description="Ports to scan (single port, range, or comma-separated)",
                        placeholder="80,443,8080-8090",
                    ),
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target host to scan",
                        placeholder="192.168.1.1",
                    ),
                ],
            ),
            CommandTemplate(
                id="service_version_detection",
                name="Service Version Detection",
                base_command="nmap",
                arguments=["-sV", "-p", "{ports}", "{target}"],
                description="Service version detection",
                argument_definitions=[
                    ArgumentDefinition(
                        name="ports",
                        type="string",
                        required=True,
                        description="Ports to scan for service detection",
                        placeholder="80,443,22,21",
                    ),
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target host to scan",
                        placeholder="192.168.1.1",
                    ),
                ],
            ),
            CommandTemplate(
                id="os_detection",
                name="OS Detection",
                base_command="nmap",
                arguments=["-O", "{target}"],
                description="OS detection",
                argument_definitions=[
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target host for OS detection",
                        placeholder="192.168.1.1",
                    )
                ],
            ),
            CommandTemplate(
                id="aggressive_scan",
                name="Aggressive Scan",
                base_command="nmap",
                arguments=["-A", "{target}"],
                description="Aggressive scan",
                argument_definitions=[
                    ArgumentDefinition(
                        name="target",
                        type="string",
                        required=True,
                        description="Target host for aggressive scan",
                        placeholder="192.168.1.1",
                    )
                ],
            ),
        ]

    def parse_results(
        self, raw_output: str, command_used: str, agent_id: str = None
    ) -> Dict[str, Any]:
        """Parse nmap output"""
        # pylint: disable=import-outside-toplevel
        from app.services.tools.nmap.parser import NmapParser

        parser = NmapParser()
        return parser.parse_single_result(raw_output, command_used, agent_id)

    def parse_version(self, raw_version: str) -> str:
        match = re.search(r"Nmap version (\d+\.\d+)", raw_version)
        return match.group(1) if match else "unknown"

    def validate_command(self, command_args: List[str]) -> bool:
        """Validate nmap command arguments"""
        return self._validate_command_common(command_args, "nmap")

    def _validate_placeholder(self, value: str, placeholder_name: str) -> bool:
        """Validate placeholder values for nmap"""
        if not value or not value.strip():
            return False

        # Define validation rules for each placeholder type
        validation_rules = {
            "ports": self._validate_ports,
            "target": self._validate_target,
        }

        # Get the validation function for this placeholder
        validator_func = validation_rules.get(placeholder_name)
        if validator_func:
            return validator_func(value)

        return True

    def _validate_ports(self, value: str) -> bool:
        """Validate ports: single port, range, or comma-separated"""
        port_patterns = value.split(",")
        for pattern in port_patterns:
            if "-" in pattern:
                # Port range like "80-90"
                try:
                    start, end = pattern.split("-", 1)
                    start_port = int(start)
                    end_port = int(end)
                    if not (
                        1 <= start_port <= 65535
                        and 1 <= end_port <= 65535
                        and start_port <= end_port
                    ):
                        return False
                except (ValueError, IndexError):
                    return False
            else:
                # Single port
                try:
                    port = int(pattern)
                    if not 1 <= port <= 65535:
                        return False
                except ValueError:
                    return False
        return True

    def _validate_target(self, value: str) -> bool:
        """Validate target (IP, hostname, network range)"""
        return bool(re.match(r"^[\w\.\-/:]+$", value))


if __name__ == "__main__":
    manager = ToolManager()

    # 1. Get available tools
    tools = manager.get_available_tools()
    print("Available tools:")
    print(json.dumps(tools, indent=2))

    # 2. Validate command
    valid = manager.validate_command(
        "nmap", ["nmap", "-sT", "-p", "80,443", "192.168.1.1"]
    )
    print(f"\nCommand validation: {valid}")

    # 3. Parse results
    NMAP_OUTPUT = "TEST"

    parsed = manager.parse_results(
        "nmap", NMAP_OUTPUT, "nmap -sT -p 22,80,443 scanme.nmap.org"
    )
    print("\nParsed results:")
    print(json.dumps(parsed, indent=2))
