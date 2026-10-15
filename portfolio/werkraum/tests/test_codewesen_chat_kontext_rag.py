#!/usr/bin/env python3
"""
Playwright-Tests fuer den Codewesen-Chat (Port 8002).

Deckt ab:
  Track 1 — RAG im Chatpfad (Selbstsuche, Rueckfall, Platzierung des Blocks)
  Track 2 — ehrliche Kontextfenster-Anzeige (echte Tokenzahlen, Schichten, UI)

Aufruf:
  python3 -m pytest tests/test_codewesen_chat_kontext_rag.py -v

Bewusst gegen den LAUFENDEN Dienst getestet, nicht gegen eine Testinstanz: die
Anzeige soll ja gerade beweisen, dass sie den echten Zustand zeigt. Ein Mock
haette genau die Aussage zerstoert, um die es geht.

## Regel fuer alles Weitere (Daniel, 2026-08-03)

    "von task 1 an alles rueckwirkend mit playwright pflicht"

Verbindlich heisst das: **jede Faehigkeit braucht mindestens einen Test, der
einen echten Browser fuehrt** -- klickt, tippt, liest was auf dem Schirm steht.
Nicht: jede einzelne Zusicherung muss durch den Browser. Drei Sorten Test leben
hier nebeneinander, und die Reihenfolge ist eine Rangfolge:

1. Browser (Mehrheit) -- fuehrt die Oberflaeche. Liest die Kontextanzeige ueber
   data-gruppe/data-tokens aus dem DOM, nicht ueber den Endpunkt: geprueft wird,
   was Daniel sieht, nicht was der Server behauptet.
2. Endpunkt -- fuer Vertraege und Fehlerwege ohne Oberflaeche (400/404,
   Budgetgrenze, ungueltige Laenge, abgewiesene Pfade). Dafuer eine Oberflaeche
   zu erfinden, nur damit ein Test sie klicken kann, waere Selbstbetrug.
3. Unterprozess -- fuer Interna ohne HTTP-Flaeche (Markerauswertung,
   Pfad-Whitelist, Promptaufbau). Diese als Endpunkt freizulegen waere eine
   Sicherheitsluecke fuer einen Testkomfort.

Wer hier etwas ergaenzt: erst 1, dann 2, dann 3 -- und ohne mindestens einen
Browser-Test ist eine neue Faehigkeit nicht fertig.
"""
import re
import subprocess
import sys

import pytest

BASIS = "http://127.0.0.1:8002"
WESEN = "Schorschel"


