import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    print("[Playwright Test] Starte E2E Test für Schritt 1: Diff-, Audit- & Kommentar-Inspector...", flush=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        # Dialoge automatisch annehmen
        page.on("dialog", lambda dialog: dialog.accept())

        # 1. Page laden
        await page.goto("http://127.0.0.1:8043/", wait_until="domcontentloaded")
        await page.wait_for_selector("#chat-title", state="attached")
        print("✓ Zensi UI geladen", flush=True)
        
        # 2. Wesen 'Resonanzknoten' wählen
        await page.wait_for_selector("#wesen-select option[value='Resonanzknoten']", state="attached", timeout=10000)
        await page.select_option("#wesen-select", "Resonanzknoten")
        await page.evaluate("setSpiegelModus('sandbox')")
        await asyncio.sleep(1)
        print("✓ Wesen 'Resonanzknoten' ausgewählt", flush=True)
        
        # 3. Diff Modal öffnen per evaluate / click
        await page.evaluate("openDiffModal()")
        await page.wait_for_selector("#diff-modal", state="visible")
        print("✓ Diff-Inspector Modal geöffnet", flush=True)
        
        # 4. Prüfen ob Modal sichtbar ist
        is_visible = await page.is_visible("#diff-modal")
        assert is_visible, "Fehler: #diff-modal ist nicht sichtbar!"
        print("✓ TEST PASS: #diff-modal ist sichtbar", flush=True)
        
        # 5. Audit-Kommentar in Textarea eingeben und speichern
        test_comment = "Playwright E2E Audit Note: Resonanzknoten Haltung in Sandbox geprüft."
        await page.fill("#diff-comment-input", test_comment)
        await page.click("button:has-text('Kommentar in Historie & Vault Sichern')")
        await asyncio.sleep(2)
        print("✓ Audit-Kommentar per UI gesendet", flush=True)
        
        # 6. Screenshot erstellen
        art_dir = Path("/root/zensi/test_artifacts")
        art_dir.mkdir(exist_ok=True)
        await page.screenshot(path=str(art_dir / "01_diff_modal_audit.png"))
        print(f"✓ Screenshot gesichert unter {art_dir / '01_diff_modal_audit.png'}", flush=True)
        
        await browser.close()
        print("🎉 SCHRITT 1 PLAYWRIGHT E2E TEST ERFOLGREICH BEENDET!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
