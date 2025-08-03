# 🐕 Doggy Door AirTag Detection System

An intelligent doggy door system that detects **ANY** Apple AirTag within 3 feet to automatically control access. Perfect for families with multiple AirTags - no configuration needed, just works with any AirTag that comes close!

**🐳 Docker-First Design** - Just run one setup script and you're ready to go! No Python environment setup required.

## ✨ Features

- 🎯 **Universal AirTag Detection** - Works with ANY Apple AirTag, no setup required
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

# 2. SSH to Pi and run setup (installs Docker)
ssh pi@your-pi-ip
cd doggydoor
./setup_pi.sh

# 3. Log out and back in to activate Docker permissions
exit
ssh pi@your-pi-ip
cd doggydoor

# 4. Configure the system
cp .env.example .env
nano .env  # Adjust HomeKit settings if needed

# 5. Build and run with Docker
./build.sh
docker-compose up -d

# 6. Check status and logs
docker-compose ps
docker-compose logs -f
```

### For Development/Testing

```bash
# Build the Docker image
./build.sh

# Test AirTag detection
docker run --rm --privileged doggydoor:latest python tools/scan_airtags.py

# Run with Docker Compose
docker-compose up
```

## 📋 Prerequisites

### Hardware Requirements

- Raspberry Pi 3B+ or newer (recommended)
- Bluetooth adapter (built-in Pi Bluetooth works)
- AirTag (any Apple AirTag will work)
- HomeKit-compatible smart switch/lock

### Software Requirements

- Raspberry Pi OS (Bullseye or newer)
- Docker (automatically installed by setup script)
- That's it! No Python setup needed - everything runs in Docker

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Detection mode: ANY Apple AirTag (no configuration needed!)
# Distance threshold in feet
PROXIMITY_THRESHOLD_FEET=3.0

# HomeKit settings (choose one method)
HOMEKIT_BRIDGE_NAME=Doggy Door Bridge
HOMEKIT_BRIDGE_PIN=123-45-678

# Safety settings
FAIL_SAFE_MODE=true
AUTO_UNLOCK_TIMEOUT_MINUTES=10
```

**Note:** The `.env` file is automatically loaded into the Docker container when you run `docker-compose up`. No additional configuration needed!

## 🔧 Setup Guide

### 1. Test AirTag Detection (Optional)

```bash
# Test AirTag detection using Docker
docker run --rm --privileged doggydoor:latest python tools/scan_airtags.py
```

This will scan for nearby Apple devices and confirm the system can detect AirTags.

### 2. Calibrate Distance (Optional)

```bash
# Calibrate distance estimation using Docker
docker run --rm --privileged -it doggydoor:latest python tools/calibrate_distance.py
```

Place an AirTag at a known distance and run this tool to improve distance accuracy.

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
# Container status
docker-compose ps

# Live logs
docker-compose logs -f

# System resources
docker stats doggydoor_app_1

# Restart count and uptime
docker inspect doggydoor-app --format='{{.RestartCount}} restarts, uptime: {{.State.StartedAt}}'
```

### Log Files

- Container logs: `docker-compose logs`
- Bluetooth debugging: `sudo systemctl status bluetooth`
- Docker system: `docker system df`

## 🛠️ Troubleshooting

### AirTag Not Detected

- Ensure AirTag is nearby and active (shake it)
- Check Bluetooth is enabled: `sudo systemctl status bluetooth`
- Test AirTag detection: `docker run --rm --privileged doggydoor:latest python tools/scan_airtags.py`
- Verify container has Bluetooth access

### Docker Issues

- Check container is running: `docker-compose ps`
- Restart container: `docker-compose restart`
- Rebuild image: `./build.sh && docker-compose up -d`
- Check container privileges: Container must run with `--privileged` for Bluetooth
- Verify .env file exists: `ls -la .env` (must be present for configuration)
- Check restart count: `docker inspect doggydoor-app --format='{{.RestartCount}}'`

### Auto-Restart Behavior

The container is configured with `restart: unless-stopped` which means:

- **Automatic restart** on crashes or failures
- **Survives system reboots** - restarts when Docker daemon starts
- **Manual stop respected** - won't restart if you manually stop it with `docker-compose down`
- **No restart loop protection** - will keep trying to restart failed containers

### Configuration Issues

- Ensure `.env` file exists in the same directory as `docker-compose.yml`
- Check environment variables are loaded: `docker-compose config` (shows resolved config)
- Verify .env format: No spaces around `=`, no quotes unless needed
- Test configuration: `docker run --rm --env-file .env doggydoor:latest python -c "from src.config import Config; Config.print_config()"`

### HomeKit Issues

- Check network connectivity
- Verify HomeKit credentials/PIN in `.env`
- Test HomeKit switch manually in Home app
- Check firewall settings (port 51827 for HAP)

### Permission Errors

- Ensure user is in `docker` group: `groups $USER`
- Check container has `--privileged` flag (set in docker-compose.yml)
- Verify Bluetooth access: `sudo systemctl status bluetooth`

### Distance Accuracy

- Run calibration: `docker run --rm --privileged -it doggydoor:latest python tools/calibrate_distance.py`
- Adjust `RSSI_AT_CALIBRATION_DISTANCE` in `.env`
- Consider environmental factors (walls, interference)

## 🔒 Security Considerations

- **Fail-Safe Mode**: Door locks on errors by default
- **Auto-Lock Timer**: Automatically locks after timeout
- **Non-Root Execution**: Container runs as non-privileged user
- **HomeKit Encryption**: All HomeKit communication is encrypted
- **Local Operation**: No cloud dependencies required
- **Auto-Restart**: Container automatically restarts if it stops or crashes

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

## 🐾 Credits

Made with ❤️ for dogs who deserve smart doors!

**License:** MIT License - see LICENSE file for details