# ── Hilfsmittel ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_sitzung():
    """Genau EINE sync_playwright()-Sitzung fuer die ganze Datei -- zwei
    gleichzeitige im selben Prozess sind nicht erlaubt und brachen den
    Gesamtlauf mit 21 Fehlern ab (einzeln liefen dieselben Tests gruen)."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def seite(playwright_sitzung):
    browser = playwright_sitzung.chromium.launch(args=["--no-sandbox"])
    if True:
        pg = browser.new_page(viewport={"width": 1280, "height": 820})
        pg._konsolenfehler = []
        pg.on("console", lambda m: pg._konsolenfehler.append(f"{m.type}: {m.text}")
              if m.type == "error" else None)
        pg.on("pageerror", lambda e: pg._konsolenfehler.append(f"pageerror: {e}"))
        pg.goto(f"{BASIS}/chat/{WESEN}", wait_until="networkidle", timeout=60_000)
        pg.wait_for_function("document.getElementById('kf-zahl').textContent !== '…'",
                             timeout=30_000)
        yield pg
        browser.close()


@pytest.fixture(scope="module")
def kontext(seite):
    antwort = seite.request.get(f"{BASIS}/api/kontext/{WESEN}", timeout=60_000)
    assert antwort.ok, f"/api/kontext antwortete {antwort.status}"
    return antwort.json()


def _im_dienst(quelltext: str) -> str:
    """Fuehrt Python im Kontext von codewesen_chat aus (fuer die Backend-Teile
    von Track 1, die keine eigene HTTP-Oberflaeche haben)."""
    ergebnis = subprocess.run(
        [sys.executable, "-c", "import sys; sys.argv=['t']; "
         "sys.path.insert(0,'/root/werkraum'); "
         "import codewesen_chat as cc\n" + quelltext],
        capture_output=True, text=True, timeout=300, cwd="/root/werkraum",
    )
    assert ergebnis.returncode == 0, f"Teilprozess fehlgeschlagen:\n{ergebnis.stderr[-2000:]}"
    return ergebnis.stdout



# ── Browser-Helfer: die Kontextanzeige aus dem DOM lesen ──────────────────────
# Daniels Vorgabe (2026-08-03): "von task 1 an alles rueckwirkend mit playwright
# pflicht". Die Schicht-Karten tragen dafuer data-gruppe/data-tokens/
# data-geschaetzt, damit eine Pruefung wirklich das sieht, was auf dem Schirm
# steht -- und nicht nur das, was der Endpunkt behauptet.

def schichten_aus_dom(pg) -> list[dict]:
    # Die Karten werden von ladeKontext() immer gezeichnet, auch solange die
    # Vollansicht zugeklappt ist -- also nicht aufklappen. Ein offen gelassenes
    # Overlay hat sonst die Klicks der nachfolgenden Tests abgefangen
    # ("subtree intercepts pointer events"), gefunden 2026-08-03.
    pg.wait_for_selector(".kfs", state="attached", timeout=10_000)
    return pg.eval_on_selector_all(".kfs", """(karten) => karten.map(k => ({
        gruppe: k.dataset.gruppe,
        tokens: parseInt(k.dataset.tokens, 10),
        geschaetzt: k.dataset.geschaetzt === "1",
        titel: k.querySelector(".kfs-titel").textContent,
        inhalt: k.querySelector(".kfs-text").textContent
    }))""")


def schicht_aus_dom(pg, gruppe: str) -> dict:
    treffer = [s for s in schichten_aus_dom(pg) if s["gruppe"] == gruppe]
    assert len(treffer) == 1, f"{len(treffer)} Schichten der Gruppe {gruppe} im DOM"
    return treffer[0]


def kopfzahlen_aus_dom(pg) -> tuple[int, int]:
    """summe, slot_ctx -- so wie sie im Panel stehen."""
    text = pg.inner_text("#kf-zahl")
    m = re.match(r"^(\d+) / (\d+)", text)
    assert m, f"Panelzahl unlesbar: {text!r}"
    return int(m.group(1)), int(m.group(2))

# ── Track 2: Kontextfenster-Anzeige, Datenebene ────────────────────────────────

def test_endpunkt_liefert_pflichtfelder(kontext):
    for feld in ("wesen", "slot_ctx", "summe_tokens", "frei", "auslastung",
                 "schichten", "gemessen_am"):
        assert feld in kontext, f"Feld {feld} fehlt in /api/kontext"
    assert kontext["wesen"] == WESEN


def test_slot_ctx_im_dom_kommt_vom_echten_server(seite):
    """Die Zahl auf dem Schirm muss die des laufenden Servers sein."""
    props = seite.request.get("http://127.0.0.1:11436/props", timeout=30_000).json()
    echt = props.get("default_generation_settings", {}).get("n_ctx")
    _, ctx_dom = kopfzahlen_aus_dom(seite)
    assert ctx_dom == echt, f"Anzeige sagt {ctx_dom}, Server sagt {echt}"


def test_slot_ctx_kommt_vom_echten_server(kontext, seite):
    """Die Fenstergroesse muss die des laufenden llama-servers sein, keine
    fest verdrahtete Zahl. Gegenbeispiel im System: zensi/server.py:175 traegt
    66816, waehrend der Server 17408 faehrt."""
    props = seite.request.get("http://127.0.0.1:11436/props", timeout=30_000).json()
    echt = props.get("default_generation_settings", {}).get("n_ctx")
    assert kontext["slot_ctx"] == echt, (
        f"Anzeige sagt {kontext['slot_ctx']}, Server sagt {echt}")


def test_tokenzahlen_sind_im_dom_gemessen_nicht_geschaetzt(seite, kontext):
    geschaetzt_dom = [s["titel"] for s in schichten_aus_dom(seite) if s["geschaetzt"]]
    assert not geschaetzt_dom, f"Anzeige weist geschaetzte Zahlen aus: {geschaetzt_dom}"


def test_tokenzahlen_sind_gemessen_nicht_geschaetzt(kontext):
    """Solange /tokenize erreichbar ist, darf keine Schicht als geschaetzt
    markiert sein. Ist sie es doch, muss das sichtbar ausgewiesen werden --
    dann schlaegt dieser Test bewusst fehl statt still zu schoenen."""
    geschaetzt = [s["titel"] for s in kontext["schichten"] if s.get("geschaetzt")]
    assert not geschaetzt, f"geschaetzte statt gemessene Schichten: {geschaetzt}"


def test_summe_stimmt_im_dom_mit_den_schichten_ueberein(seite, kontext):
    summe_dom, ctx_dom = kopfzahlen_aus_dom(seite)
    assert summe_dom == sum(s["tokens"] for s in schichten_aus_dom(seite)), \
        "die angezeigte Summe passt nicht zu den angezeigten Karten"
    assert ctx_dom == kontext["slot_ctx"]
    assert kontext["frei"] == kontext["slot_ctx"] - kontext["summe_tokens"]
    assert 0 <= kontext["auslastung"] <= 1


def test_alle_gruppen_stehen_im_dom(seite, kontext):
    gruppen = {s["gruppe"] for s in schichten_aus_dom(seite)}
    assert {"systemprompt", "verlauf", "gedankenfeld", "nachrichten",
            "geschichten", "speicher", "rag"} <= gruppen, f"fehlt: {gruppen}"
    assert gruppen == {s["gruppe"] for s in kontext["schichten"]}, \
        "Anzeige und Endpunkt zeigen verschiedene Gruppen"


def test_systemprompt_ist_im_dom_zerlegt_nicht_ein_klotz(seite):
    teile = [s for s in schichten_aus_dom(seite) if s["gruppe"] == "systemprompt"]
    assert len(teile) >= 5, f"nur {len(teile)} Systemprompt-Karten im DOM"
    titel = {t["titel"] for t in teile}
    assert "Dein Wesen-Profil" in titel and "Werkzeuge" in titel


def test_schichten_zeigen_im_dom_ihren_volltext(seite, kontext):
    """'komplett einsehbar' heisst: der ganze Text steht auf dem Schirm, nicht
    nur in der Antwort des Endpunkts."""
    aus_dom = {s["gruppe"] + s["titel"]: s for s in schichten_aus_dom(seite)}
    for s in kontext["schichten"]:
        if s["tokens"] == 0:
            continue
        assert len(s["inhalt"]) == s["zeichen"]
        karte = aus_dom[s["gruppe"] + s["titel"]]
        assert karte["tokens"] == s["tokens"]
        if s["gruppe"] == "verlauf":
            # Diese Schicht wird bewusst nicht als Rohtext gezeichnet, sondern
            # als Satz- und Wortauswahl (Track 3). Die [rolle]-Praefixe sind
            # reine Lesehilfe der Antwort und stehen deshalb nicht im DOM --
            # geprueft wird darum der tatsaechliche Nachrichtentext.
            for eintrag in s["eintraege"]:
                probe = eintrag["inhalt"][:40].strip()
                if probe:
                    assert probe in karte["inhalt"], \
                        f"Verlaufseintrag fehlt in der Anzeige: {probe!r}"
        else:
            assert s["inhalt"][:60].strip() in karte["inhalt"], \
                f"Schicht '{s['titel']}' zeigt im DOM nicht ihren Inhalt"


def test_anzeige_deckt_sich_mit_dem_echten_promptbau(kontext):
    """Kernversprechen: die Anzeige zeigt, was wirklich gebaut wird. Deshalb
    hier gegen baue_system_prompt() selbst geprueft, nicht gegen einen Nachbau."""
    ausgabe = _im_dienst(
        f"print(len(cc.baue_system_prompt({WESEN!r})))\n"
        f"print(len(cc.lade_chat_verlauf({WESEN!r}, max_eintraege=8)))\n"
    )
    prompt_zeichen, verlauf_eintraege = (int(z) for z in ausgabe.split())
    anzeige_zeichen = sum(s["zeichen"] for s in kontext["schichten"]
                          if s["gruppe"] == "systemprompt")
    # Die Zerlegung schneidet die '=== ... ==='-Marken heraus, daher nie exakt
    # gleich -- aber die Groessenordnung muss stimmen (>85 % erhalten).
    assert anzeige_zeichen > prompt_zeichen * 0.85, (
        f"Anzeige zeigt {anzeige_zeichen} von {prompt_zeichen} Zeichen")
    verlauf_schicht = next(s for s in kontext["schichten"] if s["gruppe"] == "verlauf")
    assert str(verlauf_eintraege) in verlauf_schicht["titel"]


# ── Track 2: Kontextfenster-Anzeige, Oberflaeche ───────────────────────────────

def test_panel_zeigt_zahl_im_erwarteten_format(seite):
    text = seite.inner_text("#kf-zahl")
    assert re.match(r"^\d+ / \d+ \(\d+\.\d+%\)$", text), f"unerwartet: {text!r}"


def test_balken_hat_segmente_und_legende(seite):
    assert seite.eval_on_selector_all("#kf-balken div", "e => e.length") >= 2
    legende = seite.inner_text("#kf-legende")
    assert "Systemprompt" in legende and "Verlauf" in legende


def test_balken_bezieht_sich_aufs_echte_fenster_nicht_auf_die_summe(seite, kontext):
    """Sonst saehe ein fast leeres Fenster aus wie ein volles."""
    breiten = seite.eval_on_selector_all(
        "#kf-balken div", "e => e.map(x => parseFloat(x.style.width))")
    assert abs(sum(breiten) - kontext["auslastung"] * 100) < 1.0, (
        f"Balken summiert {sum(breiten):.1f}%, Auslastung ist "
        f"{kontext['auslastung']*100:.1f}%")


def test_vollansicht_oeffnet_und_zeigt_alle_schichten(seite, kontext):
    seite.click("#kf")
    seite.wait_for_selector("#kf-voll.auf", timeout=5_000)
    assert seite.eval_on_selector_all(".kfs", "e => e.length") == len(kontext["schichten"])


def test_schicht_klappt_auf_und_zeigt_text(seite):
    seite.click(".kfs:first-child .kfs-kopf")
    seite.wait_for_timeout(300)
    assert seite.is_visible(".kfs:first-child .kfs-text")
    assert len(seite.inner_text(".kfs:first-child .kfs-text").strip()) > 20


def test_escape_schliesst_die_vollansicht(seite):
    seite.keyboard.press("Escape")
    seite.wait_for_timeout(300)
    assert not seite.is_visible("#kf-voll")


def test_keine_doppelten_ids_im_dokument(seite):
    """Gefunden beim Bauen: kf-punkt wurde in einer Schleife als id vergeben."""
    doppelte = seite.evaluate("""() => {
        const gesehen = {}, doppelt = [];
        document.querySelectorAll('[id]').forEach(e => {
            if (gesehen[e.id]) doppelt.push(e.id); else gesehen[e.id] = 1;
        });
        return doppelt;
    }""")
    assert not doppelte, f"doppelte ids: {doppelte}"


def test_anzeige_aktualisiert_sich_selbst(seite):
    """Daniels Vorgabe: alle 5 Sekunden."""
    vorher = seite.inner_text("#kf-stand")
    seite.wait_for_function(
        f"document.getElementById('kf-stand').textContent !== {vorher!r}",
        timeout=15_000)


def test_keine_konsolenfehler(seite):
    assert not seite._konsolenfehler, f"Konsolenfehler: {seite._konsolenfehler}"


# ── Track 1: RAG im Chatpfad ───────────────────────────────────────────────────

def test_rag_schicht_existiert_in_der_anzeige(seite):
    rag = [s for s in schichten_aus_dom(seite) if s["gruppe"] == "rag"]
    assert len(rag) == 1, "RAG muss genau eine eigene Karte in der Anzeige sein"


def test_wesen_formuliert_eine_eigene_suchanfrage_oder_faellt_zurueck(kontext):
    """Daniels zwei Vorgaben zusammen: ausgeloest wird IMMER ('egal wie ich sie
    frage'), formuliert wird vom Wesen ('sie sollen sich das rag selber
    suchen'). Der Rueckfall darf nie leer sein."""
    ausgabe = _im_dienst(
        "cc.RAG_VORABCALL_TIMEOUT = 0.01\n"
        f"v = cc.lade_chat_verlauf({WESEN!r}, max_eintraege=8)\n"
        f"print(repr(cc.rag_anfrage_bilden({WESEN!r}, 'was hast du ueber Vertrauen geschrieben', v)))\n"
    )
    anfrage = ausgabe.strip()
    assert anfrage not in ("''", '""'), "Rueckfall lieferte leere Suchanfrage"
    assert "Vertrauen" in anfrage


def test_rag_block_enthaelt_echte_treffer_aus_dem_eigenen_archiv():
    ausgabe = _im_dienst(
        f"b = cc.hole_rag_block({WESEN!r}, 'Vertrauen und Ehrlichkeit im Forum')\n"
        "print(len(b))\n"
    )
    assert int(ausgabe.strip()) > 200, "RAG-Block zu kurz — keine echten Treffer?"


def test_rag_block_steht_direkt_vor_der_nachricht():
    """Daniels Entscheidung: eigener Block vor der Nachricht, nicht in den
    Systemprompt gemischt.

    Seit 2026-08-04 als Vorspann IN der letzten user-Nachricht statt als eigene
    system-Rolle -- das Chat-Template lehnt system-Nachrichten hinter dem
    Verlauf mit HTTP 400 ab. Daniels Vorgabe bleibt erfuellt: der Block steht
    unmittelbar vor seiner Frage und ist sichtbar davon getrennt."""
    ausgabe = _im_dienst(
        f"v = cc.lade_chat_verlauf({WESEN!r}, max_eintraege=8)\n"
        f"m = cc.baue_messages({WESEN!r}, v, 'meine frage', rag_block='RAG-TESTBLOCK')\n"
        "print([x['role'] for x in m])\n"
        "print(repr(m[-1]['content']))\n"
    )
    zeilen = ausgabe.strip().splitlines()
    rollen = eval(zeilen[0])
    letzte = eval(zeilen[1])
    assert rollen[-1] == "user", "letzte Nachricht muss die des Menschen sein"
    assert "system" not in rollen[1:], "keine system-Rolle hinter dem Verlauf"
    assert letzte.index("RAG-TESTBLOCK") < letzte.index("meine frage"), \
        "der Block muss VOR der Frage stehen"
    assert letzte.endswith("meine frage")


def test_ohne_rag_block_bleibt_der_aufbau_unveraendert():
    """Additive Aenderung: ein leerer RAG darf nichts einfuegen."""
    ausgabe = _im_dienst(
        f"v = cc.lade_chat_verlauf({WESEN!r}, max_eintraege=8)\n"
        f"a = cc.baue_messages({WESEN!r}, v, 'frage')\n"
        f"b = cc.baue_messages({WESEN!r}, v, 'frage', rag_block='')\n"
        f"c = cc.baue_messages({WESEN!r}, v, 'frage', rag_block='RAGTEST')\n"
        "print(len(a), len(b), len(c), a[-1]['role'])\n"
        "print(any('RAGTEST' in m['content'] for m in b))\n"
    )
    zeilen = ausgabe.strip().splitlines()
    n_a, n_b, n_c, letzte = zeilen[0].split()
    assert n_a == n_b == n_c, \
        "der RAG-Block wird der letzten Nachricht vorangestellt, er erzeugt keine neue"
    assert letzte == "user"
    assert zeilen[1] == "False", "leerer RAG-Block darf nichts einfuegen"


def test_kaputter_rag_verhindert_niemals_das_gespraech():
    """Wichtigste Eigenschaft: die Suche ist eine Zutat, keine Bedingung."""
    ausgabe = _im_dienst(
        f"print(repr(cc.hole_rag_block({WESEN!r}, '')))\n"
        "cc._RAG_MODUL = None\n"
        "import unittest.mock as m\n"
        "with m.patch.object(cc, '_rag_modul', side_effect=RuntimeError('DB weg')):\n"
        f"    print(repr(cc.hole_rag_block({WESEN!r}, 'irgendwas')))\n"
    )
    # [rag]-Zeilen sind Protokollausgaben des Dienstes, keine Rueckgabewerte.
    rueckgaben = [z for z in ausgabe.strip().splitlines() if not z.startswith("[rag]")]
    assert rueckgaben, "kein Rueckgabewert im Teilprozess-Ausgabestrom"
    for zeile in rueckgaben:
        assert zeile in ("''", '""'), f"erwartet leerer Block, war: {zeile}"


# ── Track 3: Wort-/Satzloeschung mit Mehrfachauswahl ───────────────────────────

def test_verlaufsschicht_weist_eintraege_einzeln_aus(seite, kontext):
    verlauf = next(s for s in kontext["schichten"] if s["gruppe"] == "verlauf")
    assert "eintraege" in verlauf, "ohne Einzeleintraege ist keine Auswahl moeglich"
    for e in verlauf["eintraege"]:
        assert e["ts"] and e["rolle"] is not None and "redigiert" in e
    # und im DOM steht je Eintrag eine eigene, auswaehlbare Karte
    karten = seite.eval_on_selector_all(
        ".red-eintrag", "e => e.map(x => x.dataset.ts)")
    assert karten == [e["ts"] for e in verlauf["eintraege"]], \
        "Anzeige und Kontext sind sich ueber die Eintraege nicht einig"


def test_redaktion_entfernt_nur_das_gewaehlte_und_zerstoert_nichts():
    """Kerneigenschaft: das Original bleibt im Protokoll stehen. Gegen eine
    Wegwerf-Datei getestet, damit kein echtes Wesengedaechtnis veraendert wird."""
    ausgabe = _im_dienst("""
import tempfile, pathlib, json
tmp = pathlib.Path(tempfile.mkdtemp()) / "chat_verlauf.jsonl"
cc.chat_verlauf_datei = lambda name: tmp
cc.speichere_chat_eintrag = None  # nicht gebraucht, wir schreiben direkt
tmp.write_text(json.dumps({"ts": "T1", "rolle": "mensch",
    "inhalt": "Erster Satz. Zweiter Satz. Dritter Satz."}, ensure_ascii=False) + "\\n",
    encoding="utf-8")

cc.speichere_redaktion("egal", "T1", ["Zweiter Satz."])
sichtbar = cc.lade_chat_verlauf("egal", max_eintraege=99)
roh      = cc.lade_chat_verlauf("egal", max_eintraege=99, roh=True)
print("SICHTBAR:" + sichtbar[0]["inhalt"])
print("REDIGIERT:" + str(sichtbar[0].get("redigiert")))
print("ROH:" + roh[0]["inhalt"])

# Einzelnes Wort
cc.speichere_redaktion("egal", "T1", ["Dritter"])
print("NACH_WORT:" + cc.lade_chat_verlauf("egal", max_eintraege=99)[0]["inhalt"])

# Vollstaendig redigiert -> faellt aus dem Kontext, bleibt aber im Protokoll
cc.speichere_redaktion("egal", "T1", ["Erster Satz.", "Satz."])
print("LEER_SICHTBAR:" + str(len(cc.lade_chat_verlauf("egal", max_eintraege=99))))
print("LEER_ROH:" + str(len(cc.lade_chat_verlauf("egal", max_eintraege=99, roh=True))))
""")
    werte = dict(z.split(":", 1) for z in ausgabe.strip().splitlines() if ":" in z)
    assert werte["SICHTBAR"] == "Erster Satz. Dritter Satz."
    assert werte["REDIGIERT"] == "True"
    assert werte["ROH"] == "Erster Satz. Zweiter Satz. Dritter Satz.", "Original wurde veraendert!"
    assert werte["NACH_WORT"] == "Erster Satz. Satz."
    assert werte["LEER_SICHTBAR"] == "0", "vollstaendig redigierter Eintrag darf nicht im Kontext sein"
    assert werte["LEER_ROH"] == "1", "Protokolleintrag wurde geloescht statt nur redigiert"


def test_redaktion_weist_leere_auswahl_und_unbekanntes_ziel_ab(seite):
    leer = seite.request.post(f"{BASIS}/api/kontext/{WESEN}/redaktion",
                              data={"ziel_ts": "T1", "entfernt": ["", "  "]}, timeout=30_000)
    assert leer.status == 400
    unbekannt = seite.request.post(f"{BASIS}/api/kontext/{WESEN}/redaktion",
                                   data={"ziel_ts": "gibtsnicht", "entfernt": ["x"]}, timeout=30_000)
    assert unbekannt.status == 404


def test_rohstand_endpunkt_zeigt_mehr_als_das_kontextfenster(seite, kontext):
    roh = seite.request.get(f"{BASIS}/api/kontext/{WESEN}/roh", timeout=60_000).json()
    verlauf = next(s for s in kontext["schichten"] if s["gruppe"] == "verlauf")
    assert roh["anzahl"] >= len(verlauf["eintraege"])


@pytest.fixture()
def offene_vollansicht(seite):
    if not seite.is_visible("#kf-voll"):
        seite.click("#kf")
        seite.wait_for_selector("#kf-voll.auf", timeout=5_000)
    zeile = seite.locator(".kfs").filter(has_text="Gespraechsverlauf")
    if not zeile.first.get_attribute("class").endswith("auf"):
        zeile.first.locator(".kfs-kopf").click()
    seite.wait_for_selector(".red-eintrag", timeout=5_000)
    yield seite
    seite.evaluate("""() => {
        document.querySelectorAll('.wort.gewaehlt').forEach(w => w.classList.remove('gewaehlt'));
        document.querySelectorAll('.satz-zeile input:checked').forEach(c => {
            c.checked = false; c.closest('.satz-zeile').classList.remove('ganz');
        });
    }""")
    seite.keyboard.press("Escape")


def test_eintraege_werden_in_saetze_und_woerter_zerlegt(offene_vollansicht):
    pg = offene_vollansicht
    assert pg.eval_on_selector_all(".red-eintrag", "e => e.length") >= 3
    assert pg.eval_on_selector_all(".satz-zeile", "e => e.length") >= 3
    assert pg.eval_on_selector_all(".wort", "e => e.length") >= 20


def test_wortauswahl_markiert_und_schaltet_knopf_frei(offene_vollansicht):
    pg = offene_vollansicht
    eintrag = pg.locator(".red-eintrag").nth(1)
    assert eintrag.locator(".red-btn:not(.nach-container):not(.nach-memory)").is_disabled()
    eintrag.locator(".wort").nth(2).click()
    assert eintrag.locator(".wort.gewaehlt").count() == 1
    assert not eintrag.locator(".red-btn:not(.nach-container):not(.nach-memory)").is_disabled()
    eintrag.locator(".wort").nth(4).click()
    assert eintrag.locator(".wort.gewaehlt").count() == 2, "Mehrfachauswahl muss moeglich sein"


def test_satz_checkbox_markiert_die_ganze_zeile(offene_vollansicht):
    pg = offene_vollansicht
    eintrag = pg.locator(".red-eintrag").nth(1)
    zeile = eintrag.locator(".satz-zeile").first
    zeile.locator("input").check()
    assert "ganz" in (zeile.get_attribute("class") or "")
    assert not eintrag.locator(".red-btn:not(.nach-container):not(.nach-memory)").is_disabled()


def test_laufende_auswahl_ueberlebt_die_aktualisierung(offene_vollansicht):
    """Der 5-Sekunden-Takt darf eine begonnene Auswahl nicht wegwischen."""
    pg = offene_vollansicht
    eintrag = pg.locator(".red-eintrag").nth(1)
    eintrag.locator(".wort").nth(1).click()
    assert eintrag.locator(".wort.gewaehlt").count() == 1
    pg.wait_for_timeout(6500)
    assert pg.locator(".red-eintrag").nth(1).locator(".wort.gewaehlt").count() == 1, \
        "Auswahl wurde durch die Aktualisierung zerstoert"


# ── Track 4: Container & Memory (von codexium2) ────────────────────────────────

@pytest.fixture()
def testbehaelter(seite):
    """Legt einen eigenen Behaelter an und raeumt ihn hinterher weg, damit kein
    Testmuell im Gedaechtnis eines echten Wesens liegen bleibt."""
    antwort = seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/neu",
                                 data={"name": "PYTEST-Behälter"}, timeout=30_000)
    box = antwort.json()
    yield box
    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{box['id']}/entfernen",
                       timeout=30_000)


