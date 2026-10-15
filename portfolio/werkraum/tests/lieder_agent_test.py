#!/usr/bin/env python3
"""Test fuer welt/wesen_lieder_agent.py (Bauabschnitt A). Temp-Vault, kein Forum-Kontakt, die
echte Ausnahmeliste wird nicht angefasst (flarum_post_sperre wird im Speicher ersetzt).
Lauf: /root/werkraum/venv/bin/python3 /root/werkraum/tests/lieder_agent_test.py

Pflichtfrage (2026-10-02, einmalig): wann hoert dieser Code auf zu laufen, wann heilt/belebt er sich?
Aufhoeren: Er laeuft nur, wenn ihn jemand von Hand startet, und endet nach dem letzten Check mit
Exit-Code 0 (alles ok) oder 1 (mindestens ein Fehlschlag). Kein Dienst, kein Takt, kein Hintergrundprozess.
Heilen/Beleben: nichts davon -- ein Fehlschlag wird nur gezaehlt und gemeldet, der Test repariert nichts
und startet sich nicht neu. Er schreibt nur in ein frisches Temp-Verzeichnis (bleibt nach dem Lauf
liegen, der Pfad steht in der Ausgabe) und nie in den echten Lieder-Vault, die echte Ausnahmeliste
oder ans Forum."""
import os
import sys
import tempfile
import types

TMP = tempfile.mkdtemp(prefix="lieder_test_")
os.environ["LIEDER_VAULT_ROOT"] = TMP
os.environ["LIEDER_POSTEN_TROCKEN"] = "1"
sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/welt")

# flarum_post_sperre im Speicher ersetzen -- nie die echte Datei/das echte Protokoll beschreiben
_ausnahmen = {"diskussionen": {"3887": {"grund": "Daniels Einzug-Frage", "seit": "2026-09-16", "von": "Daniel"}}}
fake = types.ModuleType("flarum_post_sperre")
fake.ausnahme_liste = lambda: _ausnahmen
def _hinzu(disk_id, grund, wurzel_id=None, von="Daniel"):
    _ausnahmen["diskussionen"][str(disk_id)] = {"grund": grund, "seit": f"2026-10-02T{len(_ausnahmen['diskussionen']):02d}", "von": von}
fake.ausnahme_hinzufuegen = _hinzu
sys.modules["flarum_post_sperre"] = fake

import wesen_lieder_agent as L  # noqa: E402

ok = fehl = 0
def pruefe(name, bedingung, info=""):
    global ok, fehl
    if bedingung:
        ok += 1
        print(f"  ok   {name}")
    else:
        fehl += 1
        print(f"  FEHL {name} {info}")

def wirft(exc, fn, *a):
    try:
        fn(*a)
    except exc:
        return True
    except Exception as e:
        print("     (andere Ausnahme:", type(e).__name__, e, ")")
        return False
    return False

W = "R1ZZ1"
print("1 Pfade / Ausbruchschutz")
for schlecht in ["../x", "ideen/../../etc/passwd", "a/b/c", "evil/x", "_zaehler", ".versteckt", "", "ideen/.x", "ideen/_y"]:
    pruefe(f"abgelehnt: {schlecht!r}", wirft(ValueError, L._normalisiere, schlecht))
pruefe("ohne Ordner -> ideen", L._normalisiere("mein_gedanke") == ("ideen", "mein_gedanke.md"))
pruefe("unbekanntes Wesen", wirft(ValueError, L.vault_pfad, "Fremder"))

print("2 schreiben / anhaengen")
r = L.schreibe(W, "schnipsel/vers1", "Zeile eins\nZeile zwei")
p = L.vault_pfad(W) / "schnipsel" / "vers1.md"
pruefe("Datei angelegt", p.is_file())
meta, body = L._lies_datei(p)
pruefe("Kopf: art/status", meta["art"] == "schnipsel" and meta["status"] == "entwurf")
pruefe("Zeitstempel als Kommentar", "<!-- 20" in body and "Zeile eins" in body)
L.schreibe(W, "schnipsel/vers1", "Eindruck dazu")
meta, body = L._lies_datei(p)
pruefe("angehaengt, nicht ersetzt", "Zeile eins" in body and "Eindruck dazu" in body and body.count("<!--") == 2)
pruefe("leerer Text abgelehnt", wirft(ValueError, L.schreibe, W, "ideen/x", "   "))
L.schreibe(W, "ideen/thema_meer", "Wellen, Salz, Zeitraffer " * 40)
L.schreibe(W, "lieder/lied_a", "Strophe A " * 30)

