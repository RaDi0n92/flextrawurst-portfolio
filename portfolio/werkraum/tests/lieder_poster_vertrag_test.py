#!/usr/bin/env python3
"""Vertragstest: wesen_lieder_agent._poste() gegen den ECHTEN flarum_poster (Draft, Lock, Retry, Archiv),
aber mit abgefangenen Forum-Aufrufen (flarum_api.post_reply / start_discussion) und Temp-Pfaden --
es geht nichts ans Forum, und es werden keine echten Wesen-Ordner, Zaehler oder Locks angefasst.
Lauf: /root/werkraum/venv/bin/python3 /root/werkraum/tests/lieder_poster_vertrag_test.py

Pflichtfrage (2026-10-02, einmalig): wann hoert dieser Code auf zu laufen, wann heilt/belebt er sich?
Aufhoeren: Er laeuft nur auf Handstart und endet nach dem letzten Check mit Exit-Code 0 oder 1 -- kein
Dienst, kein Takt. Alles, was er umlegt (die Ausnahmeliste in flarum_post_sperre, die Pfade und Forum-
Aufrufe in flarum_poster, die Wartezeit time.sleep) ist nur eine Variable im Speicher dieses einen
Prozesses und verschwindet mit ihm; die Dateien und Module auf der Platte bleiben unveraendert, auch wenn
der Test mittendrin abbricht. Die Ausnahmeliste wird am Ende zusaetzlich zurueckgesetzt.
Heilen/Beleben: nichts davon -- Fehlschlaege werden nur gezaehlt und gemeldet. Geschrieben wird nur in
ein frisches Temp-Verzeichnis (bleibt liegen, Pfad steht in der Ausgabe), nie in echte Wesen-Ordner,
Zaehler, den echten Lock oder ans Forum."""
import os
import sys
import tempfile
import types
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="lieder_vertrag_"))
os.environ["LIEDER_VAULT_ROOT"] = str(TMP / "vault")
os.environ.pop("LIEDER_POSTEN_TROCKEN", None)
sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/welt")

_ausn = {"diskussionen": {}}
import flarum_post_sperre as echte_sperre  # echtes Modul laden (nur lesend benutzt)
_orig_ausn_liste, _orig_ausn_hinzu = echte_sperre.ausnahme_liste, echte_sperre.ausnahme_hinzufuegen
echte_sperre.ausnahme_liste = lambda: _ausn
echte_sperre.ausnahme_hinzufuegen = lambda d, grund, wurzel_id=None, von="x": _ausn["diskussionen"].__setitem__(
    str(d), {"grund": grund, "seit": "2026-10-02T00", "von": von})

import flarum_poster as FP  # noqa: E402
FP.CODEWESEN_BASE = TMP / "codewesen"
FP.TAGESZAEHLER_FILE = FP.CODEWESEN_BASE / "_global" / "tageszaehler.json"
FP.LOCK_FILE = TMP / "flarum_write.lock"

aufrufe = []
def fake_post_reply(discussion_id, content, token_or_username, erlaubt_trotz_sperre=False):
    aufrufe.append(("reply", discussion_id, content, token_or_username, erlaubt_trotz_sperre))
    return {"data": {"id": "5001", "type": "posts"}}
def fake_start(title, content, tag_ids, token_or_username, erlaubt_trotz_sperre=False, ausnahme_wurzel=None):
    aufrufe.append(("neu", title, content, tag_ids, token_or_username, erlaubt_trotz_sperre))
    return {"data": {"id": "6001", "type": "discussions"}}
FP.api.post_reply = fake_post_reply
FP.api.start_discussion = fake_start

import wesen_lieder_agent as L  # noqa: E402

ok = fehl = 0
def pruefe(name, bed, info=""):
    global ok, fehl
    if bed:
        ok += 1; print(f"  ok   {name}")
    else:
        fehl += 1; print(f"  FEHL {name} {info}")

W = "Schorschel"
print("1 Erste Freigabe eroeffnet Lieder-Thread ueber den echten Poster")
L.schreibe(W, "schnipsel/erster", "Zeile eins\nZeile zwei")
msg = L.freigeben(W, "schnipsel/erster")
pruefe("Meldung nennt neuen Thread d/6001", "d/6001" in msg, msg)
a = aufrufe[-1]
pruefe("start_discussion aufgerufen", a[0] == "neu")
pruefe("Tag 5 (Showcase / Projekte) uebergeben", a[3] == [5], str(a[3]))
pruefe("als Wesen gepostet", a[4] == W, str(a[4]))
pruefe("erlaubt_trotz_sperre nur wegen Lieder-Weg gesetzt", a[5] is True)
pruefe("Inhalt ohne Zeitstempel-Kommentar", "<!--" not in a[2] and "Zeile eins" in a[2], a[2])
pruefe("Thread in Ausnahmeliste mit Praefix", _ausn["diskussionen"].get("6001", {}).get("grund", "").startswith("Lieder-Thread"))
pruefe("Draft archiviert (gepostet_*)", any(p.name.startswith("gepostet_") for p in (FP.CODEWESEN_BASE / W / "entwuerfe" / "archiv").glob("*")))

