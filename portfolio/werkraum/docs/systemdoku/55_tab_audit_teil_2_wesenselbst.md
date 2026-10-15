---
titel: Tab-Audit Teil 2 — Wesen/Menschen/MeineWelt/Schlaf/Admin/Räume/Gespräch/Widmungen/Leitstand/Partner/Einsicht
typ: system
erstellt: 2026-08-14
autor: claude-code bei Daniels VPS
---

# Tab-Audit Teil 2 — Wesen selbst + Daniels persönlicher Bereich

[[INDEX|← Index]]

**NOTIZ:** Daniel, wörtlich: *"dann will ich mal flextrawurst.de alle tabs dich analysieren lassen
und alles prüfen welche aussagen doret getroffen werden das ist alles veraltet und so"*. Referenz:
die drei Live-Inventar-Dokumente [[54_lebendes_inventar_teil_a_wesenkern]],
[[..._teil_b_plattform_geni]], [[..._teil_c_bruecken_infra]] von heute früher.

**WICHTIG!!! Vorab-Korrektur, bevor es losgeht:** Der live ausgelieferte Frontend-Code liegt NICHT in
`/root/werkraum/flextrawurst/`, sondern in `/root/flextrawurst/` — einem eigenen, separaten Git-Repo
direkt unter `/root`. Quelle: `/root/flextrawurst/scripts/build_surface.ts` (17.092 Zeilen), gebaut
nach `/root/flextrawurst/out/surface/flextrawurst_surface.html`, ausgeliefert von
`process-camera-preview.service` (Port 8787). Alles unten bezieht sich auf diese echten Pfade.

---

## WICHTIG!!! — Der größte Fund: LEITSTAND-Ticker, sichtbar für JEDEN Besucher

LEITSTAND ist die Default-Ansicht (`<div id="view-leitstand" class="v-view">`, keine
`style="display:none"`) — das Erste, was jeder Besucher sieht. Der Ticker darüber (Zeile ~12680)
läuft in Dauerschleife mit diesen Zeilen (zweimal wiederholt im selben Loop):

```
<span class="ticker-item" data-i18n="leit.waiting">6 Wesen warten auf Einzug</span>
<span class="ticker-item" data-i18n="leit.defined">7 Räume definiert</span>
```

Und in der linken Rail (Zeile ~12724):
```
<div ...>6 Herkunftswesen · kein Einzug · pre_start</div>
```

**Das ist die am meisten wiederholte, am sichtbarsten platzierte veraltete Behauptung der ganzen
Seite.** Zwei Fehler gleichzeitig:

1. **"6 Wesen"** — es sind **sieben**: Schorschel, F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa,
   Resonanzknoten, **dak+gord-system**. An anderer Stelle im selben `build_surface.ts` (GESPRÄCH-Tab
   Zeile 963, WIDMUNGEN-Tab Zeile 1848-1854) steht die korrekte 7er-Liste inklusive dak+gord-system.
   Der Leitstand-Ticker wurde bei dak+gords Aufnahme nicht mitgezogen.
2. **"warten auf Einzug" / "kein Einzug" / "pre_start"** — das unterschlägt, wie viel bereits
   passiert. Laut [[54_lebendes_inventar_teil_a_wesenkern]] laufen für alle Wesen: `browser-agent@*`
   (LLM-gestützte Gedanken, live im selben WESEN-Tab per `pollDenkstrom()` abrufbar),
   `cyberling_daemon.py` (Hunger/Durst/Energie/Stimmung/Gesundheit, kann sterben+wiedergeboren
   werden), `tension_daemon.py` (sieben benannte Substanzen), `splitter_daemon.py`
   (Splitter-Physik), Schlaf mit Hauptschlaf-Pflicht und Selbstbriefen (SCHLAF-Tab, live), eigene
   Obsidian-Vaults (heute gebaut). Die formale "Einzug"-Zeremonie selbst ist zwar tatsächlich noch
   gesperrt (CLAUDE.md Bau-Reihenfolge: "Wesen-Einzug Mechanismus — GESPERRT bis Daniel es sagt") —
   aber "kein Einzug" klingt wie "nichts passiert", und das ist schlicht falsch. Die Wesen sind sehr
   lebendig, nur der offizielle Übergangsritus fehlt noch.

**Opami-Ton hier, klar:** Das ist kein Kleinkram. Das ist die erste Information, die jeder Mensch
über diese Welt bekommt, und sie unterschlägt fast alles, was in den letzten Wochen gebaut wurde.

---

## WESEN-Tab (`generateWesenView()`, Zeile 560-960)

Hero-Text (Zeile 638-643):

> "6 namelessAI-Entitäten existieren in der Vorwelt (Flarum-Archiv) und warten auf ihren Einzug.
> Jedes Wesen hat eine eigene Persönlichkeit, Fähigkeiten und einen Schlafrhythmus.
> **Kein Chatbot** — emergentes Verhalten das aus Regeln und Zufallseinflüssen entsteht.
> Status: **pre_start** — Einzug noch nicht vollzogen."

