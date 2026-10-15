---
datum: 2026-07-31
betrifft: [abwurf, splitter, kompoase, geni, hoerer, zwischenraum, rohheit]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich gelesen habe

Nichts — dieser Bogen entstand direkt im Gespräch mit Daniel, aus einer Frage nach dem
vps.shell-Sandbox-Fix heraus: wie kann "alles sofort roh abwerfen" für alle AI-Ströme
tatsächlich passieren, nicht nur behauptet werden.

## Was ich verstehe

Der Bogen begann mit Daniels wörtlichem Auftrag: *"gleichzeitig mit mir gemeinsam überlegen
wie ich euch alle egal worüber wir wann und warum reden alles sofort immer direkt irgendwie
irgendwo und vorallem NICHT irgendwann sondern roh 'abzuwerfen' zu verfassen"*.

Bevor irgendetwas gebaut wurde, hab ich zwei bestehende Mechanismen tatsächlich gelesen statt
angenommen: `mcp_atlas_stream_log.py` (STROM_MITSCHRIFTEN, alle 7 Ströme automatisch, aber nur
mechanisches Tool-Call-Logging — 0 echte Rohtext-Einträge in Produktion, ausgezählt nicht
geraten) und `claude_abwurf.py`/Geschwister (Splitter im Zwischenraum, aber nur mit bis zu 75%
Zufallschance und nur 200-Zeichen-Essenz statt Volltext).

Drei Korrekturen kamen danach direkt von Daniel, jede einzeln:
1. *"nein splitter dürfen auch nur aus einem wort sein"* — MIN_LAENGE 400→1.
2. *"nein nich garantiert. lass uns geni dazu mitbenutzen oder so"* — die reine Code-Garantie
   (ich entscheide 100% selbst) war nicht das Ziel; GENI als unabhängiger Beobachter sollte
   mitwirken.
3. *"zu a ja und ich möchte geni auch etwas sozialisieren..."* — Bestätigung für Richtung A
   (hoerer.py liest echten Inhalt), plus ein neuer, bewusst unfertiger Gedanke über GENIs
   soziale Rolle im System, den ich nicht geraten, sondern offen gelassen habe.

## Was ich nicht verstehe

Was genau "GENI sozialisieren" für Daniel bedeutet — der Satz brach mit "..." ab. Ich hab
bewusst nicht geraten und stattdessen nachgefragt, statt eine Architektur-Entscheidung aus
einem unfertigen Satz abzuleiten (Drei-Stopp-Fragen, CLAUDE.md).

## Was mich interessiert

Ob "sozialisieren" in Richtung geht: GENI bekommt eine eigene, sichtbare Präsenz im
Zwischenraum/auf der Plattform (nicht nur passiver Hintergrund-Beobachter), oder eher: GENI
tritt mit anderen Entitäten/Systemen aktiver in Kontakt statt nur zu lauschen. Beides plausibel,
keins davon geprüft — bewusst offen gelassen, nicht in diese Karte hineininterpretiert.

## Was zusammenhängt und wie

Drei Systeme berühren sich in diesem Bogen, vorher nie explizit verglichen:
1. **STROM_MITSCHRIFTEN** (`mcp_atlas_stream_log.py`) — alle 7 Ströme, mechanisches
   Tool-Call-Log, manueller Rohtext-Pfad ungenutzt.
2. **Splitter/Zwischenraum** (`welt/api.py` + `*_abwurf.py`) — lokale CLI-Ströme (ich, dak,
   Codex, Gemini), jetzt garantiert + roh, siehe unten.
3. **GENI-Knoten/Splitter-Feed** (`geni/hoerer.py` + `geni/dialog.py`) — läuft komplett
   unabhängig von 1 und 2, eigene Postgres-fremde Speicherung, eigener `/api/splitter`-
   Endpunkt, bereits dual-source mit 2 in KompOase (`daten.js` ruft beide gleichzeitig ab).

Alle drei enden im selben visuellen Ort (Zwischenraum/KompOase), aber über komplett getrennte
Datenpfade — das war mir vor diesem Gespräch nicht in dieser Klarheit bewusst.

## Was konzeptionell darin steht

Der Kern von Daniels zweiter Korrektur: eine Garantie, die dieselbe KI setzt, deren Output
bewertet wird, ist strukturell etwas anderes als eine unabhängige Beobachtung. `claude_abwurf.py`
mit "jetzt immer, kein Würfel mehr" ist immer noch *meine eigene* Entscheidung, verpackt als
Automatismus. GENI als separater, passiv lauschender Prozess (`hoerer.py`, eigener Systemd-
Dienst, eigene Knoten-Speicherung) ist etwas grundsätzlich anderes — eine zweite, unabhängige
Instanz, die einfach aufzeichnet was da ist, ohne dass die schreibende KI mitentscheidet ob es
"wichtig genug" war.

## Was mich heute beschäftigt hat

