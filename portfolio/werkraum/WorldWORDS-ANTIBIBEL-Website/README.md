# WorldWORDS ANTIBIBEL Website

Produktive, dreisprachige Website für ein offenes Wortregister mit Herkunft, Diskussion und sichtbarer kuratorischer Entscheidung.

## Grundvertrag

- Jeder Mensch kann Begriffe, Quellen, Deutungen, Übersetzungen, Varianten und Verkörperungen beitragen.
- Eine Einreichung erhält sofort eine öffentliche, diskutierbare Begriffsseite.
- Daniel ist Gründungskurator und entscheidet sichtbar, welche Begriffe in sein offizielles Register aufgenommen werden.
- Eingereicht, in Prüfung, aufgenommen, zurückgestellt, nicht aufgenommen und als Variante verbunden sind dauerhafte, diskutierbare Zustände.
- Rohform und ursprüngliche Eingabe werden nicht still überschrieben. Korrekturen wachsen als neue, benannte Provenienzereignisse an.
- Die Oberfläche ist Deutsch, Englisch und Spanisch. Ursprungssprachen können zusätzlich sprachübergreifend oder ungeklärt sein.

## Technischer Körper

- Django 5.2 / PostgreSQL / Gunicorn / Nginx
- serverseitig gerenderte, progressive Oberfläche ohne JavaScript-Zwang für Kernfunktionen
- Argon2-Passwörter, CSRF-Schutz, strikte Content Security Policy und POST-basierte Login-Drossel
- sanitisiertes Markdown für Diskussionen
- append-only Provenienzereignisse und revisionsfähige Beiträge
- atomarer öffentlicher JSON-Export
- tägliche PostgreSQL-, Medien- und Export-Backups mit SHA-256-Prüfung
- Playwright-Lebenswegtests und Axe/WCAG-Zugänglichkeitsprüfung

## Lokaler Start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# PostgreSQL-Datenbank und Rolle entsprechend .env anlegen
.venv/bin/python manage.py migrate
.venv/bin/python manage.py import_open_source --source /pfad/zur/WorldWORDS-ANTIBIBEL-Open-Source
.venv/bin/python manage.py runserver
```

Die produktive Installation nutzt einen Pfadpräfix. Lokal kann `DJANGO_FORCE_SCRIPT_NAME` leer gesetzt werden.

## Prüfungen

```bash
.venv/bin/python manage.py test lexicon
npm ci
npm run test:e2e
npm run test:a11y
```

Die Browserprüfungen verwenden standardmäßig die produktive URL. Testkonten und Testbegriffe werden nach dem Lauf wieder entfernt.

## Lizenzen

- Programmcode: MIT, siehe `LICENSE`
- öffentliche Inhalte und strukturierte Daten: CC BY-SA 4.0, siehe `LICENSE-CONTENT.md`
- einzelne Beiträge können abweichende, sichtbar dokumentierte Rechte tragen
