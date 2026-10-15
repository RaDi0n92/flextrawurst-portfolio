#!/usr/bin/env python3
"""
test_playwright_provenienz_e2e.py — Playwright Browser E2E Test für Zensi UI Export/Import & Telemetrie.
"""
import sys
from playwright.sync_api import sync_playwright

def run_playwright_test():
    print("🎭 Starte Playwright E2E Browser Test für Zensi UI...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # 1. Navigiere zu Zensi UI
        page.goto("http://127.0.0.1:8043/zensi/")
        page.wait_for_selector("#session-bar", state="attached")

        # 2. Prüfe Telemetrie-Badge & Header
        page.wait_for_selector("#physio-badge-text", state="attached")
        badge_text = page.inner_text("#physio-badge-text")
        print(f"✅ 1. Zensi UI geladen: Telemetrie-Badge = '{badge_text}'")

        # 3. Prüfe Export/Import Buttons im Session-Bar
        session_bar_html = page.inner_html("#session-bar")
        assert "exportSessionMarkdown()" in session_bar_html
        assert "triggerImportMarkdown()" in session_bar_html
        assert "exportLangGraphDB" in session_bar_html
        print("✅ 2. Session Export/Import & Audit Buttons im DOM vorhanden")

        # 4. Prüfe Mutator Modal Button
        page.wait_for_selector("button:has-text('mutator')", state="attached")
        print("✅ 3. Zensi Mutationskammer Mutator-Button im DOM vorhanden")

        # Keine echten Konsolen-Abstürze
        if console_errors:
            print(f"⚠️ Warnung: Browser-Konsole meldet Errors: {console_errors}")
        else:
            print("✅ 4. Keine kritischen JavaScript-Fehler in der Browser-Konsole")

        browser.close()
        print("\n🎉 PLAYWRIGHT E2E BROWSER TEST VOLLSTÄNDIG ERFOLGREICH!")

if __name__ == "__main__":
    run_playwright_test()
