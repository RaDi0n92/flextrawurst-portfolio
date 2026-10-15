from playwright.sync_api import sync_playwright
import json, pathlib, time
out = pathlib.Path('/root/werkraum/_gpt/playwright_megavault_bestandsaufnahme')
report = {}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={'width': 1440, 'height': 1000})

    # Gesamtatlas Netz
    page.goto('http://127.0.0.1:18108/', wait_until='networkidle', timeout=90000)
    try:
        page.get_by_text('Netz', exact=True).first.click()
        page.wait_for_load_state('networkidle', timeout=90000)
    except Exception as e:
        report['netz_click_error'] = repr(e)
    report['netz'] = {'url': page.url, 'text': page.locator('body').inner_text()[:30000]}
    page.screenshot(path=str(out/'netz.png'), full_page=True)

    # Megasuche: Suchansicht aktivieren, real suchen, Ergebnis abwarten
    page.goto('http://127.0.0.1:18108/megasuche/', wait_until='networkidle', timeout=90000)
    page.get_by_text('🔍 Live-Suche & Gesamtatlas Hybrid', exact=True).click()
    page.wait_for_timeout(500)
    report['megasuche_search_before'] = page.locator('body').inner_text()[:20000]
    # sichtbares Suchfeld nehmen
    visible_inputs = page.locator('input:visible')
    report['megasuche_visible_inputs'] = visible_inputs.count()
    if visible_inputs.count():
        q = visible_inputs.first
        q.fill('was denkt GENI genau jetzt')
        # sichtbaren Suchen-Knopf in Suchansicht
        btns = page.get_by_text('Suchen', exact=True)
        clicked = False
        for i in range(btns.count()):
            if btns.nth(i).is_visible():
                btns.nth(i).click(); clicked = True; break
        if not clicked:
            q.press('Enter')
        # Warten bis Suchhinweis weg oder 45 s
        for _ in range(90):
            text = page.locator('body').inner_text()
            if 'Durchsuche VPS-Dateisystem' not in text and ('Treffer' in text or 'KI-' in text or 'Ergebnis' in text):
                break
            page.wait_for_timeout(500)
    report['megasuche_search_after'] = {'url': page.url, 'text': page.locator('body').inner_text()[:30000]}
    page.screenshot(path=str(out/'megasuche_search_after.png'), full_page=True)

    # Fragen: WESEN und FACETTEN einzeln
    page.goto('http://127.0.0.1:8055/', wait_until='networkidle', timeout=90000)
    for tab in ('WESEN','FACETTEN'):
        try:
            page.get_by_text(tab, exact=True).first.click()
            page.wait_for_timeout(15000 if tab == 'FACETTEN' else 3000)
            report[f'fragen_{tab.lower()}'] = {'text': page.locator('body').inner_text()[:40000]}
            page.screenshot(path=str(out/f'fragen_{tab.lower()}.png'), full_page=True)
        except Exception as e:
            report[f'fragen_{tab.lower()}'] = {'exception': repr(e), 'text': page.locator('body').inner_text()[:20000]}

    b.close()
(out/'deep_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k: (v.get('url') if isinstance(v,dict) else None) for k,v in report.items()},ensure_ascii=False,indent=2))
