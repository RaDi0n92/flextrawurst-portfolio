---
titel: Toolbox (flextrawurst.de/toolbox)
typ: system
erstellt: 2026-07-10
aktualisiert: 2026-08-13
autor: claude-code bei Daniels VPS
---

# Toolbox — `flextrawurst.de/toolbox`

[[INDEX|← Index]]

*Acht Werkzeuge, ein Login, ein gemeinsamer Textkreislauf zwischen allen.*

---

## Was das ist

`https://flextrawurst.de/toolbox` (bis 2026-08-13 unter `/tts` erreichbar — der Name
"TTS" passte längst nicht mehr, siehe Nachtrag "Umzug" unten) ist eine einzige
Single-Page-App mit acht Werkzeug-Tabs: **TTS**, **Soundboard**, **Diktat**,
**Übersetzen**, **OCR**, **Dokumente**, **Webarchiv**, **Datei-Wandler**.

Backend: FastAPI-Service `tts_service.py` (systemd `tts-service.service`, Port 8035,
WorkingDirectory `/root/werkraum/welt` — der interne Servicename blieb bewusst
unverändert, nur die nach außen sichtbare URL zog um). Frontend: einzelne Datei
`/root/werkraum/welt/tts_ui.html` (wird bei jedem `GET /` frisch von der Platte
gelesen — kein Service-Neustart nötig nach reinen Frontend-Änderungen, nur bei
Python-Änderungen in `tts_service.py`). nginx (`/etc/nginx/sites-available/flextrawurst`)
proxyt `/toolbox/` → `localhost:8035/`.

---

## Zugang & Absicherung

Komplett per HTTP-Basic-Auth geschützt (`/etc/nginx/.htpasswd_tts`, Nutzer `daniel`,
Passwort nirgends in Doku/Notizen/Git festgehalten) — seit 2026-07-10, vorher war die
Seite öffentlich ohne jeden Schutz erreichbar.

**Crawler-Zugangsschlüssel:** ein zweiter, vom Login-Passwort unabhängiger Geheim-Schlüssel
als URL-Parameter (`?key=<TOKEN>`) umgeht die Basic-Auth komplett — für LLM-Crawl-Tools, die
keine Zugangsdaten mitschicken können. nginx prüft den Parameter über `map $arg_key
$tts_key_ok {...}` in `/etc/nginx/conf.d/tts-crawl-key.conf`. Token liegt in
`/root/werkraum/welt/.env.tts_crawl_key` (chmod 600), tab-übergreifender Button
"🔑 Crawler-Zugang" zeigt die fertige URL, jederzeit rotierbar (Passwort dafür: eigene
Variable `TTS_CRAWL_ROTATE_PASSWORD`, Backend-Endpunkt `POST /crawl-key/rotate`).

**Sicherheitsabwägung, mit Daniel besprochen:** der Schlüssel ist faktisch ein zweiter
Generalschlüssel zum Datei-Wandler (beliebiger Lesezugriff auf `/root/werkraum`,
`/root/visionen`) — sobald er einem LLM-Tool gegeben wird, kann er in dessen Logs landen.
Kein technischer Kompromiss dagegen, nur Daniels bewusste Entscheidung, das für den
Anwendungsfall in Kauf zu nehmen.

---

## Der gemeinsame Faden: die Textablage

Sechs der acht Tabs (TTS, OCR, Dokumente, Übersetzen, Webarchiv — Soundboard und Diktat
haben ihre eigenen, ähnlichen Bibliotheken) teilen sich einen Mechanismus namens
**Textablage** (`TEXT_VAULT_KEY`, `localStorage`-basiert): jeder dieser Tabs hat einen
Kasten "Aktuellen Text nach: TTS / Soundboard / OCR / Dokument / Übersetzen / Webarchiv /
Ablage" — ein Klick schiebt den gerade sichtbaren Text direkt in den Zieltab, ohne
Copy-Paste. Zusätzlich kann jeder Text mit Titel+Tags in eine gemeinsame Ablage-Liste
gelegt werden, die über alle Tabs hinweg durchsuchbar bleibt.

Das ist der eigentliche Kern dessen, was aus "TTS" eine "Toolbox" gemacht hat: kein
Werkzeug für sich allein, sondern ein Kreislauf — ein Snapshot aus dem Webarchiv landet im
Dokumente-Chat, dessen Antwort im Übersetzer, die Übersetzung wird von einer Stimme
gesprochen, alles ohne die Seite zu verlassen.

---

## Die acht Tabs im Einzelnen

### 1. TTS

Der ursprüngliche Kern. Textfeld bis 1.111.111 Zeichen, Live-Zeichenzähler,
Token-Schätzung, Lesetempo x0.25 bis x4, Wiedergabe mit Play/Pause/Stopp und Seek-Leiste.

**Technik:** Microsofts Edge-TTS (Neural-Voice-API), Standardstimme
`de-DE-FlorianMultilingualNeural`. Text wird in ~280-Zeichen-Häppchen geschnitten und
einzeln angefragt (siehe `_claude/spiegel/2026-06-18-tts-session.md`) — Microsoft drosselt
Datacenter-IPs, die einen langen Text auf einmal schicken, massiv (38,6s für 2800 Zeichen
in einem einzelnen Request); viele kurze Anfragen à ~1s umgehen das zuverlässig.

