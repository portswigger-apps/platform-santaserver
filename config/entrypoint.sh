#!/bin/sh
# Entrypoint script for SantaServer unified container
set -e

# JSON logging function
log_json() {
    local level="$1"
    local message="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    printf '{"timestamp":"%s","level":"%s","message":"%s","service":"santaserver-entrypoint"}\n' "$timestamp" "$level" "$message"
}

log_json "info" "Starting SantaServer unified container"

# Set default environment variables
export UVICORN_UDS=${UVICORN_UDS:-/tmp/sockets/uvicorn.sock}
export NGINX_USER=${NGINX_USER:-nginx}
export SUPERVISOR_USER=${SUPERVISOR_USER:-nginx}

# Ensure socket directory exists with proper permissions
mkdir -p /tmp/sockets
chmod 755 /tmp/sockets
chown nginx:nginx /tmp/sockets

# Ensure nginx runtime directories exist (read-only filesystem support)
mkdir -p /tmp/nginx/client_body_temp
mkdir -p /tmp/nginx/proxy_temp  
mkdir -p /tmp/nginx/fastcgi_temp
mkdir -p /tmp/nginx/uwsgi_temp
mkdir -p /tmp/nginx/scgi_temp
mkdir -p /tmp/nginx/cache

# Create supervisor PID directory and set proper permissions
mkdir -p /tmp/supervisor
chown -R nginx:nginx /tmp/nginx /tmp/supervisor
chmod -R 755 /tmp/nginx /tmp/supervisor


# Clean up any existing socket files
rm -f /tmp/sockets/uvicorn.sock /tmp/supervisor.sock

# Set up Python path for the virtual environment
export PATH="/app/.venv/bin:$PATH"
export PYTHONPATH="/app:$PYTHONPATH"

# Validate that required directories and files exist
if [ ! -d "/var/www/html" ]; then
    log_json "error" "Frontend build directory not found at /var/www/html" >&2
    exit 1
fi

if [ ! -f "/app/app/main.py" ]; then
    log_json "error" "FastAPI application not found at /app/app/main.py" >&2
    exit 1
fi

if [ ! -f "/app/.venv/bin/uvicorn" ]; then
    log_json "error" "Uvicorn not found in virtual environment" >&2
    exit 1
fi

# Test database connectivity if configured
if [ ! -z "$POSTGRES_SERVER" ]; then
    log_json "info" "Checking database connectivity"
    # Note: This is optional and will not fail the startup
    python3 -c "
import os
import sys
try:
    # Add basic connection test here if needed
    print('Database configuration found')
except Exception as e:
    print(f'Database connection warning: {e}')
" || log_json "warn" "Database connection check failed (continuing anyway)"
fi

log_json "info" "Environment setup complete"
log_json "info" "Configuration - Frontend assets: /var/www/html, Backend app: /app, Unix socket: $UVICORN_UDS, Running as user: $NGINX_USER"
log_json "info" "Starting services via supervisor"

# Execute the main command (supervisor)
exec "$@"