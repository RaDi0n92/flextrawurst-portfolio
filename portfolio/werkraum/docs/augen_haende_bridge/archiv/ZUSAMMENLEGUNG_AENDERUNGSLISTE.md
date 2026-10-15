---
autor: claude bei Daniels VPS
datum: 2026-09-20
zweck: Herkunft und Änderungsliste der zusammengelegten Bridge-Dokus, damit prüfbar ist, dass Bedeutung und Pflicht der Originale gleich geblieben sind
---

# Zusammenlegung der Bridge-Dokus — Herkunft und Änderungsliste

## Methode

Die neuen Dokus sind von Hand aus den Originalen geschrieben, ohne Bauskripte. Ausgangspunkt sind die Originale in `archiv/originale/` (Git-Stand `d32dc49d5b`, das Register in der Fassung von Codex `5b5728342d`), nicht irgendeine Zwischenfassung.

Jedes Original wurde gelesen, danach wurde in eigenen Worten aufgeschrieben, was dort dokumentiert ist. Bedeutung und Pflicht jeder Aussage bleiben gleich. Neu sind Ton, Ordnung, Verweise und die Absätze nach Daniels Regel (etwa 100 Zeichen). Nach jedem Dokument wurde das Original Abschnitt für Abschnitt gegen den neuen Text gehalten. Was dabei anders ist, steht unten.

Die einzige Ausnahme von der Handarbeit ist `ANFORDERUNGEN.md`: Dort sind die 112 Register-Zeilen von Codex Zelle für Zelle unverändert, weil sie schon Forderungen in knapper Form sind. Ihre Änderungen stehen einzeln mit Vorher und Nachher am Ende dieser Liste.

Die 21 Originale liegen unverändert in `archiv/originale/`. Das Register liegt dort in der Fassung von Codex, die vier Verweisdateien sind wieder Verweise. Zusätzlich sind sie in Git lesbar (`git show d32dc49d5b:docs/augen_haende_bridge/<Datei>`).

## Herkunft: welches Original in welchem neuen Dokument liegt

| Neues Dokument | Herkunft (Originale) | Stand |
| --- | --- | --- |
| `ANFORDERUNGEN.md` | `BRUECKE_ALLE_ANFORDERUNGEN_UND_ABNAHMEN.md` (Register); Baustartprüfung, Abschnitt »Was Daniel festgelegt hat«; Beschlüsse von Daniel vom 2026-09-20 | fertig |
| `PLAN.md` | `BRUECKE_VOM_ENDZIEL_RUECKWAERTS_ZUM_START.md`; Baustartprüfung, Abschnitt »Der nächste Bauabschnitt: erster echter Kontakt« und der Schlussabsatz des Abschnitts »Was vor dem jeweiligen Fertigmelden noch fehlt« | fertig |
| `BEFUNDE.md` | Baustartprüfung: »Ergebnis und Geltung«, »Nachgeprüfte Befunde«, »Was vor dem jeweiligen Fertigmelden noch fehlt« (Tabelle), »Zusammengehörige Quellen«, der Schlusssatz und der Satz zur Reichweite der Prüfung aus der Beweisstrategie; `POSTMORTEM_FALSCHER_BRUECKENKOERPER.md` | fertig |
| `TECHNIK.md` | Baustartprüfung: »Kleine technische Verträge, bevor daraus viel Code wird«; `V3_1_TERMINAL_CHANNEL.md`, `V3_2_VT_RUECKLESE.md`, `V3_3_PTY_RESIZE_RUECKLESE.md`, `V3_4_WINDOWS_FENSTERSCANNER_KERN.md` | fertig |
| `RECHERCHE.md` | `HINTERHOEFE_RECHERCHE_TERMINAL_SCANNER_OVERLAY.md`, `HINTERHOEFE_HAIJAGD_FENSTERSCANNER_AGENT_HARNESS.md`; Baustartprüfung: »Technische Recherche: Konsequenzen, keine Zauberrezepte« | fertig |
| `CHATGPT_UND_MCP.md` | `CHATGPT_ANTI_TERMINAL_VERTRAG.md`, `V3_AI_STROM_ANTI_TERMINAL_MCP_P0.md` | fertig |
| `NACHWEISE.md` | `PLAYWRIGHT_GUARDIAN_HARNESS_VERTRAG.md`; Baustartprüfung: »Beweisstrategie ohne Selbsttäuschung« | fertig |
| `KAPSELN_UND_HAUHAUCS.md` | `LUNA-MAX_PLANUNG_MOMENTKAPSELN_HAUHAUCS_OVERLAY.md` | fertig |
| `ERLEBEN.md` | keines der 21 Originale, sondern `docs/systemdoku/76_augen_und_haende_bridge.md` (Gemgem), `docs/vision/augen_und_haende_androidbridge_mlbb_dream.md` (Codex) und Daniels Skizze. Am 2026-09-20 auf Daniels Wunsch ergänzt | fertig |
| `2026-09-20_BRUECKE_BAUPROTOKOLL_FOKUS_UND_WIEDERAUFNAHME.md` | bleibt unverändert, der Skill schreibt hinein | — |
| `archiv/originale/` | alle 21 Originale unverändert, darunter `BRIDGE_SKILL_ORIGINAL_VOR_BAUSTARTPRUEFUNG.md`, die wortgetreue Sicherung des alten Skills. Sie ist nicht neu geschrieben und bleibt nur dort | — |
| `archiv/` | `CODEX_LETZTE_STUNDE_VOR_LIMIT_1ZU1.md` und die zwei Rohexporte (`…-messages.jsonl`, `…-astra-planung-messages.jsonl`), unverändert | — |

