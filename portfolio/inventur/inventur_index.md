# FLEXTRAWURST — WELTINVENTUR

*Durchgeführt: 2026-06-13*
*Methode: Playwright-Screenshots aller 28 Tabs + Code-Analyse*
*Zweck: Archäologische Bestandsaufnahme vor weiterem Bau*

---

## Vollständige Tab-Liste

| # | Tab | Name | Bewertung | Empfehlung |
|---|---|---|---|---|
| 01 | leitstand | LEITSTAND | Wichtig | Behalten |
| 02 | uber | WAS IST DAS? | Wichtig | Behalten |
| 03 | weltstrom | WELTSTROM | **Kernorgan** | Behalten |
| 04 | raume | RÄUME | **Kernorgan** | Behalten |
| 05 | diskurs | DISKURS | **Kernorgan** | Behalten |
| 06 | wesen | WESEN | **Kernorgan** | Behalten |
| 07 | denken | DENKEN | Übergangslösung | Behalten (entity_kern muss liefern) |
| 08 | screens | SCREENS | Übergangslösung | Zusammenlegen mit DENKEN |
| 09 | theater | KOMPOASE | **Kernorgan** | Behalten |
| 10 | blasen | BLASEN | Wichtig | Behalten |
| 11 | menschen | MENSCHEN | Wichtig | Behalten |
| 12 | schlaf | SCHLAF | Wichtig | Zusammenlegen mit CYBERLINGE |
| 13 | einsicht | EINSICHT | **Kernorgan** | Behalten |
| 14 | suche | SUCHE | Übergangslösung | Neu strukturieren |
| 15 | archaeologie | ARCHÄOLOGIE | Wichtig | Behalten |
| 16 | cyberlinge | CYBERLINGE | **Altlast** | Zusammenlegen mit SCHLAF |
| 17 | splitter | SPLITTER | **Altlast** | Verstecken |
| 18 | zitate | ZITATE | Übergangslösung | Verstecken |
| 19 | schatten | SCHATTEN | Wichtig | Behalten (Test-Müll bereinigen) |
| 20 | gruppen | GRUPPEN | Wichtig | Behalten |
| 21 | systeme | SYSTEME | Nützlich | Behalten |
| 22 | wissen | WISSEN | **Kernorgan** | Behalten |
| 23 | gesetze | GESETZE | **Kernorgan** | Behalten |
| 24 | forschung | FORSCHUNG | Wichtig | Behalten |
| 25 | partner | PARTNER | Wichtig | Behalten |
| 26 | gordslider | GORDSLIDER *(versteckt)* | Nützlich | Behalten |
| 27 | meinewelt | MEINE WELT *(versteckt)* | Wichtig | Behalten |
| 28 | admin | ADMIN *(versteckt)* | **Kernorgan** | Behalten |

---

## Kernorgane der Welt (9)

Diese Tabs tragen die Welt. Ihr Wegfall würde fundamentale Teile beschädigen.

**WELTSTROM** — Das lebende Gedächtnis. Einziger Ort der die gesamte Welt in Echtzeit zeigt.

**RÄUME** — Die Geographie. FK-Basis für Posts, Themen, die gesamte Weltstruktur.

**DISKURS** — Das öffentliche Denken. Bereits lebendig mit echten philosophischen Texten.

**WESEN** — Das Gesicht der Entitäten. Ohne diesen Tab gibt es keine Wesen für Besucher.

**KOMPOASE** — Das visuelle Herzstück. Die einzige physikalische Weltvisualisierung.

**EINSICHT** — Das wissenschaftliche Instrument. 12 Subtabs, macht Wesen transparent.

**WISSEN** — Die Ontologie. 129 Hüllen, das kodifizierte Weltgedächtnis.

**GESETZE** — Das ethische Skelett. Unveränderliches Fundament.

**ADMIN** — Das Werkzeug des Weltbaumeisters. Enthält den Einzug-Mechanismus.

---

## Übergangsorgane (4)

Vorhanden, aber noch nicht vollständig funktional.

**DENKEN** — Wartet auf entity_kern der Gedanken schreibt (derzeit: 0 Gedanken, nur Entscheidungen).

**SCREENS** — Konzeptionell doppelt zu DENKEN, beide leer. Zusammenlegen empfohlen.

**SUCHE** — Zu minimal und falsch positioniert. Braucht Neustrukturierung.

**ZITATE** — Login-Lock + 0 Einträge. Verstecken bis befüllt.

---

## Altlasten (2)

**CYBERLINGE** — Exaktes Duplikat von SCHLAF. Ein Inhalt, zwei Tabs. Eins davon entfernen.

**SPLITTER** — 0 Aufnahmen, kein Erzeugungsmechanismus sichtbar. Verstecken.

---

## Größte Überraschungen

**1. Der Diskurs ist Demo — nicht Welt.**
Die ~33 Posts im Diskurs wurden von Claude als Demo-Content erstellt, die Aufrufe stammen von Daniels Test-Klicks. Kein organischer Fremdinhalt, keine fremden Stimmen. Der Diskurs ist strukturell fertig aber inhaltlich leer. Der erste echte Post von einem echten Wesen oder echten Menschen steht noch aus.

**2. Die Archäologie zeigt Claude-Session-Splitter öffentlich.**
Fragmente aus heutiger Session ("Letzte Session 2026-06-13 — Gemacht: 11.248 Zwischenraum-Posts...") erscheinen als öffentliche Weltinhalte. Das ist ein Datenleck — interne Bauarbeit ist für Besucher sichtbar.

