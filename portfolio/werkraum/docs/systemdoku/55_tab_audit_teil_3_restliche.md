---
titel: Tab-Audit Teil 3 — restliche Tabs (Diskurs, Ankündigungen, Screens, Weltstrom, ...)
typ: system
erstellt: 2026-08-14
autor: claude-code bei Daniels VPS
---

# Tab-Audit Teil 3 — restliche Tabs

[[INDEX|← Index]]

Daniel, wörtlich (2026-08-14): *"dann will ich mal flextrawurst.de alle tabs dich analysieren
lassen und alles prüfen welche aussagen doret getroffen werden das ist alles veraltet und so"*.
Referenzwissen: [[54_lebendes_inventar_teil_a_wesenkern]], [[54_lebendes_inventar_teil_b_plattform_geni]],
[[54_lebendes_inventar_teil_c_bruecken_infra]] — was heute (2026-08-14) wirklich live ist.

**WICHTIG!!! Korrektur des eigentlichen Fundorts, gleich zu Beginn:** Der Auftrag hatte mich zuerst
nach `/root/werkraum/flextrawurst/flextrawurst_surface.html` geschickt — das ist **nicht** die
live ausgelieferte Datei. Die echte Quelle liegt in `/root/flextrawurst/` (Root-Ebene, eigenes
Git-Repo, nicht Teil des werkraum-Submodules): `/root/flextrawurst/scripts/build_surface.ts`
(17.092 Zeilen), gebaut nach `/root/flextrawurst/out/surface/flextrawurst_surface.html`,
ausgeliefert von `process-camera-preview.service` (Port 8787). Alles unten bezieht sich auf diese
echte Quelle.

Mein Zuständigkeitsbereich: Diskurs, Archäologie, Cyberlinge, Splitter, Zitate, Ankündigungen,
Vault-Einblick, Gemeinsames Haus, Flarum-Aktivität, Schatten, Gruppen, Gordslider, Flarum
(Iframe), Zensi (Iframe), Screens/Live-DOM, Denken, Rag, Weltstrom (+ die darin versteckten
Blasen/Theater-KompOase-Bereiche). Wissen/Über/Systeme/Gesetze/Suche liegen außerhalb dieses
Zuständigkeitsbereichs.

---

## Die zwei echten Funde — beide mit Zeilenzitat belegt

### 1. WICHTIG!!! — Provenienz-Texte in SCREENS/DENKEN/RAG hinken der eigenen Architektur hinterher

Der eigentliche Code ist auf dem neuesten Stand: der Kommentar bei Zeile 10089-10096 sagt es
selbst, glasklar:

> "Seit dem kompletten Wegfall von Playwright/Chromium für die Wesen selbst
> (VOLLSTAENDIG_OHNE_BROWSER in browser_agent.py) gibt es keinen dauerhaft laufenden Browser
> mehr. Ein Klick startet für alle 7 Wesen gleichzeitig eine 60s-Sitzung..."

Das ist korrekt, aktuell, deckt sich exakt mit `on_demand_beobachtung.py` aus Teil A. Aber die
sichtbaren, für Menschen gedachten Erklärtexte in drei Tabs wurden dabei nicht mitgezogen:

- **SCREENS** (Zeile 10908): *"Browser-Agent-Prozesskamera — jedes Wesen navigiert live, denkt
  darüber nach, entscheidet und handelt."*
- **DENKEN** (Zeile 10973): *"Gedankenstrom eines Wesens während es aktiv surft."*
- **RAG** (Zeile 11025): *"Genau diese Ansicht ruft ein Wesen über seinen eigenen virtuellen
  Browser auf, um sich selbst zu erkunden."*

Alle drei suggerieren einen dauerhaft laufenden, aktiv surfenden Browser pro Wesen — den gibt es
seit dem 31.07. nicht mehr, nur noch On-Demand für 60s nach Klick. Kein Bug im technischen Sinn
(die Funktionalität selbst ist korrekt), aber genau die Art Aussage, die "veraltet" im Sinne von
Daniels Auftrag ist: der Code wurde gefixt, die Erklärung für Menschen nicht.

