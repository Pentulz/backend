from typing import Any, Dict, List, Optional

from app.services.tools.base import BaseTool


class ToolManager:
    """Manages available tools"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools"""

        # Not definitive, just in order to test the tool above
        # pylint: disable=import-outside-toplevel
        from app.services.tools.nmap import NmapTool

        self.tools["nmap"] = NmapTool()

    def get_available_tools(self) -> List[Dict[str, Any]]:
        result = []
        for name, tool in self.tools.items():
            result.append(
                {
                    "type": "tools",
                    "attributes": {
                        "name": name,
                        "cmd": tool.get_base_command,
                        "export_format": tool.export_format,
                        "export_arguments": tool.export_arguments,
                        "version_arg": tool.get_version_arg,
                        "variants": [
                            {
                                "args": cmd.arguments,
                                "description": cmd.description,
                            }
                            for cmd in tool.command_templates
                        ],
                    },
                }
            )
        return result

    def validate_command(self, tool_name: str, command_args: List[str]) -> bool:
        """Validate if command is allowed for this tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return False
        return tool.validate_command(command_args)

    def parse_results(
        self, tool_name: str, raw_output: str, command_used: str
    ) -> Optional[Dict[str, Any]]:
        """Parse tool results"""
        tool = self.tools.get(tool_name)
        if not tool:
            return None
        return tool.parse_results(raw_output, command_used)
