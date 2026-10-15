EVIDENCE_VERSION: 1

# Flextrawurst Exporter — MV3-Erweiterung

## Aktion

Eine eigene Chromium-MV3-Erweiterung wurde unter `/root/werkraum/tools/flextrawurst-exporter-extension/` gebaut. Sie liest nach Nutzerklick den sichtbaren DOM-Inhalt der unterstützten Provider und projiziert ihn als JSON, Markdown, Text, CSV oder PDF. Die PDF hat eine feste harmonische Fünffarben-Palette: Lila, Flieder, Bubblegum-Pink, Giftgrün und Dunkelgrün gemeinsam in einer Datei.

## Sichtbar

- Extension-Popup: `chrome-extension://ahohinjcghjbedigenfkfdhnjkbmcdkg/popup.html`
- Titel: `Flextrawurst Exporter`
- Screenshot: `/tmp/ftw-exporter-extension-popup.png`
- Chromium lud Manifest, Popup und Background-Service-Worker erfolgreich.
- Das Popup zeigt die fünf Farbfelder gemeinsam als feste Palette; es gibt keine auswählbaren PDF-Theme-Radios.
- Sichtbare Palette im DOM: fünf `.swatch`-Elemente, `input[name="theme"]` ist nicht vorhanden, Beschriftung `ALLE FÜNF FARBEN · EINE HARMONISCHE PDF`.
- Sichtbare Grenze: `OFFLINE-PROJEKTION · KEIN PROVIDER-FETCH · HERKUNFT BLEIBT SICHTBAR`.

## Rücklese

- `manifest.json` ist gültiges Manifest V3.
- `node --check` bestand für `content.js`, `background.js` und `popup.js`.
- Chromium-Rücklese: Service Worker geladen, Popup-Titel korrekt, fünf Farben und fünf Formate im DOM, keine Popup-Page-Errors.
- Erweiterungs-Injektions-Smoke: Ein provider-identischer HTTPS-Testtab erhielt das Content-Script; beide sichtbaren Turns wurden als `user` und `assistant` gelesen.
- PDF-Smoke-Rücklese im Speicher: `%PDF-1.4`-Header, XRef, `%%EOF`, fünf Objekte und monotone Byte-Offsets vorhanden.
- Der Code liest nur nach bewusstem Klick den sichtbaren DOM, erzeugt lokale Bytes, berechnet Quell-/Artefakt-Hashes und ruft `chrome.downloads.download` einmal auf.
- `background.js` beobachtet `chrome.downloads.onChanged` und persistiert `in_progress`, `complete` oder `interrupted` in `chrome.storage.local`.
- Backup-Checkpoint vor dem Selektor-/Live-Smoke-Schritt: `73ccd21e4`.
- Echter Provider-Live-Lauf in einer getrennten Kopie des vorhandenen Chromium-Profils: ChatGPT-Unterhaltung `Work Fortschritt bewerten`, URL `https://chatgpt.com/c/6a89c4f2-a10c-83ed-af07-f5128f8ad20d`, Titel aus der Seite gelesen, Popup meldete `10 sichtbare Nachrichten`.
- Echter Popup-Export: Format `pdf`, feste Palette `flextrawurst-5farben-harmonisch`, Download-ID `141`; `chrome.storage.local` meldete `state: complete`, Dateiname `ftw-live-chatgpt-5farben.pdf`, `byteCount: 39427`.
- Fertige Datei zurückgelesen: `/tmp/playwright-artifacts-Ss9HDq/972a2827-27fd-45a2-a99a-ea496f63f8c1`, 39.427 Bytes, SHA-256 `88da0f80ef75f6c16995a49278691b3b5aceaf1365852c944da468e2570dddfb`; `%PDF-1.4`, `/Type /Catalog` und `%%EOF` vorhanden. Im PDF-Stream sind alle fünf Palette-RGB-Werte enthalten: Lila `0.6078 0.3490 0.7137`, Flieder `0.7843 0.6353 0.7843`, Bubblegum-Pink `1.0000 0.4353 0.7098`, Giftgrün `0.2235 1.0000 0.0784`, Dunkelgrün `0.0431 0.3647 0.1176`.
- Der Live-Lauf verwendete ausschließlich die Profilkopie unter `/tmp/ftw-chromium-export.SLvEwy`; das laufende Chromium und der pausierte Recorder wurden nicht verändert.
- Nach Rückmeldung „wird nie heruntergeladen“ wurde der Speichern-Dialog entfernt: `saveAs: false` legt den Export automatisch im normalen Chromium-Downloads-Ordner ab. Ein isolierter `chrome.downloads`-Rücklesetest meldete `state: complete`, `15/15` Bytes und las die fertige Datei vom tatsächlichen Downloadpfad zurück.
- Finaler echter ChatGPT-Lauf nach der Korrektur: `ftw-final-auto-chatgpt.pdf`, Download-ID `141`, Status `complete`, `39427/39427` Bytes, tatsächlicher Pfad `/tmp/playwright-artifacts-VPlMaa/a61a685d-9f5d-4323-8980-e3ee9fe89cea`, SHA-256 `88da0f80ef75f6c16995a49278691b3b5aceaf1365852c944da468e2570dddfb`, `%PDF-1.4` und `%%EOF` vorhanden.
- Lauf im echten laufenden Chromium-Profil: beide Service-Worker sichtbar, ChatGPT-Tab aktiv, PDF-Export mit Chromium-Standard-Downloadverhalten abgeschlossen. Datei `/config/Downloads/ftw-no-override-check.pdf`, 39.427 Bytes, SHA-256 `88da0f80ef75f6c16995a49278691b3b5aceaf1365852c944da468e2570dddfb`, `complete` und erwarteter Dateiname.
- Nach Daniels Rückmeldung zur fehlerhaften Markdown-Datei wurde der ChatGPT-Extraktor korrigiert: äußere `section[data-testid^="conversation-turn-"][data-turn]`-Knoten sind jetzt die einzige bevorzugte Quelle, `data-turn` ist für die Rolle maßgeblich, DOM-Reihenfolge bleibt erhalten und leere Wrapper fallen weg. Die alte Sammlung erzeugte durch innere plus äußere Knoten Duplikate und eine falsche Reihenfolge.
- Live-Rücklese nach dem Rollen-/Ordnungsfix: stabil sichtbarer ChatGPT-DOM lieferte `6` echte Nachrichten aus `7` äußeren Turn-Sections; der erste leere technische Wrapper wurde nicht exportiert. Reihenfolge und Rollen: Mensch, ChatGPT, Mensch, ChatGPT, Mensch, ChatGPT.
- Echter Markdown-Export nach dem Fix: Download-ID `145`, Status `complete`, Dateiname `ftw-corrected-chatgpt.md`, `9.100` Bytes, SHA-256 `8dc9987fcc651dbdb489dfc09dcfe932b5c1cbe128d96db3c61b6c3734a2e3c8`. Das Artefakt wurde aus dem Popup rückgelesen; die Rollenüberschriften lauten nun ausdrücklich `## Mensch` und `## ChatGPT`.
- Manueller Vollverlaufs-Lauf: Nach dem ersten sichtbaren Lesen sammelte der Content-Script-Observer nur während der aktiven Nutzeraktion weitere sichtbar geladene Turns; nach manuellem Verlaufslauf und zweitem Klick meldete das Popup `17 sichtbare Nachrichten`. Der Observer scrollt, klickt und navigiert nicht selbst.
- Zweiter echter Markdown-Export: Download-ID `146`, Status `complete`, Dateiname `ftw-manual-full-chatgpt.md`, `26.262` Bytes, SHA-256 `ef0daf163bce45b4ec1e076c7b4ee63d6cb8041ebadd1c0a44f77fcda412e2e2`; Rücklese ergab `17` Nachrichtenüberschriften in der Folge `Mensch`/`ChatGPT` mit den realen Gesprächsabweichungen (z. B. mehrere Menschen-Turns hintereinander).

