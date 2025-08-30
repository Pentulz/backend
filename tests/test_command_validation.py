import pytest

from app.services.tools.ffuf import FFufTool
from app.services.tools.nmap import NmapTool
from app.services.tools.tshark import TsharkTool


class TestNmapValidation:
    """Test nmap command validation"""

    @pytest.fixture
    def nmap_tool(self):
        return NmapTool()

    def test_valid_nmap_commands(self, nmap_tool):
        """Test valid nmap commands"""
        valid_cmds = [
            ["nmap", "-sT", "-p", "80,443", "192.168.1.1"],
            ["nmap", "-sS", "-p", "80-90", "scanme.nmap.org"],
            ["nmap", "-A", "192.168.1.0/24"],
            ["nmap", "-O", "192.168.1.1"],
        ]

        for cmd in valid_cmds:
            assert (
                nmap_tool.validate_command(cmd) is True
            ), f"Command {cmd} should be valid"

    def test_invalid_nmap_commands(self, nmap_tool):
        """Test invalid nmap commands"""
        invalid_cmds = [
            ["nmap", "-sT", "-p", "invalid_port", "192.168.1.1"],
            ["nmap", "-sT", "-p", "99999", "192.168.1.1"],
            ["nmap", "invalid", "command"],
            ["nmap", "-sT", "-p", "0", "192.168.1.1"],  # Port 0 is invalid
        ]

        for cmd in invalid_cmds:
            assert (
                nmap_tool.validate_command(cmd) is False
            ), f"Command {cmd} should be invalid"

    def test_nmap_port_validation(self, nmap_tool):
        """Test specific port validation scenarios"""
        # Valid port ranges
        valid_port_cmds = [
            ["nmap", "-sT", "-p", "1-100", "192.168.1.1"],
            ["nmap", "-sT", "-p", "80,443,8080", "192.168.1.1"],
            ["nmap", "-sT", "-p", "65535", "192.168.1.1"],
        ]

        for cmd in valid_port_cmds:
            assert (
                nmap_tool.validate_command(cmd) is True
            ), f"Port command {cmd} should be valid"

        # Invalid port ranges
        invalid_port_cmds = [
            ["nmap", "-sT", "-p", "100-50", "192.168.1.1"],  # Reverse range
            ["nmap", "-sT", "-p", "0-100", "192.168.1.1"],  # Port 0
            ["nmap", "-sT", "-p", "100-70000", "192.168.1.1"],  # Port > 65535
        ]

        for cmd in invalid_port_cmds:
            assert (
                nmap_tool.validate_command(cmd) is False
            ), f"Port command {cmd} should be invalid"


class TestFFufValidation:
    """Test ffuf command validation"""

    @pytest.fixture
    def ffuf_tool(self):
        return FFufTool()

    def test_valid_ffuf_commands(self, ffuf_tool):
        """Test valid ffuf commands"""
        valid_cmds = [
            [
                "ffuf",
                "-w",
                "/usr/share/wordlists/dirb/common.txt",
                "-u",
                "https://example.com/FUZZ",
            ],
            [
                "ffuf",
                "-w",
                "/usr/share/wordlists/dirb/common.txt",
                "-u",
                "https://example.com/FUZZ",
                "-mc",
                "200,301",
            ],
            [
                "ffuf",
                "-w",
                "/usr/share/wordlists/dirb/common.txt",
                "-u",
                "https://example.com/FUZZ",
                "-fs",
                "1234",
            ],
        ]

        for cmd in valid_cmds:
            assert (
                ffuf_tool.validate_command(cmd) is True
            ), f"Command {cmd} should be valid"

    def test_invalid_ffuf_commands(self, ffuf_tool):
        """Test invalid ffuf commands"""
        invalid_cmds = [
            [
                "ffuf",
                "-w",
                "/usr/share/wordlists/dirb/common.txt",
                "-u",
                "https://example.com/",
            ],  # No FUZZ
            [
                "ffuf",
                "-w",
                "/usr/share/wordlists/dirb/common.txt",
                "-u",
                "https://example.com/FUZZ",
                "-mc",
                "999",
            ],  # Invalid HTTP code
            [
                "ffuf",
                "-w",
                "/usr/share/wordlists/dirb/common.txt",
                "-u",
                "https://example.com/FUZZ",
                "-fs",
                "0",
            ],  # Size 0
        ]

        for cmd in invalid_cmds:
            assert (
                ffuf_tool.validate_command(cmd) is False
            ), f"Command {cmd} should be invalid"

    def test_ffuf_url_validation(self, ffuf_tool):
        """Test URL validation with FUZZ placeholder"""
        # Valid URLs with FUZZ
        valid_urls = [
            "https://example.com/FUZZ",
            "http://test.com/admin/FUZZ",
            "https://site.org/api/v1/FUZZ",
        ]

        for url in valid_urls:
            cmd = ["ffuf", "-w", "/usr/share/wordlists/dirb/common.txt", "-u", url]
            assert ffuf_tool.validate_command(cmd) is True, f"URL {url} should be valid"

        # Invalid URLs without FUZZ
        invalid_urls = [
            "https://example.com/",
            "http://test.com/admin",
            "https://site.org/api/v1",
        ]

        for url in invalid_urls:
            cmd = ["ffuf", "-w", "/usr/share/wordlists/dirb/common.txt", "-u", url]
            assert (
                ffuf_tool.validate_command(cmd) is False
            ), f"URL {url} should be invalid"


