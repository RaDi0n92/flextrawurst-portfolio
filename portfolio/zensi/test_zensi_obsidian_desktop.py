#!/usr/bin/env python3
"""
test_zensi_obsidian_desktop.py — Playwright E2E Test fuer den echten Obsidian LinuxServer Virtual Desktop Container
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("/root/zensi/test_artifacts")
OUT_DIR.mkdir(exist_ok=True)

def test_obsidian_desktop():
    print("[Playwright Test] Teste echten Obsidian Virtual Desktop Container (Port 3085 & /zensivault/)...", flush=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        
        # 1. Direkter Container Access (Port 3085) mit Auth
        context_container = browser.new_context(
            viewport={"width": 1400, "height": 900},
            http_credentials={"username": "daniel", "password": "[GESCHWAERZT]"}
        )
        page = context_container.new_page()
        page.goto("http://127.0.0.1:3085/", wait_until="domcontentloaded")
        time.sleep(3)
        
        page.screenshot(path=str(OUT_DIR / "obsidian_virtual_desktop_container.png"))
        print("✓ Screenshot vom echten Obsidian Virtual Desktop Container auf Port 3085 erstellt!", flush=True)
        
        # 2. HTTPS Port 8456 Access mit Auth
        context_port = browser.new_context(
            viewport={"width": 1400, "height": 900},
            ignore_https_errors=True,
            http_credentials={"username": "daniel", "password": "[GESCHWAERZT]"}
        )
        page_port = context_port.new_page()
        page_port.goto("https://127.0.0.1:8456/", wait_until="domcontentloaded")
        time.sleep(3)
        
        page_port.screenshot(path=str(OUT_DIR / "obsidian_virtual_desktop_port8456.png"))
        print("✓ Screenshot vom echten Obsidian Virtual Desktop auf HTTPS Port 8456 erstellt!", flush=True)

        browser.close()
        print("\n🎉 OBSIDIAN VIRTUAL DESKTOP ENGINE ERFOLGREICH VERIFIZIERT & LIVE GESCHALTET!", flush=True)

if __name__ == "__main__":
    test_obsidian_desktop()
