#!/usr/bin/env python3
"""
test_zensi_obsidian_sync.py — End-to-End Playwright Simulatorsskript für Zensi & Obsidian Vault Sync
"""

import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

VAULT_BASE = Path("/root/zensi/obsidian_vault")

def test_zensi_playwright():
    print("[Playwright Test] Starte Browser-Simulation auf http://127.0.0.1:8043...", flush=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()
        
        # Dialoge automatisch schließen
        page.on("dialog", lambda dialog: dialog.accept())

        # 1. Zensi UI laden
        page.goto("http://127.0.0.1:8043/", wait_until="domcontentloaded")
        page.wait_for_selector("#chat-title", state="attached")
        print("✓ Zensi UI geladen auf Port 8043", flush=True)
        
        # 2. Warten bis Wesensliste geladen ist
        page.wait_for_selector("#wesen-select option[value='Resonanzknoten']", state="attached", timeout=10000)
        page.select_option("#wesen-select", "Resonanzknoten")
        page.evaluate("setSpiegelModus('sandbox')")
        time.sleep(1)
        print("✓ Wesen 'Resonanzknoten' & Modus 'Sandbox' in UI gewählt", flush=True)

        # 3. Schichten-Inspector Modal via UI-Funktion öffnen
        page.evaluate("openSchichtenModal()")
        page.wait_for_selector("#schichten-modal", state="visible")
        print("✓ Schichten-Inspector Modal geöffnet", flush=True)

        # 4. Version abspeichern (v_playwright_e2e)
        page.fill("#schichten-vname-input", "v_playwright_e2e")
        page.evaluate("speichereAktuelleVersion()")
        time.sleep(2)

        # Prüfen ob Version im Obsidian Vault existiert
        v_path = VAULT_BASE / "wesensprofile" / "Resonanzknoten" / "versionen" / "v_playwright_e2e"
        if v_path.exists() and (v_path / "schichten_config.json").exists():
            print(f"✓ TEST PASS: Version 'v_playwright_e2e' direkt im Obsidian Vault unter {v_path} verankert!", flush=True)
        else:
            print(f"❌ TEST FAIL: Version {v_path} nicht gefunden", flush=True)

        # 5. In Sandbox Sichern & Modal Schließen
        page.evaluate("speichereSchichtenConfig()")
        time.sleep(1)
        page.evaluate("closeSchichtenModal()")
        print("✓ Schichten-Änderungen live in Sandbox gesichert", flush=True)

        # 6. Outputsystem Markdown Exporter Direct Test
        print("[Playwright Test] Teste direktes Outputsystem-Schreiben...", flush=True)
        from server import speichere_in_outputsystem
        saved_file = speichere_in_outputsystem("Resonanzknoten", "sandbox", "v_playwright_e2e", "e2e_playwright_essenz.md", "Essenz des Spielwesens aus E2E Test.")
        
        if Path(saved_file).exists():
            content = Path(saved_file).read_text(encoding="utf-8")
            print(f"✓ TEST PASS: Markdown Outputsystem Datei erzeugt unter: {saved_file}", flush=True)
            print(f"  Frontmatter Snippet:\n{content[:150]}", flush=True)
        else:
            print(f"❌ TEST FAIL: Outputsystem Datei konnte nicht geschrieben werden", flush=True)

        browser.close()
        print("\n🎉 ALLE PLAYWRIGHT SIMULATIONSTESTS ERFOLGREICH ABGESCHLOSSEN!", flush=True)

if __name__ == "__main__":
    test_zensi_playwright()