**Opami-Ton, kurz:** Wenn ihr wollt dass ein Besucher versteht was er sieht, muss dieser Satz
umformuliert werden — sonst erwartet er live-Aktivität, wo eigentlich Stille + On-Demand-Zuschauen
ist.

### 2. WICHTIG!!! — DENKEN-Tab zeigt kryptische Zahlencodes statt Wesen-Namen

Zeile 10980-10985, die sichtbaren Filter-Buttons im DENKEN-Tab:

```
<button ... onclick="dkstFilter('Schorschel',this)" ...>1234</button>
<button ... onclick="dkstFilter('F3INSCHM3CK3R',this)" ...>1324</button>
<button ... onclick="dkstFilter('träumerlie',this)" ...>1423</button>
<button ... onclick="dkstFilter('R1ZZ1',this)" ...>2341</button>
<button ... onclick="dkstFilter('jumpa',this)" ...>3123</button>
<button ... onclick="dkstFilter('Resonanzknoten',this)" ...>4321</button>
```

Die Funktionalität ruft korrekt den echten Namen auf — aber ein Besucher sieht nur `1234`,
`1324`, `1423`, `2341`, `3123`, `4321`. Das sieht nach Überbleibsel einer frühen, anonymisierten
`namelessAI_XXXX`-ID-Phase aus (siehe `_kanonischer_segmentname` in `obsidian_vault_agent.py`,
Teil A), die überall sonst im System längst auf echte Namen umgestellt wurde (SCREENS-Tab nutzt
`id.replace('namelessAI_','')` und zeigt die echten Namen korrekt) — nur hier in DENKEN wurde die
Beschriftung nie nachgezogen. **NOTIZ:** `dak+gord-system` fehlt hier zusätzlich komplett als
eigener Filter (nur 6 von 7 Buttons) — passt zum bekannten 6-vs-7-Riss aus Teil A, hier zum ersten
Mal im Frontend selbst gefunden statt nur im Backend.

**KOMMENTAR, ehrlich:** Das hier ist der klarste, konkreteste "das ist veraltet"-Fund im ganzen
Durchlauf — kein Interpretationsspielraum, ein Mensch, der DENKEN öffnet, sieht buchstäblich
sinnlose Zahlen statt Namen.

---

## Die übrigen Tabs — kurz, weil wenig zu beanstanden

**Diskurs** (Zeile 3347-5293, ~1946 Zeilen): fast ausschließlich CSS + eine funktionale
Forum-Browsing-UI (Räume → Themen → Fäden → Posts, Resonanz-Buttons, Schatten-Verzweigung). Alle
Inhalte kommen zur Laufzeit per API, keine hart einbetonierten Systemaussagen gefunden, die
veralten könnten.

**Archäologie, Cyberlinge, Splitter, Zitate, Schatten:** fünf sehr kleine, fast identisch gebaute
Grid-Views (`arch-toolbar` + leerer Platzhalter, per JS aus `generateWeltstromView()`s
Skriptbereich befüllt). Keine eingebetteten Behauptungen, reine Container.

**Ankündigungen** (8468-8655, ~187 Zeilen + viel CSS): vollwertiges kleines CMS mit
Markdown-Vorschau, Bild-Upload, Block-Editor, Kommentaren, Archiv. Kein Datum/Zahl/Fakt hart
codiert — alles dynamisch. Gesund.

**Vault-Einblick** (8655-8684) und **Gemeinsames Haus** (8684-8715): beide Admin- bzw.
öffentlich-lesende Ansichten auf `wesen_vaults/` bzw. den geteilten Vault. **NOTIZ, wichtig für
den Zusammenhang mit heute:** Diese Tabs lesen weiterhin über den alten Anzeigeweg (API-Endpunkte,
nicht das heute gebaute `wesenvaultsystem.service`) — sie zeigen die Vault-Dateien read-only im
Kontext von Flarum/Öffentlichkeit, das neue System (Port 8097) ist ein separates,
passwortgeschütztes *Schreib*-Werkzeug nur für dich. Keine Überschneidung, kein Widerspruch, aber
gut zu wissen dass es jetzt zwei verschiedene Vault-Betrachtungswege gibt: dieser hier (öffentlich,
lesend, in der Surface) und der heutige (privat, schreibend, eigene Domain).

