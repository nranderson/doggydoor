#!/bin/bash

# Setup script for Doggy Door on Raspberry Pi

set -e

echo "🐕 Doggy Door Setup Script"
echo "=========================="

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
    libbluetooth-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    avahi-daemon \
    libavahi-compat-libdnssd-dev \
    ca-certificates \
    gnupg \
    lsb-release

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

# Enable Bluetooth service
echo "📡 Enabling Bluetooth service..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Add user to bluetooth group
echo "👤 Adding user to bluetooth group..."
sudo usermod -a -G bluetooth $USER

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

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create configuration file from example
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚙️ Creating configuration file..."
    cp .env.example .env
    echo "📝 Please edit $APP_DIR/.env with your HomeKit and system settings"
    echo "ℹ️ AirTag detection is automatic - no specific AirTag configuration needed!"
fi

# Create systemd service file
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/doggydoor.service > /dev/null << EOF
[Unit]
Description=Doggy Door AirTag Detection System
After=network.target bluetooth.target
Wants=bluetooth.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python src/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Bluetooth permissions
SupplementaryGroups=bluetooth

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable service (but don't start yet)
sudo systemctl enable doggydoor

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔄 Please log out and back in (or run 'newgrp docker') to use Docker without sudo"
echo ""
echo "Next steps:"
echo "1. Edit configuration: nano $APP_DIR/.env"
echo "2. Test AirTag detection: python tools/scan_airtags.py"
echo "3. Calibrate distance (optional): python tools/calibrate_distance.py"
echo ""
echo "🐍 Option A - Run with Python (native):"
echo "   4a. Test the application: python src/main.py"
echo "   5a. Start the service: sudo systemctl start doggydoor"
echo "   6a. Check status: sudo systemctl status doggydoor"
echo "   7a. View logs: sudo journalctl -u doggydoor -f"
echo ""
echo "� Option B - Run with Docker (recommended):"
echo "   4b. Build Docker image: ./build.sh"
echo "   5b. Run with Docker Compose: docker-compose up -d"
echo "   6b. Check status: docker-compose ps"
echo "   7b. View logs: docker-compose logs -f"
echo ""
echo "🔍 To find and test AirTags:"
echo "   cd $APP_DIR && source venv/bin/activate && python tools/scan_airtags.py"
echo ""
echo "⚡ Quick start options:"
echo "   Native Python: sudo systemctl start doggydoor"
echo "   Docker:        docker-compose up -d"
echo ""
echo "🛑 To stop:"
echo "   Native Python: sudo systemctl stop doggydoor"
echo "   Docker:        docker-compose down"
