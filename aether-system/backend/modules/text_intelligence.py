"""
AETHER Text Intelligence Module
NASA-Inspired NLP System

Inspired by:
- NASA's metadata processing systems
- pyQuARC (metadata quality analysis)
- Document intelligence (NETMARK)
"""
import asyncio
import logging
import os
from typing import Any, Dict, List

import torch
from transformers import pipeline

from core.base_module import BaseModule
from core.config import settings
from core.event_bus import EventBus

logger = logging.getLogger(__name__)


class TextIntelligenceModule(BaseModule):
    """
    Advanced text processing using transformer models
    Summarization, NER, sentiment, embeddings
    """

    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus, "text_intelligence")
        self.summarizer = None
        self.ner = None
        self.sentiment = None
        self.embedder = None
        self.classifier = None
        self._models_loaded = False
        self._loading_error = None
        self._loaded_components = set()
        self._load_lock = asyncio.Lock()

    async def initialize(self):
        """Initialize module and keep model loading lazy."""
        logger.info("Initializing Text Intelligence Module...")
        self.initialized = True
        logger.info("Text Intelligence Module ready")

    async def warmup(self):
        """Background warmup hook used by core startup."""
        try:
            await self._ensure_models_loaded(["sentiment", "ner"])
        except Exception as exc:
            logger.warning("Text model warmup failed: %s", exc)

    async def get_status(self) -> Dict:
        status = await super().get_status()
        status["models_loaded"] = self._models_loaded
        status["loaded_components"] = sorted(self._loaded_components)
        status["loading_error"] = self._loading_error
        return status

    async def process(
        self,
        text: str,
        context: Dict = None
    ) -> Dict:
        """
        Process text with multiple NLP tasks

        Args:
            text: Input text
            context: Processing options

        Returns:
            Comprehensive text analysis
        """
        context = context or {}
        tasks = context.get("tasks", ["sentiment", "ner", "keywords"])
        if isinstance(tasks, str):
            tasks = [tasks]

        try:
            if not text or len(text.strip()) == 0:
                return {"success": False, "error": "Empty text"}

            await self._ensure_models_loaded(tasks)

            results = {
                "success": True,
                "text_length": len(text),
                "word_count": len(text.split())
            }

            ner_raw = None
            needs_ner = "all" in tasks or "ner" in tasks or "keywords" in tasks

            if "all" in tasks or "summarize" in tasks:
                if len(text) > 100:
                    results["summary"] = await asyncio.to_thread(self._summarize_sync, text)

            if needs_ner:
                ner_raw = await asyncio.to_thread(self._run_ner_sync, text)

            if "all" in tasks or "ner" in tasks:
                results["entities"] = self._extract_entities_from_ner(ner_raw or [])

            if "all" in tasks or "sentiment" in tasks:
                results["sentiment"] = await asyncio.to_thread(self._analyze_sentiment_sync, text)

            if "all" in tasks or "classify" in tasks:
                labels = context.get("labels", ["technical", "scientific", "general"])
                results["classification"] = await asyncio.to_thread(
                    self._classify_sync,
                    text,
                    labels,
                )

            if "all" in tasks or "embedding" in tasks:
                results["embedding"] = await asyncio.to_thread(self._generate_embedding_sync, text)

            if "all" in tasks or "keywords" in tasks:
                results["keywords"] = self._extract_keywords_from_ner(ner_raw or [])

            await self.emit_event(
                "text.analyzed",
                {
                    "length": results["text_length"],
                    "entities_found": len(results.get("entities", [])),
                    "sentiment": results.get("sentiment", {}).get("label"),
                },
            )

            self._update_stats(success=True)
            return results

        except Exception as exc:
            logger.error("Text analysis error: %s", exc)
            self._update_stats(success=False)
            return {"success": False, "error": str(exc)}

    async def _ensure_models_loaded(self, tasks: List[str]):
        """Single-flight model loader that only pulls required components."""
        required = self._required_components(tasks)
        if not required:
            return
        if required.issubset(self._loaded_components):
            return

        async with self._load_lock:
            missing = required - self._loaded_components
            if not missing:
                return

            logger.info("Loading text model components on demand: %s", sorted(missing))
            self._loading_error = None
            try:
                await asyncio.to_thread(self._build_required_pipelines_sync, missing)
                self._loaded_components.update(missing)
                self._models_loaded = self._loaded_components == {
                    "summarizer",
                    "ner",
                    "sentiment",
                    "embedder",
                    "classifier",
                }
            except Exception as exc:
                self._loading_error = str(exc)
                raise

    @staticmethod
    def _required_components(tasks: List[str]) -> set:
        if "all" in tasks:
            return {"summarizer", "ner", "sentiment", "embedder", "classifier"}

        required = set()
        if "summarize" in tasks:
            required.add("summarizer")
        if "ner" in tasks or "keywords" in tasks:
            required.add("ner")
        if "sentiment" in tasks:
            required.add("sentiment")
        if "classify" in tasks:
            required.add("classifier")
        if "embedding" in tasks:
            required.add("embedder")
        return required

    def _build_required_pipelines_sync(self, missing: set):
        os.environ.setdefault("HF_HOME", settings.MODEL_CACHE_DIR)
        device = 0 if torch.cuda.is_available() else -1

        if "summarizer" in missing and self.summarizer is None:
            self.summarizer = pipeline(
                "summarization",
                model=settings.DEFAULT_TEXT_MODEL,
                device=device,
            )
        if "ner" in missing and self.ner is None:
            self.ner = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple",
                device=device,
            )
        if "sentiment" in missing and self.sentiment is None:
            self.sentiment = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=device,
            )
        if "embedder" in missing and self.embedder is None:
            self.embedder = pipeline(
                "feature-extraction",
                model=settings.DEFAULT_EMBEDDING_MODEL,
                device=device,
            )
        if "classifier" in missing and self.classifier is None:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=device,
            )

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars]

    def _summarize_sync(self, text: str) -> Dict:
        """Generate summary."""
        limited = self._truncate(text, 4000)
        max_length = min(150, max(40, len(limited) // 4))
        min_length = min(30, max_length // 2)

        result = self.summarizer(
            limited,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
        )

        summary_text = result[0]["summary_text"]
        return {
            "text": summary_text,
            "original_length": len(text),
            "summary_length": len(summary_text),
            "compression_ratio": len(summary_text) / max(len(text), 1),
        }

    def _run_ner_sync(self, text: str) -> List[Dict]:
        return self.ner(self._truncate(text, 2000))

    def _extract_entities_from_ner(self, entities: List[Dict]) -> List[Dict]:
        grouped = {}
        for entity in entities:
            entity_type = entity["entity_group"]
            grouped.setdefault(entity_type, []).append(
                {
                    "text": entity["word"],
                    "confidence": round(entity["score"], 4),
                    "start": entity["start"],
                    "end": entity["end"],
                }
            )
        return [{"type": key, "instances": value} for key, value in grouped.items()]

    def _analyze_sentiment_sync(self, text: str) -> Dict:
        """Analyze sentiment."""
        result = self.sentiment(self._truncate(text, 512))[0]
        score = round(result["score"], 4)
        return {
            "label": result["label"],
            "confidence": score,
            "sentiment_score": score if result["label"] == "POSITIVE" else -score,
        }

    def _classify_sync(self, text: str, labels: List[str]) -> Dict:
        """Zero-shot classification."""
        result = self.classifier(self._truncate(text, 512), labels)
        return {
            "labels": result["labels"],
            "scores": [round(score, 4) for score in result["scores"]],
            "top_label": result["labels"][0],
            "top_confidence": round(result["scores"][0], 4),
        }

    def _generate_embedding_sync(self, text: str) -> List[float]:
        """Generate text embedding."""
        features = self.embedder(self._truncate(text, 512))
        tensor = torch.tensor(features[0], dtype=torch.float32)
        if tensor.dim() == 1:
            pooled = tensor
        else:
            pooled = tensor.mean(dim=0)
        return pooled[:384].tolist()

    def _extract_keywords_from_ner(self, entities: List[Dict]) -> List[str]:
        """Extract keywords from NER output."""
        keywords = list(
            {
                entity["word"].lower()
                for entity in entities
                if len(entity["word"]) > 3
            }
        )
        return keywords[:10]

    async def shutdown(self):
        """Cleanup."""
        logger.info("Shutting down Text Intelligence Module")
        self.summarizer = None
        self.ner = None
        self.sentiment = None
        self.embedder = None
        self.classifier = None
        self._models_loaded = False
        self._loading_error = None
        self._loaded_components = set()
        self.initialized = False
