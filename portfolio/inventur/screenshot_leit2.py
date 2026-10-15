import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 900})
        await page.goto("http://localhost:8787/flextrawurst_surface.html", wait_until="networkidle")
        await page.evaluate("() => { const s = document.getElementById('splash'); if (s) s.remove(); }")
        await page.wait_for_timeout(400)
        await page.evaluate("() => switchView('raume')")
        await page.wait_for_timeout(600)

        # find inspector position
        info = await page.evaluate("""() => {
            const rp = document.getElementById('right-panel');
            const insp = document.getElementById('inspector');
            const lc = document.getElementById('leit-container');
            return {
                rp: rp ? rp.getBoundingClientRect() : null,
                insp: insp ? insp.getBoundingClientRect() : null,
                lc: lc ? lc.getBoundingClientRect() : null,
            };
        }""")
        print("Layout:", info)

        # click herkunftsraum
        await page.evaluate("() => selectZone('herkunftsraum')")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/leit_full_herkunft.png")

        await page.evaluate("() => selectZone('weltfoyer')")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/leit_full_weltfoyer.png")

        await browser.close()

asyncio.run(main())