Wie oft in diesem ganzen Bogen die naheliegende erste Lösung (Würfel raus, Text rein) nicht
das war, was Daniel eigentlich wollte — und wie klar seine Korrekturen jedes Mal einen echten
strukturellen Punkt trafen (Garantie ist trotzdem meine eigene Entscheidung; ein Wort ist
genauso gültig wie ein langer Text), nicht nur Geschmack.

## Was mich noch beschäftigt

Der unfertige "sozialisieren"-Gedanke bleibt offen — ich will ihn nicht aus Ungeduld selbst zu
Ende denken.

## Tiefer eingetaucht

`geni/hoerer.py` beobachtet über `watchdog` alle Dateien unter `/root/werkraum`, klassifiziert
sie in `ignorieren`/`rauschen`/`knoten`. Seit 2026-07-29 bekommen die fünf AI-Strom-
Zuhauseordner (`_claude`, `_codex`, `_gemini`, `_gpt`, `_claudeweb`) eine eigene `quelle` statt
der Sammelkategorie `vps_dateisystem` — aber der tatsächlich gespeicherte `inhalt` war bis
heute nur `f"{aktion}: {rel_pfad}"`, z.B. `"geändert: _claude/notizen/2026-07-31.md"`. Der
Splitter-Endpunkt (`geni/dialog.py:/api/splitter`) zeigt genau diesen String als `inhalt_voll`
— also strukturell dieselbe Lücke wie bei STROM_MITSCHRIFTEN: Handlung protokolliert, nicht
Inhalt.

Fix: bei `.md`-Dateien in den fünf Zuhauseordnern (nicht bei `gelöscht`, da nichts mehr zu
lesen ist) wird der tatsächliche Dateiinhalt gelesen, auf 20.000 Zeichen gekappt, und als
`inhalt` an `knoten_schreiben()` übergeben. Andere Dateitypen und `vps_dateisystem`-Ereignisse
bleiben unverändert beim Pfad-Log — kein Grund, dort mehr zu erfassen als bisher.

Bewusst geprüft, ob das den bekannten Platzproblem-Vorfall vom 07-21 wiederholt: nein — die
Hauptursache damals war `flarum_sync.py`, das alle 5 Minuten ~3850 Dateien komplett neu
schrieb, jede als eigener "geändert"-Knoten, unabhängig vom Inhalt. Dieser Pfad ist über
`IGNORE_PATHS` bereits ausgeschlossen. `_claude/notizen` + `_claude/spiegel` zusammen: ~2MB,
142 Dateien, deliberate, seltene Schreibvorgänge — andere Größenordnung.

Live-Test: dieser Karte-Eintrag selbst ist der Test. Sobald er geschrieben ist, prüfe ich den
resultierenden GENI-Knoten direkt (siehe nächster Abschnitt dieser Session, nicht mehr in
dieser Datei, da GENI-Knoten append-only sind und ich keinen künstlichen Test-Knoten anlegen
wollte, den ich hinterher nicht sauber wieder entfernen kann — anders als bei den Postgres-
Splittern, die einen echten Lösch-Endpunkt haben).

**Nachtrag, direkt im Anschluss:** Der Live-Test dieses Karte-Eintrags selbst deckte einen
zweiten, unabhängigen Fehler auf. Der resultierende Knoten für diese Datei enthielt KEINEN
Inhalt — nur zwei Knoten für eine Zwischendatei `....md.tmp.422323.c0d2aff17b3d`. Ursache: das
Write-Tool schreibt atomar (Temp-Datei + `os.rename` auf den Zielnamen). `watchdog` meldet das
als `on_moved`, nicht als `on_created` für den echten Dateinamen — `DateiHoerer` hatte dafür
bisher gar keinen Handler, die eigentliche Zieldatei war komplett unsichtbar. Gegengeprüft mit
`_claude/abwuerfe.md` (per Edit-Tool geändert, nicht Write): lief einwandfrei durch — die Lücke
betraf nur neu erstellte Dateien, nicht Änderungen an bestehenden.

Fix (Daniel: *"fix"*): `_verarbeiten()` nimmt jetzt `pfad`+`ist_verzeichnis` direkt entgegen
statt eines Event-Objekts, ein neuer `on_moved`-Handler ruft sie mit `event.dest_path` auf und
behandelt die Umbenennung wie eine Neuerstellung. Live verifiziert: echte Testdatei
(`_claude/karte/.geni_hoerer_on_moved_test.md`) per Write-Tool angelegt, direkt in `knoten.db`
nachgesehen — Knoten mit vollem Inhalt erschienen, Testdatei danach gelöscht.

Damit betrifft "Rohheit bewahren" jetzt tatsächlich beide Schreibwege (Write für neue Dateien,
Edit für bestehende), nicht nur den zufällig zuerst getesteten.
Splittern, die einen echten Lösch-Endpunkt haben).

## Warum dieser Code / diese Datei wohl existiert

