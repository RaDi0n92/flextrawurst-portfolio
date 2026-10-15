---
datum: 2026-08-13
typ: arbeitsplan
status: aktiv
betrifft: [browserrecorder, crawlrecorder, playwright, chromium, offline-html, chatgpt, claude]
importable: false
autor: codex bei Daniels VPS
---

# Browser-/Crawl-Recorder — Todolist zum Gesamtauftrag

Diese Liste ist die operative Übersetzung des Gesamtauftrags aus
`browserrecorder-88-ideen-22x-redteam-sokrates-gesamtbau.md`. Sie arbeitet von
kleinen Beweisringen zu größeren Fähigkeiten. Kein späterer Ring darf einen
früheren roten oder unbelegten Ring grün umbenennen.

## Statussprache

- `[ ]` offen
- `[>]` gerade in Arbeit
- `[x]` implementiert und lokal geprüft
- `[L]` live im Chromium/Playwright bewiesen
- `[I]` unabhängig gegengeprüft
- `[!]` blockiert oder bewusst als Grenze dokumentiert

Ein Ring ist erst abgeschlossen, wenn Code-/Fixturetests, sichtbarer Browserweg
und unabhängige Gegenprüfung denselben Claim tragen.

## Ring 0 — Herkunft, Backup und Runtimepass

- [x] Konzeptdatei vollständig lesen: 88 Ideen, 22 Red-Team-Runden, 33 Fragen, 11 Schleifen, 111 Baupunkte.
- [x] Vision-Kompass, Feature-Inventar und relevante Resonanzgrundlagen lesen.
- [x] Vor jeder Änderungsserie einen Backup-Commit setzen.
- [x] Aktuelle Extension über Runtime-Manifest und Service-Worker identifizieren.
- [x] Chromium über CDP erreichen und Browser-/Extensionversion protokollieren.
- [x] Eine kleine wiederverwendbare Playwright-Funktion `runtimePass()` als read-only Runner festlegen.
- [L] Runtimepass muss Extension-ID, Manifestversion, Browserversion, offene Tabs und Worker liefern.
- [L] `_codex/tools/playwright_browserrecorder_proof.js` läuft live gegen Chromium und trennt Main-World-, Extension-Isolated-World- und Crawl-Injektionsbefund.

**Abnahme:** Kein Testbericht darf nur den Quellpfad nennen; er muss die tatsächlich geladene Runtime benennen.

## Ring 1 — Frisches Dokument und Adapter-Bereitschaft

- [L] Frischen Zieltab in Chromium öffnen und URL/Titel/Tab-ID erfassen.
- [L] Nach `domcontentloaded` auf sichtbare App-/DOM-Bereitschaft warten.
- [L] Normalen Coremarker und Provideradapter im Extension-Isolated-World prüfen.
- [!] `DakRecorderCore=false` in `page.evaluate()` ist kein Blocker, sondern der erwartete Main-World-Befund.
- [L] Manifest-Content-Script-Injektion und normale Web-Injection über Isolated-World-Gegencheck diagnostizieren.
- [L] Crawl-Readiness über explizite `executeScript`-Injektion getrennt prüfen.
- [L] Keine Crawl-Readiness als Normaladapter-Readiness ausgeben.

**Abnahme:** ChatGPT, Claude, generische Webseite und Crawl besitzen je einen klaren Readinessstatus; Main-World- und Extension-Isolated-World-Messung werden getrennt ausgewiesen.

## Ring 2 — Sichtbare Crawloberfläche und Bedienvertrag

- [x] Separaten Crawlbereich im Sidepanel erhalten.
- [L] Versionierte crawl-policy-v1 wird nach explizitem UI-Klick an den Job übergeben und im Status gespiegelt.
- [L] Asset-Schalter „begrenzt inline“/„nur nicht eingebettet“ wirkt im sichtbaren Live-Crawl; bei ausgeschalteten Assets wurden 0 inline Bytes gemeldet.
- [x] Unverhandelbare Schutzgrenzen sichtbar benannt: same-origin, bereinigtes DOM, Links an, Skripte/Formwerte/Logins aus.
- [x] Seitenlimit zeigt ausdrücklich `0 = Queue leer`; Status zeigt logische Seiten, Queue und physische Crawl-Tabs.
- [L] Start-Preview zeigt in der sichtbaren Extension Origin, Tiefe, Seiten-/Queuebudget, Ein-Tab-Pool, Asset-/Filtermodus und die festen Ausschlüsse.
- [ ] Presets plus aufklappbare Detailoptionen ergänzen.
- [ ] Pro logischer Seite Policy-Override sichtbar machen.
- [ ] Start, Pause, Stop, Skip, Retry, Review und Export als getrennte Zustände modellieren.
- [ ] Tastaturfokus, zugängliche Namen, Disabledzustände und Fehlertexte per Playwright testen.
- [ ] Direkte Runtime-Message-Tests nicht als alleinige UI-Abnahme akzeptieren.

