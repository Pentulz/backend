from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Union


@dataclass
class ArgumentDefinition:
    """Definition of a command argument"""

    name: str
    type: Literal["string", "number", "boolean"]
    required: bool
    description: str = ""
    default_value: Union[str, int, bool, None] = None
    placeholder: str = ""


@dataclass
class CommandTemplate:
    """Template for building tool commands"""

    base_command: str
    arguments: List[str]
    description: str
    argument_definitions: List[ArgumentDefinition] = None

    def __post_init__(self):
        if self.argument_definitions is None:
            self.argument_definitions = []


class BaseTool(ABC):
    """Base class for tool definitions"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the tool"""

    @property
    @abstractmethod
    def get_base_command(self) -> str:
        """Base command for the tool"""

    @property
    @abstractmethod
    def get_version_arg(self) -> str:
        """Argument to check if tool is available"""

    @property
    @abstractmethod
    def command_templates(self) -> List[CommandTemplate]:
        """Available command templates for this tool"""

    @property
    @abstractmethod
    def export_format(self) -> str:
        """Export format used by the tool (xml, json, csv, etc.)"""

    @property
    @abstractmethod
    def export_arguments(self) -> List[str]:
        """Arguments needed to export in the desired format"""

    def get_command_with_export(self, template_args: List[str]) -> List[str]:
        """Add export arguments to any command"""
        return template_args + self.export_arguments

    @abstractmethod
    def parse_results(self, raw_output: str, command_used: str) -> Dict[str, Any]:
        """Parse tool output into structured data"""

    @abstractmethod
    def validate_command(self, command_args: List[str]) -> bool:
        """Validate if command arguments match any template for this tool"""

    def _validate_command_common(
        self, command_args: List[str], base_command: str
    ) -> bool:
        """Common command validation logic for all tools"""
        if not command_args:
            return False

        # Remove base command if present
        if command_args[0] == base_command:
            command_args = command_args[1:]

        # Check if command matches any template structure
        for template in self.command_templates:
            if len(command_args) == len(template.arguments):
                # Check fixed arguments
                matches = True
                for arg, template_arg in zip(command_args, template.arguments):
                    if template_arg.startswith("{") and template_arg.endswith("}"):
                        # This is a placeholder, validate the value
                        placeholder_name = template_arg[1:-1]
                        if not self._validate_placeholder(arg, placeholder_name):
                            matches = False
                            break
                    elif "{" in template_arg and "}" in template_arg:
                        # This is a placeholder with prefix/suffix like "duration:{duration}"
                        placeholder_name = template_arg[
                            template_arg.find("{") + 1 : template_arg.find("}")
                        ]
                        if not self._validate_template_with_placeholder(
                            arg, template_arg, placeholder_name
                        ):
                            matches = False
                            break
                    elif arg != template_arg:
                        # Fixed argument must match exactly
                        matches = False
                        break
                if matches:
                    return True
        return False

    def _validate_placeholder(self, value: str, _placeholder_name: str) -> bool:
        """Validate placeholder values - to be overridden by specific tools"""
        if not value or not value.strip():
            return False
        return True

    def _validate_template_with_placeholder(
        self, value: str, _template_arg: str, _placeholder_name: str
    ) -> bool:
        """Validate template arguments with embedded placeholders - to be overridden by specific tools"""
        # Default implementation for simple cases
        if not value or not value.strip():
            return False
        return True

    def validate_and_prepare_command(
        self, command_args: List[str]
    ) -> tuple[bool, List[str]]:
        """
        Validate command and return (is_valid, complete_command_with_export)
        Returns (False, []) if invalid, (True, complete_command) if valid
        """
        if not self.validate_command(command_args):
            return False, []

        # Remove base command if present to get just the arguments
        if command_args[0] == self.get_base_command:
            args_only = command_args[1:]
        else:
            args_only = command_args

        # Build complete command with export arguments
        complete_command = [self.get_base_command] + args_only + self.export_arguments
        return True, complete_command
