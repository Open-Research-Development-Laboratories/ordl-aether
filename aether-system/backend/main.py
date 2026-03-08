"""
AETHER - Main Application Entry Point
NASA-Inspired Unified AI System

Architecture inspired by NASA's AMMOS Instrument Toolkit (AIT)
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from core.config import settings
from core.event_bus import EventBus
from core.scheduler import Scheduler
from knowledge.database import init_db
from modules.anomaly_detection import AnomalyDetectionModule
from modules.data_ingestion import DataIngestionModule
from modules.image_analysis import ImageAnalysisModule
from modules.text_intelligence import TextIntelligenceModule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def validate_runtime_config():
    """Fail fast on unsafe production config."""
    if settings.ENVIRONMENT.lower() != "production":
        return

    secret_lower = settings.SECRET_KEY.lower()
    if "your-secret-key" in secret_lower or len(settings.SECRET_KEY) < 32:
        raise RuntimeError(
            "Unsafe production SECRET_KEY. Set a strong, unique SECRET_KEY before starting."
        )

    if not settings.NASA_API_KEY or settings.NASA_API_KEY == "DEMO_KEY":
        logger.warning("NASA_API_KEY is not set for production; upstream quota limits may apply.")


class AetherCore:
    """
    Core orchestrator that manages modules, events, and data flow.
    """

    def __init__(self):
        self.event_bus = EventBus()
        self.scheduler = Scheduler()
        self.modules = {}
        self.initialized = False
        self.warmup_tasks: Dict[str, asyncio.Task] = {}

    async def initialize(self):
        """Initialize all system components."""
        if self.initialized:
            return

        logger.info("Initializing AETHER Core...")
        await init_db()

        self.modules["data_ingestion"] = DataIngestionModule(self.event_bus)
        self.modules["image_analysis"] = ImageAnalysisModule(self.event_bus)
        self.modules["anomaly_detection"] = AnomalyDetectionModule(self.event_bus)
        self.modules["text_intelligence"] = TextIntelligenceModule(self.event_bus)

        for name, module in self.modules.items():
            logger.info("Starting module: %s", name)
            await module.initialize()

        await self.scheduler.start()
        self.initialized = True

        if settings.PREWARM_MODELS:
            for name, module in self.modules.items():
                warmup = getattr(module, "warmup", None)
                if callable(warmup):
                    self.warmup_tasks[name] = asyncio.create_task(warmup(), name=f"warmup:{name}")
            if self.warmup_tasks:
                logger.info("Started background model warmup for: %s", ", ".join(self.warmup_tasks.keys()))

        logger.info("AETHER Core initialized successfully")

    def get_warmup_status(self) -> Dict[str, Dict]:
        status = {}
        for name, task in self.warmup_tasks.items():
            entry = {
                "running": not task.done(),
                "done": task.done(),
                "cancelled": task.cancelled(),
                "error": None,
            }
            if task.done() and not task.cancelled():
                exc = task.exception()
                if exc:
                    entry["error"] = str(exc)
            status[name] = entry
        return status

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down AETHER Core...")

        for task in self.warmup_tasks.values():
            if not task.done():
                task.cancel()
        if self.warmup_tasks:
            await asyncio.gather(*self.warmup_tasks.values(), return_exceptions=True)
        self.warmup_tasks.clear()

        for module in self.modules.values():
            await module.shutdown()

        await self.scheduler.stop()
        self.initialized = False
        logger.info("Shutdown complete")


aether_core = AetherCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_runtime_config()
    await aether_core.initialize()
    yield
    await aether_core.shutdown()


app = FastAPI(
    title="AETHER API",
    description="Adaptive Earth & Technology Harmonization Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    warmup = aether_core.get_warmup_status()
    failed = [name for name, item in warmup.items() if item["error"]]
    status = "healthy" if aether_core.initialized and not failed else "degraded"

    return {
        "status": status,
        "system": "AETHER",
        "version": "1.0.0",
        "core_initialized": aether_core.initialized,
        "modules": list(aether_core.modules.keys()),
        "warmup": warmup,
    }


@app.get("/ready")
async def readiness_check():
    warmup = aether_core.get_warmup_status()
    failed = [name for name, item in warmup.items() if item["error"]]
    ready = aether_core.initialized and not failed
    return {
        "ready": ready,
        "failed_warmups": failed,
    }


@app.get("/status")
async def system_status():
    """Get full system status for dashboards and monitoring."""
    module_status = {}
    for name, module in aether_core.modules.items():
        module_status[name] = await module.get_status()

    return {
        "core_initialized": aether_core.initialized,
        "modules": module_status,
        "event_bus": aether_core.event_bus.get_stats(),
        "scheduler": aether_core.scheduler.get_stats(),
        "warmup": aether_core.get_warmup_status(),
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
