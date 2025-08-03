"""
Configuration settings for the Doggy Door AirTag Detection System
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the doggy door system"""
    
    # AirTag Detection Settings
    # Note: No identifier needed - detects ANY Apple AirTag within range
    PROXIMITY_THRESHOLD_FEET: float = float(os.getenv('PROXIMITY_THRESHOLD_FEET', '3.0'))
    SCAN_INTERVAL_SECONDS: int = int(os.getenv('SCAN_INTERVAL_SECONDS', '2'))
    RSSI_CALIBRATION_DISTANCE_FEET: float = float(os.getenv('RSSI_CALIBRATION_DISTANCE_FEET', '3.28'))  # 1 meter
    RSSI_AT_CALIBRATION_DISTANCE: int = int(os.getenv('RSSI_AT_CALIBRATION_DISTANCE', '-59'))
    PATH_LOSS_EXPONENT: float = float(os.getenv('PATH_LOSS_EXPONENT', '2.0'))
    
    # HomeKit Settings
    HOMEKIT_BRIDGE_NAME: str = os.getenv('HOMEKIT_BRIDGE_NAME', 'Doggy Door Bridge')
    HOMEKIT_BRIDGE_PIN: str = os.getenv('HOMEKIT_BRIDGE_PIN', '123-45-678')
    HOMEKIT_SWITCH_NAME: str = os.getenv('HOMEKIT_SWITCH_NAME', 'Doggy Door Lock')
    HOMEKIT_PORT: int = int(os.getenv('HOMEKIT_PORT', '51827'))
    
    # Alternative: HTTP API Settings (if using existing HomeKit hub)
    HOMEKIT_API_URL: Optional[str] = os.getenv('HOMEKIT_API_URL')
    HOMEKIT_API_TOKEN: Optional[str] = os.getenv('HOMEKIT_API_TOKEN')
    HOMEKIT_SWITCH_ID: Optional[str] = os.getenv('HOMEKIT_SWITCH_ID')
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', '/app/logs/doggydoor.log')
    
    # Safety Settings
    FAIL_SAFE_MODE: bool = os.getenv('FAIL_SAFE_MODE', 'true').lower() == 'true'
    AUTO_UNLOCK_TIMEOUT_MINUTES: int = int(os.getenv('AUTO_UNLOCK_TIMEOUT_MINUTES', '10'))
    
    # Device Settings
    BLUETOOTH_ADAPTER: str = os.getenv('BLUETOOTH_ADAPTER', 'hci0')
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if cls.PROXIMITY_THRESHOLD_FEET <= 0:
            errors.append("PROXIMITY_THRESHOLD_FEET must be positive")
            
        if cls.SCAN_INTERVAL_SECONDS <= 0:
            errors.append("SCAN_INTERVAL_SECONDS must be positive")
            
        if not cls.HOMEKIT_API_URL and not cls.HOMEKIT_BRIDGE_PIN:
            errors.append("Either HOMEKIT_API_URL or HOMEKIT_BRIDGE_PIN must be set")
            
        return errors
    
    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)"""
        print("=== Doggy Door Configuration ===")
        print("Detection Mode: ANY Apple AirTag")
        print(f"Proximity Threshold: {cls.PROXIMITY_THRESHOLD_FEET} feet")
        print(f"Scan Interval: {cls.SCAN_INTERVAL_SECONDS} seconds")
        print(f"HomeKit Bridge: {cls.HOMEKIT_BRIDGE_NAME}")
        print(f"Switch Name: {cls.HOMEKIT_SWITCH_NAME}")
        print(f"Fail Safe Mode: {cls.FAIL_SAFE_MODE}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("================================")
