---
datum: 2026-08-13
typ: konzeptdokumentation
status: entwurf-v2-nach-44-facher-playwright-redteam-pruefung
betrifft: [browserrecorder, crawlrecorder, sichtbares-dom, flextrawurst, offline-html, redteam, sokrates]
importable: false
autor: codex bei Daniels VPS
---

# Browser-/Crawl-Recorder: 88 Ideen, 22 Red-Team-Runden und Gesamtbauauftrag

> **Version 2 — Beweis-, Chromium- und Bedienredteam:** Die ursprüngliche Konzeption bleibt als Herkunft erhalten. Die nachfolgenden Abschnitte überschreiben keine früheren Ideen still, sondern schärfen sie mit realen Playwright-/Chromium-Befunden, unabhängigen Gegenprüfungen und einer menschlich bedienbaren Abnahmekette.

## Auftrag und Leitplanken

Daniel will aus dem Browserrecorder zusätzlich einen ausdrücklich gestarteten Seitenlese- und Crawlrecorder machen. Für jede entdeckte Seite soll der Recorder den sichtbaren Inhalt stückweise von oben nach unten aufnehmen und als Offline-HTML, Markdown, JSON und Medien-/Linkmanifest abbilden. Der normale AI-Chatrecorder bleibt dabei ein eigener Modus. ChatGPT, Claude, Gemini und andere AI-Oberflächen profitieren vom gemeinsamen Kern, bekommen aber weiterhin eigene semantische Adapter und eigene Regressionstests.

„Alles mitnehmen“ bedeutet in diesem Konzept: alles, was der Nutzer im Browser sichtbar freigibt und dessen Capture-Schalter aktiviert, nicht heimlich jede interne API, jedes Sessiongeheimnis oder jeden unsichtbaren Datenbestand. Werbung, Tracker, Cookie-Layer und Dekoration werden standardmäßig als Ausschlusskandidaten behandelt, aber mit Herkunft und Grund protokolliert. Ein unsicherer Treffer wird nicht blind gelöscht.

Die 88 Ideen sind jeweils mit Ausgangsrichtung, erstem Angriff, verbesserter Form und einem überprüfbaren Kriterium beschrieben. Danach folgen 22 benannte Red-Team-Durchgänge über die gesamte Liste, 33 sokratische Fragen mit doppeltem Einzel-Red-Team und 11 Schleifen sowie ein Gesamtbauauftrag mit 111 separaten Red-Team-/Verbesserungspunkten.

## Nicht verhandelbare Invarianten

1. **Expliziter Start:** Ein Crawl beginnt nur durch den eigenen Crawl-Button beziehungsweise einen klaren Crawl-Auftrag.
2. **Modustrennung:** Normalaufnahme und Crawlaufnahme teilen sichere Bibliotheken, aber nicht Startlogik, Status oder Vollständigkeitsanspruch.
3. **Sichtbarkeitsgrenze:** Quelle ist der gerenderte, sichtbare Browserinhalt; versteckte DOM-Daten und fremde APIs bleiben draußen.
4. **Pro Tab wählbar:** Jeder Tab beziehungsweise jede logische Seite besitzt ein eigenes Capture-Profil, das vor und während des Scans sichtbar ist.
5. **Ausschlussbuch:** Ausgefilterte Werbung, Tracker, Cookie-Banner und Unsicherheiten werden mit Grund, Regel, URL und Hash dokumentiert.
6. **Herkunft:** Jede Seite, jeder Chunk, jedes Asset, jeder Link und jeder Filterentscheid trägt URL, Zeit, Tab-/Seiten-ID und Policy-Version.
7. **Beweisstatus:** `complete`, `partial`, `blocked`, `stopped`, `ambiguous` und `failed` bleiben unterscheidbar.
8. **Ressourcenbegrenzung:** Unendlich viele logische Seiten sind als Queue möglich; unendlich viele gleichzeitig geöffnete Browser-Tabs sind kein Ziel.
9. **Externe Ziele:** Externe Links werden katalogisiert, aber nur nach zusätzlicher Origin-Freigabe gecrawlt.
10. **Keine falsche 1:1-Behauptung:** Der Export sagt exakt, welche Projektion und welche Lücken vorliegen.

## 88 Ideen

### A. Auftrag, Modus und Herkunft — Ideen 1–11

### 1. Eigenständiger Crawl-Button

- **Idee:** Ein eigener Abschnitt „Crawlrecorder · Offline-Webatlas“ startet den Crawl und bleibt neben dem normalen Aufnahmebutton.
- **Redteam:** Ein gemeinsamer Button könnte versehentlich laufende AI-Aufnahmen in einen Seitencrawl verwandeln.
- **Verbesserung:** Getrennte Start-, Stop-, Pause- und Exportzustände mit eigenem `crawl_id`; keine automatische Umwandlung.
- **Kriterium:** Ein normaler `record`-Lauf erzeugt niemals eine Crawl-Job-ID.

### 2. Crawl-Auftrag als lesbares Formular

- **Idee:** Start-URL, erlaubte Origins, Tiefe, Seitenlimit, Tabpool und Capture-Profil werden vor Start angezeigt.
- **Redteam:** Versteckte Defaults führen zu einem größeren Crawl als beabsichtigt.
- **Verbesserung:** Vor dem Start eine zusammenfassende Freigabekarte mit allen effektiven Werten und Warnungen.
- **Kriterium:** Der Job-Manifest enthält exakt die bestätigten Optionen.

### 3. One-shot, Fortsetzen und Wiederholen

- **Idee:** Ein Auftrag kann einmalig laufen, pausieren, nach Browser-/Extension-Neustart fortgesetzt oder als neuer Lauf wiederholt werden.
- **Redteam:** Fortsetzen könnte alte und neue Zustände vermischen.
- **Verbesserung:** Parent-Job, Checkpoint-Hash und neue Laufgeneration; nie stilles Überschreiben.
- **Kriterium:** Jeder Wiederanlauf ist im Manifest als neue Generation sichtbar.

### 4. Zieldefinition „Seite gelesen“

- **Idee:** Eine Seite gilt erst als gelesen, wenn Anfang, Ende, stabile Chunks und aktivierte Inhaltsklassen geprüft wurden.
- **Redteam:** Ein erreichter Endpunkt kann bei virtuellen Seiten einen unvollständigen Körper bedeuten.
- **Verbesserung:** Seitenstatus setzt sich aus Sentinel-, Stabilitäts-, Coverage-, Asset- und Filterbelegen zusammen.
- **Kriterium:** Kein `complete`, wenn ein Pflichtbeleg fehlt.

### 5. Crawl-Plan vor Navigation

- **Idee:** Vor dem Öffnen werden URL-Regeln, Query-Strategie, Hashbehandlung und Linknormalisierung festgelegt.
- **Redteam:** Tracking-Parameter erzeugen tausende scheinbar verschiedene Seiten.
- **Verbesserung:** Konfigurierbare kanonische URL-Regeln mit Vorschau der zusammengeführten URLs.
- **Kriterium:** Jede zusammengeführte URL behält ihre beobachteten Varianten im Herkunftsprotokoll.

### 6. Benutzerfreigabe pro Origin

- **Idee:** Same-Origin ist Standard; weitere Origins, CDNs oder Bildhoster können einzeln freigegeben werden.
- **Redteam:** Ein weiter Origin-Schalter könnte den Crawl unbemerkt ausweiten.
- **Verbesserung:** Allowlist mit Herkunft, Zweck, Ablauf und sichtbarer Reichweite.
- **Kriterium:** Eine nicht freigegebene Origin wird höchstens als externer Link/Asset-Referenz katalogisiert.

### 7. Leseziel statt Downloadziel

- **Idee:** Der Auftrag heißt „sichtbare Seite lesen und abbilden“, nicht „Serverbestand herunterladen“.
- **Redteam:** Das könnte wichtige eingebettete Medien ausschließen.
- **Verbesserung:** Sichtbare Medien werden optional referenziert oder begrenzt lokal eingebettet; unsichtbare Rohressourcen bleiben draußen.
- **Kriterium:** Der Export unterscheidet `visible_reference`, `embedded_copy` und `not_captured`.

### 8. Auftragsnotiz und Zweck

- **Idee:** Der Nutzer kann Zweck und erwartete Inhaltsklassen notieren.
- **Redteam:** Freitext wird zur unprüfbaren Sonderlogik.
- **Verbesserung:** Zweck ist Metadatum, niemals eine Regel; Regeln bleiben strukturierte Optionen.
- **Kriterium:** Der Zweck beeinflusst keinen Capture-Entscheid ohne explizite Policy.

### 9. Trockenlauf

- **Idee:** Ein Crawl kann zunächst nur Links, sichtbare Blöcke, Filterkandidaten und Kosten schätzen.
- **Redteam:** Ein Trockenlauf könnte schon Ressourcen laden und als Scan missverstanden werden.
- **Verbesserung:** Status `preview_only`, keine Seitenartefakte als vollständig, klare Zählung der berührten Tabs.
- **Kriterium:** Preview und Capture besitzen getrennte Jobtypen.

### 10. Sichtbare Startbestätigung

- **Idee:** Vor dem Start zeigt das Panel Start-URL, Login-/Consent-Hinweise und gewählte Schalter.
- **Redteam:** Ein automatischer Consent-Klick würde Nutzerentscheidungen fälschen.
- **Verbesserung:** Consent bleibt manuell; der Recorder wartet und markiert `blocked_by_consent`.
- **Kriterium:** Kein synthetischer Klick auf Einwilligungs- oder Login-Controls.

### 11. Provenienz-Passport je Auftrag

- **Idee:** Ein Passport bündelt Browser, Extension, Policy, Zeit, Job, Benutzerfreigabe und Grenzen.
- **Redteam:** Ein einzelnes Manifest kann Zwischenstände nicht beweisen.
- **Verbesserung:** Versionierte Start-, Checkpoint- und Endpassports mit Parent-Hash.
- **Kriterium:** Jeder Export verweist auf die gesamte Passport-Kette.

### B. Per-Tab- und Capture-Profile — Ideen 12–22

### 12. Profilvorlage plus Tab-Override

- **Idee:** Ein globales Profil liefert Defaults; jedes Tabprofil kann einzelne Schalter überschreiben.
- **Redteam:** Ein Override wird übersehen und führt zu unerwarteten Inhalten.
- **Verbesserung:** Effektive Policy wird pro Tab als zusammengeführte, lesbare Liste angezeigt.
- **Kriterium:** Export und Status zeigen Default, Override und effektiven Wert.

### 13. Inhaltsklassen als einzelne Schalter

- **Idee:** Text, Überschriften, Listen, Tabellen, Code, Zitate, Kommentare, Links und Metadaten sind einzeln wählbar.
- **Redteam:** Zu viele Schalter machen das System unbedienbar.
- **Verbesserung:** Presets `Lesen`, `Dokumentation`, `Archiv`, `Design` plus „Details anzeigen“.
- **Kriterium:** Presets sind nur gespeicherte Policywerte und vollständig editierbar.

### 14. Bilder separat steuern

- **Idee:** Bilder können als URL, als begrenzte lokale Kopie, nur mit Alttext oder gar nicht übernommen werden.
- **Redteam:** Ein Bildschalter könnte Tracking-Pixel und redaktionelle Bilder gleich behandeln.
- **Verbesserung:** Sichtbarkeit, Größe, Mime-Typ, Dimensionen und Kontext gehen in den Entscheid ein.
- **Kriterium:** Jedes Bild bekommt `captured`, `referenced`, `filtered` oder `blocked`.

### 15. Video und Audio separat steuern

- **Idee:** Poster, Playertext, Untertitel und Medienquelle werden getrennt behandelt.
- **Redteam:** Große Videos sprengen Speicher und Urheberrechtsgrenzen.
- **Verbesserung:** Standardmäßig Metadaten/Poster/Untertitel; Binärkopie nur nach Größen- und Policyfreigabe.
- **Kriterium:** Kein großes Medienobjekt wird ohne sichtbare Einzelbestätigung eingebettet.

### 16. CSS- und Fontprofil

- **Idee:** Gerenderte Styles, Stylesheet-Referenzen und Fonts sind eigene Captureklassen.
- **Redteam:** Vollständige CSS-Kopie kann externe Tracker oder aktive Inhalte einschleusen.
- **Verbesserung:** CSS wird sanitisiert, URLs werden geprüft, Fonts bekommen Größen-/Originlimit.
- **Kriterium:** Offline-HTML enthält keine ausführbaren CSS-Ressourcen oder unprotokollierten Cross-Origin-Fetches.

### 17. Layout- und Designprofil

- **Idee:** Der Nutzer kann entscheiden, ob Layouttreue, nur Lesbarkeit oder beides priorisiert wird.
- **Redteam:** Layouttreue kann Werbung und dekorative Leerflächen konservieren.
- **Verbesserung:** `reading`, `faithful_visible`, `semantic` als klar benannte Exportprojektionen.
- **Kriterium:** Jeder Export nennt seine Projektion im Header und Manifest.

### 18. Accessibility-Profil

- **Idee:** Rollen, Labels, Alttexte, Tabellenköpfe und Fokusreihenfolge werden optional erhalten.
- **Redteam:** ARIA kann versteckte oder widersprüchliche Zustände enthalten.
- **Verbesserung:** Nur sichtbare, semantisch relevante A11y-Attribute; Konflikte werden markiert.
- **Kriterium:** A11y-Export behauptet keine Interaktivität, die offline nicht funktioniert.

### 19. Interaktionsprofil

- **Idee:** „Mehr anzeigen“, Akkordeons, Tabs und Dialoge können pro Tab ausdrücklich zum Lesen geöffnet werden.
- **Redteam:** Öffnen verändert den Seitenzustand und kann Aktionen auslösen.
- **Verbesserung:** Whitelist passiver UI-Controls, Vorher-/Nachher-Snapshot und sichtbare Bedienbestätigung.
- **Kriterium:** Kein Control wird geöffnet, wenn es Navigation, Submit, Kauf, Login oder Mutation auslösen kann.

### 20. Formularprofil standardmäßig aus

- **Idee:** Formularwerte, Inputs und private Eingaben werden nie standardmäßig kopiert.
- **Redteam:** Ein Formular kann redaktionell notwendiger sichtbarer Inhalt sein.
- **Verbesserung:** Struktur und Labels optional, Werte grundsätzlich maskiert/ausgelassen; explizite Ausnahme nur pro Seite.
- **Kriterium:** Sessiontokens, Passwortwerte und personenbezogene Inputwerte erscheinen nie im Snapshot.

### 21. Screenshot-/Viewportprofil

- **Idee:** Pro Chunk kann zusätzlich ein Screenshotbeleg gespeichert werden.
- **Redteam:** Screenshots sind schwer durchsuchbar und können private Inhalte vollständig zeigen.
- **Verbesserung:** Opt-in, viewportbezogen, mit Retention und gleicher Filter-/Policy-ID wie DOM.
- **Kriterium:** Screenshot und DOMchunk sind über `chunk_id` und Zeitfenster verbunden.

### 22. Policy-Sperre während des Laufs