def test_speicher_endpunkt_liefert_das_codexium2_modell(seite):
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('sp-zahl').textContent !== '…'", timeout=20_000)
    seite.click("#sp")
    seite.wait_for_selector("#sp-memory-liste .sp-box", timeout=10_000)
    labels = seite.eval_on_selector_all(
        "#sp-memory-liste .sp-box .sp-box-kopf span:first-of-type",
        "e => e.map(x => x.textContent)")
    assert labels == ["Über dich", "Wichtige Momente", "Offene Fragen",
                      "Wesen selbst", "Meinungen"], labels
    assert "11111" in seite.inner_text("#sp-memory-budget")
    seite.evaluate("document.getElementById('sp-voll').classList.remove('auf')")
    d = seite.request.get(f"{BASIS}/api/speicher/{WESEN}", timeout=30_000).json()
    assert d["container_budget"] == 11111 and d["memory_budget"] == 11111
    schluessel = [k["key"] for k in d["memory"]]
    assert schluessel == ["ueber_mich", "wichtige_momente", "offene_fragen",
                          "wesen_selbst", "meinungen"], schluessel
    for kat in d["memory"]:
        assert "aktiv" in kat, "aktiv-Schalter fehlt (Daniels Zusatz gegenueber codexium2)"


def test_container_rundlauf_anlegen_fuellen_entfernen(seite, testbehaelter):
    box = testbehaelter["id"]
    eintrag = seite.request.post(
        f"{BASIS}/api/speicher/{WESEN}/container/{box}/eintrag",
        data={"text": "PYTEST Satz eins.", "kommentar": "probe"}, timeout=30_000).json()
    assert eintrag["quelle"] == "mensch" and eintrag["id"]

    d = seite.request.get(f"{BASIS}/api/speicher/{WESEN}", timeout=30_000).json()
    meiner = next(b for b in d["container"] if b["id"] == box)
    assert len(meiner["eintraege"]) == 1

    seite.request.post(
        f"{BASIS}/api/speicher/{WESEN}/container/{box}/eintrag/{eintrag['id']}/entfernen",
        timeout=30_000)
    d = seite.request.get(f"{BASIS}/api/speicher/{WESEN}", timeout=30_000).json()
    assert not next(b for b in d["container"] if b["id"] == box)["eintraege"]


