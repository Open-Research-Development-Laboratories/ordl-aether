"""
AETHER Knowledge Base - Hybrid SQL + Vector Database
NASA-Inspired Knowledge Management

Inspired by:
- NASA's CMR (metadata management)
- NETMARK (document intelligence)
- NEXUS (spatial data platform)
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
import numpy as np
from chromadb.config import Settings as ChromaSettings
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class KnowledgeItem(Base):
    """Structured knowledge storage"""
    __tablename__ = "knowledge_items"
    
    id = Column(Integer, primary_key=True)
    item_type = Column(String(50), nullable=False)  # image, text, data, analysis
    title = Column(String(500))
    content = Column(Text)
    source = Column(String(255))
    metadata_json = Column(JSON)
    embedding_id = Column(String(255))  # Reference to vector DB
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeBase:
    """
    Hybrid knowledge base combining SQL and vector storage
    Like NASA's integrated metadata and document systems
    """
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.vector_client = None
        self.vector_collection = None
    
    async def initialize(self):
        """Initialize both SQL and vector databases"""
        logger.info("🧠 Initializing Knowledge Base...")
        
        # SQL Database
        self.engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Vector Database (ChromaDB)
        self.vector_client = chromadb.Client(
            ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=settings.VECTOR_DB_PATH
            )
        )
        
        # Get or create collection
        self.vector_collection = self.vector_client.get_or_create_collection(
            name="aether_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info("✅ Knowledge Base ready")
    
    async def store(
        self,
        item_type: str,
        content: str,
        title: str = None,
        source: str = None,
        metadata: Dict = None,
        embedding: List[float] = None,
        confidence: float = 1.0
    ) -> int:
        """
        Store item in knowledge base
        
        Returns:
            Item ID
        """
        session = self.Session()
        try:
            # Store in SQL
            item = KnowledgeItem(
                item_type=item_type,
                title=title or f"{item_type}_{datetime.utcnow().timestamp()}",
                content=content,
                source=source,
                metadata_json=metadata or {},
                confidence=confidence
            )
            session.add(item)
            session.commit()
            
            # Store embedding in vector DB if provided
            if embedding:
                embedding_id = f"item_{item.id}"
                self.vector_collection.add(
                    ids=[embedding_id],
                    embeddings=[embedding],
                    metadatas=[{
                        "item_id": item.id,
                        "type": item_type,
                        "source": source,
                        "title": title
                    }],
                    documents=[content[:1000]]  # Store truncated content
                )
                
                # Update SQL record with embedding reference
                item.embedding_id = embedding_id
                session.commit()
            
            logger.debug(f"💾 Stored knowledge item: {item.id}")
            return item.id
            
        finally:
            session.close()
    
    async def search(
        self,
        query: str = None,
        query_embedding: List[float] = None,
        item_type: str = None,
        source: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search knowledge base
        Supports both text and semantic (embedding) search
        """
        results = []
        
        # Semantic search with vector DB
        if query_embedding:
            vector_results = self.vector_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"type": item_type} if item_type else None
            )
            
            for i, item_id in enumerate(vector_results["ids"][0]):
                metadata = vector_results["metadatas"][0][i]
                distance = vector_results["distances"][0][i]
                
                # Get full record from SQL
                session = self.Session()
                try:
                    item = session.query(KnowledgeItem).get(metadata["item_id"])
                    if item:
                        results.append({
                            "id": item.id,
                            "type": item.item_type,
                            "title": item.title,
                            "content": item.content[:500],
                            "source": item.source,
                            "confidence": item.confidence,
                            "similarity": 1 - distance,
                            "created_at": item.created_at.isoformat()
                        })
                finally:
                    session.close()
        
        # Text search with SQL
        elif query:
            session = self.Session()
            try:
                q = session.query(KnowledgeItem)
                
                if item_type:
                    q = q.filter(KnowledgeItem.item_type == item_type)
                if source:
                    q = q.filter(KnowledgeItem.source == source)
                
                # Simple text search
                q = q.filter(
                    KnowledgeItem.content.ilike(f"%{query}%") |
                    KnowledgeItem.title.ilike(f"%{query}%")
                )
                
                q = q.order_by(KnowledgeItem.confidence.desc())
                q = q.limit(limit)
                
                for item in q.all():
                    results.append({
                        "id": item.id,
                        "type": item.item_type,
                        "title": item.title,
                        "content": item.content[:500],
                        "source": item.source,
                        "confidence": item.confidence,
                        "created_at": item.created_at.isoformat()
                    })
            finally:
                session.close()
        
        return results
    
    async def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        session = self.Session()
        try:
            total_items = session.query(KnowledgeItem).count()
            
            # Count by type
            type_counts = {}
            for item_type in ["image", "text", "data", "analysis"]:
                count = session.query(KnowledgeItem).filter_by(item_type=item_type).count()
                if count > 0:
                    type_counts[item_type] = count
            
            return {
                "total_items": total_items,
                "by_type": type_counts,
                "vector_items": self.vector_collection.count()
            }
        finally:
            session.close()


# Global knowledge base instance
knowledge_base = KnowledgeBase()


async def init_db():
    """Initialize database on startup"""
    await knowledge_base.initialize()