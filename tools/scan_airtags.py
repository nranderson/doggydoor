#!/usr/bin/env python3
"""
AirTag Scanner Utility
Use this script to detect and identify AirTags for configuration
"""

import asyncio
import logging
from bleak import BleakScanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_apple_device(device):
    """Check if device has Apple manufacturer data"""
    if not device.metadata or 'manufacturer_data' not in device.metadata:
        return False
    manufacturer_data = device.metadata['manufacturer_data']
    return 0x004C in manufacturer_data

def has_airtag_services(device):
    """Check if device has AirTag service UUIDs"""
    if not device.metadata or 'service_uuids' not in device.metadata:
        return False
    service_uuids = device.metadata['service_uuids']
    airtag_uuids = ['FD6F', 'FDAB']
    for uuid in service_uuids:
        if any(airtag_uuid.lower() in str(uuid).lower() for airtag_uuid in airtag_uuids):
            return True
    return False

def has_airtag_name(device):
    """Check if device name suggests it's an AirTag"""
    return device.name and 'airtag' in device.name.lower()

def classify_device(device):
    """Classify a BLE device as AirTag or other Apple device"""
    is_apple = is_apple_device(device)
    has_services = has_airtag_services(device)
    has_name = has_airtag_name(device)
    
    device_info = {
        'address': device.address,
        'name': device.name or 'Unknown',
        'rssi': device.rssi,
        'is_apple': is_apple,
        'is_airtag_name': has_name,
        'has_airtag_service': has_services
    }
    
    is_likely_airtag = has_name or has_services
    return device_info, is_likely_airtag

def print_results(possible_airtags, apple_devices, total_devices):
    """Print scan results to console"""
    if possible_airtags:
        print("🎯 Possible AirTags found:")
        for device in possible_airtags:
            indicators = []
            if device['is_airtag_name']:
                indicators.append("Name")
            if device['has_airtag_service']:
                indicators.append("Service")
            print(f"  📍 {device['name']} (RSSI: {device['rssi']}) - Detected by: {', '.join(indicators)}")
    
    if apple_devices:
        print("\n🍎 Other Apple devices found:")
        for device in apple_devices:
            print(f"  📱 {device['name']} (RSSI: {device['rssi']})")
    
    if not apple_devices and not possible_airtags:
        print("❌ No Apple devices or AirTags found.")
        print("Tips:")
        print("  - Make sure your AirTag is nearby")
        print("  - Try moving the AirTag to activate it")
        print("  - Check that Bluetooth is enabled")
    else:
        print("\n💡 Configuration Help:")
        print("Since AirTags use MAC address randomization for privacy,")
        print("the system detects them by advertising patterns instead.")
        print("You can use any unique identifier in AIRTAG_IDENTIFIER.")
        print("Examples: 'fluffy-collar', 'dog-tag-1', 'backyard-door'")
    
    print(f"\n📊 Total devices scanned: {total_devices}")

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
            is_apple = is_apple_device(device)
            has_name = has_airtag_name(device)
            has_services = has_airtag_services(device)
            
            if is_apple or has_name or has_services:
                device_info, is_likely_airtag = classify_device(device)
                
                if is_likely_airtag:
                    possible_airtags.append(device_info)
                else:
                    apple_devices.append(device_info)
        
        print_results(possible_airtags, apple_devices, len(devices))
        
    except Exception as e:
        logger.error(f"Error during scan: {e}")

if __name__ == "__main__":
    print("AirTag Scanner - Detect and identify AirTags")
    print("This will help you verify AirTag detection for the AIRTAG_IDENTIFIER setting\n")
    
    asyncio.run(scan_for_airtags())
