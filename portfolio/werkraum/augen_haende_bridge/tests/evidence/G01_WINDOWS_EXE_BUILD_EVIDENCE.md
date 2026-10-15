# G01 — Windows-EXE-Build und Bundle

Datum: 2026-09-19  
Pfad: `/root/werkraum/augen_haende_bridge/`

## Build

Der Build lief mit einer isolierten Windows-Python-3.13.15-Umgebung unter Wine
und PyInstaller 6.14.2. Der Build lief mit Exit-Code 0 und meldete ein Windows-
GUI-Bootloader-Bundle.

```text
Platform: Windows-10-10.0.19043-SP0
Python: 3.13.15
PyInstaller: 6.14.2
Bootloader: Windows-64bit-intel/runw.exe
Build complete! The results are available in: .../dist
```

## Artefakt

- Bundle: `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/`
- EXE: `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`
- Bundlegröße: 25,330,095 Bytes
- EXE-SHA256 (initial bundle): `9b01def12bced801e3e1f0c589434c1510a25f1123b745292414da717e69b040`
- `file`: `PE32+ executable for MS Windows 6.00 (GUI), x86-64`

## Bundle-Smoke-Test

Das vollständige Bundle startete unter Wine als Fenster mit dem Titel
`Augen & Hände Bridge`. Der Prozess und das Fenster wurden zurückgelesen; danach
wurde genau der Testprozess beendet. Kein Windows-Python außerhalb des Bundles
wurde für diesen Start verwendet.

## Grenze

Das ist ein Build- und Startbeleg aus Wine, keine Abnahme auf Daniels Windows.
Capture, echter Fokus-/Hit-Test, DPI-Verhalten, Nachrichten-Erstkontakt und ein
systemweiter Not-Aus bleiben native Windows-Prüfungen. Die Anwendung ist außerdem
noch der observe-only-Einstieg; weitere Bridge-Fähigkeiten werden nicht durch das
Vorhandensein der EXE behauptet.
## Korrigierter Fensterstart

Nach dem ersten Smoke-Test wurde der Startpfad korrigiert: Das Programm öffnet
kein bildschirmfüllendes Fenster mehr. Der aktuelle Bundle-Hash ist
`77719ce7479a38cb61e8c25eb90e45f1dd6a93d48d9eff48596c649f9f988e85`.

Der erneute Wine-Start lieferte für das native Fenster:

```text
Absolute upper-left X: 314
Absolute upper-left Y: 60
Width: 1180
Height: 680
```

Damit bleibt der reale Desktop sichtbar. Das ist ein Geometrie-/Startbeleg,
noch keine Abnahme von Durchklickbarkeit freier Bereiche.