print("3 lesen / erkunden")
pruefe("lesen", "Zeile eins" in L.lese(W, "schnipsel/vers1"))
pruefe("lesen: fehlt -> FileNotFound", wirft(FileNotFoundError, L.lese, W, "ideen/gibtsnicht"))
liste = L.erkunde(W)
pruefe("erkunden 3 Dateien", len(liste) == 3, str(liste))
pruefe("erkunden unbekannter Ordner", wirft(ValueError, L.erkunde, W, "geheim"))

print("3b Tolerante Namenssuche (nur Lesen/Freigeben/Zusammenfuegen)")
L.schreibe(W, "schnipsel/frequenz_des_werdens", "Echo sucht die Kehle")
L.schreibe(W, "schnipsel/frequenz_zwei", "noch ein Echo")
L.schreibe(W, "lieder/klang_der_nacht", "Nachtlied")
pruefe("eindeutiger Namensanfang", "Nachtlied" in L.lese(W, "lieder/klang"))
pruefe("eindeutiger Namensteil", "Nachtlied" in L.lese(W, "lieder/nacht"))
pruefe("falscher Ordner, eindeutiger Name", "Nachtlied" in L.lese(W, "schnipsel/klang_der_nacht"))
pruefe("mehrdeutig -> Fehler mit Kandidaten", wirft(FileNotFoundError, L.lese, W, "schnipsel/frequenz"))
try:
    L.lese(W, "schnipsel/frequenz")
except FileNotFoundError as e_:
    pruefe("Fehlertext nennt beide Kandidaten", "frequenz_des_werdens" in str(e_) and "frequenz_zwei" in str(e_), str(e_))
pruefe("schreiben legt weiter exakt an (kein Fuzzy)", L.schreibe(W, "schnipsel/frequenz_drei", "x") == "schnipsel/frequenz_drei")
pruefe("Namensaufloesung fuer die Freigabe (ohne zu posten)", L._finde_bestehende(W, "lieder/klang").name == "klang_der_nacht.md")

print("3c Eindruck")
L.fuehre_aus(W, "lied_schreiben:schnipsel/mit_ei", "Vers eins\nVers zwei\nEINDRUCK:\nDas hat mich ueberrascht.\nZweite Zeile davon.")
ei = (L.vault_pfad(W) / "schnipsel" / "mit_ei.md").read_text()
pruefe("Eindruck steht sichtbar unter dem Text", "Vers zwei" in ei and "**Eindruck:** Das hat mich ueberrascht.\nZweite Zeile davon." in ei, ei)
pruefe("EINDRUCK-Zeile selbst nicht mehr im Text", "\nEINDRUCK:" not in ei, ei)
pruefe("mit_ei nicht in ohne_eindruck", "schnipsel/mit_ei" not in L.ohne_eindruck(W))
pruefe("frequenz_zwei ohne Eindruck gelistet", "schnipsel/frequenz_zwei" in L.ohne_eindruck(W))
r_ = L.fuehre_aus(W, "lied_eindruck:schnipsel/frequenz_zwei", "Das war ein Test des Nachholens.")
pruefe("lied_eindruck haengt an Entwurf an", "gespeichert" in r_ and "**Eindruck:** Das war ein Test" in (L.vault_pfad(W) / "schnipsel" / "frequenz_zwei.md").read_text(), r_)
pruefe("danach nicht mehr gelistet", "schnipsel/frequenz_zwei" not in L.ohne_eindruck(W))
pruefe("Ticket nennt Dateien ohne Eindruck", "schnipsel/frequenz_drei" in L.baue_block(W) or "schnipsel/frequenz_des_werdens" in L.baue_block(W))
pruefe("leerer Eindruck abgelehnt", "fehlgeschlagen" in L.fuehre_aus(W, "lied_eindruck:schnipsel/frequenz_zwei", ""))

print("4 Rueckschau")
for i in range(8):
    L.schreibe(W, f"ideen/gross{i}", ("Wort " * 1000))
