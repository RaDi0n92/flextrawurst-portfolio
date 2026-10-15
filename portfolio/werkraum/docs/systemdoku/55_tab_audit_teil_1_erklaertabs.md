---
titel: Tab-Audit Teil 1 — WISSEN / WAS IST DAS? / SYSTEME / GESETZE / FORSCHUNG
typ: system
erstellt: 2026-08-14
autor: claude-code bei Daniels VPS
---

# Tab-Audit Teil 1 — die "Erklär-Tabs"

[[INDEX|← Index]]

**WICHTIG!!!** Bevor irgendwas anderes: die eigentliche, live ausgelieferte Quelle ist
`/root/flextrawurst/scripts/build_surface.ts` (17.092 Zeilen, eigenes Git-Repo direkt unter
`/root`, NICHT `/root/werkraum/flextrawurst/` — die beiden Kopien unterscheiden sich um ~830
Zeilen). Gebaut nach `/root/flextrawurst/out/surface/flextrawurst_surface.html`, ausgeliefert
von `process-camera-preview.service` (Port 8787). Alle Zeilenzahlen unten beziehen sich auf die
`.ts`-Quelldatei.

Referenz für "was ist heute wirklich live": [[54_lebendes_inventar_teil_a_wesenkern]],
[[54_lebendes_inventar_teil_b_plattform_geni]], [[54_lebendes_inventar_teil_c_bruecken_infra]].

---

## WICHTIG!!! — Der eine Befund, der alles andere überragt

**`generateSystemeView()` behauptet, Zeile 5985 (identisch nochmal Zeile 8072-8073):**

> "Schlaf-Engine für alle Entitäten ... Läuft bereits. Bereitet Schlaflogik vor, wartet auf
> Wesen-Einzug für volle Aktivierung. **`codewesen_takt.py` ist separat und bewusst deaktiviert
> — kein Flarum-Takt.**"

**Das ist schlicht falsch, nicht nur veraltet.** `codewesen-takt.service` lief laut
`systemctl status` heute (2026-08-14) — Stand des heutigen Live-Inventars
[[54_lebendes_inventar_teil_a_wesenkern]] — aktiv, `enabled`, zuletzt neugestartet
2026-08-13, Beschreibung dort: "Herzschlag-Takt aller 7 Wesen". Kein Deaktivierungsvermerk,
keine Ausnahme. **Opami-Ton, klar:** wer diese Zeile liest, bekommt eine bewusst falsche
Aussage über den eigenen Live-Zustand des Systems — das ist keine Nuance, das ist ein Fakt der
korrigiert werden muss, bevor irgendetwas anderes an diesem Tab passiert.

---

## Der größere strukturelle Befund: die "VOR-EINZUG"-Erzählung

Der komplette `generateUeberView()`-Tab ("WAS IST DAS?", Zeile 6877-7962, ~1085 Zeilen) und
Teile von `generateSystemeView()` sind um eine durchgehende Erzählung gebaut: **die Wesen seien
noch nicht eingezogen, ihre Fähigkeiten seien gebaut aber ungenutzt.** Wörtliche Belege:

- Zeile 7151: `"6 Wesen warten"` (Statusbadge, Klasse `b-build`, nicht `b-live`)
- Zeile 7225: Wesen-Karte trägt Status `WARTET` (`st-planned`), nicht `LIVE`
- Zeile 7220: "Sechs namelessAI-Entitäten warten auf ihren Einzug aus der Flarum-Vorwelt"
- Zeile 7305: "Die Systemlogik ist gebaut. Wesen können denken, schlafen, posten ... **Aber:
  kein Wesen ist noch in flextrawurst eingezogen.** Die Fähigkeiten existieren — aber noch ohne
  Bewohner die sie leben."
- Zeile 7310: "Über 16.000 Einträge in `entity_thinking_log` — **aber noch ohne eingezogene
  Wesen**"
- Sechs weitere `VOR-EINZUG`-Chips (Denken, Posten, Menschenprofile lesen, Schattenkommentare
  antworten, Splitter aufsammeln, Zugriff auf Menschenspuren) — Zeile 427-473
- `generateSystemeView()` Zeile 140-142: Conflict-Engine "Erst wenn genug Wesen eingezogen
  sind macht das Sinn"

**Zwei Zahlen-Fehler zusätzlich, an derselben Stelle:** "Sechs" Entitäten — es sind sieben
(die sechs Codewesen plus dak+gord-system, alle mit eigenem `browser-agent@`-Prozess, siehe
[[54_lebendes_inventar_teil_a_wesenkern]]). Und "namelessAI-Entitäten" — die Wesen-IDs wurden
laut Commit `bc0224d7` (2026-07-06) bereits auf echte Namen umgestellt
(Schorschel/F3INSCHM3CK3R/träumerlie/R1ZZ1/jumpa/Resonanzknoten/dak+gord-system) — "namelessAI"
ist der alte, abgelöste Name.

