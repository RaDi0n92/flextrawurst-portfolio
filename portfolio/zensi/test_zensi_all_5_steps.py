import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    print("[Playwright Master Test] Starte E2E Test für ALLE 5 Zensi Bausteine...", flush=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        page.on("dialog", lambda dialog: dialog.accept())

        # 1. Zensi UI laden & Wesen wählen
        await page.goto("http://127.0.0.1:8043/", wait_until="domcontentloaded")
        await page.wait_for_selector("#chat-title", state="attached")
        await page.wait_for_selector("#wesen-select option[value='Resonanzknoten']", state="attached", timeout=10000)
        await page.select_option("#wesen-select", "Resonanzknoten")
        await asyncio.sleep(1)
        print("✓ 1. Zensi UI & Wesen Resonanzknoten geladen", flush=True)

        # 2. Schritt 1: Diff Modal via Button Klick testen
        await page.click("button:has-text('diff & audit')")
        await page.wait_for_selector("#diff-modal", state="visible")
        assert await page.is_visible("#diff-modal"), "Diff Modal nicht sichtbar"
        await page.click("#diff-modal button:has-text('Schließen')")
        print("✓ 2. Schritt 1: ⚖️ Diff- & Audit-Inspector verifiziert", flush=True)

        # 3. Schritt 2: Surface Integration Check
        surface_html = Path("/root/flextrawurst/out/surface/flextrawurst_surface.html").read_text(encoding="utf-8")
        assert 'data-view="zensi"' in surface_html, "Zensi Tab fehlt in Surface"
        assert 'src="/zensi/"' in surface_html, "Zensi Iframe fehlt in Surface"
        print("✓ 3. Schritt 2: 🪞 Zensi Surface Tab Integration verifiziert", flush=True)

        # 4. Schritt 3: Multi-Wesen Symposium Modal via Button Klick
        await page.click("button:has-text('symposium')")
        await page.wait_for_selector("#symposium-modal", state="visible")
        assert await page.is_visible("#symposium-modal"), "Symposium Modal nicht sichtbar"
        await page.click("#symposium-modal button:has-text('Schließen')")
        print("✓ 4. Schritt 3: 🎭 Multi-Wesen Symposium / Arena verifiziert", flush=True)

        # 5. Schritt 4: Traum- & Schlaf-Prozessor via Button Klick
        await page.click("button:has-text('schlaf & traum')")
        await page.wait_for_selector("#traum-modal", state="visible")
        assert await page.is_visible("#traum-modal"), "Traum Modal nicht sichtbar"
        await page.click("#traum-modal button:has-text('Schließen')")
        print("✓ 5. Schritt 4: 🌙 Traum- & Schlaf-Prozessor verifiziert", flush=True)

        # 6. Schritt 5: Voice & Audio Input (Mic Button)
        is_mic_visible = await page.is_visible("#stt-btn")
        assert is_mic_visible, "Mic Button #stt-btn nicht sichtbar"
        print("✓ 6. Schritt 5: 🎙️ Mikrophon-Spracheingabe Button verifiziert", flush=True)

        # 7. Screenshot der finalen UI
        art_dir = Path("/root/zensi/test_artifacts")
        art_dir.mkdir(exist_ok=True)
        await page.screenshot(path=str(art_dir / "master_test_zensi_ui.png"))
        print(f"✓ Screenshot gesichert unter {art_dir / 'master_test_zensi_ui.png'}", flush=True)

        await browser.close()
        print("🎉 ALLE 5 ZENSI BAUSTEINE ERFOLGREICH E2E BEFAHREN UND VERIFIZIERT!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
