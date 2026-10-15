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

        # find layout
        info = await page.evaluate("""() => {
            const ids = ['world-center','leit-inspector','leit-right','inspector',
                         'leit-layout','leit-left','leit-main','leit-rail'];
            const r = {};
            for (const id of ids) {
                const el = document.getElementById(id);
                if (el) { const b = el.getBoundingClientRect(); if (b.width > 0) r[id] = b; }
            }
            // also grab all visible divs with 'insp' in id
            document.querySelectorAll('[id]').forEach(el => {
                if (el.id.includes('insp') || el.id.includes('leit') || el.id.includes('rail')) {
                    const b = el.getBoundingClientRect();
                    if (b.width > 0) r[el.id] = b;
                }
            });
            return r;
        }""")
        print("Leitstand elements:", info)

        # full screenshot
        await page.screenshot(path="screenshots/leit_gesamt2.png")

        await browser.close()

asyncio.run(main())
