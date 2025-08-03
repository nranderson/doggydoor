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

async def calibrate_distance(target_mac: str, distance_feet: float, samples: int = 10):
    """
    Calibrate RSSI at a known distance
    
    Args:
        target_mac: MAC address of the AirTag
        distance_feet: Known distance from AirTag in feet
        samples: Number of RSSI samples to collect
    """
    print(f"📏 Calibrating AirTag at {distance_feet} feet")
    print(f"🎯 Target MAC: {target_mac}")
    print(f"📊 Collecting {samples} samples...")
    print("=" * 50)
    
    target_mac = target_mac.upper().replace(':', '-')
    rssi_values = []
    
    for i in range(samples):
        print(f"Sample {i+1}/{samples}...", end=' ')
        
        try:
            devices = await BleakScanner.discover(timeout=3.0)
            
            found = False
            for device in devices:
                if device.address.upper().replace(':', '-') == target_mac:
                    rssi_values.append(device.rssi)
                    print(f"RSSI: {device.rssi} dBm")
                    found = True
                    break
            
            if not found:
                print("❌ AirTag not found")
            
            # Wait between samples
            if i < samples - 1:
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if rssi_values:
        avg_rssi = statistics.mean(rssi_values)
        std_rssi = statistics.stdev(rssi_values) if len(rssi_values) > 1 else 0
        
        print("\n📊 Calibration Results:")
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
    print("This helps you calibrate RSSI-to-distance conversion\n")
    
    # Get user input
    target_mac = input("Enter AirTag MAC address (AA:BB:CC:DD:EE:FF): ").strip()
    
    try:
        distance_feet = float(input("Enter known distance in feet (e.g., 3.0): ").strip())
    except ValueError:
        print("❌ Invalid distance value")
        return
    
    print(f"\n📍 Place the AirTag exactly {distance_feet} feet away from this device")
    input("Press Enter when ready to start calibration...")
    
    await calibrate_distance(target_mac, distance_feet)

if __name__ == "__main__":
    asyncio.run(main())
