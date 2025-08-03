#!/usr/bin/env python3
"""
AirTag Scanner Utility
Use this script to find your AirTag's MAC address
"""

import asyncio
import logging
from bleak import BleakScanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scan_for_airtags():
    """Scan for nearby AirTags and Apple devices"""
    print("🔍 Scanning for AirTags and Apple devices...")
    print("Make sure your AirTag is nearby and active!")
    print("=" * 50)
    
    try:
        devices = await BleakScanner.discover(timeout=10.0)
        
        apple_devices = []
        possible_airtags = []
        
        for device in devices:
            # Check for Apple devices (company ID 0x004C)
            is_apple = False
            if device.metadata and 'manufacturer_data' in device.metadata:
                manufacturer_data = device.metadata['manufacturer_data']
                if 0x004C in manufacturer_data:
                    is_apple = True
            
            # Check name for AirTag indicators
            is_airtag_name = device.name and 'airtag' in device.name.lower()
            
            if is_apple or is_airtag_name:
                device_info = {
                    'address': device.address,
                    'name': device.name or 'Unknown',
                    'rssi': device.rssi,
                    'is_apple': is_apple,
                    'is_airtag_name': is_airtag_name
                }
                
                if is_airtag_name:
                    possible_airtags.append(device_info)
                else:
                    apple_devices.append(device_info)
        
        # Display results
        if possible_airtags:
            print("🎯 Possible AirTags found:")
            for device in possible_airtags:
                print(f"  📍 {device['address']} - {device['name']} (RSSI: {device['rssi']})")
        
        if apple_devices:
            print("\n🍎 Other Apple devices found:")
            for device in apple_devices:
                print(f"  📱 {device['address']} - {device['name']} (RSSI: {device['rssi']})")
        
        if not apple_devices and not possible_airtags:
            print("❌ No Apple devices or AirTags found.")
            print("Tips:")
            print("  - Make sure your AirTag is nearby")
            print("  - Try moving the AirTag to activate it")
            print("  - Check that Bluetooth is enabled")
        
        print(f"\n📊 Total devices scanned: {len(devices)}")
        
    except Exception as e:
        logger.error(f"Error during scan: {e}")

if __name__ == "__main__":
    print("AirTag Scanner - Find your AirTag's MAC address")
    print("This will help you configure the AIRTAG_MAC_ADDRESS setting\n")
    
    asyncio.run(scan_for_airtags())
