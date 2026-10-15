"""Visible Playwright proof for the reference-driven Bridge Surface."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from augen_haende_bridge.reference_surface import start_server


ROOT = Path(__file__).resolve().parent
EVIDENCE_DIR = ROOT / "evidence"


def run_proof() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    server, _runtime = start_server()
    try:
        with sync_playwright() as playwright:
            executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or shutil.which("chromium")
            options = {"headless": True}
            if executable:
                options["executable_path"] = executable
            browser = playwright.chromium.launch(**options)
            page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
            page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="networkidle")

            # Reference shell: this is a spatial bridge surface, not a proof homepage.
            expect(page.get_by_test_id("reference-surface")).to_be_visible()
            expect(page.get_by_test_id("reference-status")).to_contain_text("kein Homepage-Modus")
            expect(page.locator(".diamond")).to_have_count(4)
            expect(page.locator(".terminal")).to_have_count(4)
            expect(page.get_by_test_id("regie-panel")).to_be_visible()
            expect(page.get_by_test_id("target-rail")).to_be_visible()
            page.screenshot(path=str(EVIDENCE_DIR / "playwright_b4_6_reference_surface.png"), full_page=True)

            # Target binding and individual camera/microphone controls are live DOM actions.
            page.get_by_role("button", name="Linux KDE Desktop 1").click()
            expect(page.get_by_test_id("desktop-mode")).to_have_text("Linux KDE Desktop 1")
            page.get_by_role("button", name="aus", exact=True).nth(0).click()
            expect(page.get_by_role("button", name="an", exact=True).nth(0)).to_be_visible()
            page.get_by_role("button", name="aus", exact=True).nth(0).click()
            page.get_by_role("button", name="Spruch senden").click()
            expect(page.get_by_test_id("toast")).to_contain_text("Regiespruch")

            # Each terminal owns its own scanner menu; transparency is independently adjustable.
            page.locator('[data-action="scanner"][data-target-id="terminal-2"]').click()
            expect(page.locator('[data-scanner-menu="terminal-2"]')).to_have_class("scanner-menu open")
            page.locator('[data-testid="opacity-control"]').fill("48")
            expect(page.get_by_test_id("surface-readback")).to_contain_text('"opacity": 0.48')

            # A draggable diamond is part of the surface rather than a static card.
            diamond = page.locator('[data-node-id="agent-codex"]')
            box = diamond.bounding_box()
            assert box is not None
            # Start in the geometric center: the diamond is rotated, so its
            # bounding-box corner can be outside the actual hit area.
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            page.mouse.move(center_x, center_y)
            page.mouse.down()
            page.mouse.move(center_x + 80, center_y + 40)
            page.mouse.up()
            expect(page.get_by_test_id("surface-readback")).to_contain_text('"action": "move-node"')
            page.screenshot(path=str(EVIDENCE_DIR / "playwright_b4_6_reference_surface_interaction.png"), full_page=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run_proof()
