# LLM Tree

**Dokumentation:** [🇺🇸 English](../README.md) | [🇷🇺 Русский](RU.md) | [🇩🇪 Deutsch](DE.md) | [🇯🇵 日本語](JA.md) | [🇨🇳 中文](CH.md)

Ein CLI-Tool zur Vorbereitung von Projektdaten für die Verwendung im LLM-Kontext. Es generiert eine Markdown-Datei mit der Projektstruktur und dem Inhalt der Quelldateien.

## Installation

```bash
pip install -e .
```

Oder für die globale Installation:

```bash
pip install llmtree
```

## Schnellstart

```bash
# Aktuelles Verzeichnis verarbeiten
llmtree .

# Einen bestimmten Ordner verarbeiten
llmtree /path/to/project

# Ein bestimmtes Profil verwenden
llmtree . -p python

# Profile konfigurieren
llmtree --config
```

## Hauptfunktionen

### Profile

* **default** – universelles Profil für die meisten Projekte
* **python** – optimiert für Python-Projekte
* Eigene Profile über ein interaktives Menü erstellen

### Interaktive Nutzung

Beim Ausführen von `llmtree .`:

* **Enter** – generiert die Datei `4llm.md`
* **Leertaste** – öffnet das Einstellungsmenü

### Profileinstellungen

* Einschlussmuster für Dateien
* Ausschlussmuster
* Einbeziehen der Baumstruktur
* Maximale Dateigröße
* Zeilennummerierung
* Benutzerdefinierter Header und Footer

## Konfigurationsstruktur

Die Einstellungen werden gespeichert unter `~/.llmtree/config.json`:

```json
{
  "default": {
    "name": "default",
    "include_patterns": ["*.py", "*.js", "*.md"],
    "exclude_patterns": ["node_modules/*", ".git/*"],
    "include_tree": true,
    "max_file_size": 100000,
    "encoding": "utf-8",
    "add_line_numbers": false,
    "include_hidden": false,
    "tree_depth": 3,
    "custom_header": "",
    "custom_footer": ""
  }
}
```

## Anwendungsbeispiele

### Ein Profil für Frontend erstellen

```bash
llmtree --config
# Wählen Sie "Create new profile"
# Name: frontend
# Include patterns: *.js,*.jsx,*.ts,*.tsx,*.vue,*.css,*.scss,package.json
# Exclude patterns: node_modules/*,dist/*,build/*
```

### Profil für Dokumentation

```bash
llmtree --config
# Erstellen Sie ein Profil namens "docs"
# Include patterns: *.md,*.rst,*.txt
# Baumstruktur: Ja
# Zeilennummerierung: Nein
```

## Kommandozeile

```
usage: llmtree [-h] [-p PROFILE] [-o OUTPUT] [--config] [path]

positionale Argumente:
  path                   Pfad zum Zielverzeichnis (Standard: aktuelles Verzeichnis)

optionale Argumente:
  -h, --help             Hilfe anzeigen und beenden
  -p, --profile PROFILE  Zu verwendendes Profil (Standard: default)
  -o, --output OUTPUT    Name der Ausgabedatei (Standard: 4llm.md)
  --config               Interaktive Konfiguration starten
```

## Ausgabeformat

Die generierte Datei `4llm.md` enthält:

1. Benutzerdefinierter Header (falls angegeben)
2. Projektstruktur (Baum)
3. Inhalt der Quelldateien mit Syntaxhervorhebung
4. Benutzerdefinierter Footer (falls angegeben)

Beispielausgabe:

```markdown
## Projektstruktur

```

.
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test\_main.py
└── README.md

````

## Quelldateien

### src/main.py
```python
def main():
    print("Hello, World!")
````

### README.md

```markdown
# Mein Projekt
```

## Lizenz

MIT-Lizenz
