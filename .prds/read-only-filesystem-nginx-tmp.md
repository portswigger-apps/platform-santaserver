# PRD: Read-Only Root Filesystem with Nginx /tmp Directories

**Document Version:** 1.0  
**Date:** 2025-01-07  
**Author:** System Architecture Team  
**Status:** Draft  

## Executive Summary

This PRD outlines the requirements for modifying SantaServer's unified container architecture to use a read-only root filesystem while ensuring nginx operates exclusively with directories under `/tmp`. This change enhances security posture by preventing runtime modifications to the root filesystem while maintaining full functionality.

## 1. Problem Statement

### 1.1 Current State
- Container runs with writable root filesystem
- Nginx uses default system directories for temporary files and logs
- Security exposure through potential runtime filesystem modifications
- Non-compliance with container security best practices

### 1.2 Security Concerns
- Writable root filesystem allows persistence of malicious changes
- Attack surface includes entire filesystem
- Potential for privilege escalation through filesystem modifications
- Compliance gaps with container security standards

## 2. Solution Overview

### 2.1 Objectives
- Implement read-only root filesystem for enhanced security
- Migrate all nginx temporary operations to `/tmp` directories
- Maintain existing functionality and performance
- Ensure zero-downtime deployments continue working

### 2.2 Success Criteria
- Container runs successfully with `--read-only` flag
- All nginx functionality preserved (static assets, proxying, WebSocket support)
- FastAPI backend remains accessible via unix socket
- No permission errors in application logs
- Performance degradation <5%
- Security scan shows improved posture

## 3. Technical Requirements

### 3.1 Nginx Configuration Changes

#### 3.1.1 Required Directory Structure
```
/tmp/
├── nginx/
│   ├── logs/                    # Access and error logs
│   │   ├── access.log
│   │   └── error.log
│   ├── temp/                    # Temporary directories
│   │   ├── client_body_temp/    # Large POST request handling
│   │   ├── proxy_temp/          # Reverse proxy temporary files
│   │   ├── fastcgi_temp/        # FastCGI temporary files (if used)
│   │   └── uwsgi_temp/          # uWSGI temporary files (if used)
│   ├── cache/                   # Nginx cache directory (if enabled)
│   └── nginx.pid               # Process ID file
├── sockets/
│   └── uvicorn.sock            # Unix socket (existing)
└── supervisor/                 # Supervisor runtime files
    ├── logs/
    └── supervisor.pid
```

#### 3.1.2 Nginx Configuration Updates
- **PID File**: Change from `/var/run/nginx.pid` to `/tmp/nginx/nginx.pid`
- **Access Log**: Redirect to `/tmp/nginx/logs/access.log` or stdout
- **Error Log**: Redirect to `/tmp/nginx/logs/error.log` or stderr
- **Temporary Paths**: All temp directories under `/tmp/nginx/temp/`
- **Cache Directory**: Move to `/tmp/nginx/cache/` if caching enabled

#### 3.1.3 Configuration Directives
```nginx
# Core module directives
pid /tmp/nginx/nginx.pid;
error_log /tmp/nginx/logs/error.log warn;

# HTTP module directives  
client_body_temp_path /tmp/nginx/temp/client_body_temp;
proxy_temp_path /tmp/nginx/temp/proxy_temp;
fastcgi_temp_path /tmp/nginx/temp/fastcgi_temp;
uwsgi_temp_path /tmp/nginx/temp/uwsgi_temp;
scgi_temp_path /tmp/nginx/temp/scgi_temp;

# Logging
access_log /tmp/nginx/logs/access.log combined;

# Optional: Cache configuration
# proxy_cache_path /tmp/nginx/cache levels=1:2 keys_zone=cache:10m inactive=60m;
```

### 3.2 Dockerfile Modifications

