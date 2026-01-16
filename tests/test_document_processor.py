"""
Tests for Document Processor functionality.
"""

import pytest
import tempfile
from pathlib import Path
from src.core.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test suite for Document Processor."""

    @pytest.fixture
    def processor(self):
        """Create a document processor instance."""
        return DocumentProcessor()

    def test_process_text_file(self, processor):
        """Test processing a text file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is a test document.\n\nWith multiple paragraphs.")
            temp_path = f.name

        try:
            result = processor.process_file(temp_path)
            
            assert "text" in result
            assert "metadata" in result
            assert "test document" in result["text"]
            assert result["metadata"]["file_type"] == "txt"
        finally:
            Path(temp_path).unlink()

    def test_process_markdown_file(self, processor):
        """Test processing a markdown file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Document\n\nThis is **bold** text.")
            temp_path = f.name

        try:
            result = processor.process_file(temp_path)
            
            assert "text" in result
            assert "metadata" in result
            assert result["metadata"]["file_type"] == "md"
        finally:
            Path(temp_path).unlink()

    def test_unsupported_file_type(self, processor):
        """Test handling of unsupported file types."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                processor.process_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_german_umlauts_in_text(self, processor):
        """Test handling of German umlauts in text files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write("Müller, Schäfer, Größe, Österreich")
            temp_path = f.name

        try:
            result = processor.process_file(temp_path)
            
            assert "Müller" in result["text"]
            assert "Schäfer" in result["text"]
            assert "Österreich" in result["text"]
        finally:
            Path(temp_path).unlink()
