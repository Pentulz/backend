import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional

from app.services.tools.tool_parser import BaseParser


class NmapParser(BaseParser):
    """Parser for Nmap XML output"""

    def parse_single_result(self, raw_output: str, command_used: str, agent_id: str = None) -> Dict:
        """
        Parse Nmap XML output to standard format
        Returns: {
            'findings': [Finding...],
            'statistics': {...}
        }
        """
        try:
            # Try to parse as XML first
            root = ET.fromstring(raw_output)
            return self._parse_xml_output(root, command_used, agent_id)
        except ET.ParseError:
            # Fall back to text parsing if XML fails
            return self._parse_text_output(raw_output, command_used, agent_id)

    def _parse_xml_output(self, root: ET.Element, command_used: str, agent_id: str = None) -> Dict:
        """Parse Nmap XML output"""
        findings = []

        # Parse host information
        for host in root.findall(".//host"):
            host_findings = self._parse_host(host, agent_id)
            findings.extend(host_findings)

        # Parse scan statistics
        stats = self._parse_scan_stats(root)

        return {"findings": findings, "statistics": stats}

    def _parse_host(self, host: ET.Element, agent_id: str = None) -> List[Dict]:
        """Parse individual host information"""
        findings = []

        # Get host address info
        address_elem = host.find("address")
        if address_elem is not None:
            host_ip = address_elem.get("addr", "Unknown")
        else:
            host_ip = "Unknown"

        # Get hostname if available
        hostname_elem = host.find("hostnames/hostname")
        hostname = hostname_elem.get("name", "") if hostname_elem is not None else ""

        # Parse ports and services
        for port_elem in host.findall(".//port"):
            port_finding = self._parse_port(port_elem, host_ip, hostname, agent_id)
            if port_finding:
                findings.append(port_finding)

        # Parse OS detection
        os_elem = host.find("os/osmatch")
        if os_elem is not None:
            os_name = os_elem.get("name", "Unknown OS")
            os_accuracy = os_elem.get("accuracy", "0")

            findings.append(
                self._create_finding(
                    id=f"os_{host_ip}",
                    title="Operating System Detection",
                    description=f"Detected OS: {os_name} (Accuracy: {os_accuracy}%)",
                    target=host_ip,
                    severity="info",
                    agent_id=agent_id,
                    timestamp=datetime.now().isoformat(),
                )
            )

        return findings

    def _parse_port(
        self, port_elem: ET.Element, host_ip: str, hostname: str, agent_id: str = None
    ) -> Optional[Dict]:
        """Parse individual port information"""
        port_id = port_elem.get("portid", "0")
        protocol = port_elem.get("protocol", "unknown")
        state = port_elem.find("state")
        service = port_elem.find("service")

        if state is None or state.get("state") != "open":
            return None

        # Determine severity based on port and service
        severity = self._determine_port_severity(port_id, service)

        # Build description
        service_name = (
            service.get("name", "unknown") if service is not None else "unknown"
        )
        service_product = service.get("product", "") if service is not None else ""
        service_version = service.get("version", "") if service is not None else ""

        description_parts = [f"Open {protocol} port {port_id}"]
        if service_name != "unknown":
            description_parts.append(f"Service: {service_name}")
        if service_product:
            description_parts.append(f"Product: {service_product}")
        if service_version:
            description_parts.append(f"Version: {service_version}")

        description = " - ".join(description_parts)

        target = f"{host_ip}:{port_id}"
        if hostname:
            target = f"{hostname} ({host_ip}):{port_id}"

        return self._create_finding(
            id=f"port_{host_ip}_{port_id}",
            title=f"Open Port {port_id}/{protocol}",
            description=description,
            target=target,
            severity=severity,
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
        )

    def _determine_port_severity(
        self, port_id: str, service: Optional[ET.Element]
    ) -> str:
        """Determine severity level based on port and service"""
        port_num = int(port_id) if port_id.isdigit() else 0

        # High-risk ports
        if port_num in [
            21,
            22,
            23,
            25,
            53,
            80,
            110,
            143,
            443,
            993,
            995,
            1433,
            1521,
            3306,
            3389,
            5432,
            5900,
            6379,
            8080,
            8443,
        ]:
            return "high"

        # Medium-risk ports
        if port_num in [
            135,
            139,
            445,
            1433,
            1521,
            3306,
            3389,
            5432,
            5900,
            6379,
            8080,
            8443,
        ]:
            return "medium"

        # Check service name for additional context
        if service is not None:
            service_name = service.get("name", "").lower()
            if service_name in [
                "ssh",
                "telnet",
                "ftp",
                "smtp",
                "http",
                "https",
                "mysql",
                "postgresql",
                "redis",
                "rdp",
            ]:
                return "high"
            if service_name in ["dns", "pop3", "imap", "smtp", "ldap", "kerberos"]:
                return "medium"

        return "low"

    def _parse_scan_stats(self, root: ET.Element) -> Dict:
        """Parse scan statistics"""
        stats = {
            "total_hosts": 0,
            "up_hosts": 0,
            "down_hosts": 0,
            "total_ports": 0,
            "open_ports": 0,
            "scan_duration": "0s",
        }

        # Get host counts
        hosts_elem = root.find("runstats/hosts")
        if hosts_elem is not None:
            stats["total_hosts"] = int(hosts_elem.get("total", "0"))
            stats["up_hosts"] = int(hosts_elem.get("up", "0"))
            stats["down_hosts"] = int(hosts_elem.get("down", "0"))

        # Get scan duration
        finished_elem = root.find("runstats/finished")
        if finished_elem is not None:
            stats["scan_duration"] = finished_elem.get("elapsed", "0s")

        # Count ports (this is approximate)
        open_ports = 0
        for port in root.findall(".//port"):
            state = port.find("state")
            if state is not None and state.get("state") == "open":
                open_ports += 1
        stats["open_ports"] = open_ports

        return stats

    def _parse_text_output(self, raw_output: str, command_used: str, agent_id: str = None) -> Dict:
        """Fallback parser for text-based nmap output"""
        findings = []
        lines = raw_output.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for port scan results
            if "open" in line and ("tcp" in line or "udp" in line):
                finding = self._parse_text_port_line(line, agent_id)
                if finding:
                    findings.append(finding)

            # Look for host discovery
            elif "Nmap scan report for" in line:
                finding = self._parse_text_host_line(line, agent_id)
                if finding:
                    findings.append(finding)

        return {
            "findings": findings,
            "statistics": {
                "total_hosts": 1,
                "up_hosts": 1,
                "down_hosts": 0,
                "total_ports": len([f for f in findings if "port" in f.get("id", "")]),
                "open_ports": len([f for f in findings if "port" in f.get("id", "")]),
                "scan_duration": "unknown",
            },
        }

    def _parse_text_port_line(self, line: str, agent_id: str = None) -> Optional[Dict]:
        """Parse a port line from text output"""
        try:
            # Example: "22/tcp   open  ssh"
            parts = line.split()
            if len(parts) >= 3:
                port_proto = parts[0]
                state = parts[1]
                service = parts[2] if len(parts) > 2 else "unknown"

                if state == "open":
                    port_id, protocol = port_proto.split("/")

                    severity = self._determine_port_severity(port_id, None)

                    return self._create_finding(
                        id=f"port_text_{port_id}",
                        title=f"Open Port {port_id}/{protocol}",
                        description=f"Open {protocol} port {port_id} - Service: {service}",
                        target=f"Port {port_id}",
                        severity=severity,
                        agent_id=agent_id,
                        timestamp=datetime.now().isoformat(),
                    )
        except:
            pass
        return None

    def _parse_text_host_line(self, line: str, agent_id: str = None) -> Optional[Dict]:
        """Parse a host line from text output"""
        try:
            # Example: "Nmap scan report for example.com (192.168.1.1)"
            if "Nmap scan report for" in line:
                target = line.replace("Nmap scan report for", "").strip()

                return self._create_finding(
                    id="host_discovery",
                    title="Host Discovery",
                    description="Nmap discovered host",
                    target=target,
                    severity="info",
                    agent_id=agent_id,
                    timestamp=datetime.now().isoformat(),
                )
        except:
            pass
        return None


# Test script
if __name__ == "__main__":
    parser = NmapParser()

    # Test with sample XML data from file
    with open("app/services/tools/nmap/sample.xml", "r") as f:
        sample_xml = f.read()

    result = parser.parse_single_result(
        sample_xml, "nmap -sS -p 22,80,443,8080 192.168.1.1"
    )

    print("=== NMAP PARSER TEST ===")
    print(f"Findings: {len(result['findings'])}")
    print(f"Statistics: {result['statistics']}")
    print()

    for finding in result["findings"]:
        print(f"[{finding.get('severity', 'INFO').upper()}] {finding['title']}")
        print(f"  Target: {finding['target']}")
        print(f"  Description: {finding['description']}")
        print()
