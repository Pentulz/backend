import sys
from datetime import datetime
from pathlib import Path

import pytest

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.tools.ffuf.parser import FFufParser
from app.services.tools.nmap.parser import NmapParser
from app.services.tools.tool_manager import ToolManager
from app.services.tools.tshark.parser import TsharkParser


@pytest.fixture
def sample_data():
    """Fixture to provide sample data for testing"""
    sample_data = {}

    # Load Nmap sample
    nmap_sample_path = (
        backend_dir / "app" / "services" / "tools" / "nmap" / "sample.xml"
    )
    if nmap_sample_path.exists():
        with open(nmap_sample_path, "r") as f:
            sample_data["nmap"] = f.read()

    # Load FFuf sample
    ffuf_sample_path = (
        backend_dir / "app" / "services" / "tools" / "ffuf" / "sample.json"
    )
    if ffuf_sample_path.exists():
        with open(ffuf_sample_path, "r") as f:
            sample_data["ffuf"] = f.read()

    # Load Tshark sample
    tshark_sample_path = (
        backend_dir / "app" / "services" / "tools" / "tshark" / "sample.json"
    )
    if tshark_sample_path.exists():
        with open(tshark_sample_path, "r") as f:
            sample_data["tshark"] = f.read()

    return sample_data


@pytest.fixture
def mock_jobs(sample_data):
    """Fixture to provide mock job data for testing"""
    return [
        {
            "id": "job_001",
            "tool_name": "nmap",
            "command": "nmap -sS -p 22,80,443,8080 192.168.1.1",
            "raw_output": sample_data.get("nmap", ""),
            "created_at": datetime.now().isoformat(),
            "status": "completed",
        },
        {
            "id": "job_002",
            "tool_name": "ffuf",
            "command": "ffuf -w wordlist.txt -u http://example.com/FUZZ",
            "raw_output": sample_data.get("ffuf", ""),
            "created_at": datetime.now().isoformat(),
            "status": "completed",
        },
        {
            "id": "job_003",
            "tool_name": "tshark",
            "command": "tshark -i eth0 -c 10 -T json",
            "raw_output": sample_data.get("tshark", ""),
            "created_at": datetime.now().isoformat(),
            "status": "completed",
        },
    ]


@pytest.fixture
def tool_manager():
    """Fixture to provide ToolManager instance"""
    return ToolManager()


class TestParsers:
    """Test class for individual parsers"""

    def test_nmap_parser_with_sample_data(self, sample_data):
        """Test Nmap parser with sample XML data"""
        if "nmap" not in sample_data:
            pytest.skip("Nmap sample data not available")

        parser = NmapParser()
        result = parser.parse_single_result(
            sample_data["nmap"], "nmap -sS -p 22,80,443,8080 192.168.1.1", "test_agent_001"
        )

        # Verify structure
        assert "findings" in result
        assert "statistics" in result
        assert isinstance(result["findings"], list)
        assert isinstance(result["statistics"], dict)

        # Verify findings
        assert len(result["findings"]) > 0

        # Verify statistics
        stats = result["statistics"]
        assert "total_hosts" in stats
        assert "up_hosts" in stats
        assert "open_ports" in stats

        # Check for specific findings
        port_findings = [f for f in result["findings"] if "port" in f.get("id", "")]
        assert len(port_findings) > 0

        # Verify finding structure
        for finding in result["findings"]:
            assert "id" in finding
            assert "title" in finding
            assert "description" in finding
            assert "target" in finding
            assert "severity" in finding
            assert "timestamp" in finding

    def test_ffuf_parser_with_sample_data(self, sample_data):
        """Test FFuf parser with sample JSON data"""
        if "ffuf" not in sample_data:
            pytest.skip("FFuf sample data not available")

        parser = FFufParser()
        result = parser.parse_single_result(
            sample_data["ffuf"], "ffuf -w wordlist.txt -u http://example.com/FUZZ", "test_agent_002"
        )

        # Verify structure
        assert "findings" in result
        assert "statistics" in result
        assert isinstance(result["findings"], list)
        assert isinstance(result["statistics"], dict)

        # Verify findings
        assert len(result["findings"]) > 0

        # Verify statistics
        stats = result["statistics"]
        assert "total_requests" in stats
        assert "status_codes" in stats
        assert "target_url" in stats

        # Check for specific findings
        url_findings = [f for f in result["findings"] if "ffuf" in f.get("id", "")]
        assert len(url_findings) > 0

        # Verify finding structure
        for finding in result["findings"]:
            assert "id" in finding
            assert "title" in finding
            assert "description" in finding
            assert "target" in finding
            assert "severity" in finding
            assert "timestamp" in finding

    def test_tshark_parser_with_sample_data(self, sample_data):
        """Test Tshark parser with sample JSON data"""
        if "tshark" not in sample_data:
            pytest.skip("Tshark sample data not available")

        parser = TsharkParser()
        result = parser.parse_single_result(
            sample_data["tshark"], "tshark -i eth0 -c 10 -T json", "test_agent_003"
        )

        # Verify structure
        assert "findings" in result
        assert "statistics" in result
        assert isinstance(result["findings"], list)
        assert isinstance(result["statistics"], dict)

        # Verify findings
        assert len(result["findings"]) > 0

        # Verify statistics
        stats = result["statistics"]
        assert "packets_analyzed" in stats or "total_packets" in stats
        assert "protocols_seen" in stats or "protocols" in stats

        # Verify finding structure
        for finding in result["findings"]:
            assert "id" in finding
            assert "title" in finding
            assert "description" in finding
            assert "target" in finding
            assert "severity" in finding
            assert "timestamp" in finding


