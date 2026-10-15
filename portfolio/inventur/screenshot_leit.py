import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 900})
        await page.goto("http://localhost:8787/flextrawurst_surface.html", wait_until="networkidle")

        # dismiss splash
        await page.evaluate("() => { const s = document.getElementById('splash'); if (s) s.remove(); }")
        await page.wait_for_timeout(400)

        # go to LEITSTAND (räume tab)
        await page.evaluate("() => switchView('raume')")
        await page.wait_for_timeout(600)

        # full page
        await page.screenshot(path="screenshots/leit_gesamt.png")

        # left rail
        await page.screenshot(path="screenshots/leit_rail.png", clip={"x": 0, "y": 50, "width": 260, "height": 850})

        # right panel — herkunftsraum
        await page.evaluate("() => selectZone('herkunftsraum')")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/leit_insp_herkunft.png", clip={"x": 1280, "y": 50, "width": 320, "height": 550})

        # right panel — weltfoyer (BEGRIFFSPRÜFUNG)
        await page.evaluate("() => selectZone('weltfoyer')")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/leit_insp_weltfoyer.png", clip={"x": 1280, "y": 50, "width": 320, "height": 550})

        await browser.close()
        print("Done")

asyncio.run(main())
