#!/usr/bin/env python3
"""Test fuer Bauabschnitt C: browser_agent.py (Schalter LIEDER_AKTIV, Prompt-Block, Aktionsvokabular,
Dispatcher). Temp-Vault, kein Forum-Kontakt (LIEDER_POSTEN_TROCKEN), keine echte Ausnahmeliste.
Lauf: /root/werkraum/venv/bin/python3 /root/werkraum/tests/lieder_browser_agent_test.py

Pflichtfrage (2026-10-02, einmalig): wann hoert dieser Code auf zu laufen, wann heilt/belebt er sich?
Aufhoeren: Er laeuft nur auf Handstart und endet nach dem letzten Check mit Exit-Code 0 oder 1 -- kein
Dienst, kein Takt. Der Import von browser_agent registriert in diesem Testprozess die SIGTERM/SIGINT-
Handler des Agents; sie enden mit dem Prozess. LIEDER_AKTIV wird nur als Variable im Speicher dieses
einen Prozesses umgelegt (und am Ende wieder auf False gesetzt) -- die Datei browser_agent.py und die
laufenden Agents bleiben unberuehrt, auch wenn der Test mittendrin abbricht.
Heilen/Beleben: nichts davon -- Fehlschlaege werden nur gezaehlt und gemeldet. Geschrieben wird nur in
ein frisches Temp-Verzeichnis, nie in den echten Lieder-Vault, die echte Ausnahmeliste oder ans Forum."""
import os
import sys
import tempfile
import types

TMP = tempfile.mkdtemp(prefix="lieder_ba_test_")
os.environ["LIEDER_VAULT_ROOT"] = TMP
os.environ["LIEDER_POSTEN_TROCKEN"] = "1"
sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/welt")

_ausn = {"diskussionen": {}}
fake = types.ModuleType("flarum_post_sperre")
fake.ausnahme_liste = lambda: _ausn
fake.ausnahme_hinzufuegen = lambda d, grund, wurzel_id=None, von="x": _ausn["diskussionen"].__setitem__(
    str(d), {"grund": grund, "seit": "2026-10-02T00", "von": von})
sys.modules["flarum_post_sperre"] = fake

import browser_agent as B  # noqa: E402
import wesen_lieder_agent as L  # noqa: E402

ok = fehl = 0
def pruefe(name, bed, info=""):
    global ok, fehl
    if bed:
        ok += 1; print(f"  ok   {name}")
    else:
        fehl += 1; print(f"  FEHL {name} {info}")

SEITE = {"url": "https://flextrawurst.de/flarum-live/", "titel": "Flarum", "text": "Startseite", "elemente": []}
def prompt(**kw):
    return B.baue_prompt("jumpa", SEITE, "", [], browserlos=True, **kw)

print("1 Schalter aus (im Test explizit umgelegt -- der echte Wert in browser_agent.py ist seit dem Rollout True)")
B.LIEDER_AKTIV = False
pruefe("Schalter im Test aus", B.LIEDER_AKTIV is False)
p0 = prompt(lieder_block="TESTBLOCK")
pruefe("keine lied_-Aktionen im Vokabular", "lied_schreiben" not in p0)
pruefe("kein Lieder-Block im Prompt", "TESTBLOCK" not in p0)
r = B.fuehre_aktion_aus_ohne_browser("lied_schreiben:schnipsel/x|Hallo Welt", "jumpa", None, "", "", gedanke="g")
pruefe("Aktion abgelehnt, nichts geschrieben", not (L.vault_pfad("jumpa") / "schnipsel" / "x.md").exists(), str(r))

print("2 Schalter an")
B.LIEDER_AKTIV = True
p1 = prompt(lieder_block="TESTBLOCK")
for a in ["lied_schreiben", "lied_lesen", "lied_erkunden", "lied_rueckschau", "lied_zusammenfuegen",
          "lied_freigeben", "lied_forum", "lied_antworten", "lied_eindruck"]:
    pruefe(f"Vokabular enthaelt {a}", a in p1)