- **Idee:** Während eines Scans ist die Policy sichtbar; Änderungen erzeugen eine neue Policyversion.
- **Redteam:** Ein nachträglicher Schalterwechsel macht das Ergebnis uneindeutig.
- **Verbesserung:** Aktuellen Chunk sauber abschließen, neue Generation beginnen, niemals rückwirkend umdeuten.
- **Kriterium:** Jeder Chunk trägt exakt eine unveränderliche Policyversion.

### C. Sichtbarer Inhalt und semantische Struktur — Ideen 23–33

### 23. Semantischer Lesebaum

- **Idee:** Der Export erhält Überschriften, Absätze, Listen, Tabellen, Code und Zitate als Struktur statt nur als Text.
- **Redteam:** DOM-Struktur ist oft voller Layoutwrapper.
- **Verbesserung:** Semantische Projektion plus Rohstrukturhash; Wrapper werden nur entfernt, wenn Provenienz erhalten bleibt.
- **Kriterium:** Ein semantischer Diff kann Überschriften- und Blockreihenfolge vergleichen.

### 24. Sichtbarkeitsprüfung ohne Klonfehler

- **Idee:** Sichtbarkeit wird am Original gemessen, erst danach wird ein Clone sanitisiert.
- **Redteam:** Geometrie am Clone ist leer und würde alles löschen.
- **Verbesserung:** Original-/Clone-Knoten werden positionsbezogen gekoppelt; `aria-hidden` wird zusätzlich berücksichtigt.
- **Kriterium:** Fixture mit sichtbarem Inhalt bleibt nach Sanitizing in gleicher Blockzahl erhalten.

### 25. Renderstabilität

- **Idee:** Zwei oder mehr aufeinanderfolgende Snapshots müssen stabil sein, bevor ein Chunk gezählt wird.
- **Redteam:** Animierte Werbung verhindert Stabilität.
- **Verbesserung:** Bekannte Animationen werden als volatile Zonen markiert; Text-/Strukturhash entscheidet separat.
- **Kriterium:** Ein stabiler Lesekörper kann trotz dekorativer Animation abgeschlossen werden.

### 26. Textvarianten erhalten

- **Idee:** Rohtext, lesefreundlich normalisierter Text und sichtbare Zeilenstruktur werden parallel gespeichert.
- **Redteam:** Normalisierung verschluckt echte Zeilenumbrüche oder Codeformatierung.
- **Verbesserung:** Normalisierungsversion und Quellblockhash bleiben neben jeder Projektion.
- **Kriterium:** Markdown kann aus Roh-/Strukturfeldern reproduziert werden.

### 27. Tabellenqualität

- **Idee:** Tabellenköpfe, Spalten, Zeilen, Caption und responsive Scrollbereiche werden bewahrt.
- **Redteam:** Eine mobile Tabelle kann im DOM spaltenweise statt zeilenweise vorliegen.
- **Verbesserung:** Original-HTML plus normalisierte Tabellenansicht mit Warnung bei Rekonstruktion.
- **Kriterium:** Jede rekonstruierte Tabelle trägt `reconstructed: true`.

### 28. Code und Preformatted-Inhalt

- **Idee:** Codeblöcke behalten Sprache, Whitespace, Zeilennummern und Copytext.
- **Redteam:** Syntaxhighlighting enthält duplizierte Tokenknoten.
- **Verbesserung:** Textquelle und Darstellung trennen; Tokenmarkup nur als optionale Projektion.
- **Kriterium:** Code-Text wird nicht durch Highlightwrapper verdoppelt.

### 29. Eingeklappte Bereiche

- **Idee:** Geschlossene Bereiche werden als sichtbar vorhanden, aber nicht vollständig gelesen markiert.
- **Redteam:** Der Nutzer will gerade den Inhalt und erwartet „alles“.
- **Verbesserung:** Passiver Öffnungsvorschlag pro Control; nur nach Freigabe öffnen und separat messen.
- **Kriterium:** `collapsed_unread` verhindert `complete` für die entsprechende Inhaltsklasse.

### 30. Shadow DOM und Web Components

- **Idee:** Sichtbarer Shadow-Content wird, soweit browserseitig zugänglich, als eigene Schicht erfasst.
- **Redteam:** Geschlossene Shadow Roots und Custom Elements sind nicht zuverlässig lesbar.
- **Verbesserung:** offen/geschlossen/unbekannt unterscheiden und den Host als Herkunft erhalten.
- **Kriterium:** Unzugänglicher Shadow-Content wird als Lücke statt als leerer Bereich markiert.

### 31. Canvas und SVG

- **Idee:** SVG-Struktur, sichtbare Beschriftungen und optionaler Screenshot werden getrennt gesichert.
- **Redteam:** Canvas enthält keine zugängliche Textstruktur.
- **Verbesserung:** Pixelbeleg nur opt-in; fehlende Semantik als `visual_only` deklarieren.
- **Kriterium:** Kein Pixelbild wird als maschinenlesbarer Text ausgegeben.

### 32. Iframes

- **Idee:** Iframes werden standardmäßig als Rahmen, URL und sichtbare Einbettungsmetadaten erfasst.
- **Redteam:** Cross-Origin-Inhalte können nicht sicher oder nicht erlaubt gelesen werden.
- **Verbesserung:** Same-Origin-Iframes nur mit eigener Origin-/Policyfreigabe, Cross-Origin höchstens Referenz.
- **Kriterium:** Kein iframe-Inhalt erscheint ohne eigenen Herkunfts- und Freigabenachweis.

### 33. Leserichtung und Sprache

- **Idee:** `lang`, dir, Hauptsprache und Leserichtung werden pro Snapshot ermittelt.
- **Redteam:** Mehrsprachige Seiten werden zu einem falschen Sprachlabel verdichtet.
- **Verbesserung:** Dokument-, Abschnitts- und Unsicherheitswerte getrennt speichern.
- **Kriterium:** Export kann gemischte Sprachabschnitte markieren statt sie zu überschreiben.

### D. Links, Navigation und Seitenbeziehungen — Ideen 34–44

### 34. Linkinventar mit sichtbarem Text

- **Idee:** Jeder sichtbare Link wird mit Text, Ziel, rel, Position und Quellchunk gespeichert.
- **Redteam:** Gleiche Links in Navigation und Inhalt werden unübersichtlich doppelt.
- **Verbesserung:** Vorkommen behalten, zusätzlich kanonisches Linkinventar mit Zählung führen.
- **Kriterium:** Export kann sowohl „alle Vorkommen“ als auch „einmalige Ziele“ zeigen.

### 35. Linkziel- und Originregel

- **Idee:** Interne Ziele kommen in die Crawlqueue; externe Ziele bleiben Referenzen, sofern nicht freigegeben.
- **Redteam:** Relative URLs und Subdomains werden falsch als intern klassifiziert.
- **Verbesserung:** URL-Resolver, Originklasse und Nutzer-Allowlist getrennt berechnen.
- **Kriterium:** Jede Queueaufnahme nennt die Regel, die sie erlaubt hat.

### 36. Query-Parameterprofil

- **Idee:** Parameter können behalten, entfernen, normalisieren oder als Varianten gruppiert werden.
- **Redteam:** Entfernen kann echte Filterseiten zusammenlegen.
- **Verbesserung:** Parameterklassifikation `tracking`, `content`, `unknown` mit Vorschau und Erhalt der Roh-URL.
- **Kriterium:** Unknown-Parameter werden nicht automatisch entfernt.

### 37. Fragment- und Ankerbeziehungen

- **Idee:** Hashziele werden als Seitenanker im Offline-HTML erhalten.
- **Redteam:** Hashnavigation kann auf fehlende oder gefilterte IDs zeigen.
- **Verbesserung:** ID-Inventar und gebrochene Anker im Qualitätsbericht.
- **Kriterium:** Jeder interne Fragmentlink ist `resolved`, `unresolved` oder `external`.

### 38. Sitemap als beobachteter Graph

- **Idee:** Seiten, Links, Parent-Links und Tiefe bilden einen crawlbaren Graphen.
- **Redteam:** Ein Linkgraph ist nicht automatisch Beweis, dass der Zielinhalt gelesen wurde.
- **Verbesserung:** Kantenstatus `seen`, `queued`, `captured`, `blocked`, `filtered`.
- **Kriterium:** Eine Graphkante behauptet nie mehr als ihren Status.

### 39. Navigation ohne Aktionsausführung

- **Idee:** Normale Links dürfen zum nächsten Crawlziel navigieren; Formsubmit, Kauf und Mutation nicht.
- **Redteam:** Ein Link kann trotzdem eine schreibende URL-Aktion auslösen.
- **Verbesserung:** Safe-navigation-Regeln, methodenlose GET-Prüfung, Blockliste für bekannte Aktionsmuster.
- **Kriterium:** Verdächtige Ziele werden nicht automatisch geöffnet.

### 40. Linkkontext

- **Idee:** Linktext, umgebender Absatz, Überschrift und Position helfen beim späteren Lesen.
- **Redteam:** Kontext kann private oder werbliche Nachbarschaft mitschleppen.
- **Verbesserung:** Kontext optional, mit derselben Sichtbarkeits- und Filterpolicy.
- **Kriterium:** Linkkontext ist separat abschaltbar.

### 41. Breadcrumbs und Seitentitel

- **Idee:** Titel, Breadcrumb, Canonical und Hauptnavigation werden als Seitenidentität bewahrt.
- **Redteam:** Werbetitel oder dynamische Titel sind nicht stabil.
- **Verbesserung:** Roh- und normalisierter Titel, Zeitpunkt und DOM-Quelle parallel.
- **Kriterium:** Seitenidentität verwendet nicht nur den Titel.

### 42. Defekte Links sichtbar halten

- **Idee:** Nicht erreichbare oder blockierte Ziele bleiben im Offline-Atlas als defekte Kante.
- **Redteam:** Fehlerseiten könnten den Atlas mit Müll füllen.
- **Verbesserung:** Zielstatus und Fehlerklasse anzeigen, Inhalt nur bei eigener Policy speichern.
- **Kriterium:** Defektes Ziel wird nicht als erfolgreich gelesen gezählt.

### 43. Endlosschleifen im Linkgraph

- **Idee:** URL-/Inhaltsfingerprints verhindern wiederholte Seiten.
- **Redteam:** Fingerprintkollisionen können echte Varianten verschlucken.
- **Verbesserung:** Kanonische URL, Roh-URL-Varianten und Strukturhash gemeinsam speichern.
- **Kriterium:** Zusammenlegung ist reversibel nachvollziehbar.

### 44. Navigationstreue im Offline-HTML

- **Idee:** Interne Links zeigen auf entsprechende Offline-Seiten; externe Links öffnen online in neuem Tab.
- **Redteam:** Relative Pfade brechen bei verschachtelten Exportordnern.
- **Verbesserung:** Ein zentraler Offline-Router mappt stabile Page-IDs und erhält Originalziele.
- **Kriterium:** Jeder umgeschriebene Link trägt Originalziel und Offlineziel.

### E. Bilder, Medien und Assets — Ideen 45–55

### 45. Sichtbares Bildregister

- **Idee:** Bildquelle, Alttext, Maße, Position, Lazy-Load-Status und Kontext werden erfasst.
- **Redteam:** Ein `src` kann Platzhalter sein, während `data-src` das echte Bild enthält.
- **Verbesserung:** Nur sichtbare, erlaubte Kandidaten aus mehreren Quellen sammeln und Herkunft markieren.
- **Kriterium:** Platzhalter und echte Quelle bleiben unterscheidbar.

### 46. Lazy-Load-Nachladen durch sichtbares Scrollen

- **Idee:** Der Chunkscan gibt Lazy-Assets Gelegenheit, sichtbar zu werden.
- **Redteam:** Unbegrenztes Nachladen kann unbemerkt ein Asset-Crawl werden.
- **Verbesserung:** Nur viewportnahe, sichtbare Assets mit Warte- und Größenlimit.
- **Kriterium:** Assetaufnahme ist an einen beobachteten Chunk gebunden.

### 47. Asset-Manifest statt blindem Einbetten

- **Idee:** Jedes Asset erhält Referenz, Mime, Bytes, Hash, Quelle und Captureentscheidung.
- **Redteam:** Ein großes Manifest wird selbst unlesbar.
- **Verbesserung:** Kompakte Übersicht plus maschinenlesbare Detaildatei.
- **Kriterium:** HTML, JSON und Manifest verweisen auf dieselbe Asset-ID.

### 48. Größen- und Mengenbudgets

- **Idee:** Pro Asset, Seite und Job gibt es Bytes-, Anzahl- und Laufzeitbudgets.
- **Redteam:** Kleine Budgets schneiden wichtige Hauptbilder ab.
- **Verbesserung:** Priorität nach Sichtbarkeit, semantischem Kontext, Dimensionen und Nutzerprofil.
- **Kriterium:** Budgetentscheidungen erklären sich aus einer gespeicherten Priorität.

### 49. Bildformate und Transcodierung

- **Idee:** PNG/JPEG/WebP/SVG werden erkannt; Transcodierung ist optional.
- **Redteam:** Transcodierung verändert Beweisbytes und Qualität.
- **Verbesserung:** Originalhash bewahren, abgeleitete Offlinekopie als neue Artefaktversion markieren.
- **Kriterium:** Original und Derivat sind nie dieselbe Datei-ID.

### 50. Poster und Untertitel

- **Idee:** Bei Video werden Poster, sichtbarer Titel und Untertitelspuren bevorzugt übernommen.
- **Redteam:** Untertitel können fremde Inhalte oder Tracking-URLs enthalten.
- **Verbesserung:** Textspuren sanitizen und als eigene Quelle mit URL/Hash ablegen.
- **Kriterium:** Untertitel sind optional und niemals still aus Player-Interna extrahiert.

### 51. CSS-Bildreferenzen

- **Idee:** Sichtbare Hintergrundbilder können über bereinigtes CSS referenziert werden.
- **Redteam:** CSS kann riesige Sprite- oder Trackingflächen enthalten.
- **Verbesserung:** Nur sichtbare, begrenzte URLs und keine `url()`-Kaskade ohne Policy.
- **Kriterium:** Jede CSS-Assetquelle nennt Regel und sichtbaren Bezug.

### 52. Icons und Favicons

- **Idee:** Favicon, sichtbare Icons und SVG-Symbole erhalten eine eigene kleine Klasse.
- **Redteam:** UI-Icons überwiegen den redaktionellen Inhalt.
- **Verbesserung:** Standardprofil katalogisiert nur; Archiv-/Designprofil darf einbetten.
- **Kriterium:** Iconmenge wird getrennt von redaktionellen Bildern gemeldet.

### 53. Medien ohne Abspielversprechen

- **Idee:** Offline-HTML zeigt bei nicht kopierten Medien Quelle und Capturegrund statt einen kaputten Player.
- **Redteam:** Nutzer hält eine Referenz für eine lokale Kopie.
- **Verbesserung:** UI-Badge `online-referenz`, `lokal`, `blockiert` im Export.
- **Kriterium:** Kein Offline-Player behauptet Funktionsfähigkeit ohne lokale Ressource.

### 54. Asset-Fehler und Retry

- **Idee:** Temporäre Ladefehler können pro Asset begrenzt wiederholt werden.
- **Redteam:** Retries halten einen Crawl endlos fest.
- **Verbesserung:** Exponentielles kleines Retryfenster, danach sichtbarer Fehlerstatus.
- **Kriterium:** Retryanzahl und letzte Ursache stehen im Manifest.

