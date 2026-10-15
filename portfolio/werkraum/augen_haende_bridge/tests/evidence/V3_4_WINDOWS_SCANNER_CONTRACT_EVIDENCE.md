EVIDENCE_VERSION: 1
STAGE: V3.4 Windows scanner contract
OUTCOME: PARTIAL

## Belegte Vertragsschicht

- `default_desktop`: PASS — Fake-API-Scan liefert `windows:desktop` als
  `default_target_id` mit vollständigem virtuellen Desktop-Rechteck.
- `visible_window_inventory`: PASS — sichtbare Top-Level-Fenster erscheinen
  mit stabiler Ziel-ID, Rechteck, Z-Order, Prozessdaten und `inventory`-Profil.
- `generation_stability`: PASS — Titel-/Geometrieänderung erhält die
  Generation desselben Prozesses.
- `handle_reuse_guard`: PASS — Prozess-/Klassenwechsel am selben Handle erzeugt
  eine neue Generation.
- `paired_frame_required`: PASS — Scan ohne Frame-Referenz oder Frame-Hash
  wird abgewiesen.
- `browser_regression`: PASS —
  `/root/werkraum/augen_haende_bridge/tests/playwright_proof.py` und
  `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py` liefen mit
  Exit 0.

## Ergebnis

Der Kernvertrag ist belastbar genug für die nächste Binding-Etappe. Die
Win32-`ctypes`-Funktionen sind jetzt mit expliziten `argtypes` und `restype`
typisiert, insbesondere `OpenProcess`/`CloseHandle` mit `HANDLE`. Der
Gesamtstatus bleibt `PARTIAL`, weil die Ausführung auf einem echten Windows-
Host noch fehlt.

## Nicht belegt

- Native Win32-Ausführung auf Daniels Windows.
- Desktop-/Fenster-Capture und Frame-Hash-Erzeugung.
- Virtuelle Windows-Desktops 1/2.
- UI-Automation, Overlay-Hit-Test, Fokus und Input.
- Persistente Prozessstartzeit-Identität über Scanner-Neustarts.