Die vier Dateien `…_WORTLAUT.md/.jsonl` waren Verweise (Links) auf die Rohexporte und enthielten selbst nichts. Alle Abschnitte der Baustartprüfung sind einem neuen Dokument zugeordnet.

Weggelassen wurde inhaltlich nichts. Zusammengefallen sind nur zwei Wiederholungen: In der Haijagd steht der Satz »Genau das brauchen unsere Fensterbindungen« zweimal, in `RECHERCHE.md` steht er einmal. Und die Baufolge V3.0 bis V3.7 und die Nummern der Bausteinberichte V3.1 bis V3.4 zählen in den Originalen teilweise verschieden. Beide Zählungen stehen unverändert da, und `TECHNIK.md` weist auf den Unterschied hin.

## Was gegenüber den Originalen anders ist

### PLAN.md

- Verweise: Der Pfad des Registers heißt jetzt `ANFORDERUNGEN.md`. Aus »Die 112 Anforderungen« wurde »Die 120 Anforderungen (R001–R120)«, im Auftrag von G18 aus »R001–R112« »R001–R120«. Die Baustartprüfung steht jetzt in `BEFUNDE.md`.
- Neu: der Abschnitt »Beschlüsse vom 2026-09-20, die diesen Plan ändern«, die Hinweise »Geändert durch BE01« in G01, G04 und G09, die Hinweise »Geändert durch BE03« in G02 (Auftrag, »Fertig, wenn« und der Satz zu den noch nicht gelieferten Fähigkeiten; der frühere Auftrag steht daneben), in G03, in der Kontaktstrecke und unter der Abhängigkeitstabelle, der Hinweis »Offen« in G03 (»laufend«), und die neuen Register-Zeilen in den Zeilen »Anforderungen«: R118 bei G02, R114 und R119 bei G05, R115 und R120 bei G06, R116 und R117 bei G06.5 (dort neue Zeile, R059 bleibt bei G09) und R113 bei G08.
- Neu eingefügt: der Abschnitt »Die erste Kontaktstrecke« aus der Baustartprüfung, mit den sechs Schritten, dem Absatz zum Terminaltransport und dem Schlussurteil »Für den nächsten Bauauftrag …«, das in der Baustartprüfung am Ende der Tabelle »Was vor dem jeweiligen Fertigmelden noch fehlt« stand.
- Form: Die »Fertig, wenn«-Punkte von G18, G17 und G06.5 stehen als Aufzählung. Der Satz »Die fett bezeichneten Aufträge sind jeweils als Goal-Text … gedacht« heißt jetzt »Jeder Abschnitt ist als Goal-Text … gedacht«. In der Tabelle der Abnahmen E01–E10 stehen in einigen Zellen »und« statt Schrägstrichen.

### BEFUNDE.md

