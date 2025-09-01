BEGIN;

-- Insert sample agents
INSERT INTO agents (id, name, hostname, description, platform, available_tools, token, last_seen_at, created_at) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440001',
    'Web Server 01',
    'web-server-01',
    'Primary web server for production environment',
    'LINUX',
    '[{"cmd": "nmap", "args": [], "version": "7.80", "version_arg": "--version"},
      {"cmd": "curl", "args": [], "version": "7.68.0", "version_arg": "--version"},
      {"cmd": "python", "args": [], "version": "3.8.10", "version_arg": "--version"},
      {"cmd": "docker", "args": [], "version": "20.10.7", "version_arg": "--version"}]'::jsonb,
    'tok_550e8400e29b41d4a716446655440001',
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '2 days'
),
(
    '550e8400-e29b-41d4-a716-446655440002',
    'Database Server 01',
    'db-server-01',
    'Database server for user data',
    'LINUX',
    '[{"cmd": "psql", "args": [], "version": "16", "version_arg": "--version"},
      {"cmd": "pgcli", "args": [], "version": "3.4.0", "version_arg": "--version"}]'::jsonb,
    'tok_550e8400e29b41d4a716446655440002',
    NOW() - INTERVAL '1 hour',
    NOW() - INTERVAL '5 days'
),
(
    '550e8400-e29b-41d4-a716-446655440003',
    'Windows Dev Machine',
    NULL,
    'Development machine Windows 11',
    NULL,
    '[]'::jsonb,
    'tok_550e8400e29b41d4a716446655440003',
    NOW() - INTERVAL '30 minutes',
    NOW() - INTERVAL '1 day'
),
(
    '550e8400-e29b-41d4-a716-446655440004',
    'MacBook Pro Dev',
    NULL,
    'MacBook Pro for iOS development',
    NULL,
    '[]'::jsonb,
    'tok_550e8400e29b41d4a716446655440004',
    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '3 days'
);

-- Insert sample jobs
INSERT INTO jobs (id, agent_id, name, description, action, started_at, completed_at, created_at, success) VALUES
('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'Port Scan Internal Network',
 'Scan internal network for open ports and services',
 '{"cmd": "nmap", "variant": "tcp_connect_scan", "args": ["-sT", "-p", "80,443,1000-2000", "192.168.1.171"]}'::jsonb,
 NOW() - INTERVAL '2 hours', NULL, NOW() - INTERVAL '3 hours', FALSE),
('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'Database Health Check',
 'Check PostgreSQL database performance and connections',
 '{"cmd": "psql", "variant": "custom_command", "args": ["-c", "SELECT COUNT(*) FROM pg_stat_activity;", "-d", "production"]}'::jsonb,
 NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 59 minutes 30 seconds', NOW() - INTERVAL '8 hours', TRUE),
('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', 'Web Directory Fuzzing',
 'Run directory fuzzing on web application',
 '{"cmd": "ffuf", "variant": "directory_fuzzing", "args": ["-w", "/usr/share/wordlists/dirb/common.txt", "-u", "https://example.com/FUZZ"]}'::jsonb,
 NOW() - INTERVAL '12 hours', NOW() - INTERVAL '10 hours', NOW() - INTERVAL '1 day', TRUE),
('660e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440003', 'Network Traffic Capture',
 'Capture network traffic for analysis',
 '{"cmd": "tshark", "variant": "live_capture_duration_only", "args": ["-i", "eth0", "--duration", "300"]}'::jsonb,
 NOW() - INTERVAL '1 day', NOW() - INTERVAL '23 hours', NOW() - INTERVAL '2 days', TRUE),
('660e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440004', 'OS Detection Scan',
 'Detect operating system of target host',
 '{"cmd": "nmap", "variant": "os_detection", "args": ["-O", "192.168.1.100"]}'::jsonb,
 NOW() - INTERVAL '30 minutes', NULL, NOW() - INTERVAL '45 minutes', FALSE);

-- Update jobs results if column exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'jobs' AND column_name = 'results'
    ) THEN
        -- Job 1: nmap scan results (XML format)
        UPDATE jobs SET results = '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -sS -p 22,80,443,8080 -oX - 192.168.1.1" start="1756652095" startstr="Sun Aug 31 16:54:55 2025" version="7.94SVN" xmloutputversion="1.05">
