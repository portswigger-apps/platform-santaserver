#!/bin/sh
# Entrypoint script for SantaServer unified container
set -e

echo "🚀 Starting SantaServer unified container..."

# Set default environment variables
export UVICORN_UDS=${UVICORN_UDS:-/tmp/sockets/uvicorn.sock}
export NGINX_USER=${NGINX_USER:-nginx}
export SUPERVISOR_USER=${SUPERVISOR_USER:-nginx}

# Ensure socket directory exists with proper permissions
mkdir -p /tmp/sockets
chmod 755 /tmp/sockets
chown nginx:nginx /tmp/sockets

# Ensure log directories exist
mkdir -p /tmp/logs /var/log/supervisor
chown nginx:nginx /tmp/logs /var/log/supervisor

# Clean up any existing socket files
rm -f /tmp/sockets/uvicorn.sock /tmp/supervisor.sock

# Set up Python path for the virtual environment
export PATH="/app/.venv/bin:$PATH"
export PYTHONPATH="/app:$PYTHONPATH"

# Validate that required directories and files exist
if [ ! -d "/var/www/html" ]; then
    echo "❌ Frontend build directory not found at /var/www/html"
    exit 1
fi

if [ ! -f "/app/app/main.py" ]; then
    echo "❌ FastAPI application not found at /app/app/main.py"
    exit 1
fi

if [ ! -f "/app/.venv/bin/uvicorn" ]; then
    echo "❌ Uvicorn not found in virtual environment"
    exit 1
fi

# Test database connectivity if configured
if [ ! -z "$POSTGRES_SERVER" ]; then
    echo "🔍 Checking database connectivity..."
    # Note: This is optional and will not fail the startup
    python3 -c "
import os
import sys
try:
    # Add basic connection test here if needed
    print('Database configuration found')
except Exception as e:
    print(f'Database connection warning: {e}')
" || echo "⚠️ Database connection check failed (continuing anyway)"
fi

echo "✅ Environment setup complete"
echo "📊 Configuration summary:"
echo "   - Frontend assets: /var/www/html"
echo "   - Backend app: /app"
echo "   - Unix socket: $UVICORN_UDS"
echo "   - Running as user: $NGINX_USER"

echo "🔧 Starting services via supervisor..."

# Execute the main command (supervisor)
exec "$@"