- Die Baustartprüfung ist auf mehrere Dokus verteilt (siehe Tabelle). In `BEFUNDE.md` stehen ihr Ergebnis, die fünf Befunde, die Fehlt-Tabelle, die Quellen und der Satz zur Reichweite der Prüfung (»keine neue Windows-, Playwright- oder End-to-End-Abnahme«), der in der Baustartprüfung am Ende der Beweisstrategie stand.
- »Ergebnis und Geltung«: Aus »Daniels Wortlaut bleibt die Anforderungsquelle« wurde »Daniels Aussagen bleiben die Anforderungsquelle«. Der Satz, die Gesamt-Goalliste folge erst nach dieser Prüfung, ist auf den heutigen Stand gebracht: Die Liste steht in `PLAN.md`.
- »Zusammengehörige Quellen«: Die Pfade sind auf die neuen Dokus und das Archiv umgestellt. Die Skizze heißt heute `hand-auge-bridge-ref.jpg` und nicht mehr `h a bridge.jpg`, das ist vermerkt.
- Postmortem: Die Erzählform ist in Befundform gebracht (Urteil, Vorgaben, Ursache, Fremdprüfung, Lehre). Daniels zwei Zitate stehen als Aussage über den Stand (»Außer der Dokumentation wurde nichts hinbekommen«; »Autonomie war nicht die Ursache«). Der Ich-Satz von Codex »Der eigentliche Fehler war: Ich habe deine Vorgaben nicht als harte Quelle behandelt …« steht als »Der Kern: Daniels Vorgaben wurden nicht als harte Quelle behandelt …«. Die Bestätigung »Das stimmt.« vor dem Satz zur Autonomie ist entfallen, weil sie nur auf das Zitat antwortete. Die Bemerkung, auch die Dokumentation sei zu dicht gewesen, ist ausdrücklich als Einschränkung der Bilanz formuliert.
- Neu ist nur das Feld `betrifft` mit den Schlagworten beider Originale.

### TECHNIK.md

- Inhaltlich unverändert: zehn Verträge und vier Bausteinberichte. Der Terminalvertrag trägt den Hinweis »Geändert durch BE01«.
- Neu ist der Hinweis in der Einleitung, dass die Nummern V3.1 bis V3.4 hier und die Baufolge V3.0 bis V3.7 in `CHATGPT_UND_MCP.md` teilweise verschieden zählen.

### RECHERCHE.md

- Ton: Die Einleitung der Haijagd (»Ahhh, jetzt hab ich dich …«) und der Ausdruck »hinter die Bumsbirne« sind sachlich formuliert. Ich-Formen sind aufgelöst: »Mein korrigierter Befund« heißt »Korrektur gegenüber der letzten Skill-Erweiterung«, »Meine harte Empfehlung für den Bau« heißt »Empfohlene Reihenfolge des Baus«, »deinen bereits laufenden VPS-Terminals« heißt »den bereits laufenden VPS-Terminals«. »Der wichtigste Fund ist also« heißt »Daraus folgt«.
- Neu: Der Hinweis »Geändert durch BE01« bei der Lücke zu den laufenden Terminals.
- Die Konsequenzen aus den technischen Quellen (vier Punkte und der Schlussabsatz) stammen aus der Baustartprüfung und stehen als eigener Abschnitt am Ende.

### CHATGPT_UND_MCP.md

- Neu: die Ergänzung vom 2026-09-20 mit R116 und R117 im Abschnitt »Die fünf getrennten Körper«.
- Ton: »und den gesamten Jahrmarkt« heißt »und alles Übrige«.
- Ordnung: Der Abschnitt »Gemeinsame technische Anatomie« der V3-Ergänzung steht jetzt im Abschnitt »Nicht vier Anti-Terminals bauen«, weil beide dasselbe beschreiben.

### NACHWEISE.md

- Unverändert im Inhalt: Guardian-Vertrag und Beweisstrategie. Der Satz zur Reichweite der Baustartprüfung, der am Ende der Beweisstrategie stand, steht in `BEFUNDE.md`.

### KAPSELN_UND_HAUHAUCS.md

- Verweise: Die Pfade der Exportdateien zeigen auf `archiv/`. Aus »der Wortlaut-Export bleibt unverändert« wurde »der Gesprächsexport bleibt unverändert«. Der Hinweis, die Baufolge sei durch die Baustartprüfung korrigiert, verweist auf `BEFUNDE.md` und `PLAN.md`.
- Neu: der Hinweis »Geändert durch BE01« bei der Bindung an die bestehende Session.

### ERLEBEN.md

