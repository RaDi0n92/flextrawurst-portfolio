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

        # find all divs with non-zero dimensions in leitstand area
        info = await page.evaluate("""() => {
            // look for the inspector container by any known id/class
            const candidates = ['leit-map', 'leit-inspector', 'leit-right', 'world-inspector',
                                 'leit-wrap', 'leit-layout', 'world-center', 'leit-three'];
            const result = {};
            for (const id of candidates) {
                const el = document.getElementById(id);
                if (el) result[id] = el.getBoundingClientRect();
            }
            // also find visible divs with class containing 'inspector'
            const inspEls = document.querySelectorAll('[class*="insp"]');
            result['insp_count'] = inspEls.length;
            if (inspEls.length > 0) {
                result['first_insp'] = inspEls[0].getBoundingClientRect();
                result['first_insp_id'] = inspEls[0].id;
            }
            return result;
        }""")
        print("Found elements:", info)

        await page.evaluate("() => selectZone('herkunftsraum')")
        await page.wait_for_timeout(300)

        info2 = await page.evaluate("""() => {
            const inspEls = document.querySelectorAll('[id*="insp"],[class*="insp"]');
            const result = {};
            inspEls.forEach((el, i) => {
                const r = el.getBoundingClientRect();
                if (r.width > 0) result[`el_${i}_${el.id||el.className.substring(0,20)}`] = r;
            });
            return result;
        }""")
        print("After selectZone:", info2)

        await browser.close()

asyncio.run(main())
