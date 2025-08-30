from typing import List
from typing import Any, Dict

from app.services.tools.base import BaseTool, CommandTemplate, ArgumentDefinition

class TsharkTool(BaseTool):
    """Tshark tool implementation"""
    
    @property
    def name(self) -> str:
        return "tshark"
    
    @property
    def description(self) -> str:
        return "Tshark tool implementation"
    
    @property
    def get_base_command(self) -> str:
        return "tshark"
    
    @property
    def get_version_arg(self) -> str:
        return "--version"
    
    @property
    def export_format(self) -> str:
        return "json"
    
    @property
    def export_arguments(self) -> List[str]:
        return ["-T", "json"]
    
    @property
    def command_templates(self) -> List[CommandTemplate]:
        return [
            CommandTemplate(
                base_command="tshark",
                arguments=["-i", "{interface}", "-c", "{count}", "-a", "duration:{duration}"],
                description="Live capture with duration limit",
                argument_definitions=[
                    ArgumentDefinition(
                        name="interface",
                        type="string",
                        required=True,
                        description="Network interface to capture from",
                        placeholder="eth0"
                    ),
                    ArgumentDefinition(
                        name="count",
                        type="number",
                        required=True,
                        description="Number of packets to capture",
                        placeholder="100"
                    ),
                    ArgumentDefinition(
                        name="duration",
                        type="number",
                        required=True,
                        description="Duration of capture in seconds",
                        placeholder="60"
                    )
                ]
            ),
            CommandTemplate(
                base_command="tshark",
                arguments=["-r", "{pcap_file}", "-a", "duration:{duration}"],
                description="Read PCAP file with duration filter",
                argument_definitions=[
                    ArgumentDefinition(
                        name="pcap_file",
                        type="string",
                        required=True,
                        description="Path to PCAP file to analyze",
                        placeholder="capture.pcap"
                    ),
                    ArgumentDefinition(
                        name="duration",
                        type="number",
                        required=True,
                        description="Duration to analyze from start in seconds",
                        placeholder="300"
                    )
                ]
            ),
            CommandTemplate(
                base_command="tshark",
                arguments=["-r", "{pcap_file}", "-Y", "{filter}", "-a", "duration:{duration}"],
                description="Read PCAP with filter and duration limit",
                argument_definitions=[
                    ArgumentDefinition(
                        name="pcap_file",
                        type="string",
                        required=True,
                        description="Path to PCAP file to analyze",
                        placeholder="capture.pcap"
                    ),
                    ArgumentDefinition(
                        name="filter",
                        type="string",
                        required=True,
                        description="BPF filter expression",
                        placeholder="tcp.port == 80"
                    ),
                    ArgumentDefinition(
                        name="duration",
                        type="number",
                        required=True,
                        description="Duration to analyze from start in seconds",
                        placeholder="300"
                    )
                ]
            ),
            CommandTemplate(
                base_command="tshark",
                arguments=["-i", "{interface}", "-a", "duration:{duration}"],
                description="Live capture with duration limit only",
                argument_definitions=[
                    ArgumentDefinition(
                        name="interface",
                        type="string",
                        required=True,
                        description="Network interface to capture from",
                        placeholder="eth0"
                    ),
                    ArgumentDefinition(
                        name="duration",
                        type="number",
                        required=True,
                        description="Duration of capture in seconds",
                        placeholder="60"
                    )
                ]
            ),
        ]

    def parse_results(self, raw_output: str, command_used: str) -> Dict[str, Any]:
        """Parse tshark output"""
        return raw_output


    