t = L.rueckschau(W)
grenze = L.RUECKSCHAU_TOKENS * L.ZEICHEN_PRO_TOKEN
pruefe("Budget eingehalten", 0 < len(t) <= grenze + 600, f"len={len(t)} grenze={grenze}")
pruefe("mehrere Dateien auf einmal", t.count("### ") >= 2, t[:80])
pruefe("leeres Wesen -> leer", L.rueckschau("jumpa") == "")

print("5 Zusammenfuegen")
vor = (L.vault_pfad(W) / "schnipsel" / "vers1.md").read_text()
rel = L.zusammenfuegen(W, "neues_lied", ["schnipsel/vers1", "lieder/lied_a"])
pruefe("Ziel in lieder/", rel == "lieder/neues_lied")
pruefe("Quelle unveraendert", (L.vault_pfad(W) / "schnipsel" / "vers1.md").read_text() == vor)
m, b = L._lies_datei(L.vault_pfad(W) / "lieder" / "neues_lied.md")
pruefe("Inhalt beider Quellen", "Zeile eins" in b and "Strophe A" in b and m["aus"].count(",") == 1)
pruefe("<2 Quellen abgelehnt", wirft(ValueError, L.zusammenfuegen, W, "x", ["schnipsel/vers1"]))
pruefe("Ziel existiert -> Fehler", wirft(FileExistsError, L.zusammenfuegen, W, "neues_lied", ["schnipsel/vers1", "lieder/lied_a"]))

print("6 Freigeben (trocken)")
pruefe("ideen/ nicht postbar", wirft(ValueError, L.freigeben, W, "ideen/thema_meer"))
pruefe("kein Lieder-Thread vorher", len(L.lieder_threads()) == 0)
msg = L.freigeben(W, "schnipsel/vers1")
pruefe("erster Post eroeffnet Lieder-Thread", "neuer Lieder-Thread" in msg and len(L.lieder_threads()) == 1, msg)
pruefe("Datei jetzt gepostet", L._lies_datei(L.vault_pfad(W) / "schnipsel" / "vers1.md")[0]["status"] == "gepostet")
pruefe("doppelt posten abgelehnt", wirft(ValueError, L.freigeben, W, "schnipsel/vers1"))
pruefe("anhaengen an gepostete Datei abgelehnt", wirft(ValueError, L.schreibe, W, "schnipsel/vers1", "mehr"))
for i in range(6):
    L.schreibe(W, f"schnipsel/s{i}", f"Schnipsel {i}")
    L.freigeben(W, f"schnipsel/s{i}")
st = L.tages_status(W)
pruefe("Schnipsel ohne Grenze (7 gepostet)", st["schnipsel"] == 7, str(st))
pruefe("Schnipsel zaehlen nicht als Lieder", st["lieder"] == 0)
for i in range(3):
    L.schreibe(W, f"lieder/l{i}", f"Lied {i}\nRefrain")
    m2 = L.freigeben(W, f"lieder/l{i}")
pruefe("3 ganze Lieder erlaubt", L.tages_status(W)["lieder"] == 3, m2)
L.schreibe(W, "lieder/l_vier", "Lied vier")
pruefe("4. Lied am selben Tag abgelehnt", wirft(ValueError, L.freigeben, W, "lieder/l_vier"))
pruefe("Schnipsel gehen trotzdem", "veroeffentlicht" in (L.schreibe(W, "schnipsel/nochmal", "x") and L.freigeben(W, "schnipsel/nochmal")))
L.schreibe(W, "schnipsel/fremdziel", "x")
pruefe("ziel=fremde Diskussion abgelehnt", wirft(PermissionError, L.freigeben, W, "schnipsel/fremdziel", "3887"))
pruefe("Datei nach Ablehnung weiter entwurf", L._lies_datei(L.vault_pfad(W) / "schnipsel" / "fremdziel.md")[0]["status"] == "entwurf")
pruefe("andere Wesen zaehlen getrennt", L.tages_status("jumpa")["lieder"] == 0)
msg2 = L.freigeben("jumpa", L.schreibe("jumpa", "lieder/hallo", "Hallo Welt") and "lieder/hallo", "neu:Mein eigener Faden")
pruefe("neu:<Titel> eroeffnet weiteren Thread", len(L.lieder_threads()) == 2 and "Mein eigener Faden" in msg2, msg2)

