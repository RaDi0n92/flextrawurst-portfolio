import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 900})
        await page.goto("http://localhost:8787/flextrawurst_surface.html", wait_until="networkidle")
        await page.evaluate("() => { const s = document.getElementById('splash'); if (s) s.remove(); }")
        await page.wait_for_timeout(400)
        await page.evaluate("() => switchView('leitstand')")
        await page.wait_for_timeout(700)

        # full leitstand
        await page.screenshot(path="screenshots/leit2_gesamt.png")

        # left rail
        await page.screenshot(path="screenshots/leit2_rail.png", clip={"x": 0, "y": 112, "width": 252, "height": 726})

        # herkunftsraum inspector
        await page.evaluate("() => selectZone('herkunftsraum')")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/leit2_insp_herkunft.png", clip={"x": 1287, "y": 112, "width": 313, "height": 600})

        # weltfoyer inspector (BEGRIFFSPRÜFUNG)
        await page.evaluate("() => selectZone('weltfoyer')")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/leit2_insp_weltfoyer.png", clip={"x": 1287, "y": 112, "width": 313, "height": 600})

        # stille_zone inspector (also BEGRIFFSPRÜFUNG)
        await page.evaluate("() => selectZone('stille_zone')")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/leit2_insp_stille.png", clip={"x": 1287, "y": 112, "width": 313, "height": 600})

        # scroll rail to Weltorgane section and screenshot
        await page.evaluate("() => { const r = document.getElementById('left-rail'); if(r) r.scrollTop = 600; }")
        await page.wait_for_timeout(200)
        await page.screenshot(path="screenshots/leit2_rail_weltorgane.png", clip={"x": 0, "y": 112, "width": 252, "height": 726})

        await browser.close()
        print("Done")

asyncio.run(main())
