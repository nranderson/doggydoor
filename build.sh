#!/bin/bash

# Build and test script for the Doggy Door AirTag Detection System

set -e

echo "� Building Doggy Door Docker image..."

# Build the image
docker build -t doggydoor:latest .

echo "✅ Image built successfully!"

# Show image size
echo "📊 Image size:"
docker images doggydoor:latest

echo ""
echo "🧪 Testing the image..."

# Test the image
docker run --rm doggydoor:latest python app.py

echo ""
echo "✅ Image test completed!"

echo ""
echo "📝 Usage examples:"
echo "  # Run the demo app:"
echo "  docker run --rm doggydoor:latest python app.py"
echo ""
echo "  # Run the main doggy door system:"
echo "  docker run --rm --privileged --network host doggydoor:latest python src/main.py"
echo ""
echo "  # Scan for AirTags:"
echo "  docker run --rm --privileged doggydoor:latest python tools/scan_airtags.py"
echo ""
echo "  # Run with docker-compose (recommended for Raspberry Pi):"
echo "  docker-compose up"
echo ""
echo "  # Interactive shell:"
echo "  docker run --rm -it doggydoor:latest sh"
echo ""
echo "🎯 For Raspberry Pi deployment:"
echo "  1. Copy files to Pi: scp -r . pi@your-pi:/home/pi/doggydoor"
echo "  2. Run setup: ./setup_pi.sh"
echo "  3. Configure: nano .env"
echo "  4. Start: sudo systemctl start doggydoor"