print("7 Direkte Antworten")
pruefe("unter 3887 (kein Lieder-Thread) abgelehnt", wirft(PermissionError, L.antworten, W, 3887, "hi"))
pruefe("unter unbekannter ID abgelehnt", wirft(PermissionError, L.antworten, W, 99999, "hi"))
tid = L.lieder_threads()[0]["id"]
pruefe("unter Lieder-Thread ok", "gesendet" in L.antworten(W, tid, "Gefaellt mir"))
pruefe("leere Antwort abgelehnt", wirft(ValueError, L.antworten, W, tid, " "))

print("8 Einladung / Ticket")
L._merke_tick_typ(W, "weiterarbeiten")
L._pflicht_erfuellt(W, "weiterarbeiten")
b_n = L.baue_block(W)
pruefe("erster Tick mit Rueckstand = Nachholen, mit Material", "zu diesen Dateien fehlt noch dein Eindruck" in b_n and "{" not in b_n and "Echo sucht die Kehle" in b_n, b_n[:300])
pruefe("Nachhol-Tick nennt Dateinamen und Eintragsform", "schnipsel/frequenz_des_werdens" in b_n and "lied_eindruck" in b_n)
L._pflicht_erfuellt(W, "nachholen")
b1 = L.baue_block(W)
pruefe("zweiter Tick wechselt zu Weiterarbeiten: erst waehlen, die grosse Datei kommt noch nicht", "Erst entscheidest du, dann liest du" in b1 and "lied_waehlen" in b1 and "DIE GROSSE DATEI" not in b1 and "zu diesen Dateien fehlt" not in b1)
pruefe("Ticket ohne Einladung", "Alles, was du bisher erstellt hast" in b1 and "LIEDER — DIE EINLADUNG" not in b1)
pruefe("Liste enthaelt ALLE eigenen Dateien samt Vorschau und Eindruck-Vermerk", all(("%s/%s" % (o, n)) in b1 for o, n in [("schnipsel", "frequenz_des_werdens"), ("schnipsel", "mit_ei"), ("lieder", "klang_der_nacht")]) and "mit Eindruck" in b1 and "noch ohne Eindruck" in b1 and "\u201eVers eins" in b1, b1[:1500])
pruefe("Ticket ist keine Menue-Auswahl mehr", "Such dir genau eine" not in b1 and "mindestens eine" in b1)
pruefe("keine offenen Platzhalter", "{" not in b1, b1[:300])
pruefe("eigene Dateinamen im Ticket", "schnipsel/vers1" in b1 or "ideen/thema_meer" in b1, b1[:400])
pruefe("Zaehler eingesetzt", "von hoechstens 3" in b1.replace("ö", "oe") or "von höchstens 3" in b1)
L._merke_tick_typ(W, "nachholen")
L._pflicht_erfuellt(W, "nachholen")
b2 = L.baue_block(W, mit_einladung=True)
pruefe("Einladung + Ticket", "LIEDER — DIE EINLADUNG" in b2 and "Alles, was du bisher erstellt hast" in b2 and "{" not in b2)
b3 = L.baue_block(W, folge="### x\nein Text")
pruefe("nach Rueckschau: Zurueckgelesen + Auswahl + Feinschliff", "ZURÜCKGELESEN" in b3 and "Alles, was du bisher erstellt hast" in b3 and "Feinschliff" in b3 and "{" not in b3)
pruefe("Lieder-Threads im Ticket genannt", f"d/{tid}" in b1)

