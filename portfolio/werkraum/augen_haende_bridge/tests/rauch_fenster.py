#!/usr/bin/env python3
"""Rauchtest: startet das Bridge-Fenster auf einem virtuellen Bildschirm und bedient es kurz.

Aufruf:  xvfb-run -a python3 tests/rauch_fenster.py     (braucht Xvfb)

Ohne Anzeige, ohne Eingabe in ein echtes Fenster. Zeigt, ob das Fenster nach einer Aenderung
noch startet, zeichnet und vier Handgriffe ohne Ausnahme ueberlebt: Spruch senden, Ziel waehlen
(Registry), Ziel binden (nativer Zweig mit vorgetaeuschtem Scan) und Neuzeichnen.
Ein Beleg fuer den Start, nicht fuer das Aussehen und nicht fuer Windows.
"""
import sys
import tkinter as tk
import types
from pathlib import Path

BASIS = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, BASIS + "/src")
sys.path.insert(0, BASIS + "/client_windows")

import overlay_app  # noqa: E402

app = overlay_app.BridgeOverlay()
root = app.root
root.update()
print("gestartet und gezeichnet")
print("   Agenten im Fenster:", list(app.nodes) or "keine")
print("   ausgewaehlter Agent:", app.selected_agent_id)
try:
    print("   Deckkraft des Fensters:", root.attributes("-alpha"))
except tk.TclError:
    print("   Deckkraft: nicht lesbar")

fehler = []


def nativer_bindungszweig():
    """Der Zweig, der ein echtes Fenster-Ziel an einen Agenten bindet. Der Scan ist vorgetaeuscht."""
    app.latest_native_scan = types.SimpleNamespace(items=[types.SimpleNamespace(
        target_id="native:test", label="Testfenster", source="native", availability="available")])
    try:
        app.select_target("native:test")
    finally:
        app.latest_native_scan = None


for name, aktion in (
    ("Spruch senden", lambda: app.say()),
    ("Ziel waehlen (Registry)", lambda: app.select_target(next(iter(app.registry.records)))),
    ("Ziel binden (nativer Zweig)", nativer_bindungszweig),
    ("neu zeichnen", lambda: app._draw()),
):
    try:
        aktion()
        root.update()
        print(f"   {name}: ok · Status: {app.status}")
    except Exception as e:  # noqa: BLE001 - Rauchtest soll jede Ausnahme melden
        fehler.append(name)
        print(f"   {name}: AUSNAHME {type(e).__name__}: {e}")

app.close()
sys.exit(1 if fehler else 0)