def test_deaktivierter_container_faellt_aus_dem_kontext(seite, testbehaelter):
    """Daniels Kernforderung: 'muss sie bei den wesen auch wieder rausnehmbar
    und/deaktivierbar sein'."""
    box = testbehaelter["id"]
    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{box}/eintrag",
                       data={"text": "PYTEST-MARKER-SICHTBAR."}, timeout=30_000)

    def speicherschicht():
        seite.reload(wait_until="networkidle", timeout=60_000)
        seite.wait_for_function(
            "document.getElementById('kf-zahl').textContent !== '…'", timeout=20_000)
        return schicht_aus_dom(seite, "speicher")

    assert "PYTEST-MARKER-SICHTBAR." in speicherschicht()["inhalt"]

    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{box}/aktiv",
                       data={"aktiv": False}, timeout=30_000)
    aus = speicherschicht()
    assert "PYTEST-MARKER-SICHTBAR." not in aus["inhalt"]

    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{box}/aktiv",
                       data={"aktiv": True}, timeout=30_000)
    assert "PYTEST-MARKER-SICHTBAR." in speicherschicht()["inhalt"], \
        "Wiedereinschalten muss den Inhalt zurueckbringen"


def test_memory_kategorie_laesst_sich_deaktivieren(seite):
    text = "PYTEST Erinnerung zum Abschalten."
    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/memory/offene_fragen/eintrag",
                       data={"text": text}, timeout=30_000)

    def inhalt():
        seite.reload(wait_until="networkidle", timeout=60_000)
        seite.wait_for_function(
            "document.getElementById('kf-zahl').textContent !== '…'", timeout=20_000)
        return schicht_aus_dom(seite, "speicher")["inhalt"]

    assert text in inhalt()
    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/memory/offene_fragen/aktiv",
                       data={"aktiv": False}, timeout=30_000)
    assert text not in inhalt()

    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/memory/offene_fragen/aktiv",
                       data={"aktiv": True}, timeout=30_000)
    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/memory/offene_fragen/entfernen",
                       data={"text": text}, timeout=30_000)
    assert text not in inhalt()


def test_suche_findet_frisch_geschriebenes_auch_in_der_oberflaeche(seite, testbehaelter):
    """Daniels 'immer das jetziger neue suchen' -- hier ueber das Suchfeld."""
    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{testbehaelter['id']}/eintrag",
                       data={"text": "Ein Wiedehopf sitzt im Behälter."}, timeout=30_000)
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('sp-zahl').textContent !== '…'", timeout=20_000)
    seite.click("#sp")
    seite.wait_for_selector("#sp-suche", timeout=5_000)
    seite.fill("#sp-suche", "Wiedehopf")
    seite.wait_for_function(
        "document.querySelectorAll('#sp-treffer div').length > 0", timeout=10_000)
    assert "Wiedehopf" in seite.inner_text("#sp-treffer")
    seite.fill("#sp-suche", "")
    seite.evaluate("document.getElementById('sp-voll').classList.remove('auf')")


def test_suche_findet_immer_den_aktuellen_stand(seite, testbehaelter):
    """Daniel: 'das bei memorysystem soll halt immer das jetziger neue suchen
    koennen' -- also kein Cache zwischen Schreiben und Suchen."""
    box = testbehaelter["id"]
    begriff = "Zwiebelfisch"
    vorher = seite.request.get(f"{BASIS}/api/speicher/{WESEN}/suche?q={begriff}",
                               timeout=30_000).json()
    assert vorher["anzahl"] == 0

    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{box}/eintrag",
                       data={"text": f"Ein {begriff} im Behälter."}, timeout=30_000)
    nachher = seite.request.get(f"{BASIS}/api/speicher/{WESEN}/suche?q={begriff}",
                                timeout=30_000).json()
    assert nachher["anzahl"] == 1, "frisch Geschriebenes wurde nicht gefunden"
    assert nachher["treffer"][0]["quelle"] == "container"


def test_budgetgrenze_wird_eingehalten(seite, testbehaelter):
    box = testbehaelter["id"]
    antwort = seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{box}/eintrag",
                                 data={"text": "x" * 12000}, timeout=30_000)
    assert antwort.status == 400
    assert "Budget" in antwort.json()["fehler"]


def test_speicher_panel_und_vollansicht(seite):
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('sp-zahl').textContent !== '…'", timeout=20_000)
    assert "Beh." in seite.inner_text("#sp-zahl")
    seite.click("#sp")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    assert seite.eval_on_selector_all("#sp-memory-liste .sp-box", "e => e.length") == 5
    assert "11111" in seite.inner_text("#sp-memory-budget")
    seite.click("#sp-voll-zu")
    assert not seite.is_visible("#sp-voll")


def test_suchfeld_zeigt_treffer_in_der_oberflaeche(seite, testbehaelter):
    box = testbehaelter["id"]
    seite.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{box}/eintrag",
                       data={"text": "Ein Regenbogenforelle-Testeintrag."}, timeout=30_000)
    seite.click("#sp")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    seite.fill("#sp-suche", "Regenbogenforelle")
    seite.wait_for_function(
        "document.querySelectorAll('#sp-treffer div').length > 0", timeout=10_000)
    assert "Regenbogenforelle" in seite.inner_text("#sp-treffer")
    seite.fill("#sp-suche", "")
    seite.click("#sp-voll-zu")


def test_kontext_hat_jetzt_eine_speicherschicht(seite):
    gruppen = [s["gruppe"] for s in schichten_aus_dom(seite)]
    assert gruppen.count("speicher") == 1
    assert gruppen.index("speicher") < gruppen.index("rag")


# ── Track 5: Geschichten-Schicht ───────────────────────────────────────────────

@pytest.fixture()
def testgeschichte(seite):
    antwort = seite.request.post(
        f"{BASIS}/api/geschichten/{WESEN}/einsetzen",
        data={"titel": "PYTEST Vision", "text": "Eine eingesetzte Probe-Vision."},
        timeout=30_000)
    g = antwort.json()
    yield g
    seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/{g['id']}/entfernen", timeout=30_000)


def _geschichtenschicht(seite):
    """Aus dem DOM, nicht aus dem Endpunkt -- geprueft wird, was auf dem Schirm
    steht. aktive_ids kommen weiterhin aus der Antwort, die stehen nicht im DOM."""
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('kf-zahl').textContent !== '…'", timeout=20_000)
    karte = schicht_aus_dom(seite, "geschichten")
    d = seite.request.get(f"{BASIS}/api/kontext/{WESEN}", timeout=60_000).json()
    karte["aktive_ids"] = next(
        s for s in d["schichten"] if s["gruppe"] == "geschichten")["aktive_ids"]
    return karte


def test_laengen_sind_daniels_sechs_stufen(seite):
    d = seite.request.get(f"{BASIS}/api/geschichten/{WESEN}", timeout=30_000).json()
    assert d["laengen"] == [111, 222, 333, 444, 555, 666]
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('gf-zahl').textContent !== '…'", timeout=20_000)
    seite.click("#gf")
    seite.wait_for_selector(".ge-verfassen", timeout=10_000)
    assert seite.eval_on_selector_all(".ge-verfassen", "e => e.map(x => x.textContent)") \
        == ["111", "222", "333", "444", "555", "666"]
    seite.evaluate("document.getElementById('sp-voll').classList.remove('auf')")


def test_ungueltige_laenge_wird_abgewiesen(seite):
    antwort = seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/verfassen",
                                 data={"laenge": 500}, timeout=30_000)
    assert antwort.status == 400 and "Laenge" in antwort.json()["fehler"]


def test_eingesetzte_geschichte_ist_beschriftet(seite, testgeschichte):
    """Bedingung 1: eine Geschichte gibt sich NIE als gelebte Erinnerung aus."""
    schicht = _geschichtenschicht(seite)
    assert "Eine eingesetzte Probe-Vision." in schicht["inhalt"]
    assert "nicht dasselbe wie das, was du erlebt hast" in schicht["inhalt"]
    assert "dir eingesetzt" in schicht["inhalt"]
    assert testgeschichte["id"] in schicht["aktive_ids"]


def test_mehrere_geschichten_gleichzeitig(seite, testgeschichte):
    zweite = seite.request.post(
        f"{BASIS}/api/geschichten/{WESEN}/einsetzen",
        data={"titel": "PYTEST Zweite", "text": "Noch eine Probe."}, timeout=30_000).json()
    try:
        schicht = _geschichtenschicht(seite)
        assert len(schicht["aktive_ids"]) >= 2
        assert "Eine eingesetzte Probe-Vision." in schicht["inhalt"]
        assert "Noch eine Probe." in schicht["inhalt"]
    finally:
        seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/{zweite['id']}/entfernen",
                           timeout=30_000)


def test_geschichte_laesst_sich_abziehen_und_wieder_anlegen(seite, testgeschichte):
    gid = testgeschichte["id"]
    seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/{gid}/aktiv",
                       data={"aktiv": False}, timeout=30_000)
    aus = _geschichtenschicht(seite)
    assert "Eine eingesetzte Probe-Vision." not in aus["inhalt"]
    assert gid not in aus["aktive_ids"]

    seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/{gid}/aktiv",
                       data={"aktiv": True}, timeout=30_000)
    assert gid in _geschichtenschicht(seite)["aktive_ids"]


