from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List


class BaseParser(ABC):
    """Base class for tool output parsers"""

    @abstractmethod
    def parse_single_result(
        self, raw_output: str, command_used: str, agent_id: str = None
    ) -> Dict:
        """
        Parse single tool output to standard format
        Must return: {
            'findings': [Finding...],
            'statistics': {...}
        }
        """

    def _create_finding(self, **kwargs) -> Dict:
        """Helper to create standardized finding"""
        return {
            "id": kwargs.get("id", f"finding_{hash(str(kwargs))}"),
            "severity": kwargs.get("severity", "info"),
            "title": kwargs.get("title", "Unknown Finding"),
            "description": kwargs.get("description", ""),
            "target": kwargs.get("target", ""),
            "agent_id": kwargs.get("agent_id", "unknown"),
            "timestamp": kwargs.get("timestamp", datetime.now().isoformat()),
        }

    def _count_by_severity(self, findings: List[Dict]) -> Dict:
        """Count findings by severity"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in findings:
            severity = finding.get("severity", "info")
            if severity in counts:
                counts[severity] += 1
        return counts
