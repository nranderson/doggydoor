#!/bin/bash

# Setup script for Doggy Door on Raspberry Pi (Docker-Only)

set -e

echo "🐕 Doggy Door Setup Script (Docker Edition)"
echo "=========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️ Warning: This doesn't appear to be a Raspberry Pi"
    echo "Some features may not work correctly."
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    bluetooth \
    bluez \
    curl \
    ca-certificates \
    gnupg \
    lsb-release

# Enable Bluetooth service
echo "📡 Enabling Bluetooth service..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Add user to bluetooth group
echo "👤 Adding user to bluetooth group..."
sudo usermod -a -G bluetooth $USER

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index
    sudo apt update
    
    # Install Docker Engine
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -a -G docker $USER
    
    echo "✅ Docker installed successfully"
else
    echo "ℹ️ Docker is already installed"
fi

# Install Docker Compose (standalone)
echo "🐙 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed successfully"
else
    echo "ℹ️ Docker Compose is already installed"
fi

# Create application directory
APP_DIR="/opt/doggydoor"
echo "📁 Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files (if running from source directory)
if [ -f "Dockerfile" ]; then
    echo "📋 Copying application files..."
    cp -r . $APP_DIR/
    cd $APP_DIR
fi

# Create data and logs directories
echo "📂 Creating data and logs directories..."
mkdir -p $APP_DIR/data
mkdir -p $APP_DIR/logs

# Create configuration file from example
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚙️ Creating configuration file..."
    cp .env.example .env
    echo "📝 Please edit $APP_DIR/.env with your HomeKit and system settings"
    echo "ℹ️ AirTag detection is automatic - no specific AirTag configuration needed!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔄 Please log out and back in (or run 'newgrp docker') to use Docker without sudo"
echo ""
echo "Next steps:"
echo "1. Edit configuration: nano $APP_DIR/.env"
echo "2. Test AirTag detection (optional):"
echo "   docker run --rm --privileged ghcr.io/nranderson/doggydoor:latest python tools/scan_airtags.py"
echo "3. Calibrate distance (optional):"
echo "   docker run --rm --privileged -it ghcr.io/nranderson/doggydoor:latest python tools/calibrate_distance.py"
echo ""
echo "🐳 Deploy with Watchtower (automatic updates):"
echo "   4. Use pre-built image: cp docker-compose.ghcr.yml docker-compose.yml"
echo "   5. Start the system: docker-compose up -d"
echo "   6. Check status: docker-compose ps"
echo "   7. View logs: docker-compose logs -f"
echo ""
echo "💡 Features included:"
echo "   ✅ Pre-built images from GitHub Container Registry"
echo "   ✅ Automatic updates via Watchtower (every 6 hours)"
echo "   ✅ Auto-restart on failures and reboots"
echo "   ✅ Environment variables loaded from .env file"
echo ""
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo "📊 To monitor: docker-compose logs -f"
