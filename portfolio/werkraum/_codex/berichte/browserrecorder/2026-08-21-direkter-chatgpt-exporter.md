EVIDENCE_VERSION: 1

# Direkter ChatGPT Exporter — Download und isolierte Installation

## Aktion

Die Chrome-Web-Store-Erweiterung `ilmdofdhpnhffldihboadndccenlnfll` wurde als originales CRX3 geladen, entpackt und als Store-Version 6.10.0 in einem isolierten Chromium-Profil auf Desktop 1 geladen. Kein Chat wurde exportiert.

## Sichtbar

Vor der lokalen Popup-Ansicht öffnete die Erweiterung selbstständig `https://www.chatgptexporter.com/de/welcome`. Danach wurde als einzelne sichtbare Adressleistenaktion `chrome-extension://jocghakjggbgfjhhncamlhajkhajgbdm/popup.html` geöffnet. Screenshots: `/tmp/direct-chatgpt-welcome.png` und `/tmp/direct-chatgpt-popup.png`. Titel: `ChatGPT Exporter`.

## Rücklese

CRX3: 820323 Bytes, SHA-256 `137a76b8a7947e22172f8f759411ab17acd2dd2b7ed2d19d214a88f6a9166611`. Manifest: Version 6.10.0, Berechtigung `storage`, Content-Scripts auf `chatgpt.com` und `chat.openai.com`, zusätzliche Host-/External-Connectable-Grenze `*.chatgptexporter.com`. DOM-Rücklese bestätigte PDF, Markdown, TXT, CSV, JSON und Bild sowie Selektions- und Metadatenoptionen. `chrome.storage.local` enthielt `account_info: null` und eine `ga.clientid`.

## Offen/Unbekannt

Kein realer Chat und kein Exportformat wurden ausgeführt. Die eigene FAQ erklärt PDF als temporär serverseitig verarbeitet; Löschung, Datenschutzbehauptung und Exporttreue sind nicht unabhängig bewiesen. Die unpacked ID weicht konstruktionsbedingt von der signierten Store-ID ab.

- REC-GATE-001: PASS — Vertrags-Gate vor Download und Installation war grün.
- REC-EYE-001: PASS — sichtbare Welcome- und Popup-Zustände mit Screenshots, URL, Titel, DOM und Storage rückgelesen.
- REC-DOWNLOAD-001: PASS — CRX-Datei vollständig rückgelesen; Bytezahl, CRX3-Typ und SHA-256 festgehalten.
- REC-FETCH-001: PASS — Google-Update-URL, Store-ID, Timeout, Redirect und Ergebnisstatus wurden explizit geführt; der automatische Welcome-Fetch ist als Fremdverhalten markiert.
- REC-SEC-001: PASS — Berechtigungen, Hostgrenzen, externe PDF-Verarbeitung und lokale Analytics-ID wurden geprüft und nicht als sicher umgedeutet.
- REC-DOC-001: PASS — Aktion, sichtbarer Zustand, Rücklese und offene Grenzen stehen in diesem Bericht.

OUTCOME: PASS
