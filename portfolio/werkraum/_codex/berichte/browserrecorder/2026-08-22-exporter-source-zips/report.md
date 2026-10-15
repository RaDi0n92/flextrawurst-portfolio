# Original-Exporter-ZIPs · Hash- und Quellformat-Rücklese

EVIDENCE_VERSION: 1
DATE: 2026-08-22
SURFACE: Desktop-1-Arbeitsprofil, headful Chromium/CDP 9235

## Aktion

Die vier zuvor geladenen Original-Exporter-ZIPs wurden aus dem Desktop-1-Arbeitsprofil gelesen. Die ZIP-Struktur wurde ohne Ausführung fremder Skripte geprüft: Dateianzahl, SHA-256 und sichtbare Format-Tokens aus den enthaltenen JavaScript/HTML/JSON-Dateien.

## Sichtbar

Die sichtbaren Extension-Oberflächen sind im Parity-Inventar dokumentiert. Diese Datei dokumentiert die heruntergeladenen Quellpakete und ihre Hashes; die Fremd-Binaries werden nicht in das Projekt-Repository kopiert.

## Rücklese

| Exporter | Bytes | ZIP-Einträge | SHA-256 | Quellformat-Tokens |
|---|---:|---:|---|---|
| ChatGPT | 819001 | 85 | `7fba985f443d01a1fa02b8096e791a1701e7993abdc6feea9b9100223ec1ee75` | CSV, JSON, MD, PDF, TXT |
| Claude | 629467 | 79 | `3358d8db6cc04bf61cc5b4193ee36ac37e74214321e10d4a1ef123a58bb86f11` | CSV, JSON, MD, PDF, TXT, ZIP-Projektmodus |
| Gemini | 644475 | 79 | `a342454872120794ab8672408d60ffa5e5ef41ba9e3d0b6fc8ab3ca52f9ec624` | CSV, JSON, MD, PDF, TXT |
| Grok | 572563 | 84 | `0b4104c739692503c7843f2b17c79bee10b1cdebac3f630d244778858d23f2be` | CSV, JSON, MD, PDF, TXT |

Die Format-Tokens sind Quellhinweise, keine Behauptung, dass ein Provider-Chat ohne Anmeldung exportiert wurde. Die sichtbare Provider-UI-/Formatliste steht separat im Parity-Inventar.

- REC-GATE-001: PASS — Recorder-Verträge geprüft.
- REC-FETCH-001: PASS — vier heruntergeladene ZIPs, Struktur und Hashes rückgelesen.
- REC-SEC-001: PASS — keine Zugangsdaten, Cookies oder Tokens gelesen.
- REC-DOC-001: PASS — Quelle, Hashes, Umfang und Beweisgrenze dokumentiert.

OUTCOME: PASS