### 55. Medienrechte- und Datenschutzflag

- **Idee:** Assetkopien tragen einen Hinweis auf Quelle und Capturemodus, nicht eine rechtliche Freigabe.
- **Redteam:** Ein Hinweis könnte als Lizenzbehauptung missverstanden werden.
- **Verbesserung:** Technisches Provenienzflag ohne Rechtsurteil; Nutzer entscheidet über Verwendung.
- **Kriterium:** Export sagt „Quelle erfasst“, nie „Nutzung erlaubt“.

### F. Werbung, Tracker, Müll und private Daten — Ideen 56–66

### 56. Werbefilter als Policy, nicht als Löschmagie

- **Idee:** Werbung wird über Signale erkannt und standardmäßig ausgeschlossen.
- **Redteam:** Redaktionelle Inhalte können `sponsor` oder `ad` im Namen tragen.
- **Verbesserung:** Trefferklassen `obvious_ad`, `likely_ad`, `unknown`; nur `obvious_ad` defaultmäßig entfernen.
- **Kriterium:** Jeder Ausschluss hat Signalbelege und kann im Review wieder aktiviert werden.

### 57. Ausschlussbuch für Werbung

- **Idee:** Ausgeschlossene Knoten bleiben mit Selector/Tag, Textfingerprint, URL und Grund im Audit.
- **Redteam:** Das Ausschlussbuch kann selbst sensitive Werbetexte speichern.
- **Verbesserung:** Minimierter Fingerprint, optional gekürzter Text und gleiche Retentionpolicy.
- **Kriterium:** Audit beweist Ausschluss ohne unnötige Vollkopie.

### 58. Trackerpixel-Filter

- **Idee:** Unsichtbare 1x1-Bilder, Beacon-URLs und Pixel ohne semantischen Kontext werden standardmäßig nicht übernommen.
- **Redteam:** Kleine Logos oder Statuspunkte können legitim sein.
- **Verbesserung:** Sichtbarkeit, Alttext, Kontext und Dimension gemeinsam bewerten.
- **Kriterium:** `1x1` allein genügt nie für einen Ausschluss.

### 59. Cookie- und Consent-Layer

- **Idee:** Banner und Consent-Overlays sind standardmäßig Noise; der Inhalt darunter wird nicht heimlich freigeschaltet.
- **Redteam:** Ohne Consent bleibt der Hauptinhalt unsichtbar.
- **Verbesserung:** `blocked_by_consent` statt automatischer Zustimmung; manuelle Freigabe danach erlaubt neuen Chunk.
- **Kriterium:** Der Recorder speichert keine Einwilligung als eigene Handlung.

### 60. Newsletter-/Signup-/Modalfilter

- **Idee:** Popups, Newsletter und dauerhafte Overlays werden als optionale Dekorations-/Noiseklasse erkannt.
- **Redteam:** Ein Modal kann den eigentlichen Artikel enthalten.
- **Verbesserung:** Modal mit semantischem Inhalt wird als `review_required` behalten, nicht blind entfernt.
- **Kriterium:** Popupfilter nutzt Inhalt und Z-Index/Position gemeinsam.

### 61. Navigations- und Footerfilter

- **Idee:** Wiederholte Navigation, Footerlinks und Socialleisten können vom Lesekörper getrennt werden.
- **Redteam:** Navigation ist für Offline-Lesbarkeit und Seitenbeziehungen wichtig.
- **Verbesserung:** Im HTML optional ausblenden, im Linkgraph und Seitenmetadaten trotzdem erhalten.
- **Kriterium:** „Nicht im Lesekörper“ bedeutet nicht „aus Provenienz gelöscht“.

### 62. Doppelte Karten und Feed-Müll

- **Idee:** Identische sichtbare Karten oder wiederholte Empfehlungen werden dedupliziert.
- **Redteam:** Wiederholung kann zeitliche oder redaktionelle Bedeutung tragen.
- **Verbesserung:** Nur identische aufeinanderfolgende Darstellungen deduplizieren; Vorkommen zählen.
- **Kriterium:** Der Export zeigt `occurrences` und die Deduplikationsregel.

### 63. Trackerparameter und Referrer

- **Idee:** Bekannte Trackingparameter werden aus Offlinezielen entfernt oder separat markiert.
- **Redteam:** Ein Parameter kann für den eigentlichen Inhalt nötig sein.
- **Verbesserung:** Bekannte Liste, unbekannt bleibt erhalten, Rohziel bleibt auditierbar.
- **Kriterium:** Kein Parameter wird allein wegen unbekannter Schreibweise gelöscht.

### 64. Private Daten in sichtbarem Inhalt

- **Idee:** Nutzer kann PII-/Secret-Muster im Export maskieren.
- **Redteam:** Automatische Maskierung zerstört Artikeltext und Beweiswert.
- **Verbesserung:** Erkennungsstufen, Vorschau und pro Tab bestätigte Maskierung; Rohsnapshot nur lokal geschützt.
- **Kriterium:** Maskierung ist als Transformation versioniert und nicht als „Original“ ausgegeben.

### 65. Bekannte Müllsignale als lernende Regel

- **Idee:** Klassifikator lernt aus bestätigten Filterentscheidungen eines Nutzers.
- **Redteam:** Ein falsch bestätigter Treffer wirkt auf spätere Seiten.
- **Verbesserung:** Lernen nur als lokales, versioniertes Vorschlagsmodell; nie direkt löschend.
- **Kriterium:** Jede gelernte Regel kann pro Site/Profil zurückgenommen werden.

### 66. Filtervorschau pro Tab

- **Idee:** Vor dem langen Crawl zeigt eine Vorschau „würde behalten / würde ausblenden / unsicher“.
- **Redteam:** Preview und späterer dynamischer Zustand können auseinanderlaufen.
- **Verbesserung:** Preview ist eigener Snapshot mit Zeit und begrenztem Gültigkeitsfenster.
- **Kriterium:** Der Scan meldet Änderungen gegenüber der Preview ausdrücklich.

### G. Scrollen, Virtualisierung und tabweise 0–100 % — Ideen 67–77

### 67. Echter Scrollsurface-Finder

- **Idee:** Der Recorder findet pro Seite den tatsächlich scrollenden sichtbaren Container.
- **Redteam:** Größter Container ist nicht immer der Lesekörper.
- **Verbesserung:** Kandidaten nach Sichtbarkeit, Scrollbewegung, Inhalt und Stabilität bewerten.
- **Kriterium:** Der gewählte Surface steht mit Geometrie und Auswahlgrund im Manifest.

### 68. 70-Prozent-Schritt mit mindestens 30 Prozent Überlappung

- **Idee:** Jeder Chunk bewegt sich höchstens 70 Prozent der frisch gemessenen Viewporthöhe.
- **Redteam:** Dynamisches Nachladen verändert die Maximalhöhe und erzeugt Sprünge.
- **Verbesserung:** Vorher-/Nachher-Metrik, reale Position und Überlappung je Übergang speichern.
- **Kriterium:** Kein Übergang unter 0,30 wird als bestätigt gezählt.

### 69. 0–100-Prozent-Anzeige pro logischer Seite

- **Idee:** Jeder Tab zeigt eigenen Fortschritt, Chunkzahl, Höhe und Status.
- **Redteam:** Prozent ist bei dynamischem Wachstum nur eine Schätzung.
- **Verbesserung:** `progress_estimate` und `end_sentinel` getrennt; 100 Prozent erst am stabilen Ende.
- **Kriterium:** 100 Prozent ohne End-Sentinel ist unmöglich.

### 70. Lazy-Load-Wachstum erkennen

- **Idee:** Steigt `scrollHeight` beim Scrollen, wird der Fortschritt neu berechnet.
- **Redteam:** Eine Seite wächst endlos durch Empfehlungen.
- **Verbesserung:** Wachstumslimit, Stagnationsfenster und `dynamic_end_unproven`.
- **Kriterium:** Endloswachstum endet in `partial` oder Nutzerstopp, nicht in grünem `complete`.

### 71. Chunk als unveränderliches Beweisstück

- **Idee:** Jeder Chunk enthält top, max, viewport, DOMhash, Inhaltsklassen, Filterreport und Zeit.
- **Redteam:** Vollständige HTMLkopien vervielfachen Speicher.
- **Verbesserung:** Deduphash, Referenzen und begrenzte Chunkpayload; Metadaten bleiben vollständig.
- **Kriterium:** Ein wiederholter Chunk ist als Wiederholung belegbar, ohne blind doppelt zu speichern.

### 72. Sichtfenster und Seitensnapshot trennen

- **Idee:** Chunks beweisen die Lesebewegung; der abschließende Seitensnapshot dient dem Export.
- **Redteam:** Endsnapshot kann frühere Zustände überschreiben.
- **Verbesserung:** Endsnapshot hat eigene Generation und verweist auf alle Chunks.
- **Kriterium:** Export kann die Beweiskette auch ohne Endsnapshot als unvollständig anzeigen.

### 73. Virtualisierte Knoten beobachten

- **Idee:** Knoten werden über IDs, Text-/Strukturhash und Kontext wiedererkannt, auch wenn sie aus dem DOM verschwinden.
- **Redteam:** Provider-IDs können recycelt werden.
- **Verbesserung:** Mehrsignalidentität und `identity_ambiguous` statt Zwangsdeduplikation.
- **Kriterium:** Recycelte IDs erzeugen keine stille Überschreibung.

### 74. Stopp jederzeit und sichtbar

- **Idee:** Der Nutzer kann den gesamten Job oder eine einzelne Seite stoppen.
- **Redteam:** Stoppen während Asset-/DB-Schreibvorgang lässt halbe Daten zurück.
- **Verbesserung:** kooperativer Stop, atomarer Chunkcommit, danach `stopped` mit letztem Checkpoint.
- **Kriterium:** Kein Stop löscht den letzten gültigen Chunk.

### 75. Einzelne Seite wiederholen

- **Idee:** Eine fehlerhafte Seite kann mit neuer Generation erneut gescannt werden.
- **Redteam:** Wiederholung verschleiert die erste Fehlerspur.
- **Verbesserung:** Seitenversionen nebeneinander, Auswahl einer kanonischen Exportversion erst nach Review.
- **Kriterium:** Alte Seite bleibt im Jobarchiv erhalten.

### 76. Endmarker und Gründe

- **Idee:** Ende kann DOM-Rand, Stagnation, Seitenmarker, Timeout oder Nutzerstopp sein.
- **Redteam:** Stagnation ist nicht zwingend ein echtes Ende.
- **Verbesserung:** Endgrund mit Belegstärke; nur echte und stabile Marker erlauben `complete`.
- **Kriterium:** `stagnation` bleibt mindestens `partial`.

### 77. Scroll- und DOM-Replay

- **Idee:** Ein Lauf kann mit URL, Policy und Scrollplan reproduziert werden.
- **Redteam:** Dynamische Seiten sind nicht deterministisch.
- **Verbesserung:** Replay markiert Abweichungen und erzeugt neue Generation statt zu überschreiben.
- **Kriterium:** Replay ist Vergleich, nicht nachträgliche Reparatur der Originalbeweise.

### H. Queue, Speicher, Export und Qualitätsbetrieb — Ideen 78–88

### 78. Unbegrenzte logische Seitenqueue

- **Idee:** „Quasi unendlich viele Tabs“ wird als unbeschränkte, persistente URLqueue verstanden.
- **Redteam:** Eine unbounded Queue kann Speicher und Zeit endlos binden.
- **Verbesserung:** Kein künstliches 30-Seiten-Limit, aber Nutzerbudget, Originbudget, Pausen und Backpressure.
- **Kriterium:** Queue kann wachsen, Jobstatus zeigt jederzeit verbleibende und begrenzende Budgets.

### 79. Begrenzter wiederverwendbarer Tabpool

- **Idee:** Wenige echte Browser-Tabs arbeiten nacheinander viele logische Seiten ab.
- **Redteam:** Daniel möchte jede Seite als eigenen Tab sehen.
- **Verbesserung:** `visible_tab_mode` optional; Standard ist Ressourcenpool, Audit bewahrt trotzdem jeden logischen Tab-/Slotdatensatz.
- **Kriterium:** Tab-ID-Wiederverwendung wird nicht mit Seiten-ID vermischt.

### 80. Tabfenster-Archivmodus

- **Idee:** Bei kleinen Jobs können alle fertig gescannten Seiten als eigene Tabs offen bleiben.
- **Redteam:** 30 oder 300 echte Tabs machen Chromium unbrauchbar.
- **Verbesserung:** Schwellenwert, Tabpark, automatische Ruhe-/Suspendstrategie und Warnung vor Ressourcenlast.
- **Kriterium:** „Alle Tabs offen“ ist bewusste Option, nie stiller Standard.

### 81. Persistente Queue in IndexedDB

- **Idee:** Queue, Slots, Chunks und Fehler überleben Service-Worker-Schlaf.
- **Redteam:** Parallel laufende Worker können denselben Slot doppelt nehmen.
- **Verbesserung:** Lease, Generation, monotone Sequenz und idempotenter Commit.
- **Kriterium:** Jede URL hat höchstens einen aktiven Lease.

### 82. Speicherklassen

- **Idee:** Manifest, Chunkmetadaten, HTML, Assets und Logs besitzen getrennte Retention- und Kompressionsregeln.
- **Redteam:** Kompression erschwert lokale Diagnose.
- **Verbesserung:** Lesbares Manifest, komprimierte große Payloads, reproduzierbarer Hash über dekomprimierte Bytes.
- **Kriterium:** Diagnose bleibt ohne proprietäres Werkzeug möglich.

### 83. Offline-Atlas mit Chunkkarte

- **Idee:** Offline-HTML zeigt Seitenbaum, Filterbericht, Linkgraph und auswählbare Chunks.
- **Redteam:** Ein Atlas mit vielen Inlinechunks wird riesig.
- **Verbesserung:** Standardansicht Endsnapshot, Chunks lazy aus lokalen Daten; Größenwarnung und Teil-Export.
- **Kriterium:** Chunkkarte zeigt Abdeckung und Originaltop, ohne 100-fache Kopie zu erzwingen.

### 84. HTML-, Markdown-, JSON- und Assetexport

- **Idee:** Jede Sicht projiziert denselben kanonischen Datensatz in passende Formate.
- **Redteam:** Vier Exporte entwickeln voneinander abweichende Wahrheiten.
- **Verbesserung:** Gemeinsames kanonisches Manifest plus Exportadapter und semantischer Crosscheck.
- **Kriterium:** Alle Formate tragen dieselbe `page_version`, Policy und Status.

### 85. Lokaler Exporthash und VPS-Siegel

- **Idee:** Exportbytes werden lokal und serverseitig gehasht und gegeneinander geprüft.
- **Redteam:** Hashgleichheit sagt nicht, ob Inhalt vollständig ist.
- **Verbesserung:** Hash ist nur Bytegleichheitsgate; Vollständigkeit bleibt eigener Beweisstatus.
- **Kriterium:** Kein Hash wird als Inhaltsvollständigkeit ausgegeben.

### 86. Qualitätsbericht statt grüner Erfolgsphrase

