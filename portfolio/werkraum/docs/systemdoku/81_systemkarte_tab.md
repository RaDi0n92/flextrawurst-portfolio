---
titel: Systemkarte — Tab mit sechs Architektur-Diagrammen (DE/EN, öffentlich)
typ: system
erstellt: 2026-10-01
autor: claude-code bei Daniels VPS
---

# Systemkarte — Tab mit sechs Architektur-Diagrammen

[[INDEX|← Index]]

Daniel, 2026-10-01: die Diagramme als Tab weit vorne auf die Surface, Reiter pro Diagramm,
öffentlich, crawlbar, Deutsch und Englisch, mit je eigenem Aussehen.

---

## Was gebaut wurde

Tab `systemkarte` (DE "SYSTEMKARTE", EN "SYSTEM MAP"), direkt hinter "WAS IST DAS?".

Sechs Reiter: Gesamtbild, Selbstbild, LangGraph und Weltbild, Datenbank und RAG, Vaults, Werkzeuge.

Jeder Reiter lädt sein Diagramm per `iframe`. Dazu gibt es einen Link "in neuem Fenster öffnen".

Die Diagramme sind Momentaufnahmen, Stand 2026-10-01, und im Tab auch so beschriftet.

## Wo was liegt

- Zwölf Diagramm-Dateien: `flextrawurst/public/systemkarte-<name>-<de|en>.html`.
  Der Server liefert sie ohne Login aus, ohne Neustart (flache Namen, `public/` zuerst).
- Text und Knotenliste jedes Diagramms: `flextrawurst/i18n/systemkarte.json`. Daraus baut
  `generateSystemkarteView()` in `build_surface.ts` den Text als echtes HTML in den Tab.
  Grund: Der Inhalt eines `iframe` zählt für Crawler nicht als Seitentext.
- Sitemap: `aktualisiereQuellenSitemap()` trägt die zwölf URLs in den verwalteten Block ein.
- `public/llms.txt`: neuer Abschnitt "Architecture diagrams (snapshot, 2026-10-01)" mit der
  bestehenden Vorsichtsregel (Momentaufnahme, kein Beleg für gelebtes Wesen-Leben).
- Tab-Eintrag in `switchView` (views, colViews), im Deep-Link (`allViews`) und im Sprachwechsel
  (`setLang` ruft `skSprache()`), Schlüssel `tab.systemkarte` und `sk.*` in `UI_TR` DE und EN.
- Test: Abschnitt "SYSTEMKARTE-Tab" in `tests/surface_ring_23.test.ts` (7 Tests), dazu
  "EN-Modus und Deep-Link" (3 Tests). Stand live: 126 von 126 Tests grün.

## Wie die Diagramme entstehen

