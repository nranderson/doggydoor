# doggydoor

A lightweight Docker image for running Python applications, built on Alpine Linux for minimal size and maximum efficiency.

## Features

- 🐍 **Python 3.11** - Latest stable Python version
- 🏔️ **Alpine Linux base** - Minimal footprint (~50MB base image)
- 🔒 **Security focused** - Non-root user execution
- 📦 **Essential build tools** - gcc, make, and common development libraries
- ⚡ **Fast builds** - Optimized Docker layers for caching

## Quick Start

### Build the image

```bash
./build.sh
```

### Run with Docker

```bash
# Run the demo application
docker run --rm doggydoor:latest python app.py

# Interactive Python shell
docker run --rm -it doggydoor:latest python

# Run your own script
docker run --rm -v $(pwd):/app doggydoor:latest python your_script.py
```

### Run with Docker Compose

```bash
docker-compose up
```

## Image Size

The resulting image is approximately **150-200MB**, which includes:

- Python 3.11 runtime
- Essential build tools (gcc, make)
- Common libraries (libffi, openssl)
- Your application code

## Customization

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