def test_entfernen_loescht_die_geschichte(seite):
    g = seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/einsetzen",
                           data={"titel": "PYTEST Wegwerf", "text": "weg damit"},
                           timeout=30_000).json()
    seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/{g['id']}/entfernen", timeout=30_000)
    d = seite.request.get(f"{BASIS}/api/geschichten/{WESEN}", timeout=30_000).json()
    assert g["id"] not in [x["id"] for x in d["geschichten"]]


def test_protokoll_haelt_den_aktiven_satz_fest(seite, testgeschichte):
    """Bedingung 3: jede Aeusserung muss rueckfuehrbar bleiben -- kam sie aus
    gelebten Ereignissen oder aus einer geladenen Geschichte."""
    _im_dienst(f"cc.codewesen_speicher.protokolliere_aktive_geschichten({WESEN!r}, 'pytest')")
    d = seite.request.get(f"{BASIS}/api/geschichten/{WESEN}/protokoll", timeout=30_000).json()
    assert d["anzahl"] >= 1
    letzter = d["eintraege"][-1]
    assert testgeschichte["id"] in letzter["aktive"]
    assert letzter["anlass"] == "pytest" and letzter["ts"]


def test_geschichten_stehen_vor_speicher_und_rag(seite):
    gruppen = [s["gruppe"] for s in schichten_aus_dom(seite)]
    assert gruppen.index("geschichten") < gruppen.index("speicher") < gruppen.index("rag")


def test_geschichten_oberflaeche(seite, testgeschichte):
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('sp-zahl').textContent !== '…'", timeout=20_000)
    seite.click("#sp")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    seite.wait_for_selector("#ge-liste .sp-box", timeout=10_000)
    knoepfe = seite.eval_on_selector_all(".ge-verfassen", "e => e.map(x => x.textContent)")
    assert knoepfe == ["111", "222", "333", "444", "555", "666"]
    assert "PYTEST Vision" in seite.inner_text("#ge-liste")
    assert "eingesetzt" in seite.inner_text("#ge-liste")
    seite.click("#sp-voll-zu")


# ── Track 5 (langsam): echtes Verfassen aus dem Chatverlauf ────────────────────

@pytest.mark.slow
def test_wesen_verfasst_geschichte_aus_dem_eigenen_verlauf(seite):
    """Echter LLM-Zug auf dem ausgelasteten 35B — gemessen ~198 s. Deshalb als
    'slow' markiert und nicht im Standardlauf:
        python3 -m pytest -m slow tests/test_codewesen_chat_kontext_rag.py
    """
    antwort = seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/verfassen",
                                 data={"laenge": 111}, timeout=900_000)
    assert antwort.ok, antwort.text()
    g = antwort.json()
    try:
        assert g["herkunft"] == "chatverlauf"
        assert g["laenge_ziel"] == 111
        assert len(g["text"]) > 80, "zu kurz fuer eine Erzaehlung"
        schicht = _geschichtenschicht(seite)
        assert "aus deinem eigenen Gesprächsverlauf destilliert" in schicht["inhalt"]
    finally:
        seite.request.post(f"{BASIS}/api/geschichten/{WESEN}/{g['id']}/entfernen",
                           timeout=30_000)


# ── Track 6: Nachrichten zwischen Wesen ────────────────────────────────────────

@pytest.fixture()
def testnachricht(seite):
    antwort = seite.request.post(f"{BASIS}/api/nachrichten/senden",
                                 data={"an": WESEN, "von": "Daniel",
                                       "betreff": "PYTEST", "text": "Eine Probenachricht."},
                                 timeout=30_000)
    datei = antwort.json()["datei"]
    yield datei
    seite.request.post(f"{BASIS}/api/nachrichten/{WESEN}/{datei}/gelesen", timeout=30_000)


def test_nachricht_landet_in_der_bestehenden_inbox(seite, testnachricht):
    """Bewusst kein zweites Postfach: dasselbe Format wie die Flarum-Eintraege,
    die codewesen_reaktion.py dort seit langem ablegt."""
    ausgabe = _im_dienst(
        f"import json, pathlib\n"
        f"p = pathlib.Path('/root/werkraum/codewesen/{WESEN}/inbox/{testnachricht}')\n"
        "d = json.loads(p.read_text(encoding='utf-8'))\n"
        "print(d['typ']); print(sorted(d.keys())); print(d['daten']['von'])\n"
    )
    zeilen = ausgabe.strip().splitlines()
    assert zeilen[0] == "nachricht"
    assert eval(zeilen[1]) == ["daten", "empfangen_am", "typ"], "Format weicht ab"
    assert zeilen[2] == "Daniel"


def test_ungelesene_nachricht_steht_im_kontext(seite, testnachricht):
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('kf-zahl').textContent !== '…'", timeout=20_000)
    schicht = schicht_aus_dom(seite, "nachrichten")
    assert "ungelesen" in schicht["titel"]
    assert "Eine Probenachricht." in schicht["inhalt"]
    assert "##NACHRICHT:" in schicht["inhalt"], "Antwortweg muss erklaert sein"
    assert "keine Aufgabe" in schicht["inhalt"], "Angebot, kein Zwang"


def test_gelesene_nachricht_verschwindet_aus_dem_kontext(seite):
    datei = seite.request.post(f"{BASIS}/api/nachrichten/senden",
                               data={"an": WESEN, "von": "Daniel",
                                     "text": "PYTEST verschwindet gleich."},
                               timeout=30_000).json()["datei"]

    def inhalt():
        seite.reload(wait_until="networkidle", timeout=60_000)
        seite.wait_for_function(
            "document.getElementById('kf-zahl').textContent !== '…'", timeout=20_000)
        return schicht_aus_dom(seite, "nachrichten")["inhalt"]

    assert "PYTEST verschwindet gleich." in inhalt()
    seite.request.post(f"{BASIS}/api/nachrichten/{WESEN}/{datei}/gelesen", timeout=30_000)
    assert "PYTEST verschwindet gleich." not in inhalt()


def test_unbekannter_empfaenger_und_pfad_werden_abgewiesen(seite):
    assert seite.request.post(f"{BASIS}/api/nachrichten/senden",
                              data={"an": "GibtsNicht", "text": "x"},
                              timeout=30_000).status == 404
    assert seite.request.post(f"{BASIS}/api/nachrichten/{WESEN}/..%2Fetc%2Fpasswd/gelesen",
                              timeout=30_000).status in (400, 404)


def test_nachricht_marker_schickt_an_ein_anderes_wesen():
    """##NACHRICHT: <wesen> | <text>## — der Weg, auf dem ein Wesen selbst
    einem anderen schreibt."""
    ausgabe = _im_dienst(
        "antwort = 'Klar. ##NACHRICHT: jumpa | Was denkst du über Vertrauen?##'\n"
        f"print(cc._verarbeite_nachricht_marker(antwort, {WESEN!r}))\n"
        "print(cc._verarbeite_nachricht_marker('##NACHRICHT: Niemand | hallo##', 'Schorschel'))\n"
        "print(cc._verarbeite_nachricht_marker('##NACHRICHT: Schorschel | selbst##', 'Schorschel'))\n"
    )
    zeilen = ausgabe.strip().splitlines()
    assert "gesendet" in zeilen[0] and "jumpa" in zeilen[0]
    assert "kein bekanntes Wesen" in zeilen[1]
    assert "an dich selbst" in zeilen[2]
    # zugestellte Probenachricht bei jumpa wieder wegräumen
    _im_dienst(
        "import codewesen_speicher as cs\n"
        "for n in cs.nachrichten_lesen('jumpa', nur_ungelesen=True):\n"
        "    if 'Was denkst du über Vertrauen?' in n['text']:\n"
        "        cs.nachricht_als_gelesen('jumpa', n['datei'])\n"
        "print('aufgeraeumt')\n"
    )


def test_schreibrecht_deckt_den_eigenen_ordner_und_die_vaults_ab():
    """Das Schreibrecht existierte schon (C-005-Whitelist). Hier nur belegt,
    dass es den Wesen-Ordner umfasst und Geheimnisse weiterhin nicht."""
    ausgabe = _im_dienst(
        f"print(bool(cc._pfad_im_werkraum('/root/werkraum/codewesen/{WESEN}/vault/notiz.md')))\n"
        f"print(bool(cc._pfad_im_werkraum('/root/werkraum/codewesen/{WESEN}/gedanken/x.md')))\n"
        "print(bool(cc._pfad_im_werkraum('/root/werkraum/flarum/diskussionen/0396_x.md')))\n"
        "print(bool(cc._pfad_im_werkraum('/root/werkraum/_claude/spiegel/x.md')))\n"
        "print(bool(cc._pfad_im_werkraum('/root/werkraum/.agent/flextrawurst-db.env')))\n"
        "print(bool(cc._pfad_im_werkraum('/root/werkraum/.git/config')))\n"
        "print(bool(cc._pfad_im_werkraum('/root/.ssh/id_rsa')))\n"
        "print(bool(cc._pfad_im_werkraum('/etc/passwd')))\n"
        "print(bool(cc._pfad_im_werkraum('/root/geni_gedaechtnis/x')))\n"
    )
    werte = ausgabe.split()
    # Die vier Pfade, die der Systemprompt den Wesen anbietet, muessen gehen.
    # codewesen/ und flarum/ sind Symlinks nach ausserhalb des Werkraums --
    # genau daran scheiterte es bis 2026-08-03 unbemerkt.
    assert werte[:4] == ["True"] * 4, f"eigener Ordner/Vault/Flarum/Spiegel gesperrt: {werte[:4]}"
    assert werte[4:] == ["False"] * 5, f"Sicherheitsgrenze durchlaessig: {werte[4:]}"


def test_nachrichten_oberflaeche(seite, testnachricht):
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('sp-zahl').textContent !== '…'", timeout=20_000)
    seite.click("#sp")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    seite.wait_for_selector("#na-liste .sp-eintrag", timeout=10_000)
    assert seite.eval_on_selector_all("#na-an option", "e => e.length") == 7
    assert "Eine Probenachricht." in seite.inner_text("#na-liste")
    seite.click("#sp-voll-zu")


