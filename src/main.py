"""
Main Doggy Door Application
Coordinates AirTag detection and HomeKit control
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from src.config import Config
from src.airtag_detector import AirTagDetector
from src.homekit_controller import HomeKitController

# Set up logging
def setup_logging():
    """Configure logging for the application"""
    log_dir = Path(Config.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)

class DoggyDoorApp:
    """Main application class for the doggy door system"""
    
    def __init__(self):
        self.airtag_detector = None
        self.homekit_controller = None
        self.is_running = False
        self.door_locked = True  # Start with door locked
        self.last_unlock_time = None
        self.auto_lock_task = None
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("🐕 Initializing Doggy Door System")
        
        # Validate configuration
        config_errors = Config.validate()
        if config_errors:
            logger.error("Configuration errors:")
            for error in config_errors:
                logger.error(f"  - {error}")
            raise ValueError("Invalid configuration")
        
        Config.print_config()
        
        # Initialize HomeKit controller
        logger.info("Initializing HomeKit controller...")
        self.homekit_controller = HomeKitController()
        await self.homekit_controller.initialize()
        
        # Ensure door starts locked
        await self.homekit_controller.set_door_locked(True)
        
        # Initialize AirTag detector
        logger.info("Initializing AirTag detector...")
        self.airtag_detector = AirTagDetector(
            airtag_identifier=Config.AIRTAG_IDENTIFIER,
            proximity_threshold_feet=Config.PROXIMITY_THRESHOLD_FEET,
            scan_interval=Config.SCAN_INTERVAL_SECONDS
        )
        
        # Set proximity callback
        self.airtag_detector.set_proximity_callback(self.on_proximity_change)
        
        logger.info("✅ Doggy Door System initialized successfully")
    
    async def on_proximity_change(self, is_close: bool, distance_feet: float):
        """
        Handle AirTag proximity changes
        
        Args:
            is_close: True if AirTag is within proximity threshold
            distance_feet: Current estimated distance in feet
        """
        logger.info(f"🎯 AirTag proximity: {'CLOSE' if is_close else 'FAR'} ({distance_feet:.1f}ft)")
        
        if is_close and self.door_locked:
            # AirTag is close and door is locked - unlock the door
            await self.unlock_door()
            
        elif not is_close and not self.door_locked:
            # AirTag is far and door is unlocked - lock the door
            await self.lock_door()
    
    async def unlock_door(self):
        """Unlock the doggy door"""
        try:
            logger.info("🔓 Unlocking doggy door")
            await self.homekit_controller.set_door_locked(False)
            self.door_locked = False
            self.last_unlock_time = datetime.now()
            
            # Start auto-lock timer
            if self.auto_lock_task:
                self.auto_lock_task.cancel()
            
            self.auto_lock_task = asyncio.create_task(self.auto_lock_timer())
            
        except Exception as e:
            logger.error(f"❌ Failed to unlock door: {e}")
            if Config.FAIL_SAFE_MODE:
                logger.warning("⚠️ Fail-safe mode: Door remains locked")
    
    async def lock_door(self):
        """Lock the doggy door"""
        try:
            logger.info("🔒 Locking doggy door")
            await self.homekit_controller.set_door_locked(True)
            self.door_locked = True
            
            # Cancel auto-lock timer if running
            if self.auto_lock_task:
                self.auto_lock_task.cancel()
                self.auto_lock_task = None
                
        except Exception as e:
            logger.error(f"❌ Failed to lock door: {e}")
    
    async def auto_lock_timer(self):
        """Auto-lock the door after timeout if still unlocked"""
        try:
            timeout_seconds = Config.AUTO_UNLOCK_TIMEOUT_MINUTES * 60
            logger.info(f"⏰ Auto-lock timer started ({Config.AUTO_UNLOCK_TIMEOUT_MINUTES} minutes)")
            
            await asyncio.sleep(timeout_seconds)
            
            if not self.door_locked:
                logger.warning("⏰ Auto-lock timeout reached - locking door")
                await self.lock_door()
                
        except asyncio.CancelledError:
            logger.debug("Auto-lock timer cancelled")
        except Exception as e:
            logger.error(f"Error in auto-lock timer: {e}")
    
    async def status_reporter(self):
        """Periodically report system status"""
        while self.is_running:
            try:
                # Get detector info
                detector_info = self.airtag_detector.get_last_detection_info()
                
                # Calculate uptime
                uptime = time.time() - self.start_time
                uptime_str = str(timedelta(seconds=int(uptime)))
                
                # Log status
                logger.info(f"📊 Status: Door={'🔒 LOCKED' if self.door_locked else '🔓 UNLOCKED'}, "
                           f"AirTag={'🎯 SCANNING' if detector_info['is_scanning'] else '❌ STOPPED'}, "
                           f"Uptime={uptime_str}")
                
                if detector_info['last_detection_time']:
                    last_seen = detector_info['seconds_since_last_detection']
                    logger.info(f"🔍 Last AirTag detection: {last_seen:.0f}s ago (RSSI: {detector_info['last_rssi']})")
                
                # Wait 5 minutes before next status report
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in status reporter: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def run(self):
        """Run the main application loop"""
        self.is_running = True
        self.start_time = time.time()
        
        logger.info("🚀 Starting Doggy Door System")
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Start AirTag monitoring and status reporting
            monitoring_task = asyncio.create_task(self.airtag_detector.start_monitoring())
            status_task = asyncio.create_task(self.status_reporter())
            
            # Wait for tasks to complete
            await asyncio.gather(monitoring_task, status_task)
            
        except asyncio.CancelledError:
            logger.info("Application cancelled")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shutdown the application"""
        if not self.is_running:
            return
            
        logger.info("🛑 Shutting down Doggy Door System")
        self.is_running = False
        
        # Stop AirTag monitoring
        if self.airtag_detector:
            self.airtag_detector.stop_monitoring()
        
        # Cancel auto-lock timer
        if self.auto_lock_task:
            self.auto_lock_task.cancel()
        
        # Lock the door as a safety measure
        if self.homekit_controller and not self.door_locked:
            logger.info("🔒 Locking door for safety during shutdown")
            try:
                await self.homekit_controller.set_door_locked(True)
            except Exception as e:
                logger.error(f"Failed to lock door during shutdown: {e}")
        
        # Shutdown HomeKit controller
        if self.homekit_controller:
            await self.homekit_controller.shutdown()
        
        logger.info("✅ Doggy Door System shut down complete")

async def main():
    """Main entry point"""
    setup_logging()
    
    try:
        app = DoggyDoorApp()
        await app.initialize()
        await app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
