# 🐕 Doggy Door AirTag Detection System

An intelligent doggy door system that uses Apple AirTag detection to automatically control access. When your dog (wearing an AirTag) approaches within 3 feet, the system unlocks the door via HomeKit. When they move away, it locks again.

Perfect for Raspberry Pi deployment with Docker support.

## ✨ Features

- 🎯 **AirTag Detection** - Bluetooth LE scanning to detect nearby AirTags
- 📏 **Distance Estimation** - RSSI-based distance calculation in feet
- 🏠 **HomeKit Integration** - Control any HomeKit-compatible switch/lock
- 🔒 **Safety First** - Fail-safe mode and auto-lock timeout
- 🐳 **Docker Ready** - Lightweight Alpine Linux container
- 🍓 **Raspberry Pi Optimized** - Systemd service and setup scripts
- 📊 **Comprehensive Logging** - Monitor system status and performance

## 🚀 Quick Start

### For Raspberry Pi (Recommended)

```bash
# 1. Copy to your Raspberry Pi
scp -r . pi@your-pi-ip:/home/pi/doggydoor

# 2. SSH to Pi and run setup
ssh pi@your-pi-ip
cd doggydoor
./setup_pi.sh

# 3. Identify your AirTag
source venv/bin/activate
python tools/scan_airtags.py

# 4. Configure the system
cp .env.example .env
nano .env  # Edit with your AirTag identifier and settings

# 5. Test the application
python src/main.py

# 6. Install as system service
sudo systemctl start doggydoor
sudo systemctl enable doggydoor
```

### For Development/Testing

```bash
# Build the Docker image
./build.sh

# Scan for AirTags
docker run --rm --privileged doggydoor:latest python tools/scan_airtags.py

# Run with Docker Compose
docker-compose up
```

## 📋 Prerequisites

### Hardware Requirements

- Raspberry Pi 3B+ or newer (recommended)
- Bluetooth adapter (built-in Pi Bluetooth works)
- AirTag attached to your dog's collar
- HomeKit-compatible smart switch/lock

### Software Requirements

- Raspberry Pi OS (Bullseye or newer)
- Docker and Docker Compose (for containerized deployment)
- Python 3.9+ (for native deployment)

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Your AirTag's identifier (configure to identify your specific AirTag)
AIRTAG_IDENTIFIER=my-dog-airtag

# Distance threshold in feet
PROXIMITY_THRESHOLD_FEET=3.0

# HomeKit settings (choose one method)
HOMEKIT_BRIDGE_NAME=Doggy Door Bridge
HOMEKIT_BRIDGE_PIN=123-45-678

# Safety settings
FAIL_SAFE_MODE=true
AUTO_UNLOCK_TIMEOUT_MINUTES=10
```

## 🔧 Setup Guide

### 1. Identify Your AirTag

```bash
python tools/scan_airtags.py
```

This will scan for nearby Apple devices and help you identify your AirTag.

### 2. Calibrate Distance (Optional)

```bash
python tools/calibrate_distance.py
```

Place your AirTag at a known distance and run this tool to improve distance accuracy.

### 3. HomeKit Configuration

**Option A: Create New HomeKit Bridge (Easier)**

- Use the built-in HomeKit bridge
- Add to your Home app with the PIN from your config
- The switch will appear as "Doggy Door Lock"

**Option B: Use Existing HomeKit Hub (Advanced)**

- Configure API access to your existing HomeKit hub
- Set `HOMEKIT_API_URL` and related settings in `.env`

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    AirTag       │    │  Raspberry Pi   │    │   HomeKit       │
│   (on dog)      │◄──►│  Doggy Door     │◄──►│    Switch       │
│                 │    │    System       │    │   (door lock)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
      Bluetooth LE           Main App              Network/HAP
```

## 📊 Monitoring

### Check System Status

```bash
# Service status
sudo systemctl status doggydoor

# Live logs
sudo journalctl -u doggydoor -f

# Application logs
tail -f /opt/doggydoor/logs/doggydoor.log
```

### Log Files

- System logs: `journalctl -u doggydoor`
- Application logs: `/opt/doggydoor/logs/doggydoor.log`
- Bluetooth debugging: `sudo systemctl status bluetooth`

## 🛠️ Troubleshooting

### AirTag Not Detected

- Ensure AirTag is nearby and active (shake it)
- Check Bluetooth is enabled: `sudo systemctl status bluetooth`
- Verify AirTag identifier in configuration
- Run scan tool: `python tools/scan_airtags.py`

### HomeKit Issues

- Check network connectivity
- Verify HomeKit credentials/PIN
- Test HomeKit switch manually in Home app
- Check firewall settings (port 51827 for HAP)

### Permission Errors

- Ensure user is in `bluetooth` group: `groups $USER`
- Check container has `--privileged` flag
- Verify `/dev/bus/usb` access for Docker

### Distance Accuracy

- Run calibration tool: `python tools/calibrate_distance.py`
- Adjust `RSSI_AT_CALIBRATION_DISTANCE` in config
- Consider environmental factors (walls, interference)

## 🔒 Security Considerations

- **Fail-Safe Mode**: Door locks on errors by default
- **Auto-Lock Timer**: Automatically locks after timeout
- **Non-Root Execution**: Container runs as non-privileged user
- **HomeKit Encryption**: All HomeKit communication is encrypted
- **Local Operation**: No cloud dependencies required

## 📦 Project Structure

```
doggydoor/
├── src/                    # Main application code
│   ├── main.py            # Application entry point
│   ├── airtag_detector.py # Bluetooth LE AirTag detection
│   ├── homekit_controller.py # HomeKit integration
│   └── config.py          # Configuration management
├── tools/                 # Utility scripts
│   ├── scan_airtags.py    # Detect and identify AirTags
│   └── calibrate_distance.py # Distance calibration
├── Dockerfile             # Container definition
├── docker-compose.yml     # Multi-container setup
├── setup_pi.sh           # Raspberry Pi setup script
├── .env.example          # Configuration template
└── requirements.txt      # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test on Raspberry Pi hardware
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🐾 Credits

Made with ❤️ for dogs who deserve smart doors!

### Adding Dependencies

1. Edit `requirements.txt` to add your Python packages
2. Rebuild the image: `./build.sh`

### Modifying the Base Image

The Dockerfile uses `python:3.11-alpine` for the smallest footprint. You can modify this to:

- `python:3.11-slim` - Debian-based, larger but more compatible
- `python:3.12-alpine` - Latest Python version
- `python:3.11-alpine3.18` - Specific Alpine version

### Security

The image runs as a non-root user (`appuser`) with UID/GID 1000 for enhanced security.

## Development

### Project Structure

```
.
├── Dockerfile          # Multi-stage Docker build
├── .dockerignore      # Files to exclude from build context
├── requirements.txt   # Python dependencies
├── app.py            # Demo Python application
├── docker-compose.yml # Container orchestration
├── build.sh          # Build and test script
└── README.md         # This file
```

### Best Practices

1. **Layer caching**: Requirements are installed before copying application code
2. **Security**: Non-root user execution
3. **Size optimization**: Alpine base with minimal dependencies
4. **Build efficiency**: .dockerignore excludes unnecessary files

## Troubleshooting

### Build fails with package compilation errors

Some Python packages need additional Alpine packages. Add them to the Dockerfile:

```dockerfile
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    postgresql-dev \  # For psycopg2
    jpeg-dev \        # For Pillow
    zlib-dev          # For various packages
```

### Permission errors

Ensure your application doesn't require root privileges. The container runs as user `appuser` (UID 1000).
