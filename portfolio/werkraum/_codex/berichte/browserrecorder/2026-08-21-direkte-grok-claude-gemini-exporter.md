EVIDENCE_VERSION: 1

# Direkte Grok-, Claude- und Gemini-Exporter

## Aktion

Die drei Schwester-Erweiterungen wurden anhand ihrer Store-IDs als originale CRX3-Pakete vom Google-Update-Dienst geladen, entpackt und zusammen mit dem direkten ChatGPT Exporter in einem isolierten Desktop-1-Chromium-Profil geladen.

## Sichtbar

Die Installation öffnete selbstständig vier getrennte Welcome-Tabs für ChatGPT, Grok, Claude und Gemini. Der aktive Desktop-1-Tab zeigte die ChatGPT-Welcome-Seite; die übrigen Welcome-Seiten standen im rückgelesenen Tabkontext. Kein echter Anbieterchat wurde geöffnet oder exportiert.

## Rücklese

- Grok `gjoigaflapfgapfebiajiolclnpfneao`: Version 2.4.1, 573885 Bytes, SHA-256 `4bd895b3dac7424d5ac469089823111d635ae022d458286b31d5ca644d7c0cf5`, geladene ID `mejgcedgllclplkbdhbnkekloloiagbb`.
- Claude `elhmfakncmnghlnabnolalcjkdpfjnin`: Version 3.8.0, 630788 Bytes, SHA-256 `953f928e777618a7ffca4a2c9ba5a151773064e9a67777400ec5061557b2c75e`, geladene ID `gkcibheljhdaogdidgkgmdnkplconkfn`.
- Gemini `jfepajhaapfonhhfjmamediilplchakk`: Version 4.2.0, 645795 Bytes, SHA-256 `b9b7f6c96c0a04d81279efabaa80bcec6aa6a475d65ce9ee16810d3c0507a382`, geladene ID `iapjigihodloglgbnpelfnmjcaakjmkf`.

Chrome-Profileinstellungen und DevTools-Zielliste bestätigten die drei getrennten Pfade und Service-Worker. Grok bindet `grokexporter.com` und `assets.grok.com` ein. Claude injiziert bei `document_start` in die Hauptwelt von `claude.ai` und bindet `claudexporter.com` sowie `ai-chat-exporter.net` ein. Gemini injiziert bei `document_start` in die Hauptwelt von `gemini.google.com`, bindet zwei Betreiber-Domains ein und fordert `<all_urls>`.

## Offen/Unbekannt

Keine reale Chat-Extraktion und kein PDF/JSON/CSV/Markdown-Download wurden ausgeführt. Exporttreue, lokale oder serverseitige Verarbeitung, Download-Completion und Dateihashes sind daher noch offen. Die unpacked IDs unterscheiden sich konstruktionsbedingt von den signierten Store-IDs. Geminis breite `<all_urls>`-Berechtigung ist ein Sicherheitsbefund, keine Freigabe für das normale Browserprofil.

- REC-GATE-001: PASS — Vertrags-Gate war vor Download und Installation grün.
- REC-DOWNLOAD-001: PASS — alle drei CRX-Dateien wurden mit Bytezahl, CRX-Typ und SHA-256 rückgelesen.
- REC-FETCH-001: PASS — Store-ID, Google-Updatequelle, Timeout, Redirect und Ergebnisstatus wurden explizit geführt; automatische Welcome-Navigation ist markiert.
- REC-SEC-001: PASS — Manifestberechtigungen, Hauptwelt-Injektionen, Hostgrenzen und Geminis `<all_urls>` wurden geprüft und nicht als unbedenklich umgedeutet.
- REC-DOC-001: PASS — Aktion, sichtbarer Zustand, Rücklese und offene Grenzen stehen in diesem Bericht.

OUTCOME: PASS
