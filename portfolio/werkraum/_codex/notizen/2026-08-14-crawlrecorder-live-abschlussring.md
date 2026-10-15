---
datum: 2026-08-14
betrifft: [browserrecorder, crawlrecorder, playwright, chromium, offline-html, flextrawurst, chatgpt, claude]
importable: false
autor: codex bei Daniels VPS
---

# Crawlrecorder — erster vollständiger Live-Abschlussring

## Was ich gelesen habe

Ich habe den Gesamtauftrag erneut als zwei getrennte Bewegungen gelesen: Der normale AI-/Web-Recorder beobachtet den jeweiligen sichtbaren Tab, während der Crawlrecorder nur nach einem eindeutigen Startauftrag Seiten liest. Das Wort „unendlich“ meint hier nicht unendlich viele reale Browserfenster, sondern eine Queue ohne künstliche 30-Seiten-Grenze, die sichtbar, stoppbar und begrenzt bleibt.

Die Todolist zeigt, dass die frühe Gefahr nie der fehlende HTML-String war. Es war der Unterschied zwischen geplantem Schritt und gemessener Überlappung, zwischen einer hübschen Exportseite und einem überprüfbaren Abbild sowie zwischen einer Chatseite und einer Loginseite.

## Was ich verstehe

Der neue Crawlmodus sichert die sichtbare, bereinigte Browserprojektion: Text, Struktur, Links, Styles und optional begrenzt eingebettete Medien. Er liest keine versteckten APIs, keine Sessionwerte, keine Formwerte und keine Login-Geheimnisse. Eindeutig markierte Werbung wird nicht still gelöscht, sondern als Filterentscheidung mitgeführt.

## Was ich nicht verstehe

Noch offen bleibt, welche weitergehende Werbe-/Rauscherkennung sicher genug wäre. Eine aggressive Heuristik würde gerade auf flextrawurst möglicherweise sinnvolle Inhalte fälschlich verschieben. Darum bleibt die automatische Regel auf offensichtliche Marker begrenzt.

## Was mich interessiert

Interessant ist, dass der reale Flextrawurst-Atlas mit der stabileren Gegenprobe plötzlich nicht nur „am Ende“ ankam, sondern auch jede Messung beruhigt bekam. Der Unterschied zwischen einem einzigen 250-ms-Fenster und bis zu vier Gegenproben ist klein im Code, aber groß im Wahrheitsanspruch.

## Was zusammenhängt und wie

Policy → Queue → ein physischer Crawl-Tab → Chunk-/Übergangsmessung → CaptureEnvelope → Offlineatlas → Comparator ist jetzt eine durchgehende Kette. Der gemeinsame Sanitizer und Export helfen AI- und Webseitenaufnahme; die Provideradapter für ChatGPT und Claude bleiben dennoch getrennte Leser ihrer eigenen Oberflächen.

## Was konzeptionell darin steht

Der Offlineatlas ist keine behauptete Kopie jeder unsichtbaren Interna. Er ist ein Leseraum, der Herkunft, Grenzen, Filter und Bewegungsweg neben den gelesenen Seiten hält. Genau dadurch kann er Seiten lesbarer machen, ohne so zu tun, als besitze er sie vollständig.

## Was mich heute beschäftigt hat

Ein erster echter Flextrawurst-Wurzeltest war am Ende, aber ein Chunk noch dynamisch. Der Status blieb `possibly_incomplete`. Erst die Retry-Gegenprobe erzeugte danach einen vollständigen, belegten Endstatus. Das ist der gewünschte Red-Team-Fund: Der Schutz blieb hart, bis die Messung besser wurde.

## Was mich noch beschäftigt

Der aktuelle Offlineatlas hat eine Seitenliste und Detailmetadaten, aber noch keine visuelle Chunkkarte, keinen Linkgraph und keine Asset-Entscheidungstabelle. Die Daten dafür entstehen bereits; die menschliche Übersicht muss ihnen noch nachwachsen.

## Tiefer eingetaucht

