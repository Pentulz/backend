from typing import Any, Dict, List

from app.services.tools.base import ArgumentDefinition, BaseTool, CommandTemplate


class FFufTool(BaseTool):
    """FFuf tool implementation"""

    @property
    def name(self) -> str:
        return "ffuf"

    @property
    def description(self) -> str:
        return "Fast web fuzzer"

    @property
    def get_base_command(self) -> str:
        return "ffuf"

    @property
    def get_version_arg(self) -> str:
        return "-V"

    @property
    def export_format(self) -> str:
        return "json"

    @property
    def export_arguments(self) -> List[str]:
        """Always export JSON to stdout"""
        return ["-of", "json", "-o", "-"]

    @property
    def command_templates(self) -> List[CommandTemplate]:
        return [
            CommandTemplate(
                base_command="ffuf",
                arguments=["-w", "{wordlist}", "-u", "{url}"],
                description="Directory/file fuzzing",
                argument_definitions=[
                    ArgumentDefinition(
                        name="wordlist",
                        type="string",
                        required=True,
                        description="Path to wordlist file",
                        placeholder="/usr/share/wordlists/dirb/common.txt",
                    ),
                    ArgumentDefinition(
                        name="url",
                        type="string",
                        required=True,
                        description="Target URL to fuzz",
                        placeholder="https://example.com/FUZZ",
                    ),
                ],
            ),
            CommandTemplate(
                base_command="ffuf",
                arguments=["-w", "{wordlist}", "-u", "{url}", "-mc", "{match_codes}"],
                description="Fuzzing with status code matching",
                argument_definitions=[
                    ArgumentDefinition(
                        name="wordlist",
                        type="string",
                        required=True,
                        description="Path to wordlist file",
                        placeholder="/usr/share/wordlists/dirb/common.txt",
                    ),
                    ArgumentDefinition(
                        name="url",
                        type="string",
                        required=True,
                        description="Target URL to fuzz",
                        placeholder="https://example.com/FUZZ",
                    ),
                    ArgumentDefinition(
                        name="match_codes",
                        type="string",
                        required=True,
                        description="HTTP status codes to match (comma-separated)",
                        placeholder="200,301,302",
                    ),
                ],
            ),
            CommandTemplate(
                base_command="ffuf",
                arguments=["-w", "{wordlist}", "-u", "{url}", "-fs", "{filter_size}"],
                description="Fuzzing with response size filtering",
                argument_definitions=[
                    ArgumentDefinition(
                        name="wordlist",
                        type="string",
                        required=True,
                        description="Path to wordlist file",
                        placeholder="/usr/share/wordlists/dirb/common.txt",
                    ),
                    ArgumentDefinition(
                        name="url",
                        type="string",
                        required=True,
                        description="Target URL to fuzz",
                        placeholder="https://example.com/FUZZ",
                    ),
                    ArgumentDefinition(
                        name="filter_size",
                        type="number",
                        required=True,
                        description="Filter responses by size (bytes)",
                        placeholder="1234",
                    ),
                ],
            ),
        ]

    def parse_results(self, raw_output: str, command_used: str) -> Dict[str, Any]:
        """Parse ffuf output"""
        return raw_output
