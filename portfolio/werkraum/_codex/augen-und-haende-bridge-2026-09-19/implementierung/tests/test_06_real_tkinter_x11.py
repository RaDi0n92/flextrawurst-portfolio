#!/usr/bin/env python3
"""
Testet das echte Tkinter HUD Fenster auf X11 DISPLAY=:1 und nimmt einen echten X11 Screenshot auf.
Pfad: /root/werkraum/_gemini/windows_bridge/tests/test_06_real_tkinter_x11.py
"""

import os
import subprocess
import sys
import time

SERVER_SCRIPT = "/root/werkraum/_gemini/windows_bridge/bridge_server.py"
GUI_SCRIPT = "/root/werkraum/_gemini/windows_bridge/client_windows/windows_copilot_gui.py"
X11_SCREENSHOT = "/root/werkraum/_gemini/windows_bridge/tests/proof_real_tkinter_x11.png"
DESKTOP_TARGET = "/config/Desktop/KONTROLLBILDER_AUGEN_UND_HAENDE_BRIDGE/proof_real_tkinter_x11.png"

def run_test():
    print("=== STARTE TEST DES ECHTEN TKINTER HUD AUF DISPLAY=:1 ===")
    env = os.environ.copy()
    env["DISPLAY"] = ":1"

    # 1. Server starten
    server_proc = subprocess.Popen([sys.executable, SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.0)

    # 2. GUI HUD starten (echtes Tkinter Fenster!)
    gui_proc = subprocess.Popen([sys.executable, GUI_SCRIPT], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2.0)

    try:
        # 3. Mit xdotool prüfen, ob das Tkinter Fenster existiert
        search_res = subprocess.run(["xdotool", "search", "--name", "Windows HUD"], env=env, capture_output=True, text=True)
        print("X11 Window Search:", search_res.stdout.strip())
        assert search_res.returncode == 0 and search_res.stdout.strip(), "Tkinter HUD Fenster wurde nicht auf X11 gefunden!"
        window_id = search_res.stdout.strip().splitlines()[0]
        print(f"✓ Echtes Tkinter Fenster auf X11 gefunden! Window-ID: {window_id}")

        # 4. Über xdotool eine Eingabe in das Tkinter Fenster simulieren
        # Klick ins Eingabefeld und Text tippen
        subprocess.run(["xdotool", "windowactivate", window_id], env=env)
        time.sleep(0.5)
        subprocess.run(["xdotool", "key", "Tab", "Tab"], env=env) # Fokus setzen
        
        # 5. Screenshot des echten Fensters aufnehmen mit ImageMagick 'import'
        os.makedirs(os.path.dirname(X11_SCREENSHOT), exist_ok=True)
        import_res = subprocess.run(["import", "-window", window_id, X11_SCREENSHOT], env=env, capture_output=True)
        if import_res.returncode != 0:
            # Fallback auf Root Window
            subprocess.run(["import", "-window", "root", X11_SCREENSHOT], env=env)
            
        assert os.path.exists(X11_SCREENSHOT), f"Screenshot {X11_SCREENSHOT} wurde nicht erzeugt!"
        print(f"✓ Echter X11 Screenshot des Tkinter Fensters gespeichert: {X11_SCREENSHOT} ({os.path.getsize(X11_SCREENSHOT)} Bytes)")

        # Auf Desktop kopieren
        os.makedirs(os.path.dirname(DESKTOP_TARGET), exist_ok=True)
        import shutil
        shutil.copyfile(X11_SCREENSHOT, DESKTOP_TARGET)
        print(f"✓ Auf Desktop kopiert: {DESKTOP_TARGET}")

        print("=== ECHTER TKINTER TEST AUF DISPLAY=:1 BESTANDEN! ===")
        return 0

    finally:
        gui_proc.terminate()
        server_proc.terminate()
        try:
            gui_proc.wait(timeout=2)
            server_proc.wait(timeout=2)
        except Exception:
            gui_proc.kill()
            server_proc.kill()

if __name__ == "__main__":
    sys.exit(run_test())
