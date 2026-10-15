# G11 — Scanner → observe-only Binding im gebündelten Windows-Pfad

Datum: 2026-09-20
Scope: `/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py`
Status: `PARTIAL` — die Kette ist im gebündelten Wine-Smoke grün; Wine ist
kein nativer Windows-Abnahmetest.

## Contract

- Nach einem expliziten Windows-Scan werden native Scan-Einträge im bestehenden
  Zielrail auswählbar.
- Die Auswahl ruft ausschließlich
  `create_read_only_binding()` und `read_back_binding()` auf.
- Das Binding trägt nur `Capability.OBSERVE`; kein Input, kein Terminal, keine
  Lease und kein automatisches Zielhandeln werden daraus abgeleitet.
- Der Testhaken `BRIDGE_NATIVE_BIND_TARGET_ID` ist nur aktiv, wenn Daniel ihn
  ausdrücklich setzt. Ohne ihn bleibt die Auswahl manuell.

## Evidence

- `G11-CORE-01: PASS` — die Gesamtsuite lief mit 114 Tests grün.
- `G11-WINE-01: PASS` —
  `/root/werkraum/augen_haende_bridge/tests/windows_exe_wine_native_binding.py`
  startete die gebündelte EXE mit explizitem Desktop-Testziel.
- `G11-WINE-02: PASS` — externes `xwininfo` las zuletzt
  `Augen & Hände Bridge · scan-received:2 · binding-readback` zurück; die
  Anzahl sichtbarer Wine-Fenster ist umgebungsabhängig.
- `G11-WINE-03: PASS` — G07-Scan-Smoke und G06-Erstkontakt-Smoke blieben mit
  dem neuen Bundle grün.
- `G11-NATIVE-WINDOWS: UNKNOWN` — Wine ersetzt Daniels Windows nicht.
- `G11-REAL-CLICK: NOT_EXERCISED` — der Wine-Test nutzt nur den ausdrücklich
  markierten Testhaken; ein echter menschlicher Klick auf Windows folgt noch.

## Package

- EXE SHA256:
  `265c9fa3713df411864d3dc7d04b8f6f97d34b947e8a7a3db7d1c3a9caf855cd`
- Übergabearchiv:
  `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G11-win64-handoff.zip`
- Archiv SHA256:
  `0d45d7966ec17484b6396573352d0f9d21fbc78f72a7968c27139705e8307eb1`