### 2. Soundboard

Bibliothek gespeicherter Text-Eingaben mit eigenen Kategorien ("Container", die Daniel
selbst anlegt), pro Eintrag: Titel, Text, Stimme, Tempo, Tags, Notiz, Favoriten-Stern.
Volltextsuche über Titel/Text/Kategorie/Stimme/Tags/Notiz. Aktionen pro Eintrag: laden,
abspielen, duplizieren, als MP3/WAV exportieren, löschen. Zusätzlich: Batch-MP3-Export für
mehrere ausgewählte Einträge auf einmal, JSON-Export/-Import der ganzen Bibliothek, Offline-
HTML-Export (eine eigenständige HTML-Datei, die ohne Server funktioniert).

**Persistenz:** `localStorage` (sofort) + Server-Sync (`GET`/`PUT /library`,
`tts_library.json`, atomic write) — zwei Geräte teilen sich dieselbe Bibliothek.

### 3. Diktat (neu, 2026-08-13)

Browsereigene Spracherkennung (`SpeechRecognition`/`webkitSpeechRecognition`, `de-DE`),
läuft komplett im Browser, kein Cloud-Umweg fürs Erkennen selbst. Start/Stopp-Button, Live-
Text im Feld, Kopieren-Button, optionales Speichern mit Kategorie (gleiche Container-Logik
wie Soundboard, eigene Bibliothek).

**Geräteübergreifender Entwurf:** was gerade im Feld steht, wird alle 1,2s zum Server
gesichert (`draft`-Feld in `tts_diktat_library.json`) — auf einem zweiten Gerät geladen,
steht der Text sofort da. Entstanden aus Daniels eigenem Vorschlag, nachdem direktes
Diktieren am Laptop an zwei verschiedenen strukturellen Browser-Grenzen scheiterte
(Chromium ohne Google-API-Schlüssel, Firefox ohne funktionierenden Erkennungsdienst trotz
aktiviertem Feature-Flag) — Details in
`docs/2026-08-13_diktat_stimme_bericht.md`.

**Bekannte Grenze:** keine automatische Interpunktion — die Browser-API liefert rohen
erkannten Text ohne Grammatik-Analyse. Kein Bug, sondern eine Eigenschaft der
zugrundeliegenden Web-Speech-API selbst.

→ Volle Geschichte: `docs/2026-08-13_diktat_stimme_bericht.md`.

### 4. Übersetzen

Eigener Textbereich, unabhängig vom TTS-Hauptfeld. Zielsprache wählbar aus allen Sprachen,
für die Edge-TTS eine passende Stimme hat (Übersetzung und Vorlesen sind bewusst an
dieselbe Stimmen-Datenbank gekoppelt — jede übersetzte Sprache lässt sich direkt auch
sprechen). Eigene Stimmenauswahl pro Zielsprache, mit persönlichen Favoriten (getrennt
gespeichert je Sprache), "3 Stimmen vergleichen"-Funktion, Auto-Übersetzen-Umschalter.

**"Alle Sprachen auf einmal"**: ein zweiter Modus (`/translate-all`, bis 1800 Zeichen)
übersetzt denselben Text parallel in *alle* verfügbaren Zielsprachen gleichzeitig (mit
Nebenläufigkeits-Begrenzung), nicht nur eine.

**Technik:** Google-Translate-Scraping-Client (`_google_translate_chunk`), Ergebnisse
gecacht (`tts_translation_cache.json`, Cache-Key aus Text+Quell+Zielsprache) — dieselbe
Übersetzung wird nie zweimal wirklich angefragt.

### 5. OCR

Text aus Bildern oder PDFs extrahieren. PDFs mit eingebettetem Text werden direkt gelesen;
Bild-OCR und PDFs *ohne* eingebetteten Text brauchen `tesseract-ocr` auf dem Server — der
Status wird direkt im Tab angezeigt (`GET /ocr/status`, prüft `shutil.which("tesseract")`).
Sprachauswahl Auto/Deutsch/Englisch. Ergebnis landet in einem bearbeitbaren Textfeld,
danach über die Textablage in jedes andere Werkzeug weiterreichbar.

### 6. Dokumente

Mehrere Dateien auf einmal hochladen (bis 50 pro Vorgang), Text wird extrahiert und in
Chunks zerlegt (damit Suche/Chat nicht den ganzen Text auf einmal in ein Modell kippen
müssen). Volltextsuche über die Chunks. **Chat mit den Dokumenten**: eine Frage wird gegen
ein lokales Ollama-Modell (Modellwahl automatisch oder manuell) mit den relevanten Chunks
als Kontext beantwortet — echtes RAG, kein reines Volltext-Grep.

**Scope**: eine Auswahl bestimmter Dokumente einschränkt Suche und Chat auf genau diese,
leerer Scope bedeutet alle Dokumente durchsuchen.

