import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8787/flextrawurst_surface.html", wait_until="networkidle")
        await page.evaluate("() => { const s = document.getElementById('splash'); if (s) s.remove(); }")
        await page.wait_for_timeout(400)
        await page.evaluate("() => switchView('uber')")
        await page.wait_for_timeout(500)

        # hero + nav
        await page.screenshot(path="screenshots/uber_top.png", clip={"x": 0, "y": 0, "width": 1400, "height": 900})

        # Was Wesen können section
        await page.evaluate("() => document.getElementById('ub-wesen-koennen')?.scrollIntoView({block:'start'})")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/uber_wesen_koennen.png")

        # Was Menschen können section
        await page.evaluate("() => document.getElementById('ub-menschlich')?.scrollIntoView({block:'start'})")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/uber_menschen_koennen.png")

        # Splitter section
        await page.evaluate("() => document.getElementById('ub-splitter-erkl')?.scrollIntoView({block:'start'})")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/uber_splitter.png")

        # KompOase section
        await page.evaluate("() => document.getElementById('ub-kompoase-erkl')?.scrollIntoView({block:'start'})")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/uber_kompoase.png")

        # Herkunft section
        await page.evaluate("() => document.getElementById('ub-herkunft')?.scrollIntoView({block:'start'})")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/uber_herkunft.png")

        # Vor-Einzug section
        await page.evaluate("() => document.getElementById('ub-vor-einzug')?.scrollIntoView({block:'start'})")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshots/uber_vor_einzug.png")

        await browser.close()
        print("Done")

asyncio.run(main())