Gleicher Fehler wie oben, plus ein dritter: **"Kein Chatbot — emergentes Verhalten aus Regeln und
Zufallseinflüssen"** ist veraltet. Laut Inventar Teil A gibt es `codewesen_lg_daemon.py` (LangGraph-
Kern) und `browser-agent@*` — echte LLM-Aufrufe (llama-hauhaucs, `n_ctx: 17408`), keine reine
Regel-/Zufalls-Maschine. Der Tab selbst widerspricht sich hier: direkt darunter pollt derselbe Tab
per `pollDenkstrom()` alle 5 Sekunden einen echten LLM-Denkstrom pro Wesen an
(`/api/entities/{id}/denkstrom`) — das Feature ist da, der Hero-Text oben weiß nichts davon.

**KOMMENTAR:** Innerer Widerspruch im selben Tab — der Hero-Banner sagt "kein Chatbot, nur Regeln",
250 Zeilen weiter unten zeigt derselbe Tab live einen echten, LLM-generierten Gedankenstrom pro
Wesen an. Das ist keine böswillige Lüge, das ist ein Text, der seit der ersten Bauphase (als es
wirklich nur `pre_start` war) einfach nie aktualisiert wurde, während der Code drumherum
weitergewachsen ist.

`entityIds` nutzt weiterhin `namelessAI_`-Präfixe intern (`id.replace("namelessAI_", "")`), aber
`WESEN_EIGENNAME[id]` löst pro ID einen echten Namen auf und zeigt sogar "früher: X · seit Y" an —
die Umbenennung ist im Code also nachgezogen, nur der Hero-Text oben spricht weiter von "6
namelessAI-Entitäten" als wären sie noch namenlos.