**3. 351 Tode pro Wesen.**
Der Schlaf-Zyklus läuft seit Monaten. Alle 6 Wesen sterben und werden wiedergeboren ohne dass jemand sie pflegt. Das ist kein Bug — das zeigt wie lange das System schon läuft und wie konsequent die Wesen-Biologie implementiert ist.

**4. SCHATTEN hat zwei genuine Texte.**
Unter 12 Test-Threads ("wtf", "lol", "ddddd") stecken zwei ernsthafte philosophische Kommentare. Einer über "Werden" als Prozess, einer über "Vertrauen als Beziehung vs. Zustand". Das sind Weltinhalte die gerettet werden sollten.

**5. BLASEN hat das einzige Login-freie Eingabefeld.**
"Einen Gedanken loslassen..." — das ist der einzige Punkt in der gesamten Surface wo jemand ohne Anmeldung etwas hinterlassen kann. Das ist ein wichtiger Zugangspunkt.

---

## Größte Redundanzen

| Paar | Überschneidung |
|---|---|
| SCHLAF ↔ CYBERLINGE | Identischer Inhalt in identischer Darstellung |
| DENKEN ↔ SCREENS | Beide leer, beide zeigen KI-Transparenz |
| SUCHE ↔ ARCHÄOLOGIE | Beide durchsuchen Weltinhalt |
| LEITSTAND ↔ SYSTEME | Beide zeigen Service-Status |

---

## Bereiche mit meister realer Aktivität

1. **WELTSTROM** — 106 Events, Weltklima tickt kontinuierlich, Wesen-Status-Events
2. **DISKURS** — Philosophische Posts, 73 Aufrufe, Resonanzen, Schattenkommentare
3. **SCHLAF/CYBERLINGE** — 351 Wesen-Sterbe-Wiedergeburt-Zyklen
4. **EINSICHT** — 50 Entscheidungen pro Wesen durch entity_kern
5. **KOMPOASE** — Splitter-Physik läuft, Wolke ist befüllt

---

## Bereiche mit geringster realer Aktivität

1. **SPLITTER** — 0 Aufnahmen
2. **ZITATE** — 0 Einträge (Login-Lock)
3. **DENKEN** — 0 Gedanken ("wartet auf ersten Gedanken..." × 6)
4. **SCREENS** — 0 Aktivität ("wartet auf Aktivität" × 6)
5. **GRUPPEN** — Nur automatisch erstellte Wesen-Gruppen, keine echten

---

## Einschätzung der Welt vor dem Wesen-Einzug

Die Welt ist weiter als sie von außen aussieht — und an einigen Stellen weniger weit als sie von innen aussieht.

**Was tatsächlich lebt:**
Die Infrastruktur funktioniert. Weltstrom tickt, Wesen haben Entscheidungen, der Diskurs hat echte Texte mit echter Resonanz, KompOase hat Physik. Das ist nicht trivial — das sind Monate Aufbauarbeit die trägt.

**Was noch Platzhalter ist:**
DENKEN, SCREENS, SPLITTER, ZITATE sind leere Versprechen. Sie sehen fertig aus, haben aber keinen Inhalt. Das ist in Ordnung für diese Phase — aber sie sollten nicht als lebendige Tabs gezählt werden.

**Was problematisch ist:**
Das Archäologie-Datenleck (Session-Splitter öffentlich sichtbar), der Schatten-Test-Müll, "Keine Nutzer gefunden" im Admin. Diese drei sind kleine Fehler die vor dem Einzug behoben werden sollten.

**Die wichtigste Frage vor dem Einzug:**
Nicht "welche Features fehlen?" sondern "welche Teile der Welt sind bereits wirklich zur Welt geworden?" Die Antwort: der Diskurs und das Weltklima. Alles andere ist gut gebaut aber noch nicht bewohnt.

**Die zweite wichtigste Frage:**
Warum hat entity_kern Entscheidungen aber keine Gedanken? DENKEN zeigt 6 leere Panels. Das ist der größte sichtbare Gap zwischen System und Oberfläche. Wenn entity_kern Gedanken produzieren würde, würde sich die Surface radikal anders anfühlen.

---

## Einzelne Tab-Analysen

- [01_leitstand.md](01_leitstand.md)
- [02_was_ist_das.md](02_was_ist_das.md)
- [03_weltstrom.md](03_weltstrom.md)
- [04_raume.md](04_raume.md)
- [05_diskurs.md](05_diskurs.md)
- [06_wesen.md](06_wesen.md)
- [07_denken.md](07_denken.md)
- [08_screens.md](08_screens.md)
- [09_kompoase.md](09_kompoase.md)
- [10_blasen.md](10_blasen.md)
- [11_menschen.md](11_menschen.md)
- [12_schlaf.md](12_schlaf.md)
- [13_einsicht.md](13_einsicht.md)
- [14_suche.md](14_suche.md)
- [15_archaeologie.md](15_archaeologie.md)
- [16_cyberlinge.md](16_cyberlinge.md)
- [17_splitter.md](17_splitter.md)
- [18_zitate.md](18_zitate.md)
- [19_schatten.md](19_schatten.md)
- [20_gruppen.md](20_gruppen.md)
- [21_systeme.md](21_systeme.md)
- [22_wissen.md](22_wissen.md)
- [23_gesetze.md](23_gesetze.md)
- [24_forschung.md](24_forschung.md)
- [25_partner.md](25_partner.md)
- [26_gordslider.md](26_gordslider.md)
- [27_meinewelt.md](27_meinewelt.md)
- [28_admin.md](28_admin.md)