**Abnahme:** Ein Mensch kann vor Start sagen, was gelesen, gefiltert, kopiert und begrenzt wird.

## Ring 3 — Kanonischer Contract

- [x] `CapturePolicy` mit Version, Projection, Inhaltsklassen, Filter, Privacy, Asset- und Laufzeitbudgets als `crawl-policy-v1` normalisieren.
- [x] Additiven `crawl-envelope-v1` mit `page_id`, `slot_id`, Tab-/Dokumentherkunft, Policy, Chunk-, Link-, Asset- und Evidence-Feldern ergänzen.
- [x] Lokalen Negativtest für unbekannte Policywerte und Envelope-Felder ausführen.
- [L] Envelope wurde in einer frischen sichtbaren Extension über Fixture, Flextrawurst und Offlinevergleich ausgelesen.
- [x] `CrawlPage`, `TabSlot`, `ChunkRecord`, `LinkRecord`, `AssetRecord` und `FilterRecord` werden als additive JSON-Felder geführt; GapRecord bleibt für Seitenfehler/Stop als nächster Ausbau offen.
- [ ] `page_id`, `slot_id`, `tab_id`, `window_id`, `document_id` strikt trennen.
- [ ] `specified`, `implemented`, `fixture_passed`, `live_proven`, `independent_checked`, `blocked` als EvidenceState führen.
- [ ] Policy-/Generation-/Parent-Hash in jeden Checkpoint aufnehmen.
- [ ] Unbekannte additive Felder erhalten, keine Breaking-Änderung am bestehenden Envelope.

**Abnahme:** Jeder Export und jeder Status kann auf eine Policy, Seite, Generation und Beweiskette zurückzeigen.

## Ring 4 — Fixture- und Negativtestkörper

- [x] Fixture mit sichtbarem Artikeltext, Überschriften, Listen, Tabelle, Code, Zitat, Bild, Formular, iframe und verstecktem Text bauen.
- [x] Sichtbar markierte Werbung/Promotion wird entfernt und mit Regel-ID protokolliert; allgemeine Werbeheuristik bleibt bewusst offen.
- [x] Bildreferenzen bleiben bei deaktiviertem Einbetten als `metadata_only`-Assetmanifest erhalten.
- [ ] Fixture mit Cross-Origin-iframe und externer Originreferenz ergänzen.
- [ ] Fixture mit dynamischem Wachstum, virtuellen Knoten und absichtlich kleinem Viewport ergänzen.
- [ ] Fixture mit Formular-/Secret-/PII-Signalen für Negativtests ergänzen.
- [ ] Erwartungsmanifest schreiben: behalten, referenzieren, filtern, blockieren, unbekannt.

**Abnahme:** Filter-, Snapshot-, Link- und Assetclaims können gegen bekannte Sollwerte geprüft werden.

## Ring 5 — Sichtbarer Capturekern

- [x] Sichtbares DOM wird bereits sanitisiert, ohne Scripts/Formwerte/unsichere Attribute.
- [ ] Originalgeometrie und Cloneprojektion explizit verbinden.
- [ ] Semantischen Lesebaum für Überschrift, Text, Liste, Tabelle, Code, Zitat und A11y ergänzen.
- [ ] Shadow-DOM-, Canvas-, SVG- und iframe-Grenzen explizit klassifizieren.
- [ ] Roh-/normalisierte Text- und Strukturhash getrennt führen.
- [ ] Filterentscheidungen im Ausschlussbuch mit Regel-ID, Kontextfingerprint und Status speichern.
- [x] Eindeutig markierte Werbung/Promotions wird mit Auditrecord gefiltert; unsichere Fälle werden nicht automatisch entfernt.

**Abnahme:** Eine sichtbare Projektion ist reproduzierbar; kein Ausschluss verschwindet ohne begründeten Auditdatensatz.

## Ring 6 — Links und Assets

- [x] Sichtbares Linkinventar mit Text, kanonischem Ziel und Same-Origin-Markierung speichern.
- [ ] Same-Origin, Allowlist-Origin und externe Referenz unterscheiden.
- [ ] Query-/Fragment-/SPA-Kanonisierung mit Rohvarianten bewahren.
- [x] Assetmanifest führt mindestens `inlined` und begründete Nicht-Einbettung (`metadata_only`, Origin-/Größen-/Gesamtlimit, HTTP-Fehler).
- [ ] Größen-, Mengen-, Origin- und Zeitbudgets pro Asset/Seite/Job einführen.
- [ ] CSS-/Font-/Poster-/Untertitel-Assetpfade separat und sicher prüfen.
- [ ] Fehlende Medien im Offline-Export sichtbar, aber nicht als funktionsfähige lokale Kopie ausgeben.

