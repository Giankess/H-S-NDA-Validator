import pinecone
from typing import List, Dict, Any
import numpy as np
from ..core.config import settings
from sentence_transformers import SentenceTransformer

class VectorStorage:
    def __init__(self):
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        self.index_name = "nda-embeddings"
        self._ensure_index_exists()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists"""
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                dimension=384,  # Dimension for all-MiniLM-L6-v2
                metric="cosine"
            )
        self.index = pinecone.Index(self.index_name)

    def create_embedding(self, text: str) -> List[float]:
        """Create an embedding for a text"""
        return self.model.encode(text).tolist()

    def store_document_embedding(self, document_id: str, text: str, metadata: Dict[str, Any] = None):
        """Store a document embedding in Pinecone"""
        embedding = self.create_embedding(text)
        self.index.upsert(
            vectors=[(document_id, embedding, metadata or {})]
        )

    def store_clause_embedding(self, document_id: str, clause_id: str, text: str, metadata: Dict[str, Any] = None):
        """Store a clause embedding in Pinecone"""
        embedding = self.create_embedding(text)
        vector_id = f"{document_id}:{clause_id}"
        self.index.upsert(
            vectors=[(vector_id, embedding, metadata or {})]
        )

    def find_similar_clauses(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar clauses based on text similarity"""
        query_embedding = self.create_embedding(text)
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return results.matches

    def store_feedback_embedding(self, document_id: str, feedback_id: str, text: str, metadata: Dict[str, Any] = None):
        """Store feedback embedding for learning"""
        embedding = self.create_embedding(text)
        vector_id = f"feedback:{document_id}:{feedback_id}"
        self.index.upsert(
            vectors=[(vector_id, embedding, metadata or {})]
        )

    def find_similar_feedback(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar feedback based on text similarity"""
        query_embedding = self.create_embedding(text)
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"type": "feedback"}
        )
        return results.matches 