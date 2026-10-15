EVIDENCE_VERSION: 1

# flextrawurst Surface — Tab-Export

Datum: 2026-08-21  
Quelle: `https://flextrawurst.de/`  
Desktop: sichtbares Chromium auf `DISPLAY=:1`  
Belegwurzel: `/tmp/flextrawurst-surface-export-v7/`

## Sichtbarer Lauf

- Die Splash-Seite wurde sichtbar über `BETRETEN` geöffnet; der nachgelagerte Willkommensdialog wurde sichtbar über `Überspringen` geschlossen.
- Im tatsächlichen DOM wurden 43 `.v-tab[data-view]`-Einträge gefunden.
- Jeder Tab wurde einzeln angesprochen. Danach wurde der sichtbare Scrollkörper auf Anfang gesetzt, per Maus-Wheel in endlichen Schritten bewegt und pro Schritt als Screenshot gesichert.
- 26 Tabs wurden aktiv angezeigt und bis zum Ende bestätigt. 17 Tabs waren im nicht eingeloggten/rollenabhängigen Surface-Zustand nicht aktiv bestätigbar (`codegeil`, `uber`, `wesen`, `gespraech`, `rag`, `gordslider`, `admin`, `wissen`, `leitstand`, `weltstrom`, `raume`, `suche`, `splitter`, `zitate`, `schatten`, `gruppen`, `vaulteinblick`). Diese bleiben im Export sichtbar markiert; ihre Nichterreichbarkeit wird nicht als Inhaltserfolg ausgegeben.
- Scrollspur: 1–27 Schritte pro Tab; die bekannten Lücken stehen in `surface-capture.json` unter `known_gaps`.

## Navigierbare Artefakte

Aus `/tmp/flextrawurst-surface-export-v7/surface-capture.json` wurden erzeugt:

- `SURFACE.html`: statische, scriptfreie Surface mit 43 Inhaltsankern und Tab-Index.
- `SURFACE.md`: Markdown-Projektion mit denselben Fragmentzielen.
- PDF: `was-ist-das-flextrawurst-surface-tabs.pdf`, 297836 Bytes, SHA-256 `cb4e4f093d187c1cf7a6cc14529ae24878a18e86c4ede9f9f5cc4f817c970512`.
- DOCX: `was-ist-das-flextrawurst-surface-tabs.docx`, 122530 Bytes, SHA-256 `8549749bf278a91f8f62261671977b1d44f3243013847d652089649989c4fac7`.

Die PDF enthält 86 interne `/Dest`-Sprungziele (Index und Rücksprung je Tab) und 52 externe URL-Anmerkungen. Die DOCX enthält 86 interne `w:anchor`-Hyperlinks und 33 externe Hyperlink-Beziehungen. Damit sind alle 43 Tab-Ziele klickbar; der Inhaltstatus bleibt pro Tab sichtbar.

## Browser und direkte Exporter

- Google Chrome wurde systemweit installiert: `Google Chrome 151.0.7922.173`.
- Installationspaket: `/root/werkraum/tools/browser_installs/google-chrome-stable_current_amd64.deb`, SHA-256 `878e5ab495b8a694980fca61bc09b37e651ccedce2291c73434d16e48a2646fd`.
- Chromium `150.0.7871.181` wurde in einem isolierten sichtbaren Desktop-1-Profil mit allen vier direkten Exporter-Unpacked-Verzeichnissen geladen; vier Service-Worker und vier Welcome-Seiten wurden bestätigt. Beleg: `/tmp/dak-chromium-direct-exporters-desktop1.json`.
- Für Google Chrome wurde anschließend die offizielle Chrome-Web-Store-Updatequelle per systemweiter `ExtensionInstallForcelist` gesetzt. Auf `DISPLAY=:1` zeigt `chrome://extensions` die vier Zielkarten als `enabled`: Gemini, Grok, ChatGPT und Claude (zusätzlich ist „Google Docs Offline“ systemseitig vorhanden). Rücklese aus dem Extension-UI: `/tmp/dak-chrome-exporters-desktop1.json`; sichtbarer Screenshot: `/tmp/chrome-exporters-desktop1-final.png`.
- Die vier Ziel-Exporter sind damit in diesem Chrome-Desktop-1-Profil dauerhaft installiert und aktiviert; die heruntergeladenen CRX-Dateien und ihre Original-Hashes bleiben separat unter `/root/werkraum/tools/direct_exporters/` archiviert.

## Gate-Marker

- REC-GATE-001: PASS — Contract-Gate grün.
- REC-BACKUP-001: PASS — Backup-Sicherheitspunkte vor Surface-Code und Browserinstallation vorhanden.
- REC-CRAWL-001: PASS — endlicher Tab-/Wheel-Lauf mit Fortschrittsprüfung und dokumentierten Lücken.
- REC-EYE-001: PASS — echte Surface ohne Splash-/Welcome-Overlay sichtbar geprüft; Schritt-Screenshots je Tab vorhanden.
- REC-FETCH-001: PASS — Quelle, DOM-Tab-Inventar und Zustandsgrenzen dokumentiert.
- REC-DOWNLOAD-001: PASS — PDF/DOCX-Bytes und SHA-256 aus finalen Dateien rückgelesen.
- REC-REPLICA-001: PASS — PDF/DOCX stammen aus derselben Surface-Capture-Projektion; Tab-Anker maschinell geprüft.
- REC-SEC-001: PASS — nur öffentliche Surface-Quelle und kontrollierte lokale Profile; keine fremden Uploads.
- REC-DOC-001: PASS — Capture-JSON, Screenshots, Artefaktmanifest und dieser Bericht vorhanden.

OUTCOME: PASS
