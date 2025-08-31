from typing import Any, Dict, List, Optional

from app.services.tools.base_tool import BaseTool


class ToolManager:
    """Manages available tools"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools"""

        # Not definitive, just in order to test the tool above
        # pylint: disable=import-outside-toplevel
        from app.services.tools.nmap.tool import NmapTool

        self.tools["nmap"] = NmapTool()

        # pylint: disable=import-outside-toplevel
        from app.services.tools.tshark.tool import TsharkTool

        self.tools["tshark"] = TsharkTool()

        # pylint: disable=import-outside-toplevel
        from app.services.tools.ffuf.tool import FFufTool

        self.tools["ffuf"] = FFufTool()

    def get_available_tools(self) -> List[Dict[str, Any]]:
        result = []
        for name, tool in self.tools.items():
            result.append(
                {
                    "type": "tools",
                    "id": name,
                    "attributes": {
                        "name": name,
                        "cmd": tool.get_base_command,
                        "export_format": tool.export_format,
                        "export_arguments": tool.export_arguments,
                        "version_arg": tool.get_version_arg,
                        "variants": [
                            {
                                "id": cmd.id,
                                "name": cmd.name,
                                "description": cmd.description,
                                "arguments": cmd.arguments,
                                "argument_definitions": (
                                    [
                                        {
                                            "name": arg.name,
                                            "type": arg.type,
                                            "required": arg.required,
                                            "description": arg.description,
                                            "default_value": arg.default_value,
                                            "placeholder": arg.placeholder,
                                        }
                                        for arg in cmd.argument_definitions
                                    ]
                                    if cmd.argument_definitions
                                    else []
                                ),
                            }
                            for cmd in tool.command_templates
                        ],
                    },
                }
            )
        return result

    def get_tool_variant(
        self, tool_name: str, variant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific variant by ID for a tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return None

        for template in tool.command_templates:
            if template.id == variant_id:
                return {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "arguments": template.arguments,
                    "argument_definitions": (
                        [
                            {
                                "name": arg.name,
                                "type": arg.type,
                                "required": arg.required,
                                "description": arg.description,
                                "default_value": arg.default_value,
                                "placeholder": arg.placeholder,
                            }
                            for arg in template.argument_definitions
                        ]
                        if template.argument_definitions
                        else []
                    ),
                }
        return None

    def build_command_from_variant(
        self, tool_name: str, variant_id: str, custom_args: Dict[str, str]
    ) -> Optional[List[str]]:
        """Build a command from a variant with custom arguments"""
        variant = self.get_tool_variant(tool_name, variant_id)
        if not variant:
            return None

        tool = self.tools.get(tool_name)
        if not tool:
            return None

        # Find the actual template object
        cmd_template = None
        for t in tool.command_templates:
            if t.id == variant_id:
                cmd_template = t
                break

        if not cmd_template:
            return None

        # Build command by replacing placeholders
        command_args = []
        for arg in cmd_template.arguments:
            if arg.startswith("{") and arg.endswith("}"):
                # This is a placeholder
                placeholder_name = arg[1:-1]
                if placeholder_name in custom_args:
                    command_args.append(custom_args[placeholder_name])
                else:
                    # Check if there's a default value
                    arg_def = next(
                        (
                            a
                            for a in cmd_template.argument_definitions
                            if a.name == placeholder_name
                        ),
                        None,
                    )
                    if arg_def and arg_def.default_value is not None:
                        command_args.append(str(arg_def.default_value))
                    else:
                        return None  # Missing required argument
            elif "{" in arg and "}" in arg:
                # This is a placeholder with prefix/suffix like "duration:{duration}"
                placeholder_name = arg[arg.find("{") + 1 : arg.find("}")]
                if placeholder_name in custom_args:
                    command_args.append(
                        arg.replace(
                            f"{{{placeholder_name}}}", custom_args[placeholder_name]
                        )
                    )
                else:
                    # Check if there's a default value
                    arg_def = next(
                        (
                            a
                            for a in cmd_template.argument_definitions
                            if a.name == placeholder_name
                        ),
                        None,
                    )
                    if arg_def and arg_def.default_value is not None:
                        command_args.append(
                            arg.replace(
                                f"{{{placeholder_name}}}", str(arg_def.default_value)
                            )
                        )
                    else:
                        return None  # Missing required argument
            else:
                # Fixed argument
                command_args.append(arg)

        return command_args

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

    def get_tool(self, tool_name: str) -> BaseTool:
        """Get tool by name"""
        return self.tools.get(tool_name)
