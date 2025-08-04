"""
AirTag Detection Module
Handles Bluetooth Low Energy scanning to detect AirTags and estimate distance

Note: AirTags use MAC address randomization for privacy, so we identify them
by their Bluetooth advertising data, service UUIDs, and manufacturer data.
"""

import asyncio
import logging
import math
import time
from typing import Optional, Callable, Set, Awaitable, Union
from bleak import BleakScanner, BLEDevice
from bleak.backends.device import BLEDevice as BLEDeviceType
from src.config import Config

logger = logging.getLogger(__name__)

class AirTagDetector:
    """Detects AirTags via Bluetooth LE and estimates distance"""
    
    # Apple's company identifier for Bluetooth manufacturer data
    APPLE_COMPANY_ID = 0x004C
    
    # Known AirTag service UUIDs and advertising data patterns
    AIRTAG_SERVICE_UUIDS = {
        "FD6F",  # Apple's offline finding service UUID
        "FDAB",  # Apple's continuity service UUID
    }
    
    # AirTag advertising data type identifiers
    AIRTAG_DATA_TYPES = {
        0x12,  # Offline finding advertising type
        0x1E,  # Nearby action type
    }
    
    def __init__(self, 
                 proximity_threshold_feet: float = 3.0,
                 scan_interval: float = 2.0):
        """
        Initialize AirTag detector to detect ANY Apple AirTag
        
        Args:
            proximity_threshold_feet: Distance threshold in feet
            scan_interval: How often to scan in seconds
        """
        self.proximity_threshold_feet = proximity_threshold_feet
        self.scan_interval = scan_interval
        self.is_scanning = False
        self.last_detection_time = 0
        self.last_rssi = None
        self.proximity_callback: Optional[Callable[[bool, float], Awaitable[None]]] = None
        
        # Track known AirTag addresses (they change, but we can track recent ones)
        self.known_airtag_addresses: Set[str] = set()
        
        # RSSI to distance conversion parameters
        self.rssi_at_1m = Config.RSSI_AT_CALIBRATION_DISTANCE
        self.path_loss_exponent = Config.PATH_LOSS_EXPONENT
        
        logger.info("AirTag detector initialized to detect ANY Apple AirTag")
        logger.info(f"Proximity threshold: {self.proximity_threshold_feet} feet")
        logger.warning("Note: AirTags use MAC randomization. Detection based on advertising data patterns.")
    
    def set_proximity_callback(self, callback: Callable[[bool, float], Awaitable[None]]):
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
        Scan for ANY AirTag and return the closest one
        
        Returns:
            Tuple of (device, distance_feet) if found, None otherwise
        """
        try:
            logger.debug("Scanning for any AirTags...")
            
            closest_airtag = None
            closest_distance = float('inf')
            
            def device_found(device, advertisement_data):
                nonlocal closest_airtag, closest_distance
                
                # Check if this is an AirTag
                if self.is_any_airtag(device, advertisement_data):
                    distance_feet = self.rssi_to_distance_feet(advertisement_data.rssi)
                    
                    # Keep track of the closest one
                    if distance_feet < closest_distance:
                        closest_airtag = device
                        closest_distance = distance_feet
                    
                    logger.debug(f"Found AirTag: RSSI={advertisement_data.rssi}, Distance={distance_feet:.2f}ft")
            
            # Use callback-based scanning
            scanner = BleakScanner(device_found)
            await scanner.start()
            await asyncio.sleep(self.scan_interval)
            await scanner.stop()
            
            if closest_airtag:
                self.last_detection_time = time.time()
                # Get RSSI from the last advertisement data (stored in closest_distance calculation)
                rssi = self.rssi_to_distance_feet_inverse(closest_distance)
                self.last_rssi = rssi
                logger.debug(f"Closest AirTag: Distance={closest_distance:.2f}ft")
                return closest_airtag, closest_distance
            
            logger.debug("No AirTags found in scan")
            return None
            
        except Exception as e:
            logger.error(f"Error during BLE scan: {e}")
            return None
    
    def rssi_to_distance_feet_inverse(self, distance_feet: float) -> int:
        """Convert distance back to RSSI (for logging purposes)"""
        distance_meters = distance_feet / 3.28084
        rssi = self.rssi_at_1m - (10 * self.path_loss_exponent * math.log10(distance_meters))
        return int(rssi)

    def is_any_airtag(self, device: BLEDevice, advertisement_data) -> bool:
        """
        Check if a BLE device is likely an AirTag using advertising data patterns
        
        Args:
            device: BLE device to check
            advertisement_data: Advertisement data from the device
            
        Returns:
            True if this appears to be an AirTag
        """
        # First check if this is a known Apple device
        if not self._is_apple_device(device, advertisement_data):
            return False
        
        # Check for AirTag-specific service UUIDs
        if advertisement_data.service_uuids:
            device_uuids = set(str(uuid).upper() for uuid in advertisement_data.service_uuids)
            if device_uuids.intersection(self.AIRTAG_SERVICE_UUIDS):
                logger.debug(f"Found AirTag by service UUID: {device.address}")
                self.known_airtag_addresses.add(device.address)
                return True
        
        # Check for AirTag-specific advertising data patterns
        if self._has_airtag_advertising_data(device, advertisement_data):
            logger.debug(f"Found AirTag by advertising data: {device.address}")
            self.known_airtag_addresses.add(device.address)
            return True
        
        # Check if this is a previously seen AirTag address
        # (AirTags may not always advertise the same data)
        if device.address in self.known_airtag_addresses:
            logger.debug(f"Found known AirTag address: {device.address}")
            return True
        
        return False
    
    def _is_apple_device(self, device: BLEDevice, advertisement_data) -> bool:
        """Check if device is from Apple based on manufacturer data"""
        if not advertisement_data.manufacturer_data:
            return False
        
        return self.APPLE_COMPANY_ID in advertisement_data.manufacturer_data
    
    def _has_airtag_advertising_data(self, device: BLEDevice, advertisement_data) -> bool:
        """
        Check for AirTag-specific advertising data patterns
        
        AirTags advertise with specific data patterns that can help identify them
        even when MAC addresses change.
        """
        if not advertisement_data.manufacturer_data:
            return False
        
        apple_data = advertisement_data.manufacturer_data.get(self.APPLE_COMPANY_ID)
        
        if not apple_data or len(apple_data) < 2:
            return False
        
        # Check for AirTag advertising data type identifiers
        data_type = apple_data[0]
        if data_type in self.AIRTAG_DATA_TYPES:
            return True
        
        # Additional pattern matching could be added here
        # For example, checking specific byte patterns that AirTags use
        
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
