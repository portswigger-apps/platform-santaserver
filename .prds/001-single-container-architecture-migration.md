# PRD: Single Container Migration for SantaServer

## Status: ✅ COMPLETED

**Implementation Date**: 2025-08-07  
**Status**: Successfully implemented and committed  
**Commit Hash**: cf9d801 - "feat: migrate to unified container architecture"

### Implementation Summary
- ✅ Single unified Dockerfile created with multi-stage build
- ✅ Supervisor configuration implemented for process management  
- ✅ Unix socket communication configured between nginx and uvicorn
- ✅ Non-root execution established (nginx user UID 101)
- ✅ Docker Compose updated for single container deployment
- ✅ Frontend build pipeline integrated into container
- ✅ Backend configuration updated for socket binding
- ✅ Development scripts and configuration files added
- ✅ Documentation updated to reflect new architecture

## Executive Summary

This Product Requirements Document outlines the migration of SantaServer from a multi-container Docker Compose architecture to a single, consolidated container running nginx-unprivileged, Python FastAPI backend, and serving static frontend assets. The migration aims to simplify deployment, reduce operational complexity, and maintain security through process supervision and Unix socket communication.

### Key Benefits
- **Simplified Deployment**: Single container instead of 3 separate services
- **Reduced Resource Usage**: Eliminate inter-container networking overhead
- **Enhanced Security**: Unix socket communication eliminates network exposure
- **Operational Efficiency**: Single process to monitor, scale, and maintain
- **Development Simplicity**: Unified build and deployment pipeline

## Current Architecture Analysis

### Current State
```yaml
Services:
- backend: Python 3.13 + FastAPI + uvicorn (port 8000)
- frontend: Node.js 18 + Svelte + built assets (port 3000)
- nginx: Reverse proxy (port 80 → 8088 external)
- db: PostgreSQL 17 (separate, unchanged)
```

### Current Issues
- Complex multi-container orchestration
- Network overhead between containers
- Multiple build contexts and Dockerfiles
- Container startup dependencies
- Resource allocation across 3 containers

### Current Strengths to Preserve
- Non-root user execution
- WebSocket support for real-time features
- Proper health checks
- Development reload capabilities

## Target Architecture Design

### Single Container Architecture
```
nginx-unprivileged:latest
├── nginx (process managed by supervisor)
├── uvicorn (FastAPI backend, process managed by supervisor)
├── supervisor (process manager)
├── Built frontend assets (served directly by nginx)
└── Unix socket communication (/tmp/uvicorn.sock)
```

### Communication Flow
```
Client Request → nginx:8080 
                ↓
Static Files (/): nginx serves directly from /var/www/html
                ↓
API Requests (/api): nginx → unix:/tmp/uvicorn.sock → uvicorn → FastAPI
```

## Technical Specifications

### Dockerfile Architecture

```dockerfile
# Multi-stage build approach
FROM node:18-alpine AS frontend-build
# Build frontend assets

FROM python:3.13-slim AS backend-build
# Install Python dependencies with uv

FROM nginx:1.25-alpine-unprivileged AS runtime
# Combine all components
```

### Process Management - Supervisor Configuration

**supervisord.conf**
```ini
[supervisord]
nodaemon=true
user=nginx
logfile=/tmp/supervisord.log
pidfile=/tmp/supervisord.pid

[program:uvicorn]
command=uv run uvicorn app.main:app --uds /tmp/uvicorn.sock
directory=/app
user=nginx
autorestart=true
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
priority=100

[program:nginx]
command=nginx -g "daemon off;"
autorestart=true
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
priority=200
depends_on=uvicorn

[eventlistener:processes]
command=/usr/local/bin/supervisor-watchdog
events=PROCESS_STATE_FATAL
```

### Unix Socket Communication

**Nginx Configuration**
```nginx
upstream backend {
    server unix:/tmp/uvicorn.sock;
}

server {
    listen 8080;
    server_name _;
    root /var/www/html;
    index index.html;

    # Serve frontend static assets
    location / {
        try_files $uri $uri/ /index.html;
        gzip_static on;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API requests to FastAPI via Unix socket
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

**FastAPI Configuration Updates**
```python
# Update main.py for Unix socket binding
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        uds="/tmp/uvicorn.sock",  # Unix socket instead of host:port
        log_level="info"
    )
```

### Environment Variables

```bash
# Container environment
POSTGRES_SERVER=db
POSTGRES_USER=santaserver
POSTGRES_PASSWORD=santaserver_dev
POSTGRES_DB=santaserver
POSTGRES_PORT=5432
SECRET_KEY=development_secret_key_change_in_production
TENANT_ID=your_tenant_id
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
ENVIRONMENT=development