Erzeugt mit Archify (MIT, https://github.com/tt-a1i/archify), Befehl `finalize`, Qualität
`showcase`. Die Quelle sind Python-Skripte mit je einer deutschen und englischen Fassung,
abgelegt unter `flextrawurst/ops/systemkarte/` (siehe Abschnitt "Neu erzeugen").

Aussehen: pro Diagramm eine Archify-Vorlage (`meta.visual_preset`). Gesamtbild classic,
Selbstbild editorial, LangGraph und Vaults blueprint, Datenbank und Werkzeuge signal-flow bzw.
editorial. Im Viewer lässt sich die Vorlage oben im Menü umstellen.

Breitengrenze: Der Validator verlangt für Architektur-Diagramme eine Breite von höchstens
1240 px. Darüber schrumpft die Schrift unter die Lesbarkeitsgrenze.

## Für öffentliche Fassung entfernt

Der Hinweis auf den Crawler-Zugang der Toolbox und das Wort "Basic-Auth" stehen nicht in den
Diagrammen. Ein Test prüft die zwölf Dateien auf diese Begriffe.

## Beleglage der Inhalte

Gelesen oder abgefragt am 2026-10-01: Quellcode (`codewesen_lg_daemon.py`, `innenleben/`,
`weltbild_builder.py`, `rag_*`, `obsidian_api.py`, `events_stream_api.py`), PostgreSQL
(nur lesend, 108 Tabellen in public) und die lauschenden Ports.

Nur aus der Doku, nicht nachgeprüft: der Takt der Welt-Brücke, die Liste der Daemons, die
Surface-Tabs und der Zugriff der Bridge auf die Wesen-Vaults. Diese Stellen sind in den
Diagrammen selbst als solche markiert.

## Build in der Claude-Code-Umgebung (gelöst, 2026-10-01)

In der Claude-Code-Umgebung zeigt `/root` nicht auf das VPS-Home (das liegt unter `/vps_root`).
`build_surface.ts` las deshalb für den Tab Guardianstyle `/root/.claude/.guardianstyle_banner_state.json`
und die dort genannten Dateien nicht und lieferte die volle Fassung mit fast leerem
Guardianstyle-View (24 KB statt 555 KB). Die öffentliche Fassung war nie betroffen (der Bereich
liegt hinter `ARCHGATE`).

Behoben mit der Hilfsfunktion `vpsPfad()` in `build_surface.ts`: existiert ein `/root/...`-Pfad
nicht, wird `/vps_root/...` versucht. Auf dem VPS selbst bleibt der Pfad unverändert. Danach
ergibt der Build in beiden Umgebungen dieselbe volle Fassung (Guardianstyle-View 555.530 Byte).

## Zwei weitere Korrekturen in `build_surface.ts` (2026-10-01)

**Englisch-Modus.** Im Englisch-Modus warf die Surface beim Laden `SyntaxError: Unexpected
identifier 't'`, und das große Diskurs-Skript startete nicht. Ursache: `applyLegacyText` lief
auch auf dynamisch eingefügten `<script>`-Elementen und schrieb deren Text über eine
Regex-Rückfallstufe mit einer kaputten Kopie zurück (jedes `s` wurde zu einem Leerzeichen).
Behoben: `eachTextNode` fasst `SCRIPT`, `STYLE` und `TEXTAREA` nie als Wurzel an.

**Deep-Link bei frischem Laden.** `switchView('uber')` leert am Skriptende den Hash. Der Hash
war deshalb schon leer, wenn `ftwDeepLink` am `DOMContentLoaded` lief. Behoben: Rückgriff auf
den früh gesicherten `window.__ftwFruehHash`. Getestet im Browser: `#systemkarte/<name>`,
`#wesen` und `#diskurs` öffnen jetzt, `#admin` ohne Rechte landet weiter auf "WAS IST DAS?".

Drei neue Tests im Abschnitt "EN-Modus und Deep-Link" (126 von 126 Tests grün).

## Neu erzeugen

Die Quellskripte liegen im Repo: `flextrawurst/ops/systemkarte/` (`build_i18n.py`,
`merge_manifest.py`, `regenerate.sh`, `README.md`). Ein Probelauf erzeugte alle zwölf Dateien
und das Manifest byte-gleich zu den Live-Dateien.

## Offen

- Die Diagramme nennen interne Ports, Dienstnamen und DB-Zahlen. Daniel hat "öffentlich"
  entschieden.
- Nichts Offenes aus diesem Baustein.

## Dritte Korrektur: Backslashes im Legacy-Übersetzungsblock (2026-10-01, Daniels Go)

In `applyLegacyText` und `LEGACY_REGEX_EN` gingen in der gebauten Seite die Backslashes verloren
(`\s` und `\d` stehen in einem Template-Literal und müssen als `\\s` und `\\d` geschrieben werden).
Die Whitespace-Normalisierung machte aus jedem `s` ein Leerzeichen, und die Zahl-plus-Wort-Regeln
(z.B. "5 Beiträge" zu "5 posts") griffen nie. Folge: Einträge des Legacy-Wörterbuchs, deren Text
ein kleines `s` enthält, wurden nie übersetzt.

Behoben durch doppelte Backslashes in diesem Block (8 Zeilen). Gemessen im Englisch-Modus der
öffentlichen Surface: 74 von 4381 Textknoten ändern sich, alle durch bereits vorhandene
Wörterbuch-Einträge (z.B. "Systemkörper" zu "System bodies", "Resonanzen" zu "Resonances").
Der Deutsch-Modus ist unberührt. Neuer Test: "EN-Legacy-Regeln: Backslashes in der gebauten Seite"
(127 von 127 Tests grün).
