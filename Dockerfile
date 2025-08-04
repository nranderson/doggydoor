# Use Alpine Linux as the base image for minimal size
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install essential system dependencies for Python packages and Bluetooth
# - build-base: Contains gcc, make, and other build tools
# - libffi-dev: For packages that need FFI
# - openssl-dev: For SSL/TLS support
# - bluez-dev: Bluetooth development libraries
# - dbus-dev: D-Bus development libraries (needed for Bluetooth)
# - linux-headers: Linux kernel headers
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    bluez-dev \
    dbus-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Create a non-root user for security
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# Create necessary directories and change ownership
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy requirements file first (if it exists) for better Docker layer caching
# This allows pip install to be cached if requirements don't change
COPY --chown=appuser:appuser requirements.txt* ./

# Install Python dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir --user -r requirements.txt; fi

# Copy the rest of the application code
COPY --chown=appuser:appuser . .

# Set the PATH to include user-installed packages
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Set PYTHONPATH to include the app directory so 'src' module can be found
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Default command - can be overridden
CMD ["python", "--version"]
