"""
AETHER Knowledge Base - Hybrid SQL + Vector Database
NASA-Inspired Knowledge Management

Inspired by:
- NASA's CMR (metadata management)
- NETMARK (document intelligence)
- NEXUS (spatial data platform)
"""
import logging
from datetime import datetime
from typing import Dict, List

import chromadb
from chromadb.config import Settings as ChromaSettings
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text, create_engine, func
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
            item = KnowledgeItem(
                item_type=item_type,
                title=title or f"{item_type}_{datetime.utcnow().timestamp()}",
                content=content,
                source=source,
                metadata_json=metadata or {},
                confidence=confidence,
            )
            session.add(item)
            session.commit()

            if embedding:
                embedding_id = f"item_{item.id}"
                self.vector_collection.add(
                    ids=[embedding_id],
                    embeddings=[embedding],
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
                        results.append(
                            {
                                "id": item.id,
                                "type": item.item_type,
                                "title": item.title,
                                "content": item.content[:500],
                                "source": item.source,
                                "confidence": item.confidence,
                                "similarity": 1 - distance,
                                "created_at": item.created_at.isoformat(),
                            }
                        )
                finally:
                    session.close()

        elif query:
            session = self.Session()
            try:
                stmt = session.query(KnowledgeItem)

                if item_type:
                    stmt = stmt.filter(KnowledgeItem.item_type == item_type)
                if source:
                    stmt = stmt.filter(KnowledgeItem.source == source)

                stmt = stmt.filter(
                    KnowledgeItem.content.ilike(f"%{query}%")
                    | KnowledgeItem.title.ilike(f"%{query}%")
                )
                stmt = stmt.order_by(KnowledgeItem.confidence.desc()).limit(limit)

                for item in stmt.all():
                    results.append(
                        {
                            "id": item.id,
                            "type": item.item_type,
                            "title": item.title,
                            "content": item.content[:500],
                            "source": item.source,
                            "confidence": item.confidence,
                            "created_at": item.created_at.isoformat(),
                        }
                    )
            finally:
                session.close()

        return results

    async def get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        session = self.Session()
        try:
            total_items = session.query(KnowledgeItem).count()
            by_type_rows = (
                session.query(KnowledgeItem.item_type, func.count(KnowledgeItem.id))
                .group_by(KnowledgeItem.item_type)
                .all()
            )
            by_type = {item_type: count for item_type, count in by_type_rows}

            return {
                "total_items": total_items,
                "by_type": by_type,
                "vector_items": self.vector_collection.count() if self.vector_collection else 0,
            }
        finally:
            session.close()


knowledge_base = KnowledgeBase()


async def init_db():
    """Initialize database on startup."""
    await knowledge_base.initialize()
