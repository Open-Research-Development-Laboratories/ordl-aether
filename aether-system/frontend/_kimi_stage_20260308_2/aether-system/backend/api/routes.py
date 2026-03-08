"""
AETHER API Routes
RESTful API for all system operations
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from knowledge.database import knowledge_base
from main import aether_core

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic models for request/response
class AnalyzeRequest(BaseModel):
    data_type: str  # image, text, time_series
    content: Optional[str] = None
    context: Optional[Dict] = {}


class IngestRequest(BaseModel):
    source: str
    context: Optional[Dict] = {}


class SearchRequest(BaseModel):
    query: Optional[str] = None
    item_type: Optional[str] = None
    source: Optional[str] = None
    limit: int = 10


# Image Analysis Endpoints
@router.post("/analyze/image")
async def analyze_image(
    file: UploadFile = File(...),
    analysis_type: str = Form("full")
):
    """
    Analyze uploaded image
    Returns classifications, object detections, and embeddings
    """
    try:
        content = await file.read()
        
        module = aether_core.modules.get("image_analysis")
        if not module:
            raise HTTPException(status_code=503, detail="Image analysis module not available")
        
        result = await module.process(
            content,
            context={"type": analysis_type}
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        # Store in knowledge base
        await knowledge_base.store(
            item_type="image_analysis",
            content=f"Image analysis: {result.get('classifications', [])}",
            title=f"Analysis of {file.filename}",
            source="upload",
            metadata={
                "filename": file.filename,
                "size": len(content),
                "analysis": result
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Image analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/text")
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text content
    Summarization, NER, sentiment, classification
    """
    try:
        module = aether_core.modules.get("text_intelligence")
        if not module:
            raise HTTPException(status_code=503, detail="Text intelligence module not available")
        
        result = await module.process(
            request.content,
            context=request.context
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        # Store in knowledge base
        await knowledge_base.store(
            item_type="text_analysis",
            content=request.content[:1000],
            title=f"Text analysis: {result.get('summary', {}).get('text', '')[:50]}...",
            source="api",
            metadata={
                "sentiment": result.get("sentiment"),
                "entities": result.get("entities")
            },
            embedding=result.get("embedding")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Text analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/anomalies")
async def detect_anomalies(request: AnalyzeRequest):
    """
    Detect anomalies in time-series data
    """
    try:
        module = aether_core.modules.get("anomaly_detection")
        if not module:
            raise HTTPException(status_code=503, detail="Anomaly detection module not available")
        
        # Parse comma-separated values
        data = [float(x.strip()) for x in request.content.split(",")]
        
        result = await module.process(
            data,
            context=request.context
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Anomaly detection endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Data Ingestion Endpoints
@router.post("/ingest/{source_name}")
async def ingest_data(source_name: str, request: IngestRequest):
    """
    Ingest data from external sources
    """
    try:
        module = aether_core.modules.get("data_ingestion")
        if not module:
            raise HTTPException(status_code=503, detail="Data ingestion module not available")
        
        result = await module.process(source_name, request.context)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Data ingestion endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingest/sources")
async def get_data_sources():
    """Get available data sources"""
    try:
        module = aether_core.modules.get("data_ingestion")
        if not module:
            raise HTTPException(status_code=503, detail="Data ingestion module not available")
        
        sources = await module.get_sources()
        return {"sources": sources}
        
    except Exception as e:
        logger.error(f"Get sources endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Knowledge Base Endpoints
@router.post("/knowledge/search")
async def search_knowledge(request: SearchRequest):
    """
    Search knowledge base
    """
    try:
        results = await knowledge_base.search(
            query=request.query,
            item_type=request.item_type,
            source=request.source,
            limit=request.limit
        )
        
        return {
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Knowledge search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats")
async def knowledge_stats():
    """Get knowledge base statistics"""
    try:
        stats = await knowledge_base.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Knowledge stats endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Events
@router.get("/events/recent")
async def get_recent_events(event_type: Optional[str] = None, limit: int = 50):
    """Get recent system events"""
    try:
        events = aether_core.event_bus.get_recent_events(event_type, limit)
        return {
            "events": events,
            "count": len(events)
        }
        
    except Exception as e:
        logger.error(f"Events endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Unified Analysis Endpoint
@router.post("/analyze")
async def unified_analysis(request: AnalyzeRequest):
    """
    Unified analysis endpoint - routes to appropriate module
    """
    try:
        if request.data_type == "image":
            raise HTTPException(status_code=400, detail="Use /analyze/image for image uploads")
        
        elif request.data_type == "text":
            return await analyze_text(request)
        
        elif request.data_type == "time_series":
            return await detect_anomalies(request)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown data type: {request.data_type}")
            
    except Exception as e:
        logger.error(f"Unified analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))