print("9 Dispatcher")
pruefe("schreiben", "geschrieben" in L.fuehre_aus("jumpa", "lied_schreiben:ideen/neu1|Hallo"))
pruefe("schreiben mit TEXT-Block", "geschrieben" in L.fuehre_aus("jumpa", "lied_schreiben:ideen/neu2", "langer Text"))
pruefe("lesen", "Hallo" in L.fuehre_aus("jumpa", "lied_lesen:ideen/neu1"))
pruefe("erkunden", "Datei(en)" in L.fuehre_aus("jumpa", "lied_erkunden"))
L.fuehre_aus("jumpa", "lied_schreiben:schnipsel/mehrzeilig|Zeile eins.\\nZeile zwei.\\n\\nZeile vier")
inh = (L.vault_pfad("jumpa") / "schnipsel" / "mehrzeilig.md").read_text()
pruefe("woertliches \\n -> echte Umbrueche", "\\n" not in inh and "Zeile eins.\nZeile zwei.\n\nZeile vier" in inh, inh)
L.fuehre_aus("jumpa", "lied_schreiben:schnipsel/echt", "Echt\nmehrzeilig mit \\n im Text")
pruefe("echte Umbrueche (TEXT-Block) bleiben unveraendert", "mit \\n im Text" in (L.vault_pfad("jumpa") / "schnipsel" / "echt.md").read_text())
pruefe("rueckschau setzt Folge", "gleich" in L.fuehre_aus("jumpa", "lied_rueckschau") and L.hole_folge("jumpa") and L.hole_folge("jumpa") is None)
pruefe("Fehler werden Text, kein Wurf", L.fuehre_aus("jumpa", "lied_lesen:ideen/gibtsnicht").startswith("[Lieder fehlgeschlagen"))
fehltext = L.fuehre_aus("jumpa", "lied_freigeben:schnipsel/erfundener_name")
pruefe("falscher Dateiname: vorhandene Dateien werden genannt", "Das hast du aktuell" in fehltext and "schnipsel/mehrzeilig" in fehltext, fehltext)
pruefe("antworten fremder Thread", "fehlgeschlagen" in L.fuehre_aus("jumpa", "lied_antworten:3887|hi"))
pruefe("forum Liste", "Lieder-Threads" in L.fuehre_aus("jumpa", "lied_forum"))
pruefe("unbekannte Aktion", "unbekannte" in L.fuehre_aus("jumpa", "lied_quatsch"))

print("8b Mehrfach-Eindruck, Tick-Wechsel, Zusammenfuegen mit Format-Resten")
L.schreibe(W, "schnipsel/mf_a", "A-Vers")
L.schreibe(W, "schnipsel/mf_b", "B-Vers")
r_ = L.fuehre_aus(W, "lied_eindruck:mehrere", "## schnipsel/mf_a\nEindruck A\n## schnipsel/mf_b\nEindruck B\n## schnipsel/gibtsnicht\nx")
pruefe("mehrere Dateien in einer Aktion", "**Eindruck:** Eindruck A" in (L.vault_pfad(W) / "schnipsel" / "mf_a.md").read_text() and "**Eindruck:** Eindruck B" in (L.vault_pfad(W) / "schnipsel" / "mf_b.md").read_text(), r_)
pruefe("unbekannter Abschnitt meldet Fehler, bricht die anderen nicht ab", "gibtsnicht" in r_ and "fehlgeschlagen" in r_, r_)
L._merke_tick_typ(W, "weiterarbeiten")
L._pflicht_erfuellt(W, "weiterarbeiten")
pruefe("nach Weiterarbeiten kommt Nachholen (bei Rueckstand)", L.naechster_tick_typ(W) == "nachholen")
L._merke_tick_typ(W, "nachholen")
L._pflicht_erfuellt(W, "nachholen")
pruefe("nach Nachholen kommt Weiterarbeiten", L.naechster_tick_typ(W) == "weiterarbeiten")
_alt = L.ohne_eindruck
L.ohne_eindruck = lambda w: []
pruefe("ohne Rueckstand nur noch Weiterarbeiten", L.naechster_tick_typ(W) == "weiterarbeiten")
L.ohne_eindruck = _alt
fw_, im_, aus_ = L._nachhol_fenster(W)
pruefe("Nachhol-Fenster: nur Dateien ohne Eindruck", "mf_a" not in fw_ and not any("mf_a" in n for n in im_) and len(im_) >= 1, str(im_))
alt_b = L.vault_pfad(W) / "schnipsel" / "alt_mit_rest.md"
alt_b.write_text("---\nart: schnipsel\nstatus: entwurf\ntitel: alt_mit_rest\nerstellt: 2026-10-01 10:00\n---\n<!-- x -->\nErste Haelfte\n\nGEDANKE: ich besuche gleich etwas\n\nENTSCCHIEIDUNG: flarum_besuchen:d/1\n\nZweite Haelfte\n")
L.schreibe(W, "schnipsel/sauber", "Sauber")
L.zusammenfuegen(W, "lieder/mf_lied", ["schnipsel/alt_mit_rest", "schnipsel/sauber"])
zl = (L.vault_pfad(W) / "lieder" / "mf_lied.md").read_text()
haupt_zl, _, ablage_zl = zl.partition(L._ABGETRENNT_MARKE)
pruefe("Zusammenfuegen: Format-Absaetze raus aus dem Text, zweite Haelfte bleibt", "Erste Haelfte" in haupt_zl and "Zweite Haelfte" in haupt_zl and "GEDANKE" not in haupt_zl and "ENTSCC" not in haupt_zl and "Sauber" in haupt_zl, zl)
pruefe("Zusammenfuegen: abgetrennte Absaetze unveraendert unter der Trennlinie am Dateiende", "GEDANKE: ich besuche gleich etwas" in ablage_zl and "ENTSCCHIEIDUNG: flarum_besuchen:d/1" in ablage_zl and "alt_mit_rest" in ablage_zl and zl.rstrip().endswith("flarum_besuchen:d/1"), zl)
pruefe("abgetrennte Absaetze gehen nie ins Forum", "GEDANKE" not in L._post_inhalt("t", L._lies_datei(L.vault_pfad(W) / "lieder" / "mf_lied.md")[1]))
L.zusammenfuegen(W, "lieder/mf_lied2", ["lieder/mf_lied", "schnipsel/sauber"])
zl2 = (L.vault_pfad(W) / "lieder" / "mf_lied2.md").read_text()
pruefe("erneutes Zusammenfuegen: Ablage bleibt Ablage, nicht im Text", "GEDANKE" not in zl2.partition(L._ABGETRENNT_MARKE)[0] and "GEDANKE: ich besuche" in zl2.partition(L._ABGETRENNT_MARKE)[2], zl2)

