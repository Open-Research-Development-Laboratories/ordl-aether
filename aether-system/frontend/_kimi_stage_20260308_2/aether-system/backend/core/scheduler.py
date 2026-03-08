"""
AETHER Task Scheduler
Background job scheduling for data ingestion and processing
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List

import schedule

logger = logging.getLogger(__name__)


class Scheduler:
    """Background task scheduler"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
        self.stats = {
            "jobs_executed": 0,
            "errors": 0
        }
    
    async def start(self):
        """Start scheduler loop"""
        self.running = True
        asyncio.create_task(self._run_loop())
        logger.info("⏰ Scheduler started")
    
    async def stop(self):
        """Stop scheduler"""
        self.running = False
        schedule.clear()
        logger.info("⏰ Scheduler stopped")
    
    async def _run_loop(self):
        """Main scheduler loop"""
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(1)
    
    def add_job(
        self,
        func: Callable,
        interval: str,
        args: tuple = None,
        kwargs: dict = None
    ):
        """Add scheduled job"""
        if interval == "1min":
            schedule.every(1).minutes.do(func, *args or (), **kwargs or {})
        elif interval == "5min":
            schedule.every(5).minutes.do(func, *args or (), **kwargs or {})
        elif interval == "1hour":
            schedule.every(1).hours.do(func, *args or (), **kwargs or {})
        elif interval == "1day":
            schedule.every(1).days.do(func, *args or (), **kwargs or {})
        
        logger.info(f"📅 Scheduled job: {func.__name__} ({interval})")
    
    def get_stats(self) -> Dict:
        return {
            **self.stats,
            "running": self.running,
            "scheduled_jobs": len(schedule.jobs)
        }