class TestToolManager:
    """Test class for ToolManager functionality"""

    def test_tool_manager_initialization(self, tool_manager):
        """Test that ToolManager can be initialized"""
        assert tool_manager is not None
        assert hasattr(tool_manager, "get_tool")
        assert hasattr(tool_manager, "parse_results")

    def test_tool_manager_get_tool(self, tool_manager):
        """Test that ToolManager can retrieve tools"""
        # Test Nmap tool retrieval
        nmap_tool = tool_manager.get_tool("nmap")
        assert nmap_tool is not None
        assert hasattr(nmap_tool, "parse_results")

        # Test FFuf tool retrieval
        ffuf_tool = tool_manager.get_tool("ffuf")
        assert ffuf_tool is not None
        assert hasattr(ffuf_tool, "parse_results")

        # Test Tshark tool retrieval
        tshark_tool = tool_manager.get_tool("tshark")
        assert tshark_tool is not None
        assert hasattr(tshark_tool, "parse_results")

    def test_tool_manager_parse_results(self, tool_manager, sample_data):
        """Test that ToolManager can parse results for each tool"""
        for tool_name, data in sample_data.items():
            result = tool_manager.parse_results(
                tool_name, data, f"{tool_name} test command", f"test_agent_{tool_name}"
            )

            # Verify basic structure
            assert result is not None
            assert "findings" in result
            assert "statistics" in result
            assert len(result["findings"]) > 0