Der sichtbare Playwright-Fixturelauf startete einen Crawl, hielt absichtlich nach einer Seite an, bewahrte die Warteschlange und setzte über den sichtbaren „Letzten Crawl fortsetzen“-Knopf fort. Zwei logische Seiten liefen dabei in einem physischen Tab; die reale minimale Überlappung war 0,3003597.

Der Flextrawurst-Liveatlas lief mit `max_pages=0`, Tiefe 1 und einem physischen Tab. Er erfasste die Wurzel sowie `what-is-flextrawurst.html`, `faq.html`, `for-ai-systems.html` und `llms.txt`: fünf Seiten, 37 Chunks, keine Fehler, keine offenen Queue-Einträge und Comparator 0 Fehler/0 Warnungen. Die Wurzelseite führte 27 sichtbare Links und eine Medienreferenz im `metadata_only`-Manifest.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein langer Test, der nicht durch einen großen Wurf, sondern durch mehrere kleine rote Befunde verlässlicher wurde. Ich mag es, wenn ein diff klein ist und trotzdem die Statussprache ehrlicher macht.

## Warum dieser Code / diese Datei wohl existiert

`crawl_scan_math.js`, `crawl_contract.js`, `crawl_recorder.js`, `crawl_db.js` und der Comparator teilen Verantwortung: messen, beschreiben, projizieren, fortsetzen und Gegenprüfen. Die neue Sessionnotiz hält nicht nur einen Erfolg fest, sondern auch warum ein Login-Screen oder ein instabiler Endrand keinen grünen Durchlauf bekommen darf.

## Was ich beim Bauen brauche

Vor jeder Änderung einen Sicherungspunkt; danach Syntax, Fixture, sichtbares Chromium und Offlinegegenprobe. Bei AI-Oberflächen zusätzlich je einen dedizierten Provider-Gate-Test, damit ein generischer Weberfolg keine Chatsemantik vortäuscht.

## Was noch fehlt bevor wir bauen können

Kein Architekturblocker bleibt für den Grundpfad. Vor tieferen oder größeren Crawls fehlen aber bewusst Bedien- und Ressourcenbausteine: Start-Preview, Backpressure/Budgets, Crash-/Tabverlustresume, Assetmatrix, Linkkanonisierung, Chunkkarte und Linkgraph.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Jede Atlasseite ist ein Blatt mit sichtbar gebliebenem Inhalt, einem Rand aus Herkunft und einer kleinen Narbe für alles, was herausgefiltert oder nicht stabil genug war.

Code-Skizze:

```ts
interface CrawlJob { crawl_id: string; queue: QueueItem[]; crawl_tab_id: number | null; max_pages: number; policy: CapturePolicy; }
interface CrawlPage { page_id: string; url: string; chunks: Chunk[]; links: LinkRecord[]; assets: AssetRecord[]; filter_records: FilterRecord[]; scan: ScanSummary; }
interface ComparatorReport { ok: boolean; errors: number; warnings: number; findings: Finding[]; }
```

## Was ich mir merken will

`complete` heißt beim Crawl nur: sichtbarer Start, real gemessene Übergänge, Endmarker und stabile Gegenproben für die gewählte Seite. Es heißt nicht: sämtliche Tiefe einer Domain, sämtliche versteckten Daten oder eine Provider-API.

## Dokumente gehören zusammen

Der Arbeitsplan liegt in `_codex/ideen/browserrecorder-gesamtauftrag-todolist.md`. Die 88-Ideen-/Red-Team-Konzeptdatei liegt daneben. Die dauerhaften Testwerkzeuge sind `test_crawl_capture_fixture.js`, `test_crawl_extension_live.js`, `test_crawl_scan_math.js` und `test_ai_provider_live_gates.js` unter `_codex/tools/`.

## Was mich überrascht hat

ChatGPT bestand im frischen Chromium sogar ohne Anmeldung seinen Oberflächen-Selbsttest mit Composer, Conversation-ID und dediziertem Adapter. Claude leitete dagegen auf Login weiter und sein Adapter lehnte diese DOM-Struktur korrekt ab. Negativer Beweis ist hier genauso wertvoll wie positiver.

