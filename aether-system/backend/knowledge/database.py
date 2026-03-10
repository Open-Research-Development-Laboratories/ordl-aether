"""
AETHER Knowledge Base - Hybrid SQL + Vector Database
NASA-Inspired Knowledge Management

Inspired by:
- NASA's CMR (metadata management)
- NETMARK (document intelligence)
- NEXUS (spatial data platform)
"""
import logging
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings as ChromaSettings
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text, create_engine, func, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class KnowledgeItem(Base):
    """Structured knowledge storage."""

    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True)
    item_type = Column(String(50), nullable=False)
    title = Column(String(500))
    content = Column(Text)
    source = Column(String(255))
    metadata_json = Column(JSON)
    embedding_id = Column(String(255))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeBase:
    """
    Hybrid knowledge base combining SQL and vector storage.
    """

    def __init__(self):
        self.engine = None
        self.Session = None
        self.vector_client = None
        self.vector_collection = None

    @staticmethod
    def _json_safe(value: Any) -> Any:
        """Convert model outputs into JSON-safe native Python values."""
        if value is None or isinstance(value, (str, bool, int)):
            return value
        if isinstance(value, float):
            return value if math.isfinite(value) else None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, dict):
            return {str(key): KnowledgeBase._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [KnowledgeBase._json_safe(item) for item in value]
        if hasattr(value, "item") and callable(value.item):
            try:
                return KnowledgeBase._json_safe(value.item())
            except Exception:
                pass
        if hasattr(value, "tolist") and callable(value.tolist):
            try:
                return KnowledgeBase._json_safe(value.tolist())
            except Exception:
                pass
        return str(value)

    @classmethod
    def _normalize_embedding(cls, embedding: List[float] = None) -> List[float] | None:
        if not embedding:
            return None
        normalized = cls._json_safe(embedding)
        if not isinstance(normalized, list):
            return None

        output = []
        for value in normalized:
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            if math.isfinite(numeric):
                output.append(numeric)
        return output or None

    @classmethod
    def _serialize_item(cls, item: KnowledgeItem, similarity: float = None) -> Dict[str, Any]:
        data = {
            "id": item.id,
            "type": item.item_type,
            "title": item.title,
            "preview": (item.content or "")[:500],
            "content": item.content or "",
            "full_content": item.content or "",
            "source": item.source,
            "confidence": item.confidence,
            "metadata": cls._json_safe(item.metadata_json or {}),
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }
        if similarity is not None:
            data["similarity"] = similarity
        return data

    async def initialize(self):
        """Initialize both SQL and vector databases."""
        logger.info("Initializing Knowledge Base...")

        engine_kwargs = {}
        if settings.DATABASE_URL.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        self.engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

        self.vector_client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.vector_collection = self.vector_client.get_or_create_collection(
            name="aether_knowledge",
            metadata={"hnsw:space": "cosine"},
        )

        logger.info("Knowledge Base ready")

    async def store(
        self,
        item_type: str,
        content: str,
        title: str = None,
        source: str = None,
        metadata: Dict = None,
        embedding: List[float] = None,
        confidence: float = 1.0,
    ) -> int:
        """
        Store item in knowledge base.
        Returns item ID.
        """
        session = self.Session()
        try:
            safe_metadata = self._json_safe(metadata or {})
            safe_embedding = self._normalize_embedding(embedding)
            safe_confidence = self._json_safe(confidence)
            if isinstance(safe_confidence, (int, float)):
                safe_confidence = float(safe_confidence)
            else:
                safe_confidence = 1.0

            item = KnowledgeItem(
                item_type=item_type,
                title=title or f"{item_type}_{datetime.utcnow().timestamp()}",
                content=content,
                source=source,
                metadata_json=safe_metadata,
                confidence=safe_confidence,
            )
            session.add(item)
            session.commit()

            if safe_embedding:
                embedding_id = f"item_{item.id}"
                self.vector_collection.add(
                    ids=[embedding_id],
                    embeddings=[safe_embedding],
                    metadatas=[
                        {
                            "item_id": item.id,
                            "type": item_type,
                            "source": source,
                            "title": title,
                        }
                    ],
                    documents=[content[:1000]],
                )
                item.embedding_id = embedding_id
                session.commit()

            logger.debug("Stored knowledge item: %s", item.id)
            return item.id
        finally:
            session.close()

    async def search(
        self,
        query: str = None,
        query_embedding: List[float] = None,
        item_type: str = None,
        source: str = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Search knowledge base.
        Supports both text and semantic (embedding) search.
        """
        results = []

        if query_embedding:
            vector_results = self.vector_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"type": item_type} if item_type else None,
            )

            ids = vector_results.get("ids", [[]])[0]
            metadatas = vector_results.get("metadatas", [[]])[0]
            distances = vector_results.get("distances", [[]])[0]

            item_ids = [meta["item_id"] for meta in metadatas if meta and "item_id" in meta]
            if item_ids:
                session = self.Session()
                try:
                    rows = session.query(KnowledgeItem).filter(KnowledgeItem.id.in_(item_ids)).all()
                    rows_by_id = {row.id: row for row in rows}

                    for i, _ in enumerate(ids):
                        metadata = metadatas[i] if i < len(metadatas) else {}
                        item = rows_by_id.get(metadata.get("item_id"))
                        if not item:
                            continue
                        distance = distances[i] if i < len(distances) else 1.0
                        results.append(self._serialize_item(item, similarity=1 - distance))
                finally:
                    session.close()

        else:
            session = self.Session()
            try:
                stmt = session.query(KnowledgeItem)

                if item_type:
                    stmt = stmt.filter(KnowledgeItem.item_type == item_type)
                if source:
                    stmt = stmt.filter(KnowledgeItem.source == source)

                if query:
                    stmt = stmt.filter(
                        KnowledgeItem.content.ilike(f"%{query}%")
                        | KnowledgeItem.title.ilike(f"%{query}%")
                    )
                stmt = stmt.order_by(
                    KnowledgeItem.confidence.desc(),
                    KnowledgeItem.updated_at.desc(),
                    KnowledgeItem.id.desc(),
                ).limit(limit)

                for item in stmt.all():
                    results.append(self._serialize_item(item))
            finally:
                session.close()

        return results

    async def get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        try:
            # Use raw aggregate SQL first. In a partially-corrupted sqlite file this
            # is more resilient than the ORM count() path, which expands into a
            # subquery selecting every column and can touch damaged pages.
            with self.engine.connect() as conn:
                total_items = conn.execute(text("SELECT COUNT(*) FROM knowledge_items")).scalar() or 0
                by_type_rows = conn.execute(
                    text(
                        """
                        SELECT item_type, COUNT(id) AS item_count
                        FROM knowledge_items
                        GROUP BY item_type
                        """
                    )
                ).fetchall()
            by_type = {item_type: count for item_type, count in by_type_rows}
        except DatabaseError:
            logger.exception("Knowledge stats raw SQL failed")
            by_type = {}
            total_items = 0

        return {
            "total_items": total_items,
            "by_type": by_type,
            "vector_items": self.vector_collection.count() if self.vector_collection else 0,
        }

    async def get_item(self, item_id: int) -> Dict[str, Any] | None:
        """Fetch a single knowledge item by ID."""
        session = self.Session()
        try:
            item = session.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
            if not item:
                return None
            return self._serialize_item(item)
        finally:
            session.close()

    async def update_item(
        self,
        item_id: int,
        *,
        metadata: Dict[str, Any] | None = None,
        content: str | None = None,
        title: str | None = None,
    ) -> Dict[str, Any] | None:
        """Update an existing knowledge item and return its serialized form."""
        session = self.Session()
        try:
            item = session.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
            if not item:
                return None

            if metadata is not None:
                item.metadata_json = self._json_safe(metadata)
            if content is not None:
                item.content = content
            if title is not None:
                item.title = title

            item.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(item)
            return self._serialize_item(item)
        finally:
            session.close()


knowledge_base = KnowledgeBase()


async def init_db():
    """Initialize database on startup."""
    await knowledge_base.initialize()
