from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 pg=b.new_page()
 r=pg.goto('http://127.0.0.1:18108/',wait_until='domcontentloaded',timeout=60000)
 print({'status':r.status if r else None,'url':pg.url,'title':pg.title(),'body':pg.locator('body').inner_text()[:3000]})
 pg.screenshot(path='/root/werkraum/_gpt/playwright_root_debug.png',full_page=True)
 b.close()
