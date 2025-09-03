from typing import Any, Dict, List

from app.services.tools.tool import ArgumentDefinition, BaseTool, CommandTemplate


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
        return ["-s", "-noninteractive", "-o", "/dev/stdout", "-of", "json"]

    @property
    def command_templates(self) -> List[CommandTemplate]:
        return [
            CommandTemplate(
                id="directory_fuzzing",
                name="Directory Fuzzing",
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
                id="status_code_matching",
                name="Status Code Matching",
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
                id="size_filtering",
                name="Size Filtering",
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

    def parse_results(
        self, raw_output: str, command_used: str, agent_id: str = None
    ) -> Dict[str, Any]:
        """Parse ffuf output"""
        # pylint: disable=import-outside-toplevel
        from app.services.tools.ffuf.parser import FFufParser

        parser = FFufParser()
        return parser.parse_single_result(raw_output, command_used, agent_id)

    def validate_command(self, command_args: List[str]) -> bool:
        """Validate ffuf command arguments"""
        return self._validate_command_common(command_args, "ffuf")

    def _validate_placeholder(self, value: str, placeholder_name: str) -> bool:
        """Validate placeholder values for ffuf"""
        if not value or not value.strip():
            return False

        # Define validation rules for each placeholder type
        validation_rules = {
            "wordlist": lambda v: bool(v.strip()),
            "url": lambda v: bool(v.strip() and "FUZZ" in v),
            "match_codes": self._validate_match_codes,
            "filter_size": self._validate_filter_size,
        }

        # Get the validation function for this placeholder
        validator_func = validation_rules.get(placeholder_name)
        if validator_func:
            return validator_func(value)

        return True

    def _validate_match_codes(self, value: str) -> bool:
        """Validate HTTP status codes"""
        codes = value.split(",")
        for code in codes:
            try:
                code_num = int(code.strip())
                if not 100 <= code_num <= 599:
                    return False
            except ValueError:
                return False
        return True

    def _validate_filter_size(self, value: str) -> bool:
        """Validate numeric size"""
        try:
            size = int(value)
            return size > 0
        except ValueError:
            return False
