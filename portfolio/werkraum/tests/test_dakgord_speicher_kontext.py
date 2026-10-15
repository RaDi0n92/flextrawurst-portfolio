#!/usr/bin/env python3
"""
Playwright-Tests fuer dak+gords neue Oberflaeche: Kontextfenster,
Gedankenfeld, Container & Memory, Geschichten (web_chat.py, Port 8000).

2026-08-12, Daniel: "klar will ich das memoryysystem und die container und
auch die kontextfensteranzeige usw so wie bei codexium2 ... zum editieren
erstellen und so ... genau so wie die geschichten und so". Portiert aus
codewesen_chat.py, dort schon Playwright-pflichtig (Daniel, 2026-08-03:
"von task 1 an alles rueckwirkend mit playwright pflicht") -- dieselbe
Pflicht gilt hier.
"""
import re

import pytest

BASIS = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def playwright_sitzung():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def seite(playwright_sitzung):
    browser = playwright_sitzung.chromium.launch(args=["--no-sandbox"])
    pg = browser.new_page(viewport={"width": 1400, "height": 900})
    pg._fehler = []
    pg.on("console", lambda m: pg._fehler.append(f"{m.type}: {m.text}")
          if m.type == "error" else None)
    pg.on("pageerror", lambda e: pg._fehler.append(f"pageerror: {e}"))
    pg.goto(f"{BASIS}/", wait_until="networkidle", timeout=30_000)
    pg.wait_for_function(
        "document.getElementById('kf-zahl').textContent !== '…'", timeout=15_000)
    yield pg
    browser.close()


def test_keine_konsolenfehler(seite):
    assert not seite._fehler, seite._fehler


def test_kf_zeigt_echte_zahlen(seite):
    text = seite.inner_text("#kf-zahl")
    assert re.match(r"^\d+ / \d+ \(\d+\.\d+%\)$", text), text
    summe = int(text.split(" / ")[0])
    fenster = int(text.split(" / ")[1].split(" ")[0])
    assert 0 < summe < fenster, f"{summe} von {fenster}"


def test_kf_voll_zeigt_verfassung_und_bausteine(seite):
    seite.click("#kf")
    seite.wait_for_selector("#kf-voll.auf", timeout=5_000)
    try:
        karten = seite.query_selector_all(".kfs")
        assert len(karten) >= 8, f"nur {len(karten)} Schichten (erwartet: 4 Verfassung + organ + 4 Bausteine + verlauf)"
        gruppen = {k.get_attribute("data-gruppe") for k in karten}
        for pflicht in ("verfassung", "organ", "gedankenfeld", "nachrichten",
                        "geschichten", "speicher", "verlauf"):
            assert pflicht in gruppen, f"Schicht-Gruppe {pflicht} fehlt: {gruppen}"
    finally:
        seite.click("#kf-voll-zu")
        seite.wait_for_selector("#kf-voll", state="hidden", timeout=5_000)


def test_escape_schliesst_kontextfenster(seite):
    seite.click("#kf")
    seite.wait_for_selector("#kf-voll.auf", timeout=5_000)
    seite.keyboard.press("Escape")
    seite.wait_for_selector("#kf-voll", state="hidden", timeout=5_000)


def test_sp_voll_oeffnet_mit_allen_vier_spalten(seite):
    seite.click("#sp")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    try:
        spalten = seite.query_selector_all(".sp-spalte > h3")
        titel = {s.inner_text() for s in spalten}
        assert {"BEHÄLTER", "MEMORY", "GEDANKENFELD", "GESCHICHTEN"} <= titel, titel
    finally:
        seite.click("#sp-voll-zu")
        seite.wait_for_selector("#sp-voll", state="hidden", timeout=5_000)


