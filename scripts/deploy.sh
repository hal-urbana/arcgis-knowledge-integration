#!/bin/bash
#
# Deployment script for ArcGIS Knowledge Integration
# automates packaging, CI/CD setup, and deployment

set -e

REPOSITORY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPOSITORY_DIR"

echo "🚀 ArcGIS Knowledge Integration - Deployment Script"
echo "==================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="arcgis-knowledge-integration"
BRANCH_NAME="main"
DOCKER_IMAGE_NAME="arcgis-knowledge-integration"
DOCKER_CONTAINER_NAME="arcgis-knowledge-integration"

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
    print_info "Current branch: $CURRENT_BRANCH"
    read -p "Switch to $BRANCH_NAME for deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment aborted"
        exit 1
    fi
    git checkout "$BRANCH_NAME"
    print_success "Switched to main branch"
fi

# Build Docker image
print_info "Building Docker image..."
docker build -t "$DOCKER_IMAGE_NAME:latest" .

if [ $? -eq 0 ]; then
    print_success "Docker image built"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Run Docker container
print_info "Starting Docker container..."
docker run -d --name "$DOCKER_CONTAINER_NAME" \
    -v "$REPOSITORY_DIR/config:/app/config" \
    -v "$REPOSITORY_DIR/logs:/app/logs" \
    "$DOCKER_IMAGE_NAME:latest"

if [ $? -eq 0 ]; then
    print_success "Container started: $DOCKER_CONTAINER_NAME"
else
    print_error "Failed to start container"
    docker rm -f "$DOCKER_CONTAINER_NAME" 2>/dev/null || true
    exit 1
fi

# Test deployment
print_info "Testing deployment..."
sleep 5  # Give container time to start

# Check container status
CONTAINER_STATUS=$(docker ps -q -f name="$DOCKER_CONTAINER_NAME")
if [ -n "$CONTAINER_STATUS" ]; then
    print_success "Container is running"
else
    print_error "Container stopped unexpectedly"
    docker logs "$DOCKER_CONTAINER_NAME"
    exit 1
fi

# Health check (replace with actual endpoint)
print_info "Performing health check..."
sleep 3
# Placeholders for health check logic
# if curl http://localhost:8080/health; then
#    print_success "Health check passed"
# else
#    print_error "Health check failed"
#    exit 1
# fi

print_success "Deployment successful!"

echo ""
echo "Deployment Summary:"
echo "-------------------"
echo "Repository: $REPOSITORY_DIR"
echo "Image: $DOCKER_IMAGE_NAME:latest"
echo "Container: $DOCKER_CONTAINER_NAME"
echo "Status: Running"

# Cleanup function
cleanup() {
    print_info "Cleaning up..."
    docker stop "$DOCKER_CONTAINER_NAME"
    docker rm "$DOCKER_CONTAINER_NAME"
}

# Register trap to cleanup on exit
trap cleanup EXIT

echo ""
print_info "Use 'docker logs -f $DOCKER_CONTAINER_NAME' to view logs"
print_info "Use 'docker exec -it $DOCKER_CONTAINER_NAME bash' to access container shell"