- **Idee:** Report nennt Seiten, Chunks, Filter, Assets, Links, Lücken, Fehler und Grenzen.
- **Redteam:** Nutzer ertrinkt in Diagnosedaten.
- **Verbesserung:** Kurzstatus plus aufklappbare Beweiskarte und maschinenlesbarer Report.
- **Kriterium:** Jede Warnung hat eine konkrete nächste Aktion.

### 87. AI-Provider-Regressionsmatrix

- **Idee:** ChatGPT und Claude werden nach jeder gemeinsamen Kernänderung mit sichtbaren eigenen Tests geprüft; Gemini/Grok folgen getrennt.
- **Redteam:** Ein Crawlfix kann Chatsemantik oder Scrolllogik beschädigen.
- **Verbesserung:** Gate-Matrix für Normalaufnahme, Snapshot, Link-/Medienprojektion und Crawl getrennt.
- **Kriterium:** Kein Crawlcommit gilt als grün, wenn ChatGPT-/Claude-Smokes rot sind.

### 88. Externe unabhängige Lesbarkeitsprüfung

- **Idee:** Ein read-only Comparator öffnet den Export erneut und prüft DOM, Links, Medienstatus, Filter und Status.
- **Redteam:** Der Export prüft sich sonst mit derselben fehlerhaften Logik selbst.
- **Verbesserung:** Zweite, kleinere Prüfschicht mit absichtlich anderer Implementierung und Negativtests.
- **Kriterium:** Ein synthetisch fehlendes Bild, Link oder Chunk wird vom Comparator erkannt.

## Sofortige Synthese aus den 88 Ideen

Die beste gemeinsame Form ist kein „unendlich viele Tabs offen“-Mechanismus. Sie ist ein **unbegrenzter logischer Seitenatlas mit begrenztem Browser-Tabpool**, optional ergänzt durch einen sichtbaren Tabpark für kleine Läufe. Jede logische Seite hat ihren eigenen 0–100-Prozent-Verlauf, ihre eigene Policy, ihre eigene Generation, ihren eigenen Filterbericht und ihre eigenen Chunks. Dadurch profitieren normale Websites und AI-Websites vom gemeinsamen Snapshot-/Exportkern, ohne dass ChatGPT oder Claude ihre Providersemantik verlieren.

Werbung wird nicht nach Bauchgefühl aus dem HTML radiert. Der Recorder führt drei parallele Wahrheiten: den bereinigten Lesekörper, das Ausschlussbuch und den Roh-/Strukturfingerprint des sichtbaren Ausgangs. So kann der Nutzer pro Tab anklicken, was er möchte, und später nachvollziehen, was bewusst nicht in den Lesekörper gelangte.

## 22 Red-Team-Runden über alle 88 Ideen

Diese 22 Runden sind konzeptionelle Gegenprüfungen. Sie sind keine Behauptung, dass 22 vollständige Browserläufe stattgefunden haben. Jede Runde greift die bis dahin beste Fassung an und schreibt die überlebende Regel fest.

| Runde | Angriffsschwerpunkt | Schwachstelle | Verbesserung, die bleibt | Restunsicherheit |
|---:|---|---|---|---|
| 1 | Auftragstrennung | Ein Crawl startet aus einer normalen Aufnahme heraus. | Eigene Crawl-Job-ID, eigener Button und eigener Statusautomat. | Panelzustand muss noch live getestet werden. |
| 2 | Nutzerfreigabe | „Alles“ wird als pauschale Erlaubnis missverstanden. | Effective Policy pro Tab mit sichtbarer Zusammenfassung. | Viele Optionen brauchen Presets. |
| 3 | Sichtbarkeitsgrenze | DOM-Daten werden mit internen Providerdaten verwechselt. | Nur gerenderte, sichtbare Projektion; Provideradapter bleiben separat. | Shadow DOM und Canvas bleiben partiell. |
| 4 | Werbung | Ein Adselector entfernt redaktionellen Inhalt. | Drei Klassen, Ausschlussbuch und Review für Unsicherheit. | Klassifikation bleibt heuristisch. |
| 5 | Tracker | Kleine echte Icons werden als Pixel gelöscht. | Kontext, Maße, Alttext und Sichtbarkeit gemeinsam prüfen. | Seitenspezifische Sonderfälle. |
| 6 | Consent | Automatisches Wegklicken fälscht Nutzerhandlung. | `blocked_by_consent`, manuelle Freigabe, neue Generation. | Ein Nutzer kann unklar entscheiden. |
| 7 | Layout | 1:1-Design konserviert Müll und aktive Ressourcen. | Lesekörper, faithful-visible und semantic als getrennte Projektionen. | CSS-Reproduktion ist nie universell. |
| 8 | Links | Interne/externe Ziele werden zu aggressiv zusammengelegt. | Rohziel, kanonisches Ziel und Originentscheidung parallel. | Query-Semantik bleibt domainabhängig. |
| 9 | Medien | Große Assets machen den Atlas unbrauchbar. | Sichtbare Priorität, Budget, Referenz-vs-Kopie und Hash. | Rechte-/Nutzungsfrage bleibt außerhalb des Tools. |
| 10 | Virtualisierung | Endposition wird mit Vollständigkeit verwechselt. | Überlappende Chunks, Endmarker, Wachstumssignale und Lückenstatus. | Manche Feeds haben keinen echten Endmarker. |
| 11 | Tabzahl | 30 Tabs werden durch „unendlich“ ersetzt und erschöpfen Chromium. | Unbegrenzte logische Queue, begrenzter Pool, sichtbarer Tabpark optional. | Ressourcenbudget muss UI-seitig gut erklärt werden. |
| 12 | Worker-Schlaf | In-Memory-Queue verliert den Lauf. | IndexedDB-Checkpoint plus Lease und Generation. | Recovery nach hartem Browserabsturz braucht Smoke-Test. |
| 13 | Deduplizierung | Wiederholte Inhalte werden fälschlich gelöscht. | Aufeinanderfolgende identische Sichtungen zusammenfassen, Vorkommen zählen. | Recycelte Provider-IDs bleiben schwierig. |
| 14 | Filtertransparenz | „Müll“ verschwindet ohne Beleg. | Ausschlussbuch mit kompakter Provenienz und Wiederherstellbarkeit. | Ausschlussbuch darf nicht selbst Datenleck werden. |
| 15 | Datenschutz | Sichtbare Login-/Formdaten landen im Snapshot. | Forms/Werte default off, Maskierung versioniert, keine Secrets. | PII-Erkennung kann Fehlklassifikationen haben. |
| 16 | Interaktion | „Mehr anzeigen“ verändert die Seite und startet Aktionen. | Passive Control-Whitelist, Vorher-/Nachher-Snapshot, manuelle Bestätigung. | Komplexe Webapps bleiben teils `blocked`. |
| 17 | Offline-Navigation | Exportlinks zeigen auf falsche relative Pfade. | Page-ID-Router mit Originalziel und Offlineziel. | Dynamische Router brauchen Fixture-Matrix. |
| 18 | Exportwahrheit | HTML, MD und JSON erzählen unterschiedliche Stände. | Kanonisches Manifest, Adapterexporte und Crosscheck. | Große Inline-HTMLs brauchen Lazy-Loading. |
| 19 | Fehlerstatus | Ein roter Fehler stoppt den ganzen Atlas. | Seite/Asset/Chunk individuell klassifizieren; Job kann partial weiterlaufen. | Nutzer muss Teilresultate verstehen. |
| 20 | AI-Regression | Crawländerung bricht ChatGPT-/Claude-Import. | Separate Normal-/Crawl-Gates und Pflicht-Smokes für ChatGPT/Claude. | Browser-Versionen können zusätzlich driften. |
| 21 | Selbstprüfung | Dieselbe Capturelogik bestätigt sich selbst. | Read-only Comparator mit anderer Implementierung und Mutationstests. | Comparator muss bewusst kleiner bleiben. |
| 22 | Überversprechen | „Perfekte Kopie“ überdeckt Grenzen. | Exportkopf nennt Policy, Projektion, Filter, Lücken, Assets und Endgrund. | Marketing-/UI-Texte müssen diese Sprache ebenfalls einhalten. |

## Zwischenfassung nach 22 Runden

Die 88 Ideen überleben nur gemeinsam mit drei Anzeigen: **Was wurde aufgenommen? Was wurde bewusst ausgeschlossen? Was konnte nicht bewiesen werden?** Das ist der Kern des Gesamtauftrags. Eine zusätzliche Tabzahl ist dagegen kein Qualitätsmerkmal. Qualität entsteht aus logischen Seiten-IDs, stabilen Chunks, einer gespeicherten Policy und einem reproduzierbaren Status.

## 33 sokratische Fragen zur Einfügung in das Konzept

Jede Frage wird einzeln beantwortet. Danach folgt ein erster Angriff (`RT1`), eine erste Verbesserung, ein zweiter Angriff (`RT2`) und eine zweite Verbesserung. Die Fragen sind absichtlich so gestellt, dass sie das Konzept an seinen eigenen Voraussetzungen prüfen.

### Frage 1 — Was genau soll „alles“ heißen?

- **Einbau:** Alles sichtbare, durch Policy freigegebene und technisch stabil beobachtbare; nicht versteckte Daten.
- **RT1:** „Sichtbar“ ist bei Scroll- und Lazy-Load-Seiten zeitabhängig.
- **Verbesserung 1:** Sichtbarkeit wird pro Chunk, Zeit und Surface belegt.
- **RT2:** Auch ein sichtbarer Werbeblock ist sichtbar.
- **Verbesserung 2:** Sichtbarkeit und Aufnahmeentscheidung werden getrennt protokolliert.

### Frage 2 — Wer entscheidet, was Müll ist?

- **Einbau:** Der Nutzer entscheidet per Profil; der Filter liefert nur begründete Vorschläge.
- **RT1:** Nutzerprofile können zu viel oder zu wenig entfernen.
- **Verbesserung 1:** Preset plus Tab-Override plus Preview.
- **RT2:** Ein falsches Preset wirkt auf viele Seiten.
- **Verbesserung 2:** Profile sind site-/originbezogen, versioniert und jederzeit rücksetzbar.

### Frage 3 — Warum darf Werbung draußen bleiben, wenn sie sichtbar ist?

- **Einbau:** Weil der Auftrag eine lesbare Projektion erlaubt; die sichtbare Herkunft bleibt im Ausschlussbuch.
- **RT1:** Das Ausschlussbuch könnte später als Rohkopie missbraucht werden.
- **Verbesserung 1:** Minimierte Fingerprints statt Volltextstandard.
- **RT2:** Ohne Vorschau ist Wiederherstellung schwer.
- **Verbesserung 2:** Reviewansicht zeigt begrenzten Kontext und erlaubt Capture-Neustart.

### Frage 4 — Ist ein Offline-HTML ohne externe Assets überhaupt eine Kopie?

- **Einbau:** Es ist eine klar benannte Projektion; lokal eingebettete und externe Referenzassets werden unterschieden.
- **RT1:** Nutzer erwartet, dass Bilder offline erscheinen.
- **Verbesserung 1:** sichtbare Bilder optional lokal einbetten, mit Budget.
- **RT2:** Große Medien machen das Ergebnis unhandlich.
- **Verbesserung 2:** Teil-Export und Assetpaket neben dem HTML.

### Frage 5 — Was ist eine Seite bei einer SPA?

- **Einbau:** Eine logische URL-/State-/Content-Version, nicht nur ein Browser-Tab.
- **RT1:** Gleiches URL kann mehrere Zustände haben.
- **Verbesserung 1:** State-Fingerprint und Navigationsevent als Seitenversion.
- **RT2:** State-Fingerprints können private Daten enthalten.
- **Verbesserung 2:** minimierter Strukturhash, keine Formwerte.

### Frage 6 — Warum braucht jede Seite 0–100 Prozent?

- **Einbau:** Damit Fortschritt pro logischer Seite sichtbar bleibt und nicht im Jobtotal verschwindet.
- **RT1:** Prozent bei dynamischem Wachstum täuscht Genauigkeit vor.
- **Verbesserung 1:** Schätzung und Endbeweis getrennt anzeigen.
- **RT2:** Nutzer liest trotzdem nur die Zahl.
- **Verbesserung 2:** 100 Prozent nur mit Endmarker; sonst „oberer/unterer Bereich gesichtet“.

### Frage 7 — Sind unendlich viele Tabs wirklich das Ziel?

- **Einbau:** Nein, unendlich viele logische Seiten; echte Tabs nur als begrenzte Arbeitsmittel.
- **RT1:** Daniel möchte einzelne Tabs nachvollziehen.
- **Verbesserung 1:** sichtbarer Tabpark als optionaler Modus.
- **RT2:** Tabpark skaliert schlecht.
- **Verbesserung 2:** Tab-ID und logische Seiten-ID strikt trennen; Park nur für kleine Jobs.

### Frage 8 — Was muss bei ChatGPT gleich bleiben?

- **Einbau:** Normalaufnahme, Rollen, Scrollbeweise, Recovery und Exportstatus.
- **RT1:** Gemeinsames Sanitizing könnte Chat-Controls entfernen.
- **Verbesserung 1:** AI-Adapter liefern ihre Hauptwurzel und eigene Semantik.
- **RT2:** Crawlpolicy könnte in Normalaufnahme einsickern.
- **Verbesserung 2:** getrennte Jobtypen und Regression-Gate.

### Frage 9 — Was muss bei Claude gleich bleiben?

- **Einbau:** Providerkennung, User/Assistant-Trennung, echte Conversation-ID und Endstatus.
- **RT1:** Generischer HTML-Clone könnte Rollen verlieren.
- **Verbesserung 1:** AI-Export bleibt Adapterdomäne.
- **RT2:** gemeinsame Snapshot-Änderung kann Adapterroot falsch wählen.
- **Verbesserung 2:** Claude-Smoke nach jedem Core-/Exportcommit.

### Frage 10 — Wann ist ein Link „mitgenommen“?

- **Einbau:** Wenn sichtbarer Text, Rohziel, kanonisches Ziel, Originstatus und Vorkommen gespeichert sind.
- **RT1:** Ein Link ohne erreichbares Ziel ist nicht navigierbar.
- **Verbesserung 1:** Linkstatus getrennt von Zielinhalt.
- **RT2:** Offline-Router kann defekte Ziele schön aussehen lassen.
- **Verbesserung 2:** Originalstatus sichtbar neben Offlineziel.

### Frage 11 — Wann ist ein Bild „mitgenommen“?

- **Einbau:** Als lokale Kopie, Referenz oder begründetem Ausschluss mit jeweils eigener Klasse.
- **RT1:** Ein URL-Eintrag ist keine Bildkopie.
- **Verbesserung 1:** `embedded_bytes` und `source_url` getrennt.
- **RT2:** Base64 kann Export aufblasen.
- **Verbesserung 2:** Assetpaket und Schwellenwerte.

### Frage 12 — Was tun mit Cross-Origin-Inhalten?

- **Einbau:** Referenzieren, nicht lesen; eigene Freigabe für zusätzliche Origins.
- **RT1:** Viele Seiten leben in CDNs und Iframes.
- **Verbesserung 1:** Origin-Allowlist mit Zweck.
- **RT2:** Freigabe kann zu einem fremden Crawl werden.
- **Verbesserung 2:** per Origin Tiefe, Budget und Ablauf getrennt begrenzen.

### Frage 13 — Was ist ein Beweis für Vollständigkeit?

