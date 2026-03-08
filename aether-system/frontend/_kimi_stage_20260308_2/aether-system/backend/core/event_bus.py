"""
AETHER Event Bus - Inter-module communication system
Inspired by NASA's distributed event processing (NFER)
"""
import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class Event:
    """Event object - represents system events like NASA's telemetry"""
    def __init__(
        self,
        event_type: str,
        source: str,
        payload: Any,
        priority: int = 5,
        metadata: Optional[Dict] = None
    ):
        self.event_type = event_type
        self.source = source
        self.payload = payload
        self.priority = priority
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        self.id = f"{source}_{self.timestamp.timestamp()}"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.event_type,
            "source": self.source,
            "payload": self.payload,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class EventBus:
    """
    Central event bus - enables decoupled module communication
    Like NASA's integrated ground data systems
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.stats = {
            "events_published": 0,
            "events_processed": 0,
            "errors": 0
        }
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to event type"""
        self.subscribers[event_type].append(callback)
        logger.debug(f"📡 Subscription added: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from event type"""
        if callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
    
    async def publish(self, event: Event):
        """Publish event to all subscribers"""
        self.stats["events_published"] += 1
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify subscribers
        callbacks = self.subscribers.get(event.event_type, [])
        
        if callbacks:
            logger.debug(f"📨 Event published: {event.event_type} -> {len(callbacks)} subscribers")
            
            tasks = []
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        tasks.append(callback(event))
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"❌ Event handler error: {e}")
                    self.stats["errors"] += 1
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            self.stats["events_processed"] += len(callbacks)
    
    def get_stats(self) -> Dict:
        """Get event bus statistics"""
        return {
            **self.stats,
            "active_subscriptions": sum(len(subs) for subs in self.subscribers.values()),
            "event_types": list(self.subscribers.keys()),
            "history_size": len(self.event_history)
        }
    
    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get recent events"""
        events = self.event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [e.to_dict() for e in events[-limit:]]