#!/usr/bin/env python3
"""
Playwright-Tests fuer GENIs Kontextanzeige (dialog.py, Port 8020).

2026-08-12, Daniel: "die anderen 6 wesen auch mal echt testen" galt am 04.08.
fuer codewesen_chat.py -- dieselbe Pflicht gilt hier: Struktur pruefen reicht
nicht, es muss ein echter Browser gegen den echten Dienst laufen (Regel aus
tests/test_codewesen_chat_kontext_rag.py, Daniel 2026-08-03: "von task 1 an
alles rueckwirkend mit playwright pflicht").

GENI terminiert HTTPS selbst mit einem selbstsignierten Zertifikat (bewusst
lokal, siehe docs/systemdoku/11_geni.md) -- deshalb ignore_https_errors.
"""
import re

import pytest

BASIS = "https://127.0.0.1:8020"


@pytest.fixture(scope="session")
def playwright_sitzung():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def seite(playwright_sitzung):
    browser = playwright_sitzung.chromium.launch(args=["--no-sandbox", "--ignore-certificate-errors"])
    pg = browser.new_page(viewport={"width": 1400, "height": 900}, ignore_https_errors=True)
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


def test_kf_balken_hat_segmente(seite):
    segmente = seite.query_selector_all("#kf-balken div")
    assert len(segmente) >= 1, "kein Segment im Balken"


def test_modell_anzeige_zeigt_das_echte_modell(seite):
    """Bis 2026-08-12 stand hier ein Dropdown mit 'blitz -- e2b'/'tief -- e4b' --
    tote Auswahl, MODELLE-Dict wurde nie gelesen. Ersetzt durch eine echte
    Anzeige ueber /api/modell."""
    text = seite.inner_text("#modell-label")
    assert "hauhaucs" in text, text
    assert "e2b" not in text and "e4b" not in text, \
        f"alte gemma4-Bezeichnung noch sichtbar: {text!r}"


def test_kein_totes_dropdown_mehr_im_dom(seite):
    assert seite.query_selector("#modell-select") is None


def test_kf_voll_oeffnet_und_zeigt_schichten(seite):
    seite.click("#kf")
    seite.wait_for_selector("#kf-voll.auf", timeout=5_000)
    try:
        karten = seite.query_selector_all(".kfs")
        assert len(karten) >= 5, f"nur {len(karten)} Schichten sichtbar"

        gruppen = {k.get_attribute("data-gruppe") for k in karten}
        assert "systemprompt" in gruppen
        assert "verlauf" in gruppen

        erste = karten[0]
        assert erste.get_attribute("data-tokens") is not None
    finally:
        seite.click("#kf-voll-zu")
        seite.wait_for_selector("#kf-voll", state="hidden", timeout=5_000)


def test_schicht_klappt_auf_und_zeigt_text(seite):
    seite.click("#kf")
    seite.wait_for_selector("#kf-voll.auf", timeout=5_000)
    try:
        erste_kopf = seite.query_selector(".kfs .kfs-kopf")
        erste_kopf.click()
        box = seite.query_selector(".kfs.auf .kfs-text")
        assert box is not None, "Schicht ging nach Klick nicht auf"
        assert len(seite.inner_text(".kfs.auf .kfs-text").strip()) > 0
    finally:
        seite.click("#kf-voll-zu")
        seite.wait_for_selector("#kf-voll", state="hidden", timeout=5_000)


def test_escape_schliesst_die_vollansicht(seite):
    seite.click("#kf")
    seite.wait_for_selector("#kf-voll.auf", timeout=5_000)
    seite.keyboard.press("Escape")
    seite.wait_for_selector("#kf-voll", state="hidden", timeout=5_000)


def test_eingabe_aktiviert_gedaechtnisabruf_live(seite):
    """GENI-Besonderheit gegenueber den Wesen-Chats: Resonanz/Gedaechtnisabruf/
    Direktzugriff sind eingabeabhaengig. Ein Signalwort im Textfeld muss die
    Schicht live aufleuchten lassen, ohne dass gesendet wird."""
    feld = seite.query_selector("#eingabe")
    feld.fill("")
    seite.wait_for_timeout(700)  # Debounce (400ms) + Netzwerk-Rundlauf
    vorher = seite.inner_text("#kf-zahl")

    feld.fill("was hast du heute alles beobachtet")
    seite.wait_for_timeout(700)
    nachher = seite.inner_text("#kf-zahl")

    assert vorher != nachher, \
        f"Kontextanzeige aendert sich nicht mit der Eingabe: {vorher!r} == {nachher!r}"
    assert int(nachher.split(" / ")[0]) > int(vorher.split(" / ")[0]), \
        "Gedaechtnisabruf-Schicht sollte die Tokenzahl erhoehen, nicht senken"
