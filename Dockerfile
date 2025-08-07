# Multi-stage Dockerfile for SantaServer unified container
# Combines frontend build, backend setup, and nginx runtime with supervisor

# =============================================================================
# Stage 1: Frontend Build
# =============================================================================
FROM node:18-alpine AS frontend-build

WORKDIR /app

# Copy frontend package files for dependency installation
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile --production=false

# Copy frontend source code and build
COPY frontend/ ./
RUN yarn build

# =============================================================================
# Stage 2: Backend Dependencies
# =============================================================================
FROM python:3.13-slim AS backend-build

WORKDIR /app

# Install system dependencies required for Python packages and uv
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Copy backend dependencies first for better caching
COPY backend/pyproject.toml backend/uv.lock ./

# Copy app/__init__.py for version detection during uv sync
COPY backend/app/__init__.py ./app/__init__.py

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy the rest of the backend application code
COPY backend/ ./

# =============================================================================
# Stage 3: Runtime Container with Python 3.13 and nginx
# =============================================================================
FROM python:3.13-slim AS runtime

# Install nginx, supervisor, and other required packages
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Create nginx user (similar to nginx-unprivileged)
RUN groupadd -g 101 nginx && \
    useradd -g nginx -u 101 -r -s /bin/false nginx

# Configure nginx to run as non-root
RUN sed -i '/user /c\user nginx;' /etc/nginx/nginx.conf && \
    sed -i 's|pid /run/nginx.pid;|pid /tmp/nginx.pid;|' /etc/nginx/nginx.conf && \
    mkdir -p /var/cache/nginx /var/lib/nginx/body /var/lib/nginx/fastcgi && \
    mkdir -p /var/lib/nginx/proxy /var/lib/nginx/scgi /var/lib/nginx/uwsgi && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /var/lib/nginx && \
    rm -f /etc/nginx/sites-enabled/default

# Create application directory and set up proper permissions
RUN mkdir -p /app /var/log/supervisor /tmp/sockets /tmp/uv-cache && \
    chown -R nginx:nginx /app /var/log/supervisor /tmp/sockets /tmp/uv-cache && \
    chmod 755 /tmp/sockets

# Copy frontend build artifacts to nginx web root
COPY --from=frontend-build --chown=nginx:nginx /app/build /var/www/html

# Copy backend application and Python environment
COPY --from=backend-build --chown=nginx:nginx /app /app
COPY --from=backend-build --chown=nginx:nginx /app/.venv /app/.venv

# Copy configuration files
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY config/nginx-unified.conf /etc/nginx/conf.d/default.conf
COPY config/entrypoint.sh /entrypoint.sh
COPY config/supervisor-watchdog.py /usr/local/bin/supervisor-watchdog

# Set up proper permissions for all files
RUN chown -R nginx:nginx /app /var/www/html && \
    chmod +x /entrypoint.sh && \
    chmod +x /usr/local/bin/supervisor-watchdog && \
    chmod 644 /etc/supervisor/conf.d/supervisord.conf && \
    chmod 644 /etc/nginx/conf.d/default.conf

# Remove default nginx configuration
RUN rm -f /etc/nginx/conf.d/default.conf.bak

# Set working directory
WORKDIR /app

# Switch to non-root user
USER nginx

# Expose port 8080 (non-privileged port)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Use entrypoint script to set up environment and start supervisor
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf", "-n"]