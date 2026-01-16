# DSGVO-Konformität - ARES

**Detaillierte Dokumentation zur Datenschutz-Grundverordnung (DSGVO) Konformität**

## 📋 Übersicht

ARES (Autonomous Resilient Enterprise Suite) wurde speziell entwickelt, um den strengen Anforderungen der Datenschutz-Grundverordnung (DSGVO) zu entsprechen. Diese Dokumentation erläutert die technischen und organisatorischen Maßnahmen (TOM), die ARES implementiert, um die Datenhoheit und den Datenschutz zu gewährleisten.

## 🎯 DSGVO-Grundsätze

### Artikel 5 DSGVO - Grundsätze für die Verarbeitung personenbezogener Daten

ARES implementiert alle in Artikel 5 DSGVO festgelegten Grundsätze:

#### 1. Rechtmäßigkeit, Verarbeitung nach Treu und Glauben, Transparenz
- ✅ **Lokale Verarbeitung**: Alle Daten werden ausschließlich auf Ihrer Infrastruktur verarbeitet
- ✅ **Transparente Verarbeitung**: Vollständige Audit-Logs aller Verarbeitungsschritte
- ✅ **Keine versteckten Datenübertragungen**: Keine Verbindungen zu externen Cloud-Diensten

#### 2. Zweckbindung
- ✅ **Dokumentierte Zwecke**: Verarbeitung nur für dokumentierte Geschäftszwecke
- ✅ **Keine Zweckentfremdung**: Daten werden nicht für andere Zwecke verwendet

#### 3. Datenminimierung
- ✅ **Selektive Verarbeitung**: Nur relevante Dokumententeile werden verarbeitet
- ✅ **Chunking**: Dokumente werden in relevante Abschnitte aufgeteilt
- ✅ **PII-Maskierung**: Personenbezogene Daten werden vor der Verarbeitung maskiert

#### 4. Richtigkeit
- ✅ **Faktenprüfung**: Audit-Mechanismus überprüft Antworten gegen Quellen
- ✅ **Quellenangaben**: Alle Antworten enthalten Quellenverweise
- ✅ **Konfidenz-Scores**: Transparente Angabe der Antwortqualität

#### 5. Speicherbegrenzung
- ✅ **Löschfunktion**: Dokumente können vollständig aus dem Index entfernt werden
- ✅ **Keine permanente Speicherung**: Daten werden nur für den dokumentierten Zweck gespeichert

#### 6. Integrität und Vertraulichkeit
- ✅ **Lokale Speicherung**: Daten verbleiben in Ihrer Kontrolle
- ✅ **Verschlüsselung**: ChromaDB-Datenbank mit Zugriffskontrollen
- ✅ **PII-Maskierung**: Automatische Anonymisierung sensibler Daten

## 🛡️ Technische Maßnahmen

### 1. Privacy by Design (Artikel 25 DSGVO)

ARES implementiert "Privacy by Design" durch:

#### Automatische PII-Erkennung
- **Microsoft Presidio Integration**: Erkennung von:
  - Namen (PERSON)
  - E-Mail-Adressen
  - Telefonnummern
  - IBAN-Codes
  - Postadressen (LOCATION)
  - Kreditkartennummern
  - Datum/Zeit-Informationen

#### Maskierungsstrategien
- **Replace**: Ersetzung durch Platzhalter (z.B. `[NAME]`, `[EMAIL]`)
- **Hash**: Einweg-Hash-Verschlüsselung
- **Encrypt**: Verschlüsselung (konfigurierbar)

#### Verarbeitungs-Pipeline
```
Dokument → PII-Erkennung → Maskierung → Indexierung → Verarbeitung
         ↓
    Audit-Log
```

### 2. Datenlokalisierung

- ✅ **100% Offline**: Keine Abhängigkeit von Cloud-Diensten
- ✅ **Lokale LLM-Inferenz**: Ollama läuft auf Ihrer Infrastruktur
- ✅ **Lokale Vektordatenbank**: ChromaDB speichert Daten lokal
- ✅ **Keine externe Kommunikation**: Keine API-Calls zu externen Diensten

