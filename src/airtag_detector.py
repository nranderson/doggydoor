"""
AirTag Detection Module
Handles Bluetooth Low Energy scanning to detect AirTags and estimate distance
"""

import asyncio
import logging
import math
import time
from typing import Optional, Callable
from bleak import BleakScanner, BLEDevice
from bleak.backends.device import BLEDevice as BLEDeviceType
from src.config import Config

logger = logging.getLogger(__name__)

class AirTagDetector:
    """Detects AirTags via Bluetooth LE and estimates distance"""
    
    def __init__(self, 
                 target_mac: str,
                 proximity_threshold_feet: float = 3.0,
                 scan_interval: float = 2.0):
        """
        Initialize AirTag detector
        
        Args:
            target_mac: MAC address of the target AirTag
            proximity_threshold_feet: Distance threshold in feet
            scan_interval: How often to scan in seconds
        """
        self.target_mac = target_mac.upper().replace(':', '-')
        self.proximity_threshold_feet = proximity_threshold_feet
        self.scan_interval = scan_interval
        self.is_scanning = False
        self.last_detection_time = 0
        self.last_rssi = None
        self.proximity_callback: Optional[Callable[[bool, float], None]] = None
        
        # RSSI to distance conversion parameters
        self.rssi_at_1m = Config.RSSI_AT_CALIBRATION_DISTANCE  # Typical RSSI at 1 meter
        self.path_loss_exponent = Config.PATH_LOSS_EXPONENT  # Path loss exponent (2.0 for free space)
        
        logger.info(f"AirTag detector initialized for MAC: {self.target_mac}")
        logger.info(f"Proximity threshold: {self.proximity_threshold_feet} feet")
    
    def set_proximity_callback(self, callback: Callable[[bool, float], None]):
        """Set callback function to be called when proximity status changes"""
        self.proximity_callback = callback
    
    def rssi_to_distance_feet(self, rssi: int) -> float:
        """
        Convert RSSI to distance in feet using path loss model
        
        Args:
            rssi: Received Signal Strength Indicator in dBm
            
        Returns:
            Estimated distance in feet
        """
        if rssi == 0:
            return float('inf')
        
        # Calculate distance in meters using path loss formula
        # RSSI = RSSI_at_1m - 10 * n * log10(distance)
        # Rearranged: distance = 10^((RSSI_at_1m - RSSI) / (10 * n))
        distance_meters = 10 ** ((self.rssi_at_1m - rssi) / (10 * self.path_loss_exponent))
        
        # Convert meters to feet
        distance_feet = distance_meters * 3.28084
        
        logger.debug(f"RSSI {rssi} dBm -> {distance_feet:.2f} feet")
        return distance_feet
    
    async def scan_for_airtag(self) -> Optional[tuple[BLEDevice, float]]:
        """
        Scan for the target AirTag
        
        Returns:
            Tuple of (device, distance_feet) if found, None otherwise
        """
        try:
            logger.debug("Scanning for AirTags...")
            
            # Scan for BLE devices
            devices = await BleakScanner.discover(timeout=self.scan_interval)
            
            for device in devices:
                # Check if this is our target AirTag
                if self.is_target_airtag(device):
                    distance_feet = self.rssi_to_distance_feet(device.rssi)
                    self.last_detection_time = time.time()
                    self.last_rssi = device.rssi
                    
                    logger.debug(f"Found target AirTag: RSSI={device.rssi}, Distance={distance_feet:.2f}ft")
                    return device, distance_feet
            
            logger.debug("Target AirTag not found in scan")
            return None
            
        except Exception as e:
            logger.error(f"Error during BLE scan: {e}")
            return None
    
    def is_target_airtag(self, device: BLEDevice) -> bool:
        """
        Check if a BLE device is our target AirTag
        
        Args:
            device: BLE device to check
            
        Returns:
            True if this is the target AirTag
        """
        # Check MAC address
        if device.address.upper().replace(':', '-') == self.target_mac:
            return True
        
        # Check if device appears to be an AirTag by name or manufacturer data
        if device.name and 'airtag' in device.name.lower():
            logger.info(f"Found AirTag by name: {device.name} ({device.address})")
            return device.address.upper().replace(':', '-') == self.target_mac
        
        # Check manufacturer data for Apple (company ID 0x004C)
        if device.metadata and 'manufacturer_data' in device.metadata:
            manufacturer_data = device.metadata['manufacturer_data']
            if 0x004C in manufacturer_data:  # Apple company ID
                logger.debug(f"Found Apple device: {device.address}")
                return device.address.upper().replace(':', '-') == self.target_mac
        
        return False
    
    def is_within_proximity(self, distance_feet: float) -> bool:
        """Check if distance is within proximity threshold"""
        return distance_feet <= self.proximity_threshold_feet
    
    async def start_monitoring(self):
        """Start continuous monitoring for the target AirTag"""
        if self.is_scanning:
            logger.warning("Already scanning for AirTags")
            return
        
        self.is_scanning = True
        logger.info(f"Starting AirTag monitoring (scan interval: {self.scan_interval}s)")
        
        last_proximity_state = None
        
        try:
            while self.is_scanning:
                result = await self.scan_for_airtag()
                
                if result:
                    device, distance_feet = result
                    is_close = self.is_within_proximity(distance_feet)
                    
                    # Log detection
                    logger.info(f"AirTag detected: {distance_feet:.2f}ft {'(CLOSE)' if is_close else '(FAR)'}")
                    
                    # Call proximity callback if state changed
                    if self.proximity_callback and last_proximity_state != is_close:
                        logger.info(f"Proximity state changed: {'CLOSE' if is_close else 'FAR'}")
                        try:
                            await self.proximity_callback(is_close, distance_feet)
                        except Exception as e:
                            logger.error(f"Error in proximity callback: {e}")
                    
                    last_proximity_state = is_close
                else:
                    # No AirTag detected
                    if last_proximity_state is not False:
                        logger.info("AirTag no longer detected (assuming FAR)")
                        if self.proximity_callback:
                            try:
                                await self.proximity_callback(False, float('inf'))
                            except Exception as e:
                                logger.error(f"Error in proximity callback: {e}")
                        last_proximity_state = False
                
                # Wait before next scan
                await asyncio.sleep(self.scan_interval)
                
        except asyncio.CancelledError:
            logger.info("AirTag monitoring cancelled")
        except Exception as e:
            logger.error(f"Error in AirTag monitoring: {e}")
        finally:
            self.is_scanning = False
            logger.info("AirTag monitoring stopped")
    
    def stop_monitoring(self):
        """Stop AirTag monitoring"""
        self.is_scanning = False
    
    def get_last_detection_info(self) -> dict:
        """Get information about the last detection"""
        return {
            'last_detection_time': self.last_detection_time,
            'last_rssi': self.last_rssi,
            'seconds_since_last_detection': time.time() - self.last_detection_time if self.last_detection_time else None,
            'is_scanning': self.is_scanning
        }
