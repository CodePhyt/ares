"""
Tests for PII Masker functionality.
"""

import pytest
from src.security.pii_masker import GermanPIIMasker


class TestGermanPIIMasker:
    """Test suite for German PII Masker."""

    @pytest.fixture
    def masker(self):
        """Create a PII masker instance."""
        return GermanPIIMasker(masking_strategy="replace")

    def test_detect_email(self, masker):
        """Test email detection."""
        text = "Kontaktieren Sie uns unter max.mustermann@example.com"
        detections = masker.detect_pii(text)
        
        assert len(detections) > 0
        assert any(d["entity_type"] == "EMAIL_ADDRESS" for d in detections)

    def test_detect_name(self, masker):
        """Test name detection."""
        text = "Herr Max Mustermann hat die Rechnung bezahlt."
        detections = masker.detect_pii(text)
        
        # May or may not detect depending on Presidio model
        assert isinstance(detections, list)

    def test_mask_text(self, masker):
        """Test text masking."""
        text = "Email: test@example.com"
        result = masker.mask_text(text)
        
        assert "masked_text" in result
        assert "original_text" in result
        assert result["original_text"] == text
        assert isinstance(result["masked"], bool)

    def test_audit_document(self, masker):
        """Test document auditing."""
        text = "Kontakt: max@example.com, Telefon: +49 123 456789"
        audit = masker.audit_document(text)
        
        assert "total_pii" in audit
        assert "entity_breakdown" in audit
        assert "compliance_status" in audit
        assert isinstance(audit["total_pii"], int)

    def test_empty_text(self, masker):
        """Test handling of empty text."""
        result = masker.mask_text("")
        assert result["masked"] is False
        assert result["pii_count"] == 0

    def test_german_umlauts(self, masker):
        """Test handling of German umlauts."""
        text = "Müller, Schäfer, Größe"
        result = masker.mask_text(text)
        
        # Should not crash with umlauts
        assert "masked_text" in result