class TestReportGeneration:
    """Test class for report generation functionality"""

    def test_basic_report_generation(self, tool_manager, sample_data):
        """Test basic report generation with sample data"""
        if not sample_data:
            pytest.skip("No sample data available")

        # Generate findings for each tool
        all_findings = []
        all_statistics = {}

        for tool, data in sample_data.items():
            result = tool_manager.parse_results(tool, data, f"{tool} test command", f"test_agent_{tool}")

            if result and "findings" in result and "statistics" in result:
                all_findings.extend(result["findings"])
                all_statistics[tool] = result["statistics"]

        # Verify we have findings
        assert len(all_findings) > 0

        # Create a simple report structure
        report = {
            "metadata": {
                "report_id": "test_report_001",
                "name": "Test Security Assessment Report",
                "created_at": datetime.now().isoformat(),
                "total_jobs": len(sample_data),
            },
            "summary": {
                "total_findings": len(all_findings),
                "tools_used": list(sample_data.keys()),
                "severity_distribution": {},
            },
            "findings_by_tool": {},
            "all_findings": all_findings,
        }

        # Count findings by severity
        for finding in all_findings:
            severity = finding.get("severity", "unknown")
            report["summary"]["severity_distribution"][severity] = (
                report["summary"]["severity_distribution"].get(severity, 0) + 1
            )

        # Group findings by tool
        for tool in sample_data.keys():
            tool_findings = [f for f in all_findings if tool in f.get("id", "")]
            report["findings_by_tool"][tool] = {
                "tool_name": tool.title(),
                "jobs_count": 1,
                "findings": tool_findings,
                "statistics": all_statistics.get(tool, {}),
            }

        # Verify report structure
        assert report["summary"]["total_findings"] > 0
        assert len(report["summary"]["tools_used"]) > 0
        assert len(report["summary"]["severity_distribution"]) > 0

        # Verify findings by tool
        for tool, tool_data in report["findings_by_tool"].items():
            assert "tool_name" in tool_data
            assert "findings" in tool_data
            assert "statistics" in tool_data

    def test_finding_severity_levels(self, tool_manager, sample_data):
        """Test that findings have appropriate severity levels"""
        if not sample_data:
            pytest.skip("No sample data available")

        severity_levels = set()

        for tool, data in sample_data.items():
            result = tool_manager.parse_results(tool, data, f"{tool} test command", f"test_agent_{tool}")

            if result and "findings" in result:
                for finding in result["findings"]:
                    severity = finding.get("severity", "unknown")
                    severity_levels.add(severity)

                    # Verify severity is one of the expected values
                    assert severity in ["low", "medium", "high", "critical", "info"]

        # Should have multiple severity levels
        assert len(severity_levels) > 1

    def test_agent_id_in_findings(self, tool_manager, sample_data):
        """Test that agent_id is correctly included in findings"""
        if not sample_data:
            pytest.skip("No sample data available")

        for tool, data in sample_data.items():
            test_agent_id = f"test_agent_{tool}"
            result = tool_manager.parse_results(tool, data, f"{tool} test command", test_agent_id)

            if result and "findings" in result:
                for finding in result["findings"]:
                    # Verify agent_id is present and correct
                    assert "agent_id" in finding
                    assert finding["agent_id"] == test_agent_id

    def test_finding_targets(self, tool_manager, sample_data):
        """Test that findings have appropriate targets"""
        if not sample_data:
            pytest.skip("No sample data available")

        for tool, data in sample_data.items():
            result = tool_manager.parse_results(tool, data, f"{tool} test command", f"test_agent_{tool}")

            if result and "findings" in result:
                for finding in result["findings"]:
                    target = finding.get("target", "")
                    assert target != ""

                    # Verify target format based on tool
                    if tool == "nmap":
                        # Nmap targets should contain IP addresses or hostnames
                        # More flexible check for nmap targets
                        assert (
                            any(
                                ip in target
                                for ip in [
                                    "192.168.1.1",
                                    "router.local",
                                    "internetbox.home",
                                ]
                            )
                            or ":" in target
                        )
                    elif tool == "ffuf":
                        # FFuf targets should be URLs
                        assert (
                            "http://" in target
                            or "https://" in target
                            or "example.com" in target
                        )
                    elif tool == "tshark":
                        # Tshark targets should contain protocol information or IP addresses
                        assert (
                            any(
                                proto in target.lower()
                                for proto in ["arp", "tcp", "udp", "eth"]
                            )
                            or "packet" in target.lower()
                            or "→" in target
                            or any(
                                ip in target
                                for ip in ["172.21", "192.168", "10.0", "127.0"]
                            )
                        )

    def test_statistics_consistency(self, tool_manager, sample_data):
        """Test that statistics are consistent across different tools"""
        if not sample_data:
            pytest.skip("No sample data available")

        for tool, data in sample_data.items():
            result = tool_manager.parse_results(tool, data, f"{tool} test command", f"test_agent_{tool}")

            if result and "statistics" in result:
                stats = result["statistics"]

                # Verify statistics are not empty
                assert len(stats) > 0

                # Verify statistics values are reasonable
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        assert value >= 0
                    elif isinstance(value, dict):
                        assert len(value) >= 0


class TestErrorHandling:
    """Test class for error handling scenarios"""

    def test_parsers_with_invalid_data(self):
        """Test that parsers handle invalid data gracefully"""
        invalid_data = "This is not valid XML or JSON data"

        # Test Nmap parser with invalid data
        nmap_parser = NmapParser()
        result = nmap_parser.parse_single_result(invalid_data, "nmap invalid", "test_agent_001")
        assert "findings" in result
        assert "statistics" in result

        # Test FFuf parser with invalid data
        ffuf_parser = FFufParser()
        result = ffuf_parser.parse_single_result(invalid_data, "ffuf invalid", "test_agent_002")
        assert "findings" in result
        assert "statistics" in result

        # Test Tshark parser with invalid data
        tshark_parser = TsharkParser()
        result = tshark_parser.parse_single_result(invalid_data, "tshark invalid", "test_agent_003")
        assert "findings" in result
        assert "statistics" in result

    def test_tool_manager_with_unknown_tool(self, tool_manager):
        """Test ToolManager behavior with unknown tools"""
        # Test getting unknown tool
        unknown_tool = tool_manager.get_tool("unknown_tool")
        assert unknown_tool is None

        # Test parsing with unknown tool
        result = tool_manager.parse_results(
            "unknown_tool", "some data", "unknown command", "test_agent_unknown"
        )
        assert result is None