### 7. Webarchiv

Snapshot einer URL speichern — Roh-HTML *und* extrahierter Text werden beide behalten.
Seitenanzahl > 1 crawlt intern innerhalb derselben Domain weiter. Zwei Render-Modi:
"HTTP-HTML" (schneller, sieht nur was der Server roh ausliefert) oder
"Browser-gerendert" (langsamer, sieht auch was JavaScript nachträglich einfügt).

**Vergleichs-Funktion**: zwei Snapshots derselben oder verschiedener Zeitpunkte lassen sich
gegeneinander diffen (`POST /webarchive/compare`) — was wurde hinzugefügt, entfernt,
geändert, seit der letzte Snapshot gemacht wurde.

### 8. Datei-Wandler

VPS-Pfade oder eigene Uploads → Offline-HTML/Markdown/ZIP-Export. Ursprünglich ein
eigenständiger Dienst (Port 8878, eigener Login, unter `[SERVER-IP]:8449` erreichbar),
2026-07-10 zusätzlich in die Toolbox eingehängt ("mit allem was er kann"). Backend
unverändert, nur zusätzlich über `/toolbox/dateiwandler/` erreichbar (nginx-Proxy, gleiche
Timeouts/Body-Limits wie die alte Route). Die alte, separate Route läuft unabhängig weiter.

---

## Tab-Mechanik (technisch, für künftige neue Tabs)

Rein clientseitig, generisch: `[data-tab-target]`-Buttons und `[data-tab-panel]`-Sections
werden per `querySelectorAll` eingesammelt, ein gemeinsamer Klick-Handler schaltet
`.on`-Klassen um. Aktiver Tab landet in `localStorage` und im URL-Parameter `?tab=`.

**Wichtig für neue Tabs:** der Tab-Name muss zusätzlich in drei fest kodierten
Whitelist-Arrays stehen (`renderTabState`, `setTab`, `currentTab` — alle drei identisch),
sonst fällt die Routing-Logik beim Laden/Persistieren stumm auf `'tts'` zurück, auch wenn
der Klick-Handler selbst generisch ist.

---

## Bekannte offene Punkte

- Ungenutzte Backend-Routen für Logs/Formulare (`/logs/*`, `/forms/*` in
  `tts_service.py`) sind weiterhin nicht entfernt — nur der UI-Zugang fehlt seit 2026-07-10.
  Kein Sicherheits- oder Funktionsrisiko (nichts verlinkt mehr dorthin), aber totes Gewicht
  im Server-Code. Kein Auftrag dafür bisher.
- Crawler-Schlüssel-Rotation ist ein manueller Zwei-Dateien-Vorgang (`.env.tts_crawl_key` +
  `conf.d/tts-crawl-key.conf`), kein automatisiertes Tooling dafür.

---

## Nachtrag 2026-08-13: Umzug von `/tts` auf `/toolbox`

Daniels Auftrag, wörtlich: *"setzt ma den /tts weg und mach taraus flextrawurst.de/toolbox
und auch genau so abgesichert wie bisher"*. Der Name "TTS" passte längst nicht mehr — das
war schon am 2026-07-10 Daniels eigene Einschätzung ("eine scheiß Benennung für das, was
jetzt mittlerweile auf dieser Domain gebastelt wurde").

**Geändert:**
- Alle drei nginx-Locations (`= /toolbox`, `/toolbox/`, `/toolbox/dateiwandler/`) —
  Login-Schutz und Crawler-Schlüssel-Mechanik unverändert übernommen, nur der Pfad.
- Alle hartcodierten `/tts/`-Pfade im Frontend (Datei-Wandler-Formular und -Fetches,
  Crawler-Key-URL-Bauer, `/crawl-key/rotate`-Aufruf) und im Backend (`crawl_url` im
  Rotations-Endpunkt) auf `/toolbox/` nachgezogen.
- `<title>`/`<h1>` von "TTS" auf "Toolbox" geändert.

**Bewusst NICHT geändert:** interner Servicename (`tts-service.service`), Dateinamen
(`tts_service.py`, `tts_ui.html`, `tts_library.json` usw.), `.htpasswd_tts`,
`tts-crawl-key.conf` — nur die nach außen sichtbare URL und die im Frontend sichtbaren
Texte. Eine vollständige interne Umbenennung war nicht Teil des Auftrags.

**Alte URL:** `/tts/` liefert jetzt bewusst 404, kein Redirect wurde beibehalten — alte
Lesezeichen oder geteilte Crawler-Links (inklusive der alten `?key=`-URL) funktionieren
nicht mehr, neue müssen verteilt werden.

**Verifiziert:** `nginx -t` sauber, alle drei Locations live getestet (401 ohne Login, 301
bei fehlendem Slash, 200 mit Crawler-Key), ausgeliefertes HTML frei von Alt-Pfaden,
`/library`, `/diktat-library` und `/dateiwandler/` über den neuen Pfad erreichbar.

---

*Weiter: [[23_umgekehrte_neugier]] | [[INDEX]]*
