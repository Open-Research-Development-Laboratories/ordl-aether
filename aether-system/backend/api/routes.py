"""
AETHER API Routes
RESTful API for all system operations
"""
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from core.config import settings
from knowledge.database import knowledge_base

logger = logging.getLogger(__name__)
router = APIRouter()


def get_aether_core():
    from main import aether_core
    return aether_core


def _safe_filename_suffix(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix:
        return suffix

    if upload.content_type and "/" in upload.content_type:
        subtype = upload.content_type.split("/", 1)[1].split(";")[0].strip().lower()
        if subtype == "jpeg":
            return ".jpg"
        if subtype:
            return f".{subtype}"
    return ".bin"


async def _persist_uploaded_asset(upload: UploadFile, content: bytes) -> Optional[str]:
    suffix = _safe_filename_suffix(upload)
    stored_name = f"{uuid4().hex}{suffix}"
    destination = settings.UPLOAD_DIR / stored_name
    await asyncio.to_thread(destination.write_bytes, content)
    return f"/uploads/{stored_name}"


def _image_report_content(filename: str, result: Dict[str, Any]) -> str:
    classifications = result.get("classifications") or []
    detections = result.get("detections") or []
    lines = [
        "Image Analysis Report",
        "",
        f"Filename: {filename}",
        f"Image Size: {result.get('image_size')}",
        f"Analysis Type: {result.get('analysis_type', 'full')}",
        f"Embedding Available: {'yes' if result.get('embedding') else 'no'}",
        "",
        "Top Classifications",
    ]

    if classifications:
        for item in classifications[:5]:
            lines.append(
                f"- {item.get('label', 'unknown')} ({float(item.get('confidence', 0.0)) * 100:.1f}%, {item.get('category', 'other')})"
            )
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Detections")
    if detections:
        for item in detections[:10]:
            lines.append(f"- {item.get('label', 'unknown')} ({float(item.get('confidence', 0.0)) * 100:.1f}%)")
    else:
        lines.append("- none")

    component_errors = result.get("component_errors") or {}
    if component_errors:
        lines.append("")
        lines.append("Component Errors")
        for name, message in component_errors.items():
            lines.append(f"- {name}: {message}")

    return "\n".join(lines)


def _text_record(title_text: str, input_text: str, result: Dict[str, Any]) -> Dict[str, Any]:
    summary_text = result.get("summary", {}).get("text")
    preview_title = summary_text or title_text or input_text[:80]
    preview_title = (preview_title or "Untitled text analysis").strip()
    if len(preview_title) > 60:
        preview_title = f"{preview_title[:57]}..."

    classification = result.get("classification") or {}
    entities = result.get("entities") or []
    keywords = result.get("keywords") or []
    sentiment = result.get("sentiment") or {}
    lines = [
        "Text Analysis Report",
        "",
        f"Characters: {result.get('text_length', len(input_text))}",
        f"Words: {result.get('word_count', len(input_text.split()))}",
    ]
    if summary_text:
        lines.extend(["", "Summary", summary_text])
    if sentiment:
        lines.extend(
            [
                "",
                "Sentiment",
                f"{sentiment.get('label', 'UNKNOWN')} ({float(sentiment.get('confidence', 0.0)) * 100:.1f}%)",
            ]
        )
    if classification.get("labels"):
        lines.extend(["", "Classification"])
        for label, score in zip(classification.get("labels", []), classification.get("scores", [])):
            lines.append(f"- {label}: {float(score) * 100:.1f}%")
    if keywords:
        lines.extend(["", "Keywords", ", ".join(keywords)])
    if entities:
        lines.append("")
        lines.append("Entities")
        for entity_group in entities:
            entity_text = ", ".join(
                instance.get("text", "") for instance in entity_group.get("instances", [])[:5]
            )
            lines.append(f"- {entity_group.get('type', 'unknown')}: {entity_text}")
    lines.extend(["", "Original Text", input_text])
    content = "\n".join(lines)
    metadata = {
        "input_text": input_text,
        "summary": result.get("summary"),
        "sentiment": sentiment,
        "entities": entities,
        "keywords": keywords,
        "classification": classification,
        "text_length": result.get("text_length"),
        "word_count": result.get("word_count"),
        "embedding_dimensions": len(result.get("embedding") or []),
        "models": {
            "summary": settings.DEFAULT_TEXT_MODEL,
            "ner": "dslim/bert-base-NER",
            "sentiment": "distilbert-base-uncased-finetuned-sst-2-english",
            "classification": "facebook/bart-large-mnli",
            "embedding": settings.DEFAULT_EMBEDDING_MODEL,
        },
    }
    return {
        "title": f"Text analysis: {preview_title}",
        "content": content,
        "metadata": metadata,
    }


def _anomaly_record(raw_input: str, result: Dict[str, Any]) -> Dict[str, Any]:
    anomaly_indices = [entry.get("index") for entry in result.get("anomalies", [])]
    severity = result.get("severity", "unknown")
    statistics = result.get("statistics") or {}
    metadata = {
        "input_series": raw_input,
        "data_points": result.get("data_points"),
        "anomaly_count": result.get("anomaly_count"),
        "anomaly_rate": statistics.get("anomaly_rate"),
        "severity": severity,
        "anomaly_indices": anomaly_indices,
        "anomalies": result.get("anomalies"),
        "statistics": statistics,
        "method": result.get("method"),
        "combined": result.get("combined"),
        "statistical": result.get("statistical"),
        "isolation_forest": result.get("isolation_forest"),
        "trend": result.get("trend"),
    }
    return {
        "title": f"Anomaly detection: {severity} severity",
        "content": "\n".join(
            [
                "Anomaly Detection Report",
                "",
                f"Data Points: {result.get('data_points', 0)}",
                f"Anomalies Found: {result.get('anomaly_count', 0)}",
                f"Anomaly Rate: {float(statistics.get('anomaly_rate', 0.0)) * 100:.2f}%",
                f"Severity: {severity}",
                f"Indices: {', '.join(str(index) for index in anomaly_indices) if anomaly_indices else 'none'}",
                "",
                f"Input Series: {raw_input}",
            ]
        ),
        "metadata": metadata,
    }


# Pydantic models for request/response
class AnalyzeRequest(BaseModel):
    data_type: str  # image, text, time_series
    content: Optional[str] = None
    context: Dict = Field(default_factory=dict)


class IngestRequest(BaseModel):
    source: str
    context: Dict = Field(default_factory=dict)


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
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size is {settings.MAX_FILE_SIZE_MB}MB",
            )

        aether_core = get_aether_core()
        module = aether_core.modules.get("image_analysis")
        if not module:
            raise HTTPException(status_code=503, detail="Image analysis module not available")
        
        result = await asyncio.wait_for(
            module.process(content, context={"type": analysis_type}),
            timeout=settings.ANALYSIS_TIMEOUT_SECONDS,
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        asset_url = None
        try:
            asset_url = await _persist_uploaded_asset(file, content)
        except Exception as exc:
            logger.warning("Unable to persist uploaded asset for knowledge base: %s", exc)

        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(content),
            "asset_url": asset_url,
            "image_size": result.get("image_size"),
            "analysis_type": result.get("analysis_type"),
            "classifications": result.get("classifications"),
            "detections": result.get("detections"),
            "has_embedding": bool(result.get("embedding")),
            "component_errors": result.get("component_errors", {}),
            "models": {
                "classification": settings.DEFAULT_IMAGE_MODEL,
                "detection": "facebook/detr-resnet-50",
                "embedding": "google/vit-base-patch16-224",
            },
        }

        await knowledge_base.store(
            item_type="image_analysis",
            content=_image_report_content(file.filename or "uploaded image", result),
            title=f"Analysis of {file.filename}",
            source="upload",
            metadata=metadata,
            embedding=result.get("embedding"),
        )

        return knowledge_base._json_safe(result)
        
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Image analysis timed out")
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
        text_content = (request.content or "").strip()
        if not text_content:
            raise HTTPException(status_code=400, detail="Text content is required")

        aether_core = get_aether_core()
        module = aether_core.modules.get("text_intelligence")
        if not module:
            raise HTTPException(status_code=503, detail="Text intelligence module not available")
        
        result = await asyncio.wait_for(
            module.process(text_content, context=request.context),
            timeout=settings.ANALYSIS_TIMEOUT_SECONDS,
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        record = _text_record(request.context.get("title") if request.context else None, text_content, result)
        await knowledge_base.store(
            item_type="text_analysis",
            content=record["content"],
            title=record["title"],
            source="api",
            metadata=record["metadata"],
            embedding=result.get("embedding")
        )

        return knowledge_base._json_safe(result)
        
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Text analysis timed out")
    except Exception as e:
        logger.error(f"Text analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/anomalies")
async def detect_anomalies(request: AnalyzeRequest):
    """
    Detect anomalies in time-series data
    """
    try:
        raw = (request.content or "").strip()
        if not raw:
            raise HTTPException(status_code=400, detail="Time-series content is required")

        aether_core = get_aether_core()
        module = aether_core.modules.get("anomaly_detection")
        if not module:
            raise HTTPException(status_code=503, detail="Anomaly detection module not available")
        
        try:
            data = [float(value.strip()) for value in raw.split(",") if value.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid numeric format in time-series input")
        if len(data) < 3:
            raise HTTPException(status_code=400, detail="Provide at least 3 numeric values")
        if len(data) > 50000:
            raise HTTPException(status_code=413, detail="Too many values. Max is 50000")
        
        result = await asyncio.wait_for(
            module.process(data, context=request.context),
            timeout=settings.ANALYSIS_TIMEOUT_SECONDS,
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        record = _anomaly_record(raw, result)
        await knowledge_base.store(
            item_type="anomaly_detection",
            content=record["content"],
            title=record["title"],
            source="api",
            metadata=record["metadata"],
        )

        return knowledge_base._json_safe(result)
        
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Anomaly detection timed out")
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
        aether_core = get_aether_core()
        module = aether_core.modules.get("data_ingestion")
        if not module:
            raise HTTPException(status_code=503, detail="Data ingestion module not available")
        
        result = await module.process(source_name, request.context)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return knowledge_base._json_safe(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data ingestion endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingest/sources")
async def get_data_sources():
    """Get available data sources"""
    try:
        aether_core = get_aether_core()
        module = aether_core.modules.get("data_ingestion")
        if not module:
            raise HTTPException(status_code=503, detail="Data ingestion module not available")
        
        sources = await module.get_sources()
        return {"sources": sources}
        
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats")
async def knowledge_stats():
    """Get knowledge base statistics"""
    try:
        stats = await knowledge_base.get_stats()
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge stats endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Events
@router.get("/events/recent")
async def get_recent_events(event_type: Optional[str] = None, limit: int = 50):
    """Get recent system events"""
    try:
        aether_core = get_aether_core()
        events = aether_core.event_bus.get_recent_events(event_type, limit)
        return {
            "events": events,
            "count": len(events)
        }
        
    except HTTPException:
        raise
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
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unified analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
