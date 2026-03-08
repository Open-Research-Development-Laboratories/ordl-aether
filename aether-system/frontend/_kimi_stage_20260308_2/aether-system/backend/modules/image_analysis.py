"""
AETHER Image Analysis Module
NASA-Inspired Computer Vision System

Inspired by:
- NASA's TilePredictor (CNN-based classification)
- CNN Pose Estimation for Spacecraft
- OnSight (Mars terrain analysis)
"""
import io
import logging
from typing import Any, Dict, List, Optional

import torch
from PIL import Image
from transformers import pipeline

from core.base_module import BaseModule
from core.config import settings
from core.event_bus import EventBus

logger = logging.getLogger(__name__)


class ImageAnalysisModule(BaseModule):
    """
    Multi-purpose image analysis using state-of-the-art models
    """
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus, "image_analysis")
        self.classifier = None
        self.object_detector = None
        self.embedder = None
    
    async def initialize(self):
        """Load AI models"""
        logger.info("🖼️ Initializing Image Analysis Module...")
        
        try:
            # Image classification (Vision Transformer)
            self.classifier = pipeline(
                "image-classification",
                model=settings.DEFAULT_IMAGE_MODEL,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Object detection
            self.object_detector = pipeline(
                "object-detection",
                model="facebook/detr-resnet-50",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Image embeddings for similarity search
            self.embedder = pipeline(
                "feature-extraction",
                model="google/vit-base-patch16-224",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.initialized = True
            logger.info("✅ Image Analysis Module ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize image models: {e}")
            raise
    
    async def process(
        self,
        image_data: Any,
        context: Dict = None
    ) -> Dict:
        """
        Process image and return comprehensive analysis
        
        Args:
            image_data: PIL Image, bytes, or file path
            context: Additional processing options
        
        Returns:
            Analysis results with classifications, detections, embeddings
        """
        context = context or {}
        analysis_type = context.get("type", "full")
        
        try:
            # Convert to PIL Image
            image = self._load_image(image_data)
            
            results = {
                "success": True,
                "image_size": image.size,
                "analysis_type": analysis_type
            }
            
            # Classification
            if analysis_type in ["full", "classification"]:
                classifications = await self._classify(image)
                results["classifications"] = classifications
            
            # Object detection
            if analysis_type in ["full", "detection"]:
                detections = await self._detect_objects(image)
                results["detections"] = detections
            
            # Generate embedding for similarity search
            if analysis_type in ["full", "embedding"]:
                embedding = await self._generate_embedding(image)
                results["embedding"] = embedding
            
            # Emit event for other modules
            await self.emit_event(
                "image.analyzed",
                {
                    "classifications": results.get("classifications", []),
                    "detection_count": len(results.get("detections", [])),
                    "has_embedding": "embedding" in results
                }
            )
            
            self._update_stats(success=True)
            return results
            
        except Exception as e:
            logger.error(f"❌ Image analysis error: {e}")
            self._update_stats(success=False)
            return {"success": False, "error": str(e)}
    
    def _load_image(self, image_data: Any) -> Image.Image:
        """Load image from various formats"""
        if isinstance(image_data, Image.Image):
            return image_data
        elif isinstance(image_data, bytes):
            return Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str):
            return Image.open(image_data)
        else:
            raise ValueError(f"Unsupported image type: {type(image_data)}")
    
    async def _classify(self, image: Image.Image) -> List[Dict]:
        """Classify image content"""
        results = self.classifier(image)
        return [
            {
                "label": r["label"],
                "confidence": round(r["score"], 4),
                "category": self._categorize_label(r["label"])
            }
            for r in results[:5]
        ]
    
    async def _detect_objects(self, image: Image.Image) -> List[Dict]:
        """Detect objects in image"""
        results = self.object_detector(image)
        return [
            {
                "label": r["label"],
                "confidence": round(r["score"], 4),
                "bbox": r["box"]
            }
            for r in results if r["score"] > 0.5
        ]
    
    async def _generate_embedding(self, image: Image.Image) -> List[float]:
        """Generate image embedding for similarity search"""
        features = self.embedder(image)
        # Flatten and convert to list
        embedding = features[0][0][0]
        return embedding[:256]  # Return first 256 dimensions
    
    def _categorize_label(self, label: str) -> str:
        """Categorize label into broad categories"""
        label_lower = label.lower()
        categories = {
            "nature": ["tree", "mountain", "lake", "forest", "ocean", "sky"],
            "technology": ["computer", "phone", "car", "aircraft", "satellite"],
            "space": ["planet", "star", "galaxy", "nebula", "astronaut"],
            "structure": ["building", "bridge", "road", "house"]
        }
        
        for category, keywords in categories.items():
            if any(kw in label_lower for kw in keywords):
                return category
        return "other"
    
    async def shutdown(self):
        """Cleanup"""
        logger.info("🛑 Shutting down Image Analysis Module")
        self.classifier = None
        self.object_detector = None
        self.embedder = None
        self.initialized = False