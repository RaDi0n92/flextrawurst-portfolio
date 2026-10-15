EVIDENCE_VERSION: 1

# Desktop-1-Umgebung — fünf Erweiterungen geladen

STAGE: live-click
OUTCOME: PASS

## Sichtbarer Lauf

Playwright hat auf `DISPLAY=:1` ein sichtbares Chromium-Profil gestartet und die vier bereits vorhandenen Exporter aus dem Desktop-1-Profil zusammen mit dem Recorder als Unpacked-Extensions geladen. Die Erweiterungsseite meldete:

- Gemini Exporter `jfepajhaapfonhhfjmamediilplchakk` · 4.3.0
- Grok Exporter `gjoigaflapfgapfebiajiolclnpfneao` · 2.4.1
- ChatGPT Exporter `ilmdofdhpnhffldihboadndccenlnfll` · 6.10.0
- Claude Exporter `elhmfakncmnghlnabnolalcjkdpfjnin` · 3.8.1
- AI UI Recorder `molhhdlenmhokfibmbojpapccaidfepi` · 1.8.0

Der Recorder-Workspace wurde als echte Extension-Origin geöffnet. Der Zugangsschlüssel wurde über die sichtbare Recorder-UI im neuen Profil gespeichert; der Schlüssel selbst steht nicht in diesem Bericht.

## Belegdateien

- [Erweiterungsseite](2026-08-22-desktop1-all-exporters-installed/extensions-page.png)
- [Recorder-Seitenleiste](2026-08-22-desktop1-all-exporters-installed/recorder-sidepanel.png)

- REC-GATE-001: PASS — Recorder-Vertragsgate war vor der Änderung vollständig grün.
- REC-EYE-001: PASS — Playwright headful auf DISPLAY=:1; echte `chrome://extensions/`-Seite und echte `chrome-extension://`-Seitenleiste sichtbar geprüft.
- REC-BACKUP-001: PASS — Backup-Commit `05a16b5bf` wurde vor der Installation gesetzt.
- REC-FETCH-001: PASS — kein unmarkierter Fetch; die Aktion war eine lokale Extension-Installation und sichtbare Profil-Konfiguration.
- REC-SEC-001: PASS — Zugangsschlüssel wurde nur über Passwortfeld in das temporäre Chromium-Profil geschrieben und nicht ausgegeben.
- REC-DOC-001: PASS — fünf IDs, Versionen, Extension-Origin und Screenshots dokumentiert.

OUTCOME: PASS
