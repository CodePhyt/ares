# ARES - Autonomes Resilientes Enterprise Suite

**Ein DSGVO-konformes, 100% Offline AI Command Center für deutsche Unternehmen**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](RELEASE_NOTES.md)

## 🛡️ Was ist ARES?

ARES ist ein AI Command Center für deutsche Unternehmen. Es hilft dir, Dokumente zu durchsuchen und zu analysieren. Alles funktioniert offline - deine Daten bleiben bei dir.

### Wichtigste Funktionen

- **🔒 100% Offline**: Alles läuft auf deinem Computer - keine Cloud nötig
- **🛡️ DSGVO-konform**: Automatische Erkennung und Maskierung von persönlichen Daten
- **🧠 Intelligente Suche**: Findet die richtigen Informationen in deinen Dokumenten
- **📊 Einfache Bedienung**: Schöne Benutzeroberfläche zum Arbeiten
- **🇩🇪 Deutsch**: Funktioniert perfekt mit deutschen Texten und Umlauten

## 🚀 Schnellstart

### Was du brauchst

- Python 3.12 oder neuer
- Docker (optional, aber empfohlen)
- Mindestens 8GB RAM
- 20GB freier Speicherplatz

### Installation mit Docker (Einfachste Methode)

**Schritt 1**: Starte alle Services
```bash
docker-compose up -d
```

**Schritt 2**: Lade die AI-Modelle
```bash
docker exec ares-ollama ollama pull llama3:8b && docker exec ares-ollama ollama pull mxbai-embed-large
```

Das war's! ARES läuft jetzt.

### Zugriff

- **Benutzeroberfläche**: http://localhost:8501
- **API Dokumentation**: http://localhost:8000/docs
- **Status prüfen**: http://localhost:8000/health

## 📖 Wie funktioniert es?

### 1. Dokumente hochladen

Du kannst verschiedene Dateiformate hochladen:
- PDF-Dateien
- Word-Dokumente (.docx)
- Textdateien (.txt)
- Markdown-Dateien (.md)
- Excel-Dateien (.xlsx)

ARES analysiert deine Dokumente automatisch und macht sie durchsuchbar.

### 2. Fragen stellen

Stelle einfach Fragen zu deinen Dokumenten. Zum Beispiel:
- "Was steht im Vertrag über die Kündigungsfrist?"
- "Welche Informationen gibt es über Projekt X?"
- "Zusammenfassung des Berichts"

ARES sucht in deinen Dokumenten und gibt dir eine Antwort.

### 3. Ergebnisse ansehen

Du bekommst:
- Eine klare Antwort auf deine Frage
- Quellenangaben (welche Dokumente wurden verwendet)
- Eine Vertrauensbewertung (wie sicher ist die Antwort)
- Informationen über gefundene persönliche Daten

## 🎨 Neue Features in Version 1.1.0

### Analytics Dashboard

Sieh dir an, wie ARES läuft:
- Geschwindigkeit der AI
- Speicherverbrauch
- Anzahl der verarbeiteten Anfragen
- Statistiken über geschützte persönliche Daten

### PDF Export

Exportiere deine Suchergebnisse als professionelles PDF:
- Mit ARES-Wasserzeichen
- Alle Quellenangaben enthalten
- Perfekt für Berichte und Dokumentation

### Dokument-Beziehungen

Sieh, wie deine Dokumente zusammenhängen:
- Visuelle Darstellung der Verbindungen
- Welche Dokumente haben ähnliche Themen
- Einfache Übersicht über deine Dokumentensammlung

### Premium Design

Schöne Benutzeroberfläche:
- Dunkles Design (Slate & Gold)
- Hell/Dunkel Modus
- Einfache Navigation
- Professionelles Aussehen

## 🔒 Datenschutz

ARES ist sehr sicher:

- **Alles offline**: Deine Daten verlassen nie deinen Computer
- **Automatischer Schutz**: Persönliche Daten werden automatisch erkannt und maskiert
- **DSGVO-konform**: Erfüllt alle deutschen Datenschutzanforderungen
- **Keine Cloud**: Keine Verbindung zu externen Servern

### Welche Daten werden geschützt?

ARES erkennt und schützt:
- Namen von Personen
- Adressen
- IBAN-Nummern
- E-Mail-Adressen

## 💻 Technische Details

### Was wird verwendet?

- **Python 3.12+**: Moderne Programmiersprache
- **FastAPI**: Schneller Webserver
- **Ollama**: Lokale AI-Modelle (keine Internetverbindung nötig)
- **ChromaDB**: Datenbank für Dokumente
- **Streamlit**: Benutzeroberfläche

### Unterstützte Formate

- PDF
- Word (.docx)
- Text (.txt)
- Markdown (.md)
- Excel (.xlsx)

## 📚 Dokumentation

### Für Anfänger

- [QUICKSTART.md](QUICKSTART.md) - Schritt-für-Schritt Anleitung
- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Schnelle Installation

### Für Fortgeschrittene

- [DEPLOYMENT.md](DEPLOYMENT.md) - Produktions-Installation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Probleme lösen
- [DSGVO_KONFORMITÄT.md](DSGVO_KONFORMITÄT.md) - Datenschutz-Details

## ❓ Häufige Fragen

### Wie schnell ist ARES?

Die Antwortzeit hängt von der Größe deiner Dokumente ab. Normalerweise bekommst du eine Antwort in 5-10 Sekunden.

### Brauche ich Internet?

Nein! ARES funktioniert komplett offline. Du brauchst nur Internet, um es herunterzuladen und die AI-Modelle zu installieren.

### Kann ich viele Dokumente hochladen?

Ja, ARES kann viele Dokumente verwalten. Je mehr Dokumente, desto mehr Speicherplatz brauchst du.

### Ist es kostenlos?

ARES ist Open Source. Du kannst es kostenlos verwenden.

### Funktioniert es nur auf Deutsch?

ARES funktioniert am besten mit deutschen Texten, kann aber auch andere Sprachen verstehen.

## 🐛 Probleme?

Wenn etwas nicht funktioniert:

1. Prüfe, ob alle Services laufen: `docker-compose ps`
2. Sieh dir die Logs an: `docker-compose logs -f`
3. Lies die [TROUBLESHOOTING.md](TROUBLESHOOTING.md) Anleitung

## 🤝 Mithelfen

Du kannst bei der Entwicklung helfen:
- Fehler melden
- Neue Funktionen vorschlagen
- Code verbessern

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

## 📝 Lizenz

Proprietär - Alle Rechte vorbehalten.

## 🙏 Danksagungen

ARES verwendet:
- Ollama für lokale AI
- ChromaDB für die Datenbank
- Microsoft Presidio für Datenschutz
- FastAPI für den Server
- Streamlit für die Oberfläche

---

**Version**: 1.1.0  
**Status**: Produktionsbereit  
**Letzte Aktualisierung**: Januar 2024

**Für Fragen und Support, siehe die Dokumentation oder öffne ein Issue auf GitHub.**
