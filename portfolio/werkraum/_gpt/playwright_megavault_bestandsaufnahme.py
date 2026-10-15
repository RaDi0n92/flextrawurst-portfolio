from playwright.sync_api import sync_playwright
import json, time, pathlib

out = pathlib.Path('/root/werkraum/_gpt/playwright_megavault_bestandsaufnahme')
out.mkdir(parents=True, exist_ok=True)
urls = {
    'gesamtatlas': 'http://127.0.0.1:18108/',
    'suche': 'http://127.0.0.1:18108/suche',
    'megasuche': 'http://127.0.0.1:18108/megasuche/',
    'megavault': 'http://127.0.0.1:18108/megavault',
    'fragen': 'http://127.0.0.1:8055/',
}
report = {}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    for name, url in urls.items():
        entry = {'url': url}
        try:
            response = page.goto(url, wait_until='networkidle', timeout=90000)
            entry['status'] = response.status if response else None
            entry['title'] = page.title()
            entry['body_text'] = page.locator('body').inner_text(timeout=10000)[:30000]
            entry['links'] = page.locator('a').all_inner_texts()[:100]
            entry['buttons'] = page.locator('button').all_inner_texts()[:100]
            entry['inputs'] = page.locator('input').count()
            entry['textareas'] = page.locator('textarea').count()
            entry['selects'] = page.locator('select').count()
            entry['errors_console'] = []
            page.screenshot(path=str(out / f'{name}.png'), full_page=True)
        except Exception as e:
            entry['exception'] = repr(e)
        report[name] = entry

    # Teste die sichtbare Suchseite mit einer realen Frage.
    page.goto(urls['megasuche'], wait_until='networkidle', timeout=90000)
    inputs = page.locator('input')
    if inputs.count():
        candidate = inputs.first
        candidate.fill('was denkt GENI genau jetzt')
        candidate.press('Enter')
        try:
            page.wait_for_load_state('networkidle', timeout=90000)
        except Exception:
            time.sleep(8)
        report['megasuche_test'] = {
            'url': page.url,
            'body_text': page.locator('body').inner_text()[:30000],
        }
        page.screenshot(path=str(out / 'megasuche_test.png'), full_page=True)

    # Teste /fragen über UI, ohne den aktuellen Zustand zu verändern.
    page.goto(urls['fragen'], wait_until='networkidle', timeout=90000)
    txt = page.locator('textarea')
    inp = page.locator('input')
    field = txt.first if txt.count() else (inp.first if inp.count() else None)
    if field is not None:
        field.fill('was denkt GENI genau jetzt')
        buttons = page.locator('button')
        if buttons.count():
            buttons.first.click()
        else:
            field.press('Enter')
        try:
            page.wait_for_timeout(30000)
        except Exception:
            pass
        report['fragen_test'] = {
            'url': page.url,
            'body_text': page.locator('body').inner_text()[:30000],
        }
        page.screenshot(path=str(out / 'fragen_test.png'), full_page=True)

    browser.close()

(out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: {x:v for x,v in val.items() if x in ('url','status','title','inputs','textareas','selects','exception')} for k,val in report.items()}, ensure_ascii=False, indent=2))
print('REPORT', out / 'report.json')
