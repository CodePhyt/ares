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

## [1.1.0] - 2024-01-20

### Added - Enterprise Features
- **📊 Analytics Dashboard**: Comprehensive System Health tab with:
  - Real-time inference speed tracking (tokens/sec)
  - Memory usage visualization (Process, ChromaDB, System)
  - Query performance metrics and history
  - Privacy Shield counter (session-based PII masking statistics)
  - API metrics dashboard with uptime, error rates, and request timing
- **📄 Advanced PDF Export**: Professional audit reports with:
  - ARES watermark on every page
  - Complete query audit trails
  - Source citations with page numbers
  - Color-coded metrics tables
  - GDPR compliance footer
  - One-click export from any query result
- **🗺️ Document Relationship Discovery**: Interactive network visualization:
  - Keyword-based document relationship mapping
  - Network graph with Plotly visualization
  - Network statistics (nodes, edges, density)
  - Document details table with connection counts
- **🎨 Premium UI Enhancements**:
  - Slate & Gold premium dark theme
  - Dark/Light mode toggle
  - Custom page title: "ARES | Enterprise AI Command Center"
  - Professional navigation tabs (Query, Analytics, Discovery, Export)
  - Smooth animations and transitions
  - Enterprise branding elements
- **🐳 Docker Quickstart**: 2-command deployment guide
- **📚 Enhanced Documentation**:
  - ENTERPRISE_FEATURES.md - Complete feature documentation
  - IMPLEMENTATION_SUMMARY.md - Technical implementation details
  - DEPLOYMENT_CHECKLIST.md - Pre/post-deployment checklist
  - DOCKER_QUICKSTART.md - Quick deployment guide

### Changed
- Updated UI theme to premium Slate & Gold color scheme
- Enhanced Streamlit configuration with new theme colors
- Improved PDF export handling with proper file download support
- Added exports directory to .gitignore

### Technical
- Added new dependencies: plotly, networkx, reportlab, Pillow, psutil, streamlit-aggrid
- New API endpoints:
  - `GET /api/v1/system/health` - Detailed system health metrics
  - `GET /api/v1/documents/graph` - Document relationship graph data
  - `POST /api/v1/export/audit-pdf` - PDF export endpoint
- Enhanced metrics collection with system monitoring
- Improved error handling and user feedback

### Fixed
- PDF export file handling in UI
- Memory usage calculation accuracy
- Graph visualization layout improvements

---

## [Unreleased]

### Planned Features
- Advanced authentication and authorization
- Multi-user support with role-based access control
- Enhanced audit logging and reporting
- Performance optimizations for large document collections
- Additional language support
- API rate limiting and throttling
- WebSocket support for real-time updates