<scaninfo type="syn" protocol="tcp" numservices="4" services="22,80,443,8080"/>
<verbose level="0"/>
<debugging level="0"/>
<hosthint><status state="up" reason="unknown-response" reason_ttl="0"/>
<address addr="192.168.1.1" addrtype="ipv4"/>
<hostnames>
</hostnames>
</hosthint>
<host starttime="1756652095" endtime="1756652095"><status state="up" reason="echo-reply" reason_ttl="63"/>
<address addr="192.168.1.1" addrtype="ipv4"/>
<hostnames>
<hostname name="internetbox.home" type="PTR"/>
</hostnames>
<ports><port protocol="tcp" portid="22"><state state="closed" reason="reset" reason_ttl="63"/><service name="ssh" method="table" conf="3"/></port>
<port protocol="tcp" portid="80"><state state="open" reason="syn-ack" reason_ttl="63"/><service name="http" method="table" conf="3"/></port>
<port protocol="tcp" portid="443"><state state="open" reason="syn-ack" reason_ttl="63"/><service name="https" method="table" conf="3"/></port>
<port protocol="tcp" portid="8080"><state state="closed" reason="reset" reason_ttl="63"/><service name="http-proxy" method="table" conf="3"/></port>
</ports>
<times srtt="824" rttvar="1788" to="100000"/>
</host>
<runstats><finished time="1756652095" timestr="Sun Aug 31 16:54:55 2025" summary="Nmap done at Sun Aug 31 16:54:55 2025; 1 IP address (1 host up) scanned in 0.32 seconds" elapsed="0.32" exit="success"/><hosts up="1" down="0" total="1"/>
</runstats>
</nmaprun>'
        WHERE id = '660e8400-e29b-41d4-a716-446655440001';

        -- Job 2: Database health check results (JSON format)
        UPDATE jobs SET results = '{"active_connections": 23, "max_connections": 100, "cpu_usage": "15%", "status": "healthy"}'
        WHERE id = '660e8400-e29b-41d4-a716-446655440002';

        -- Job 3: ffuf directory fuzzing results (JSON format)
        UPDATE jobs SET results = '{
          "results": [
            {
              "url": "http://example.com/",
              "status": 200,
              "length": 1234,
              "words": 45,
              "lines": 12
            },
            {
              "url": "http://example.com/admin",
              "status": 403,
              "length": 0,
              "words": 0,
              "lines": 0
            },
            {
              "url": "http://example.com/login",
              "status": 200,
              "length": 567,
              "words": 23,
              "lines": 8
            },
            {
              "url": "http://example.com/backup",
              "status": 200,
              "length": 8901,
              "words": 156,
              "lines": 45
            },
            {
              "url": "http://example.com/config",
              "status": 200,
              "length": 234,
              "words": 12,
              "lines": 3
            },
            {
              "url": "http://example.com/phpinfo.php",
              "status": 200,
              "length": 45678,
              "words": 890,
              "lines": 234
            }
          ],
          "config": {
            "url": "http://example.com/FUZZ",
            "wordlist": "/usr/share/wordlists/dirb/common.txt"
          }
        }'
        WHERE id = '660e8400-e29b-41d4-a716-446655440003';

        -- Job 4: tshark network capture results (JSON format)
        UPDATE jobs SET results = '[
            {
              "_index": "packets-2025-08-31",
              "_type": "doc",
              "_score": null,
              "_source": {
                "layers": {
                  "frame": {
                    "frame.section_number": "1",
                    "frame.interface_id": "0",
                    "frame.interface_id_tree": {
                      "frame.interface_name": "eth0"
                    },
                    "frame.encap_type": "1",
                    "frame.time": "Aug 31, 2025 14:34:40.277082914 CEST",
                    "frame.time_utc": "Aug 31, 2025 12:34:40.277082914 UTC",
                    "frame.time_epoch": "1756643680.277082914",
                    "frame.offset_shift": "0.000000000",
                    "frame.time_delta": "0.000000000",
                    "frame.time_delta_displayed": "0.000000000",
                    "frame.time_relative": "0.000000000",
                    "frame.number": "1",
                    "frame.len": "42",
                    "frame.cap_len": "42",
                    "frame.marked": "0",
                    "frame.ignored": "0",
                    "frame.protocols": "eth:ethertype:arp"
                  },
                  "eth": {
                    "eth.dst": "00:15:5d:4f:40:ba",
                    "eth.dst_tree": {
                      "eth.dst_resolved": "Microsoft_4f:40:ba",
                      "eth.dst.oui": "5469",
                      "eth.dst.oui_resolved": "Microsoft Corporation",
                      "eth.addr": "00:15:5d:4f:40:ba",
                      "eth.addr.oui": "5469",
                      "eth.addr.oui_resolved": "Microsoft Corporation",
                      "eth.dst.lg": "0",
                      "eth.lg": "0",
                      "eth.dst.ig": "0",
                      "eth.ig": "0"
                    },
                    "eth.src": "00:15:5d:1d:08:c9",
                    "eth.src_tree": {
                      "eth.src_resolved": "Microsoft_1d:08:c9",
                      "eth.src.oui": "5469",
                      "eth.src.oui_resolved": "Microsoft Corporation",
                      "eth.addr": "00:15:5d:08:c9",
                      "eth.addr.oui": "5469",
                      "eth.addr.oui_resolved": "Microsoft Corporation",
                      "eth.src.lg": "0",
                      "eth.lg": "0",
                      "eth.src.ig": "0",
                      "eth.ig": "0"
                    },
                    "eth.type": "0x0806"
                  },
                  "arp": {
                    "arp.hw.type": "1",
                    "arp.proto.type": "0x0800",
                    "arp.hw.size": "6",
                    "arp.proto.size": "4",
                    "arp.opcode": "1",
                    "arp.src.hw_mac": "00:15:5d:1d:08:c9",
                    "arp.src.proto_ipv4": "172.21.0.1",
                    "arp.dst.hw_mac": "00:15:5d:4f:40:ba",
                    "arp.dst.proto_ipv4": "172.21.1.225"
                  }
                }
              }
            }
          ]'
        WHERE id = '660e8400-e29b-41d4-a716-446655440004';

        -- Job 5: nmap OS detection results (XML format)
        UPDATE jobs SET results = '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -O 192.168.1.100" start="1756652095" startstr="Sun Aug 31 16:54:55 2025" version="7.94SVN" xmloutputversion="1.05">
