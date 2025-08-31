from unittest.mock import AsyncMock

import pytest

from app.schemas.jobs import JobAction, JobCreate
from app.services.tools.tool_manager import ToolManager


class TestJobCreation:
    """Test job creation functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def tool_manager(self):
        """Real tool manager for testing"""
        return ToolManager()

    def test_create_valid_nmap_job(self, tool_manager):
        """Test creating a valid Nmap job"""
        # Create job action
        action = JobAction(
            name="nmap",
            variant="tcp_connect_scan",
            args={"target": "192.168.1.171", "ports": "80,443,1000-2000"},
        )

        # Create job
        job = JobCreate(
            name="Port Scan Internal Network",
            description="Scan internal network for open ports and services",
            agent_id="550e8400-e29b-41d4-a716-446655440001",
            action=action,
        )

        # Verify job structure
        assert job.name == "Port Scan Internal Network"
        assert job.action.name == "nmap"
        assert job.action.variant == "tcp_connect_scan"
        assert job.action.args["target"] == "192.168.1.171"
        assert job.action.args["ports"] == "80,443,1000-2000"

        # Test command building
        command = tool_manager.build_command_from_variant(
            job.action.name, job.action.variant, job.action.args
        )
        assert command is not None
        assert "-sT" in command
        assert "-p" in command
        assert "192.168.1.171" in command

    def test_create_valid_ffuf_job(self, tool_manager):
        """Test creating a valid FFuf job"""
        action = JobAction(
            name="ffuf",
            variant="directory_fuzzing",
            args={
                "wordlist": "/usr/share/wordlists/dirb/common.txt",
                "url": "https://example.com/FUZZ",
            },
        )

        job = JobCreate(
            name="Web Directory Fuzzing",
            description="Fuzz web directories for hidden files",
            agent_id="550e8400-e29b-41d4-a716-446655440001",
            action=action,
        )

        assert job.action.name == "ffuf"
        assert job.action.variant == "directory_fuzzing"

        # Test command building
        command = tool_manager.build_command_from_variant(
            job.action.name, job.action.variant, job.action.args
        )
        assert command is not None
        assert "-w" in command
        assert "-u" in command

    def test_create_valid_tshark_job(self, tool_manager):
        """Test creating a valid Tshark job"""
        action = JobAction(
            name="tshark",
            variant="live_capture_duration_only",
            args={"interface": "eth0", "duration": "60"},
        )

        job = JobCreate(
            name="Network Traffic Capture",
            description="Capture network traffic for 60 seconds",
            agent_id="550e8400-e29b-41d4-a716-446655440001",
            action=action,
        )

        assert job.action.name == "tshark"
        assert job.action.variant == "live_capture_duration_only"

        # Test command building
        command = tool_manager.build_command_from_variant(
            job.action.name, job.action.variant, job.action.args
        )
        assert command is not None
        assert "-i" in command
        assert "eth0" in command

    def test_invalid_tool_name(self):
        """Test job creation with invalid tool name"""
        action = JobAction(
            name="invalid_tool", variant="some_variant", args={"target": "192.168.1.1"}
        )

        job = JobCreate(
            name="Invalid Tool Job",
            description="Job with invalid tool",
            agent_id="550e8400-e29b-41d4-a716-446655440001",
            action=action,
        )

        # This should pass Pydantic validation but fail in service validation
        assert job.action.name == "invalid_tool"

    def test_invalid_variant(self):
        """Test job creation with invalid variant"""
        action = JobAction(
            name="nmap", variant="invalid_variant", args={"target": "192.168.1.1"}
        )

        job = JobCreate(
            name="Invalid Variant Job",
            description="Job with invalid variant",
            agent_id="550e8400-e29b-41d4-a716-446655440001",
            action=action,
        )

        # This should pass Pydantic validation but fail in service validation
        assert job.action.variant == "invalid_variant"

    def test_missing_required_arguments(self):
        """Test job creation with missing required arguments"""
        action = JobAction(
            name="nmap",
            variant="tcp_connect_scan",
            args={
                "target": "192.168.1.1"
                # Missing "ports" argument
            },
        )

        job = JobCreate(
            name="Incomplete Job",
            description="Job with missing arguments",
            agent_id="550e8400-e29b-41d4-a716-446655440001",
            action=action,
        )

        # This should pass Pydantic validation but fail in service validation
        assert "ports" not in job.action.args

    def test_job_action_validation(self):
        """Test JobAction validation rules"""
        # Valid action
        valid_action = JobAction(
            name="nmap",
            variant="tcp_connect_scan",
            args={"target": "192.168.1.1", "ports": "80,443"},
        )
        assert valid_action.name == "nmap"
        assert valid_action.variant == "tcp_connect_scan"

        # Test empty name (should fail)
        with pytest.raises(ValueError, match=".*Tool name cannot be empty.*"):
            JobAction(name="", variant="test", args={})

        # Test empty variant (should fail)
        with pytest.raises(ValueError, match=".*Template variant cannot be empty.*"):
            JobAction(name="nmap", variant="", args={})

        # Test invalid args type (should fail)
        with pytest.raises(ValueError, match=".*Input should be a valid dictionary.*"):
            JobAction(name="nmap", variant="test", args="not_a_dict")

    def test_job_create_validation(self):
        """Test JobCreate validation rules"""
        # Valid job
        valid_job = JobCreate(
            name="Test Job",
            description="Test description",
            agent_id="550e8400-e29b-41d4-a716-446655440001",
            action=JobAction(
                name="nmap",
                variant="tcp_connect_scan",
                args={"target": "192.168.1.1", "ports": "80,443"},
            ),
        )
        assert valid_job.name == "Test Job"

        # Test empty name (should fail)
        with pytest.raises(
            ValueError, match=".*String should have at least 1 character.*"
        ):
            JobCreate(
                name="",
                description="Test",
                agent_id="550e8400-e29b-41d4-a716-446655440001",
                action=JobAction(
                    name="nmap",
                    variant="tcp_connect_scan",
                    args={"target": "192.168.1.1", "ports": "80,443"},
                ),
            )


class TestToolVariants:
    """Test tool variants functionality"""

    def test_available_variants(self):
        """Test that all expected variants are available"""
        manager = ToolManager()
        tools = manager.get_available_tools()

        # Check Nmap variants
        nmap_tool = next(t for t in tools if t["id"] == "nmap")
        nmap_variants = [v["id"] for v in nmap_tool["attributes"]["variants"]]

        expected_nmap_variants = [
            "list_scan",
            "tcp_connect_scan",
            "tcp_syn_scan",
            "service_version_detection",
            "os_detection",
            "aggressive_scan",
        ]

        for variant in expected_nmap_variants:
            assert variant in nmap_variants, f"Missing Nmap variant: {variant}"

        # Check FFuf variants
        ffuf_tool = next(t for t in tools if t["id"] == "ffuf")
        ffuf_variants = [v["id"] for v in ffuf_tool["attributes"]["variants"]]

        expected_ffuf_variants = [
            "directory_fuzzing",
            "status_code_matching",
            "size_filtering",
        ]

        for variant in expected_ffuf_variants:
            assert variant in ffuf_variants, f"Missing FFuf variant: {variant}"

    def test_variant_argument_definitions(self):
        """Test that variants have proper argument definitions"""
        manager = ToolManager()
        tools = manager.get_available_tools()

        # Test Nmap TCP Connect Scan
        nmap_tool = next(t for t in tools if t["id"] == "nmap")
        tcp_scan_variant = next(
            v
            for v in nmap_tool["attributes"]["variants"]
            if v["id"] == "tcp_connect_scan"
        )

        required_args = [
            arg["name"]
            for arg in tcp_scan_variant["argument_definitions"]
            if arg["required"]
        ]

        assert "target" in required_args
        assert "ports" in required_args
        assert len(required_args) == 2

        # Test FFuf Directory Fuzzing
        ffuf_tool = next(t for t in tools if t["id"] == "ffuf")
        dir_fuzzing_variant = next(
            v
            for v in ffuf_tool["attributes"]["variants"]
            if v["id"] == "directory_fuzzing"
        )

        required_args = [
            arg["name"]
            for arg in dir_fuzzing_variant["argument_definitions"]
            if arg["required"]
        ]

        assert "wordlist" in required_args
        assert "url" in required_args
        assert len(required_args) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