- **Einbau:** Anfang, stabile Überlappung, Ende, keine unaufgelösten Pflichtlücken und Policykonsistenz.
- **RT1:** Eine Seite kann dynamisch nach dem Ende wachsen.
- **Verbesserung 1:** Wachstumsauswertung und Wartefenster.
- **RT2:** Niemals absolut beweisbar.
- **Verbesserung 2:** `complete_as_observed` statt metaphysisches „vollständig“.

### Frage 14 — Darf der Recorder interagieren?

- **Einbau:** Nur passive, ausdrücklich erlaubte Lesesteuerungen.
- **RT1:** „Mehr anzeigen“ ist für Inhalt oft nötig.
- **Verbesserung 1:** manuelle Freigabe und neue Generation.
- **RT2:** Nutzer vergisst, was er freigegeben hat.
- **Verbesserung 2:** Interaktionslog pro Control im Report.

### Frage 15 — Was passiert bei Consent?

- **Einbau:** Blockieren und erklären; keine Einwilligung simulieren.
- **RT1:** Crawl bleibt dann leer.
- **Verbesserung 1:** Pause mit „im Browser bestätigen und fortsetzen“.
- **RT2:** Warten kann unendlich dauern.
- **Verbesserung 2:** Timeout mit `blocked_by_consent`, nicht mit Erfolg.

### Frage 16 — Was darf der Filter lernen?

- **Einbau:** Nur lokale Vorschläge aus bestätigten Entscheidungen.
- **RT1:** Ein Fehlklick vergiftet spätere Läufe.
- **Verbesserung 1:** Regelversionen und Vorschlagsstatus.
- **RT2:** Nutzer kann den Status übersehen.
- **Verbesserung 2:** Keine automatische Aktivierung, klare Herkunft jeder Regel.

### Frage 17 — Wie bleibt das Ergebnis lesbar?

- **Einbau:** Kurzansicht, Seitenbaum, Chunkkarte und Detailreport.
- **RT1:** Vollständige Auditdaten überfrachten Menschen.
- **Verbesserung 1:** progressive Offenlegung.
- **RT2:** Zu kompakte Ansicht versteckt Lücken.
- **Verbesserung 2:** Warnungen sind immer oben sichtbar, Details aufklappbar.

### Frage 18 — Wie wird die Queue unendlich, ohne gefährlich zu werden?

- **Einbau:** Queue ohne künstliche 30-Seiten-Decke, aber mit expliziten Budgets und Pause.
- **RT1:** Ein Linkgraph kann tatsächlich unendlich sein.
- **Verbesserung 1:** Origin-, Zeit-, Seiten-, Byte- und Tiefenbudgets.
- **RT2:** Nutzer setzt versehentlich „kein Limit“.
- **Verbesserung 2:** Kein-Limit-Modus verlangt sichtbare Warnung und Stopbutton.

### Frage 19 — Was bedeutet „pro Tab auswählbar“, wenn Tabs wiederverwendet werden?

- **Einbau:** Policy hängt an der logischen Seite; physischer Tab ist nur Slot.
- **RT1:** UI zeigt falsche Tabnummer.
- **Verbesserung 1:** `page_id`, `slot_id`, `tab_id` getrennt.
- **RT2:** Nutzer denkt in Browser-Tabs.
- **Verbesserung 2:** Panel nennt „Seite X · bearbeitet in Slot Y“.

### Frage 20 — Was bleibt vom Rohzustand?

- **Einbau:** Kein unbereinigtes Voll-DOM als Export; aber Strukturhash, Filterbuch und sichtbare Metadaten bleiben.
- **RT1:** Ohne Roh-DOM kann man Fehlfilter nicht prüfen.
- **Verbesserung 1:** lokaler Review-Snapshot optional geschützt.
- **RT2:** Review-Snapshot könnte Secrets enthalten.
- **Verbesserung 2:** Form-/Script-/Credentialflächen auch dort entfernen oder separat sperren.

### Frage 21 — Wie wird ein dynamischer Feed gelesen?

- **Einbau:** echte Scrolloberfläche, Überlappung, Stabilität, Wachstum und virtuelle Identität.
- **RT1:** Feed lädt neue Inhalte nach und ersetzt alte.
- **Verbesserung 1:** Chunk- und Knotenhashes statt nur aktueller DOMzählung.
- **RT2:** Identität bleibt unsicher.
- **Verbesserung 2:** Ambiguität blockiert nur den betroffenen Vollständigkeitsclaim.

### Frage 22 — Was macht der Export mit fehlenden Medien?

- **Einbau:** Platzhalter mit Quelle, Grund und Status.
- **RT1:** Platzhalter wirkt wie kaputte Kopie.
- **Verbesserung 1:** klare Badges und Assetreport.
- **RT2:** Badges verändern das Seitenbild.
- **Verbesserung 2:** Originalansicht und Lesekopf getrennt.

### Frage 23 — Wie vermeidet man Werbung in Screenshots?

- **Einbau:** Screenshotfilter kann Zonen maskieren oder Screenshot deaktivieren.
- **RT1:** Maskierung ist keine echte 1:1-Ansicht.
- **Verbesserung 1:** Screenshotstatus „masked visible projection“.
- **RT2:** Nutzer will Designbeleg ohne Werbung.
- **Verbesserung 2:** zwei Screenshotprofile: faithful und reading-masked.

### Frage 24 — Wie werden Styles offline sicher?

- **Einbau:** sanitisiertes CSS, begrenzte URLs, keine aktiven Imports.
- **RT1:** Entfernte CSS-Imports brechen Layout.
- **Verbesserung 1:** fehlende Regeln als Assetwarnung.
- **RT2:** Vollständiges CSS kann schädliche URL-Ketten enthalten.
- **Verbesserung 2:** URL-Graph flach begrenzen und jede Kante protokollieren.

### Frage 25 — Was ist bei Loginseiten erlaubt?

- **Einbau:** Nutzer darf im bestehenden Browser eingeloggt lesen; Recorder kopiert nur sichtbaren Output.
- **RT1:** Sichtbarer Output kann private Nachrichten enthalten.
- **Verbesserung 1:** private/site-specific Policy und Forms-/PII-Schalter.
- **RT2:** Automatische PII-Maskierung ist unzuverlässig.
- **Verbesserung 2:** Preview plus lokale Warnung; keine Serverweitergabe ohne expliziten VPS-Schalter.

### Frage 26 — Wie wird ein Abbruch wertvoll?

- **Einbau:** Letzten gültigen Chunk, Grund, Fortschritt und Fortsetzungspunkt sichern.
- **RT1:** Halber Snapshot wird als fertig gelesen.
- **Verbesserung 1:** `stopped`, `complete:false`, Checkpoint.
- **RT2:** Resume könnte den alten Fehler wiederholen.
- **Verbesserung 2:** neue Generation mit altem Parent.

### Frage 27 — Wie wird ein Filterfehler korrigierbar?

- **Einbau:** Filterentscheidung pro Knotenversion und Review-/Re-run-Funktion.
- **RT1:** Re-run überschreibt die alte Lesekopie.
- **Verbesserung 1:** Seitenversionen nebeneinander.
- **RT2:** Nutzer weiß nicht, welche Version exportiert wird.
- **Verbesserung 2:** kanonische Auswahl im Atlasmanifest.

### Frage 28 — Welche Teile teilen ChatGPT und Crawl wirklich?

- **Einbau:** Sanitizing, Hash, Exportmanifest, Link-/Assetmodell und Qualitätsstatus.
- **RT1:** Chatnachrichten haben Rollen- und Providersemantik.
- **Verbesserung 1:** Adapter liefern semantische Blocks; Crawl liefert Seitenblocks.
- **RT2:** Gemeinsame Felder erzwingen falsche Gleichheit.
- **Verbesserung 2:** gemeinsamer Envelope, typisierte Payloads.

### Frage 29 — Welche Regression ist am gefährlichsten?

- **Einbau:** Falsche Vollständigkeit und falsches Provider-Mixing.
- **RT1:** Tests messen nur Counts.
- **Verbesserung 1:** Herkunft, Rollen, Hashes, Lücken und echte Wheelwege prüfen.
- **RT2:** Tests können dieselbe Hilfsfunktion wiederverwenden.
- **Verbesserung 2:** unabhängiger Comparator und reale Playwright-Smokes.

### Frage 30 — Was darf niemals automatisch geschehen?

- **Einbau:** Consent, Formsubmit, Login, Käufe, Löschungen, fremde Origins und versteckte Datenzugriffe.
- **RT1:** Dadurch bleiben viele Seiten unvollständig.
- **Verbesserung 1:** blockiert mit konkreter manueller Aktion.
- **RT2:** Nutzer klickt aus Ungeduld alles frei.
- **Verbesserung 2:** Freigabe zeigt exakte Reichweite und neue Policygeneration.

### Frage 31 — Wie wird ein „schöner“ Export ehrlich?

- **Einbau:** Lesbare Ansicht vorne, Provenienz-/Lückenkarte direkt daneben.
- **RT1:** Gestaltung kann Warnungen verstecken.
- **Verbesserung 1:** Status und Endgrund im sichtbaren Kopf.
- **RT2:** Nutzer ignoriert technische Hinweise.
- **Verbesserung 2:** natürliche Sprache plus maschinenlesbare Details.

### Frage 32 — Wie wird das System erweiterbar?

- **Einbau:** Captureklassen, Filterregeln, Exporter und Adapter als Module.
- **RT1:** Module erzeugen unterschiedliche Sicherheitsstandards.
- **Verbesserung 1:** gemeinsamer Policy-/Provenance-Contract.
- **RT2:** Contract wird zu starr.
- **Verbesserung 2:** additive Versionierung und unbekannte Felder erhalten.

### Frage 33 — Woran erkennen wir, dass der nächste Bauauftrag gut genug ist?

- **Einbau:** An grünen Gates für expliziten Start, Policy, Filterbuch, Chunks, Queue, Export und AI-Regression.
- **RT1:** Grüne Tests können die falsche Sache testen.
- **Verbesserung 1:** reale Browserpfade plus absichtliche Fehlerfälle.
- **RT2:** Auch reale Tests decken nie jede Site ab.
- **Verbesserung 2:** klare Abnahmegrenzen und keine universelle Kopierbehauptung.

## 11 Sokrates-Schleifen über die 33 Fragen

| Schleife | Leitfrage | Was angegriffen wurde | Was verbessert wurde |
|---:|---|---|---|
| 1 | Was ist sichtbar? | Sichtbarkeit mit technischer Kenntnis verwechselt. | Gerenderter DOM plus Zeit-/Chunkbeleg. |
| 2 | Was ist auswählbar? | Globale Defaults verstecken Tababweichungen. | Effective Policy pro logischer Seite. |
| 3 | Was ist Müll? | Adfilter als Wahrheit behandelt. | Vorschlag, Ausschlussbuch, Review. |
| 4 | Was ist eine Seite? | Tab, URL und State vermischt. | `page_id`, State-Fingerprint, Generation. |
| 5 | Was heißt 100 Prozent? | Prozentzahl ohne Endbeweis. | Schätzung versus Sentinel. |
| 6 | Was heißt unendlich? | Unbegrenzte Tabs statt Queue. | Bounded Pool, unbounded Queue, Budgets. |
| 7 | Was heißt 1:1? | Designkopie mit Inhalts-/Sicherheitskopie verwechselt. | Benannte Projektionen und Filterstatus. |
| 8 | Was wird gespeichert? | Rohdaten, Derivate und Referenzen vermischt. | Kanonischer Envelope und Assetklassen. |
| 9 | Was darf interagieren? | Inhaltsgewinn gegen Seiteneffekt getauscht. | Passive Whitelist und manuelle Generation. |
| 10 | Was muss beweisen? | Selbstprüfung und grüne Counts genügen. | unabhängiger Comparator und Negativtests. |
| 11 | Was wird gebaut? | Große diffuse Plattform statt Gates. | phasenweiser Bauauftrag mit 111 Angriffspunkten. |

Die 11 Schleifen führen zu einem einzigen Satz: **Der Recorder darf viel mitnehmen, aber jede Mitnahme braucht einen Schalter, eine Herkunft, einen Status und eine Grenze.**

## Nächster Gesamtbauauftrag

### Ziel

Baue den bestehenden separaten Crawlrecorder zu einem policygesteuerten, sichtbaren Seitenatlas aus. Der Auftrag startet nur über die Crawloberfläche, arbeitet mit einer persistenten logischen Seitenqueue und einem begrenzten wiederverwendbaren Tabpool, kann für kleine Läufe optional jede Seite als eigenen sichtbaren Tab offenlassen und erzeugt pro Seite eine 0–100-Prozent-Beweiskette aus überlappenden Chunks. Der Export muss lesbar, navigierbar und möglichst assettreu sein, ohne Werbung, Tracker, Formwerte, Sessiongeheimnisse oder versteckte DOM-/API-Daten standardmäßig mitzunehmen.

### Bestehende Herkunft, die unverändert bleiben muss

- Der normale AI-Recorder bleibt der normale AI-Recorder.
- ChatGPT- und Claude-Adapter behalten Provider-ID, Rollen, Conversation-ID, echte Scrollsurface und ihre eigenen Regression-Gates.
- Gemini-/Grok-/andere Webpfade dürfen nicht als semantisch verstanden behauptet werden, wenn nur der generische Webadapter aktiv ist.
- `core/recorder_core.js`, `core/export_engine.js`, `core/crawl_recorder.js`, `core/crawl_db.js`, Sidepanel und Hintergrund bilden weiterhin getrennte, lesbare Schichten.
- Sichtbarer Browserinhalt ist die Quelle; keine verdeckten API- oder Credential-Pfade ergänzen.
- `possibly_incomplete`, `partial`, `stopped`, `blocked` und `complete` bleiben ehrlich unterscheidbar.

### Bauphasen

1. **Contract-Gate:** Typen für Job, Page, Slot, Policy, Chunk, Asset, Link, Filterentscheid, Gap und Exportmanifest.
2. **Trigger-Gate:** eigener Crawlauftrag mit Preview, Freigabe, Pause, Stop und Resume; Normalaufnahme bleibt unangetastet.
3. **Policy-Gate:** Presets, per-Tab-Overrides, effektive Policyansicht und Policyversionen.
4. **Visible-Capture-Gate:** semantischer Lesebaum, sichtbarer Clone, Style-/A11y-/Code-/Tabellenprojektion.
5. **Noise-Gate:** Werbung, Tracker, Consent, Modal, Navigation, Footer und PII als begründete Filterentscheidungen.
6. **Link-Gate:** URLkanonisierung, Origin-Allowlist, Offline-Router, Linkgraph und defekte Kanten.
7. **Asset-Gate:** Bild-/Video-/Audio-/Poster-/Untertitel-/Fontmanifest, Budgets, Referenz-vs-Kopie und Hashes.
8. **Scroll-Gate:** echter Scrollsurface, 70-Prozent-Schritte, 30-Prozent-Überlappung, Wachstum, Endmarker und 0–100 Prozent je Seite.
9. **Queue-Gate:** unbounded logische Queue, bounded Tabpool, Leases, IndexedDB-Checkpoints, Generationen und optionale Tabparks.
10. **Export-Gate:** kanonischer Envelope, Offline-HTML mit Seitenbaum/Chunkkarte, Markdown, JSON, Assetpaket und VPS-/Lokalhash.
11. **Audit-Gate:** unabhängiger Comparator, Mutationstests, Filter-Review, ChatGPT-/Claude-Smokes, echte Flextrawurst-Läufe und Negativfälle.
12. **Abnahme-Gate:** nur überprüfbare Claims; kein „perfekte Kopie“-Label ohne passende Projection-, Coverage- und Assetbelege.

