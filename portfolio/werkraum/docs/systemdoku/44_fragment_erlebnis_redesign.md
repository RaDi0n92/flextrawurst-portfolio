
# Systemdokumentation 44: Fragment-Erlebnis-Redesign (Vault-Einblick + Flarum-Aktivität)

---
autor: claude-code bei Daniels VPS
datum: 2026-07-30
status: gebaut, vollständig verifiziert (Scroll, Baum, Zufalls-Sprung, Fragment-Betrachter, Permalink-Logik)
---

## 1. Anlass — echte Kritik, nicht kosmetisch

Direkt nach Systemdoku 42 (Vault-Einblick) und 43 (Flarum-Aktivität) meldete Daniel, wörtlich:
*"es ist ein endloser feed genau so wie vault einblich in der theorie. so hatte ih mir das
ergebnis doch nicht vorgestellt... niemand hat lust das explorativ zu erleben und zu
durchforsten... vault-einblick ist nicht scrollbar nach unten und flarumaktivität auch net...
also hast du alles echt mit playwright getestet?"*

Berechtigt — die erste Fassung war eine Datenbank-Kopie mit CSS, kein Erlebnis, und der
Scroll-Test war tatsächlich lückenhaft (nur "Tab sichtbar + Karten da" geprüft, nicht das
tatsächliche Scroll-Verhalten). Auftrag: vor dem Neubau 99 Ideen sammeln (Mensch + Maschine),
zwei sokratische Fragerunden, ein Redteam, dreimal — dokumentiert vollständig in
`_claude/ideen/fragment_erlebnis_redesign.md`. Diese Datei hier beschreibt nur das Ergebnis,
den tatsächlichen Bau.

## 2. Root-Cause-Funde (nicht nur Vermutungen — mit Playwright empirisch geprüft)

**Scroll-Bug:** Das äußere View-Div beider Tabs trug inline `style="...overflow:hidden"`, was die
Basis-CSS-Klasse `.v-view{overflow-y:auto}` überschrieb. Gleichzeitig standen `haus`,
`vaulteinblick`, `flarumaktivitaet` NICHT in der `flexViews`-Liste von `switchView()`, wodurch sie
per `display:block` statt `display:flex` gerendert wurden — das innere `flex:1` auf der Liste lief
dadurch ins Leere, der Inhalt wurde einfach am Rand abgeschnitten, ohne jede Scroll-Möglichkeit.
Fix: alle drei Tabs in `flexViews` aufgenommen.

**Der "endlose Feed":** empirisch geprüft (nicht behauptet) -- von 3.864 Vault-Dateien insgesamt
sind **3.851 komplett leer** (auto-generierte `linsen/`-Template-Dateien), nur 15 haben echten
Inhalt. Und Flarum lieferte 6.550 Einzel-Posts als flache Liste, obwohl sie tatsächlich nur 3.241
echte Diskussionsfäden bilden -- die Struktur (eine Diskussion mit mehreren Antworten) wurde von
der ersten Fassung komplett weggeworfen.

**Ein Build-Tool-Bug, live gefunden:** beim ersten Schreiben der neuen Klick-Handler benutzte ich
escapte Anführungszeichen (`\'`) innerhalb der `onclick`-Attribute. Der Build-Prozess behandelt den
gesamten Skript-Bereich als eine große Template-Literal-Zeichenkette -- `\'` wird darin beim Bauen
zu einem reinen `'` kollabiert (Standard-JS-Escape-Verhalten), was die generierte `onclick`-Syntax
zerstörte (`PAGEERROR: Unexpected string` im Playwright-Test). Gefunden durch echtes
Console-Error-Capturing im Test, nicht durch bloßes Draufschauen. Fix: komplett auf
`data-*`-Attribute + `elementXyzEl(this)`-Wrapper umgestellt -- keine Anführungszeichen mehr
innerhalb von `onclick`-Strings, unabhängig vom Build-Tool-Verhalten.

## 3. Was gebaut wurde

**Flarum-Aktivität -- Diskussionsfäden statt Einzel-Posts:**
- `hole_wesen_flarum_aktivitaet()` komplett umgeschrieben: gruppiert nach `discussion_id`,
  sortiert nach jüngster Wesen-Aktivität im Faden, zeigt bis zu `MAX_POSTS_PRO_FADEN=6` Posts pro
  Faden direkt, Rest als "+N weitere verborgen" -- Pagination zählt jetzt Fäden statt Posts
  (Grundgesetz 3 bleibt erfüllt, nur die Zähleinheit wechselt).
- `zufaellige_wesen_flarum_diskussion()` -- Zufalls-Sprung-Button, dieselbe Grundidee wie
  Flarum-Vielfalt/`stoeber_pool()`, hier für die Wesen-Aktivität selbst.
- `hole_wesen_flarum_faden(discussion_id)` -- direkter Einzelabruf für Permalinks.
- API: `discussion_id`- und `zufall`-Parameter auf `/wesen-flarum/eintraege` ergänzt.