print("2 Zweite Freigabe geht als Antwort in den Thread")
L.schreibe(W, "lieder/mein_lied", "Strophe 1\n\nRefrain\n\n## Eindruecke\nHat Spass gemacht")
msg2 = L.freigeben(W, "lieder/mein_lied")
b = aufrufe[-1]
pruefe("post_reply an Thread 6001", b[0] == "reply" and b[1] == 6001, str(b[:2]))
pruefe("Titel als Ueberschrift, Eindruecke mitgepostet", b[2].startswith("### mein_lied") and "Hat Spass gemacht" in b[2], b[2][:80])
pruefe("Zaehler: 1 Lied, 1 Schnipsel", L.tages_status(W)["lieder"] == 1 and L.tages_status(W)["schnipsel"] == 1, str(L.tages_status(W)))

print("2b Aktionszeile in schon bestehender Datei wird beim Posten entfernt")
altlast = L.vault_pfad(W) / "schnipsel" / "altlast.md"
altlast.parent.mkdir(parents=True, exist_ok=True)
altlast.write_text("---\nart: schnipsel\nstatus: entwurf\ntitel: altlast\n---\n<!-- x -->\nZeile A\n\nlied_freigeben:schnipsel/altlast\n")
L.freigeben(W, "schnipsel/altlast")
pruefe("gepostet ohne Aktionszeile", "lied_freigeben" not in aufrufe[-1][2] and "Zeile A" in aufrufe[-1][2], aufrufe[-1][2])

print("2c Eindruck unter schon gepostete Datei geht als Antwort in ihren Thread")
L.schreibe(W, "schnipsel/mit_eindruck", "Vers\nEINDRUCK:\nSo ist es entstanden.")
L.freigeben(W, "schnipsel/mit_eindruck")
pruefe("Eindruck im ersten Post mit gepostet", "**Eindruck:** So ist es entstanden." in aufrufe[-1][2], aufrufe[-1][2])
L.schreibe(W, "schnipsel/ohne_eindruck_x", "Nur Vers")
L.freigeben(W, "schnipsel/ohne_eindruck_x")
rr = L.fuehre_aus(W, "lied_eindruck:schnipsel/ohne_eindruck_x", "Nachgeholt: das war so gemeint.")
pruefe("Nachgeholter Eindruck als Antwort gepostet", "gepostet" in rr and aufrufe[-1][0] == "reply" and aufrufe[-1][1] == 6001 and aufrufe[-1][2].startswith("**Eindruck:** Nachgeholt"), rr + str(aufrufe[-1]))
pruefe("Eindruck steht danach auch in der Datei", "**Eindruck:** Nachgeholt" in (L.vault_pfad(W) / "schnipsel" / "ohne_eindruck_x.md").read_text())

print("3 Direkte Antwort")
msg3 = L.antworten("jumpa", 6001, "Mir gefaellt der Refrain")
c = aufrufe[-1]
pruefe("post_reply als jumpa", c[0] == "reply" and c[3] == "jumpa" and c[1] == 6001)
pruefe("Meldung mit Post-ID", "5001" in msg3, msg3)
n = len(aufrufe)
try:
    L.antworten("jumpa", 3887, "x")
except PermissionError:
    pass
pruefe("fremder Thread: kein Forum-Aufruf", len(aufrufe) == n)

print("4 Fehler des Forums")
def kaputt(*a, **k):
    raise Exception("503 Forum down")
FP.api.post_reply = kaputt
FP.time.sleep = lambda s: None  # Retry-Wartezeiten im Test ueberspringen
L.schreibe(W, "schnipsel/zweiter", "noch ein Vers")
try:
    L.freigeben(W, "schnipsel/zweiter")
    pruefe("Forumsfehler wird gemeldet", False)
except RuntimeError as e:
    pruefe("Forumsfehler wird gemeldet", "503" in str(e), str(e))
pruefe("Datei danach wieder entwurf", L._lies_datei(L.vault_pfad(W) / "schnipsel" / "zweiter.md")[0]["status"] == "entwurf")
pruefe("Zaehler unveraendert (4 Schnipsel vor dem Fehler)", L.tages_status(W)["schnipsel"] == 4)
pruefe("Draft als fehler_* archiviert", any(p.name.startswith("fehler_") for p in (FP.CODEWESEN_BASE / W / "entwuerfe" / "archiv").glob("*")))

echte_sperre.ausnahme_liste, echte_sperre.ausnahme_hinzufuegen = _orig_ausn_liste, _orig_ausn_hinzu
print(f"\n{ok} ok, {fehl} fehl  (Temp: {TMP})")
sys.exit(1 if fehl else 0)
