#!/usr/bin/env python3
"""
Tshark Pentest Parser - Multi-agent network intelligence for penetration testing
"""

import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict, Counter
import ipaddress


class TsharkPentestParser:
    """Parser for tshark output focused on pentest intelligence across multiple agents"""
    
    def __init__(self):
        # Known security-relevant protocols
        self.security_protocols = {
            'ssh': 22, 'telnet': 23, 'smtp': 25, 'dns': 53,
            'http': 80, 'pop3': 110, 'ntp': 123, 'snmp': 161,
            'https': 443, 'smb': 445, 'ldap': 389, 'rdp': 3389
        }
        
        # Known vendor OUIs for asset identification
        self.vendor_ouis = {
            '5469': 'Microsoft Corporation',
            '0007E9': 'Intel Corporation',
            '000C29': 'VMware',
            '525400': 'Red Hat (QEMU)',
            '080027': 'Oracle (VirtualBox)'
        }
    
    def parse_multi_agent_results(self, agent_results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Parse results from multiple agents and correlate findings
        
        Args:
            agent_results: {agent_id: {raw_tshark_json, metadata}}
            
        Returns:
            Comprehensive pentest intelligence report
        """
        
        # Parse each agent's data
        agent_analyses = {}
        for agent_id, data in agent_results.items():
            agent_analyses[agent_id] = self._parse_agent_traffic(
                data['raw_data'], 
                agent_id,
                data.get('metadata', {})
            )
        
        # Cross-agent correlation
        correlation_analysis = self._correlate_agents(agent_analyses)
        
        # Generate pentest intelligence
        return {
            'scan_metadata': self._generate_scan_metadata(agent_results),
            'network_topology': self._build_network_topology(agent_analyses),
            'asset_discovery': self._aggregate_assets(agent_analyses),
            'communication_matrix': self._build_communication_matrix(agent_analyses),
            'security_findings': self._identify_security_findings(agent_analyses),
            'agent_perspectives': agent_analyses,
            'correlation_insights': correlation_analysis,
            'recommendations': self._generate_recommendations(agent_analyses, correlation_analysis)
        }
    
    def _parse_agent_traffic(self, raw_packets: List[Dict], agent_id: str, metadata: Dict) -> Dict:
        """Parse traffic from a single agent"""
        
        analysis = {
            'agent_id': agent_id,
            'agent_location': metadata.get('location', 'Unknown'),
            'capture_info': self._extract_capture_info(raw_packets),
            'discovered_hosts': {},
            'protocols_seen': defaultdict(int),
            'network_segments': set(),
            'arp_table': {},
            'dns_queries': [],
            'suspicious_activities': [],
            'communication_flows': []
        }
        
        for packet in raw_packets:
            self._analyze_packet(packet, analysis)
        
        # Post-process analysis
        analysis['network_summary'] = self._summarize_network_view(analysis)
        
        return analysis
    
    def _analyze_packet(self, packet: Dict, analysis: Dict):
        """Analyze individual packet for intelligence"""
        layers = packet.get('_source', {}).get('layers', {})
        
        # Frame analysis
        frame = layers.get('frame', {})
        timestamp = frame.get('frame.time_epoch')
        
        # Ethernet analysis
        eth = layers.get('eth', {})
        if eth:
            self._analyze_ethernet(eth, analysis)
        
        # ARP analysis (network discovery)
        arp = layers.get('arp', {})
        if arp:
            self._analyze_arp(arp, analysis, timestamp)
        
        # IP analysis
        ip = layers.get('ip', {})
        if ip:
            self._analyze_ip(ip, analysis, timestamp)
        
        # TCP/UDP analysis
        tcp = layers.get('tcp', {})
        udp = layers.get('udp', {})
        if tcp:
            self._analyze_tcp(tcp, ip, analysis, timestamp)
        if udp:
            self._analyze_udp(udp, ip, analysis, timestamp)
        
        # DNS analysis
        dns = layers.get('dns', {})
        if dns:
            self._analyze_dns(dns, analysis, timestamp)
        
        # HTTP analysis
        http = layers.get('http', {})
        if http:
            self._analyze_http(http, ip, analysis, timestamp)
    
    def _analyze_ethernet(self, eth: Dict, analysis: Dict):
        """Analyze Ethernet layer for asset discovery"""
        src_mac = eth.get('eth.src')
        dst_mac = eth.get('eth.dst')
        
        for mac in [src_mac, dst_mac]:
            if mac and mac not in analysis['discovered_hosts']:
                vendor = self._identify_vendor_by_mac(mac)
                analysis['discovered_hosts'][mac] = {
                    'mac': mac,
                    'vendor': vendor,
                    'first_seen': datetime.now().isoformat(),
                    'ips_associated': set(),
                    'protocols': set()
                }
    
    def _analyze_arp(self, arp: Dict, analysis: Dict, timestamp: str):
        """Analyze ARP for network topology discovery"""
        opcode = arp.get('arp.opcode')
        src_ip = arp.get('arp.src.proto_ipv4')
        dst_ip = arp.get('arp.dst.proto_ipv4')
        src_mac = arp.get('arp.src.hw_mac')
        dst_mac = arp.get('arp.dst.hw_mac')
        
        if src_ip and dst_ip:
            # Update ARP table
            if src_ip not in analysis['arp_table']:
                analysis['arp_table'][src_ip] = {
                    'ip': src_ip,
                    'mac': src_mac,
                    'first_seen': timestamp,
                    'arp_requests': 0,
                    'arp_replies': 0
                }
            
            # Track network segments
            try:
                analysis['network_segments'].add(str(ipaddress.ip_network(f"{src_ip}/24", strict=False)))
                analysis['network_segments'].add(str(ipaddress.ip_network(f"{dst_ip}/24", strict=False)))
            except:
                pass
            
            # Count ARP operations
            if opcode == '1':  # ARP Request
                analysis['arp_table'][src_ip]['arp_requests'] += 1
                
                # Detect potential ARP scanning
                agent_requests = sum(host.get('arp_requests', 0) for host in analysis['arp_table'].values())
                if agent_requests > 50:  # Threshold for ARP scanning
                    analysis['suspicious_activities'].append({
                        'type': 'potential_arp_scanning',
                        'description': f'High volume of ARP requests detected ({agent_requests} requests)',
                        'timestamp': timestamp,
                        'source_ip': src_ip
                    })
            
            elif opcode == '2':  # ARP Reply
                analysis['arp_table'][src_ip]['arp_replies'] += 1
        
        analysis['protocols_seen']['ARP'] += 1
    
    def _analyze_ip(self, ip: Dict, analysis: Dict, timestamp: str):
        """Analyze IP layer for host discovery"""
        src_ip = ip.get('ip.src')
        dst_ip = ip.get('ip.dst')
        
        # Track communication flows
        if src_ip and dst_ip:
            flow = f"{src_ip} → {dst_ip}"
            analysis['communication_flows'].append({
                'source': src_ip,
                'destination': dst_ip,
                'timestamp': timestamp,
                'protocol': 'IP'
            })
            
            # Detect cross-network communication
            try:
                src_net = ipaddress.ip_network(f"{src_ip}/24", strict=False)
                dst_net = ipaddress.ip_network(f"{dst_ip}/24", strict=False)
                
                if src_net != dst_net:
                    analysis['suspicious_activities'].append({
                        'type': 'cross_network_communication',
                        'description': f'Communication between different network segments: {src_net} ↔ {dst_net}',
                        'timestamp': timestamp,
                        'flow': flow
                    })
            except:
                pass
    
    def _analyze_tcp(self, tcp: Dict, ip: Dict, analysis: Dict, timestamp: str):
        """Analyze TCP for service discovery"""
        src_port = tcp.get('tcp.srcport')
        dst_port = tcp.get('tcp.dstport')
        flags = tcp.get('tcp.flags', {})
        
        if dst_port:
            port = int(dst_port)
            service = self._identify_service_by_port(port)
            
            if service:
                analysis['protocols_seen'][f'TCP/{service}'] += 1
                
                # Track potential service enumeration
                if port in [22, 80, 443, 445, 3389]:  # Common pentest targets
                    analysis['suspicious_activities'].append({
                        'type': 'service_connection_attempt',
                        'description': f'Connection attempt to {service} service on port {port}',
                        'timestamp': timestamp,
                        'destination': ip.get('ip.dst'),
                        'port': port,
                        'service': service
                    })
        
        analysis['protocols_seen']['TCP'] += 1
    
    def _analyze_udp(self, udp: Dict, ip: Dict, analysis: Dict, timestamp: str):
        """Analyze UDP traffic"""
        dst_port = udp.get('udp.dstport')
        
        if dst_port:
            port = int(dst_port)
            service = self._identify_service_by_port(port)
            
            if service:
                analysis['protocols_seen'][f'UDP/{service}'] += 1
        
        analysis['protocols_seen']['UDP'] += 1
    
    def _analyze_dns(self, dns: Dict, analysis: Dict, timestamp: str):
        """Analyze DNS queries for reconnaissance detection"""
        query_name = dns.get('dns.qry.name')
        query_type = dns.get('dns.qry.type')
        
        if query_name:
            analysis['dns_queries'].append({
                'query': query_name,
                'type': query_type,
                'timestamp': timestamp
            })
            
            # Detect potential DNS reconnaissance
            if any(keyword in query_name.lower() for keyword in ['admin', 'mail', 'ftp', 'test', 'dev']):
                analysis['suspicious_activities'].append({
                    'type': 'suspicious_dns_query',
                    'description': f'DNS query for potentially interesting hostname: {query_name}',
                    'timestamp': timestamp,
                    'query': query_name
                })
        
        analysis['protocols_seen']['DNS'] += 1
    
    def _analyze_http(self, http: Dict, ip: Dict, analysis: Dict, timestamp: str):
        """Analyze HTTP for web reconnaissance"""
        method = http.get('http.request.method')
        uri = http.get('http.request.uri')
        host = http.get('http.host')
        user_agent = http.get('http.user_agent')
        
        if method and uri:
            analysis['suspicious_activities'].append({
                'type': 'http_request',
                'description': f'{method} request to {host}{uri}',
                'timestamp': timestamp,
                'method': method,
                'uri': uri,
                'host': host,
                'user_agent': user_agent
            })
        
        analysis['protocols_seen']['HTTP'] += 1
    
    def _correlate_agents(self, agent_analyses: Dict) -> Dict:
        """Correlate findings across multiple agents"""
        correlation = {
            'shared_networks': {},
            'cross_agent_communications': [],
            'asset_confirmations': {},
            'attack_patterns': []
        }
        
        # Find shared network segments
        all_segments = {}
        for agent_id, analysis in agent_analyses.items():
            for segment in analysis['network_segments']:
                if segment not in all_segments:
                    all_segments[segment] = []
                all_segments[segment].append(agent_id)
        
        correlation['shared_networks'] = {
            segment: agents for segment, agents in all_segments.items() 
            if len(agents) > 1
        }
        
        # Cross-agent communication detection
        for agent_id, analysis in agent_analyses.items():
            for flow in analysis['communication_flows']:
                # Check if destination IP is seen by another agent
                for other_agent_id, other_analysis in agent_analyses.items():
                    if agent_id != other_agent_id:
                        if flow['destination'] in other_analysis['arp_table']:
                            correlation['cross_agent_communications'].append({
                                'source_agent': agent_id,
                                'target_agent': other_agent_id,
                                'flow': flow,
                                'confirmed_by_target': True
                            })
        
        return correlation
    
    def _build_network_topology(self, agent_analyses: Dict) -> Dict:
        """Build comprehensive network topology"""
        topology = {
            'network_segments': set(),
            'inter_segment_routing': [],
            'network_devices': {},
            'segment_agents': {}
        }
        
        for agent_id, analysis in agent_analyses.items():
            # Collect all network segments
            topology['network_segments'].update(analysis['network_segments'])
            
            # Map agents to segments
            for segment in analysis['network_segments']:
                if segment not in topology['segment_agents']:
                    topology['segment_agents'][segment] = []
                topology['segment_agents'][segment].append(agent_id)
            
            # Detect inter-segment routing from cross-network communications
            for activity in analysis['suspicious_activities']:
                if activity['type'] == 'cross_network_communication':
                    topology['inter_segment_routing'].append({
                        'agent': agent_id,
                        'communication': activity['description'],
                        'timestamp': activity['timestamp']
                    })
        
        topology['network_segments'] = list(topology['network_segments'])
        return topology
    
    def _generate_recommendations(self, agent_analyses: Dict, correlation: Dict) -> List[Dict]:
        """Generate security recommendations based on analysis"""
        recommendations = []
        
        # Network segmentation recommendations
        if correlation['shared_networks']:
            recommendations.append({
                'category': 'Network Security',
                'priority': 'High',
                'title': 'Network Segmentation Review',
                'description': f'Multiple network segments detected across agents. Review segmentation policies.',
                'details': f"Shared segments: {list(correlation['shared_networks'].keys())}",
                'remediation': 'Implement proper VLAN isolation and firewall rules between network segments.'
            })
        
        # Service exposure recommendations
        exposed_services = {}
        for agent_id, analysis in agent_analyses.items():
            for activity in analysis['suspicious_activities']:
                if activity['type'] == 'service_connection_attempt':
                    service = activity['service']
                    if service not in exposed_services:
                        exposed_services[service] = []
                    exposed_services[service].append(agent_id)
        
        if exposed_services:
            recommendations.append({
                'category': 'Service Hardening',
                'priority': 'Medium',
                'title': 'Exposed Services Detected',
                'description': f'Services detected across network: {", ".join(exposed_services.keys())}',
                'details': f'Services by agent: {exposed_services}',
                'remediation': 'Review service necessity and implement proper access controls.'
            })
        
        # DNS reconnaissance recommendations
        total_dns_queries = sum(len(analysis['dns_queries']) for analysis in agent_analyses.values())
        if total_dns_queries > 100:
            recommendations.append({
                'category': 'Monitoring',
                'priority': 'Medium',
                'title': 'High DNS Query Volume',
                'description': f'Detected {total_dns_queries} DNS queries across all agents.',
                'details': 'High DNS activity may indicate reconnaissance or automated tools.',
                'remediation': 'Implement DNS query monitoring and rate limiting.'
            })
        
        return recommendations
    
    def _identify_vendor_by_mac(self, mac: str) -> str:
        """Identify vendor from MAC address OUI"""
        if not mac or len(mac) < 8:
            return 'Unknown'
        
        oui = mac.replace(':', '').upper()[:6]
        return self.vendor_ouis.get(oui, 'Unknown')
    
    def _identify_service_by_port(self, port: int) -> Optional[str]:
        """Identify service by port number"""
        for service, service_port in self.security_protocols.items():
            if port == service_port:
                return service
        return None
    
    def _extract_capture_info(self, packets: List[Dict]) -> Dict:
        """Extract capture metadata"""
        if not packets:
            return {}
        
        first_packet = packets[0].get('_source', {}).get('layers', {}).get('frame', {})
        last_packet = packets[-1].get('_source', {}).get('layers', {}).get('frame', {})
        
        return {
            'total_packets': len(packets),
            'capture_start': first_packet.get('frame.time'),
            'capture_end': last_packet.get('frame.time'),
            'interface': first_packet.get('frame.interface_id_tree', {}).get('frame.interface_name', 'Unknown')
        }
    
    def _summarize_network_view(self, analysis: Dict) -> Dict:
        """Summarize network view from agent perspective"""
        return {
            'total_hosts_discovered': len(analysis['discovered_hosts']),
            'network_segments_seen': len(analysis['network_segments']),
            'protocols_detected': len(analysis['protocols_seen']),
            'suspicious_activities_count': len(analysis['suspicious_activities']),
            'dns_queries_count': len(analysis['dns_queries']),
            'top_protocols': dict(Counter(analysis['protocols_seen']).most_common(5))
        }
    
    def _aggregate_assets(self, agent_analyses: Dict) -> Dict:
        """Aggregate discovered assets across all agents"""
        all_assets = {}
        
        for agent_id, analysis in agent_analyses.items():
            for ip, details in analysis['arp_table'].items():
                if ip not in all_assets:
                    all_assets[ip] = {
                        'ip': ip,
                        'mac': details['mac'],
                        'vendor': self._identify_vendor_by_mac(details['mac']),
                        'discovered_by_agents': [],
                        'services_detected': set(),
                        'first_seen': details['first_seen']
                    }
                all_assets[ip]['discovered_by_agents'].append(agent_id)
            
            # Add service information from suspicious activities
            for activity in analysis['suspicious_activities']:
                if activity['type'] == 'service_connection_attempt':
                    target_ip = activity.get('destination')
                    service = activity.get('service')
                    if target_ip in all_assets and service:
                        all_assets[target_ip]['services_detected'].add(service)
        
        # Convert sets to lists for JSON serialization
        for asset in all_assets.values():
            asset['services_detected'] = list(asset['services_detected'])
        
        return all_assets
    
    def _build_communication_matrix(self, agent_analyses: Dict) -> Dict:
        """Build communication matrix between network segments"""
        matrix = defaultdict(lambda: defaultdict(int))
        
        for agent_id, analysis in agent_analyses.items():
            for flow in analysis['communication_flows']:
                src_ip = flow['source']
                dst_ip = flow['destination']
                
                try:
                    src_net = str(ipaddress.ip_network(f"{src_ip}/24", strict=False))
                    dst_net = str(ipaddress.ip_network(f"{dst_ip}/24", strict=False))
                    matrix[src_net][dst_net] += 1
                except:
                    pass
        
        return dict(matrix)
    
    def _identify_security_findings(self, agent_analyses: Dict) -> Dict:
        """Identify security-relevant findings"""
        findings = {
            'critical': [],
            'high': [],
            'medium': [],
            'informational': []
        }
        
        for agent_id, analysis in agent_analyses.items():
            # Analyze suspicious activities
            for activity in analysis['suspicious_activities']:
                if activity['type'] == 'cross_network_communication':
                    findings['high'].append({
                        'title': 'Cross-Network Communication Detected',
                        'description': activity['description'],
                        'agent': agent_id,
                        'timestamp': activity['timestamp']
                    })
                elif activity['type'] == 'service_connection_attempt':
                    service = activity.get('service', 'Unknown')
                    if service in ['ssh', 'rdp', 'smb']:
                        findings['medium'].append({
                            'title': f'{service.upper()} Service Access Attempt',
                            'description': activity['description'],
                            'agent': agent_id,
                            'timestamp': activity['timestamp']
                        })
                elif activity['type'] == 'potential_arp_scanning':
                    findings['high'].append({
                        'title': 'Potential ARP Scanning Detected',
                        'description': activity['description'],
                        'agent': agent_id,
                        'timestamp': activity['timestamp']
                    })
        
        return findings
    
    def _generate_scan_metadata(self, agent_results: Dict) -> Dict:
        """Generate overall scan metadata"""
        return {
            'total_agents': len(agent_results),
            'agent_locations': {
                agent_id: data.get('metadata', {}).get('location', 'Unknown')
                for agent_id, data in agent_results.items()
            },
            'scan_timestamp': datetime.now().isoformat(),
            'analysis_type': 'network_traffic_analysis'
        }


# Example usage with sample data
def main():
    """Example usage with multiple agent data"""
    
    # Sample data for Agent A (from the provided document)
    agent_a_data = [
        {
            "_source": {
                "layers": {
                    "frame": {
                        "frame.number": "1",
                        "frame.time": "Aug 31, 2025 14:34:40.277082914 CEST",
                        "frame.time_epoch": "1756643680.277082914",
                        "frame.len": "42"
                    },
                    "eth": {
                        "eth.dst": "00:15:5d:4f:40:ba",
                        "eth.src": "00:15:5d:1d:08:c9"
                    },
                    "arp": {
                        "arp.opcode": "1",
                        "arp.src.hw_mac": "00:15:5d:1d:08:c9",
                        "arp.src.proto_ipv4": "172.21.0.1",
                        "arp.dst.proto_ipv4": "172.21.1.225"
                    }
                }
            }
        }
    ]
    
    # Sample data for Agent B (simulated)
    agent_b_data = [
        {
            "_source": {
                "layers": {
                    "frame": {
                        "frame.number": "1",
                        "frame.time": "Aug 31, 2025 14:34:40.280000000 CEST",
                        "frame.time_epoch": "1756643680.280000000",
                        "frame.len": "74"
                    },
                    "eth": {
                        "eth.dst": "00:15:5d:1d:08:c9",
                        "eth.src": "00:15:5d:4f:40:ba"
                    },
                    "arp": {
                        "arp.opcode": "2",
                        "arp.src.hw_mac": "00:15:5d:4f:40:ba",
                        "arp.src.proto_ipv4": "172.21.1.225",
                        "arp.dst.proto_ipv4": "172.21.0.1"
                    }
                }
            }
        }
    ]
    
    # Prepare agent results
    agent_results = {
        'agent_dmz_01': {
            'raw_data': agent_a_data,
            'metadata': {
                'location': 'DMZ Network',
                'agent_ip': '172.21.0.100',
                'deployment': 'on-premises'
            }
        },
        'agent_internal_01': {
            'raw_data': agent_b_data,
            'metadata': {
                'location': 'Internal Network',
                'agent_ip': '172.21.1.100',
                'deployment': 'on-premises'
            }
        }
    }
    
    # Parse with pentest intelligence
    parser = TsharkPentestParser()
    pentest_report = parser.parse_multi_agent_results(agent_results)
    
    # Display results
    print("=== PENTULZ NETWORK INTELLIGENCE REPORT ===\n")
    
    print("SCAN METADATA:")
    print(f"  Total Agents: {pentest_report['scan_metadata']['total_agents']}")
    print(f"  Agent Locations: {pentest_report['scan_metadata']['agent_locations']}")
    
    print("\nNETWORK TOPOLOGY:")
    topology = pentest_report['network_topology']
    print(f"  Network Segments: {topology['network_segments']}")
    print(f"  Segment Distribution: {topology['segment_agents']}")
    
    print("\nDISCOVERED ASSETS:")
    for ip, asset in pentest_report['asset_discovery'].items():
        print(f"  {ip} ({asset['vendor']}) - Discovered by: {asset['discovered_by_agents']}")
    
    print("\nSECURITY FINDINGS:")
    for severity, findings in pentest_report['security_findings'].items():
        if findings:
            print(f"  {severity.upper()}:")
            for finding in findings:
                print(f"    - {finding['title']}: {finding['description']}")
    
    print("\nRECOMMENDations:")
    for rec in pentest_report['recommendations']:
        print(f"  [{rec['priority']}] {rec['title']}")
        print(f"    {rec['description']}")
        print(f"    Remediation: {rec['remediation']}\n")


if __name__ == "__main__":
    main()