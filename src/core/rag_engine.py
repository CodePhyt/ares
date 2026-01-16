"""
Hybrid RAG Engine with Parent-Document-Retriever and Cross-Encoder Re-ranking.
Combines ChromaDB (vector search) with BM25 (keyword search) for optimal retrieval.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from loguru import logger
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Represents a document chunk with metadata."""
    id: str
    content: str
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: float = 0.0


class HybridRAGEngine:
    """
    Enterprise-grade hybrid RAG engine combining:
    - Vector search (ChromaDB with mxbai-embed-large)
    - Keyword search (BM25)
    - Parent-Document-Retriever pattern
    - Cross-Encoder re-ranking
    """

    def __init__(
        self,
        chroma_db_path: str = "./chroma_db",
        collection_name: str = "ares_documents",
        ollama_base_url: str = "http://localhost:11434",
        embedding_model: str = "mxbai-embed-large",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        """
        Initialize the hybrid RAG engine.

        Args:
            chroma_db_path: Path to ChromaDB storage
            collection_name: Name of the ChromaDB collection
            ollama_base_url: Base URL for Ollama API
            embedding_model: Model name for embeddings
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.ollama_base_url = ollama_base_url
        self.embedding_model = embedding_model

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(anonymized_telemetry=False),
        )
        
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info("Loaded existing ChromaDB collection: {}", collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Created new ChromaDB collection: {}", collection_name)

        # Initialize BM25 (will be built from documents)
        self.bm25: Optional[BM25Okapi] = None
        self.bm25_documents: List[str] = []
        self.bm25_id_map: Dict[int, str] = {}

        # Initialize Cross-Encoder for re-ranking
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        logger.info("Hybrid RAG Engine initialized")

    @staticmethod
    def _create_httpx_client() -> httpx.AsyncClient:
        """Create a reusable HTTP client with connection pooling."""
        return httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama."""
        try:
            import httpx
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.ollama_base_url}/api/embeddings",
                    json={"model": self.embedding_model, "prompt": text},
                )
                response.raise_for_status()
                return response.json()["embedding"]
        except Exception as e:
            logger.error("Error getting embedding: {}", e)
            raise

    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Split text into chunks with overlap (Parent-Document-Retriever pattern).
        
        Args:
            text: Full document text
            metadata: Document metadata (filename, page, etc.)

        Returns:
            List of document chunks
        """
        words = text.split()
        chunks = []
        parent_id = metadata.get("document_id", "unknown")

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunk_id = f"{parent_id}_chunk_{i}"
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "parent_id": parent_id,
            }

            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    content=chunk_text,
                    parent_id=parent_id,
                    metadata=chunk_metadata,
                )
            )

        return chunks

    def index_document(
        self,
        document_id: str,
        text: str,
        metadata: Dict[str, Any],
        rebuild_bm25: bool = True,
    ) -> int:
        """
        Index a document using Parent-Document-Retriever pattern.

        Args:
            document_id: Unique document identifier
            text: Document text
            metadata: Document metadata (filename, page, etc.)
            rebuild_bm25: Whether to rebuild BM25 index

        Returns:
            Number of chunks created
        """
        try:
            # Create chunks
            chunks = self._chunk_text(text, {**metadata, "document_id": document_id})
            
            if not chunks:
                logger.warning("No chunks created for document: {}", document_id)
                return 0

            # Get embeddings for all chunks
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = []
            
            for chunk_text in chunk_texts:
                embedding = self._get_embedding(chunk_text)
                embeddings.append(embedding)

            # Store in ChromaDB
            self.collection.add(
                ids=[chunk.id for chunk in chunks],
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=[chunk.metadata for chunk in chunks],
            )

            # Update BM25 index
            if rebuild_bm25:
                self._rebuild_bm25()

            logger.info(
                "Indexed document {} with {} chunks",
                document_id,
                len(chunks),
            )
            return len(chunks)

        except Exception as e:
            logger.error("Error indexing document {}: {}", document_id, e)
            raise

    def _rebuild_bm25(self):
        """Rebuild BM25 index from all documents in ChromaDB."""
        try:
            # Fetch all documents from ChromaDB
            results = self.collection.get()
            
            if not results["documents"]:
                logger.warning("No documents found for BM25 index")
                return

            # Tokenize documents for BM25
            tokenized_docs = [doc.split() for doc in results["documents"]]
            self.bm25 = BM25Okapi(tokenized_docs)
            self.bm25_documents = results["documents"]
            self.bm25_id_map = {
                i: results["ids"][i] for i in range(len(results["ids"]))
            }

            logger.info("Rebuilt BM25 index with {} documents", len(tokenized_docs))

        except Exception as e:
            logger.error("Error rebuilding BM25 index: {}", e)

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        top_k_parents: int = 3,
        rerank_top_k: int = 3,
    ) -> List[DocumentChunk]:
        """
        Perform hybrid search combining vector and keyword search.

        Args:
            query: Search query
            top_k: Number of chunks to retrieve
            top_k_parents: Number of parent documents to return
            rerank_top_k: Number of results to re-rank

        Returns:
            List of relevant document chunks with scores
        """
        try:
            # Vector search with ChromaDB
            query_embedding = self._get_embedding(query)
            vector_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2,  # Get more for re-ranking
            )

            vector_chunks = []
            if vector_results["ids"] and len(vector_results["ids"][0]) > 0:
                for i, chunk_id in enumerate(vector_results["ids"][0]):
                    vector_chunks.append(
                        DocumentChunk(
                            id=chunk_id,
                            content=vector_results["documents"][0][i],
                            metadata=vector_results["metadatas"][0][i],
                            score=1.0 - vector_results["distances"][0][i],  # Convert distance to similarity
                        )
                    )

            # Keyword search with BM25
            keyword_chunks = []
            if self.bm25:
                tokenized_query = query.split()
                bm25_scores = self.bm25.get_scores(tokenized_query)
                
                # Get top BM25 results
                top_indices = sorted(
                    range(len(bm25_scores)),
                    key=lambda i: bm25_scores[i],
                    reverse=True,
                )[:top_k * 2]

                for idx in top_indices:
                    chunk_id = self.bm25_id_map.get(idx)
                    if chunk_id:
                        # Get full metadata from ChromaDB
                        result = self.collection.get(ids=[chunk_id])
                        if result["documents"]:
                            keyword_chunks.append(
                                DocumentChunk(
                                    id=chunk_id,
                                    content=result["documents"][0],
                                    metadata=result["metadatas"][0] if result["metadatas"] else {},
                                    score=float(bm25_scores[idx]),
                                )
                            )

            # Combine and deduplicate
            all_chunks = {}
            for chunk in vector_chunks + keyword_chunks:
                if chunk.id not in all_chunks:
                    all_chunks[chunk.id] = chunk
                else:
                    # Combine scores (weighted average)
                    existing = all_chunks[chunk.id]
                    existing.score = (existing.score + chunk.score) / 2

            candidate_chunks = list(all_chunks.values())

            # Re-rank with Cross-Encoder
            if len(candidate_chunks) > rerank_top_k:
                rerank_pairs = [
                    [query, chunk.content] for chunk in candidate_chunks[:rerank_top_k * 2]
                ]
                rerank_scores = self.cross_encoder.predict(rerank_pairs)
                
                for i, chunk in enumerate(candidate_chunks[:rerank_top_k * 2]):
                    chunk.score = float(rerank_scores[i])

                # Sort by re-ranked scores
                candidate_chunks = sorted(
                    candidate_chunks,
                    key=lambda x: x.score,
                    reverse=True,
                )

            # Group by parent and select top parents
            parent_groups: Dict[str, List[DocumentChunk]] = {}
            for chunk in candidate_chunks[:top_k * 2]:
                parent_id = chunk.metadata.get("parent_id") or chunk.metadata.get("document_id", "unknown")
                if parent_id not in parent_groups:
                    parent_groups[parent_id] = []
                parent_groups[parent_id].append(chunk)

            # Select top chunks from top parents
            final_chunks = []
            sorted_parents = sorted(
                parent_groups.items(),
                key=lambda x: max(c.score for c in x[1]),
                reverse=True,
            )[:top_k_parents]

            for parent_id, chunks in sorted_parents:
                final_chunks.extend(sorted(chunks, key=lambda x: x.score, reverse=True)[:2])

            return final_chunks[:top_k]

        except Exception as e:
            logger.error("Error in hybrid search: {}", e)
            return []

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks."""
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"document_id": document_id},
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                self._rebuild_bm25()
                logger.info("Deleted document {} with {} chunks", document_id, len(results["ids"]))
                return True
            
            return False

        except Exception as e:
            logger.error("Error deleting document {}: {}", document_id, e)
            return False