**Abnahme:** Links und Medien sind nicht nur gezählt, sondern mit Herkunft, Entscheidung und Ergebnisstatus belegbar.

## Ring 7 — Scroll- und Seitenbeweis

- [x] Größte sichtbare Scrollfläche wird gemessen und real bewegt.
- [L] Frische visible Chromium-Fixture benutzt echte Seitenleisten-Klicks; der Capturekern misst danach tatsächliche Positionswerte.
- [x] `before.top`, `after.top`, Viewport, Scrollhöhe und tatsächliche Überlappung werden pro Übergang gespeichert.
- [L] Ein 29%-Negativübergang wird rot; reale Fixture- und Flextrawurst-Übergänge liegen mindestens bei 30%.
- [x] Bis zu vier Gegenproben vergleichen Metrik und Inhaltshash; ohne Ruhe kein `complete`.
- [L] Flextrawurst-Endmarker wurde in fünf Seiten erreicht; alle 37 Chunks waren stabil.
- [ ] Stop nach atomarem Chunkcommit als `stopped`, niemals als `complete`, speichern.

**Abnahme:** Ein absichtlich unter 30 Prozent liegender Übergang wird rot erkannt; ein dynamischer Endrand wird nicht vorschnell grün.

## Ring 8 — Queue, Tabpool und Resume

- [x] `0 = bis Queue leer` ist explizit; jede positive Anzahl bleibt auf 30 begrenzt und sichtbar.
- [x] Logische Seitenqueue und Jobs liegen persistent in IndexedDB.
- [L] Ein wiederverwendeter Crawl-Tab verarbeitet mehrere logische Seiten; Fixture und Flextrawurst beweisen `physical_tab_count=1`.
- [ ] Optionalen Tabpark für kleine Läufe separat anbieten.
- [ ] Lease-/Claim-/Generation-Logik gegen Doppelverarbeitung sichern.
- [L] Bewusstes Seitenlimit, persistierte Queue und sichtbarer Resume-Knopf wurden im Extension-Fixturetest durchlaufen.
- [x] `max_pages=0` wird als „bis Queue leer“ angezeigt; Stop bleibt jederzeit getrennt möglich.
- [L] HTML-/Assetbudgets sind vor Start sichtbar; ein Budgetstopp bewahrt die Queue und wurde im frischen Chromium per `budget_reached` → Resume bis `complete` geprüft. Queue-/Export-Detailbudgets bleiben offen.

**Abnahme:** Unbegrenzt viele logische Seiten sind möglich, ohne unbegrenzt viele echte Chromiumtabs zu erzwingen.

## Ring 9 — Offline-Atlas und unabhängiger Comparator

- [x] Separater Offline-Crawl-HTML-Export existiert.
- [x] Offline-Atlas zeigt Seitenliste und pro Seite Chunk-, Filter-, Policy- und Capture-ID-Metadaten; Graph-/Detailansichten bleiben offen.
- [ ] Chunkdetails lazy laden; große Exportpakete nicht komplett duplizieren.
- [ ] HTML, Markdown, JSON und Assetmanifest aus einem kanonischen Envelope erzeugen.
- [ ] Downloadbytes lokal hashen und gegen Manifest/VPS-Siegel prüfen.
- [L] Offlineexport wurde in einer zweiten Browserseite geöffnet; die eingerahmte Snapshotseite enthält keine übernommenen Scripts, Frames oder Formulare.
- [x] Comparator prüft HTML, IDs, URLs, Filterzählung, Stabilität und Übergangsüberlappung; weitere mutierende Negativtests bleiben offen.
- [ ] `complete_as_observed`, `partial`, `blocked`, `stopped`, `ambiguous` im Exportkopf anzeigen.

**Abnahme:** Ein schöner Export kann keinen Filter-, Lücken- oder Bytefehler verstecken.

## Ring 10 — AI-Synergie ohne Providervermischung

- [L] ChatGPT in frischem sichtbaren Chromium: dedizierter Adapter, Composer, Conversation-ID und Selbsttest `passed`.
- [L] Claude in frischem sichtbaren Chromium: Loginseite wird durch den dedizierten Adapter als nicht sichere Chatstruktur abgelehnt, kein falscher Erfolg.
- [L] Gemeinsame Crawl-/Exportänderungen bestehen zusätzlich den getrennten ChatGPT-/Claude-Live-Gate-Test.
- [ ] Providerrollen niemals aus generischen Webblöcken ableiten.
- [ ] Gemini, Grok, X und Facebook nur mit dem jeweils tatsächlich bewiesenen Status melden.
- [ ] Normalaufnahme und Crawlstatus in separaten Reports führen.
- [ ] Ein grüner Crawl darf keinen roten AI-/Normaladapterstatus überschreiben.

