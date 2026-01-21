# MD Web-App (Prototyp)

Web-Applikation für die Verwaltung von Mitarbeitergesprächen im Kanton Zürich.

## Features

- 🔐 Token-basierte Authentifizierung
- 👥 Führungskräfte sehen nur ihre Direct Reports
- 📝 Gespräche erfassen und bearbeiten
- 📄 PDF-Generierung im Kanton ZH Design
- 📊 Übersicht und Statistiken

## Tech Stack

- **Backend:** Python Flask
- **Frontend:** HTML, CSS, JavaScript
- **Daten:** CSV-basiert
- **PDF:** ReportLab

## Installation

### Voraussetzungen
- Python 3.11+
- pip

### Setup

1. Repository klonen:
```bash
git clone https://github.com/DEIN-USERNAME/mitarbeitergespraeche.git
cd mitarbeitergespraeche
```

2. Dependencies installieren:
```bash
cd server
pip install -r requirements.txt
```

3. Daten initialisieren:
```bash
python setup_data.py
```

4. Tokens generieren:
```bash
python generate_tokens.py
```

5. Server starten:
```bash
python app.py
# oder
start_server.bat
```

6. Browser öffnen:
```
http://localhost:5000
```

## Projektstruktur
```
mitarbeitergespraeche/
├── server/
│   ├── app.py                  # Flask Server
│   ├── setup_data.py           # Daten-Setup
│   ├── generate_tokens.py      # Token-Generator
│   ├── requirements.txt        # Dependencies
│   └── start_server.bat        # Start-Script
├── data/
│   ├── stammdaten.csv          # Mitarbeitende
│   ├── gespraeche.csv          # Gespräche
│   ├── tokens.csv              # Tokens (nicht in Git!)
│   └── pdf_export/             # PDFs (nicht in Git!)
├── app/
│   ├── index.html              # Login
│   ├── dashboard.html          # Dashboard
│   ├── gespraech.html          # Gespräch bearbeiten
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── utils.js
└── README.md
```

## Verwendung

### Als Führungskraft
1. Token per Email erhalten
2. Link öffnen: `http://server:5000?token=DEIN_TOKEN`
3. Gespräche bearbeiten
4. PDF generieren

### Als HR
1. HR Master-Token verwenden
2. Alle Gespräche einsehen
3. Tokens verwalten

## Sicherheit

- Tokens sind wie Passwörter zu behandeln
- `tokens.csv` nie in Git committen
- Bei Verdacht auf Kompromittierung: Tokens neu generieren

## Entwickelt für

Kanton Zürich - HR Team

## Lizenz


Intern - Nicht für öffentliche Nutzung