class TestTsharkValidation:
    """Test tshark command validation"""

    @pytest.fixture
    def tshark_tool(self):
        return TsharkTool()

    def test_valid_tshark_commands(self, tshark_tool):
        """Test valid tshark commands"""
        valid_cmds = [
            ["tshark", "-i", "eth0", "-c", "100", "-a", "duration:60"],
            ["tshark", "-r", "capture.pcap", "-a", "duration:300"],
            [
                "tshark",
                "-r",
                "capture.pcap",
                "-Y",
                "tcp.port == 80",
                "-a",
                "duration:300",
            ],
            ["tshark", "-i", "eth0", "-a", "duration:60"],
        ]

        for cmd in valid_cmds:
            assert (
                tshark_tool.validate_command(cmd) is True
            ), f"Command {cmd} should be valid"

    def test_invalid_tshark_commands(self, tshark_tool):
        """Test invalid tshark commands"""
        invalid_cmds = [
            [
                "tshark",
                "-i",
                "eth0",
                "-c",
                "invalid",
                "-a",
                "duration:60",
            ],  # Invalid count
            ["tshark", "-i", "eth0", "-c", "100", "-a", "duration:0"],  # Duration 0
            ["tshark", "-i", "eth0", "-c", "-1", "-a", "duration:60"],  # Negative count
        ]

        for cmd in invalid_cmds:
            assert (
                tshark_tool.validate_command(cmd) is False
            ), f"Command {cmd} should be invalid"

    def test_tshark_duration_validation(self, tshark_tool):
        """Test duration validation with prefix/suffix format"""
        # Valid durations
        valid_durations = [
            "duration:60",
            "duration:300",
            "duration:1",
        ]

        for duration in valid_durations:
            cmd = ["tshark", "-i", "eth0", "-a", duration]
            assert (
                tshark_tool.validate_command(cmd) is True
            ), f"Duration {duration} should be valid"

        # Invalid durations
        invalid_durations = [
            "duration:0",
            "duration:-1",
            "duration:abc",
        ]

        for duration in invalid_durations:
            cmd = ["tshark", "-i", "eth0", "-a", duration]
            assert (
                tshark_tool.validate_command(cmd) is False
            ), f"Duration {duration} should be invalid"


def test_all_tools_implement_validate_command():
    """Test that all tools implement the validate_command method"""
    tools = [NmapTool(), FFufTool(), TsharkTool()]

    for tool in tools:
        assert hasattr(
            tool, "validate_command"
        ), f"Tool {tool.__class__.__name__} missing validate_command method"
        assert callable(
            tool.validate_command
        ), f"Tool {tool.__class__.__name__} validate_command is not callable"


def test_export_arguments_are_added():
    """Test that export arguments are automatically added to validated commands"""

    # Test Nmap
    nmap = NmapTool()
    cmd = ["nmap", "-sT", "-p", "80,443", "192.168.1.1"]
    is_valid, complete_cmd = nmap.validate_and_prepare_command(cmd)
    print(f"Nmap command: {cmd}")
    print(f"Complete command: {complete_cmd}")
    print(f"Export format: {nmap.export_format}")
    print(f"Export args: {nmap.export_arguments}")
    assert is_valid is True
    assert complete_cmd[0] == "nmap"
    assert complete_cmd[-2:] == ["-oX", "-"]  # Nmap exports to XML

    # Test FFuf
    ffuf = FFufTool()
    cmd = [
        "ffuf",
        "-w",
        "/usr/share/wordlists/dirb/common.txt",
        "-u",
        "https://example.com/FUZZ",
    ]
    is_valid, complete_cmd = ffuf.validate_and_prepare_command(cmd)
    print(f"\nFFuf command: {cmd}")
    print(f"Complete command: {complete_cmd}")
    print(f"Export format: {ffuf.export_format}")
    print(f"Export args: {ffuf.export_arguments}")
    assert is_valid is True
    assert complete_cmd[0] == "ffuf"
    # FFuf has 4 export arguments: ['-of', 'json', '-o', '-']
    assert complete_cmd[-4:] == ["-of", "json", "-o", "-"]

    # Test Tshark
    tshark = TsharkTool()
    cmd = ["tshark", "-i", "eth0", "-c", "100", "-a", "duration:60"]
    is_valid, complete_cmd = tshark.validate_and_prepare_command(cmd)
    print(f"\nTshark command: {cmd}")
    print(f"Complete command: {complete_cmd}")
    print(f"Export format: {tshark.export_format}")
    print(f"Export args: {tshark.export_arguments}")
    assert is_valid is True
    assert complete_cmd[0] == "tshark"
    assert complete_cmd[-2:] == ["-T", "json"]  # Tshark exports to JSON


def test_invalid_commands_return_false():
    """Test that invalid commands return False and empty list"""
    nmap = NmapTool()
    invalid_cmd = ["nmap", "-sT", "-p", "invalid_port", "192.168.1.1"]
    is_valid, complete_cmd = nmap.validate_and_prepare_command(invalid_cmd)
    print(f"Invalid nmap command: {invalid_cmd}")
    print(f"Result: valid={is_valid}, command={complete_cmd}")
    assert is_valid is False
    assert complete_cmd == []
