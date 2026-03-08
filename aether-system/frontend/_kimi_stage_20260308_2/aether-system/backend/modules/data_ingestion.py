"""
AETHER Data Ingestion Module
NASA-Inspired Data Pipeline

Inspired by:
- NASA's CMR (Common Metadata Repository)
- NEXUS (Deep Data Platform)
- NASA's data harvesting systems
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import httpx
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.base_module import BaseModule
from core.config import settings
from core.event_bus import EventBus

logger = logging.getLogger(__name__)

Base = declarative_base()


class DataSource(Base):
    """SQLAlchemy model for data sources - inspired by NASA's CMR"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # api, file, stream
    url = Column(String(500))
    last_ingested = Column(DateTime)
    metadata_json = Column(Text)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class DataRecord(Base):
    """SQLAlchemy model for ingested data"""
    __tablename__ = "data_records"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer)
    record_type = Column(String(50))
    content_json = Column(Text)
    embedding_json = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class DataIngestionModule(BaseModule):
    """
    Multi-source data ingestion pipeline
    Fetches, processes, and stores data from various sources
    """
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus, "data_ingestion")
        self.engine = None
        self.Session = None
        self.http_client = None
        self.sources = {}
    
    async def initialize(self):
        """Initialize database and HTTP client"""
        logger.info("📥 Initializing Data Ingestion Module...")
        
        # Setup database
        self.engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Setup HTTP client
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Register default sources
        await self._register_default_sources()
        
        self.initialized = True
        logger.info("✅ Data Ingestion Module ready")
    
    async def _register_default_sources(self):
        """Register built-in data sources"""
        default_sources = [
            {
                "name": "NASA_APOD",
                "type": "api",
                "url": "https://api.nasa.gov/planetary/apod",
                "description": "NASA Astronomy Picture of the Day"
            },
            {
                "name": "OpenMeteo",
                "type": "api",
                "url": "https://api.open-meteo.com/v1/forecast",
                "description": "Weather data"
            }
        ]
        
        session = self.Session()
        try:
            for source in default_sources:
                existing = session.query(DataSource).filter_by(name=source["name"]).first()
                if not existing:
                    db_source = DataSource(
                        name=source["name"],
                        source_type=source["type"],
                        url=source["url"],
                        metadata_json=json.dumps(source)
                    )
                    session.add(db_source)
            
            session.commit()
        finally:
            session.close()
    
    async def process(
        self,
        source_name: str,
        context: Dict = None
    ) -> Dict:
        """
        Ingest data from a specific source
        
        Args:
            source_name: Name of registered source
            context: Ingestion parameters
        
        Returns:
            Ingestion results
        """
        context = context or {}
        
        try:
            if source_name == "NASA_APOD":
                return await self._fetch_nasa_apod(context)
            elif source_name == "weather":
                return await self._fetch_weather(context)
            elif source_name == "file":
                return await self._process_file(context)
            else:
                return {"success": False, "error": f"Unknown source: {source_name}"}
                
        except Exception as e:
            logger.error(f"❌ Data ingestion error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _fetch_nasa_apod(self, context: Dict) -> Dict:
        """Fetch NASA Astronomy Picture of the Day"""
        api_key = context.get("api_key", settings.NASA_API_KEY or "DEMO_KEY")
        
        url = f"{settings.NASA_API_KEY}/planetary/apod"
        params = {"api_key": api_key}
        
        if "date" in context:
            params["date"] = context["date"]
        
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Store in database
        session = self.Session()
        try:
            record = DataRecord(
                source_id=1,  # NASA_APOD source
                record_type="apod",
                content_json=json.dumps(data),
                timestamp=datetime.utcnow()
            )
            session.add(record)
            session.commit()
            
            # Update source last_ingested
            source = session.query(DataSource).filter_by(name="NASA_APOD").first()
            if source:
                source.last_ingested = datetime.utcnow()
                session.commit()
        finally:
            session.close()
        
        # Emit event
        await self.emit_event(
            "data.ingested",
            {
                "source": "NASA_APOD",
                "type": "apod",
                "title": data.get("title"),
                "media_type": data.get("media_type")
            }
        )
        
        return {
            "success": True,
            "source": "NASA_APOD",
            "data": data,
            "stored": True
        }
    
    async def _fetch_weather(self, context: Dict) -> Dict:
        """Fetch weather data from OpenMeteo"""
        lat = context.get("latitude", 40.7128)
        lon = context.get("longitude", -74.0060)
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "hourly": "temperature_2m,precipitation_probability"
        }
        
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame for analysis
        hourly = data.get("hourly", {})
        df = pd.DataFrame({
            "time": hourly.get("time", []),
            "temperature": hourly.get("temperature_2m", []),
            "precipitation_prob": hourly.get("precipitation_probability", [])
        })
        
        return {
            "success": True,
            "source": "OpenMeteo",
            "location": {"lat": lat, "lon": lon},
            "current": data.get("current", {}),
            "forecast_hours": len(df),
            "data_preview": df.head(5).to_dict()
        }
    
    async def _process_file(self, context: Dict) -> Dict:
        """Process uploaded file"""
        file_path = context.get("file_path")
        file_type = context.get("file_type", "auto")
        
        if not file_path:
            return {"success": False, "error": "No file path provided"}
        
        # Detect file type
        if file_type == "auto":
            if file_path.endswith(".csv"):
                file_type = "csv"
            elif file_path.endswith(".json"):
                file_type = "json"
            elif file_path.endswith((".png", ".jpg", ".jpeg")):
                file_type = "image"
            else:
                file_type = "text"
        
        # Process based on type
        if file_type == "csv":
            df = pd.read_csv(file_path)
            return {
                "success": True,
                "file_type": "csv",
                "rows": len(df),
                "columns": list(df.columns),
                "preview": df.head(5).to_dict()
            }
        
        elif file_type == "json":
            with open(file_path, 'r') as f:
                data = json.load(f)
            return {
                "success": True,
                "file_type": "json",
                "keys": list(data.keys()) if isinstance(data, dict) else "list",
                "size": len(str(data))
            }
        
        elif file_type == "image":
            from PIL import Image
            img = Image.open(file_path)
            return {
                "success": True,
                "file_type": "image",
                "size": img.size,
                "mode": img.mode
            }
        
        else:
            with open(file_path, 'r') as f:
                content = f.read()
            return {
                "success": True,
                "file_type": "text",
                "length": len(content),
                "preview": content[:500]
            }
    
    async def get_sources(self) -> List[Dict]:
        """Get all registered data sources"""
        session = self.Session()
        try:
            sources = session.query(DataSource).all()
            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.source_type,
                    "url": s.url,
                    "last_ingested": s.last_ingested.isoformat() if s.last_ingested else None,
                    "status": s.status
                }
                for s in sources
            ]
        finally:
            session.close()
    
    async def shutdown(self):
        """Cleanup"""
        logger.info("🛑 Shutting down Data Ingestion Module")
        if self.http_client:
            await self.http_client.aclose()
        self.initialized = False