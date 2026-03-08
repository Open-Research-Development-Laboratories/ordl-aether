"""
AETHER Base Module - Abstract base for all AI modules
Inspired by NASA's modular instrument design
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from core.event_bus import EventBus

logger = logging.getLogger(__name__)


class BaseModule(ABC):
    """
    Abstract base class for all AETHER modules
    Ensures consistent interface across all components
    """
    
    def __init__(self, event_bus: EventBus, module_name: str):
        self.event_bus = event_bus
        self.module_name = module_name
        self.initialized = False
        self.stats = {
            "operations": 0,
            "errors": 0,
            "last_operation": None
        }
    
    @abstractmethod
    async def initialize(self):
        """Initialize module - load models, setup resources"""
        pass
    
    @abstractmethod
    async def process(self, data: Any, context: Dict = None) -> Dict:
        """Process input data and return results"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Cleanup resources"""
        pass
    
    async def get_status(self) -> Dict:
        """Get module status - for health monitoring"""
        return {
            "name": self.module_name,
            "initialized": self.initialized,
            "stats": self.stats
        }
    
    def _update_stats(self, success: bool = True):
        """Update operation statistics"""
        self.stats["operations"] += 1
        if not success:
            self.stats["errors"] += 1
        self.stats["last_operation"] = {"success": success}
    
    async def emit_event(self, event_type: str, payload: Any, priority: int = 5):
        """Emit event to the system"""
        from core.event_bus import Event
        event = Event(
            event_type=event_type,
            source=self.module_name,
            payload=payload,
            priority=priority
        )
        await self.event_bus.publish(event)