### Ziel-Datenmodell, Code-Skizze

```ts
type CrawlStatus = "preview" | "running" | "paused" | "stopped" | "complete"
  | "partial" | "blocked" | "failed";
type CaptureDecision = "captured" | "referenced" | "filtered" | "blocked" | "unknown";
type Projection = "reading" | "faithful_visible" | "semantic";

type CapturePolicy = {
  version: string;
  projection: Projection;
  content: Record<"text"|"headings"|"lists"|"tables"|"code"|"quotes"|"comments"|"metadata", boolean>;
  links: { visibleText: boolean; context: boolean; internalTargets: boolean; externalTargets: boolean };
  assets: { images: CaptureDecision; media: CaptureDecision; css: boolean; fonts: boolean; icons: boolean; screenshots: boolean };
  noise: { ads: "off"|"review"|"on"; trackers: boolean; consent: "block"|"manual"; navigation: boolean; footer: boolean; popups: "off"|"review"|"on" };
  privacy: { forms: boolean; values: false; pii: "warn"|"mask" };
  limits: { assetBytes: number; pageBytes: number; maxChunks: number; timeoutMs: number };
};

type CrawlPage = {
  pageId: string; crawlId: string; generation: number; slotId?: string; tabId?: number;
  rawUrl: string; canonicalUrl: string; origin: string; depth: number;
  policyVersion: string; status: CrawlStatus; progressEstimate: number;
  chunks: ChunkRecord[]; links: LinkRecord[]; assets: AssetRecord[];
  exclusions: FilterRecord[]; gaps: GapRecord[]; endReason?: string;
};

type ChunkRecord = {
  chunkId: string; ordinal: number; top: number; max: number; viewport: number;
  overlap?: number; stable: boolean; htmlHash: string; policyVersion: string;
  capturedAt: string; htmlRef?: string; repeatedFrom?: string;
};
```

## 111 Gesamtbau-Red-Team-/Verbesserungspunkte

Jeder Punkt ist ein eigener Angriff auf den nächsten Bauauftrag. Die Form ist bewusst knapp: `Angriff → Verbesserung`. Die Nummern sind nicht Dekoration, sondern ein Abnahmeindex.

### Auftrag und Sicherheit — 001–011

001. Crawl startet durch normalen Recordbutton → getrennte Message-Typen und Buttons.

002. Ein alter Crawlstatus bindet den neuen Tab → `crawl_id` und aktive Tab-ID bei jedem Refresh prüfen.

003. URLfeld akzeptiert `javascript:` → nur absolute HTTP/HTTPS-URLs zulassen.

004. Start-Preview zeigt nicht alle Defaults → effektive Policy vor Start vollständig rendern.

005. Origin-Allowlist wird still erweitert → jede Origin als expliziter Allowlist-Eintrag speichern.

006. Consent wird automatisch bestätigt → nur `blocked_by_consent` und manuelle Fortsetzung.

007. Login-Formwerte gelangen in den Snapshot → Controls/Werte standardmäßig entfernen und testen.

008. Crawl-Auftrag hat keinen Zweck/Benutzerbeleg → Startmanifest mit Freigabezeit und Auftragstext.

009. Stopbutton ist während Commit wirkungslos → kooperativer Stop nach atomarem Checkpoint.

010. Pause wird als Erfolg exportiert → `paused`/`stopped` bleibt vom `complete` getrennt.

011. Unbekannte Optionen werden ignoriert → Policyversion plus `unknown_option`-Warnung.

### Policy und Tabprofil — 012–022

012. Globales Profil überschreibt Tab-Override → effektive Policy durch deterministische Mergefunktion.

013. Tabprofil wird beim Slotwechsel verloren → Policy an `page_id`, nicht nur `tab_id`, binden.

014. Schalteränderung verändert alte Chunks → neue Policygeneration beginnen.

015. Preset „Archiv“ aktiviert alles → Presets bleiben begrenzte, sichtbare Policywerte.

016. Bilder an/aus ist zu grob → Referenz, Kopie, Metadaten und Ausschluss getrennt anbieten.

017. Medienbudget ist unsichtbar → verbleibende Bytes/Anzahl je Tab anzeigen.

018. Formswitch verspricht sichere Werte → Wertfeld technisch nie serialisieren.

019. Screenshotprofil ignoriert Privacy → Screenshot opt-in und eigener Filter-/Retentionstatus.

020. Interaktionsprofil öffnet gefährliche Controls → passive Whitelist plus blockierende Standardregel.

021. Nutzer weiß nicht, was effektiv gilt → Policy-Chip pro Tab und Exportkopf.

022. Policy wird nach Resume falsch rekonstruiert → Policyversion im Checkpoint und Resume-Validator.

### Sichtbarer DOM und Projektion — 023–033

023. Clone verliert sichtbare Inhalte → Sichtbarkeit am Original messen, danach klonen.

024. `aria-hidden` wird falsch behandelt → Geometrie und ARIA gemeinsam werten, Konflikt markieren.

025. Wrapperfilter zerstört Semantik → semantische Projektion neben Strukturhash speichern.

026. Script-/Stylefilter lässt aktive Attribute → Event-, nonce-, srcdoc-, integrity- und unsafe-URL-Attribute entfernen.

027. CSS-Entfernung zerstört Lesbarkeit → sanitisiertes CSS mit fehlenden-Asset-Warnungen.

028. Tabelle wird als Textplatte exportiert → strukturierte Tabelle plus Rekonstruktionsflag.

029. Codehighlight dupliziert Text → Textquelle unabhängig vom Tokenmarkup.

030. Eingeklappter Inhalt wird als gelesen behauptet → `collapsed_unread` und optionaler manueller Re-run.

031. Shadow DOM fehlt still → offen/geschlossen/unbekannt ausweisen.

032. Canvas wird als Text ausgegeben → `visual_only` und opt-in Screenshot.

033. Mehrsprachige Seite erhält ein falsches Sprachlabel → Dokument- und Abschnittssprache getrennt.

### Filter und Werbung — 034–044

034. `ad` im Klassennamen löscht Artikel → nur Signalbündel, nicht Einzelstring.

035. Sponsorenhinweis wird ungewollt Filter → likely/unknown in Review statt Auto-Ausschluss.

036. 1x1-Logo wird als Tracker gelöscht → Kontext und Alttext berücksichtigen.

037. Consent-Banner verdeckt Hauptinhalt → blockieren und manuelle Fortsetzung anbieten.

038. Newslettermodal enthält Haupttext → Modalinhalt klassifizieren und reviewen.

039. Footerfilter entfernt wichtige Sitemaplinks → Lesekörper und Linkgraph trennen.

040. Wiederholung ist redaktionell gemeint → Vorkommen zählen und nur identische direkte Wiederholung deduplizieren.

041. Filterbuch enthält private Werbetexte → gekürzte, gehashte Auditdarstellung.

042. Nutzer kann Filter nicht rückgängig machen → Re-include-Review und neue Seitenversion.

043. Lernregel wirkt auf fremde Origins → Regel an Origin/Profil binden.

044. Preview stimmt nach dynamischem Laden nicht → Previewzeit, Differenzreport und neue Entscheidung.

### Links und Navigation — 045–055

045. Relative URL bricht offline → zentraler Resolver mit Original- und Offlineziel.

046. Trackingparameter werden blind entfernt → bekannte Parameterliste, unknown behalten.

047. Subdomain wird automatisch intern → Originklasse und Allowlist explizit.

048. Externer Link wird gecrawlt → nur referenzieren, außer eigener Originfreigabe.

049. Formularlink löst Aktion aus → sichere Navigation und verdächtige URLblockade.

050. Fragmentziel fehlt offline → Ankerinventar und broken-anchor-Bericht.

051. URLvarianten werden zusammengelegt → Rohvarianten und Kanonisierungsgrund erhalten.

052. Linktext enthält Filter-/PII-Reste → Linkpolicy übernimmt Privacy-/Filterregeln.

053. Defekte Ziele sehen erfolgreich aus → Statusbadge und keine captured-page-Zählung.

054. SPA-Navigation erzeugt keine neue Seite → URL-/State-/Content-Fingerprint.

055. Navigation wiederholt denselben Graph → Lease plus URL-/Strukturhash-Deduplikation.

### Assets und Medien — 056–066

056. Lazy-Image bleibt Placeholder → nur viewportnah nach Scroll erneut prüfen.

057. CDN-URL wird als lokale Kopie ausgegeben → `referenced` statt `embedded`.

058. Base64-Asset bläht HTML → Assetpaket und HTML-Referenz bei Budgetüberschreitung.

059. Video lädt nie → Poster/Untertitel/Metadaten separat sichern und Fehler melden.

060. CSS-Hintergrundbild fehlt → sichtbare CSS-Assetliste mit Status.

061. Font lädt von fremder Origin → Referenz oder Allowlist, nie still kopieren.

062. SVG enthält aktive Links → sanitizen und safe-URL-Policy anwenden.

063. Medienretry hängt → begrenzte Retries und Zeitbudget.

064. Assetduplikate vervielfachen Speicher → Contenthash plus Seitenvorkommen.

065. Abgeleitete Transcodierung überschreibt Original → neue Artefaktversion und Originalhash.

066. Assetrechte werden behauptet → nur technische Provenienz, kein Rechtsurteil.

### Scrollen und Seitenbeweis — 067–077

067. Falscher Container wird gescrollt → Kandidaten messen, real klicken, Bewegung verifizieren.

068. 240-Pixel-Mindestschritt verletzt Überlappung → maximal 70 Prozent der frischen Höhe.

069. `scrollHeight` wächst → Fortschritt neu berechnen und Wachstum reporten.

070. Virtuelle IDs recyceln → Mehrsignalidentität und Ambiguitätsstatus.

071. Endposition wird zu früh gelesen → zweimal stabil messen und dynamischen Nachlauf abwarten.

072. Chunkhash ist gleich trotz anderer Position → Position/Ordinal zusätzlich speichern.

073. Wiederholter Chunk wird gelöscht → Referenz auf Ursprungschunk und Vorkommenzahl.

074. Stop während Assetcommit → Commitqueue leeren, dann stopped setzen.

075. Einzelne Seite soll neu laufen → Generation/Parent erhalten.

076. Stagnation wird als echtes Ende gewertet → Endgrund `stagnation` höchstens partial.

077. Replay überschreibt Original → neue Replaygeneration und Vergleichsreport.

### Queue, Tabs und Wiederaufnahme — 078–088

078. Max-30-Clamp bleibt versteckt → optionales Seitenlimit oder „bis Queue leer“ sichtbar.

079. Unbounded Queue läuft endlos → Zeit-, Byte-, Origin-, Tiefen- und Stopbudgets.

080. 300 echte Tabs erschöpfen Chromium → bounded pool als Standard, Tabpark nur opt-in.

081. Tab-ID wird als Seite behandelt → `tab_id`, `slot_id`, `page_id` separat modellieren.

082. Worker schläft ein → IndexedDB-Checkpoint plus Lease.

083. Zwei Worker nehmen denselben Slot → atomarer Claim mit Leaseablauf.

084. Browsercrash verliert zuletzt gelesene Seite → Checkpoint nach jedem Chunk.

085. Resume verwendet alte Policy → Policyhash beim Claim prüfen.

086. Fehlerseite blockiert den ganzen Job → Seitenfehler lokal markieren und nächste Queue fortsetzen.

087. Queue wächst schneller als Speicherung → Backpressure und persistente Batchgrenze.

088. Tabpark bleibt offen → sichtbarer Parkstatus, Suspend-/Schließoption und Ressourcenwarnung.

### Export, Atlas und Qualitätsbericht — 089–099

089. HTML, MD und JSON driften → gemeinsamer kanonischer Envelope.

090. Chunkkarte lädt alle HTMLs sofort → lazy Chunkpayload und Teil-Export.

091. Offline-Link zeigt falsches Ziel → Routertest mit Original-/Offlinepaaren.

092. Filterbericht fehlt im schönen Export → Status-/Filterkopf direkt neben dem Lesekörper.

093. Fehlendes Bild wirkt kaputt → Badge `online`, `lokal`, `filtered`, `blocked`.

094. HTML enthält aktive Reste → unabhängiger Script/Form/Event-Attribute-Scan.

095. Exporthash wird als Vollständigkeit missverstanden → Bytegleichheit und Inhaltsstatus getrennt.

096. VPS-Siegel ist nicht atomar → Tempfile, Flush, fsync, Rename und Manifesthash.

097. Alte Version wird überschrieben → immutable page generation und Parent-Hash.

098. Große Exporte blockieren Panel → asynchroner Exportstatus und Downloadmanifest.

099. Nutzer verliert Warnungen → Kurzreport plus dauerhafte Detaildatei.

### Tests, AI-Regressionsmatrix und Abnahme — 100–110

100. Fixture ist zu sauber → Werbung, Consent, Lazyload, Tabelle, Code und defekte Links einbauen.

101. Nur generischer Webadapter wird getestet → ChatGPT-Smoke mit Rollen und Conversation-ID ergänzen.

102. Claude wird vom Webfallback verdeckt → Claude-Live-Adaptertest und Titel-/Rollenassertions.

103. Gemini/Grok werden zu semantischen Adaptern erklärt → generisch versus dediziert im Status prüfen.

104. Nur Startseite wird gecrawlt → Flextrawurst-Start plus verlinkte Unterseite mit separaten Page-IDs.

105. Nur Erfolgspfad ist grün → Consent, Stop, Timeout, Assetfehler und Resume testen.

106. Filter wird nur anhand Counts geprüft → Ausschlussgrund, Reinclude und unabhängiger DOMvergleich.

107. Linkgraph wird nur als Zahl geprüft → Originalziel, Offlineziel, Origin und Status vergleichen.

108. Medien werden nur als URLs geprüft → lokales Assethashing und Referenz-/Kopiestatus testen.

109. Tabpool-Rennen bleiben unsichtbar → künstliche Worker-/Lease-/Crash-Tests.

110. Export prüft sich selbst → read-only Comparator mit absichtlich mutierten HTML-/JSON-/Manifestfällen.

### Endentscheidung — 111

111. Der Gesamtclaim lautet „alles perfekt kopiert“ → ersetzt durch: **„Sichtbare, ausgewählte und sanitizierte Projektion mit per-Seite-Beweiskette; ausgeschlossene, blockierte und nicht beweisbare Teile sind nachvollziehbar ausgewiesen.“**

## Abnahmebedingungen für den nächsten Bauauftrag

Der Bauauftrag ist erst bereit für Umsetzung, wenn folgende Bedingungen als konkrete Tests vorliegen:

