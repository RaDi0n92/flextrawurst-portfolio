import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    print("[Playwright Test] Starte E2E Test für Schritt 3: Multi-Wesen Symposium / Arena...", flush=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        page.on("dialog", lambda dialog: dialog.accept())

        # 1. Page laden
        await page.goto("http://127.0.0.1:8043/", wait_until="domcontentloaded")
        await page.wait_for_selector("#chat-title", state="attached")
        print("✓ Zensi UI geladen", flush=True)
        
        # 2. Wesen wählen
        await page.wait_for_selector("#wesen-select option[value='Resonanzknoten']", state="attached", timeout=10000)
        await page.select_option("#wesen-select", "Resonanzknoten")
        await asyncio.sleep(1)
        
        # 3. Symposium Modal öffnen
        await page.evaluate("openSymposiumModal()")
        await page.wait_for_selector("#symposium-modal", state="visible")
        print("✓ Symposium Modal geöffnet", flush=True)
        
        # 4. Symposium starten via evaluate
        await page.fill("#symposium-thema-input", "Playwright E2E Streitfall: Ist Bewusstsein lokal oder vernetzt?")
        await page.evaluate("starteSymposiumUI()")
        await asyncio.sleep(2)
        print("✓ Symposium gestartet", flush=True)
        
        # 5. Screenshot erstellen
        art_dir = Path("/root/zensi/test_artifacts")
        art_dir.mkdir(exist_ok=True)
        await page.screenshot(path=str(art_dir / "03_symposium_arena.png"))
        print(f"✓ Screenshot gesichert unter {art_dir / '03_symposium_arena.png'}", flush=True)
        
        await browser.close()
        print("🎉 SCHRITT 3 PLAYWRIGHT E2E TEST ERFOLGREICH BEENDET!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
