# Abnahme: bounded Asset- und Manifest-Fetch

Datum: 2026-08-15 14:47 +0200  
Stufe: `fetch-assets`  
EVIDENCE_VERSION: 1

## Aktion

Die sichtbare Seitenaufnahme begrenzt same-origin Asset-Fetches jetzt vor dem
vollständigen Einlesen: `content-length` wird vorgeprüft, der Response-Stream
wird bounded gelesen, ein Abort-Timer beendet langsame Requests, und
Content-Type, finale URL, Bytezahl und SHA-256-Status werden als Asset-
Provenienz mitgeführt. `0` ist kein Infinity-Schalter mehr. Die optionale
Owner-Manifest-Probe ist im normalen Capture-Pfad deaktiviert und wird nur
über `discover_owner_manifest: true` angefordert; auch ihr JSON-Body ist auf
2 MiB begrenzt.

## Sichtbar

Der isolierte Chromium-Worker erfasste eine lokale Fixture-Seite mit drei
sichtbaren Bildern und einem Stylesheet. Der Terminal-Livebeleg meldete:

- `small.bin`: `11` Bytes, `inlined: true`, `sha256_status: computed`;
- `large.bin`: `128` deklarierte Bytes, `inlined: false`,
  `reason: asset_limit_declared`;
- `slow.bin`: `inlined: false`,
  `reason: asset_fetch_timeout_1000ms`;
- Owner-Manifest: `status: not_requested`.

## Rücklese

Der Test `_codex/tools/test_recorder_fetch_provenance_live.js` liest die
Asset-Metadaten aus dem echten Extension-Worker zurück und prüft Bytezahl,
Hashformat, Limitgrund, Timeoutgrund und den fehlenden Manifest-Fetch. Die
bestehende Universal-Collection-Regression blieb mit `ok: true` und zwei
Snapshots grün. Syntax- und Diff-Prüfung waren fehlerfrei.

## Offen / unbekannt

Diese Stufe beweist Asset- und Manifest-Fetch-Provenienz. Sie beweist noch
nicht die vollständige Download-Abnahme, Server-Upload-Limits oder jeden
anderen `fetch()`-Aufruf des Recorders. Diese Pfade bleiben separate Marker-
Stufen und dürfen nicht aus diesem Bericht als erledigt abgeleitet werden.

- REC-GATE-001: PASS — der Gate-Checker akzeptiert `fetch-assets` und diesen Bericht
- REC-FETCH-001: PASS — isolierter Worker beweist bounded stream, deklarierte Größe, SHA-256, Final-URL, Abort und explizite Manifest-Probe
- REC-DOC-001: PASS — Aktion, Sichtbar, Rücklese und Offen/Unbekannt sind getrennt dokumentiert

OUTCOME: PASS