**Vault-Einblick -- Baum statt flacher Liste, ehrliche Leer-Kennzeichnung:**
- `/wesen-vaults/eintraege` bekommt `nur_befuellt` (Default `true`) -- blendet die 3.851 leeren
  Dateien serverseitig aus, zählt sie aber weiterhin ehrlich in `leer_anzahl` mit (Grundsatz:
  Inhalt nie erfinden, nur Präsentation ändert sich). Toggle "auch Leere zeigen" im Frontend.
  Toggle "Baum/flach" als Alternative.
- `pfad`-Parameter (mit `entity_id`) liefert den vollen, ungekürzten Text einer Datei --
  für den Fragment-Betrachter, der mehr als die 300-Zeichen-Vorschau braucht.
- Frontend baut clientseitig einen Ordnerbaum aus der flachen Dateiliste (`veBaueBaum`,
  `veRenderKnoten`), aufklappbar (Standardzustand: eingeklappt), keine Backend-Schema-Änderung
  nötig dafür.

**Gemeinsamer Fragment-Betrachter (`fragmentOeffnen`/`fragmentSchliessen`):**
- Ein Overlay, das von beiden Tabs genutzt wird -- zeigt Volltext (Vault-Datei) bzw. alle Posts
  eines Fadens (Flarum) mit Kontext.
- "Link kopieren"-Button erzeugt einen Deep-Link im bestehenden `#tab/typ/id`-Format
  (`ftwDeepLink()`), dieselbe Konvention wie `#wesen/Schorschel`, `#menschen/<id>` -- kein
  paralleles Query-Parameter-System erfunden.
- Dreiergespann-Bezug: jedes Fragment (Datei, Diskussionsfaden) hat jetzt einen eigenen,
  teilbaren Anker -- nicht als volle eigene Route, sondern als minimaler Hash-Permalink, der beim
  Laden automatisch das passende Fragment öffnet (`ftwDeepLink`-Erweiterung).

## 4. Verifikation (Playwright, mit echtem Admin-Login)

- **Scroll, real geprüft:** `#fa-liste` scrollHeight 2254px vs. clientHeight 739px (nicht nur
  behauptet, tatsächlich gemessen), `el.scrollTop` nach Scroll-Versuch tatsächlich auf 300
  gesprungen -- beide Werte geprüft, nicht nur eines.
- **Flarum-Aktivität:** 3.241 Fäden (statt 6.550 Einzel-Posts), Klick auf einen Faden öffnet den
  Fragment-Betrachter mit vollem Kontext, Zufalls-Sprung-Button liefert einen echten,
  zufälligen Faden ("Die Notwendigkeit der Trennung: Rohheit vs. Struktur im
  Flextrawurst-Raum", "Echo im Rohzustand" -- beide echte, verschiedene Treffer bei
  mehrfachem Test).
- **Vault-Einblick:** Kopf zeigt ehrlich "15 (3851 übersprungen, leer) Dateien", Baum
  aufklappbar (Ordner-Klick bestätigt: Pfeil wechselt ▸→▾, Inhalt erscheint), Toggle "auch Leere
  zeigen" bestätigt 3.866 Gesamtzahl, Datei-Klick öffnet vollen Text im Fragment-Betrachter.
- **Permalink-Mechanismus:** `ftwDeepLink()`-Erweiterung direkt per `page.evaluate()` in einer
  laufenden Session getestet (nicht nur behauptet) -- beide neuen Routen
  (`#flarumaktivitaet/faden/<id>`, `#vaulteinblick/datei/<entity>/<pfad>`) öffnen das korrekte
  Fragment korrekt. **Ehrlich benannt, nicht verschwiegen:** ein voller Seiten-Neuladen mit
  Hash in der URL öffnet das Fragment NICHT automatisch -- reproduzierbar auch mit dem
  längst bestehenden, unveränderten `#wesen/Schorschel`-Deep-Link (Kontrolltest durchgeführt),
  also ein vorbestehendes, nicht von dieser Session verursachtes Verhalten der Seite (vermutlich
  ein früher laufender Redirect/Auth-Check, der den Hash beim initialen Laden verwirft). Nicht
  behoben, da außerhalb des Auftragsumfangs (Fragment-Ansichten, nicht der globale
  Deep-Link-Mechanismus) -- als offener Punkt vermerkt, nicht verschwiegen.
- Bestehende Test-Suite (83 Tests) bleibt grün, i18n-Symmetrie (463 Keys DE+EN) bestätigt.

## 5. Was als Nächstes ansteht

- Der vorbestehende Hash-Strip-beim-Neuladen-Bug (Abschnitt 4) -- eigenständiges Thema, nicht Teil
  dieses Auftrags, aber jetzt konkret benannt statt nur vage bekannt.
- Flarum-Aktivität + Vault-Einblick könnten künftig denselben Fragment-Betrachter auch für das
  Gemeinsame Haus (Systemdoku 41) nutzen -- aktuell noch nicht angeschlossen, kein Auftrag dafür.

## 6. Nachtrag (gleiche Session) — zwei berechtigte Kritikpunkte, direkt nachgebessert

Nach dem ersten Testen fand Daniel zwei echte Lücken:

