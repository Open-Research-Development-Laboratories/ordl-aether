"""
AETHER Text Intelligence Module
NASA-Inspired NLP System

Inspired by:
- NASA's metadata processing systems
- pyQuARC (metadata quality analysis)
- Document intelligence (NETMARK)
"""
import logging
from typing import Any, Dict, List, Optional

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
    
    async def initialize(self):
        """Load NLP models"""
        logger.info("📝 Initializing Text Intelligence Module...")
        
        try:
            # Text summarization
            self.summarizer = pipeline(
                "summarization",
                model=settings.DEFAULT_TEXT_MODEL,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Named Entity Recognition
            self.ner = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Sentiment analysis
            self.sentiment = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Text embeddings for similarity
            self.embedder = pipeline(
                "feature-extraction",
                model=settings.DEFAULT_EMBEDDING_MODEL,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Zero-shot classification
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.initialized = True
            logger.info("✅ Text Intelligence Module ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize NLP models: {e}")
            raise
    
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
        tasks = context.get("tasks", ["all"])
        
        try:
            if not text or len(text.strip()) == 0:
                return {"success": False, "error": "Empty text"}
            
            results = {
                "success": True,
                "text_length": len(text),
                "word_count": len(text.split())
            }
            
            # Summarization
            if "all" in tasks or "summarize" in tasks:
                if len(text) > 100:
                    summary = await self._summarize(text)
                    results["summary"] = summary
            
            # Named Entity Recognition
            if "all" in tasks or "ner" in tasks:
                entities = await self._extract_entities(text)
                results["entities"] = entities
            
            # Sentiment Analysis
            if "all" in tasks or "sentiment" in tasks:
                sentiment = await self._analyze_sentiment(text)
                results["sentiment"] = sentiment
            
            # Text Classification
            if "all" in tasks or "classify" in tasks:
                labels = context.get("labels", ["technical", "scientific", "general"])
                classification = await self._classify(text, labels)
                results["classification"] = classification
            
            # Generate embedding
            if "all" in tasks or "embedding" in tasks:
                embedding = await self._generate_embedding(text)
                results["embedding"] = embedding
            
            # Extract keywords
            if "all" in tasks or "keywords" in tasks:
                keywords = await self._extract_keywords(text)
                results["keywords"] = keywords
            
            # Emit event
            await self.emit_event(
                "text.analyzed",
                {
                    "length": results["text_length"],
                    "entities_found": len(results.get("entities", [])),
                    "sentiment": results.get("sentiment", {}).get("label")
                }
            )
            
            self._update_stats(success=True)
            return results
            
        except Exception as e:
            logger.error(f"❌ Text analysis error: {e}")
            self._update_stats(success=False)
            return {"success": False, "error": str(e)}
    
    async def _summarize(self, text: str) -> Dict:
        """Generate summary"""
        max_length = min(150, len(text) // 4)
        min_length = min(30, max_length // 2)
        
        result = self.summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
        
        return {
            "text": result[0]["summary_text"],
            "original_length": len(text),
            "summary_length": len(result[0]["summary_text"]),
            "compression_ratio": len(result[0]["summary_text"]) / len(text)
        }
    
    async def _extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities"""
        entities = self.ner(text)
        
        # Group by entity type
        grouped = {}
        for entity in entities:
            entity_type = entity["entity_group"]
            if entity_type not in grouped:
                grouped[entity_type] = []
            grouped[entity_type].append({
                "text": entity["word"],
                "confidence": round(entity["score"], 4),
                "start": entity["start"],
                "end": entity["end"]
            })
        
        return [
            {"type": k, "instances": v}
            for k, v in grouped.items()
        ]
    
    async def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment"""
        result = self.sentiment(text[:512])[0]  # Truncate for model
        return {
            "label": result["label"],
            "confidence": round(result["score"], 4),
            "sentiment_score": result["score"] if result["label"] == "POSITIVE" else -result["score"]
        }
    
    async def _classify(self, text: str, labels: List[str]) -> Dict:
        """Zero-shot classification"""
        result = self.classifier(text[:512], labels)
        
        return {
            "labels": result["labels"],
            "scores": [round(s, 4) for s in result["scores"]],
            "top_label": result["labels"][0],
            "top_confidence": round(result["scores"][0], 4)
        }
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate text embedding"""
        features = self.embedder(text[:512])
        # Average pooling
        embedding = torch.tensor(features[0]).mean(dim=0).tolist()
        return embedding[:384]  # Return first 384 dimensions
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords using NER and frequency"""
        entities = self.ner(text)
        
        # Get unique entity texts
        keywords = list(set([e["word"].lower() for e in entities if len(e["word"]) > 3]))
        
        return keywords[:10]
    
    async def shutdown(self):
        """Cleanup"""
        logger.info("🛑 Shutting down Text Intelligence Module")
        self.summarizer = None
        self.ner = None
        self.sentiment = None
        self.embedder = None
        self.classifier = None
        self.initialized = False