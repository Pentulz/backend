# Response Examples

Here are some examples of the responses you can expect from the API.

## `GET http://localhost:8000/api/v1/reports/`

```json
{
    "data": [
        {
            "type": "reports",
            "id": "770e8400-e29b-41d4-a716-446655440001",
            "attributes": {
                "results": {
                    "period": "2024-08-21 to 2024-08-28",
                    "summary": "Weekly Security Report",
                    "warnings": 8,
                    "risk_level": "low",
                    "total_scans": 15,
                    "recommendations": [
                        "Update OpenSSL on web-server-01",
                        "Enable fail2ban on all Linux servers",
                        "Review firewall rules for database access"
                    ],
                    "vulnerabilities_found": 0
                },
                "created_at": "2025-08-27T08:23:25.256535"
            }
        },
        {
            "type": "reports",
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "attributes": {
                "results": {
                    "period": "2024-08-27 to 2024-08-28",
                    "status": "all_systems_operational",
                    "summary": "Infrastructure Health Report",
                    "healthy_systems": 4,
                    "systems_checked": 4,
                    "performance_metrics": {
                        "average_cpu": "18%",
                        "average_memory": "65%",
                        "network_latency": "12ms"
                    }
                },
                "created_at": "2025-08-28T02:23:25.256535"
            }
        }
    ]
}
```

## `GET http://localhost:8000/api/v1/jobs/`

```json
{
    "data": [
        {
            "type": "jobs",
            "id": "660e8400-e29b-41d4-a716-446655440005",
            "attributes": {
                "name": "iOS Build Test",
                "description": "Build and test iOS application",
                "agent_id": "550e8400-e29b-41d4-a716-446655440004",
                "action": {
                    "args": [
                        "-project",
                        "MyApp.xcodeproj",
                        "test"
                    ],
                    "scheme": "MyApp",
                    "command": "xcodebuild"
                },
                "started_at": "2025-08-28T07:53:25.256535",
                "completed_at": null,
                "created_at": "2025-08-28T07:38:25.256535",
                "results": null
            }
        },
        {
            "type": "jobs",
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "attributes": {
                "name": "Port Scan Internal Network",
                "description": "Scan internal network for open ports and services",
                "agent_id": "550e8400-e29b-41d4-a716-446655440001",
                "action": {
                    "args": [
                        "-sS",
                        "-O",
                        "192.168.1.0/24"
                    ],
                    "command": "nmap",
                    "timeout": 300
                },
                "started_at": "2025-08-28T06:23:25.256535",
                "completed_at": "2025-08-28T06:38:25.256535",
                "created_at": "2025-08-28T05:23:25.256535",
                "results": {
                    "status": "completed",
                    "duration": "45s",
                    "open_ports": [
                        22,
                        80,
                        443,
                        3306
                    ],
                    "hosts_found": 12
                }
            }
        },
        {
            "type": "jobs",
            "id": "660e8400-e29b-41d4-a716-446655440002",
            "attributes": {
                "name": "Database Health Check",
                "description": "Check PostgreSQL database performance and connections",
                "agent_id": "550e8400-e29b-41d4-a716-446655440002",
                "action": {
                    "args": [
                        "-c",
                        "SELECT COUNT(*) FROM pg_stat_activity;"
                    ],
                    "command": "psql",
                    "database": "production"
                },
                "started_at": "2025-08-28T02:23:25.256535",
                "completed_at": "2025-08-28T02:23:55.256535",
                "created_at": "2025-08-28T00:23:25.256535",
                "results": {
                    "status": "healthy",
                    "cpu_usage": "15%",
                    "max_connections": 100,
                    "active_connections": 23
                }
            }
        },
    ]
}	
```

## `GET http://localhost:8000/api/v1/agents/`

```json	
{
    "data": [
        {
            "type": "agents",
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "attributes": {
                "hostname": "web-server-01",
                "description": "Primary web server for production environment",
                "platform": "LINUX",
                "available_tools": {
                    "curl": "7.68.0",
                    "nmap": "7.80",
                    "docker": "20.10.7",
                    "python": "3.8.10"
                },
                "token": "tok_550e8400e29b41d4a716446655440001",
                "last_seen_at": "2025-08-28T08:18:25.256535",
                "created_at": "2025-08-26T08:23:25.256535"
            }
        },
        {
            "type": "agents",
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "attributes": {
                "hostname": "db-server-01",
                "description": "Database server for user data",
                "platform": "LINUX",
                "available_tools": {
                    "htop": "3.0.5",
                    "redis": "6.2.6",
                    "postgresql": "13.7"
                },
                "token": "tok_550e8400e29b41d4a716446655440002",
                "last_seen_at": "2025-08-28T07:23:25.256535",
                "created_at": "2025-08-23T08:23:25.256535"
            }
        }
    ]
}
```

## `GET http://localhost:8000/api/v1/agents/550e8400-e29b-41d4-a716-4466554400011`

```json
{
    "data": {
        "type": "agents",
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "attributes": {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "hostname": "web-server-01",
            "description": "Primary web server for production environment",
            "platform": "LINUX",
            "available_tools": {
                "curl": "7.68.0",
                "nmap": "7.80",
                "docker": "20.10.7",
                "python": "3.8.10"
            },
            "token": "tok_550e8400e29b41d4a716446655440001",
            "last_seen_at": "2025-08-28T08:18:25.256535",
            "created_at": "2025-08-26T08:23:25.256535"
        }
    }
}
```


## `GET http://localhost:8000/api/v1/jobs/660e8400-e29b-41d4-a716-446655440001`

```json
{
    "data": {
        "type": "jobs",
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "attributes": {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "name": "Port Scan Internal Network",
            "description": "Scan internal network for open ports and services",
            "agent_id": "550e8400-e29b-41d4-a716-446655440001",
            "action": {
                "args": [
                    "-sS",
                    "-O",
                    "192.168.1.0/24"
                ],
                "command": "nmap",
                "timeout": 300
            },
            "started_at": "2025-08-28T06:23:25.256535",
            "completed_at": "2025-08-28T06:38:25.256535",
            "created_at": "2025-08-28T05:23:25.256535",
            "results": {
                "status": "completed",
                "duration": "45s",
                "open_ports": [
                    22,
                    80,
                    443,
                    3306
                ],
                "hosts_found": 12
            }
        }
    }
}
```

## Error Responses

```json
{
    "error": {
        "status": "400",
        "title": "Bad Request",
        "detail": "Invalid job id"
    }
}

{
    "error": {
        "status": "400",
        "title": "Bad Request",
        "detail": "Invalid agent id"
    }
}
```

