#!/bin/bash

# Build and test script for the lightweight Python Docker image

set -e

echo "🐋 Building lightweight Python Docker image..."

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
echo "  # Run with docker-compose:"
echo "  docker-compose up"
echo ""
echo "  # Interactive Python shell:"
echo "  docker run --rm -it doggydoor:latest python"
echo ""
echo "  # Mount current directory and run:"
echo "  docker run --rm -v \$(pwd):/app doggydoor:latest python your_script.py"