#### 3.2.1 Directory Creation
Add directory creation and permission setup in Dockerfile:
```dockerfile
# Create nginx runtime directories in /tmp
RUN mkdir -p /tmp/nginx/logs \
             /tmp/nginx/temp/client_body_temp \
             /tmp/nginx/temp/proxy_temp \
             /tmp/nginx/temp/fastcgi_temp \
             /tmp/nginx/temp/uwsgi_temp \
             /tmp/nginx/temp/scgi_temp \
             /tmp/nginx/cache \
             /tmp/supervisor/logs && \
    chown -R nginx:nginx /tmp/nginx /tmp/supervisor && \
    chmod -R 755 /tmp/nginx /tmp/supervisor
```

#### 3.2.2 Read-Only Root Filesystem
Enable read-only root filesystem in runtime:
```dockerfile
# Add tmpfs mounts for writable areas
VOLUME ["/tmp"]
```

### 3.3 Container Startup Modifications

#### 3.3.1 Entrypoint Script Updates
Update `config/entrypoint.sh` to ensure directories exist at startup:
```bash
#!/bin/bash
# Ensure nginx runtime directories exist
mkdir -p /tmp/nginx/{logs,temp/{client_body_temp,proxy_temp,fastcgi_temp,uwsgi_temp,scgi_temp},cache}
mkdir -p /tmp/supervisor/logs

# Set proper permissions
chown -R nginx:nginx /tmp/nginx /tmp/supervisor
chmod -R 755 /tmp/nginx /tmp/supervisor

# Continue with existing startup logic
exec "$@"
```

### 3.4 Supervisor Configuration Updates

#### 3.4.1 Log File Locations
Update supervisor to use `/tmp` for all log files:
```ini
[supervisord]
logfile=/tmp/supervisor/supervisord.log
pidfile=/tmp/supervisor/supervisord.pid
childlogdir=/tmp/supervisor/logs
```

### 3.5 Docker Compose Changes

#### 3.5.1 Read-Only Mode
Add read-only filesystem flag to docker-compose.yml:
```yaml
services:
  santaserver:
    # ... existing configuration
    read_only: true
    tmpfs:
      - /tmp:size=100m,mode=1777
```

## 4. Implementation Plan

### 4.1 Phase 1: Configuration Updates (Week 1)
- **Tasks:**
  - Update nginx-unified.conf with /tmp paths
  - Modify supervisord.conf for /tmp logging
  - Update entrypoint.sh for directory creation
  - Create development testing environment

- **Deliverables:**
  - Updated configuration files
  - Development environment validation
  - Basic functionality testing

### 4.2 Phase 2: Dockerfile Changes (Week 2)
- **Tasks:**
  - Modify Dockerfile for directory creation
  - Add proper permission setup
  - Update build process documentation
  - Create read-only container testing

- **Deliverables:**
  - Updated Dockerfile
  - Container build validation
  - Read-only filesystem testing

### 4.3 Phase 3: Integration and Testing (Week 3)
- **Tasks:**
  - Integration testing with full application stack
  - Performance benchmarking
  - Security validation
  - Documentation updates

- **Deliverables:**
  - Complete integration testing
  - Performance benchmarks
  - Security scan results
  - Updated documentation

### 4.4 Phase 4: Production Deployment (Week 4)
- **Tasks:**
  - Staged deployment to production
  - Monitoring and validation
  - Rollback procedures validation
  - Team training

- **Deliverables:**
  - Production deployment
  - Monitoring dashboards
  - Operational procedures
  - Team documentation

## 5. Risk Assessment and Mitigation

### 5.1 High Risks

#### 5.1.1 Performance Impact
- **Risk**: Memory pressure from tmpfs usage
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: 
  - Monitor /tmp usage with alerts
  - Size tmpfs appropriately (100MB initial)
  - Implement log rotation for /tmp files
  - Performance testing under load

#### 5.1.2 Debugging Challenges
- **Risk**: Logs lost on container restart
- **Probability**: High
- **Impact**: Low
- **Mitigation**:
  - Configure log forwarding to external systems
  - Consider stdout/stderr redirection for critical logs
  - Maintain debug procedures for live containers

### 5.2 Medium Risks

#### 5.2.1 Directory Permissions
- **Risk**: Permission errors preventing startup
- **Probability**: Low
- **Impact**: High
- **Mitigation**:
  - Comprehensive testing in development
  - Detailed entrypoint script validation
  - Fallback procedures for permission issues

