-- Platform enum
CREATE TYPE platform_type AS ENUM ('WINDOWS', 'MACOS', 'LINUX');

-- Agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    hostname TEXT NULL,
    description TEXT,
    platform platform_type NULL,
    available_tools JSONB NULL,
    token TEXT NOT NULL,
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_agent_name UNIQUE (name),
    CONSTRAINT unique_agent_hostname UNIQUE (hostname)
);

-- Jobs table  
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT,
    action JSONB NOT NULL,
    results TEXT,
    success BOOLEAN DEFAULT NULL,
    started_at TIMESTAMP WITH TIME ZONE NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    results JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for many-to-many between jobs and reports
CREATE TABLE reports_jobs (
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, report_id)
);

-- Indexes for performance
CREATE INDEX idx_agents_last_seen ON agents(last_seen_at);
CREATE INDEX idx_agents_platform ON agents(platform);
CREATE INDEX idx_jobs_agent_id ON jobs(agent_id);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_reports_created_at ON reports(created_at);
CREATE INDEX idx_reports_jobs_job_id ON reports_jobs(job_id);
CREATE INDEX idx_reports_jobs_report_id ON reports_jobs(report_id);