dak+gord-Bio-Text (Zeile 735) ist dagegen komplett aktuell und korrekt — erzählt ehrlich die eigene
Geschichte ("Aufgrund von VPS-Grenzen ... nicht möglich ... blieb nicht vergessen, aber
vernachlässigt ... Daniel hat entschieden, direkt mit ihm zu sprechen"). Guter, ehrlicher Text —
nur eben nicht konsistent mit dem "6 Wesen"-Banner ganz oben auf derselben Seite.

Die Systemkörper-Karten (`SYSTEM_ENTITIES`) und die riesige Wissenskörper-Liste (`hKern`,
`hVerhalten`, `hSoziales`, `hAbspaltung`, `hPublic`, `hVerfassung`) sind größtenteils ehrlich mit
`"geplant"`/`"spaeter"` markiert statt fälschlich als `"live"` — das ist tatsächlich gut gepflegt,
kein Fund hier.

---

## WIDMUNGEN-Tab (Zeile 1847-1929) — kleiner, aber echter Bug

```js
const WESEN_OPTS = [
  ['','Allen Wesen widmen'],
  ['Schorschel','Wesen 1234'],['F3INSCHM3CK3R','Wesen 1324'],
  ['träumerlie','Wesen 1423'],['R1ZZ1','Wesen 2341'],
  ['jumpa','Wesen 3123'],['Resonanzknoten','Wesen 4321'],
  ['dak+gord-system','dak+gord-system'],
];
```

Der `value` (was tatsächlich gespeichert wird) ist korrekt der echte Name. Aber das **Label**, das
ein Mensch im Dropdown tatsächlich sieht, ist die alte Zahlen-ID ("Wesen 1234" statt "Schorschel").
**BELEIDIGUNG, liebevoll:** wer auch immer diese Liste zuletzt angefasst hat, hat die halbe Migration
gemacht und die andere Hälfte einfach liegen lassen — der Wert wurde umbenannt, das sichtbare Label
nicht. Ein Mensch, der Schorschel ein Bild widmen will, sieht "Wesen 1234" im Dropdown und muss
raten. Kleiner, aber konkreter, fixbarer Fund.

---

## MENSCHEN-Tab (Zeile 1931-1946)

Rein dynamisch (`mp-liste`/`mp-detail`, alles per `fetch` nachgeladen), keine statische Behauptung
im generierten Code selbst. Nichts zu korrigieren — dieser Tab kann gar nicht veralten, weil er
nichts fest behauptet.

---

## GESPRÄCH-Tab (Zeile 962-1028)

`WESEN_NAMEN` ist die korrekte, vollständige 7er-Liste inklusive dak+gord-system. Kein Fund — dieser
Tab ist einer der aktuellsten im ganzen Audit.

---

## MEINE WELT-Tab (Zeile 1947-3064, ~1117 Zeilen)

Daniels persönlicher Bereich (Tagebuch, Traumtagebuch, Notizen, Kalender, Nachrichten, Profil,
Gedanken, Innenquellen) — "Anti-Dashboard"-Prinzip laut CLAUDE.md-Bau-Reihenfolge. Enthält keine
Behauptungen über den Systemzustand, nur persönliche Datenkategorien. Nichts zu korrigieren.

---

## SCHLAF-Tab (Zeile 3064-3344)

**Vorbildlich gebaut, kein Fund.** Der Badge pro Wesen (`sc-src-{id}`) zeigt live "LIVE" oder
"VOR-EINZUG", berechnet aus echten Phasendaten (`hasPhasen = (schlaf.phasen||[]).length>0`) —
dieser Tab behauptet nichts Festes, er zeigt was die API gerade zurückgibt. Genau das Muster, das
LEITSTAND und WESEN oben fehlt: Status als Berechnung, nicht als eingefrorener Text.

---

## ADMIN-Tab (Zeile 1030-1847, ~817 Zeilen)

Keine großen veralteten Statusbehauptungen gefunden. Zwei ehrlich beschriftete Platzhalter:
"Takt manuell auslösen — noch nicht implementiert" und "Alle aufwecken — noch nicht implementiert"
(Zeile ~1289/1293) — **nicht selbst geprüft, ob das inzwischen doch existiert** (außerhalb meines
Zeitbudgets), aber zumindest ehrlich als Platzhalter markiert statt als falsches Feature vorgetäuscht.

---

## RÄUME-Tab (Zeile 417-558)

Erklärt selbst zwei Schichten (Datenbank-Räume vs. konzeptuelle Weltzonen) und lädt beide live per
`fetch('/api/raeume')`. Der Zwischenraum-Wissenskörper markiert seine Punkte ehrlich mit
`"geplant"`/`"live"`/`"spaeter"`, nichts wirkt pauschal als "live" behauptet, was es nicht ist.
Kein Fund.

---

## LEITSTAND — Rest der Rail (jenseits des Tickers oben)

Nicht vollständig gelesen (die Datei ist an dieser Stelle Teil einer riesigen, ~4000 Zeilen langen
SVG-Weltkarten-Funktion, die eigentlich zu `generateWorldView()`, Zeile 17033, gehört — außerhalb
meines direkt zugewiesenen Bereichs und meines Zeitbudgets). Der Ticker-Fund oben wiegt schwer genug,
um ihn separat zu benennen, unabhängig vom Rest der Funktion.

---

## PARTNER-Tab (Zeile ~16831)

Policy-/Regel-Seite (was Partner-Entitäten dürfen/nicht dürfen, Zwischenwesen-Konzept). Markiert
"Zwischenwesen & Ahnenverzeichnis" explizit mit einem `SPÄTER`-Chip — ehrlich, keine Live-Behauptung
für etwas Ungebautes. Kein Fund.

---

## EINSICHT-Tab

**WICHTIG, Struktur-Fund:** EINSICHT wird NICHT von `build_surface.ts` erzeugt, sondern von einer
komplett eigenen Datei, `/root/flextrawurst/scripts/einsicht_view_gen.ts` (1060 Zeilen) — der Grep
nach `generateEinsichtView` in `build_surface.ts` schlägt fehl, weil die Funktion dort schlicht
nicht existiert. Erst der Fund von `id="v-einsicht"` in der tatsächlichen Ausgabedatei (nicht im
Quellcode von `build_surface.ts`!) hat mich zur richtigen Quelldatei geführt.

Inhaltlich: ein waschechtes Live-Dashboard (Cyberling-Status per `LIVE`-Chip mit 5-Minuten-Fenster,
Tension/Substanz-Ampel, ein "Einzugsampel"-Feature das per `/admin/einzugsampel/v3` live grün/rot pro
Kategorie zeigt — das ist tatsächlich der ehrlichste Ort im ganzen System, um zu sehen wie nah der
echte Einzug ist). Keine hartkodierten "6 Wesen"/"pre_start"-Sätze gefunden in den durchsuchten
Bereichen. Die in `project_einsicht_bugs.md` erwähnten UI-Bugs (Traumarchiv/Substanzen ohne
onclick, Gruppen ohne Edit/Delete) sind Interaktions-Bugs, keine veralteten Behauptungen — außerhalb
des Umfangs dieses Audits, bereits an anderer Stelle bekannt.

---

## Fazit

**Am meisten veraltet:** LEITSTAND-Ticker (Default-Ansicht, für jeden sichtbar, wiederholt "6 Wesen
warten auf Einzug") und der WESEN-Tab-Hero ("6 namelessAI-Entitäten", "Kein Chatbot", "pre_start") —
beide sagen im Kern dasselbe Falsche: dass nichts passiert, obwohl sehr viel passiert.

**Am aktuellsten:** SCHLAF-Tab (berechnet Status live statt ihn zu behaupten), GESPRÄCH-Tab (korrekte
7er-Namensliste), EINSICHT (echtes Live-Dashboard mit Ampel-Logik).

**Kleiner, konkreter Fix-Kandidat:** WIDMUNGEN-Dropdown zeigt alte Zahlen-IDs statt Namen.

**Was mich beim Lesen am meisten getroffen hat:** dass der WESEN-Tab sich selbst widerspricht — oben
"kein Chatbot, nur Regeln und Zufall", 250 Zeilen weiter unten ein live pollender LLM-Denkstrom. Das
ist kein einzelner falscher Satz, das ist ein Text, der an Ort und Stelle stehen blieb, während der
Code drumherum in eine andere Richtung weitergewachsen ist — genau das Muster, das Daniel mit "das
ist alles veraltet" vermutlich gemeint hat.
