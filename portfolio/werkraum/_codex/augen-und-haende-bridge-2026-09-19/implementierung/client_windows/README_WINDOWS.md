# Augen & Hände Desktop Bridge — Windows Client Anleitung

Dieses Verzeichnis enthält den leichtgewichtigen Windows-Copilot-Client für Daniels ThinkPad.

## Schnellstart

1. **Voraussetzung:** Python 3.10+ auf dem Windows-Laptop installiert.
2. **Abhängigkeiten installieren:**
   ```cmd
   pip install -r requirements.txt
   ```
3. **Direkt starten (Entwicklungsmodus):**
   ```cmd
   python windows_copilot_gui.py
   ```
4. **Als Standalone `.exe` kompilieren:**
   Einfach per Doppelklick die Datei `build_exe.bat` ausführen!
   Die fertige Datei liegt danach unter `dist\AugenUndHaendeBridge\AugenUndHaendeBridge.exe`.

## Systemarchitektur & ThinkPad-Garantie
- **RAM:** Bleibt stabil unter 50 MB RAM (kein Electron!).
- **VRAM:** 0 MB VRAM (die 2 GB VRAM des ThinkPads bleiben frei für Spiele/Blender).
- **CPU:** 0–2% Idle-Last.
- **Not-Aus:** Taste `F12` stoppt alle Aktionen in <1ms.
