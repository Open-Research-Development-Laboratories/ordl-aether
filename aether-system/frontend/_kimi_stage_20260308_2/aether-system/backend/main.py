"""
AETHER - Main Application Entry Point
NASA-Inspired Unified AI System

Architecture inspired by NASA's AMMOS Instrument Toolkit (AIT)
"""
import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router
from core.config import settings
from core.event_bus import EventBus
from core.scheduler import Scheduler
from knowledge.database import init_db
from modules.data_ingestion import DataIngestionModule
from modules.image_analysis import ImageAnalysisModule
from modules.anomaly_detection import AnomalyDetectionModule
from modules.text_intelligence import TextIntelligenceModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AetherCore:
    """
    Core orchestrator - inspired by NASA's integrated mission control systems
    Manages all modules, events, and data flow
    """
    def __init__(self):
        self.event_bus = EventBus()
        self.scheduler = Scheduler()
        self.modules = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize all system components"""
        if self.initialized:
            return
        
        logger.info("🚀 Initializing AETHER Core...")
        
        # Initialize database
        await init_db()
        
        # Initialize modules (like NASA's instrument toolkit)
        self.modules['data_ingestion'] = DataIngestionModule(self.event_bus)
        self.modules['image_analysis'] = ImageAnalysisModule(self.event_bus)
        self.modules['anomaly_detection'] = AnomalyDetectionModule(self.event_bus)
        self.modules['text_intelligence'] = TextIntelligenceModule(self.event_bus)
        
        # Start all modules
        for name, module in self.modules.items():
            logger.info(f"📦 Starting module: {name}")
            await module.initialize()
        
        # Start scheduler
        await self.scheduler.start()
        
        self.initialized = True
        logger.info("✅ AETHER Core initialized successfully")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down AETHER Core...")
        
        for name, module in self.modules.items():
            await module.shutdown()
        
        await self.scheduler.stop()
        self.initialized = False
        logger.info("✅ Shutdown complete")


# Global core instance
aether_core = AetherCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    await aether_core.initialize()
    yield
    await aether_core.shutdown()


# Create FastAPI app
app = FastAPI(
    title="AETHER API",
    description="Adaptive Earth & Technology Harmonization Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "system": "AETHER",
        "version": "1.0.0",
        "modules": list(aether_core.modules.keys())
    }

# System status
@app.get("/status")
async def system_status():
    """Get full system status - inspired by NASA's mission control dashboards"""
    module_status = {}
    for name, module in aether_core.modules.items():
        module_status[name] = await module.get_status()
    
    return {
        "core_initialized": aether_core.initialized,
        "modules": module_status,
        "event_bus": aether_core.event_bus.get_stats(),
        "scheduler": aether_core.scheduler.get_stats()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )