# ARES - Autonome Resiliente Enterprise Suite

**Ein DSGVO-konformes, 100% offline AI Command Center für deutsche Unternehmen**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Lizenz](https://img.shields.io/badge/lizenz-Proprietär-red.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](RELEASE_NOTES.md)

## 🛡️ Übersicht

ARES ist ein Enterprise-grade AI Command Center, das speziell für deutsche Unternehmen entwickelt wurde, die **absolute Datenhoheit** und **DSGVO-Konformität** benötigen. Mit Privacy-First-Prinzipien ermöglicht ARES Organisationen, sensible Dokumente zu indexieren, zu durchsuchen und zu analysieren - alles während die Daten niemals Ihre Infrastruktur verlassen.

### Hauptfunktionen

- **🔒 100% Offline-Betrieb**: Alle Verarbeitung erfolgt lokal - keine Cloud-Abhängigkeiten
- **🛡️ DSGVO-konform**: Automatische PII-Erkennung und -Maskierung mit Microsoft Presidio
- **🧠 Agentisches Reasoning**: PLAN/SEARCH/AUDIT-Workflow für genaue, faktengeprüfte Antworten
- **🔍 Hybrid-Suche**: Kombiniert Vektorsuche (ChromaDB) mit Keyword-Suche (BM25) für optimale Ergebnisse
- **📊 Enterprise-UI**: Professionelle Streamlit-Oberfläche mit Echtzeit-Streaming und Quellenangaben
- **🇩🇪 Deutsche Sprachunterstützung**: Vollständige Unterstützung für deutschen Text, einschließlich Umlaute

## 🏗️ Architektur

### Kernkomponenten

1. **Backend (FastAPI)**: Asynchrone REST-API mit umfassender Swagger-Dokumentation
2. **RAG-Engine**: Hybrid-Suche kombiniert:
   - Vektorsuche über ChromaDB mit `mxbai-embed-large` Embeddings
   - Keyword-Suche über BM25
   - Parent-Document-Retriever-Muster zur Kontexterhaltung
   - Cross-Encoder Re-Ranking zur Relevanzoptimierung
3. **Reasoning-Agent**: LangGraph-basierter Agent mit:
   - **PLAN**: Bestimmt, ob Abfrage Dokumentensuche erfordert
   - **SEARCH**: Führt Hybrid-RAG-Abruf durch
   - **AUDIT**: Faktenprüfung der Antworten gegen abgerufenen Kontext
4. **Privacy Shield**: Microsoft Presidio-Integration für:
   - Namen, Adressen, IBANs, E-Mail-Erkennung
   - Automatische Maskierung vor Verarbeitung
   - Compliance-Auditierung
5. **Frontend (Streamlit)**: Cyber-Enterprise-Dunkeltheme-UI mit:
   - Echtzeit-Token-Streaming
   - Quellenangaben mit Dateinamen/Seitennummern
   - Privacy-Status-Indikatoren

### Technologie-Stack

- **Python 3.12+**: Modernes Python mit Type Hints
- **FastAPI**: Hochperformantes asynchrones Web-Framework
- **Ollama**: Lokale LLM-Inferenz (Llama-3-8B & mxbai-embed-large)
- **ChromaDB**: Vektordatenbank für Embeddings
- **LangChain/LangGraph**: Agent-Orchestrierung
- **Microsoft Presidio**: PII-Erkennung und Anonymisierung
- **Streamlit**: Interaktive Web-Oberfläche

## 🚀 Schnellstart

> **Neu bei ARES?** Schauen Sie sich die [Schnellstart-Anleitung](QUICKSTART.md) für eine Schritt-für-Schritt-Anleitung an!

### Voraussetzungen

- Python 3.12 oder höher
- Docker und Docker Compose (für containerisierte Bereitstellung)
- Ollama installiert und laufend

### Installation

1. **Repository klonen**
   ```bash
   git clone https://github.com/CodePhyt/ares.git
   cd ares
   ```

2. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

3. **Deutsches spaCy-Modell für Presidio herunterladen**
   ```bash
   python -m spacy download de_core_news_sm
   ```

4. **Umgebung konfigurieren**
   ```bash
   cp .env.example .env
   # .env mit Ihren Einstellungen bearbeiten
   ```

5. **Ollama starten und Modelle laden**
   ```bash
   # Ollama-Service starten
   ollama serve
   
   # Erforderliche Modelle laden (in einem anderen Terminal)
   ollama pull llama3:8b
   ollama pull mxbai-embed-large
   ```

6. **Backend starten**
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

7. **Frontend starten** (in einem anderen Terminal)
   ```bash
   streamlit run src/ui/app.py
   ```

8. **Anwendung öffnen**
   - Frontend: http://localhost:8501
   - API-Dokumentation: http://localhost:8000/docs

### Docker-Bereitstellung

```bash
# Alle Services starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f

# Services stoppen
docker-compose down
```

## 📖 Verwendung

### Dokumente hochladen

1. Navigieren Sie zur Seitenleiste in der Streamlit-UI
2. Klicken Sie auf "Upload Documents"
3. Wählen Sie eine Datei (PDF, DOCX, TXT, MD oder XLSX)
4. Klicken Sie auf "Upload & Index"
5. Das Dokument wird:
   - Auf PII gescannt
   - Gechunkt und indexiert
   - Abfragebereit gemacht

### Dokumente abfragen

1. Geben Sie Ihre Frage in die Chat-Oberfläche ein
2. ARES wird:
   - Die Abfragestrategie planen
   - Relevante Dokumente durchsuchen
   - Eine Antwort generieren
   - Auf Genauigkeit prüfen
3. Zitate und Konfidenz-Scores anzeigen
4. PII-Maskierungsstatus überprüfen

## 🔒 Datenschutz & Sicherheit

### Datenhoheit

- **100% Lokale Verarbeitung**: Alle KI-Inferenz erfolgt auf Ihrer Infrastruktur
- **Keine externen APIs**: Keine Daten werden an Cloud-Services gesendet
- **Verschlüsselte Speicherung**: ChromaDB-Daten werden lokal mit Zugriffskontrollen gespeichert

### PII-Schutz

- **Automatische Erkennung**: Microsoft Presidio erkennt:
  - Namen (PERSON)
  - E-Mail-Adressen
  - Telefonnummern
  - IBAN-Codes
  - Physische Adressen (LOCATION)
  - Kreditkartennummern
- **Maskierungsstrategien**: Ersetzen, Hashen oder Verschlüsseln sensibler Daten
- **Audit-Protokollierung**: Verfolgung aller PII-Erkennungs- und Maskierungsereignisse

### DSGVO-Konformität

ARES ist mit DSGVO Artikel 25 (Datenschutz durch Technikgestaltung) entwickelt:

- **Privacy by Default**: PII-Maskierung standardmäßig aktiviert
- **Datenminimierung**: Nur notwendige Daten werden verarbeitet
- **Recht auf Löschung**: Dokumente können aus dem Index gelöscht werden
- **Audit-Trails**: Umfassende Protokollierung für Compliance-Berichte

Für detaillierte DSGVO-Konformitätsinformationen siehe [DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md).

## 🧪 Tests

Test-Suite ausführen:

```bash
# Alle Tests ausführen
pytest

# Mit Coverage
pytest --cov=src --cov-report=html

# Spezifische Testdatei
pytest tests/test_pii_masker.py
```

## 📁 Projektstruktur

```
.
├── src/
│   ├── api/              # FastAPI Backend
│   ├── core/             # Kernfunktionalität
│   ├── security/         # Datenschutz & Sicherheit
│   ├── ui/               # Streamlit Frontend
│   └── utils/            # Hilfsfunktionen
├── scripts/              # Utility-Skripte
├── examples/             # Beispielcode und Daten
├── tests/                # Test-Suite
├── docker-compose.yml    # Docker-Orchestrierung
└── [Konfigurationsdateien]
```

## ⚙️ Konfiguration

Wichtige Konfigurationsoptionen in `.env`:

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large

# ChromaDB
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=ares_documents

# Datenschutz
ENABLE_PII_MASKING=true
PII_MASKING_STRATEGY=replace

# RAG
TOP_K_DOCUMENTS=5
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

## 📚 Zusätzliche Dokumentation

- **[QUICKSTART.md](QUICKSTART.md)**: Schritt-für-Schritt Setup-Anleitung
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Produktions-Bereitstellungsanleitung
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Häufige Probleme und Lösungen
- **[DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md)**: DSGVO-Konformitätsdokumentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Entwicklungsrichtlinien
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Projektübersicht

## 🆘 Support

Für technischen Support oder Fragen:
- Überprüfen Sie die [Schnellstart-Anleitung](QUICKSTART.md) für Setup-Hilfe
- Prüfen Sie [TROUBLESHOOTING.md](TROUBLESHOOTING.md) für häufige Probleme
- Überprüfen Sie die [API-Dokumentation](http://localhost:8000/docs) beim Ausführen des Backends
- Prüfen Sie [DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md) für DSGVO-Konformitätsdetails
- Überprüfen Sie Logs in der Anwendungskonsole

## 🙏 Danksagungen

Erstellt mit:
- [Ollama](https://ollama.ai/) - Lokale LLM-Inferenz
- [ChromaDB](https://www.trychroma.com/) - Vektordatenbank
- [Microsoft Presidio](https://github.com/microsoft/presidio) - PII-Erkennung
- [LangChain](https://www.langchain.com/) - LLM-Orchestrierung
- [FastAPI](https://fastapi.tiangolo.com/) - Web-Framework
- [Streamlit](https://streamlit.io/) - UI-Framework

---

**ARES v1.0.0** - Entwickelt für deutsche Enterprise-Datenhoheit 🛡️