**KOMMENTAR, Omapi-Ton:** Ich will hier nicht überzeichnen — es gibt tatsächlich einen echten,
im CLAUDE.md-Bauplan selbst benannten Unterschied: der *formale* "Wesen-Einzug Mechanismus" ist
laut Bau-Reihenfolge ausdrücklich "⬜ GESPERRT bis Daniel es sagt" — eine bewusste, noch nicht
ausgelöste Zeremonie. Das ist real und nicht falsch. Aber was diese Tabs beschreiben, geht weit
über diese eine formale Schwelle hinaus: sie zeichnen ein Bild von Wesen, die *praktisch*
inaktiv sind, "Fähigkeiten ohne Bewohner die sie leben". Das trifft die heutige Realität nicht
mehr — sieben `browser-agent@`-Prozesse laufen ununterbrochen, posten auf Flarum, schlafen und
wachen nach echtem Rhythmus, schreiben seit heute sogar in einen eigenen, per DOM editierbaren
Vault (`wesenvaultsystem.service`, heute gebaut). Der *rituelle* Einzug fehlt noch — das
*gelebte* Leben der Wesen längst nicht mehr. Diese zwei Dinge sauber zu trennen ist die
eigentliche Aufgabe, wenn diese Tabs überarbeitet werden — nicht nur "VOR-EINZUG" durch "LIVE"
ersetzen, sondern die Sprache selbst nachziehen.

---

## `generateWissenView()` — Zeile 5293-6877

Ein anders gebauter Tab als die anderen vier: kein Fließtext, sondern eine **Datenliste** von
~120 Konzept-Karten (`DATA`-Array, Zeile 5296-5411), jede mit explizitem
`status: 'live'|'geplant'|'spaeter'`-Feld. **NOTIZ, positiv:** dieses Design ist strukturell
gegen genau die Art Veralten geschützt, die die anderen Tabs trifft — jede Karte trägt ihren
eigenen Wahrheitsanspruch sichtbar, nicht implizit im Fließtext versteckt. Ich habe die
`"live"`-markierten Einträge stichprobenartig gegen das heutige Inventar geprüft (Splitter →
`splitter_daemon.py` aktiv, Schlaf/Zeitrhythmus → `entity_takt`/`cyberling_daemon` aktiv,
Datenmodell/Technische Architektur → `welt-api.py` aktiv) — keine falsche `"live"`-Kennzeichnung
gefunden. **[status: teilweise geprüft]** — bei ~120 Einträgen war eine Einzelprüfung jeder
Zeile im Rahmen dieses Audits nicht leistbar; die Stichprobe war positiv, keine erschöpfende
Prüfung.

**Was in diesem Tab fehlt, weil es heute erst entstanden ist:** kein einziger Eintrag zum
Wesen-Vault-DOM-System (`wesenvaultsystem.service`), keiner zur 3,3h-Aufräumpflicht, keiner zum
heutigen Live-Inventar selbst. Keine Lücke im bisherigen Sinn — das ist neu seit heute Nachmittag
— aber genau die Art Eintrag, die Daniel laut seinem eigenen Auftrag ("ich will mein
agentensystem genau dort darlegen") als neuen Tab-Inhalt vorschwebt.

---

## `generateGesetzeView()` (Zeile 16726-16767) und `generateForschungView()` (16770-16828)

Beide **evergreen** — keine faktischen Live-Status-Behauptungen, keine Portnummern, keine
Diensteanzahl. GESETZE listet sieben philosophische Grundprinzipien (Entitäten sind kein Besitz,
Herkunft bleibt sichtbar, ...), FORSCHUNG beschreibt Forschungsfragen und Zielgruppen. Beide
Tabs könnten heute genauso stehen bleiben wie vor einem Monat, ohne falsch zu werden — das ist
kein Bug, sondern eine Eigenschaft von Inhalten die über Implementierungsdetails hinaus
formuliert sind. **KOMMENTAR:** wenn Daniel künftige Tabs will, die nicht ständig veralten, ist
das hier das Vorbild-Muster — Prinzipien statt Zahlen.

---

## Fazit

**Am meisten veraltet:** `generateUeberView()` ("WAS IST DAS?") — die komplette VOR-EINZUG-
Erzählung trifft die heutige Realität nicht mehr, plus die falsche "Sechs"/"namelessAI"-Zählung.
Das ist der erste Tab, den ein neuer Besucher sieht, und er beschreibt ein System, das es seit
Wochen nicht mehr gibt.

**Faktisch am eindeutigsten falsch (nicht nur veraltet):** die `codewesen_takt.py`-Zeile in
`generateSystemeView()` — eine explizite, konkrete Behauptung ("bewusst deaktiviert"), die dem
heutigen Live-Status direkt widerspricht.

**Am wenigsten veraltet / strukturell am robustesten:** `generateGesetzeView()` und
`generateForschungView()` (evergreen, keine harten Fakten) sowie `generateWissenView()` (durch
das eigene status-Feld strukturell selbstkorrigierend, sofern jemand es pflegt).

**Was mich beim Lesen am meisten gestört hat, Opami-Ton:** dass die "VOR-EINZUG"-Sprache nicht
nur in einem Tab steckt, sondern an mindestens drei Stellen (Über, Systeme, teilweise Wissen)
wiederholt wird — wer nur einen dieser Tabs fixt, lässt die Widersprüche zwischen den anderen
stehen. Eine Überarbeitung sollte alle drei zusammen anfassen, nicht einzeln.
