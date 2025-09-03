import re
from typing import Any, Dict, List

from app.services.tools.tool import ArgumentDefinition, BaseTool, CommandTemplate


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
                id="live_capture_with_count",
                name="Live Capture with Count",
                base_command="tshark",
                arguments=[
                    "-i",
                    "{interface}",
                    "-c",
                    "{count}",
                    "-a",
                    "duration:{duration}",
                ],
                description="Live capture with duration limit",
                argument_definitions=[
                    ArgumentDefinition(
                        name="interface",
                        type="string",
                        required=True,
                        description="Network interface to capture from",
                        placeholder="eth0",
                    ),
                    ArgumentDefinition(
                        name="count",
                        type="number",
                        required=True,
                        description="Number of packets to capture",
                        placeholder="100",
                    ),
                    ArgumentDefinition(
                        name="duration",
                        type="number",
                        required=True,
                        description="Duration of capture in seconds",
                        placeholder="60",
                    ),
                ],
            ),
            CommandTemplate(
                id="pcap_duration_filter",
                name="PCAP Duration Filter",
                base_command="tshark",
                arguments=["-r", "{pcap_file}", "-a", "duration:{duration}"],
                description="Read PCAP file with duration filter",
                argument_definitions=[
                    ArgumentDefinition(
                        name="pcap_file",
                        type="string",
                        required=True,
                        description="Path to PCAP file to analyze",
                        placeholder="capture.pcap",
                    ),
                    ArgumentDefinition(
                        name="duration",
                        type="number",
                        required=True,
                        description="Duration to analyze from start in seconds",
                        placeholder="300",
                    ),
                ],
            ),
            CommandTemplate(
                id="pcap_filter_duration",
                name="PCAP Filter with Duration",
                base_command="tshark",
                arguments=[
                    "-r",
                    "{pcap_file}",
                    "-Y",
                    "{filter}",
                    "-a",
                    "duration:{duration}",
                ],
                description="Read PCAP with filter and duration limit",
                argument_definitions=[
                    ArgumentDefinition(
                        name="pcap_file",
                        type="string",
                        required=True,
                        description="Path to PCAP file to analyze",
                        placeholder="capture.pcap",
                    ),
                    ArgumentDefinition(
                        name="filter",
                        type="string",
                        required=True,
                        description="BPF filter expression",
                        placeholder="tcp.port == 80",
                    ),
                    ArgumentDefinition(
                        name="duration",
                        type="number",
                        required=True,
                        description="Duration to analyze from start in seconds",
                        placeholder="300",
                    ),
                ],
            ),
            CommandTemplate(
                id="live_capture_duration_only",
                name="Live Capture Duration Only",
                base_command="tshark",
                arguments=["-i", "{interface}", "-a", "duration:{duration}"],
                description="Live capture with duration limit only",
                argument_definitions=[
                    ArgumentDefinition(
                        name="interface",
                        type="string",
                        required=True,
                        description="Network interface to capture from",
                        placeholder="eth0",
                    ),
                    ArgumentDefinition(
                        name="duration",
                        type="number",
                        required=True,
                        description="Duration of capture in seconds",
                        placeholder="60",
                    ),
                ],
            ),
        ]

    def parse_results(
        self, raw_output: str, command_used: str, agent_id: str = None
    ) -> Dict[str, Any]:
        """Parse tshark output"""
        # pylint: disable=import-outside-toplevel
        from app.services.tools.tshark.parser import TsharkParser

        parser = TsharkParser()
        return parser.parse_single_result(raw_output, command_used, agent_id)

    def parse_version(self, raw_version: str) -> str:
        match = re.search(r"TShark \(Wireshark\) (\d+\.\d+\.\d+)", raw_version)
        return match.group(1) if match else super().parse_version(raw_version)

    def validate_command(self, command_args: List[str]) -> bool:
        """Validate tshark command arguments"""
        return self._validate_command_common(command_args, "tshark")

    def _validate_placeholder(self, value: str, placeholder_name: str) -> bool:
        """Validate placeholder values for tshark"""
        if not value or not value.strip():
            return False

        # Define validation rules for each placeholder type
        validation_rules = {
            "interface": self._validate_interface,
            "count": self._validate_count,
            "pcap_file": self._validate_pcap_file,
            "filter": self._validate_filter,
        }

        # Get the validation function for this placeholder
        validator_func = validation_rules.get(placeholder_name)
        if validator_func:
            return validator_func(value)

        return True

    def _validate_interface(self, value: str) -> bool:
        """Validate network interface name"""
        return bool(re.match(r"^[\w\-]+$", value))

    def _validate_count(self, value: str) -> bool:
        """Validate numeric count"""
        try:
            count = int(value)
            return count > 0
        except ValueError:
            return False

    def _validate_pcap_file(self, value: str) -> bool:
        """Validate PCAP file path"""
        return bool(value.strip())

    def _validate_filter(self, value: str) -> bool:
        """Validate BPF filter"""
        return bool(value.strip())

    def _validate_template_with_placeholder(
        self, value: str, template_arg: str, placeholder_name: str
    ) -> bool:
        """Validate template arguments with embedded placeholders like 'duration:{duration}'"""
        # Extract prefix and suffix
        placeholder_start = template_arg.find("{")
        placeholder_end = template_arg.find("}")

        if placeholder_start == -1 or placeholder_end == -1:
            return False

        prefix = template_arg[:placeholder_start]
        suffix = template_arg[placeholder_end + 1 :]

        # Check if the value starts with prefix and ends with suffix
        if not value.startswith(prefix) or not value.endswith(suffix):
            return False

        # Extract the actual placeholder value
        placeholder_value = value[len(prefix) : len(value) - len(suffix)]

        # Validate the placeholder value
        if placeholder_name == "duration":
            try:
                duration = int(placeholder_value)
                return duration > 0
            except ValueError:
                return False

        return True