# New socket configuration
UVICORN_UDS=/tmp/uvicorn.sock
NGINX_USER=nginx
SUPERVISOR_USER=nginx
```

## Implementation Plan

### Phase 1: Development and Testing (Week 1)

1. **Create New Dockerfile**
   - Multi-stage build with frontend compilation
   - Python runtime installation
   - Supervisor installation and configuration
   - Proper file permissions and user setup

2. **Update Configuration Files**
   - Supervisor configuration for process management
   - Nginx configuration with Unix socket upstream
   - FastAPI modifications for socket binding

3. **Local Development Testing**
   - Build and test single container locally
   - Validate all functionality works
   - Performance baseline testing

### Phase 2: Integration and Validation (Week 2)

1. **Docker Compose Integration**
   - Update docker-compose.yml for single service
   - Maintain database service separately
   - Update networking configuration

2. **Health Check Implementation**
   - Container health checks for supervisor processes
   - Application health endpoints
   - Monitoring integration points

3. **Development Workflow Updates**
   - Hot reload capabilities for development
   - Volume mounting for local development
   - Build optimization for faster iterations

## Security Considerations

### Process Security
- **Non-root Execution**: All processes run as nginx user (UID 101)
- **Process Isolation**: Supervisor manages process lifecycle
- **Resource Limits**: CPU and memory constraints
- **File System Permissions**: Proper ownership and access controls

### Network Security
- **Internal Communication**: Unix sockets eliminate network exposure
- **External Access**: Only port 8080 exposed (non-privileged)
- **WebSocket Security**: Proper upgrade handling and validation
- **Headers**: Security headers and proxy forwarding

### Container Security
- **Base Image**: nginx-unprivileged for security hardening
- **Dependencies**: Minimal package installation
- **Scanning**: Regular vulnerability scanning
- **Secrets**: Environment-based configuration only

### Access Control
- **File Permissions**: Restrictive permissions on configuration files
- **Socket Access**: Proper Unix socket permissions
- **Log Access**: Structured logging with appropriate access levels
- **Health Checks**: Non-authenticated endpoints with minimal information exposure

## Performance Impact

### Expected Improvements
- **Reduced Latency**: Unix socket communication (~20-30% faster than HTTP)
- **Lower Memory Usage**: Single process space (~15-25% memory reduction)
- **Faster Startup**: Reduced container orchestration overhead
- **Network Efficiency**: Elimination of container-to-container networking

### Monitoring Metrics
- Container startup time (target: <30 seconds)
- Request latency (maintain <200ms for API calls)
- Memory usage (target: <512MB total)
- CPU usage (target: <50% under normal load)

### Load Testing Scenarios
1. **API Load**: 1000 concurrent requests to /api endpoints
2. **WebSocket Load**: 500 concurrent WebSocket connections
3. **Static Asset Load**: High traffic to frontend resources
4. **Mixed Load**: Realistic production traffic patterns

## Testing Strategy

### Unit Testing
- Backend: Existing pytest suite with httpx TestClient
- Frontend: Existing Svelte testing framework
- Configuration: Supervisor and nginx config validation

### Integration Testing
- Container build and startup
- Process management (supervisor restart scenarios)
- Unix socket communication
- WebSocket functionality
- Health check endpoints

### Load Testing
- Performance benchmarking vs. current architecture
- Stress testing under high load
- Memory leak detection
- Long-running stability tests

### Security Testing
- Container vulnerability scanning
- Process privilege escalation testing
- Network isolation validation
- File permission auditing

## Deployment Guidelines

### Development Environment
```bash
# Build and run single container
docker build -t santaserver:unified .
docker run -d \
  --name santaserver \
  -p 8080:8080 \
  -e POSTGRES_SERVER=host.docker.internal \
  santaserver:unified

# With docker-compose (updated)
docker-compose -f docker-compose.unified.yml up -d
```

## Rollback Plan

### Immediate Rollback (< 5 minutes)
1. **Container Rollback**: Revert to previous image tag
2. **Load Balancer**: Switch traffic back to multi-container setup
3. **Health Check**: Verify all services operational
4. **Monitoring**: Confirm metrics return to normal

### Configuration Rollback
1. **Docker Compose**: Revert to previous docker-compose.yml
2. **Environment Variables**: Restore original configuration
3. **Network Configuration**: Re-enable container networking
4. **Database**: No changes required (external service)

### Emergency Procedures
- **Automated Rollback**: Health check failures trigger automatic reversion
- **Manual Override**: Emergency deployment procedures
- **Communication**: Incident response and stakeholder notification
- **Post-Mortem**: Root cause analysis and improvement planning

## Success Metrics

### Technical Metrics
- **Deployment Complexity**: Reduce from 3 containers to 1 (66% reduction)
- **Build Time**: Target <5 minutes for complete build
- **Startup Time**: Target <30 seconds for container ready
- **Resource Usage**: 25% reduction in memory footprint
- **Network Latency**: 20-30% improvement in API response times

### Operational Metrics
- **Deployment Frequency**: Ability to deploy more frequently
- **Mean Time to Recovery**: Faster recovery from issues
- **Monitoring Complexity**: Simplified metrics and logging
- **Developer Experience**: Easier local development setup

### Quality Metrics
- **Zero Regression**: All existing functionality preserved
- **Performance**: Maintain or improve current performance
- **Security**: Equal or enhanced security posture
- **Reliability**: 99.9% uptime maintained

## Risks and Mitigation

### Technical Risks
- **Single Point of Failure**: Mitigated by horizontal scaling and health checks
- **Process Management**: Mitigated by supervisor reliability and monitoring
- **Socket Communication**: Mitigated by proper error handling and fallbacks
- **Build Complexity**: Mitigated by multi-stage Docker builds and caching

### Operational Risks
- **Knowledge Transfer**: Mitigated by comprehensive documentation
- **Deployment Changes**: Mitigated by gradual rollout and training
- **Monitoring Gaps**: Mitigated by enhanced observability
- **Rollback Complexity**: Mitigated by automated rollback procedures

## Conclusion

The migration to a single container architecture represents a significant simplification of the SantaServer deployment model while maintaining all current functionality and security posture. The use of nginx-unprivileged, supervisor process management, and Unix socket communication provides a robust, secure, and performant solution that reduces operational complexity and improves developer experience.

The phased implementation plan ensures minimal risk while providing clear validation points throughout the migration process. Success metrics and rollback procedures provide confidence in the migration approach and ability to revert if issues arise.

This migration aligns with modern containerization best practices while maintaining the high security and performance standards required for enterprise-grade Santa management.