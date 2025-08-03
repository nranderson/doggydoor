#!/bin/bash

# Doggy Door Setup - Docker Deployment (Recommended)
# This script redirects to the Docker-only setup for easier maintenance

echo "🐕 Doggy Door Setup"
echo "=================="
echo ""
echo "For the best experience, we recommend using Docker deployment."
echo "This provides:"
echo "  ✅ Automatic updates via Watchtower"
echo "  ✅ Pre-built images from GitHub Container Registry"
echo "  ✅ Simplified installation and maintenance"
echo "  ✅ No Python virtual environment setup needed"
echo ""
echo "Running Docker setup script..."
echo ""

# Check if Docker setup script exists
if [ -f "setup_pi_docker.sh" ]; then
    chmod +x setup_pi_docker.sh
    ./setup_pi_docker.sh
else
    echo "❌ setup_pi_docker.sh not found!"
    echo "Please ensure you have the complete project files."
    exit 1
fi
