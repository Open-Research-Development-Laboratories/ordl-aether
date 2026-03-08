"""
AETHER Image Analysis Module
NASA-Inspired Computer Vision System

Inspired by:
- NASA's TilePredictor (CNN-based classification)
- CNN Pose Estimation for Spacecraft
- OnSight (Mars terrain analysis)
"""
import asyncio
import io
import logging
import os
from typing import Any, Dict, List

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel, pipeline

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
        self.embedder_processor = None
        self._models_loaded = False
        self._loading_error = None
        self._loaded_components = set()
        self._load_lock = asyncio.Lock()

    async def initialize(self):
        """Initialize module and keep model loading lazy."""
        logger.info("Initializing Image Analysis Module...")
        self.initialized = True
        logger.info("Image Analysis Module ready")

    async def warmup(self):
        """Background warmup hook used by core startup."""
        try:
            await self._ensure_models_loaded("classification")
        except Exception as exc:
            logger.warning("Image model warmup failed: %s", exc)

    async def get_status(self) -> Dict:
        status = await super().get_status()
        status["models_loaded"] = self._models_loaded
        status["loaded_components"] = sorted(self._loaded_components)
        status["loading_error"] = self._loading_error
        return status

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
        analysis_type = context.get("type", "classification")

        try:
            image = self._prepare_image(self._load_image(image_data))

            results = {
                "success": True,
                "image_size": image.size,
                "analysis_type": analysis_type,
                "component_errors": {},
            }

            if analysis_type in {"full", "classification"}:
                try:
                    await self._ensure_models_loaded("classification")
                    results["classifications"] = await asyncio.to_thread(self._classify_sync, image)
                except Exception as exc:
                    results["component_errors"]["classification"] = str(exc)

            if analysis_type in {"full", "detection"}:
                try:
                    await self._ensure_models_loaded("detection")
                    results["detections"] = await asyncio.to_thread(self._detect_objects_sync, image)
                except Exception as exc:
                    results["component_errors"]["detection"] = str(exc)

            if analysis_type in {"full", "embedding"}:
                try:
                    await self._ensure_models_loaded("embedding")
                    results["embedding"] = await asyncio.to_thread(self._generate_embedding_sync, image)
                except Exception as exc:
                    results["component_errors"]["embedding"] = str(exc)

            if not any(key in results for key in ("classifications", "detections", "embedding")):
                errors = results["component_errors"]
                joined = "; ".join(f"{name}: {message}" for name, message in errors.items())
                raise RuntimeError(joined or "No image analysis components completed successfully")

            if not results["component_errors"]:
                results.pop("component_errors")

            await self.emit_event(
                "image.analyzed",
                {
                    "classifications": results.get("classifications", []),
                    "detection_count": len(results.get("detections", [])),
                    "has_embedding": "embedding" in results,
                },
            )

            self._update_stats(success=True)
            return results

        except Exception as exc:
            logger.error("Image analysis error: %s", exc)
            self._update_stats(success=False)
            return {"success": False, "error": str(exc)}

    async def _ensure_models_loaded(self, analysis_type: str):
        """Single-flight model loader that only pulls required components."""
        required = self._required_components_for_analysis(analysis_type)
        if required.issubset(self._loaded_components):
            return

        async with self._load_lock:
            missing = required - self._loaded_components
            if not missing:
                return

            logger.info("Loading image model components on demand: %s", sorted(missing))
            self._loading_error = None
            try:
                await asyncio.to_thread(self._build_required_pipelines_sync, missing)
                self._loaded_components.update(missing)
                self._models_loaded = self._loaded_components == {
                    "classifier",
                    "object_detector",
                    "embedder",
                }
            except Exception as exc:
                self._loading_error = str(exc)
                raise

    @staticmethod
    def _required_components_for_analysis(analysis_type: str) -> set:
        if analysis_type == "full":
            return {"classifier", "object_detector", "embedder"}
        if analysis_type == "detection":
            return {"object_detector"}
        if analysis_type == "embedding":
            return {"embedder"}
        return {"classifier"}

    def _build_required_pipelines_sync(self, missing: set):
        os.environ.setdefault("HF_HOME", settings.MODEL_CACHE_DIR)
        device = 0 if torch.cuda.is_available() else -1
        if "classifier" in missing and self.classifier is None:
            self.classifier = pipeline(
                "image-classification",
                model=settings.DEFAULT_IMAGE_MODEL,
                device=device,
            )
        if "object_detector" in missing and self.object_detector is None:
            self.object_detector = pipeline(
                "object-detection",
                model="facebook/detr-resnet-50",
                device=device,
            )
        if "embedder" in missing and self.embedder is None:
            embedder_model_name = "google/vit-base-patch16-224"
            self.embedder_processor = AutoImageProcessor.from_pretrained(embedder_model_name)
            self.embedder = AutoModel.from_pretrained(embedder_model_name)
            self.embedder.to("cuda:0" if device >= 0 else "cpu")
            self.embedder.eval()

    def _load_image(self, image_data: Any) -> Image.Image:
        """Load image from various formats."""
        if isinstance(image_data, Image.Image):
            return image_data
        if isinstance(image_data, bytes):
            return Image.open(io.BytesIO(image_data))
        if isinstance(image_data, str):
            return Image.open(image_data)
        raise ValueError(f"Unsupported image type: {type(image_data)}")

    def _prepare_image(self, image: Image.Image) -> Image.Image:
        """Normalize and cap image dimensions for faster inference."""
        normalized = image.convert("RGB")
        max_size = (1024, 1024)
        normalized.thumbnail(max_size, Image.Resampling.LANCZOS)
        return normalized

    def _classify_sync(self, image: Image.Image) -> List[Dict]:
        """Classify image content."""
        results = self.classifier(image)
        return [
            {
                "label": item["label"],
                "confidence": round(float(item["score"]), 4),
                "category": self._categorize_label(item["label"]),
            }
            for item in results[:5]
        ]

    def _detect_objects_sync(self, image: Image.Image) -> List[Dict]:
        """Detect objects in image."""
        results = self.object_detector(image)
        return [
            {
                "label": item["label"],
                "confidence": round(float(item["score"]), 4),
                "bbox": item["box"],
            }
            for item in results
            if float(item["score"]) > 0.5
        ]

    def _generate_embedding_sync(self, image: Image.Image) -> List[float]:
        """Generate image embedding for similarity search."""
        inputs = self.embedder_processor(images=image, return_tensors="pt")
        device = next(self.embedder.parameters()).device
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.embedder(**inputs)

        pooled = getattr(outputs, "pooler_output", None)
        if pooled is None:
            pooled = outputs.last_hidden_state.mean(dim=1)

        return pooled[0][:384].detach().cpu().tolist()

    def _categorize_label(self, label: str) -> str:
        """Categorize label into broad categories."""
        label_lower = label.lower()
        categories = {
            "nature": ["tree", "mountain", "lake", "forest", "ocean", "sky"],
            "technology": ["computer", "phone", "car", "aircraft", "satellite"],
            "space": ["planet", "star", "galaxy", "nebula", "astronaut"],
            "structure": ["building", "bridge", "road", "house"],
        }

        for category, keywords in categories.items():
            if any(keyword in label_lower for keyword in keywords):
                return category
        return "other"

    async def shutdown(self):
        """Cleanup."""
        logger.info("Shutting down Image Analysis Module")
        self.classifier = None
        self.object_detector = None
        self.embedder = None
        self.embedder_processor = None
        self._models_loaded = False
        self._loading_error = None
        self._loaded_components = set()
        self.initialized = False
