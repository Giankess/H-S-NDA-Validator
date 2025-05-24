from typing import List, Dict, Any
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from ..core.config import settings

class VectorStorage:
    def __init__(self):
        self.client = QdrantClient(url=settings.VECTOR_DB_URL)
        self.collection_name = "nda-embeddings"
        self._ensure_collection_exists()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _ensure_collection_exists(self):
        """Ensure the Qdrant collection exists"""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Dimension for all-MiniLM-L6-v2
                    distance=models.Distance.COSINE
                )
            )

    def create_embedding(self, text: str) -> List[float]:
        """Create an embedding for a text"""
        return self.model.encode(text).tolist()

    def store_document_embedding(self, document_id: str, text: str, metadata: Dict[str, Any] = None):
        """Store a document embedding in Qdrant"""
        embedding = self.create_embedding(text)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=document_id,
                    vector=embedding,
                    payload=metadata or {}
                )
            ]
        )

    def store_clause_embedding(self, document_id: str, clause_id: str, text: str, metadata: Dict[str, Any] = None):
        """Store a clause embedding in Qdrant"""
        embedding = self.create_embedding(text)
        vector_id = f"{document_id}:{clause_id}"
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=vector_id,
                    vector=embedding,
                    payload=metadata or {}
                )
            ]
        )

    def find_similar_clauses(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar clauses based on text similarity"""
        query_embedding = self.create_embedding(text)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True
        )
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "metadata": hit.payload
            }
            for hit in results
        ]

    def store_feedback_embedding(self, document_id: str, feedback_id: str, text: str, metadata: Dict[str, Any] = None):
        """Store feedback embedding for learning"""
        embedding = self.create_embedding(text)
        vector_id = f"feedback:{document_id}:{feedback_id}"
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=vector_id,
                    vector=embedding,
                    payload=metadata or {}
                )
            ]
        )

    def find_similar_feedback(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar feedback based on text similarity"""
        query_embedding = self.create_embedding(text)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(value="feedback")
                    )
                ]
            )
        )
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "metadata": hit.payload
            }
            for hit in results
        ] 