print("8c Erst waehlen, dann lesen; Pflicht wird erzwungen")
Wp = "R1ZZ1"
L.schreibe(Wp, "schnipsel/pf_a", "Pflicht A")
L.schreibe(Wp, "schnipsel/pf_b", "Pflicht B")
L.fuehre_aus(Wp, "lied_eindruck:schnipsel/pf_a|Eindruck A")
L.fuehre_aus(Wp, "lied_eindruck:schnipsel/pf_b|Eindruck B")
for o_ in L.ohne_eindruck(Wp):
    L.schreibe_eindruck(Wp, o_, "Eindruck")
L._setze_pflicht(Wp, None)
t1 = L.baue_block(Wp)
pruefe("ohne Rueckstand: Weiterarbeiten, Dateiliste ohne grosse Datei", "lied_waehlen" in t1 and "DIE GROSSE DATEI" not in t1 and L.hole_folge(Wp) is None, t1[:200])
t2 = L.baue_block(Wp)
pruefe("nichts gewaehlt -> derselbe Tick kommt wieder, mit Erinnerung", "ERINNERUNG" in t2 and "lied_waehlen" in t2, t2[:200])
r_w = L.fuehre_aus(Wp, "lied_waehlen:schnipsel/gibtsnicht")
pruefe("unbekannte Datei zaehlt nicht als Wahl", "fehlgeschlagen" in r_w and L._offene_pflicht(Wp) == "weiterarbeiten", r_w)
r_w = L.fuehre_aus(Wp, "lied_waehlen:schnipsel/pf_a, schnipsel/pf_b")
pruefe("Wahl mit zwei Dateien ok, Pflicht erfuellt", "Gewählt" in r_w and L._offene_pflicht(Wp) is None, r_w)
fo_ = L.hole_folge(Wp)
pruefe("danach kommt die grosse Datei samt vollem Text der Wahl (Folge)", fo_ and "DEINE WAHL" in fo_ and "Pflicht A" in fo_ and "Pflicht B" in fo_ and "DIE GROSSE DATEI" in fo_, str(fo_)[:300])
tb = L.baue_block(Wp, folge=fo_)
pruefe("Folge-Block: grosse Datei + Liste, ohne Erst-waehlen-Text", "DIE GROSSE DATEI" in tb and "Erst entscheidest du" not in tb and "Über dieser Liste steht die große Datei" in tb and "{" not in tb, tb[:200])
L.schreibe(Wp, "schnipsel/pf_c", "Neu ohne Eindruck")
L._setze_pflicht(Wp, None)
L._merke_tick_typ(Wp, "weiterarbeiten"); L._pflicht_erfuellt(Wp, "weiterarbeiten")
n1 = L.baue_block(Wp)
pruefe("Nachholen: Tick ohne Eindruck bleibt offen", "zu diesen Dateien fehlt" in n1 and L._offene_pflicht(Wp) == "nachholen")
n2 = L.baue_block(Wp)
pruefe("Nachholen nicht erfuellt -> wieder Nachholen mit Erinnerung", "zu diesen Dateien fehlt" in n2 and "ERINNERUNG" in n2 and "Eindruck" in n2)
L.fuehre_aus(Wp, "lied_eindruck:schnipsel/pf_c|Jetzt ein Eindruck")
pruefe("Eindruck geschrieben -> Pflicht erfuellt", L._offene_pflicht(Wp) is None)

