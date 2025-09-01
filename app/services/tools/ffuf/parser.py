import json
from datetime import datetime
from typing import Dict, Optional

from app.services.tools.tool_parser import BaseParser


class FFufParser(BaseParser):
    """Parser for FFuf JSON output"""

    def parse_single_result(self, raw_output: str, command_used: str, agent_id: str = None) -> Dict:
        """
        Parse FFuf JSON output to standard format
        Returns: {
            'findings': [Finding...],
            'statistics': {...}
        }
        """
        try:
            # Try to parse as JSON first
            data = json.loads(raw_output)
            return self._parse_json_output(data, command_used, agent_id)
        except json.JSONDecodeError:
            # Fall back to text parsing if JSON fails
            return self._parse_text_output(raw_output, command_used, agent_id)

    def _parse_json_output(self, data: Dict, command_used: str, agent_id: str = None) -> Dict:
        """Parse FFuf JSON output"""
        findings = []

        # Parse results
        results = data.get("results", [])
        for result in results:
            finding = self._parse_result(result, command_used, agent_id)
            if finding:
                findings.append(finding)

        # Parse statistics
        stats = self._parse_stats(data)

        return {"findings": findings, "statistics": stats}

    def _parse_result(self, result: Dict, command_used: str, agent_id: str = None) -> Optional[Dict]:
        """Parse individual FFuf result"""
        url = result.get("url", "")
        status = result.get("status", 0)
        content_length = result.get("length", 0)
        words = result.get("words", 0)
        lines = result.get("lines", 0)

        if not url:
            return None

        # Determine severity based on status code and content
        severity = self._determine_severity(status, content_length)

        # Build description
        description_parts = [f"Status: {status}"]
        if content_length > 0:
            description_parts.append(f"Length: {content_length}")
        if words > 0:
            description_parts.append(f"Words: {words}")
        if lines > 0:
            description_parts.append(f"Lines: {lines}")

        description = " - ".join(description_parts)

        # Determine finding type based on status code
        finding_type = self._get_finding_type(status)

        return self._create_finding(
            id=f"ffuf_{hash(url)}",
            title=f"{finding_type} - {status}",
            description=description,
            target=url,
            severity=severity,
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
        )

    def _determine_severity(self, status: int, content_length: int) -> str:
        """Determine severity level based on status code and content length"""
        # High severity for successful responses (2xx, 3xx) with content
        if 200 <= status < 400 and content_length > 0:
            return "high"

        # Medium severity for redirects and client errors
        if 300 <= status < 500:
            return "medium"

        # Low severity for server errors and other cases
        return "low"

    def _get_finding_type(self, status: int) -> str:
        """Get finding type based on status code"""
        if 200 <= status < 300:
            return "Successful Response"
        elif 300 <= status < 400:
            return "Redirect Response"
        elif 400 <= status < 500:
            return "Client Error"
        elif 500 <= status < 600:
            return "Server Error"
        else:
            return "Unknown Response"

    def _parse_stats(self, data: Dict) -> Dict:
        """Parse FFuf statistics"""
        config = data.get("config", {})
        results = data.get("results", [])

        # Count by status code
        status_counts = {}
        for result in results:
            status = result.get("status", 0)
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count by content length
        length_counts = {}
        for result in results:
            length = result.get("length", 0)
            if length > 0:
                length_counts[length] = length_counts.get(length, 0) + 1

        return {
            "total_requests": len(results),
            "status_codes": status_counts,
            "content_lengths": length_counts,
            "target_url": config.get("url", "unknown"),
            "wordlist_size": config.get("wordlist", "unknown"),
        }

    def _parse_text_output(self, raw_output: str, command_used: str, agent_id: str = None) -> Dict:
        """Fallback parser for text-based ffuf output"""
        findings = []
        lines = raw_output.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for ffuf result lines
            # Example: "200     1234   /admin"
            if line and line[0].isdigit():
                finding = self._parse_text_result_line(line, agent_id)
                if finding:
                    findings.append(finding)

        return {
            "findings": findings,
            "statistics": {
                "total_requests": len(findings),
                "status_codes": {},
                "content_lengths": {},
                "target_url": "unknown",
                "wordlist_size": "unknown",
            },
        }

    def _parse_text_result_line(self, line: str, agent_id: str = None) -> Optional[Dict]:
        """Parse a result line from text output"""
        try:
            # Example: "200     1234   /admin"
            parts = line.split()
            if len(parts) >= 3:
                status = int(parts[0])
                length = int(parts[1]) if parts[1].isdigit() else 0
                url = parts[2]

                severity = self._determine_severity(status, length)
                finding_type = self._get_finding_type(status)

                description = f"Status: {status}"
                if length > 0:
                    description += f" - Length: {length}"

                return self._create_finding(
                    id=f"ffuf_text_{hash(url)}",
                    title=f"{finding_type} - {status}",
                    description=description,
                    target=url,
                    severity=severity,
                    agent_id=agent_id,
                    timestamp=datetime.now().isoformat(),
                )
        except:
            pass
        return None


# Test script
if __name__ == "__main__":
    parser = FFufParser()

    # Test with sample JSON data from file
    with open("app/services/tools/ffuf/sample.json", "r") as f:
        sample_json = f.read()

    result = parser.parse_single_result(
        sample_json, "ffuf -w wordlist.txt -u http://example.com/FUZZ"
    )

    print("=== FFUF PARSER TEST ===")
    print(f"Findings: {len(result['findings'])}")
    print(f"Statistics: {result['statistics']}")
    print()

    for finding in result["findings"]:
        print(f"[{finding.get('severity', 'INFO').upper()}] {finding['title']}")
        print(f"  Target: {finding['target']}")
        print(f"  Description: {finding['description']}")
        print()
