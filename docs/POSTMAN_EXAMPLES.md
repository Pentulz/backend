# Postman Examples for Job Creation

## Overview
This document provides JSON body examples for testing job creation with the new variant system in Postman.

## Base URL
```
http://localhost:8000/api/v1
```

## 1. Create Nmap TCP Connect Scan Job

**Endpoint:** `POST /jobs`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Port Scan Internal Network",
  "description": "Scan internal network for open ports and services",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "nmap",
    "variant": "tcp_connect_scan",
    "args": {
      "target": "192.168.1.171",
      "ports": "80,443,1000-2000"
    }
  }
}
```

**Expected Response:** 201 Created

## 2. Create FFuf Directory Fuzzing Job

**Endpoint:** `POST /jobs`

**Body:**
```json
{
  "name": "Web Directory Fuzzing",
  "description": "Fuzz web directories for hidden files",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "ffuf",
    "variant": "directory_fuzzing",
    "args": {
      "wordlist": "/usr/share/wordlists/dirb/common.txt",
      "url": "https://example.com/FUZZ"
    }
  }
}
```

## 3. Create Tshark Network Capture Job

**Endpoint:** `POST /jobs`

**Body:**
```json
{
  "name": "Network Traffic Capture",
  "description": "Capture network traffic for 5 minutes",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "tshark",
    "variant": "live_capture_duration_only",
    "args": {
      "interface": "eth0",
      "duration": "300"
    }
  }
}
```

## 4. Create Nmap OS Detection Job

**Endpoint:** `POST /jobs`

**Body:**
```json
{
  "name": "OS Detection Scan",
  "description": "Detect operating system of target host",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "nmap",
    "variant": "os_detection",
    "args": {
      "target": "192.168.1.100"
    }
  }
}
```

## 5. Create Nmap Service Version Detection Job

**Endpoint:** `POST /jobs`

**Body:**
```json
{
  "name": "Service Version Detection",
  "description": "Detect service versions on target host",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "nmap",
    "variant": "service_version_detection",
    "args": {
      "target": "192.168.1.100",
      "ports": "22,80,443,3306"
    }
  }
}
```

## 6. Create FFuf Status Code Matching Job

**Endpoint:** `POST /jobs`

**Body:**
```json
{
  "name": "Status Code Fuzzing",
  "description": "Fuzz with specific status code matching",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "ffuf",
    "variant": "status_code_matching",
    "args": {
      "wordlist": "/usr/share/wordlists/dirb/common.txt",
      "url": "https://example.com/FUZZ",
      "match_codes": "200,301,302,404"
    }
  }
}
```

## 7. Create Nmap Aggressive Scan Job

**Endpoint:** `POST /jobs`

**Body:**
```json
{
  "name": "Aggressive Security Scan",
  "description": "Comprehensive security scan with aggressive options",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "nmap",
    "variant": "aggressive_scan",
    "args": {
      "target": "192.168.1.100"
    }
  }
}
```

## 8. Create Tshark PCAP Analysis Job

**Endpoint:** `POST /jobs`

**Body:**
```json
{
  "name": "PCAP File Analysis",
  "description": "Analyze PCAP file with duration filter",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "tshark",
    "variant": "pcap_duration_filter",
    "args": {
      "pcap_file": "/path/to/capture.pcap",
      "duration": "600"
    }
  }
}
```

## Testing Invalid Cases

### 1. Invalid Tool Name
```json
{
  "name": "Invalid Tool Job",
  "description": "Job with invalid tool",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "invalid_tool",
    "variant": "some_variant",
    "args": {"target": "192.168.1.1"}
  }
}
```

### 2. Invalid Variant
```json
{
  "name": "Invalid Variant Job",
  "description": "Job with invalid variant",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "nmap",
    "variant": "invalid_variant",
    "args": {"target": "192.168.1.1"}
  }
}
```

### 3. Missing Required Arguments
```json
{
  "name": "Incomplete Job",
  "description": "Job with missing arguments",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": {
    "name": "nmap",
    "variant": "tcp_connect_scan",
    "args": {
      "target": "192.168.1.1"
      // Missing "ports" argument
    }
  }
}
```