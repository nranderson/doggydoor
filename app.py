#!/usr/bin/env python3
"""
Doggy Door AirTag Detection System - Demo Application
"""

import sys
import platform
import os

def main():
    print("� Doggy Door AirTag Detection System")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Current user: {os.getenv('USER', 'unknown')}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print("=" * 50)
    print("✅ Python is running successfully in the container!")
    print("")
    print("🚀 To run the full doggy door system:")
    print("   python src/main.py")
    print("")
    print("🔍 To scan for AirTags:")
    print("   python tools/scan_airtags.py")
    print("")
    print("📏 To calibrate distance:")
    print("   python tools/calibrate_distance.py")

if __name__ == "__main__":
    main()
