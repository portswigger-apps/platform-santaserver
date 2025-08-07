#!/bin/bash
# Build and test script for SantaServer (unified container architecture)

set -e

echo "🔨 Building SantaServer..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the container using main Dockerfile (unified architecture)
print_status "Building Docker image..."
if docker build -t santaserver:latest .; then
    print_success "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Validate image
print_status "Validating Docker image..."
IMAGE_SIZE=$(docker images santaserver:latest --format "{{.Size}}")
print_status "Image size: $IMAGE_SIZE"

# Check if image has required components
print_status "Inspecting image layers..."
if docker run --rm santaserver:latest ls -la /var/www/html > /dev/null 2>&1; then
    print_success "Frontend assets found"
else
    print_warning "Frontend assets not found or not accessible"
fi

if docker run --rm santaserver:latest ls -la /app/app/main.py > /dev/null 2>&1; then
    print_success "Backend application found"
else
    print_error "Backend application not found"
    exit 1
fi

if docker run --rm santaserver:latest which supervisord > /dev/null 2>&1; then
    print_success "Supervisor found"
else
    print_error "Supervisor not found"
    exit 1
fi

# Test basic container startup (without database)
print_status "Testing basic container startup..."
CONTAINER_ID=$(docker run -d --name santaserver-test -p 8081:8080 \
    -e POSTGRES_SERVER=dummy \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=test \
    -e POSTGRES_DB=test \
    santaserver:latest)

print_status "Container started with ID: $CONTAINER_ID"
print_status "Waiting for container to initialize..."

# Wait for container to start
sleep 15

# Check if container is still running
if docker ps | grep -q santaserver-test; then
    print_success "Container is running"
    
    # Check if nginx responds
    if curl -f http://localhost:8081/health > /dev/null 2>&1; then
        print_success "Health check endpoint accessible"
    else
        print_warning "Health check endpoint not accessible (may be expected without database)"
    fi
    
    # Show container logs for debugging
    print_status "Container logs (last 20 lines):"
    docker logs --tail 20 santaserver-test
    
else
    print_error "Container failed to stay running"
    print_status "Container logs:"
    docker logs santaserver-test
fi

# Cleanup test container
print_status "Cleaning up test container..."
docker stop santaserver-test > /dev/null 2>&1 || true
docker rm santaserver-test > /dev/null 2>&1 || true

print_success "Build and basic validation complete!"
print_status "To test with database, run:"
print_status "  docker-compose up -d"
print_status "  curl http://localhost:8080/health"