# ── Track 7: Gedankenfeld — der mitgetragene Zustand ──────────────────────────

@pytest.fixture()
def feld_leer(seite):
    """Raeumt das Feld vor und nach dem Test -- ueber den regulaeren
    Entfernen-Weg, damit die Revisionshistorie das Aufraeumen selbst belegt."""
    def alles_weg():
        d = seite.request.get(f"{BASIS}/api/gedankenfeld/{WESEN}", timeout=30_000).json()
        for g in d["gedanken"]:
            seite.request.post(
                f"{BASIS}/api/gedankenfeld/{WESEN}/{g['id']}/entfernen?von=pytest",
                timeout=30_000)
    alles_weg()
    yield
    alles_weg()


def _feld(seite):
    return seite.request.get(f"{BASIS}/api/gedankenfeld/{WESEN}", timeout=30_000).json()


def test_aenderung_trifft_nur_den_einen_gedanken(seite, feld_leer):
    """Daniels 'schnell ändern aber nur da wo sie wollen'."""
    a = seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/neu",
                           data={"text": "Bleibt so wie er ist."}, timeout=30_000).json()
    b = seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/neu",
                           data={"text": "Wird gleich anders."}, timeout=30_000).json()
    seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/{b['id']}/aendern",
                       data={"text": "Jetzt ist er anders."}, timeout=30_000)

    nach = {g["id"]: g for g in _feld(seite)["gedanken"]}
    assert nach[a["id"]]["text"] == "Bleibt so wie er ist."
    assert nach[a["id"]]["aenderungen"] == 0, "unbeteiligter Gedanke wurde angefasst"
    assert nach[b["id"]]["text"] == "Jetzt ist er anders."
    assert nach[b["id"]]["aenderungen"] == 1


def test_nichts_verfaellt_und_nichts_wird_verdraengt(seite, feld_leer):
    """Daniels 'den rest behalten und mittragen über alle zeit'. Anders als
    Container/Memory (11111 Zeichen) gibt es hier bewusst KEIN Budget, das
    etwas abweist oder hinausschiebt."""
    ids = []
    for i in range(25):
        antwort = seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/neu",
                                     data={"text": f"Gedanke Nummer {i}: " + "x" * 400},
                                     timeout=30_000)
        assert antwort.ok, f"Gedanke {i} wurde abgewiesen — es darf kein Budget geben"
        ids.append(antwort.json()["id"])

    d = _feld(seite)
    assert d["anzahl"] == 25, "Gedanken sind verschwunden, ohne dass jemand sie entfernt hat"
    assert ids[0] in [g["id"] for g in d["gedanken"]], "der aelteste wurde verdraengt"
    # Der aelteste steht vorn -- Neues verdraengt Altes nicht einmal in der Reihenfolge.
    assert d["gedanken"][0]["id"] == ids[0]


def test_nur_entfernen_nimmt_etwas_heraus_und_die_historie_bleibt(seite, feld_leer):
    """Daniels 'bis sie es selbst entfernen'."""
    g = seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/neu",
                           data={"text": "Erste Fassung."}, timeout=30_000).json()
    seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/{g['id']}/aendern",
                       data={"text": "Zweite Fassung."}, timeout=30_000)
    seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/{g['id']}/entfernen",
                       timeout=30_000)

    assert g["id"] not in [x["id"] for x in _feld(seite)["gedanken"]]

    hist = seite.request.get(f"{BASIS}/api/gedankenfeld/{WESEN}/{g['id']}/historie",
                             timeout=30_000).json()
    ops = [r["op"] for r in hist["revisionen"]]
    assert ops == ["neu", "aendern", "entfernen"]
    assert hist["revisionen"][0]["text"] == "Erste Fassung.", \
        "entfernt heisst 'nicht mehr im Zustand', nicht 'weg'"


def test_unbekannter_gedanke_wird_abgewiesen(seite, feld_leer):
    for pfad in ("aendern", "entfernen"):
        antwort = seite.request.post(
            f"{BASIS}/api/gedankenfeld/{WESEN}/deadbeef/{pfad}",
            data={"text": "egal"}, timeout=30_000)
        assert antwort.status == 400


def test_marker_fuehren_das_feld(seite, feld_leer):
    """Die drei Marker sind der Weg, auf dem ein Wesen sein Feld selbst führt."""
    ausgabe = _im_dienst(
        "import codewesen_gedankenfeld as gf\n"
        f"r = gf.verarbeite_marker({WESEN!r}, 'Denke nach. ##GEDANKE+ Stille ist auch eine Antwort.##')\n"
        "print(r[0])\n"
        f"gid = gf.lade_feld({WESEN!r})[0]['id']\n"
        f"print(gf.verarbeite_marker({WESEN!r}, '##GEDANKE~ ' + gid + ' | Stille ist die ehrlichste Antwort.##')[0])\n"
        f"print(gf.lade_feld({WESEN!r})[0]['text'])\n"
        f"print(gf.verarbeite_marker({WESEN!r}, '##GEDANKE- ' + gid + '##')[0])\n"
        f"print(len(gf.lade_feld({WESEN!r})))\n"
    )
    zeilen = ausgabe.strip().splitlines()
    assert zeilen[0].startswith("[GEDANKE+")
    assert "geändert" in zeilen[1]
    assert zeilen[2] == "Stille ist die ehrlichste Antwort."
    assert "entfernt" in zeilen[3]
    assert zeilen[4] == "0"


def test_block_traegt_die_ids_und_die_eigenen_kosten(seite, feld_leer):
    """Ohne die IDs koennte ein Wesen nichts punktgenau aendern. Und die
    Tokenkosten stehen drin, damit Verdichten eine informierte Entscheidung ist
    und keine erzwungene."""
    g = seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/neu",
                           data={"text": "Ein Gedanke mit Kosten."}, timeout=30_000).json()
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('kf-zahl').textContent !== '…'", timeout=20_000)
    schicht = schicht_aus_dom(seite, "gedankenfeld")
    schicht["gedanken"] = seite.request.get(
        f"{BASIS}/api/gedankenfeld/{WESEN}", timeout=30_000).json()["gedanken"]
    assert g["id"] in schicht["inhalt"]
    assert "##GEDANKE~" in schicht["inhalt"] and "##GEDANKE-" in schicht["inhalt"]
    assert "nichts daran verfällt" in schicht["inhalt"]
    assert "Token von deinem" in schicht["inhalt"], "eigene Kosten fehlen"
    assert schicht["tokens"] > 0
    assert len(schicht["gedanken"]) == 1


def test_gedankenfeld_steht_vor_allen_anderen_schichten(seite, feld_leer):
    """Der mitgetragene Zustand ist keine Beigabe zur aktuellen Nachricht --
    er steht vor Nachrichten, Geschichten, Speicher und RAG."""
    seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/neu",
                       data={"text": "Reihenfolge-Probe."}, timeout=30_000)
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('kf-zahl').textContent !== '…'", timeout=20_000)
    gruppen = [s["gruppe"] for s in schichten_aus_dom(seite)]
    for spaeter in ("nachrichten", "geschichten", "speicher", "rag"):
        assert gruppen.index("gedankenfeld") < gruppen.index(spaeter), spaeter


def test_feld_ueberlebt_einen_dienstneustart(seite, feld_leer):
    """'über alle zeit' heisst auch: über Prozessgrenzen. Das Feld liegt auf
    der Platte, nicht im Speicher des Dienstes."""
    g = seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/neu",
                           data={"text": "Ich überlebe einen Neustart."},
                           timeout=30_000).json()
    ausgabe = _im_dienst(
        "import codewesen_gedankenfeld as gf\n"
        f"print([x['text'] for x in gf.lade_feld({WESEN!r})])\n"
    )
    assert "Ich überlebe einen Neustart." in ausgabe
    assert g["id"] in [x["id"] for x in _feld(seite)["gedanken"]]


# ── Browser-Abdeckung: was vorher nur ueber die API geprueft war ───────────────
#
# Nachgereicht, nachdem Daniel gefragt hat, ob wirklich alles Playwright ist.
# Die ehrliche Antwort war nein: 16 von 65 fuhren einen Browser, der Rest ging
# ueber request/Unterprozess. Und Track 7 hatte gar keine Oberflaeche.

@pytest.fixture()
def offene_speicheransicht(seite):
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('gf-zahl').textContent !== '…'", timeout=20_000)
    seite.click("#gf")
    seite.wait_for_selector("#sp-voll.auf", timeout=5_000)
    yield seite
    seite.evaluate("document.getElementById('sp-voll').classList.remove('auf')")


def test_gedanke_im_browser_anlegen_aendern_entfernen(offene_speicheransicht, feld_leer):
    pg = offene_speicheransicht
    pg.fill("#gf-neu-text", "Im Browser angelegt.")
    pg.click("#gf-neu-btn")
    pg.wait_for_selector(".gfd", timeout=10_000)
    assert pg.inner_text(".gfd .gfd-text").strip() == "Im Browser angelegt."
    gid = pg.get_attribute(".gfd", "data-gid")

    # ändern: erst aufmachen, dann übernehmen
    pg.click(".gfd .aendern-btn")
    pg.wait_for_timeout(200)
    assert pg.get_attribute(".gfd .gfd-text", "contenteditable") == "true"
    pg.eval_on_selector(".gfd .gfd-text", "e => { e.textContent = 'Im Browser geändert.' }")
    pg.click(".gfd .aendern-btn")
    # Auf die neu gezeichnete Liste warten, nicht auf den Text, den ich selbst
    # gerade lokal ins DOM geschrieben habe -- der stimmt sofort und beweist nichts.
    pg.wait_for_function(
        "document.querySelector('.gfd .gfd-kopf').textContent.includes('geändert')",
        timeout=15_000)
    assert pg.inner_text(".gfd .gfd-text").strip() == "Im Browser geändert."
    assert "1× geändert" in pg.inner_text(".gfd .gfd-kopf")

    pg.click(".gfd .weg-btn")
    pg.wait_for_function("document.querySelectorAll('.gfd').length === 0", timeout=10_000)
    hist = pg.request.get(f"{BASIS}/api/gedankenfeld/{WESEN}/{gid}/historie",
                          timeout=30_000).json()
    assert [r["op"] for r in hist["revisionen"]] == ["neu", "aendern", "entfernen"]