- Das Dokument gehört nicht zur Zusammenlegung der 21 Originale. Es beschreibt das Erleben der Bridge und stammt aus Gemgems Doku 76 und dem DREAM, das auch die Android-Bridge und Gord enthält, dazu aus Daniels Skizze. Ich habe beide Quellen vollständig gelesen.
- Aufgenommen ist, was man sieht und tut: Skizze, zwei Welten, Terminal, Rauten mit Banner und Ticker, Nervensägen-Modus, Regie, Kamera, Mikrofon, Sehen, Hände, Bilder und Texte mit Sichtbarkeit, WorldDOM, selbstentworfene Brücken und Freiheitsprofile, Zeit-Scrubber, Memory Seeds, ChatGPT, Android-Bridge, Gord, der Werkraum und das Schlussbild.
- Nicht übernommen, weil es Technik und nicht Erleben ist: die Windows-Linux-Tabelle (Verweis auf Doku 76, Abschnitt 7), das Sparsamkeits-Gesetz mit den RAM- und VRAM-Zahlen (steht in R045 und `BEFUNDE.md`, Befund 5), die Code-Skizzen der Datenklassen und der JSON-Beispiele, und die Anweisung vom 2026-09-18, erst vollständig zu dokumentieren. Tragbarkeit, alte Systeme und Open-Source-Traum (DREAM § 11 bis § 13) sind nur verwiesen, mit den Register-Zeilen R104–R110.
- Ton: Die Quellen sagen »HUD« und »Overlay«. Das ist nach R118 als kleine schwebende Teile gelesen, und das steht in der Einleitung. Die Zeitzusagen »unter 1 ms« und die Cursorleihe sind als Ziele und nicht als Messwerte gekennzeichnet, wie es `BEFUNDE.md` (Befund 5) verlangt. Die Skizze ist aus dem Bild beschrieben, das ich angesehen habe.
- Neu gegenüber den Quellen: die Hinweise auf spätere Beschlüsse (BE01 beim Terminal, R119 bei den Rauten, R113 bis R115 bei Objekten und Terminals, R103 bei Gord) und die Tabelle »Wo das im Register steht«.
- Abweichung zwischen zwei Dokus: Doku 76 nennt die Herkunft von WorldDOM-Knoten `real`, `inferred`, `authored`, `projected`, die Recherche von Codex nennt sie `native`, `ocr`, `vision`, `user_marked`, `agent_inferred`. Beide Schreibweisen stehen da, mit dem Hinweis, dass dasselbe Prinzip gemeint ist.

## Außerhalb der neuen Dokus

- `augen_haende_bridge/wiki/00_KARTE.md`: fünf Zeilen ergänzt (Befunde, Nachweise, Kapseln und Hauhaucs, Erleben, Originale im Archiv).
- Drei Dateien nennen weiterhin alte Dateinamen: `tests/evidence/B4_6_REFERENCE_SURFACE_EVIDENCE.md`, `BUILD_LOG.md` und `docs/systemdoku/78_augen_und_haende_bauplan.md`. Sie sind historische Belege und bleiben unverändert. Die genannten Originale liegen unter demselben Namen in `archiv/originale/`.
- Beide Skills sind nicht angefasst. Der Greenfield-Skill verweist auf `PLAN.md`, `ANFORDERUNGEN.md`, `TECHNIK.md` und `CHATGPT_UND_MCP.md`. Diese vier Dateien gibt es.
- Meine ersten Fassungen von `PLAN.md`, `TECHNIK.md`, `RECHERCHE.md`, `CHATGPT_UND_MCP.md` und `ANFORDERUNGEN.md` sind überschrieben. Sie liegen in Git in den Commits `155dd6a8e1` (`PLAN.md`), `d32dc49d5b` (`TECHNIK.md`, `RECHERCHE.md`, `CHATGPT_UND_MCP.md`) und `0598eb42ee` (`ANFORDERUNGEN.md`).

## Offene Punkte

- Es gibt keinen offenen Punkt zur Reihenfolge mehr: G02 liefert die exe mit dem kompletten ersten Körper (BE03), G03 folgt danach.
- BE04 (Harness und Skills 1:1, Playwright zuletzt) ist im Register eingetragen und im Plan beim Arbeitsvertrag vermerkt. Die Skills und die Harness sind dabei nicht angefasst.
- `START_HIER.md` und `README.md` nennen als Pflichtlektüre nur `PLAN.md`, `ANFORDERUNGEN.md`, `TECHNIK.md` und das Bauprotokoll. Ob `BEFUNDE.md` (mit der Lehre für die Wiederaufnahme) und `NACHWEISE.md` dazukommen sollen, entscheidet Daniel.

## ANFORDERUNGEN.md — Vorher und Nachher

