"""
HomeKit Integration Module
Handles communication with HomeKit accessories and switches
"""

import asyncio
import logging
import requests
from typing import Optional
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SWITCH
from src.config import Config

logger = logging.getLogger(__name__)

class HomeKitSwitch(Accessory):
    """HomeKit switch accessory for controlling the doggy door lock"""
    
    category = CATEGORY_SWITCH
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add switch service
        switch_service = self.add_preload_service('Switch')
        self.switch_on_char = switch_service.configure_char('On', setter_callback=self.set_switch)
        
        self.is_locked = True  # Door starts locked
        self.switch_on_char.set_value(self.is_locked)
        
        logger.info("HomeKit switch accessory initialized")
    
    def set_switch(self, value):
        """Callback when switch is toggled via HomeKit"""
        self.is_locked = value
        logger.info(f"HomeKit switch toggled: {'LOCKED' if value else 'UNLOCKED'}")
    
    async def set_lock_state(self, locked: bool):
        """Programmatically set the lock state"""
        if self.is_locked != locked:
            self.is_locked = locked
            self.switch_on_char.set_value(locked)
            logger.info(f"Lock state changed: {'LOCKED' if locked else 'UNLOCKED'}")

class HomeKitController:
    """Controls HomeKit switches for the doggy door system"""
    
    def __init__(self):
        self.driver: Optional[AccessoryDriver] = None
        self.switch: Optional[HomeKitSwitch] = None
        self.use_api = bool(Config.HOMEKIT_API_URL)
        
        if self.use_api:
            logger.info("Using HomeKit API mode")
        else:
            logger.info("Using HomeKit HAP bridge mode")
    
    async def initialize(self):
        """Initialize HomeKit controller"""
        if self.use_api:
            await self._initialize_api_mode()
        else:
            await self._initialize_bridge_mode()
    
    async def _initialize_api_mode(self):
        """Initialize API-based HomeKit control"""
        if not Config.HOMEKIT_API_URL:
            raise ValueError("HOMEKIT_API_URL required for API mode")
        
        logger.info(f"Initializing HomeKit API connection to {Config.HOMEKIT_API_URL}")
        
        # Test API connection
        try:
            await self._api_test_connection()
            logger.info("HomeKit API connection successful")
        except Exception as e:
            logger.error(f"Failed to connect to HomeKit API: {e}")
            raise
    
    async def _initialize_bridge_mode(self):
        """Initialize HAP bridge mode"""
        logger.info("Initializing HomeKit HAP bridge")
        
        # Create accessory driver
        self.driver = AccessoryDriver(port=Config.HOMEKIT_PORT, persist_file='/app/data/accessory.state')
        
        # Create switch accessory
        self.switch = HomeKitSwitch(self.driver, Config.HOMEKIT_SWITCH_NAME)
        self.driver.add_accessory(accessory=self.switch)
        
        # Start the driver
        logger.info(f"Starting HomeKit bridge on port {Config.HOMEKIT_PORT}")
        logger.info(f"Setup code: {Config.HOMEKIT_BRIDGE_PIN}")
        
        # Start driver in background
        asyncio.create_task(self._run_driver())
        
        # Give it time to start
        await asyncio.sleep(2)
    
    async def _run_driver(self):
        """Run the HomeKit driver"""
        try:
            self.driver.start()
        except Exception as e:
            logger.error(f"HomeKit driver error: {e}")
    
    async def _api_test_connection(self):
        """Test API connection"""
        headers = {}
        if Config.HOMEKIT_API_TOKEN:
            headers['Authorization'] = f'Bearer {Config.HOMEKIT_API_TOKEN}'
        
        # This is a placeholder - you'll need to adapt for your specific HomeKit API
        response = requests.get(f"{Config.HOMEKIT_API_URL}/status", headers=headers, timeout=10)
        response.raise_for_status()
    
    async def set_door_locked(self, locked: bool):
        """
        Set the door lock state
        
        Args:
            locked: True to lock door, False to unlock
        """
        try:
            if self.use_api:
                await self._api_set_switch(locked)
            else:
                await self._bridge_set_switch(locked)
            
            logger.info(f"Door {'LOCKED' if locked else 'UNLOCKED'}")
            
        except Exception as e:
            logger.error(f"Failed to set door lock state: {e}")
            if Config.FAIL_SAFE_MODE:
                logger.warning("Fail-safe mode: Door will remain in safe state")
            raise
    
    async def _api_set_switch(self, locked: bool):
        """Set switch via API"""
        if not Config.HOMEKIT_SWITCH_ID:
            raise ValueError("HOMEKIT_SWITCH_ID required for API mode")
        
        headers = {}
        if Config.HOMEKIT_API_TOKEN:
            headers['Authorization'] = f'Bearer {Config.HOMEKIT_API_TOKEN}'
        
        # This is a placeholder - adapt for your specific HomeKit API
        data = {
            'characteristics': [{
                'aid': 1,
                'iid': int(Config.HOMEKIT_SWITCH_ID),
                'value': locked
            }]
        }
        
        response = requests.put(
            f"{Config.HOMEKIT_API_URL}/characteristics",
            json=data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
    
    async def _bridge_set_switch(self, locked: bool):
        """Set switch via HAP bridge"""
        if not self.switch:
            raise RuntimeError("HomeKit switch not initialized")
        
        await self.switch.set_lock_state(locked)
    
    async def get_door_state(self) -> bool:
        """
        Get current door lock state
        
        Returns:
            True if locked, False if unlocked
        """
        try:
            if self.use_api:
                return await self._api_get_switch()
            else:
                return await self._bridge_get_switch()
        except Exception as e:
            logger.error(f"Failed to get door state: {e}")
            if Config.FAIL_SAFE_MODE:
                return True  # Assume locked in fail-safe mode
            raise
    
    async def _api_get_switch(self) -> bool:
        """Get switch state via API"""
        if not Config.HOMEKIT_SWITCH_ID:
            raise ValueError("HOMEKIT_SWITCH_ID required for API mode")
        
        headers = {}
        if Config.HOMEKIT_API_TOKEN:
            headers['Authorization'] = f'Bearer {Config.HOMEKIT_API_TOKEN}'
        
        # This is a placeholder - adapt for your specific HomeKit API
        response = requests.get(
            f"{Config.HOMEKIT_API_URL}/characteristics",
            params={'id': f'1.{Config.HOMEKIT_SWITCH_ID}'},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        return data['characteristics'][0]['value']
    
    async def _bridge_get_switch(self) -> bool:
        """Get switch state via HAP bridge"""
        if not self.switch:
            raise RuntimeError("HomeKit switch not initialized")
        
        return self.switch.is_locked
    
    async def shutdown(self):
        """Shutdown HomeKit controller"""
        if self.driver:
            logger.info("Shutting down HomeKit bridge")
            self.driver.stop()