- Der normale Recorder und der Crawlrecorder können im selben Tab nacheinander benutzt werden, ohne Status- oder Datenvermischung.
- Ein Crawl startet ausschließlich über den sichtbaren Crawlauftrag und zeigt seine effektive Policy vor Start.
- Eine Flextrawurst-Seite und mindestens eine Unterseite laufen je Seite von Anfang bis stabilem Endmarker, mit eigener Chunkkarte und eigener 0–100-Prozent-Anzeige.
- Ein Lauf mit `max_pages = 0` bedeutet ausdrücklich „bis Queue leer oder Budget/Stop“, nicht „unbegrenzt Ressourcen verbrauchen“.
- Der Tabpool bleibt begrenzt; der logische Seitenatlas kann über die frühere 30-Seiten-Decke hinaus wachsen.
- Werbe-/Tracker-/Consent-/Modalfilter erzeugen sichtbare Ausschlussentscheidungen und löschen nichts spurlos.
- Links werden vollständig als Vorkommen und kanonische Ziele erfasst; externe Links werden nicht ohne Originfreigabe gecrawlt.
- Bilder und Medien tragen den Status lokale Kopie, Online-Referenz, gefiltert, blockiert oder unbekannt.
- Offline-HTML, Markdown und JSON stammen aus demselben kanonischen Manifest und tragen dieselbe Policy-/Seitengeneration.
- Ein unabhängiger Comparator findet absichtlich entfernte Scripts, Formwerte, Links, Bilder und Chunks.
- ChatGPT und Claude bestehen ihre Normalaufnahme-Smokes nach jeder gemeinsamen Kernänderung; ihre semantischen Adapter bleiben getrennt.
- Kein Exportstatus behauptet mehr, als die Sichtfenster, Filterberichte, Assetbelege und Endmarker tragen.

## Endergebnis

Die 88 Ideen, 22 Red-Team-Runden, 33 sokratischen Fragen, 11 Sokrates-Schleifen und 111 Bauauftragsangriffe laufen auf eine nüchterne, aber starke Architektur hinaus: Der Browserrecorder wird zum **optional gestarteten, policygesteuerten Sichtbarkeits- und Crawlrecorder**. Er kann Seiten sehr weitgehend lesbar und navigierbar abbilden — inklusive Text, Struktur, Links, Bildern, Medien, Styles, Tabellen und Code — aber er macht aus Sichtbarkeit keine heimliche Datenbankkopie. Die Nutzerwahl steht pro logischer Seite im Mittelpunkt; Werbung und Müll werden standardmäßig aus dem Lesekörper gehalten, bleiben aber als begründete Ausschlussentscheidung auffindbar.

Das ist der nächste Gesamtbauauftrag. Vor dem eigentlichen Codebau müssen nur noch die vorhandenen Crawl-Dateien gegen diese Contract-/Policy-/Queue-Schicht gemappt und die sechs wichtigsten Fixtures ergänzt werden. ChatGPT und Claude werden dabei nicht „mitgezogen“, sondern an jedem gemeinsamen Kern-Gate ausdrücklich wieder abgenommen.

## Version 2: Beweisbarkeit im echten Chromium

### Was diesmal tatsächlich geprüft wurde

Die folgenden Befunde stammen aus dem laufenden Chromium über Playwright/CDP und aus dem geladenen Extension-Service-Worker. Sie sind absichtlich nicht mit einer bloßen Node-Syntaxprüfung vermischt.

1. Chromium war über `http://127.0.0.1:9222` erreichbar; der Browser meldete Chrome 150.0.7871.181.
2. Im Browser waren 19 Seiten sichtbar, darunter Flextrawurst, Tagesschau, ChatGPT, Claude, Gemini, X, Facebook und Grok; zusätzlich lief der Extension-Service-Worker.
3. Das Sidepanel war direkt als `chrome-extension://…/sidepanel.html` erreichbar und enthielt getrennte Normal- und Crawlcontrols.
4. Ein echter Playwright-Crawlstart über das sichtbare Sidepanel auf `what-is-flextrawurst.html`, `max_pages=1`, `max_depth=0` endete mit `100%`, `complete`, 9 Chunks, Queue 0 und 7.604 HTML-Zeichen.
5. Ein echter Playwright-Wheel-Schritt auf der Seite bewegte den HTML-Scroller um 389,33 Pixel bei 556 Pixel Viewporthöhe; die gemessene Überlappung lag bei 0,29976. Das ist knapp unter der Zielgrenze 0,30 und deshalb ein negativer Beleg für den generischen Testschritt, nicht ein grüner Überlappungsbeweis.
6. Bestehende und neu geöffnete normale Webseiten-Dokumente zeigten in `page.evaluate()` `DakRecorderCore=false` und `DakRecorderAdapterWeb=false`. Ein anschließender Gegencheck im Extension-Isolated-World meldete im frischen Dokument jedoch vor manueller Nachinjektion `core=true`, `adapter=web`, `booted=true`, Selftest `passed`, 5 sichtbare Blöcke und 6 Links. Daraus folgt: Der frühere Core-Blocker war ein falscher Messkanal — Main-World und Extension-Isolated-World dürfen nicht verwechselt werden. Der Crawlpfad und der normale Content-Script-Pfad müssen trotzdem getrennte Readiness-Gates behalten.
7. Der aktuell geladene Extension-Service-Worker meldete Manifestversion 1.8.0. Die reale Laufzeitquelle wird damit über Runtime-Manifest und nicht über den Dateipfad behauptet.

### Harte Korrekturen aus dem Livebefund

- **Kein Core-Claim aus der falschen Welt:** `page.evaluate()` sieht die Extension-Isolated-World nicht. Der Test muss nach Extension-Reload oder neuer Navigation im Extension-World-Target `core`, Adapter, Versionsmarker und Selftest prüfen; Main-World-Ergebnisse bleiben ein separater Webseitenbefund.
- **Kein Überlappungsclaim aus einer Konstanten:** Der aktuelle Crawlcode schreibt `overlap: 0.30` in den Status, misst aber nicht pro Übergang die tatsächliche Überlappung. Der Bau muss `before.top`, `after.top`, `viewport_height`, realen Delta und berechnete Überlappung speichern. Ein harter Wert ist kein Beweis.
- **Kein Stabilitätsclaim aus `previousTop !== metrics.top`:** Das ist nur eine Positionsänderung. Stabilität braucht zwei Inhalts-/Strukturhashes mit Wartefenster und gleicher Policy.
- **Kein Policy-Claim, wenn nur ein String existiert:** Die aktuelle Crawlpolicy ist `user_started_same_origin_only_visible_dom_no_scripts_no_credentials`; die UI besitzt noch keine vollständige per-Tab-Inhaltsklassenauswahl. Das Konzept beschreibt die Zielarchitektur, nicht den aktuellen Implementierungsstand.
- **Kein „unbounded“ claim im aktuellen Code:** `startCrawl` klemmt `max_pages` derzeit auf 30 und `runCrawl` öffnet pro Seite einen neuen Tab. Queue-/Tabpool-Architektur ist noch Bauauftrag.
- **Kein Filterclaim ohne Filterbeleg:** Die aktuelle Crawlcapture-Schicht sanitisiert Scripts, Formulare und bestimmte Attribute, enthält aber noch keine belastbare Werbeklassifikation mit Reviewbuch. „Werbung draußen“ ist erst nach Fixture-/Livebelegen zulässig.

### Playwright-/Chromium-Beweismatrix

| Gate | Ort der Messung | erlaubte Aktion | Beleg | Gegenprüfung | Statusclaim |
|---|---|---|---|---|---|
| R0 Laufzeit | CDP-Browser, Extension-Service-Worker | verbinden, Manifest lesen | Browser-/Extensionversion, Extension-ID | Runtime-ID gegen erwartete Manifestfelder | `runtime_known` |
| R1 Dokument | frischer Zieltab | sichtbar navigieren/reloaden | URL, Titel, Document-ID, `readyState` | neuer Document-Key nach Reload | `document_fresh` |
| R2 Normaladapter | Content-Script-Welt | nur `evaluate` zum Lesen | Coremarker, Adapter-ID, Version, Selbsttest | erwarteter Provider gegen Host/URL | `adapter_ready` |
| R3 Crawladapter | per `chrome.scripting.executeScript` im Tab | Capturefunktion injizieren und aufrufen | `DakCrawlCapture`-Marker, Capturepolicy | Script-/Form-/Event-Scan im Ergebnis | `crawl_capture_ready` |
| R4 Sichtsurface | echtes DOM im Zieltab | sichtbaren Container klicken | Tag, Box, Top, Height, ScrollHeight | Klickposition innerhalb Box; Topänderung nach Wheel | `surface_verified` |
| R5 Bewegung | Playwright-Maus/Tastatur | echtes `mouse.wheel` oder sichtbares Scrollcontrol | before/after-Metrik, Delta, Zeit | unabhängige DOM-Messung nach Wartefenster | `movement_observed` |
| R6 Chunk | Capture im Chromiumtab | sichtbaren Chunk sichern | HTML-/Strukturhash, Policy, Zeit, Position | zweiter stabiler Snapshot | `chunk_stable` |
| R7 Überlappung | aus R5-Metriken | keine Sonderaktion | `1 - delta / viewport` | Grenzwert 0,30 pro Übergang | `overlap_proven` |
| R8 Ende | Zieltab | bis Endmarker scrollen | end marker, final metrics, growth window | zweimal gleicher Endhash plus kein Wachstum | `complete_as_observed` |
| R9 Filter | Original-/Reviewfixture und Capture | keine versteckte Quelle | keep/exclude/unknown mit Regel-ID | unabhängiger Comparator und Reinclude-Test | `filter_audited` |
| R10 Queue | Extension-Service-Worker + IndexedDB | Start, Pause, Resume, Stop | page/slot/lease/generation | künstlicher Worker-/Tabverlust | `queue_consistent` |
| R11 Export | Sidepanel und Download | Exportbutton sichtbar klicken | Downloaddatei, Bytes, SHA-256 | erneut parsen und gegen Manifest vergleichen | `export_verified` |
| R12 AI | frischer ChatGPT-/Claude-Tab | nur providergeeignete Sichtprüfung | Adapter-ID, Rollen, Conversation-ID, Scrollbelege | Crawlpfad darf keine AI-Rolle ersetzen | `ai_regression_passed` |

### Was Playwright beweisen darf und was nicht

Playwright darf beweisen, dass eine sichtbare Nutzeraktion stattfand, dass ein bestimmtes Chromium-Dokument zu einer bestimmten Zeit eine bestimmte DOM-/Scrolloberfläche hatte, dass die Extension im richtigen Tab reagierte und dass ein Export anschließend als Datei vorlag. `page.evaluate` darf für Messung und Snapshot im sichtbaren Dokument verwendet werden; es darf nicht als Ersatz für die Nutzeraktion dienen, wenn gerade Scrollen, Klicken oder Navigation getestet wird.

Playwright darf nicht beweisen, dass unsichtbare Providerdaten fehlen, dass eine Seite serverseitig vollständig ist oder dass eine externe Ressource rechtlich kopiert werden darf. Diese Aussagen bleiben außerhalb des Recorderbeweises. Der korrekte Claim lautet immer: **„Diese sichtbare, freigegebene Projektion wurde in diesem Chromiumlauf mit diesen Belegen erstellt.“**

### Synergie ohne Vermischung

Die Synergie entsteht auf vier gemeinsamen Verträgen:

1. **Beweis-Envelope:** Lauf-ID, Dokument-ID, Tab-/Slot-/Page-ID, Policyversion, Zeit, URL, Hash und Status.
2. **Sanitizing-Contract:** Keine Scripts, Formwerte, Sessionwerte oder unsicheren URLs im Offline-Seitenkörper.
3. **Export-Contract:** HTML, Markdown, JSON und Assetmanifest projizieren denselben kanonischen Seiten-/Chunkstand.
4. **Comparator-Contract:** Jeder Export kann außerhalb seiner Erzeugungsfunktion erneut gelesen und gegen Manifest, Filterbuch und Lücken geprüft werden.

Nicht gemeinsam sind die Providerselektoren, die Rollenlogik, die AI-Conversation-ID und die semantische Nachrichtenklassifikation. ChatGPT und Claude dürfen vom gemeinsamen Envelope und den Sicherheitsfiltern profitieren, aber eine Website-Chunkkarte darf nicht als Chatturnbeweis ausgegeben werden.

### Menschliche Bedienbarkeit als eigenes Beweisgate

Ein technisch korrekter Crawl ist nicht bedienbar, wenn der Mensch nicht erkennt, was jetzt passiert. Deshalb braucht jeder Lauf eine sichtbare, progressive Bedienfolge:

1. **Vorher:** Start-URL, Originreichweite, Seiten-/Zeit-/Bytebudgets, effektives Profil und Warnungen.
2. **Start:** eine klare Aktion „Crawl starten“, kein Start durch normales Chatrecording.
3. **Währenddessen:** globale Jobzeile plus eine Zeile pro logischer Seite mit URL, Prozent-Schätzung, Chunkzahl, Status, Filter-/Assetwarnung und aktuellem Tab-/Slotbezug.
4. **Eingriff:** Pause, Seite überspringen, Seite wiederholen, gesamten Crawl stoppen und „warum?“ als sichtbare Aktion.
5. **Nachher:** kurzer Satz mit Seitenzahl, `complete_as_observed`/partial, Lücken und Filterzahlen; Details aufklappbar.
6. **Export:** HTML/MD/JSON/Assets einzeln wählbar; vor Download zeigt der Dialog Projection, Policy, Größen und Warnungen.

Bedienbarkeit wird mit Playwright als Nutzerweg geprüft: sichtbarer Button, zugänglicher Name, Fokusreihenfolge, Tastaturbedienung, Disabled-Zustand, Statusänderung und Fehlermeldung. Ein Test, der nur `runtime.sendMessage` direkt aufruft, ist für die Funktionalität nützlich, aber kein UI-Abnahmebeleg.

## 44-fache Gesamtschleife: Playwright-, Chromium-, Synergie- und Bedienredteam

Die folgenden 44 Runden greifen die komplette Datei jeweils als Gesamtsystem an. Jede Runde enthält den Angriff, den konkreten Gegenbeleg oder die Prüfaktion und die Verbesserung, die nach dem Angriff gilt. Die Runden sind Design-/Abnahmeschleifen; sie behaupten keine 44 bereits ausgeführten Implementierungsreleases.

### Laufzeit, Provenienz und frische Dokumente — Runden 1–11