Register-Zeilen R001–R112: alle 112 zellenweise unverändert gegen das Original geprüft. Neu sind die Spalte Stand, die Abschnitte »Was Daniel festgelegt hat« und »Beschlüsse von Daniel vom 2026-09-20« sowie die Zeilen R113–R120. Zusätzlich ist die Zeile SKIZZE in den Quellen auf den heutigen Dateinamen `hand-auge-bridge-ref.jpg` umgestellt.

### 1. Frontmatter

Grund: Provenienz: wer wann was bearbeitet hat (R010 verlangt Autoren)

Vorher:
> status: Planungsbaseline, keine Produktabnahme
> ---

Nachher:
> status: Planungsbaseline, keine Produktabnahme
> bearbeitet: 2026-09-20 durch claude bei Daniels VPS — Zusammenlegung mit dem Abschnitt »Was Daniel festgelegt hat« der Baustartprüfung, Spalte Stand, Beschlüsse und Ergänzungen von Daniel vom 2026-09-20, Ton einzelner Sätze; Bedeutung und Pflicht der Zeilen R001–R112 unverändert
> ---

### 2. Wozu, Satz 5

Grund: Verweis: das Original heißt nach der Zusammenlegung PLAN.md

Vorher: Die zusammengehörige Rückwärtsplanung steht unter `/root/werkraum/docs/augen_haende_bridge/BRUECKE_VOM_ENDZIEL_RUECKWAERTS_ZUM_START.md`.

Nachher: Die zusammengehörige Rückwärtsplanung steht in `/root/werkraum/docs/augen_haende_bridge/PLAN.md`.

### 3. Wozu, Absatz 2

Grund: Ton/Zeitbezug: »aktuell« war der Stand vom 19.09.; jetzt datiert

Vorher: `Das aktuelle Gespräch ergänzt:`

Nachher: `Ergänzung aus dem Gespräch vom 2026-09-19:`

### 4. Wozu, Absatz 3

Grund: Zusatz: erklärt die neue Spalte Stand (neu, keine Umformulierung)

Vorher: `historische Teilbeweise werden nicht automatisch übernommen.`

Nachher:
> historische Teilbeweise werden nicht automatisch übernommen. Die Spalte Stand führt die fünf Zustände aus »Vollständigkeit und Statuspflege«. Ein Verweis in dieser Spalte (BE…, R…) nennt einen späteren Beschluss von Daniel, der die Zeile ändert oder präzisiert; die Zeile selbst bleibt dabei unverändert.

### 5. Quellen U / A

Grund: Verweis: die Datei war ein Link auf diesen Export, der jetzt im Archiv liegt

Vorher: `/root/werkraum/docs/augen_haende_bridge/2026-09-18_19_CODEX_GESAMTSESSION_WORTLAUT.jsonl` — U bezeichnet

Nachher: `/root/werkraum/docs/augen_haende_bridge/archiv/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-messages.jsonl` — U bezeichnet

### 6. Quellen ASTRA

Grund: Verweis: Datei war ein Link auf diesen Export; Ordinalbereich der Datei genannt

Vorher: `/root/werkraum/docs/augen_haende_bridge/2026-09-19_ASTRA-LUNA_PLANUNG_WORTLAUT.md` — enger Planungsabschnitt, besonders 548–569

Nachher:
> `/root/werkraum/docs/augen_haende_bridge/archiv/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-astra-planung-messages.jsonl` — enger Planungsabschnitt (`ordinal` 548–587), besonders 548–569

### 7. Quellen LUNA

Grund: Verweis: neuer Dateiname nach der Zusammenlegung

Vorher: `/root/werkraum/docs/augen_haende_bridge/2026-09-19_LUNA-MAX_PLANUNG_MOMENTKAPSELN_HAUHAUCS_OVERLAY.md` — abgeleitete Planung

Nachher: `/root/werkraum/docs/augen_haende_bridge/KAPSELN_UND_HAUHAUCS.md` — abgeleitete Planung

### 8. Quellen PRÜFUNG

Grund: Verweis: die Baustartprüfung ist auf mehrere Dokumente verteilt

Vorher: `/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRUECKE_BAUSTART_PRUEFUNG_UND_VEREINBARUNG.md`

Nachher:
> `/root/werkraum/docs/augen_haende_bridge/BEFUNDE.md` (Baustartprüfung vom 2026-09-19; ihre technischen Verträge stehen in `TECHNIK.md`, die Beweisstrategie in `NACHWEISE.md`, die Kontaktstrecke in `PLAN.md`)

