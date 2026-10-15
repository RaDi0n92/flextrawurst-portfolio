# Versionen 0.5.6 bis 0.5.8 (2026-10-01)

Gebaut unter Wine (PyInstaller onedir), nativ von Daniel bedient und bestätigt für 0.5.7 und 0.5.8 (Terminal-Markieren und -Scrollen, Selbstbild).

| Version | ZIP SHA256 (zur Zeit des Baus) | Inhalt |
|---|---|---|
| 0.5.6 | `85cdf015d25acc9527fee41bd4607e4bcf92e983e55cd13b9126c8d15040f621` | Rechtsklick-Menü, Kopieren ohne harte Umbrüche, PTY-Schreiben |
| 0.5.7 | `d044c6810eadaf6520c0b66303cd5239b92042e563f76a2e423bfa3df5f64153` | Menüposition, Rollbalken, Rad, Markieren mit Blättern |
| 0.5.8 | `a153fa10db5f7118d17792f3c1233a81134d9d3b9b0854062f32f3f51d123184` | Selbstbild-Fenster je Agent |

Proben unter Wine: `probes/terminal_rollbalken_smoketest.py` (Verlauf, Rad, Ziehen am Griff), `probes/kamera_fenster_smoketest.py` (Pixel: gespiegelt, Farben richtig).
Tests: 858, nur die drei bekannten Fehlschläge in `test_terminal_adapter.py`. Nativ nicht geprüft: Mikrofon, Rad bei Vollbild-Programmen, Menü-Eintrag „Selbstbild: durchklickbar“.