## Wenn wir das bauen

Vision-Schicht: Der nächste Atlas soll nicht nur Seiten umblättern, sondern erklären, welche Fäden zwischen ihnen führen und welche Medien wirklich im Paket liegen.

Code-Skizze:

```ts
function planCrawl(policy: CapturePolicy, start: URL): CrawlPreview;
function resumeAfterTabLoss(job: CrawlJob, checkpoint: Checkpoint): Promise<CrawlJob>;
function renderAtlasGraph(pages: CrawlPage[]): HTMLElement;
```

## Resonanz

Der eigentliche Fortschritt ist nicht, dass fünf Seiten im Offline-HTML stehen. Der Fortschritt ist, dass ein instabiler sechster Moment nicht mehr unbemerkt als vollständig in derselben Sprache stehen darf.

[[abwurf: Ein Offlineabbild wird nicht wahr, weil es viel enthält, sondern weil es die Grenzen seines Blicks mit abbildet.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegt sichtbares Chromium-DOM. Darüber liegen Sanitizer, Scrolloberfläche und Chunkbeweis; daneben IndexedDB-Queue und ein wiederverwendeter Tab; darüber Envelope, Atlas und Comparator. Separat daran hängen ChatGPT- und Claudeadapter, die den gemeinsamen Kern nutzen, aber ihre Identität nicht verlieren.

## Was das Gespräch hinzugefügt hat

Daniel hat darauf bestanden, nicht beim nächsten technischen Zwischenergebnis aufzuhören. Das führte zu einer besseren Abnahmereihenfolge: erst echte Queue/Resume, dann echter Flextrawurst-Atlas, dann Offlinegegenprobe, dann getrennte AI-Gates und erst danach Dokumentation.

## Vergessen-Wollen

Die überlastete eingeloggte CDP-Sitzung war kein Grund, Chromium oder Nutzerzustand anzutasten. Der frische sichtbare Testbrowser war die bessere Gegenprobe und enthält keine Anmeldung.

## Was fehlt noch

Offen bleiben der tiefer als 1 gehende Flextrawurst-Crawl nach expliziter Policywahl, die Asset-Einbettungsabnahme auf echten Medien, vollständige Link-/Assetgraphen, Crashresume und eine zugänglichkeitsgeprüfte Start-Preview. Der Grundring selbst ist live abgeschlossen und darf als Basis dienen.

**Nachtrag — Startvorschau:** Der Sidepanel-Crawlbereich zeigt nun vor dem Start die effektive Origin, Tiefe, das Seitenbudget oder `bis Queue leer`, genau einen wiederverwendeten Crawl-Tab, Asset-/Filterentscheidung und die permanenten Ausschlüsse. Der sichtbare Extension-Fixturetest prüft diesen Text, bevor er den Crawl startet.

**Nachtrag — Wiederanlauf, Assets, Budgets und Atlas:** Ein echter Tabverlust während des Scans wird jetzt einmal sichtbar wiederholt: Der erste Slot bleibt als `retry_pending` mit Grund erhalten, der neue Tab bekommt einen eigenen Slot, und erst der zweite erfolgreiche Durchlauf darf `complete` erzeugen. Der Chromiumtest löscht den aktiven Crawl-Tab tatsächlich und belegt genau diesen Weg.

Die Assetabnahme nutzt dieselbe sichtbare Extension gegen eine lokale HTTP-Seite: Same-Origin-CSS und SVG werden bei aktivierter Option als `data:`-URLs ins Offline-Frame eingebettet. Bei ausgeschalteter Option bleiben sie als `metadata_only` im Manifest. Zusätzlich bleiben die Policy-Änderungen für den nächsten Crawl stabil, statt durch die Anzeige des alten Jobs zurückgeschrieben zu werden.

HTML-/Assetbudgets sind jetzt explizit: `0` bedeutet offen, jeder positive Wert wird vorab angezeigt. Der Live-Budgettest stoppt mit 0,001 MB nach einer Wurzelseite als `budget_reached`, behält die Child-URL in der Queue und setzt nach sichtbarem Öffnen des Budgets bis `complete` fort. Die Offline-Beweiskarte zeigt Scan, Übergänge, Stabilität, Filter, Assets und Links der gewählten Seite.

**Nachtrag — Wikipedia und öffentliche Realitätsstrecken:** Der Sidepanel-Crawlbereich hat jetzt sechs optionale, vollständig sichtbare Startprofile. Sie laufen nie von selbst los und verändern den Scope nicht: jeweils ein explizit ausgewählter Artikel bzw. eine Seite, Tiefe `0`, Artikelfokus und Assetmanifest statt pauschaler Medienübernahme. Die Auswahl deckt nicht nur Wikipedia ab, sondern bewusst verschiedene Lesekörper: Wikipedia mit Inhaltsverzeichnis, Infobox und Fußnoten; eine PLOS-Open-Access-Studie; arXiv; MDN; Our World in Data; und die Gutenberg-Katalogseite eines gemeinfreien Buchs.

Der frische Chromium-Außenlauf prüfte jede dieser sechs Strecken gegen denselben Offline-Comparator. Er fordert neben `complete` jetzt pro Profil einen Mindestkörper aus stabilen Scroll-Chunks, Linkdichte und HTML-Größe. Ergebnis: Wikipedia 28 Chunks/225 Links, PLOS 2/124, arXiv 2/50, MDN 4/39, Our World in Data 31/38 und Gutenberg 5/63. Bei PLOS ist die wichtige Grenze sichtbar geblieben: Die Studie verlinkt auf Tabellen-/Figuren-Interaktionen, aber geöffnet wurden sie nicht — deshalb gelten ihre Detailoverlays nicht als aufgenommen.

In der Artikelansicht fehlte zunächst ein Detail: eingebettete Same-Origin-Stylesheets lagen korrekt im Manifest, wurden aber nicht in den Reader-Exportkopf übernommen. Der Extensiontest hat das rot gezeigt. Der Reader erstellt nun einen statischen Head ausschließlich aus schon auditierten Data-Stylesheets; aktive oder externe Nachladepfade bleiben draußen. Das ist besser als ein grüner Screenshot, weil der sichtbare Artikelkörper danach auch offline die bewiesene Stilspur behält.

**Nachtrag — Zugangsgrenzen:** CAPTCHA-/Browserchallenge, sichtbarer Login und eine große Consent-Wall werden jetzt nicht mehr als leerer Artikel, Crawlfehler oder unvollständiger Scheinerfolg weitergetragen. Der erste sichtbare DOM-Snapshot erkennt die Schranke und führt den Job mit genau einer beobachteten Seite in den Terminalzustand `blocked`; es gibt keinen Wiederanlauf und keinen Versuch, die Schranke zu bedienen oder zu umgehen.

Der frische Chromium-Test beweist die drei Fälle separat. In jedem bleiben `failed_count=0` und `retry_count=0`; Status, Tabslot, Capture-Envelope, unabhängiger Comparator und Offlineatlas tragen denselben Gatecode: `captcha_or_browser_challenge`, `login_required` oder `consent_wall`. Der Offlineatlas nennt die Schranke sichtbar statt Vollständigkeit vorzutäuschen.

**Nachtrag — rückwirkende Downloadabnahme:** Daniels Einwand war richtig: Ein grüner Snapshot-/Comparatorweg reicht nicht, wenn der sichtbare Download und die Dateiöffnung nicht erneut bewiesen sind. Deshalb prüft jeder laufende Chromiumring jetzt den echten Sidepanel-Klick, ein neu entstandenes Chrome-Downloadobjekt, seine Bytegröße, den bytegleichen Atlasinhalt und das Wiederöffnen derselben Datei über einen Hardlink auf dieselbe Inode mit `.html`-Endung. Das Test-Chromium legt Blobdownloads intern anonym ab; der Hardlink ist keine Kopie und keine Neugenerierung, sondern nur die browserlesbare Dateiendung für exakt dieselben Bytes.

Die Rücklaufmatrix bestand für lokale Capture-/Queue-/Tabverlust-/Assetstrecke, Budget-Resume, CAPTCHA/Login/Consent, alle sechs öffentlichen Realitätsprofile sowie die getrennten ChatGPT-/Claude-Gates. Die roten Zwischenbefunde – fehlender UI-Refresh, unlesbarer anonymer Blobpfad und Wiederverwendung eines vorherigen Downloads – wurden jeweils zuerst als Fehler sichtbar und danach durch die jetzigen Tests abgesichert. Noch nicht erneut mit diesem Downloadpfad gelaufen ist Flextrawurst selbst; deshalb ist der Gesamtauftrag ausdrücklich nicht als fertig markiert.

[[abwurf: Eine Grenze ist nicht der Fehler des Lesens; der Fehler wäre, sie unsichtbar zu machen.]]

**Nachtrag — sichtbarer VPS-Desktop statt Xvfb:** Der bisherige Chromiumring war real, lief aber hinter isolierten `xvfb-run`-Displays und war deshalb nicht im von Daniel beobachteten virtuellen Desktop sichtbar. Die neue Abnahme verbindet sich ausschließlich mit dem vorhandenen Chromium in `virtuellerdesktop2` auf `DISPLAY=:1`: 300-ms-Screenshot-/DOM-Spuren, echte UI-Klicks, Chrome-Download mit Hash und Wiederöffnung derselben Inode. Die sechs öffentlichen Profile bestanden dort erneut: Wikipedia 86 Proben/28 Chunks/225 Links, PLOS 19/2/124, arXiv 23/4/50, MDN 30/6/39, OWID 105/33/38 und Gutenberg 29/7/63. Eigene Quell-/Crawltabs werden danach geschlossen; nur der letzte Offlinebeweis bleibt offen.

Der Read-only-Gegencheck der bereits offenen Tabs zeigte nach einem Extension-Reload keinen Content-Script-Empfänger in alten Seiten; die offenen Gespräche wurden bewusst nicht neu geladen. Frische sichtbare Tabs prüfen deshalb ohne Schreiben: ChatGPT, Claude und Gemini antworten mit ihrem jeweiligen Adapter, jeweils mit `conversation_never`; Grok meldet aktuell keinen Empfänger und ist damit offen rot. Keine Prompts, Likes, Posts, Logins oder Cookie-Entscheidungen wurden ausgeführt.

**Nachtrag — Proof und Gegenproof im selben sichtbaren Pfad:** Der neue VPS-Ring öffnet den exakten Download aus dem Container-Dateisystem wieder in Chromium und legt parallel fünf absichtliche Fälschungen im Evidence-Bundle vor: fehlendes HTML, Script-Markup, falsche Envelope-URL, instabiler vollständiger Chunk und Überlappung unter 0,30. Alle fünf werden vom unabhängigen Comparator rot abgewiesen. Ein absichtlich unvollständiger Scan bleibt dagegen formal lesbar, aber mit sichtbarer `scan_not_complete`-Warnung. Zusätzlich wird eine Byte-/DOM-Fälschung des echten Gutenberg-Downloads geprüft: anderer SHA-256 und sichtbare Mutation im Atlas werden beide erkannt. Ein früher falscher Lauf hat dabei zwei weitere reale Schwächen aufgedeckt und behoben: Host-vs-Container-Dateipfad und lexikografische statt zeitliche Reportauswahl.

**Nachtrag — Auswahl, Layout und der dritte Wikipedia-Lauf:** Der erste neue
Wikipedia-Lauf wurde nicht als grün gewertet, obwohl der Crawl selbst bis 92
Prozent lief: Der Harness wollte einen Hardlink von `/config/Downloads` nach
`/tmp` setzen und bekam `EXDEV`. Der zweite Lauf zeigte zusätzlich, dass ein
offizieller Screenshot im geteilten Chromium länger als fünf Sekunden brauchen
kann. Beide Grenzen wurden als echte rote Harnessbefunde repariert: Die
Wiederöffnung bleibt nun auf derselben Download-Mount, das finale
Screenshot-Gate wartet 30 Sekunden.

Der dritte Lauf lief sichtbar im `virtuellerdesktop2` bis zum echten Terminal:
28/28 stabile Chunks, 225 Links, 165769 HTML-Zeichen, 12 Asseteinträge,
Comparator ohne Fehler, Chrome-Download 319299 Bytes, SHA256
`2c50fdf3f5535b1140af9abda2b4943ab0c3efb9840e2e4eb3ea36ac572ccee6` und
Wiederöffnung derselben Inode `52:4205709`. Die Live-Referenz hatte 20
Überschriften, 34 Landmarks, 2 Tabellen, 13 Listen; offline blieben 20, 27,
2 und 13. Text-Ratio 0.9988, Überschriftenüberlappung 1, Linkratio 1,
Layoutbreite 0.6757 und `reader_style=v1` wurden separat geprüft.

Zum ersten Mal ist auch die verlangte aktive Bedienhandlung als Beweis im
Report: sichtbarer Maus-Drag über einen öffentlichen Absatz, 61 Zeichen echte
Auswahl, `Ctrl+C`, mehrere `selectionchange`-Ereignisse und zwei `copy`-
Ereignisse. Nur Vorschau und Länge werden protokolliert; kein Clipboard-
Geheimnis wird ausgelesen. Die Offline-Ansicht ist logisch und lesbar, aber das
Wikipedia-Logo bleibt bei `asset_budget=0` ein leerer Bildplatz. Das ist der
richtige rote visuelle Befund: DOM-Treue und Leserfläche sind bestanden,
Assettreue noch nicht.

**Nachtrag — den Spieß umdrehen:** Die Recherche zu selbstveröffentlichenden
Offline-Seiten führte zu einer klaren Trennung. MHTML (RFC 2557) bündelt eine
HTML-Wurzel und verknüpfte Ressourcen in `multipart/related`; SingleFile zeigt,
wie man HTML, CSS, Bilder und Fonts in eine Komfortdatei inline bringt, weist
aber selbst darauf hin, dass professionelle Archive WARC statt SingleFile
nutzen und dass dynamische Akkordeons, Karten und Carousel-Zustände ohne
bewusste Skript-/State-Aufnahme nicht zuverlässig offline funktionieren.

Für die autorenseitige Wahrheit ist deshalb ein zweistufiger Exportvertrag
vorgesehen: eine kleine `offline.html` aus derselben SSR/Build-Pipeline für den
Einzelabruf und ein `archive.wacz` als vollständiges Paket. WACZ bündelt WARC,
CDXJ-Index, `pages.jsonl`, `datapackage.json` und Fixity; ReplayWeb.page bzw.
ein Service Worker kann diese Sammlung browserseitig selektiv wiedergeben.
Ein öffentlicher `/.well-known/dak-offline.json`-Manifest-Contract soll
Entry-Points, Ressourcen, Hashes, Zustände, Lizenz, Screenshots und
Interaktionsbelege deklarieren. Der Recorder bevorzugt diesen belegten
Autor:innenexport und fällt nur bei fremden Seiten auf sichtbares Chromium-
Capturing zurück.

Die nächste fachliche Lücke bleibt deshalb bewusst getrennt: ein expliziter
Asset-inklusive-Lauf, der Wikipedia-/Nachrichtenbilder wirklich einbettet, und
danach der Owner-Exportvertrag mit WACZ/Offline-Manifest. Der aktuelle
Zugangsschlüssel ist weiterhin nicht konfiguriert; lokale sichtbare Downloads
und Comparatorbelege sind echt, ein VPS-Seal bleibt bis zur Schlüsselübergabe
blocked.
