import json
from typing import Dict, Optional

from app.services.tools.tool_parser import BaseParser


class TsharkParser(BaseParser):
    """Parser for tshark JSON output"""

    def __init__(self):
        # Common service ports for identification
        self.service_ports = {
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            53: "DNS",
            21: "FTP",
            25: "SMTP",
            110: "POP3",
            143: "IMAP",
            3306: "MySQL",
            5432: "PostgreSQL",
            1433: "MSSQL",
            445: "SMB",
            139: "NetBIOS",
            3389: "RDP",
        }

    def parse_single_result(self, raw_output: str, command_used: str) -> Dict:
        """Parse tshark JSON output into standardized findings"""
        try:
            packets = json.loads(raw_output)
        except json.JSONDecodeError:
            return {"findings": [], "statistics": {"error": "Invalid JSON format"}}

        findings = []
        protocols_seen = {}

        for packet in packets:
            try:
                layers = packet["_source"]["layers"]
                frame_num = layers["frame"]["frame.number"]
                timestamp = layers["frame"]["frame.time_epoch"]

                # Parse different protocol types
                finding = None
                if "arp" in layers:
                    finding = self._parse_arp_packet(layers, frame_num, timestamp)
                    protocols_seen["ARP"] = protocols_seen.get("ARP", 0) + 1

                elif "tcp" in layers and "ip" in layers:
                    finding = self._parse_tcp_packet(layers, frame_num, timestamp)
                    protocols_seen["TCP"] = protocols_seen.get("TCP", 0) + 1

                elif "udp" in layers and "ip" in layers:
                    finding = self._parse_udp_packet(layers, frame_num, timestamp)
                    protocols_seen["UDP"] = protocols_seen.get("UDP", 0) + 1

                elif "http" in layers:
                    finding = self._parse_http_packet(layers, frame_num, timestamp)
                    protocols_seen["HTTP"] = protocols_seen.get("HTTP", 0) + 1

                elif "dns" in layers:
                    finding = self._parse_dns_packet(layers, frame_num, timestamp)
                    protocols_seen["DNS"] = protocols_seen.get("DNS", 0) + 1

                elif "icmp" in layers:
                    finding = self._parse_icmp_packet(layers, frame_num, timestamp)
                    protocols_seen["ICMP"] = protocols_seen.get("ICMP", 0) + 1

                else:
                    finding = self._parse_generic_packet(layers, frame_num, timestamp)

                if finding:
                    findings.append(finding)

            except Exception:
                # Skip malformed packets
                continue

        return {
            "findings": findings,
            "statistics": {
                "packets_analyzed": len(packets),
                "protocols_seen": protocols_seen,
            },
        }

    def _parse_arp_packet(
        self, layers: Dict, frame_num: str, timestamp: str
    ) -> Optional[Dict]:
        """Parse ARP packet"""
        arp = layers["arp"]
        src_ip = arp.get("arp.src.proto_ipv4")
        dst_ip = arp.get("arp.dst.proto_ipv4")
        opcode = arp.get("arp.opcode")

        if not src_ip or not dst_ip:
            return None

        arp_type = "Request" if opcode == "1" else "Reply"

        return self._create_finding(
            id=f"arp_{frame_num}",
            title=f"ARP {arp_type}",
            description=f"ARP {arp_type.lower()} between {src_ip} and {dst_ip}",
            target=f"{src_ip} → {dst_ip}",
            timestamp=timestamp,
        )

    def _parse_tcp_packet(
        self, layers: Dict, frame_num: str, timestamp: str
    ) -> Optional[Dict]:
        """Parse TCP packet"""
        tcp = layers["tcp"]
        ip = layers["ip"]

        src_ip = ip.get("ip.src")
        dst_ip = ip.get("ip.dst")
        src_port = tcp.get("tcp.srcport")
        dst_port = tcp.get("tcp.dstport")

        if not all([src_ip, dst_ip, src_port, dst_port]):
            return None

        service = self.service_ports.get(int(dst_port), f"Port {dst_port}")

        return self._create_finding(
            id=f"tcp_{frame_num}",
            title=f"TCP Traffic to {service}",
            description=f"TCP connection from {src_ip}:{src_port} to {dst_ip}:{dst_port}",
            target=f"{src_ip}:{src_port} → {dst_ip}:{dst_port}",
            timestamp=timestamp,
        )

    def _parse_udp_packet(
        self, layers: Dict, frame_num: str, timestamp: str
    ) -> Optional[Dict]:
        """Parse UDP packet"""
        udp = layers["udp"]
        ip = layers["ip"]

        src_ip = ip.get("ip.src")
        dst_ip = ip.get("ip.dst")
        src_port = udp.get("udp.srcport")
        dst_port = udp.get("udp.dstport")

        if not all([src_ip, dst_ip, src_port, dst_port]):
            return None

        service = self.service_ports.get(int(dst_port), f"Port {dst_port}")

        return self._create_finding(
            id=f"udp_{frame_num}",
            title=f"UDP Traffic to {service}",
            description=f"UDP communication from {src_ip}:{src_port} to {dst_ip}:{dst_port}",
            target=f"{src_ip}:{src_port} → {dst_ip}:{dst_port}",
            timestamp=timestamp,
        )

    def _parse_http_packet(
        self, layers: Dict, frame_num: str, timestamp: str
    ) -> Optional[Dict]:
        """Parse HTTP packet"""
        http = layers["http"]
        ip = layers.get("ip", {})

        method = http.get("http.request.method")
        uri = http.get("http.request.uri")
        host = http.get("http.host")
        response_code = http.get("http.response.code")

        src_ip = ip.get("ip.src", "unknown")
        dst_ip = ip.get("ip.dst", "unknown")

        if method and uri:
            # HTTP Request
            return self._create_finding(
                id=f"http_{frame_num}",
                title=f"HTTP {method} Request",
                description=f"{method} request to {host}{uri}",
                target=f"{host}{uri}",
                timestamp=timestamp,
            )

        elif response_code:
            # HTTP Response
            return self._create_finding(
                id=f"http_{frame_num}",
                title=f"HTTP {response_code} Response",
                description=f"HTTP response code {response_code}",
                target=f"{src_ip} → {dst_ip}",
                timestamp=timestamp,
            )

        return None

    def _parse_dns_packet(
        self, layers: Dict, frame_num: str, timestamp: str
    ) -> Optional[Dict]:
        """Parse DNS packet"""
        dns = layers["dns"]

        query_name = dns.get("dns.qry.name")
        query_type = dns.get("dns.qry.type")

        if query_name:
            return self._create_finding(
                id=f"dns_{frame_num}",
                title="DNS Query",
                description=f"DNS {query_type} query for {query_name}",
                target=query_name,
                timestamp=timestamp,
            )

        return self._create_finding(
            id=f"dns_{frame_num}",
            title="DNS Response",
            description="DNS response packet",
            target="DNS Server",
            timestamp=timestamp,
        )

    def _parse_icmp_packet(
        self, layers: Dict, frame_num: str, timestamp: str
    ) -> Optional[Dict]:
        """Parse ICMP packet"""
        icmp = layers["icmp"]
        ip = layers.get("ip", {})

        src_ip = ip.get("ip.src")
        dst_ip = ip.get("ip.dst")
        icmp_type = icmp.get("icmp.type")

        if not src_ip or not dst_ip:
            return None

        # Simple ICMP type identification
        icmp_types = {
            "0": "Echo Reply",
            "3": "Destination Unreachable",
            "8": "Echo Request (Ping)",
            "11": "Time Exceeded",
        }

        icmp_name = icmp_types.get(icmp_type, f"Type {icmp_type}")

        return self._create_finding(
            id=f"icmp_{frame_num}",
            title=f"ICMP {icmp_name}",
            description=f"ICMP {icmp_name} from {src_ip} to {dst_ip}",
            target=f"{src_ip} → {dst_ip}",
            timestamp=timestamp,
        )

    def _parse_generic_packet(
        self, layers: Dict, frame_num: str, timestamp: str
    ) -> Optional[Dict]:
        """Parse generic packet when specific protocol parser not available"""
        frame = layers.get("frame", {})
        protocols = frame.get("frame.protocols", "unknown")
        packet_size = frame.get("frame.len", "0")

        # Try to extract basic IP info if available
        ip = layers.get("ip", {})
        src_ip = ip.get("ip.src")
        dst_ip = ip.get("ip.dst")

        if src_ip and dst_ip:
            target = f"{src_ip} → {dst_ip}"
            description = f"Network traffic ({protocols}) - Size: {packet_size} bytes"
        else:
            target = "Unknown hosts"
            description = f"Network packet ({protocols}) - Size: {packet_size} bytes"

        return self._create_finding(
            id=f"packet_{frame_num}",
            title="Network Traffic",
            description=description,
            target=target,
            timestamp=timestamp,
        )


# Test script
if __name__ == "__main__":
    parser = TsharkParser()

    # Test with your sample data
    with open("app/services/tools/tshark/sample.json", "r") as f:
        sample_data = f.read()

    result = parser.parse_single_result(sample_data, "tshark -i eth0 -c 10 -T json")

    print("=== TSHARK PARSER TEST ===")
    print(f"Findings: {len(result['findings'])}")
    print(f"Statistics: {result['statistics']}")
    print()

    for finding in result["findings"]:
        print(f"[{finding.get('severity', 'INFO').upper()}] {finding['title']}")
        print(f"  Target: {finding['target']}")
        print(f"  Description: {finding['description']}")
        print()