### 3. Zugriffskontrolle

- ✅ **Dateisystem-Berechtigungen**: ChromaDB-Datenbank mit Zugriffskontrollen
- ✅ **API-Authentifizierung**: Konfigurierbare Authentifizierung (erweiterbar)
- ✅ **Audit-Logging**: Vollständige Protokollierung aller Zugriffe

### 4. Verschlüsselung

- ✅ **Datenbank-Verschlüsselung**: ChromaDB unterstützt Verschlüsselung auf Dateisystemebene
- ✅ **Transport-Verschlüsselung**: HTTPS für API-Kommunikation (konfigurierbar)
- ✅ **Maskierte Speicherung**: PII wird maskiert in der Datenbank gespeichert

## 📊 Verarbeitungsregister (Artikel 30 DSGVO)

ARES unterstützt die Erstellung eines Verarbeitungsregisters durch:

### Automatische Protokollierung
- **Dokument-Upload**: Zeitstempel, Dateiname, PII-Erkennung
- **Abfragen**: Zeitstempel, Abfrageinhalt, verwendete Dokumente
- **PII-Verarbeitung**: Anzahl erkannte Entitäten, Maskierungsstrategie
- **Löschungen**: Zeitstempel, gelöschte Dokument-ID

### Audit-Logs
Alle Verarbeitungsschritte werden in strukturierten Logs erfasst:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event": "document_uploaded",
  "document_id": "uuid",
  "pii_detected": 5,
  "pii_masked": true,
  "chunks_created": 42
}
```

## 🔐 Betroffenenrechte (Kapitel III DSGVO)

### Recht auf Auskunft (Artikel 15)
- ✅ **Dokumenten-Status**: Abfrage welche Dokumente indexiert sind
- ✅ **PII-Erkennung**: Audit-Berichte über erkannte personenbezogene Daten
- ✅ **Verarbeitungsprotokolle**: Zugriff auf Audit-Logs

### Recht auf Berichtigung (Artikel 16)
- ✅ **Dokument-Update**: Neues Dokument mit korrigierten Daten hochladen
- ✅ **Löschung und Neu-Indexierung**: Altes Dokument löschen, korrigiertes neu indexieren

### Recht auf Löschung (Artikel 17)
- ✅ **Vollständige Löschung**: `DELETE /api/v1/documents/{document_id}`
- ✅ **Chunk-Entfernung**: Alle zugehörigen Chunks werden entfernt
- ✅ **BM25-Index-Update**: Keyword-Index wird aktualisiert

### Recht auf Einschränkung (Artikel 18)
- ✅ **Dokument-Deaktivierung**: Dokument kann aus Suchindex entfernt werden
- ✅ **PII-Maskierung**: Erhöhte Maskierung für bestimmte Dokumente

### Recht auf Datenübertragbarkeit (Artikel 20)
- ✅ **Datenexport**: ChromaDB-Daten können exportiert werden
- ✅ **Strukturierte Formate**: JSON-Export von Dokumenten-Metadaten

### Widerspruchsrecht (Artikel 21)
- ✅ **Opt-out PII-Verarbeitung**: PII-Maskierung kann deaktiviert werden
- ✅ **Selektive Verarbeitung**: Bestimmte Dokumente können ausgeschlossen werden

## 🔍 Datenschutz-Folgenabschätzung (DSFA)

### Risikobewertung

#### Geringes Risiko
- ✅ **Lokale Verarbeitung**: Keine Datenübertragung ins Ausland
- ✅ **Maskierung**: PII wird vor Verarbeitung maskiert
- ✅ **Kontrollierte Umgebung**: Verarbeitung auf eigener Infrastruktur

#### Maßnahmen zur Risikominimierung
1. **PII-Maskierung standardmäßig aktiviert**
2. **Regelmäßige Audit-Logs-Überprüfung**
3. **Zugriffskontrollen auf Datenbankebene**
4. **Verschlüsselung der gespeicherten Daten**

## 📝 Vertragsgestaltung (Artikel 28 DSGVO)

### Auftragsverarbeitung

Falls ARES als Dienstleistung bereitgestellt wird, sollten folgende Punkte im Auftragsverarbeitungsvertrag (AVV) geregelt werden:

1. **Gegenstand und Dauer der Verarbeitung**
   - Indexierung und Suche in Unternehmensdokumenten
   - Laufzeit: Vertragslaufzeit

2. **Art und Zweck der Verarbeitung**
   - Dokumentenanalyse und -suche
   - PII-Erkennung und -maskierung

3. **Art der personenbezogenen Daten**
   - Namen, E-Mail-Adressen, Telefonnummern, IBANs, Adressen
   - (Alle werden maskiert verarbeitet)

4. **Kategorien betroffener Personen**
   - Mitarbeiter, Kunden, Geschäftspartner
   - (Abhängig von den indexierten Dokumenten)

5. **Technische und organisatorische Maßnahmen**
   - Siehe Abschnitt "Technische Maßnahmen" oben

## 🚨 Meldepflichten (Artikel 33, 34 DSGVO)

### Datenschutzverletzungen

ARES unterstützt die Erkennung und Meldung von Datenschutzverletzungen:

- ✅ **Audit-Logs**: Vollständige Protokollierung für Forensik
- ✅ **Anomalie-Erkennung**: Ungewöhnliche Zugriffsmuster können erkannt werden
- ✅ **Export-Funktionen**: Logs können für Meldungen exportiert werden

### Meldeprozess
1. **Erkennung**: Ungewöhnliche Aktivitäten in Audit-Logs
2. **Dokumentation**: Export relevanter Log-Einträge
3. **Meldung**: An Aufsichtsbehörde (innerhalb 72 Stunden)
4. **Benachrichtigung**: An betroffene Personen (wenn erforderlich)

## ✅ Konformitäts-Checkliste

### Technische Maßnahmen
- [x] Lokale Verarbeitung (keine Cloud-Abhängigkeit)
- [x] Automatische PII-Erkennung
- [x] PII-Maskierung vor Verarbeitung
- [x] Verschlüsselung der gespeicherten Daten
- [x] Zugriffskontrollen
- [x] Audit-Logging
- [x] Löschfunktionen

### Organisatorische Maßnahmen
- [x] Dokumentation der Verarbeitungszwecke
- [x] Verarbeitungsregister (durch Audit-Logs)
- [x] Datenschutz-Folgenabschätzung
- [x] Verfahrensdokumentation

### Betroffenenrechte
- [x] Auskunftsrecht (Abfrage-Funktionen)
- [x] Löschrecht (DELETE-Endpoint)
- [x] Widerspruchsrecht (PII-Maskierung deaktivierbar)
- [x] Datenübertragbarkeit (Export-Funktionen)

## 📞 Kontakt

Bei Fragen zur DSGVO-Konformität von ARES wenden Sie sich bitte an:

- **Technischer Support**: Siehe README.md
- **Datenschutzbeauftragter**: Kontaktieren Sie Ihren internen Datenschutzbeauftragten

## 📚 Weitere Ressourcen

- [DSGVO-Text (EUR-Lex)](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32016R0679)
- [BfDI - Bundesbeauftragter für den Datenschutz](https://www.bfdi.bund.de/)
- [Microsoft Presidio Dokumentation](https://microsoft.github.io/presidio/)

---

**Stand**: Januar 2024  
**Version**: 1.0.0  
**Gültig für**: ARES v1.0.0

---

*Diese Dokumentation dient als Leitfaden zur DSGVO-Konformität. Für eine rechtsverbindliche Bewertung konsultieren Sie bitte einen Datenschutzbeauftragten oder Rechtsanwalt.*