def test_gedanke_anlegen_zeigen_entfernen(seite):
    """Der komplette Rundlauf: anlegen -> im Panel sichtbar -> im
    Kontextfenster sichtbar -> entfernen -> weg. Kein API-Test -- echte
    Klicks, echte Formulare."""
    marke = "PYTEST-DAKGORD-GEDANKE"
    seite.click("#sp")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    try:
        seite.fill("#gf-neu-text", marke)
        seite.click("#gf-neu-btn")
        seite.wait_for_function(
            "document.getElementById('gf-liste').textContent.includes('" + marke + "')",
            timeout=8_000,
        )
        karte = seite.query_selector(f".gfd:has-text('{marke}')")
        assert karte is not None, "Gedanke nicht in der Liste erschienen"
        gid = karte.get_attribute("data-gid")

        # Im Kontextfenster nachschauen -- derselbe Text, echte Tokenzahl
        seite.click("#kf-voll-zu") if seite.query_selector("#kf-voll.auf") else None
        kontext = seite.request.get(f"{BASIS}/api/kontext").json()
        gedankenfeld_schicht = next(s for s in kontext["schichten"] if s["gruppe"] == "gedankenfeld")
        assert marke in gedankenfeld_schicht["inhalt"], "Gedanke nicht im echten Kontext angekommen"
        assert gedankenfeld_schicht["tokens"] > 0

        # Aufraeumen: entfernen
        karte.query_selector(".weg-btn").click()
        seite.wait_for_function(
            "!document.getElementById('gf-liste').textContent.includes('" + marke + "')",
            timeout=8_000,
        )
        kontext_danach = seite.request.get(f"{BASIS}/api/kontext").json()
        gedankenfeld_danach = next(s for s in kontext_danach["schichten"] if s["gruppe"] == "gedankenfeld")
        assert marke not in gedankenfeld_danach["inhalt"], "Gedanke nach Entfernen noch im Kontext"
    finally:
        if seite.query_selector("#sp-voll.auf"):
            seite.click("#sp-voll-zu")


def test_container_anlegen_eintrag_hinzufuegen_entfernen(seite):
    """Locator statt Element-Handle: ladeSpeicher() rendert #sp-container-liste
    nach jeder Aktion komplett neu, ein einmal geholter Element-Handle wird
    dabei ungueltig. Locator loest sich bei jeder Aktion neu auf."""
    seite.click("#sp")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    try:
        import time as _time
        name = f"PYTEST-Behaelter-{int(_time.time())}"
        box = seite.locator(f".sp-box:has-text('{name}')")

        seite.fill("#sp-neuer-name", name)
        seite.click("#sp-neu-btn")
        box.wait_for(timeout=8_000)

        box.locator(".sp-eintrag-add input").fill("PYTEST-Eintrag")
        box.locator(".sp-eintrag-add button").click()
        seite.wait_for_function(
            "document.getElementById('sp-container-liste').textContent.includes('PYTEST-Eintrag')",
            timeout=8_000,
        )

        box.locator(".sp-box-weg").click()
        seite.wait_for_function(
            "!document.getElementById('sp-container-liste').textContent.includes('" + name + "')",
            timeout=8_000,
        )
    finally:
        if seite.query_selector("#sp-voll.auf"):
            seite.click("#sp-voll-zu")


def test_geschichte_einsetzen_und_entfernen(seite):
    seite.click("#sp")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    try:
        seite.fill("#ge-titel", "PYTEST-Geschichte")
        seite.fill("#ge-text", "Ein Testtext fuer die Geschichten-Schicht.")
        seite.click("#ge-einsetzen")
        seite.wait_for_function(
            "document.getElementById('ge-liste').textContent.includes('PYTEST-Geschichte')",
            timeout=8_000,
        )
        box = seite.query_selector(".sp-box[data-gid]:has-text('PYTEST-Geschichte')")
        assert box is not None
        gid = box.get_attribute("data-gid")
        box.query_selector(".ge-weg").click()
        seite.wait_for_function(
            "!document.getElementById('ge-liste').textContent.includes('PYTEST-Geschichte')",
            timeout=8_000,
        )
    finally:
        if seite.query_selector("#sp-voll.auf"):
            seite.click("#sp-voll-zu")
