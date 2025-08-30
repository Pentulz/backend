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
INSERT INTO jobs (id, agent_id, name, description, action, started_at, completed_at, created_at) VALUES
('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'Port Scan Internal Network',
 'Scan internal network for open ports and services',
 '{"cmd": "nmap", "args": ["-sS", "-O", "192.168.1.0/24"], "timeout": 300}'::jsonb,
 NOW() - INTERVAL '2 hours', NULL, NOW() - INTERVAL '3 hours'),
('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'Database Health Check',
 'Check PostgreSQL database performance and connections',
 '{"cmd": "psql", "args": ["-c", "SELECT COUNT(*) FROM pg_stat_activity;"], "database": "production"}'::jsonb,
 NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 59 minutes 30 seconds', NOW() - INTERVAL '8 hours'),
('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', 'Security Vulnerability Scan',
 'Run security scan on web application',
 '{"cmd": "nikto", "args": ["-h", "https://example.com"], "scan_type": "web"}'::jsonb,
 NOW() - INTERVAL '12 hours', NOW() - INTERVAL '10 hours', NOW() - INTERVAL '1 day'),
('660e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440003', 'Windows System Update',
 'Check and install Windows updates',
 '{"cmd": "powershell", "args": ["Get-WindowsUpdate", "-Install"], "elevated": true}'::jsonb,
 NOW() - INTERVAL '1 day', NOW() - INTERVAL '23 hours', NOW() - INTERVAL '2 days'),
('660e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440004', 'iOS Build Test',
 'Build and test iOS application',
 '{"cmd": "xcodebuild", "args": ["-project", "MyApp.xcodeproj", "test"], "scheme": "MyApp"}'::jsonb,
 NOW() - INTERVAL '30 minutes', NULL, NOW() - INTERVAL '45 minutes');

-- Update jobs results if column exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'jobs' AND column_name = 'results'
    ) THEN
        UPDATE jobs SET results = '{"open_ports": [22, 80, 443, 3306], "hosts_found": 12, "duration": "45s", "status": "completed"}'::jsonb
        WHERE id = '660e8400-e29b-41d4-a716-446655440001';

        UPDATE jobs SET results = '{"active_connections": 23, "max_connections": 100, "cpu_usage": "15%", "status": "healthy"}'::jsonb
        WHERE id = '660e8400-e29b-41d4-a716-446655440002';

        UPDATE jobs SET results = '{"vulnerabilities": [], "warnings": 2, "info": 15, "scan_time": "120s", "status": "clean"}'::jsonb
        WHERE id = '660e8400-e29b-41d4-a716-446655440003';

        UPDATE jobs SET results = '{"updates_installed": 5, "reboot_required": true, "duration": "25m", "status": "completed"}'::jsonb
        WHERE id = '660e8400-e29b-41d4-a716-446655440004';

        RAISE NOTICE 'Results column found and updated';
    ELSE
        RAISE NOTICE 'Results column not found, skipping results update';
    END IF;
END
$$;

-- Insert sample reports
INSERT INTO reports (id, results, created_at) VALUES
('770e8400-e29b-41d4-a716-446655440001',
 '{
    "summary": "Weekly Security Report",
    "period": "2024-08-21 to 2024-08-28",
    "total_scans": 15,
    "vulnerabilities_found": 0,
    "warnings": 8,
    "recommendations": [
        "Update OpenSSL on web-server-01",
        "Enable fail2ban on all Linux servers",
        "Review firewall rules for database access"
    ],
    "risk_level": "low"
 }'::jsonb,
 NOW() - INTERVAL '1 day'),
('770e8400-e29b-41d4-a716-446655440002',
 '{
    "summary": "Infrastructure Health Report",
    "period": "2024-08-27 to 2024-08-28",
    "systems_checked": 4,
    "healthy_systems": 4,
    "performance_metrics": {
        "average_cpu": "18%",
        "average_memory": "65%",
        "network_latency": "12ms"
    },
    "status": "all_systems_operational"
 }'::jsonb,
 NOW() - INTERVAL '6 hours');

-- Link jobs to reports
INSERT INTO reports_jobs (job_id, report_id) VALUES
('660e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440001'),
('660e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440001'),
('660e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440002'),
('660e8400-e29b-41d4-a716-446655440004', '770e8400-e29b-41d4-a716-446655440002');

COMMIT;