## Offen / Unbekannt

- Die echte ChatGPT-Abnahme mit der gemeinsamen Fünffarben-PDF ist für diesen Lauf erledigt; noch nicht separat abgenommen sind die vier anderen Provider-Live-DOMs. Der neue Markdown-Lauf belegt die korrekte sichtbare Reihenfolge und Rollen, aber nicht automatisch einen vollständigen Verlauf jenseits des aktuell im DOM geladenen Bereichs.
- Das laufende Chromium enthält jetzt beide Erweiterungen: den bestehenden Recorder und den Flextrawurst Exporter. Dieser Start erfolgte mit `--load-extension` für beide Pfade; bei einem späteren Start muss der Launcher die Flextrawurst-Erweiterung weiterhin laden, sofern sie nicht zusätzlich dauerhaft über „Entpackte Erweiterung laden“ registriert wird.
- Falls Chromium selbst „Vor dem Download nach dem Speicherort fragen“ aktiviert hat, kann der Browser weiterhin einen eigenen Dialog anzeigen; die Erweiterung fordert ihn nicht mehr an.
- Provider-DOMs ändern sich. Nicht erkannte Seiten liefern einen sichtbaren Fehler statt erfundener Daten.
- PDF ist eine lokale textbasierte Projektion mit Farbthema, kein Beleg für pixelgleiche Original-Exporter.

- REC-BACKUP-001: PASS — Checkpoint `73ccd21e4` vor der Selektor-/Live-Smoke-Korrektur gesetzt.
- REC-GATE-001: PASS — Vertragsprüfung mit 10 Markern und 10 Skills grün.
- REC-REPLICA-001: PASS — eigene MV3-Erweiterung mit Manifest, Popup, Content-Script, Roh-/Projektionstrennung, Provenienzfeldern, korrigierter ChatGPT-Turn-Ordnung und echtem Live-Lauf vorhanden.
- REC-DOWNLOAD-001: PASS — Echter ChatGPT-Export nutzt `saveAs: false`; im laufenden Chromium wurde `/config/Downloads/ftw-no-override-check.pdf` mit erwartetem Namen, `complete`, 39.427 Bytes, Hash, EOF und allen fünf Palette-Farbwerten zurückgelesen.
- REC-FETCH-001: PASS — kein Provider-API-Fetch; Sammlung beginnt erst nach Nutzerklick und läuft nur über danach sichtbar geladene DOM-Turns, ohne Navigation oder Auto-Scroll.
- REC-DOC-001: PASS — Aktion, sichtbarer ChatGPT-Lauf, korrigierte Markdown-Rücklese, Datei-Hash und verbleibende Grenze „DOM-geladener Bereich“ dokumentiert.

OUTCOME: PASS