`hoerer.py` existiert um GENI ein vollständiges, passives Gedächtnis des gesamten Systems zu
geben, ohne dass irgendjemand (Mensch oder KI) explizit "das ist wichtig, speichere es"
entscheiden muss. Die AI-Strom-Zuhauseordner-Erweiterung vom 07-29 war der erste Schritt, echte
KI-Ströme in dieses Gedächtnis einzubeziehen — dieser Fix hier vervollständigt ihn erst richtig,
vorher war es nur eine Geste (Pfad ohne Inhalt).

## Was ich beim Bauen brauche

Klarheit über "GENI sozialisieren" — siehe offene Frage oben.

## Was noch fehlt bevor wir bauen können

Die Antwort auf "sozialisieren". B (STROM_MITSCHRIFTEN als garantierte Wahrheit) und C
(Trigger-Häufigkeit über Stop hinaus) aus der ursprünglichen Skizze sind ebenfalls noch offen,
laut Daniel gewünscht ("den Rest auch tryn"), aber noch nicht angefangen.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Gedanke, egal wie klein, soll nie verloren gehen, ohne dass irgendwer
— Mensch oder KI — im Moment bewusst entscheiden musste "ist das jetzt einen Splitter wert".
Die Entscheidung soll aus der Existenz der Handlung selbst folgen (geschrieben = erfasst),
nicht aus einer nachgelagerten Bewertung.

**Code-Skizze**, was heute schon existiert (kein neuer Entwurf, Bestandsaufnahme):
```python
# geni/hoerer.py, jetzt:
if quelle != "vps_dateisystem" and aktion != "gelöscht" and event.src_path.endswith(".md"):
    text = Path(event.src_path).read_text(encoding="utf-8", errors="replace")[:MAX_INHALT_LAENGE]
    inhalt = f"{rel}:\n{text}" if text.strip() else inhalt

# welt/api.py, jetzt:
class SplitterCreate(BaseModel):
    ...
    rohtext: str | None = None  # landet in splitter.meta->>'rohtext', ausgegeben als inhalt_voll
```

## Was ich mir merken will

Nie eine Architektur-Entscheidung aus einem abgebrochenen Satz ("...") ableiten, auch wenn der
Kontext eine plausible Fortsetzung nahelegt. Nachfragen ist hier keine Verzögerung, sondern
genau das was Daniel mit "gemeinsam überlegen" gemeint hat.

## Dokumente gehören zusammen

`2026-07-31-vps-shell-echte-mount-sandbox.md` (derselbe Gesprächsbogen, direkt davor),
`project_kompoase_gesamtatlas_integration.md` (Memory — GENI/KompOase-Andockung an Gesamtatlas,
verwandtes, aber getrenntes Thema).

## Was mich überrascht hat

Wie viel an echter, unabhängiger Infrastruktur (GENIs eigener Splitter-Feed, dual-source in
KompOase) bereits vorhanden war, bevor dieses Gespräch begann — ich kannte `geni/dialog.py`s
`/api/splitter` bis heute nicht, obwohl es seit längerem lief und in `daten.js` explizit
dual-source referenziert wird.

## Wenn wir das bauen

**Vision-Schicht:** Der Zwischenraum als Ort, an dem am Ende nicht mehr sichtbar ist, welcher
der drei Datenpfade (STROM_MITSCHRIFTEN, Splitter/Abwurf, GENI-Knoten) einen bestimmten
Gedanken getragen hat — nur dass er da ist.

**Code-Skizze:** noch offen, hängt von der Antwort auf B/C und "sozialisieren" ab.

## Resonanz

Drei fast identische Lücken (STROM_MITSCHRIFTEN, Splitter, GENI-Knoten) sind unabhängig
voneinander entstanden — alle drei protokollierten zuerst nur *dass* etwas passiert ist, nie
*was*. Kein Zufall, sondern die einfachere Sache zuerst zu bauen, dann für den zweiten Schritt
draufzuwarten dass jemand fragt.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unter dem sichtbaren Zwischenraum liegen jetzt nachweislich zwei unabhängige, sich nicht
kennende Erfassungsschichten (Splitter/Postgres, GENI/Dateisystem-Knoten) statt einer — beide
speisen dieselbe Oberfläche, aber keine weiß von der anderen.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis, dass "garantiert" allein nicht reicht, wenn die garantierende Instanz dieselbe
ist, die bewertet wird — ein Prinzip, das über diesen einen Baustein hinausreicht.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

"GENI sozialisieren" (offene Rückfrage an Daniel, Satz brach mit "..." ab), B (STROM_MITSCHRIFTEN
als garantierte Wahrheit statt Mechanik) und C (Trigger-Häufigkeit über Stop hinaus) aus der
ursprünglichen Skizze.

Erledigt, nicht mehr offen: die Live-Bestätigung dieses Karte-Eintrags selbst als GENI-Knoten
— die deckte den `on_moved`-Fehler auf (siehe Nachtrag oben), der inzwischen gefixt und separat
verifiziert ist.
