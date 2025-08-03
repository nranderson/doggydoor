#!/usr/bin/env python3
"""
Distance Calibration Tool
Use this script to calibrate RSSI-to-distance conversion for your AirTag
"""

import asyncio
import logging
import statistics
from bleak import BleakScanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_likely_airtag(device):
    """Check if a device is likely an AirTag based on advertising data"""
    # Check for Apple manufacturer data
    has_apple_data = False
    if device.metadata and 'manufacturer_data' in device.metadata:
        manufacturer_data = device.metadata['manufacturer_data']
        if 0x004C in manufacturer_data:
            has_apple_data = True
    
    # Check for AirTag service UUIDs
    has_airtag_service = False
    if device.metadata and 'service_uuids' in device.metadata:
        service_uuids = device.metadata['service_uuids']
        airtag_uuids = ['FD6F', 'FDAB']
        for uuid in service_uuids:
            if any(airtag_uuid.lower() in str(uuid).lower() for airtag_uuid in airtag_uuids):
                has_airtag_service = True
                break
    
    # Check name
    has_airtag_name = device.name and 'airtag' in device.name.lower()
    
    return has_apple_data and (has_airtag_service or has_airtag_name)

def find_best_airtag(devices):
    """Find the AirTag with the strongest signal"""
    best_airtag = None
    best_rssi = -999
    
    for device in devices:
        if is_likely_airtag(device) and device.rssi > best_rssi:
            best_airtag = device
            best_rssi = device.rssi
    
    return best_airtag

async def collect_sample(sample_num, total_samples):
    """Collect a single RSSI sample"""
    print(f"Sample {sample_num}/{total_samples}...", end=' ')
    
    try:
        devices = await BleakScanner.discover(timeout=3.0)
        best_airtag = find_best_airtag(devices)
        
        if best_airtag:
            airtag_info = {
                'name': best_airtag.name or 'Unknown AirTag',
                'address': best_airtag.address
            }
            print(f"RSSI: {best_airtag.rssi} dBm ({airtag_info['name']})")
            return best_airtag.rssi, airtag_info
        else:
            print("❌ No AirTag found")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

async def calibrate_distance(distance_feet: float, samples: int = 10):
    """
    Calibrate RSSI at a known distance for any detected AirTag
    
    Args:
        distance_feet: Known distance from AirTag in feet
        samples: Number of RSSI samples to collect
    """
    print(f"📏 Calibrating AirTag at {distance_feet} feet")
    print(f"📊 Collecting {samples} samples...")
    print("Will use the strongest AirTag signal found")
    print("=" * 50)
    
    rssi_values = []
    airtag_info = None
    
    for i in range(samples):
        rssi, info = await collect_sample(i + 1, samples)
        
        if rssi is not None:
            rssi_values.append(rssi)
            airtag_info = info
        
        # Wait between samples
        if i < samples - 1:
            await asyncio.sleep(2)
    
    if rssi_values:
        avg_rssi = statistics.mean(rssi_values)
        std_rssi = statistics.stdev(rssi_values) if len(rssi_values) > 1 else 0
        
        print("\n📊 Calibration Results:")
        if airtag_info:
            print(f"  AirTag: {airtag_info['name']}")
        print(f"  Distance: {distance_feet} feet")
        print(f"  Average RSSI: {avg_rssi:.1f} dBm")
        print(f"  Standard Deviation: {std_rssi:.1f} dBm")
        print(f"  Samples collected: {len(rssi_values)}")
        print(f"  RSSI range: {min(rssi_values)} to {max(rssi_values)} dBm")
        
        print("\n⚙️ Configuration values:")
        print(f"RSSI_CALIBRATION_DISTANCE_FEET={distance_feet}")
        print(f"RSSI_AT_CALIBRATION_DISTANCE={int(avg_rssi)}")
        
    else:
        print("❌ No RSSI samples collected. Make sure the AirTag is nearby and active.")

async def main():
    print("AirTag Distance Calibration Tool")
    print("This helps you calibrate RSSI-to-distance conversion")
    print("Note: Will automatically detect any nearby AirTag\n")
    
    try:
        distance_input = await asyncio.to_thread(input, "Enter known distance in feet (e.g., 3.0): ")
        distance_feet = float(distance_input.strip())
    except ValueError:
        print("❌ Invalid distance value")
        return
    
    print(f"\n📍 Place any AirTag exactly {distance_feet} feet away from this device")
    await asyncio.to_thread(input, "Press Enter when ready to start calibration...")
    
    await calibrate_distance(distance_feet)

if __name__ == "__main__":
    asyncio.run(main())