### 9. Quellen, neue Zeile

Grund: Zusatz: Kürzel für die Quelle der Beschlüsse vom 2026-09-20

Vorher: `| JETZT | Laufendes Gespräch nach dem archivierten Ausschnitt: vollständiger Umfang, Endziel zuerst, Bedienbarkeit als Abnahme |`

Nachher:
> | JETZT | Laufendes Gespräch nach dem archivierten Ausschnitt: vollständiger Umfang, Endziel zuerst, Bedienbarkeit als Abnahme |
> | D0920 | Gespräch von Daniel mit Claude Code in vd1 am 2026-09-20: Beschlüsse BE01 und BE02 und die Zeilen R113–R120; nachlesbar im Gesprächsprotokoll dieser Sitzung (in vd1 unter `/config/.claude/chat_log_2026-09.md`, Einträge vom 2026-09-20) |

### 10. Leseregel, letzter Satz

Grund: Zusatz: wendet die vorhandene Vorrangregel auf die neuen Beschlüsse an

Vorher: `der vorhandene Archivumfang bleibt unverändert.`

Nachher:
> der vorhandene Archivumfang bleibt unverändert. Die Beschlüsse von Daniel vom 2026-09-20 (unten) sind spätere ausdrückliche Korrekturen und gehen den Zeilen vor.

### 11. Überschrift 1

Grund: Ton: Umgangssprache (»Babysitten«); Bedeutung gleich

Vorher: `## 1. Programm, Lieferung und Arbeiten ohne Babysitten`

Nachher: `## 1. Programm, Lieferung und Arbeiten ohne ständige Betreuung`

### 12. Überschrift Konflikte

Grund: Ton: Redewendung; Bedeutung gleich (nichts wird verdeckt)

Vorher: `## Konflikte und fehlende Eindeutigkeit — nicht unter den Teppich`

Nachher: `## Konflikte und fehlende Eindeutigkeit — bleiben sichtbar`

### 13. Nicht vergessen, Absatz 1

Grund: Ton: Bildsprache; Bedeutung gleich

Vorher: `bleiben Arbeitsanforderungen (R008–R010), keine neue Funktionskathedrale.`

Nachher: `bleiben Arbeitsanforderungen (R008–R010), keine zusätzlichen Produktfunktionen.`

### 14. Vollständigkeit, letzter Satz

Grund: Ton: Umgangssprache (»entsorgt«); Bedeutung gleich

Vorher: `nicht einseitig als »später« entsorgt werden.`

Nachher: `nicht einseitig mit dem Etikett »später« aus dem Umfang genommen werden.`

### 15. Tabellenkopf aller zehn Abschnitte

Grund: Struktur: neue Spalte Stand; Kopfbeschriftung »Verbindliches Ergebnis« → »Forderung«, »Fertigbeleg« → »Nachweis«. Zellinhalt aller 112 Zeilen unverändert (zellenweise geprüft)

Vorher: `| ID | Verbindliches Ergebnis | Quelle | Goal | Fertigbeleg |`

Nachher: `| ID | Forderung | Stand | Quelle | Goal | Nachweis |`

### 16. Abschnitt »Was Daniel festgelegt hat«

Grund: Zusammenlegung: der Abschnitt gehört zu den Anforderungen; Inhalt unverändert

Vorher: `(Abschnitt der Baustartprüfung, 11 Festlegungen)`

Nachher: `(dieselben 11 Festlegungen; Überschrift um »(Stand 2026-09-19)« und einen Einleitungssatz ergänzt)`

### 17. Neue Abschnitte

Grund: Zusatz: Daniels Beschlüsse und neue Wünsche vom 2026-09-20, ohne Zeilen des Originals umzuformulieren

Vorher: `—`

Nachher: `»Beschlüsse von Daniel vom 2026-09-20« (BE01, BE02, Offene Punkte) und »11. Ergänzungen vom 2026-09-20« (R113–R120)`

### 18. Absätze im ganzen Dokument

Grund: Lesbarkeit nach Daniels Regel (~100 Zeichen je Absatz); geprüft: nach dem Zusammenziehen von Leerraum identischer Text

Vorher: `(lange Absätze in einer Zeile)`

Nachher: `(dieselben Sätze, an Satzgrenzen in Absätze von etwa 100 Zeichen geteilt)`