#### 5.2.2 Disk Space Exhaustion
- **Risk**: /tmp running out of space
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**:
  - Monitoring with alerts at 80% usage
  - Automatic cleanup policies
  - Configurable tmpfs size

### 5.3 Low Risks

#### 5.3.1 Configuration Complexity
- **Risk**: Complex nginx configuration management
- **Probability**: Low
- **Impact**: Low
- **Mitigation**:
  - Clear documentation
  - Configuration validation tools
  - Team training

## 6. Acceptance Criteria

### 6.1 Functional Requirements
- [ ] Container starts successfully with `--read-only` flag set
- [ ] Nginx serves static frontend assets without errors
- [ ] FastAPI backend accessible via unix socket at `/tmp/sockets/uvicorn.sock`
- [ ] WebSocket connections work for real-time features
- [ ] Health check endpoints return successfully
- [ ] All API endpoints respond correctly

### 6.2 Security Requirements
- [ ] No write attempts to read-only root filesystem
- [ ] All nginx temporary files created in `/tmp/nginx/`
- [ ] Container passes security scan with improved score
- [ ] No privilege escalation vulnerabilities introduced
- [ ] File permissions correctly set for nginx user (UID 101)

### 6.3 Performance Requirements
- [ ] Response time degradation <5% compared to baseline
- [ ] Memory usage increase <10% due to tmpfs
- [ ] Container startup time increase <10%
- [ ] /tmp usage remains under 80% of allocated space under normal load

### 6.4 Operational Requirements
- [ ] Container logs accessible via docker logs
- [ ] Monitoring alerts configured for /tmp usage
- [ ] Rollback procedure tested and documented
- [ ] Zero-downtime deployment compatibility maintained

## 7. Monitoring and Observability

### 7.1 Key Metrics
- `/tmp` filesystem usage and growth rate
- Container memory usage (tmpfs impact)
- Nginx error rate and response times
- Failed write attempts to read-only filesystem

### 7.2 Alerts
- `/tmp` usage >80%
- Read-only filesystem write violations
- Nginx permission errors
- Container restart due to /tmp issues

### 7.3 Logging Strategy
- **Option 1**: File-based logs in `/tmp` with external log forwarding
- **Option 2**: stdout/stderr redirection with container log collection
- **Recommended**: Hybrid approach with critical logs to stdout/stderr

## 8. Documentation Updates Required

### 8.1 Development Documentation
- Update DEVELOPMENT.md with new container requirements
- Add troubleshooting guide for read-only filesystem issues
- Update local development setup instructions

### 8.2 Operations Documentation
- Update deployment procedures
- Add monitoring setup guide
- Create troubleshooting runbook

### 8.3 Security Documentation
- Document security improvements achieved
- Update security assessment results
- Create security configuration checklist

## 9. Rollback Plan

### 9.1 Immediate Rollback
1. Remove `read_only: true` from docker-compose.yml
2. Deploy previous container version
3. Validate functionality restored

### 9.2 Configuration Rollback
1. Revert nginx-unified.conf to previous version
2. Rebuild container without /tmp modifications
3. Deploy and validate

### 9.3 Data Preservation
- No persistent data stored in /tmp (by design)
- Application state preserved in database
- No data loss during rollback operations

## 10. Future Considerations

### 10.1 Container Optimization
- Consider distroless base images for further security
- Evaluate multi-stage build optimizations
- Assess container scanning automation

### 10.2 Security Enhancements
- Implement security policy enforcement (AppArmor/SELinux)
- Consider runtime security monitoring
- Evaluate secrets management improvements

### 10.3 Performance Optimization
- Monitor and optimize tmpfs size based on actual usage
- Consider log streaming to reduce /tmp usage
- Evaluate caching strategies for performance

---

**Approval:**
- [ ] Security Team Review
- [ ] Architecture Team Review  
- [ ] Operations Team Review
- [ ] Development Team Review

**Implementation Start Date:** TBD  
**Target Completion Date:** TBD