# G01 — Opt-in-Transportbindung der EXE

Datum: 2026-09-19  
Pfad: `/root/werkraum/augen_haende_bridge/`

## Implementierung

- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/bridge_runtime.py`
  hält den Asyncio-Transport in einem eigenen Hintergrundthread.
- Die EXE verbindet sich nur, wenn `BRIDGE_URL` und `BRIDGE_TOKEN` beide gesetzt
  sind. Ohne vollständige Konfiguration bleibt sie offline.
- Empfangene Event-Nachrichten werden an den Tk-Thread zurückgereicht und erst
  nach `confirm_received` als empfangen bestätigt.
- Der vorhandene Loopback-Relay bleibt Loopback-only; es wurde kein öffentlicher
  VPS-Endpunkt erfunden oder aktiviert.

## Belege

- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`: 39 Tests grün.
- Der echte `BridgeRuntime`-Integrationstest startete einen Loopback-Relay,
  verband den Runtime-Thread, empfing `runtime-first-contact` als `say`-Event
  und bestätigte die Zustellung als `received`.
- Vollständige Testmenge nach dem Integrationstest: 40 Tests grün.
- Windows-Bundle mit PyInstaller 6.14.2 und `websockets==16.1.1` neu gebaut: Exit-Code 0.
- PyInstaller verarbeitete `hook-websockets.py`.
- EXE: `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`
- Aktueller SHA256: `8b118d1a53b606bccb9512ab7180ebf3e8a6cc62b1a96adde7af96d94ba8982f`

## Grenze

Dieser Schritt beweist die Paketbindung und den isolierten Runtime-Vertrag. Er
beweist noch keinen erreichbaren VPS-Endpunkt, kein echtes Windows-Notebook und
keinen Agenten-Erstkontakt. Die Surface wurde für diesen Schritt nicht gestartet.