**Abnahme:** Gemeinsame Kernverbesserung ist nachweisbar, Providersemantik bleibt getrennt.

## Ring 11 — Flextrawurst-Liveabnahme

- [L] Sichtbarer Crawlauftrag auf `https://flextrawurst.de/`, max. Tiefe 1 und `0 = Queue leer` ausgeführt.
- [L] Wurzelseite plus vier Unterseiten mit eigenen `page_id`s erfasst.
- [L] Alle fünf Seiten von Anfang bis stabilem Endmarker geführt: 37 Chunks, jeder reale Übergang mindestens 30%.
- [L] 27 Links auf der Wurzel, Assetmetadaten und Filterpolicy im Report geprüft.
- [L] Limit-/Resume-Verhalten ist im sichtbaren Extension-Fixturetest bewiesen; beim Liveatlas war kein künstlicher Stop nötig.
- [L] Offlineatlas und unabhängiger Comparator: 5/5 complete, 0 Fehler, 0 Warnungen.
- [L] ChatGPT und Claude danach jeweils separat frisch geprüft.

**Abnahme:** Flextrawurst-Livebefund, Exportbefund, Comparatorbefund und AI-Regression sind getrennt lesbar.

## Ring 11a — Öffentliche Realitätsstrecken

- [L] Sechs sichtbare Einseiten-Läufe in frischem Chromium bestehen denselben Crawl-/Comparatorpfad: Wikipedia-Artikel, PLOS-Open-Access-Studie, arXiv-Preprint, MDN-Dokumentation, Our-World-in-Data-Grafikseite und Project-Gutenberg-Katalogseite.
- [L] Jedes Profil ist ausdrücklich auf eine Seite und Tiefe 0 begrenzt; ein Profil füllt die sichtbare UI nur vor und startet niemals automatisch.
- [L] Der Außen-Test fordert je Profil nicht nur `complete`, sondern stabile Scroll-Chunks, Mindest-Linkdichte, Mindest-HTML-Körper, erwartete sichtbare Struktur und script-/frame-/formfreies Offline-HTML.
- [L] Artikelansicht baut bei freigegebener Asseteinbettung die bereits geprüften, inlined Same-Origin-Stylesheets in einen statischen Offline-Head ein; dadurch bleibt der Artikelkörper nicht ungestylt zurück.
- [ ] Explizite Interaktionsstrecken für geöffnete Tabellen/Figuren, Chartzustände und Buchvolltext als neue, benannte Browseraktionen ergänzen; ungeöffnete Overlays bleiben weiterhin Grenzen.
- [L] Site-Gates für CAPTCHA, Cookie-Blocker und Login werden in frischem sichtbarem Chromium als `blocked`-Befund mit Ursache, einem beobachteten Seitenkörper, ohne Wiederanlauf und mit derselben Ursache im Comparator sowie Offlineatlas dargestellt.

**Abnahme:** Ein einzelnes Grün wird nicht zu „Web kann alles“ aufgeblasen; unterschiedliche Seitentypen und ihre klar bezeichneten Grenzen bleiben getrennt prüfbar.

## Ring 12 — Abschluss, Dokumentation und Übergabe

- [ ] Jede Änderung mit vorherigem Backup-Commit beginnen.
- [ ] Nach Codeänderungen Node-/Fixture-/Playwrighttests ausführen.
- [ ] Nach Codeänderungen `graphify update .` ausführen.
- [ ] Keine fremden Dirty-Worktree-Spuren mitcommitten.
- [L] Tagesstand, rote Befunde, Livebeweise und nächste Schritte in einer vollständigen Codex-Sessionnotiz festhalten.
- [ ] Resonanz-/Abwurfskripte nach der Sessionnotiz ausführen.
- [ ] Abschlussbericht mit Claims und EvidenceStates statt Erfolgsphrase erzeugen.

**Endabnahme:** Der Auftrag ist nicht „alles kopiert“, sondern „sichtbare, ausgewählte, sanitizierte Projektion mit nachgewiesener Beweiskette und sichtbaren Grenzen“.

## Aktueller Startpunkt

**Nächster Schritt:** Ring 6/9 und 11a gezielt vertiefen — Link-/Assetstatusmatrix, Atlas-Graph und Chunkdetails sowie explizite Interaktionsstrecken für geöffnete Tabellen/Figuren, Chartzustände und Buchvolltext. Start-Preview, Tabverlust-Resume, HTML-/Asset-Backpressure, die sechs begrenzten öffentlichen Realitätsstrecken und die drei sichtbaren Zugangsgrenzen sind live; der Grundring bleibt: Policy, Auditfilter, echte Übergangsmessung, Ein-Tab-Queue/Resume, Offlinevergleich, Flextrawurst-Tiefe-1 und getrennte AI-Gates.