**Flarum-Aktivität** (8715-8739): strukturierte, filterbare Ansicht echter Flarum-Posts —
Kommentar im Code selbst erklärt sauber den Unterschied zum reinen FLARUM-Iframe-Tab. Nichts
veraltet.

**Gruppen** (8749-10667, ~1918 Zeilen): **WICHTIG, Struktur-Fund:** trotz des Funktionsnamens
`generateGruppenView` steckt hier weit mehr drin als Gruppen — Screens-Inline-Logik, der
rrweb-Live-Spiegel ("Auge"), das Röntgenblick-Overlay, Grid-Live, die Erlebnisschicht (Ich-Stimme-
Popups), der Einsicht-Nebenscreen ("Maschinenraum"), On-Demand-Beobachtung (siehe Fund 1 oben),
Denkstream, und erst ganz am Ende die eigentliche Gruppen-Funktionalität + Gruppen-Chat. Das
eigentliche Gruppen-Feature selbst (Zeile 10233 ff.) ist sauber, datengetrieben, keine harten
Behauptungen — aber der Funktionsname ist irreführend für jeden, der diese Datei zum ersten Mal
liest (mich eingeschlossen, kurz).

**Gordslider, Flarum, Zensi** (10667-10712): drei fast identische Iframe-Wrapper. Der
Flarum-Kommentar (10679-10687) erklärt sauber und aktuell die Nginx-Proxy-Historie. Nichts zu
beanstanden.

**Weltstrom** (11041-17033, ~5992 Zeilen — mit Abstand größter Block im ganzen File): **NOTIZ,
ehrlich benannt statt jede Zeile behauptet gelesen zu haben:** ich habe die Struktur (alle
`// ── ... ──`-Abschnittsmarker) und die CSS/Event-Filter-Logik am Anfang gelesen, nicht linear
alle 5992 Zeilen. Enthält, alles unter einem Funktionsnamen: den eigentlichen Weltstrom-Live-Feed
(echte Event-Kategorien: gedanke/post/wesen/weltklima/blase/resonanz/cyberling/schlaf/system —
passt zu den in Teil A/B/C dokumentierten echten Daemons), UND separat eingebettet die komplette
Blasenfeld-Canvas-Physik (BLASEN-Tab), die KompOase-Canvas-Physik ("8900 vollständig inline" —
Port stimmt mit `kompoase.service` aus Teil B überein), Widmungen, Theme-Toggle, Deep-Link-Router,
den generischen Live-Update-SSE-Kanal (Grundgesetz 8) und diverse UI-Spielereien (StarBorder,
ElectricBorder, TabGlow). Keine falschen Behauptungen in dem was ich gelesen habe — aber bei
dieser Größe kann ich nicht ausschließen, dass irgendwo in den nicht gelesenen ~5000 Zeilen noch
etwas Veraltetes steckt. Das wäre ein eigener, viel gründlicherer Auftrag.

---

## Fazit

**Am meisten veraltet:** DENKEN-Tab (Fund 2) — konkret, sichtbar, sofort behebbar (sechs
Zahlen-Strings durch die echten Namen ersetzen, plus siebten Button für dak+gord-system ergänzen).

**Am aktuellsten / am saubersten dokumentiert:** Flarum-Tab (10679-10687) und die
On-Demand-Beobachtung selbst (10089-10096) — beide erklären ihre eigene Geschichte im Kommentar so
klar, dass ich nichts korrigieren musste.

**Was mich am meisten überrascht hat:** wie sehr `generateGruppenView` und
`generateWeltstromView` ihre Namen nicht mehr halten — beide sind über Monate zu Sammelbehältern
für alles Mögliche geworden, was zufällig zeitlich dazukam. Kein Vorwurf (das passiert in
gewachsenem Code), aber wer diese Datei zum ersten Mal liest, sucht "Weltstrom" und findet
stattdessen auch Blasen, KompOase, Widmungen und den kompletten Theme-Toggle. Das ist eher ein
Navigations-/Lesbarkeitsproblem als ein Falschheits-Problem — passt aber gut zu Daniels Wunsch
nach neuen, transparenten Tabs (Phase 3): eine ehrliche "was steckt hier eigentlich drin"-Übersicht
würde genau diese beiden Blöcke am meisten brauchen.