<scaninfo type="connect" protocol="tcp" numservices="1000" services="1-1000"/>
<verbose level="0"/>
<debugging level="0"/>
<host starttime="1756652095" endtime="1756652095"><status state="up" reason="echo-reply" reason_ttl="64"/>
<address addr="192.168.1.100" addrtype="ipv4"/>
<hostnames>
<hostname name="desktop-100" type="PTR"/>
</hostnames>
<os>
<osmatch name="Windows 10 1903" accuracy="98" line="1">
<osclass type="general purpose" vendor="microsoft" osfamily="windows" osgen="10" accuracy="98"/>
</osmatch>
<osmatch name="Windows 10 1909" accuracy="97" line="2">
<osclass type="general purpose" vendor="microsoft" osfamily="windows" osgen="10" accuracy="97"/>
</osmatch>
</os>
<ports><port protocol="tcp" portid="80"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="http" method="table" conf="3"/></port>
<port protocol="tcp" portid="135"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="msrpc" method="table" conf="3"/></port>
<port protocol="tcp" portid="139"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="netbios-ssn" method="table" conf="3"/></port>
<port protocol="tcp" portid="445"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="microsoft-ds" method="table" conf="3"/></port>
</ports>
<times srtt="824" rttvar="1788" to="100000"/>
</host>
<runstats><finished time="1756652095" timestr="Sun Aug 31 16:54:55 2025" summary="Nmap done at Sun Aug 31 16:54:55 2025; 1 IP address (1 host up) scanned in 2.45 seconds" elapsed="2.45" exit="success"/><hosts up="1" down="0" total="1"/>
</runstats>
</nmaprun>'
        WHERE id = '660e8400-e29b-41d4-a716-446655440005';

        RAISE NOTICE 'Results column found and updated with real tool outputs';
    ELSE
        RAISE NOTICE 'Results column not found, skipping results update';
    END IF;
END
$$;

COMMIT;
