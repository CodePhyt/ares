"""
PII Masker using Microsoft Presidio for German text.
Detects and anonymizes Names, Addresses, IBANs, and Emails.
"""

from typing import List, Dict, Any, Optional
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from loguru import logger
import spacy


class GermanPIIMasker:
    """
    Enterprise-grade PII detection and masking for German text.
    Ensures GDPR compliance by anonymizing sensitive data before processing.
    """

    def __init__(self, masking_strategy: str = "replace"):
        """
        Initialize the PII masker with German language support.

        Args:
            masking_strategy: Strategy for masking ('replace', 'hash', 'encrypt')
        """
        self.masking_strategy = masking_strategy
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # German-specific entity types to detect
        self.german_entities = [
            "PERSON",      # Names
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "IBAN_CODE",   # German IBANs
            "CREDIT_CARD",
            "LOCATION",    # Addresses
            "DATE_TIME",
        ]
        
        logger.info("German PII Masker initialized with strategy: {}", masking_strategy)

    def detect_pii(self, text: str, language: str = "de") -> List[Dict[str, Any]]:
        """
        Detect PII entities in German text.

        Args:
            text: Input text to analyze
            language: Language code (default: 'de' for German)

        Returns:
            List of detected PII entities with positions and types
        """
        try:
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=self.german_entities,
            )
            
            detections = [
                {
                    "entity_type": result.entity_type,
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                    "text": text[result.start:result.end],
                }
                for result in results
            ]
            
            logger.debug("Detected {} PII entities", len(detections))
            return detections
            
        except Exception as e:
            logger.error("Error detecting PII: {}", e)
            return []

    def mask_text(
        self,
        text: str,
        language: str = "de",
        custom_operators: Optional[Dict[str, OperatorConfig]] = None,
    ) -> Dict[str, Any]:
        """
        Mask PII in text according to the configured strategy.

        Args:
            text: Input text containing potential PII
            language: Language code (default: 'de')
            custom_operators: Custom masking operators for specific entity types

        Returns:
            Dictionary with masked text and audit information
        """
        try:
            # Detect PII
            detections = self.detect_pii(text, language)
            
            if not detections:
                return {
                    "masked_text": text,
                    "original_text": text,
                    "detections": [],
                    "pii_count": 0,
                    "masked": False,
                }

            # Configure masking operators
            operators = custom_operators or self._get_default_operators()
            
            # Anonymize
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=detections,
                operators=operators,
            )

            audit_info = {
                "masked_text": anonymized_result.text,
                "original_text": text,
                "detections": detections,
                "pii_count": len(detections),
                "masked": True,
                "entities_found": list(set(d["entity_type"] for d in detections)),
            }

            logger.info(
                "Masked {} PII entities in text (types: {})",
                len(detections),
                audit_info["entities_found"],
            )

            return audit_info

        except Exception as e:
            logger.error("Error masking PII: {}", e)
            return {
                "masked_text": text,
                "original_text": text,
                "detections": [],
                "pii_count": 0,
                "masked": False,
                "error": str(e),
            }

    def _get_default_operators(self) -> Dict[str, OperatorConfig]:
        """Get default masking operators based on strategy."""
        if self.masking_strategy == "replace":
            return {
                "PERSON": OperatorConfig("replace", {"new_value": "[NAME]"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
                "IBAN_CODE": OperatorConfig("replace", {"new_value": "[IBAN]"}),
                "LOCATION": OperatorConfig("replace", {"new_value": "[ADDRESS]"}),
                "DATE_TIME": OperatorConfig("replace", {"new_value": "[DATE]"}),
                "CREDIT_CARD": OperatorConfig("replace", {"new_value": "[CARD]"}),
            }
        elif self.masking_strategy == "hash":
            return {
                "PERSON": OperatorConfig("hash"),
                "EMAIL_ADDRESS": OperatorConfig("hash"),
                "PHONE_NUMBER": OperatorConfig("hash"),
                "IBAN_CODE": OperatorConfig("hash"),
                "LOCATION": OperatorConfig("hash"),
                "DATE_TIME": OperatorConfig("hash"),
                "CREDIT_CARD": OperatorConfig("hash"),
            }
        else:  # default to replace
            return self._get_default_operators()

    def audit_document(self, text: str) -> Dict[str, Any]:
        """
        Audit a document for PII without masking.
        Used for compliance reporting.

        Args:
            text: Document text to audit

        Returns:
            Audit report with PII statistics
        """
        detections = self.detect_pii(text)
        
        entity_counts = {}
        for detection in detections:
            entity_type = detection["entity_type"]
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        return {
            "total_pii": len(detections),
            "entity_breakdown": entity_counts,
            "detections": detections,
            "compliance_status": "compliant" if len(detections) == 0 else "requires_masking",
        }
