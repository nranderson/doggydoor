#!/usr/bin/env python3
"""
Simple Python application to demonstrate the Docker container.
"""

import sys
import platform
import os

def main():
    print("🐍 Python Docker Container Demo")
    print("=" * 40)
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Current user: {os.getenv('USER', 'unknown')}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print("=" * 40)
    print("✅ Python is running successfully in the container!")

if __name__ == "__main__":
    main()
