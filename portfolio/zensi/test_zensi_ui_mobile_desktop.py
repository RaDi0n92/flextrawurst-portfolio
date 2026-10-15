#!/usr/bin/env python3
"""
test_zensi_ui_mobile_desktop.py — Playwright Skript zur Inspektion & Verifikation der Zensi UI (Desktop & Mobile)
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("/root/zensi/test_artifacts")
OUT_DIR.mkdir(exist_ok=True)

def test_ui():
    print("[Playwright UI Test] Starte Desktop & Mobile Inspektion...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        
        # ── 1. DESKTOP TEST (1280x800) ──
        context_desk = browser.new_context(viewport={"width": 1280, "height": 800})
        page_desk = context_desk.new_page()
        page_desk.goto("http://127.0.0.1:8043/", wait_until="domcontentloaded")
        page_desk.wait_for_selector("#chat-title", state="attached")
        time.sleep(1)
        
        # Screenshot Desktop Initial
        page_desk.screenshot(path=str(OUT_DIR / "desktop_initial.png"))
        print("✓ Desktop Initial Screenshot erstellt", flush=True)
        
        # Wesen 'Resonanzknoten' wählen & Modus Sandbox setzen
        page_desk.wait_for_selector("#wesen-select option[value='Resonanzknoten']", state="attached")
        page_desk.select_option("#wesen-select", "Resonanzknoten")
        page_desk.evaluate("setSpiegelModus('sandbox')")
        time.sleep(1)
        page_desk.screenshot(path=str(OUT_DIR / "desktop_wesen_geladen.png"))
        print("✓ Desktop Wesen Geladen Screenshot erstellt", flush=True)
        
        # Modal öffnen
        page_desk.evaluate("openSchichtenModal()")
        page_desk.wait_for_selector("#schichten-modal", state="visible")
        time.sleep(1)
        page_desk.screenshot(path=str(OUT_DIR / "desktop_modal_open.png"))
        print("✓ Desktop Schichten-Modal Screenshot erstellt", flush=True)
        page_desk.evaluate("closeSchichtenModal()")

        # ── 2. MOBILE TEST (375x812 - iPhone 12) ──
        context_mob = browser.new_context(viewport={"width": 375, "height": 812})
        page_mob = context_mob.new_page()
        page_mob.goto("http://127.0.0.1:8043/", wait_until="domcontentloaded")
        page_mob.wait_for_selector("#chat-title", state="attached")
        time.sleep(1)
        
        # Screenshot Mobile Initial
        page_mob.screenshot(path=str(OUT_DIR / "mobile_initial.png"))
        print("✓ Mobile Initial Screenshot erstellt", flush=True)

        # Drawer öffnen via UI Funktion
        page_mob.evaluate("toggleDrawer()")
        time.sleep(1)
        page_mob.screenshot(path=str(OUT_DIR / "mobile_drawer_open.png"))
        print("✓ Mobile Drawer Open Screenshot erstellt", flush=True)

        # Wesen in Mobile Drawer wählen
        page_mob.wait_for_selector("#wesen-select option[value='Resonanzknoten']", state="attached")
        page_mob.select_option("#wesen-select", "Resonanzknoten")
        page_mob.evaluate("setSpiegelModus('sandbox')")
        time.sleep(1)
        page_mob.screenshot(path=str(OUT_DIR / "mobile_wesen_geladen.png"))
        print("✓ Mobile Wesen Geladen Screenshot erstellt", flush=True)

        # Drawer schließen & Header prüfen
        page_mob.evaluate("closeDrawer()")
        time.sleep(1)
        page_mob.screenshot(path=str(OUT_DIR / "mobile_header_with_wesen.png"))
        print("✓ Mobile Header mit geladenem Wesen Screenshot erstellt", flush=True)

        # Schichten Modal auf Mobile öffnen
        page_mob.evaluate("openSchichtenModal()")
        page_mob.wait_for_selector("#schichten-modal", state="visible")
        time.sleep(1)
        page_mob.screenshot(path=str(OUT_DIR / "mobile_modal_open.png"))
        print("✓ Mobile Schichten-Modal Screenshot erstellt", flush=True)

        # Vault Explorer auf Mobile testen
        page_mob.goto("http://127.0.0.1:8043/zensi/vault/", wait_until="domcontentloaded")
        time.sleep(1)
        page_mob.screenshot(path=str(OUT_DIR / "mobile_vault_explorer.png"))
        print("✓ Mobile Vault Explorer Screenshot erstellt", flush=True)

        browser.close()
        print("\n🎉 PLAYWRIGHT UI INSPEKTIONSERGEBNISSE ERFOLGREICH GESICHERT!", flush=True)

if __name__ == "__main__":
    test_ui()