print("9a Aktionszeilen im Text")
L.fuehre_aus("jumpa", "lied_schreiben:schnipsel/mit_aktion", "Echte Zeile\nZweite Zeile\n\nlied_freigeben:schnipsel/mit_aktion\nENTSCHEIDUNG: nachdenken")
inh2 = (L.vault_pfad("jumpa") / "schnipsel" / "mit_aktion.md").read_text()
pruefe("Aktionszeilen beim Schreiben entfernt", "lied_freigeben" not in inh2 and "ENTSCHEIDUNG" not in inh2 and "Zweite Zeile" in inh2, inh2)
L.fuehre_aus("jumpa", "lied_schreiben:schnipsel/mit_format", "Zeile eins\nEINSICHT: das fuehlte sich gut an\n\nGEDANKE: ich besuche gleich etwas\n\nENTSCCHIEIDUNG: flarum_besuchen:d/1859\nBEGRÜNDUNG: weil")
inh3 = (L.vault_pfad("jumpa") / "schnipsel" / "mit_format.md").read_text()
pruefe("ab GEDANKE:/ENTSCHEIDUNG: (auch Tippfehler) abgeschnitten", "Zeile eins" in inh3 and "EINSICHT" in inh3 and "GEDANKE" not in inh3 and "ENTSCC" not in inh3 and "BEGR" not in inh3, inh3)
pruefe("Text nur aus Aktionszeile -> abgelehnt", "fehlgeschlagen" in L.fuehre_aus("jumpa", "lied_schreiben:schnipsel/nur_aktion", "lied_freigeben:x"))
pruefe("Liedzeile mit 'Lied' im Wort bleibt", "Das Lied: klingt" in (L.schreibe("jumpa", "schnipsel/wort", "Das Lied: klingt\nlied ohne unterstrich: bleibt") and (L.vault_pfad("jumpa") / "schnipsel" / "wort.md").read_text()))

print("9b Zwischenstatus sendet")
orig_poste = L._poste
def kaputt(*a, **k):
    raise RuntimeError("Forum nicht erreichbar")
L._poste = kaputt
L.schreibe("jumpa", "schnipsel/fehlerfall", "Text")
pruefe("Sendefehler wird weitergegeben", wirft(RuntimeError, L.freigeben, "jumpa", "schnipsel/fehlerfall"))
pruefe("nach Sendefehler zurueck auf entwurf", L._lies_datei(L.vault_pfad("jumpa") / "schnipsel" / "fehlerfall.md")[0]["status"] == "entwurf")
pruefe("Zaehler nach Sendefehler unveraendert", L.tages_status("jumpa")["schnipsel"] == 0)
L._poste = orig_poste
fp = L.vault_pfad("jumpa") / "schnipsel" / "haengt.md"
L.schreibe("jumpa", "schnipsel/haengt", "Text")
m_, b_ = L._lies_datei(fp); m_["status"] = "sendet"; fp.write_text(L._fm_schreibe(m_, b_))
pruefe("haengende Datei (sendet) blockiert Doppelposten", wirft(ValueError, L.freigeben, "jumpa", "schnipsel/haengt"))

print("10 Tageswechsel")
alt = L._heute
L._heute = lambda: "2099-01-01"
pruefe("neuer Tag -> Zaehler 0", L.tages_status(W)["lieder"] == 0 and L.tages_status(W)["schnipsel"] == 0)
L._heute = alt

print(f"\n{ok} ok, {fehl} fehl  (Temp: {TMP})")
sys.exit(1 if fehl else 0)