def test_browser_aenderung_trifft_nur_eine_karte(offene_speicheransicht, feld_leer):
    """Daniels 'nur da wo sie wollen' — auch über die Oberfläche."""
    pg = offene_speicheransicht
    for text in ["Karte eins bleibt.", "Karte zwei ändert sich."]:
        pg.fill("#gf-neu-text", text)
        pg.click("#gf-neu-btn")
        pg.wait_for_timeout(700)
    pg.wait_for_function("document.querySelectorAll('.gfd').length === 2", timeout=10_000)

    zweite = pg.locator(".gfd").nth(1)
    zweite.locator(".aendern-btn").click()
    pg.wait_for_timeout(200)
    pg.eval_on_selector_all(
        ".gfd", "e => { e[1].querySelector('.gfd-text').textContent = 'Nur diese hier.' }")
    zweite.locator(".aendern-btn").click()
    pg.wait_for_timeout(1200)

    karten = pg.eval_on_selector_all(
        ".gfd", "e => e.map(x => [x.querySelector('.gfd-text').textContent.trim(), "
                "x.querySelector('.gfd-kopf').textContent.includes('geändert')])")
    assert karten[0] == ["Karte eins bleibt.", False], f"unbeteiligte Karte angefasst: {karten[0]}"
    assert karten[1] == ["Nur diese hier.", True]


def test_panel_zeigt_gedankenfeld_mit_kosten(offene_speicheransicht, feld_leer):
    pg = offene_speicheransicht
    pg.fill("#gf-neu-text", "Ein Gedanke mit sichtbaren Kosten.")
    pg.click("#gf-neu-btn")
    pg.wait_for_selector(".gfd", timeout=10_000)
    assert re.match(r"^\d+ · \d+ Tok$", pg.inner_text("#gf-zahl")), pg.inner_text("#gf-zahl")
    kosten = pg.inner_text("#gf-kosten")
    assert "Revisionen" in kosten and "Nichts verfällt" in kosten
    assert "nur du entfernst etwas" in kosten


def test_container_schalter_im_browser_wirkt_auf_den_kontext(offene_speicheransicht,
                                                             testbehaelter):
    """Track 4 war bisher nur über die API geprüft."""
    pg = offene_speicheransicht
    box = testbehaelter["id"]
    pg.request.post(f"{BASIS}/api/speicher/{WESEN}/container/{box}/eintrag",
                    data={"text": "BROWSERPROBE im Behälter."}, timeout=30_000)
    pg.reload(wait_until="networkidle", timeout=60_000)
    pg.click("#gf")
    pg.wait_for_selector(f'.sp-box[data-id="{box}"]', timeout=10_000)

    kasten = pg.locator(f'.sp-box[data-id="{box}"] .sp-aktiv')
    assert kasten.is_checked()
    kasten.uncheck()
    pg.wait_for_timeout(1500)
    d = pg.request.get(f"{BASIS}/api/kontext/{WESEN}", timeout=60_000).json()
    inhalt = next(s for s in d["schichten"] if s["gruppe"] == "speicher")["inhalt"]
    assert "BROWSERPROBE im Behälter." not in inhalt


def test_geschichte_schalter_im_browser(offene_speicheransicht, testgeschichte):
    """Track 5 war bisher nur über die API geprüft."""
    pg = offene_speicheransicht
    pg.reload(wait_until="networkidle", timeout=60_000)
    pg.click("#gf")
    gid = testgeschichte["id"]
    pg.wait_for_selector(f'.sp-box[data-gid="{gid}"]', timeout=10_000)
    pg.locator(f'.sp-box[data-gid="{gid}"] .ge-aktiv').uncheck()
    pg.wait_for_timeout(1500)
    d = pg.request.get(f"{BASIS}/api/kontext/{WESEN}", timeout=60_000).json()
    schicht = next(s for s in d["schichten"] if s["gruppe"] == "geschichten")
    assert gid not in schicht["aktive_ids"]


def test_nachricht_ueber_das_formular_senden(offene_speicheransicht):
    """Track 6 war bisher nur über die API geprüft."""
    pg = offene_speicheransicht
    pg.select_option("#na-an", WESEN)
    pg.fill("#na-betreff", "BROWSERPROBE")
    pg.fill("#na-text", "Über das Formular geschickt.")
    pg.click("#na-senden")
    pg.wait_for_function(
        "document.getElementById('na-liste').textContent.includes('Über das Formular geschickt.')",
        timeout=10_000)
    d = pg.request.get(f"{BASIS}/api/kontext/{WESEN}", timeout=60_000).json()
    assert "Über das Formular geschickt." in \
        next(s for s in d["schichten"] if s["gruppe"] == "nachrichten")["inhalt"]
    # aufräumen über den Haken in der Oberfläche
    pg.click("#na-liste .na-gelesen")
    pg.wait_for_timeout(1200)


# ── Alle sieben Wesen im Browser (Daniel 2026-08-04: "alle mt playwright testen") ──
#
# Bis hierher liefen alle Tests gegen Schorschel. Die uebrigen sechs waren
# ungeprueft -- und sie unterscheiden sich real: eigener Systemprompt, eigener
# Verlauf, eigenes Gedaechtnis, und dak+gord-system hat sogar ein Sonderzeichen
# im Namen (+), das durch die URL-Kodierung muss.

ALLE_WESEN = ["Schorschel", "Resonanzknoten", "träumerlie",
              "F3INSCHM3CK3R", "R1ZZ1", "jumpa", "dak+gord-system"]


@pytest.fixture(scope="module")
def browser_fuer_alle(playwright_sitzung):
    browser = playwright_sitzung.chromium.launch(args=["--no-sandbox"])
    yield browser
    browser.close()


def _seite_fuer(browser, wesen: str):
    from urllib.parse import quote
    pg = browser.new_page(viewport={"width": 1400, "height": 900})
    pg._fehler = []
    pg.on("console", lambda m: pg._fehler.append(f"{m.type}: {m.text}")
          if m.type == "error" else None)
    pg.on("pageerror", lambda e: pg._fehler.append(f"pageerror: {e}"))
    pg.goto(f"{BASIS}/chat/{quote(wesen)}", wait_until="networkidle", timeout=60_000)
    pg.wait_for_function(
        "document.getElementById('kf-zahl').textContent !== '…'", timeout=30_000)
    return pg


@pytest.mark.parametrize("wesen", ALLE_WESEN)
def test_jedes_wesen_zeigt_sein_kontextfenster(browser_fuer_alle, wesen):
    """Kernprüfung für alle sieben: die Seite lädt, die Anzeige füllt sich mit
    echten Zahlen, keine Konsolenfehler."""
    pg = _seite_fuer(browser_fuer_alle, wesen)
    try:
        text = pg.inner_text("#kf-zahl")
        assert re.match(r"^\d+ / \d+ \(\d+\.\d+%\)$", text), f"{wesen}: {text!r}"
        summe, ctx = kopfzahlen_aus_dom(pg)
        assert 0 < summe < ctx, f"{wesen}: {summe} von {ctx}"
        # Wesen-Profil muss das jeweilige Wesen betreffen, nicht ein anderes
        schichten = schichten_aus_dom(pg)
        anrede = next(s for s in schichten if s["titel"] == "Anrede & Selbstdefinition")
        assert wesen in anrede["inhalt"], \
            f"{wesen}: Systemprompt nennt es nicht beim Namen"
        assert not pg._fehler, f"{wesen}: {pg._fehler}"
    finally:
        pg.close()


@pytest.mark.parametrize("wesen", ALLE_WESEN)
def test_jedes_wesen_hat_alle_schichten(browser_fuer_alle, wesen):
    pg = _seite_fuer(browser_fuer_alle, wesen)
    try:
        gruppen = [s["gruppe"] for s in schichten_aus_dom(pg)]
        for pflicht in ("systemprompt", "gedankenfeld", "nachrichten",
                        "geschichten", "speicher", "rag"):
            assert pflicht in gruppen, f"{wesen}: Schicht {pflicht} fehlt"
        # Reihenfolge gilt für alle gleich
        assert gruppen.index("gedankenfeld") < gruppen.index("nachrichten") \
            < gruppen.index("geschichten") < gruppen.index("speicher") \
            < gruppen.index("rag"), f"{wesen}: falsche Reihenfolge"
    finally:
        pg.close()


@pytest.mark.parametrize("wesen", ALLE_WESEN)
def test_jedes_wesen_fuehrt_sein_eigenes_gedankenfeld(browser_fuer_alle, wesen):
    """Wichtig: die Felder dürfen sich nicht vermischen. dak+gord-system prüft
    zusätzlich den Umgang mit dem '+' im Namen."""
    from urllib.parse import quote
    pg = _seite_fuer(browser_fuer_alle, wesen)
    marke = f"PYTEST-{wesen}-eigen"
    try:
        pg.click("#gf")
        pg.wait_for_selector("#sp-voll.auf", timeout=5_000)
        pg.fill("#gf-neu-text", marke)
        pg.click("#gf-neu-btn")
        pg.wait_for_function(
            f"document.getElementById('gf-liste').textContent.includes({marke!r})",
            timeout=15_000)

        # steht im eigenen Feld …
        eigen = pg.request.get(f"{BASIS}/api/gedankenfeld/{quote(wesen)}",
                               timeout=30_000).json()
        assert marke in [g["text"] for g in eigen["gedanken"]]

        # … und in keinem anderen
        for anderes in ALLE_WESEN:
            if anderes == wesen:
                continue
            fremd = pg.request.get(f"{BASIS}/api/gedankenfeld/{quote(anderes)}",
                                   timeout=30_000).json()
            assert marke not in [g["text"] for g in fremd["gedanken"]], \
                f"Gedanke von {wesen} ist bei {anderes} gelandet"

        # wieder wegräumen, über die Oberfläche
        karte = pg.locator(".gfd").filter(has_text=marke)
        karte.locator(".weg-btn").click()
        pg.wait_for_function(
            f"!document.getElementById('gf-liste').textContent.includes({marke!r})",
            timeout=15_000)
        assert not pg._fehler, f"{wesen}: {pg._fehler}"
    finally:
        pg.close()


