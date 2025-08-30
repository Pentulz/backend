import json
from typing import Any, Dict, List

from app.services.tools.base import ArgumentDefinition, BaseTool, CommandTemplate
from app.services.tools.manager import ToolManager


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

    def parse_results(self, raw_output: str, command_used: str) -> Dict[str, Any]:
        """Parse nmap output"""
        return raw_output


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
