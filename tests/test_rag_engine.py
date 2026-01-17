"""
Tests for RAG Engine functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.core.rag_engine import HybridRAGEngine, DocumentChunk


class TestHybridRAGEngine:
    """Test suite for Hybrid RAG Engine."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def rag_engine(self, temp_db_path):
        """Create a RAG engine instance with temporary storage."""
        # Note: This requires Ollama to be running
        # In CI/CD, you might want to mock the embedding function
        import os
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return HybridRAGEngine(
            chroma_db_path=temp_db_path,
            collection_name="test_collection",
            ollama_base_url=ollama_url,
            chunk_size=100,  # Smaller for testing
            chunk_overlap=10,
        )

    def test_chunk_text(self, rag_engine):
        """Test text chunking."""
        text = " ".join(["word"] * 200)  # Create long text
        metadata = {"document_id": "test_doc", "filename": "test.txt"}
        
        chunks = rag_engine._chunk_text(text, metadata)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        assert all(chunk.parent_id == "test_doc" for chunk in chunks)

    def test_chunk_metadata(self, rag_engine):
        """Test that chunk metadata is preserved."""
        text = "Test document content"
        metadata = {"document_id": "doc1", "filename": "test.pdf", "page": 1}
        
        chunks = rag_engine._chunk_text(text, metadata)
        
        if chunks:
            assert chunks[0].metadata["filename"] == "test.pdf"
            assert chunks[0].metadata["page"] == 1

    @pytest.mark.skip(reason="Requires Ollama running")
    def test_index_document(self, rag_engine):
        """Test document indexing."""
        document_id = "test_doc_1"
        text = "This is a test document with some content."
        metadata = {"filename": "test.txt"}
        
        chunks_created = rag_engine.index_document(
            document_id=document_id,
            text=text,
            metadata=metadata,
            rebuild_bm25=False,  # Skip BM25 rebuild for speed
        )
        
        assert chunks_created > 0

    @pytest.mark.skip(reason="Requires Ollama running")
    def test_hybrid_search(self, rag_engine):
        """Test hybrid search."""
        # First index a document
        rag_engine.index_document(
            document_id="test_doc",
            text="Machine learning is a subset of artificial intelligence.",
            metadata={"filename": "test.txt"},
            rebuild_bm25=True,
        )
        
        # Then search
        results = rag_engine.hybrid_search(
            query="What is machine learning?",
            top_k=3,
        )
        
        assert isinstance(results, list)
        assert all(isinstance(chunk, DocumentChunk) for chunk in results)

    def test_delete_document(self, rag_engine):
        """Test document deletion."""
        # Should handle non-existent document gracefully
        result = rag_engine.delete_document("non_existent_doc")
        assert isinstance(result, bool)