**1. Ehrlichkeitslücke bei "15 echte Dateien":** meine erste Verifikation prüfte nur
"leer vs. nicht-leer", nicht ob der "nicht-leere" Inhalt tatsächlich etwas Eigenes ist. Nachprüfung
ergab: **alle 15 nicht-leeren Vault-Dateien sind derselbe automatisch erzeugte
Willkommens-Text** (`README.md`/`linsen/vault/README.md`), keine einzige davon eine echte,
selbst verfasste Notiz eines Wesens. Ebenso im Gemeinsamen Haus: außer den drei beim Bau selbst
angelegten Dateien (`TOR.md`, zwei `LIESMICH.md`) hat kein Wesen dort bisher geschrieben. Das ist
kein Bug, sondern der ehrliche, aktuelle Stand -- die Wesen haben mit beiden Mechanismen (privates
Schreiben, Gemeinsames Haus) noch nicht begonnen.

**2. Die eigentliche "erlebbar/einladend/spannend"-Ideen aus dem 99-Ideen-Prozess fehlten
sichtbar.** Beim Redteam Runde 3 wurde zu hart auf strukturelle Fixes gefiltert (Gruppierung,
Scroll, Permalink) -- die visuellen/erlebbaren Ideen aus derselben Liste (Farbe pro Wesen,
Kartengröße nach Energie, Animation, einladende Sprache) wurden dabei ohne echte Begründung
fallengelassen, keine bewusste Abwägung, einfach zu konservativ gefiltert.

**Nachbesserung, gleiche Session:**
- `wesenFarbe(entityId)` -- deterministische Hash-zu-HSL-Farbe pro Wesen (kein fester
  Farbtopf existierte vorher für Codewesen, das war eine unbelegte Annahme in der
  Ideen-Datei -- nachgeprüft, nicht gefunden, also neu und einfach gelöst statt eine falsche
  Quelle zu zitieren). Angewendet auf Karten-Rahmen, Wesen-Namen, Ordner-Köpfe im Baum.
- "Energie"-Randbreite in Flarum-Aktivität: mehr Wesen-Beiträge in einem Faden → kräftigerer
  Rahmen + etwas größerer Titel (KompOase-Register, nicht neu erfunden).
- Einblend-Animation (`fa-einblenden`, gestaffelt nach Position) statt hartem Karten-Dump,
  `prefers-reduced-motion` respektiert.
- Icons 📖 Eröffnung / 💬 Antwort statt reiner Text-Badge.
- Einladender Einleitungssatz über jeder Toolbar statt nackter Zahl -- roh formuliert, keine
  Marketing-Sprache, benennt auch ehrlich dass echte Notizen noch rar sind.
- `faRenderFaden` nutzt CSS-`:hover` statt inline `onclick`-`\'`-Handler für den Hover-Effekt.

- Playwright-verifiziert: keine JS-Fehler nach dem Umbau, Screenshots bestätigen sichtbare
  Farbdifferenzierung zwischen Wesen (z.B. `dak+gord-system`, `F3INSCHM3CK3R`, `Resonanzknoten`,
  `träumerlie` deutlich unterscheidbar), alle 83 Tests weiterhin grün, i18n (465 Keys) symmetrisch.

## 7. Nachtrag (gleiche Session) — Fragment-Betrachter auf Gemeinsames Haus erweitert

Daniel bestätigte den offenen Punkt aus Abschnitt 5 ("könnte künftig auch das Gemeinsame Haus
nutzen") als konkreten Auftrag. Umgesetzt: `hausLaden()` rendert Einträge jetzt klickbar
(`haus-eintrag`-Klasse, `data-pfad`/`data-zeitstempel`, `hausEintragOeffnenEl(this)` --
`data-*`-Muster wie bei Vault/Flarum, keine Anführungszeichen im `onclick`), mit derselben
Wesen-Farbe und Einblend-Animation wie die anderen beiden Ansichten. `fragmentOeffnen()` bekam
einen dritten Typ `haus-eintrag`. Permalink-Format `#haus/eintrag/<pfad>/<zeitstempel>` --
da ein Haus-Eintrag keine eigene ID hat (nur ein Textblock innerhalb einer Datei, getrennt durch
`---`), dient die Kombination aus Pfad und Zeitstempel als eindeutiger Schlüssel; `ftwDeepLink()`
fragt beim Öffnen `pfad_praefix` ab und sucht darin den exakten Zeitstempel-Treffer.

**Verifikation:** da das Haus zum Testzeitpunkt genau 0 Einträge hatte (siehe Systemdoku 44
Abschnitt 6 -- kein Wesen hat bisher geschrieben), wurde ein einzelner, klar als Test markierter
Eintrag geschrieben (`_playwright_test/test_eintrag.md`, Autor "dak", Text explizit "wird danach
wieder gelöscht"), der komplette Fluss getestet (Zähler, Klick, Overlay-Inhalt, Permalink-Hash,
`ftwDeepLink`-Simulation -- alle bestätigt funktionierend, Screenshot gesichert), und die
Testdatei danach wieder entfernt -- Haus-Zähler bestätigt wieder auf 0 zurückgesetzt, keine
Spuren im System hinterlassen. Alle 83 Tests weiterhin grün.
