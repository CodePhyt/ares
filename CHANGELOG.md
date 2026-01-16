# Changelog

All notable changes to ARES will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of ARES (Autonomous Resilient Enterprise Suite)
- **Core RAG Engine**: Hybrid search combining ChromaDB (vector) and BM25 (keyword)
- **Parent-Document-Retriever**: Context preservation with chunking and parent relationships
- **Cross-Encoder Re-ranking**: Relevance optimization using sentence-transformers
- **Reasoning Agent**: PLAN/SEARCH/AUDIT workflow for fact-checked responses
- **PII Masking**: Microsoft Presidio integration for German text (Names, Addresses, IBANs, Emails)
- **FastAPI Backend**: Asynchronous REST API with comprehensive Swagger documentation
- **Streamlit Frontend**: Cyber-enterprise dark theme UI with:
  - Real-time token streaming simulation
  - Source citations with file names and page numbers
  - Privacy status indicators
- **Document Processing**: Support for PDF, DOCX, TXT, MD, and XLSX files
- **Docker Support**: Complete docker-compose setup with backend, Ollama, and frontend services
- **Test Suite**: Comprehensive pytest tests for core functionality
- **Documentation**: 
  - Professional English README
  - Detailed German GDPR compliance documentation (DSGVO_KONFORMITÄT.md)
- **Configuration Management**: Environment-based settings with Pydantic validation
- **Setup Scripts**: Automated setup for Linux/Mac (bash) and Windows (PowerShell)
- **Utility Scripts**: Ollama connection and model checking tool

### Technical Details
- Python 3.12+ with full type hints
- Loguru for structured logging
- Pydantic for data validation
- 100% offline operation (no cloud dependencies)
- GDPR-compliant by design

### Security
- Automated PII detection and masking
- Local-only data processing
- Encrypted storage support
- Audit logging for compliance

---

## [Unreleased]

### Planned Features
- Advanced authentication and authorization
- Multi-user support with role-based access control
- Enhanced audit logging and reporting
- Performance optimizations for large document collections
- Additional language support
- Advanced visualization and analytics
- API rate limiting and throttling
- WebSocket support for real-time updates