| Runde | Redteam-Angriff | Gegenbeweis / Live-Prüfung | Verbesserung nach der Runde |
|---:|---|---|---|
| 1 | Die Datei behauptet Playwright, nennt aber keinen Browseranschluss. | CDP `9222`, Runtime-Manifest und Service-Worker explizit lesen. | Jeder Lauf beginnt mit R0-Laufzeitpass und Browser-/Extensionversion. |
| 2 | Ein vorhandener Tab wird als frisch injiziert behandelt. | Neuer Tab und Reload melden `core=false`; das ist ein echter Negativbefund. | Neue Document-ID plus Core-/Adaptermarker sind Pflicht vor jedem Normaltest. |
| 3 | Extensionversion aus dem Gitpfad wird mit Runtimeversion verwechselt. | Service-Worker meldet Manifest 1.8.0; Dateipfad allein beweist nichts. | Runtime-Manifest ist Beweisquelle, Quellpfad nur Provenienzmetadatum. |
| 4 | Crawl- und Normaladapter werden gleich behandelt. | Crawl funktioniert per `executeScript`, normale Dokumente sind uninjiziert. | Zwei getrennte Readiness-Gates und getrennte Fehlertexte. |
| 5 | `document.readyState` gilt als App-Bereitschaft. | Dynamische Seiten können danach noch keine Oberfläche haben. | App-/Adapter-Selftest und DOM-Stabilitätsfenster ergänzen. |
| 6 | `page.evaluate`-Scroll gilt als echte Benutzerbewegung. | Kein Nutzerweg, keine Wheel-/Click-Kausalität. | Bewegung ausschließlich mit Playwright-Maus/Tastatur; evaluate nur messen. |
| 7 | Ein sichtbares Ergebnis ohne Tab-/Fenster-ID genügt. | Viele gleichartige Flextrawurst-Tabs existieren gleichzeitig. | `browser_context`, `windowId`, `tabId`, `slotId`, `pageId`, URL und Document-ID verbinden. |
| 8 | Eine URL identifiziert eine SPA-Seite eindeutig. | Gleiches URL kann nach Navigation/State andere Inhalte zeigen. | Navigation-, State- und Contentfingerprint als Seitengeneration. |
| 9 | Service-Worker lebt während des gesamten Jobs. | MV3-Worker kann schlafen oder neu starten. | IndexedDB-Checkpoint, Lease, Resume-Claim und Worker-Recovery testen. |
| 10 | Ein frischer Lauf kann alte IndexedDB-Daten übernehmen. | Gleiche Origin und alte Crawljobs bleiben im Browser. | Neue `crawl_id`, Generation und explizite Exportauswahl; keine stillen Altseiten. |
| 11 | Eine laufende Seite wird beim Test versehentlich aktiviert. | `active:false` verhindert Fokuswechsel nicht in jeder Nebenaktion. | Aktiver Tab vor/nach jedem Schritt messen und Aktivitätswechsel als Ereignis protokollieren. |

### Sichtung, Scrollbeweis und Dynamik — Runden 12–22

| Runde | Redteam-Angriff | Gegenbeweis / Live-Prüfung | Verbesserung nach der Runde |
|---:|---|---|---|
| 12 | Der größte Scrollcontainer ist der richtige. | Flextrawurst zeigt DIV, Unterseite HTML; Containerform variiert. | Kandidaten messen, klicken, bewegen und Auswahlgrund speichern. |
| 13 | Ein Klick auf die Box beweist Fokus. | Klick kann an Overlay oder falscher Position landen. | Koordinaten, aktives Element und Topänderung nach Wheel protokollieren. |
| 14 | Eine feste Mindestbewegung ist immer sicher. | 389,33 bei 556 Höhe ergaben 0,29976 Überlappung. | Kein Mindestdelta über 70%-Regel; reale Überlappung pro Übergang berechnen. |
| 15 | `overlap: 0.30` im Status ist ein Beleg. | Aktueller Code setzt den Wert konstant. | `overlap_measured`, `overlap_min` und Rohmetriken speichern; Konstante nur Zielgrenze. |
| 16 | Ein neuer Topwert bedeutet Stabilität. | Positionsänderung sagt nichts über DOM-Nachladen. | Vorher-/Nachher-Contenthash zweimal nach Wartefenster vergleichen. |
| 17 | `at_bottom` ist ein stabiler Endmarker. | Dynamische Seiten können nach dem Rand wachsen. | Endhash, ScrollHeight-Wachstumsfenster und zweiter Randcheck. |
| 18 | Ein Chunk-HTML ist eine vollständige Seite. | Aktueller Export speichert finalen HTMLkörper plus Chunkmetadaten. | Chunkpayload, Endsnapshot und Projektion ausdrücklich trennen. |
| 19 | Doppelte Chunks dürfen vollständig dedupliziert werden. | Derselbe Inhalt kann an zwei Positionen semantisch relevant sein. | Position, Ordinal und `reused_previous_html` behalten. |
| 20 | Virtuelle Knoten lassen sich über eine ID verfolgen. | Provider können IDs recyceln oder ganz weglassen. | Mehrsignalidentität plus `ambiguous` und Kontextfenster. |
| 21 | Ein Stop nach `crawl_cancelled` ist sofort sicher. | Schreiben/Assetcapture kann noch laufen. | Stop nur nach atomarem Chunkcommit; letzter Checkpoint sichtbar. |
| 22 | Replay repariert einen alten Lauf. | Neue Sichtung kann andere dynamische Inhalte haben. | Replay als neue Generation, nie als Überschreiben oder Lückenschluss ohne Beleg. |

### DOM, Filter, Assets und Export — Runden 23–33

| Runde | Redteam-Angriff | Gegenbeweis / Live-Prüfung | Verbesserung nach der Runde |
|---:|---|---|---|
| 23 | Sanitized DOM ist automatisch vollständig. | Filter entfernt Scripts, Forms und versteckte Inhalte; das ist eine Projektion. | Root, Dropklassen, Filterpolicy und Längenlimit im Exportkopf anzeigen. |
| 24 | Sichtbarkeit kann am Clone gemessen werden. | Clone besitzt keine echte Geometrie. | Original messen, Clone erst danach sanitizen; Fixture mit sichtbaren Knoten. |
| 25 | Werbefilter ist mit einer Selectorliste beweisbar. | `ad`-Signale können redaktionelle Inhalte treffen. | Signalbündel, Reviewklasse, Ausschlussbuch und Reinclude-Test. |
| 26 | Filterauslassung braucht keine Gegenprobe. | Ohne erwarteten Fixtureinhalt bleibt False Positive unsichtbar. | Goldfixture mit behaltenem Artikel, Ad, Pixel, Modal und Footer. |
| 27 | Forms=0 beweist keine privaten Daten. | Daten können als Text, ARIA, URL oder Scriptattribute auftreten. | Secret-/PII-Scan des bereinigten Exportes plus Negativtests. |
| 28 | Linkanzahl beweist Linkqualität. | Gleiche Ziele, kaputte Anker und Trackingvarianten bleiben offen. | Vorkommen, kanonische Ziele, Originstatus und broken-anchor-Bericht. |
| 29 | Bild-URL ist Bildkopie. | Aktuelle Liveprüfung fand Referenzen, keine garantierte Binärkopie. | `embedded`, `referenced`, `filtered`, `blocked`, Hash und Bytezahl getrennt. |
| 30 | CSS-inline macht Design offline treu. | Styles können externe Imports, Assets oder aktive URLs enthalten. | CSS-Sanitizing, Assetgraph, fehlende-Style-Warnung und Layoutfixture. |
| 31 | HTML-Export ist nach Download fertig geprüft. | Erzeuger und Prüfer könnten dieselbe Logik teilen. | Download erneut öffnen, DOM unabhängig zählen, Scripts/Forms/Links mutieren und erkennen. |
| 32 | Hashgleichheit beweist Inhaltstreue. | Gleiche falsche Bytes bleiben gleich. | Bytegate, Struktur-/Inhaltsgate und Coveragegate separat anzeigen. |
| 33 | Eine schöne Atlasansicht genügt. | Warnungen können unter dem Endsnapshot verschwinden. | Status-/Filter-/Endgrundkopf oben; Detailreport aufklappbar, nicht versteckt. |

### Queue, AI-Synergie und menschliche Bedienung — Runden 34–44

| Runde | Redteam-Angriff | Gegenbeweis / Live-Prüfung | Verbesserung nach der Runde |
|---:|---|---|---|
| 34 | 30 Seiten sind schon „unendlich“. | Aktueller Code klemmt `max_pages` auf 30. | Erst Queue/Pool bauen, dann `0 = bis Queue leer oder Budget/Stop` anbieten. |
| 35 | Für jede Seite ein echter Tab skaliert. | 19 offene Seiten existieren bereits; weitere Tabs erhöhen Chromiumlast. | Bounded Tabpool standardmäßig, Tabpark nur bewusst für kleine Läufe. |
| 36 | Tabpool zerstört menschliche Nachvollziehbarkeit. | Physischer Tab und logische Seite würden verwechselt. | Page-/Slot-/Tab-IDs getrennt anzeigen und im Atlas verlinken. |
| 37 | ChatGPT/Claude profitieren automatisch von jedem Webfilter. | Provideradapter brauchen eigene Rollen-/Conversation- und Scrollsemantik. | Gemeinsamer Envelope, getrennte Adapter und verpflichtende AI-Smokes. |
| 38 | Ein grüner Crawl beweist gesunde Normalaufnahme. | Livebefund: Crawlpfad kann grün sein, Core im Webseiten-Dokument false. | Keine Cross-Mode-Erfolgskopplung; Matrixstatus pro Modus. |
| 39 | Ein direkter Runtime-Message-Test ist UI-Abnahme. | Er umgeht sichtbare Buttons, Fokus und Disabledzustände. | Playwright klickt Sidepanel; Runtime-Tests bleiben ergänzende Unit-/Integrationstests. |
| 40 | Viele Checkboxen sind maximale Wahlfreiheit. | Menschen verlieren bei 20 Schaltern die effektive Auswahl. | Presets, progressive Details, effektive Policykarte und Preview. |
| 41 | Stop/Pause braucht nur technische Statuswerte. | Nutzer muss wissen, ob Daten sicher erhalten sind. | Aktionstext: „letzten Chunk gesichert“, „fortsetzen ab Seite/Chunk“, „nichts gelöscht“. |
| 42 | Fehlertext darf technisch bleiben. | `executeScript`-/Timeoutfehler sind keine nächste Handlung. | Fehler + Ursache + nächste sichtbare Aktion + Retry/Skip/Review. |
| 43 | Ein Exportbutton ohne Vorwarnung ist schneller. | Größe, Projection, Filter und fehlende Medien überraschen erst nach Download. | Vor-Download-Zusammenfassung und einzelne Exportformate auswählbar. |
| 44 | Die gesamte Datei ist nach all dem automatisch bewiesen. | Die Datei ist eine Spezifikation; nur konkrete Chromiumläufe beweisen Implementierung. | Abnahme trennt `specified`, `implemented`, `live_proven`, `independent_checked` und verbietet stärkere Claims. |

## Verbesserte Endarchitektur nach 44 Runden

### Statusmodell der Wahrheit

Jede Behauptung erhält zwei Achsen:

```ts
type ImplementationState = "specified" | "implemented" | "fixture_passed"
  | "live_proven" | "independent_checked" | "blocked";

type EvidenceRecord = {
  claim: string;
  state: ImplementationState;
  crawlId?: string;
  pageId?: string;
  slotId?: string;
  tabId?: number;
  windowId?: number;
  documentId?: string;
  browserVersion?: string;
  extensionId?: string;
  extensionVersion?: string;
  policyVersion?: string;
  playwrightAction?: string;
  before?: Record<string, unknown>;
  after?: Record<string, unknown>;
  comparator?: { name: string; result: "pass" | "fail" | "not_run" };
  createdUtc: string;
};
```

Ein `complete`-Seitenstatus ist nur zulässig, wenn die Seite `live_proven` für Start/Bewegung/Chunks/Ende besitzt und der Export mindestens `fixture_passed` sowie `independent_checked` für Sanitizing und Formatkonsistenz besitzt. Für reale fremde Seiten kann der Comparator nur das bereinigte Ergebnis prüfen; er darf keine unsichtbare Quelle erfinden.

### Exakter Playwright-Abnahmeablauf

```ts
// 1. Browser-/Extensionpass
const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const worker = findExtensionWorker(browser);
const runtime = await worker.evaluate(async () => ({
  id: chrome.runtime.id,
  manifest: chrome.runtime.getManifest(),
  tabs: await chrome.tabs.query({})
}));

// 2. Frischer Dokumentpass — kein bestehendes Dokument vertrauen
const page = await context.newPage();
await page.goto(url, { waitUntil: "domcontentloaded" });
await waitForVisibleAppOrRecordBlocked(page);
const documentProof = await page.evaluate(() => ({
  url: location.href,
  ready: document.readyState,
  core: Boolean(globalThis.DakRecorderCore),
  adapter: globalThis.DakRecorderAdapterWeb?.id || null,
  title: document.title
}));

// 3. Echte Browserbewegung, evaluate nur für Messung
const surface = await chooseAndMeasureSurface(page);
await page.mouse.click(surface.box.x + 8, surface.box.y + Math.min(80, surface.box.h / 2));
await page.mouse.wheel(0, Math.floor(surface.viewport * 0.70));
const transition = await readStableBeforeAfterMetrics(page);
assert(transition.overlap >= 0.30);

// 4. sichtbarer Buttonweg für Start/Stop/Export
await panel.getByRole("button", { name: "Crawl starten" }).click();
await panel.getByRole("button", { name: /Crawl stoppen|Crawl pausieren/ }).isVisible();
```

Der Ausschnitt ist eine Methodenskizze, kein fertiger Test. Besonders wichtig sind `findExtensionWorker`, `waitForVisibleAppOrRecordBlocked`, `chooseAndMeasureSurface` und `readStableBeforeAfterMetrics`: Sie müssen Belegdaten zurückgeben, nicht nur Assertions ausführen. Bei einem negativen Core-/Adapterbefund wird der Test als `blocked` beendet; er wird nicht durch einen generischen Crawlstatus grün gefärbt.

### Menschlicher Bedienvertrag

Der Mensch muss vor jedem kosten- oder datenträchtigen Schritt wissen:

- welche Seiten und Origins berührt werden;
- welche Inhaltsklassen pro Seite aktiv sind;
- ob Bilder lokal kopiert oder nur referenziert werden;
- welche Filter standardmäßig greifen;
- wie viele echte Tabs maximal offen sind;
- wie Pause, Stop, Skip, Review und Resume wirken;
- welcher Status wirklich bewiesen und welcher nur geschätzt ist.

Die Bedienoberfläche bekommt daher keine versteckten „magischen“ Fallbacks. Ein generischer Webfallback darf sichtbar helfen, aber nicht behaupten, ChatGPT-/Claude-Semantik verstanden zu haben. Ein ausgeschalteter Filter bleibt ausgeschaltet, auch wenn eine heuristische Regel meint, es besser zu wissen.

## Finale Korrektur des Bauauftrags

Der nächste Bau beginnt nicht mit 111 Features gleichzeitig. Er beginnt mit einem schmalen Proof-Ring:

1. frischer Chromium-/Extension-/Dokumentpass;
2. expliziter Crawlstart aus dem Sidepanel;
3. ein Flextrawurst-Textfixture mit Bild, Link, Tabelle, Code, Werbung, Trackerpixel und Consent-Block;
4. gemessene Scrolltransitionen mit echter Überlappung statt Konstante;
5. persistenter Chunkcheckpoint und sauberer Stop;
6. unabhängiger Export-/Sanitizing-Comparator;
7. danach erst Queue/Tabpool;
8. anschließend ChatGPT-/Claude-Regressionen im frischen Dokument;
9. erst dann größere Origin-/Asset-/SPA-Fälle.

Diese Reihenfolge erzeugt Synergie: Jeder Ring liefert einen Vertrag, den die nächste Schicht wiederverwendet, aber keine Schicht darf den Beweis einer anderen simulieren. Der reale Chromiumlauf bleibt der Ort, an dem sichtbar wird, ob die Architektur lebt.

[[abwurf: Ein grüner Crawl darf niemals den fehlenden Core im frischen Dokument überstrahlen.]]
