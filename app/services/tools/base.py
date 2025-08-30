import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class CommandTemplate:
    """Template for building tool commands"""

    base_command: str
    arguments: List[str]
    description: str


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
        pass
    
    @property
    @abstractmethod
    def get_base_command(self) -> str:
        """Base command for the tool"""
        pass

    @property
    @abstractmethod
    def get_version_arg(self) -> str:
        """Argument to check if tool is available"""
        pass

    @property
    @abstractmethod
    def command_templates(self) -> List[CommandTemplate]:
        """Available command templates for this tool"""
        
    @property
    @abstractmethod
    def export_format(self) -> str:
        """Export format used by the tool (xml, json, csv, etc.)"""
        pass
    
    @property
    @abstractmethod
    def export_arguments(self) -> List[str]:
        """Arguments needed to export in the desired format"""
        pass
    
    def get_command_with_export(self, template_args: List[str]) -> List[str]:
        """Add export arguments to any command"""
        return template_args + self.export_arguments

    @abstractmethod
    def parse_results(self, raw_output: str, command_used: str) -> Dict[str, Any]:
        """Parse tool output into structured data"""

    def validate_command(self, command_args: List[str]) -> bool:
        """Validate if command matches any template"""
        command_str = " ".join(command_args)

        for template in self.command_templates:
            template_str = " ".join([template.base_command] + template.arguments)
            # Simple validation - check if command matches template pattern
            pattern = template_str.replace("{target}", r"[\w\.\-]+").replace(
                "{ports}", r"[\d\-,]+"
            )
            if re.match(pattern, command_str):
                return True
        return False