pruefe("Lieder-Block im Prompt", "TESTBLOCK" in p1)
pruefe("TEXT:-Beispiel fuer Mehrzeiliges im Vokabular", "TEXT:\n" in p1 and "mehrere" in p1.lower() or "Mehrere" in p1)
pruefe("Hinweis: kein \\n in die ENTSCHEIDUNG-Zeile", "mit \\n in die ENTSCHEIDUNG" in p1)
p2 = prompt()
pruefe("ohne Block: Aktionen ja, Block nein", "lied_schreiben" in p2 and "TESTBLOCK" not in p2)
p3 = B.baue_prompt("jumpa", SEITE, "", [], vault_takt=True, browserlos=True, lieder_block="TESTBLOCK")
pruefe("im Vault-Takt-Prompt weder Aktionen noch Block", "lied_schreiben" not in p3 and "TESTBLOCK" not in p3)
echt = L.baue_block("jumpa", mit_einladung=True)
p4 = prompt(lieder_block=echt)
pruefe("echter Einladungs-Prompt mit Antwortformat", "ENTSCHEIDUNG:" in p4 and "Alles, was du bisher erstellt hast" in p4)
print(f"     (Prompt-Laenge Einladung+Ticket: {len(p4)} Zeichen, ~{len(p4)//3} Token; ohne Block: {len(p2)} Zeichen)")
pruefe("Einladungs-Prompt unter 6500 Token (Slot ~11111)", len(p4) // 3 < 6500)

print("3 Dispatcher bei Schalter an")
r = B.fuehre_aktion_aus_ohne_browser("lied_schreiben:schnipsel/vers|Zeile eins", "jumpa", None, "", "", gedanke="g")
pruefe("schreiben -> Kontext", r[1] and "geschrieben" in r[1], str(r))
pruefe("kurzer Vers OHNE angehaengten Gedanken", "Gedanke zu diesem Eintrag" not in (L.vault_pfad("jumpa") / "schnipsel" / "vers.md").read_text())
r = B.fuehre_aktion_aus_ohne_browser("lied_schreiben:ideen/lang", "jumpa", None, "", "", gedanke="g", freitext="Langer Text\nzweite Zeile")
pruefe("TEXT-Block (freitext) wird benutzt", "zweite Zeile" in (L.vault_pfad("jumpa") / "ideen" / "lang.md").read_text(), str(r))
r = B.fuehre_aktion_aus_ohne_browser("lied_schreiben:ideen/etikett|mein_lied.md", "jumpa", None, "", "", gedanke="g")
pruefe("nur Dateiname hinter | abgelehnt", r[1] and "fehlgeschlagen" in r[1] and not (L.vault_pfad("jumpa") / "ideen" / "etikett.md").exists(), str(r))
r = B.fuehre_aktion_aus_ohne_browser("lied_rueckschau", "jumpa", None, "", "")
pruefe("Rueckschau -> Folge gesetzt", L.hole_folge("jumpa") is not None, str(r))
r = B.fuehre_aktion_aus_ohne_browser("lied_freigeben:schnipsel/vers", "jumpa", None, "", "")
pruefe("Freigabe (trocken) -> eroeffnet Lieder-Thread", r[1] and "Lieder-Thread" in r[1], str(r))
tid = L.lieder_threads()[0]["id"]
r = B.fuehre_aktion_aus_ohne_browser(f"lied_antworten:{tid}|Schoen", "R1ZZ1", None, "", "")
pruefe("direkte Antwort unter Lieder-Thread", r[1] and "gesendet" in r[1], str(r))
r = B.fuehre_aktion_aus_ohne_browser("lied_antworten:3887|hallo", "R1ZZ1", None, "", "")
pruefe("direkte Antwort unter fremdem Thread abgelehnt", r[1] and "kein Lieder-Thread" in r[1], str(r))
r = B.fuehre_aktion_aus_ohne_browser("nachdenken", "jumpa", None, "", "")
pruefe("andere Aktionen unberuehrt", r[0] == "wach")

print("4 Browser-Variante hat den Zweig")
import inspect
pruefe("fuehre_aktion_aus enthaelt lied_-Zweig", 'e.startswith("lied_")' in inspect.getsource(B.fuehre_aktion_aus))

B.LIEDER_AKTIV = False
print(f"\n{ok} ok, {fehl} fehl  (Temp: {TMP})")
sys.exit(1 if fehl else 0)
