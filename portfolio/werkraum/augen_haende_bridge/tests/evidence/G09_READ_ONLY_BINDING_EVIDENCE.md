# G09 — read-only Zielauswahl und Binding-Rücklese

Datum: 2026-09-20
Scope: `/root/werkraum/augen_haende_bridge/`
Status: `PARTIAL` — der frame- und generation-gekoppelte VPS-Core ist
bewiesen; native Windows-Zielauswahl und echtes Overlay-Hit-Testing bleiben
offen.

## Contract

- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/read_only_binding.py`
  bindet nur einen sichtbaren, verfügbaren Scanner-Eintrag mit vorhandener
  Beobachtungsfähigkeit.
- Das Binding bewahrt `scan_id`, `frame_ref`, `frame_hash` und
  `target_generation`.
- `read_back_binding()` akzeptiert nur denselben Target-Generation-/Frame-
  Zeugen; sonst wird `stale` zurückgegeben.
- Das erzeugte Binding enthält ausschließlich `Capability.OBSERVE`.
  Es erzeugt keine Eingabe, keine Terminalfähigkeit und keine Lease.

## Evidence

- `G09-CORE-01: PASS` — fünf Tests in
  `/root/werkraum/augen_haende_bridge/tests/test_read_only_binding.py`.
- `G09-CORE-02: PASS` — identischer Target-Generation-Wechsel wird als
  `target_generation_changed` abgewiesen.
- `G09-CORE-03: PASS` — neuer Frame-Zeuge wird als `paired_frame_changed`
  abgewiesen.
- `G09-CORE-04: PASS` — unavailable oder ohne `inventory`/`capture` kann
  nicht gebunden werden.
- `G09-CORE-05: PASS` — frischer identischer Snapshot erzeugt
  `BindingStatus.MATCHED` und `valid=True`.
- `G09-NATIVE-WINDOWS: UNKNOWN` — keine echte Windows-Oberfläche in dieser
  Umgebung.
- `G09-PLAYWRIGHT: NOT_APPLICABLE` — der Schritt ändert keine
  browserbedienbare Oberfläche; die bestehende Browser-Regression bleibt
  separat erforderlich.

## Boundary

G09 beweist die sichere Daten- und Beweisgrenze für spätere native Auswahl.
Es behauptet nicht, dass ein Windows-Fenster bereits verschoben, fokussiert,
geklickt oder an eine EXE-Raute geheftet werden kann.