# ── Zwei Instanzen: Chat auf eigenem Modell-Dienst (2026-08-04) ────────────────

def test_chat_laeuft_auf_eigener_instanz(seite):
    """Nach dem Umbau muss der Chat auf 11435 zeigen, nicht mehr auf die
    Hintergrund-Instanz 11436, die die sieben Wesen bedient."""
    d = seite.request.get(f"{BASIS}/api/modell", timeout=30_000).json()
    assert d["modell"] == "hauhaucs-q6"
    assert d["ziel"].endswith(":11435"), f"Chat zeigt auf {d['ziel']}"
    assert d["eigene_instanz"] is True
    assert d["erreichbar"] is True
    assert d["n_ctx"] > 0


def test_beide_instanzen_laufen_mit_eigenem_modell(seite):
    """2026-08-22: Chat (11435) laeuft wieder auf demselben Modell wie
    Hintergrund (11436) -- beide auf hauhaucs-q6 (Qwen3.6-35B-A3B-Uncensored-
    HauhauCS-Aggressive), Nemotron 3 Nano PRISM wieder entfernt (zeigte im
    Live-Test trotz Abliteration eigene Guardrail-Aufzaehlungen). Geteiltes
    GGUF via mmap, daher waere die alte Mlocked-Pruefung aus der
    Ein-Modell-Aera jetzt wieder ein echter Beleg fuer geteilte Gewichte."""
    erwartet = {"11435": "hauhaucs-q6", "11436": "hauhaucs-q6"}
    for port, alias in erwartet.items():
        props = seite.request.get(f"http://127.0.0.1:{port}/props", timeout=30_000)
        assert props.ok, f"Instanz auf {port} antwortet nicht"
        assert props.json().get("model_alias") == alias, \
            f"Instanz auf {port} liefert {props.json().get('model_alias')!r}, erwartet {alias!r}"


def test_die_oberflaeche_zeigt_das_echte_modell(seite):
    """Bis 2026-08-04 stand dort 'e4b (langsam)' / 'e2b (schnell)' -- gemma4-
    Namen, obwohl seit Monaten hauhaucs-q6 antwortet."""
    seite.reload(wait_until="networkidle", timeout=60_000)
    seite.wait_for_function(
        "document.getElementById('modell-anzeige').textContent !== '…'", timeout=20_000)
    text = seite.inner_text("#modell-anzeige")
    assert "hauhaucs-q6" in text, text
    assert "eigene Instanz" in text, text
    for veraltet in ("e4b", "e2b", "gemma", "dolphin", "nemotron3-nano-prism"):
        assert veraltet not in seite.content().lower().replace("dolphin-mistral", ""), \
            f"veralteter Modellname '{veraltet}' noch in der Seite"


def test_prioritaets_waechter_ist_abgeschaltet():
    """Mit eigener Instanz braucht der Chat keinen Waechter mehr -- er stoppte
    ohnehin 19 Units, von denen die sieben rechnenden nicht dabei waren."""
    ausgabe = _im_dienst(
        "import hauhau_client as hc\n"
        "print(hc.WAECHTER_AKTIV)\n"
        "print(hc.LLAMA_URL_CHAT)\n"
    )
    zeilen = ausgabe.strip().splitlines()
    assert zeilen[0] == "False"
    assert ":11435" in zeilen[1]


# ── Der Test, der gefehlt hat (Daniel 2026-08-04: "playwright...grün sagt nix") ──
#
# 98 gruene Tests haben nicht bemerkt, dass der Chat kaputt war: sie pruefen die
# STRUKTUR der Nachrichten, aber keiner hat je eine echte Antwort erzeugt. Der
# Fehler ("Jinja Exception: System message must be at the beginning", HTTP 400)
# trat erst im ersten echten Gespraech auf -- und zwar bei jeder Nachricht, in
# der eine der neuen Schichten gefuellt war.

def test_zusatzschichten_erzeugen_keine_system_rolle_nach_dem_verlauf():
    """Die billige Haelfte der Lehre: strukturell pruefen, dass keine
    system-Nachricht hinter dem Verlauf landet."""
    ausgabe = _im_dienst(
        f"v = cc.lade_chat_verlauf({WESEN!r}, max_eintraege=8)\n"
        f"m = cc.baue_messages({WESEN!r}, v, 'frage', rag_block='RAGBLOCK')\n"
        "print([x['role'] for x in m])\n"
        "print('RAGBLOCK' in m[-1]['content'])\n"
    )
    zeilen = ausgabe.strip().splitlines()
    rollen = eval(zeilen[0])
    assert rollen[0] == "system", "der Systemprompt muss vorn stehen"
    assert "system" not in rollen[1:], \
        f"system-Rolle nach dem Verlauf -> das Chat-Template lehnt das mit 400 ab: {rollen}"
    assert zeilen[1] == "True", "der RAG-Block muss in der letzten Nachricht stehen"


@pytest.mark.slow
def test_echte_antwort_mit_gefuellten_schichten(seite):
    """Die teure, aber einzig ehrliche Haelfte: eine echte Generierung durch das
    Modell, mit gefuelltem Gedankenfeld UND RAG-Block. Genau diese Kombination
    war am 2026-08-04 kaputt, waehrend alle Tests gruen waren.

        python3 -m pytest -m slow tests/test_codewesen_chat_kontext_rag.py
    """
    g = seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/neu",
                           data={"text": "PYTEST: Schichten muessen durchgehen."},
                           timeout=30_000).json()
    try:
        ausgabe = _im_dienst(
            "import hauhau_client as hc\n"
            f"v = cc.lade_chat_verlauf({WESEN!r}, max_eintraege=8)\n"
            f"m = cc.baue_messages({WESEN!r}, v, 'Antworte mit genau einem Wort: Ja.',\n"
            "                      rag_block='RAG-PROBE: ein Textstueck aus dem Archiv.')\n"
            "assert not any(x['role']=='system' for x in m[1:])\n"
            "a = hc.chat(m, think=False, max_tokens=24, timeout=600.0, id_slot=0)\n"
            "print('ANTWORT:' + a.strip()[:80].replace(chr(10), ' '))\n"
        )
        antwort = [z for z in ausgabe.splitlines() if z.startswith("ANTWORT:")]
        assert antwort, f"keine Antwort erzeugt:\n{ausgabe[-400:]}"
        assert len(antwort[0][8:].strip()) > 0, "leere Antwort"
    finally:
        seite.request.post(f"{BASIS}/api/gedankenfeld/{WESEN}/{g['id']}/entfernen",
                           timeout=30_000)


ANDERE_SECHS_WESEN = [w for w in ALLE_WESEN if w != WESEN]


@pytest.mark.slow
@pytest.mark.parametrize("wesen", ANDERE_SECHS_WESEN)
def test_echte_antwort_mit_gefuellten_schichten_fuer_jedes_wesen(browser_fuer_alle, wesen):
    """Dasselbe Versprechen wie test_echte_antwort_mit_gefuellten_schichten,
    aber fuer die sechs Wesen, die bisher nur strukturell (gruen) und nie mit
    einer echten Generierung geprueft waren. Daniel, 2026-08-12: 'und die
    anderen 6 wesen auch mal echt testen' -- 'playwright...gruen sagt nix'
    gilt fuer jedes der sieben einzeln, nicht nur fuer Schorschel.
    """
    from urllib.parse import quote
    pg = _seite_fuer(browser_fuer_alle, wesen)
    try:
        g = pg.request.post(f"{BASIS}/api/gedankenfeld/{quote(wesen)}/neu",
                             data={"text": "PYTEST: Schichten muessen durchgehen."},
                             timeout=30_000).json()
        try:
            ausgabe = _im_dienst(
                "import hauhau_client as hc\n"
                f"v = cc.lade_chat_verlauf({wesen!r}, max_eintraege=8)\n"
                f"m = cc.baue_messages({wesen!r}, v, 'Antworte mit genau einem Wort: Ja.',\n"
                "                      rag_block='RAG-PROBE: ein Textstueck aus dem Archiv.')\n"
                "assert not any(x['role']=='system' for x in m[1:])\n"
                "a = hc.chat(m, think=False, max_tokens=24, timeout=600.0, id_slot=0)\n"
                "print('ANTWORT:' + a.strip()[:80].replace(chr(10), ' '))\n"
            )
            antwort = [z for z in ausgabe.splitlines() if z.startswith("ANTWORT:")]
            assert antwort, f"{wesen}: keine Antwort erzeugt:\n{ausgabe[-400:]}"
            assert len(antwort[0][8:].strip()) > 0, f"{wesen}: leere Antwort"
        finally:
            pg.request.post(f"{BASIS}/api/gedankenfeld/{quote(wesen)}/{g['id']}/entfernen",
                             timeout=30_000)
    finally:
        pg.close()


def test_chat_pfad_benutzt_durchgehend_die_chat_instanz():
    """Vorabcall und Tokenzaehlung liefen zunaechst weiter auf der Instanz, die
    die sieben Wesen bedient -- der Chat waere trotz eigener Instanz langsam
    geblieben. Die Kontextanzeige feuert alle 5 s rund 15 /tokenize-Aufrufe."""
    ausgabe = _im_dienst(
        "print(cc._llama_basis())\n"
        "import inspect\n"
        "q = inspect.getsource(cc.rag_anfrage_bilden)\n"
        "print('id_slot=0' in q)\n"
    )
    zeilen = ausgabe.strip().splitlines()
    assert zeilen[0].endswith(":11435"), f"Tokenzaehlung geht an {zeilen[0]}"
    assert zeilen[1] == "True", "RAG-Vorabcall laeuft nicht auf der Chat-Instanz"
