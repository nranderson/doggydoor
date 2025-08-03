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
    libavahi-compat-libdnssd-dev

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
    echo "📝 Please edit $APP_DIR/.env with your AirTag MAC address and settings"
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
echo "Next steps:"
echo "1. Edit configuration: nano $APP_DIR/.env"
echo "2. Find your AirTag MAC: python tools/scan_airtags.py"
echo "3. Calibrate distance: python tools/calibrate_distance.py"
echo "4. Test the application: python src/main.py"
echo "5. Start the service: sudo systemctl start doggydoor"
echo "6. Check status: sudo systemctl status doggydoor"
echo "7. View logs: sudo journalctl -u doggydoor -f"
echo ""
echo "🔍 To find your AirTag MAC address:"
echo "   cd $APP_DIR && source venv/bin/activate && python tools/scan_airtags.py"
echo ""
echo "⚡ Quick start (after configuration):"
echo "   sudo systemctl start doggydoor"
echo ""
echo "🛑 To stop the service:"
echo "   sudo systemctl stop doggydoor"
