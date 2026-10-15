# Verlauf: Daniel und ChatGPT auf dem VPS

Rekonstruiert von Claude Code, 2026-09-17, aus echten Dateispuren auf dem VPS —
kein Chatverlauf-Zitat, sondern was sich aus Zeitstempeln, angelegten Strukturen und
Commits nachvollziehen lässt. Wird schrittweise weitergeführt, nicht in einem Rutsch.

**Methodik-Nachtrag (während der Arbeit ergänzt):** Daniel, wörtlich: "wenn musst du
wirklich tag um tag prüfen seit tag 1" — die anfängliche Chronik (Stichproben an
auffälligen Tagen) genügte nicht. Ab dem Abschnitt "2026-07-25" unten wird jeder Tag
einzeln benannt, auch stille, auf Basis einer vollständigen Tagesdatei-Zählung für
`_gpt/` (`find ... -printf '%TY-%Tm-%Td' | sort | uniq -c`). `gptspieleversuchzeigen`
(23.07.) und `DREIERREGEN`/das Fünf-Sessions-Experiment (26.07.) liegen außerhalb von
`_gpt/` und sind unten separat abgedeckt.

Dies ist ausdrücklich ein **laufendes Mehrsessionen-Projekt**, kein Rest-einer-Nacht-
Abschluss: 56 Tage von Tag 1 bis heute sind ehrlich zu viel für eine Sitzung. Die
folgende Statusliste ist der Einstiegspunkt für JEDE künftige Session (auch eine
ganz frische, ohne Erinnerung an dieses Gespräch) — sie muss nicht die Prosa
durchsuchen, sondern kann hier direkt ablesen, wo weitergemacht werden muss.

### Statusliste — was ist wie weit geprüft

**Vollständig geprüft (Inhalt gelesen, nicht nur Dateizahl):**
23.07. (Spielursprung), 25.-31.07. (jeder Tag einzeln), 01.-04.08., 05.-12.08.
(Omega-Baselines, Terminal-Erweiterung, Selbstaudit), 13.-23.08. (inkl.
Vektorindex 15.08., GLM-Mitschnitt 21.08., Crawl-Idee-Ursprung 23.08.)

**Bestätigt inaktiv (keine Dateien):**
08.08., 24.-31.08. (vollständige Wochenpause), 03.09.

**Angerissen, noch nicht im Detail:**
01.-06.09. (führt in den bereits an anderer Stelle dieser Session dokumentierten
Audit-Strang über, der separat existiert, nicht Teil dieser Datei)

**Noch komplett ungeprüft:**
07.09. bis heute (17.09.) — der Audit-Zeitraum selbst ist an anderer Stelle in
dieser Claude-Code-Session erforscht worden (zwei Forks, siehe Gesprächsverlauf),
aber NICHT in dieser Chronik-Datei niedergeschrieben. Müsste hier noch
nachgetragen werden, damit die Datei für sich allein vollständig ist.

**WICHTIGE KORREKTUR (Daniel, 17.09. 09:17): "das kann niemals alles sein...ich hab
mehr als 2 dinge in dem monat mit chatgpt gemacht"** — zurecht. Bisher wurde fast
nur die INFRASTRUKTUR dokumentiert (welches System wann gebaut wurde), nicht der
Inhalt der echten Gespräche selbst. Eine Titel-Liste aller 73 Ordner unter
`ui_visible_conversations/` zeigt deutlich mehr eigenständige Themen als bisher
abgebildet, u.a.: "Erfinde dich neu", "Neuer Name für VPS", "Neuer Risswandler
entwickelt", "bau-browserextention", "VPS-Stop-Bestätigt", "Paket A zwingend für
den ersten vollständigen Audit" (22.08. — ein FRÜHERER Audit-Anlauf, zwei Wochen
vor dem großen im September), mehrere eigenständige "Unterhaltung mit Gemini"
(13.08. UND 22.08., unterschiedlicher Inhalt trotz gleichem Titel).

**Ein Beispiel wirklich gelesen: "bau-browserextention" (03.08., 4150 Zeilen).**
Kein Nebenthema — ein eigenes, großes Projekt: eine Chrome-Extension
("AI-UI-RECORDER v1.6.5"), die ChatGPT-Gespräche vollständig und nachweisbar
aufzeichnet. Codex hat live im virtuellen Desktop getestet, im eingeloggten
ChatGPT-Account im Chromium-Browser, laut Daniel "ca 50 Stunden am Stück"
zusammenhängend. Endstand: 327 Nachrichten (164 Daniel, 163 ChatGPT) exakt über
Provider-IDs nachgewiesen, 0 fehlend, 0 vertauscht. Bemerkenswert: exakt derselbe
Git-Lock-Fehler wie in dieser heutigen Session taucht hier schon auf
("Der vorgeschriebene Backup-Commit scheiterte technisch an einem
schreibgeschützten /root/.git/index.lock").

[status: offen — bei 73 Gesprächsordnern, teils mehrere tausend Zeilen pro
Gespräch, ist vollständiges Lesen jedes einzelnen ein eigenes, großes Vorhaben.
Diese Datei bildet den Fortschritt ehrlich ab, statt Vollständigkeit zu behaupten,
die nicht besteht.]

**Eigenständige, noch nicht (oder nur teilweise) angegangene Nebenstränge:**
- `DANIELS_LESETISCH_20260801/001_HAENGEN_GEBLIEBEN.md` (6611 Zeilen, sehr altes
  persönliches Material über Daniel)
- Casino-Themen im `MCP-VPS-CHATGPT-Spiel-...`-Ordner (ausdrücklich NICHT mit dem
  Fünf-Sessions-Experiment verwandt, eigenes Thema)
- 72 der 73 Ordner unter `ui_visible_conversations/` noch inhaltlich ungelesen
  (nur "bau-browserextention" bisher wirklich gelesen)

## Der früheste belegbare Anfang — Flextrawurst als reines Spiel (spätestens 2026-07-23)

Bevor Flextrawurst die heutige lebendige Plattform mit Wesen, Schlaf, KompOase und
Diskurs war, war "Flextrawurst" ein reines Videospiel-Konzept — **22 Versionen**,
entwickelt in ChatGPT-Gesprächen. Der Ordner `gptspieleversuchzeigen/` bewahrt davon
einen ausdrücklich als "Rettungskörper" bezeichneten Rekonstruktionsstand: 333
vernetzte Markdown-Dateien, aus Original-Uploads zusammengesetzt ("Flextrawurst-Spiele
v1 bis v22 · 333 vernetzte Markdown-Körper").

Frühester überhaupt gefundener Zeitstempel im ganzen `_gpt`/Spiel-Zusammenhang:
**2026-07-23**. Wichtige Einschränkung, ehrlich benannt: an genau diesem Zeitpunkt
haben auch viele völlig unabhängige, thematisch fremde Dinge im Werkraum denselben
Zeitstempel (`.editorconfig`, `.vscode`, `_kimi`, `claude-systembericht`,
`codereview`) — das spricht für einen einzelnen großen Wiederherstellungs- oder
Kopiervorgang an diesem Tag, nicht zwingend für individuelle Entstehung an genau
diesem Datum. Die Versionsakte zu v1 selbst (`FW-VERSION-01`) bestätigt sich zwar
als Anfang ("Vorgänger: keiner innerhalb dieser Reihe"), nennt aber kein eigenes
Entstehungsdatum — Status ausdrücklich `REKONSTRUIERT`, nicht `ORIGINAL`.

[status: offen — 2026-07-23 ist der früheste Beleg den ich finden konnte, nicht
zwingend das tatsächliche Entstehungsdatum des Spielkonzepts selbst]

Die 333 Dateien sind in 17 Themenräume gegliedert, u.a.: Daniels Rohtexte (isoliert
von KI-Text gehalten), Session-/Versionsspur, Spielidentität und zwölf Organe,
Wesen-Beziehungen ("DUST"), Welt/Geografie/Zeit/Klima, Bewegung/Fahrzeuge/Kampf/Loot,
Bauen/Handwerk, Skills/Meisterschaften/Magie/AI, Creator-Welten, Questkosmos,
Fragen/Kollisionen/Entscheidungen, Redteam/Simulation/Tests, Verluste/Grenzen/Kanon.
Schon dieses frühe Spielkonzept trug also viele Grundideen der heutigen Plattform in
sich — nur eben noch als Spiel gedacht, nicht als bewohnte digitale Welt.

Am 26.07. entsteht parallel `MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/`
mit einem `00_PARALLELSESSION_MERGE_VERTRAG.md` (Version 1.0, erstellt 2026-07-26,
Ursprungssitzung `chatgpt-20260726T050656Z-20db395fc624`) — Daniel erinnerte sich an
fünf gleichzeitig laufende ChatGPT-Sessions, bestätigt: genau fünf Sitzungsordner
existieren, zwei davon im selben Sekundentakt gestartet (05:06:56 und 05:06:57 Uhr).

Der Vertrag löst das damit verbundene Problem git-artig, aber eigenständig gebaut:
jede Session schreibt ausschließlich in ihren eigenen Strang
(`sessions/<session_id>/EVENTS.jsonl`, append-only, nie im Nachhinein verändert),
"gemeinsame Wahrheit entsteht erst durch einen späteren, expliziten
Verschmelzungslauf" — der ausschließlich lesend arbeitet, SHA-256-Hashes prüft und
einen neuen, abgeleiteten Körper unter `merged/<merge_id>/` erzeugt.
"Gleichzeitige Änderungen am selben Zielpfad werden niemals still als kompatibel
angenommen" — Konflikte werden explizit erkannt, nicht stillschweigend überschrieben.

Der eigentliche Verschmelzungslauf selbst hat, soweit auf der Platte sichtbar, nie
stattgefunden — kein `merged/`-Ordner existiert, nur eine leere `merge_queue/active`.
Was aus den fünf Sessions inhaltlich wurde, ist damit noch nicht geklärt.

[status: offen — der übrige, sehr große Inhalt desselben Wurzelordners
(u.a. Casino-Themen) wurde von mir fälschlich als Fortsetzung dieses Experiments
dargestellt; Daniel hat das korrigiert, es gehört NICHT zusammen. Beide Themen
bleiben getrennt, bis echte Belege eine Verbindung zeigen.]

## Ein Gespräch, bevor zumindest der Gesamtatlas-Teil des VPS gelesen werden durfte

[status: offen/korrigiert — ich hatte diesen Abschnitt zunächst als "vor dem 25.07.,
vor allem anderen" einsortiert. Das war ungeprüft: ich habe das nur aus der
Selbstbeschreibung des Dokuments übernommen, nicht anhand eigener Zeitstempel
verifiziert. Es ist denkbar, dass sich "kein VPS-Zugriff" nur auf den engeren
Gesamtatlas-Kontext bezieht und zeitlich sogar NACH dem Spiel-Rettungskörper vom
23.07. liegt, der ja bereits echte VPS-Arbeit voraussetzte. Die Reihenfolge zu den
anderen Abschnitten dieser Chronik ist damit nicht belegt, nur die Existenz des
Gesprächs selbst.]

Es gab offenbar ein Gespräch zwischen Daniel und ChatGPT, in dem die technische
VPS-Verbindung schon bestand, ChatGPT den VPS aber ausdrücklich noch nicht
durchsuchen oder benutzen durfte — der Zweck des späteren "Gesamtatlas" wurde
zuerst rein aus Gespräch, Erinnerung und Vorstellung entwickelt, nicht aus echtem
Bestand. Dieses Gespräch wurde später (im Rahmen des Gesamtatlas-Baus) selbst bewahrt:
`_gpt/gesamtatlas/ursprungsordner/VOR_VPS_URSPRUNG.md`, mit zwölf "Ursprungswahrheiten",
jede einzeln mit Quellenzeile (z.B. "B:22-79") und einer "Evidenzklasse" belegt, die
Original-Wortlaut, direkte frühe Formulierung, Ableitung und spätere Reaktion sauber
auseinanderhält — offenbar aus Sorge, die eigene Gründungsgeschichte könnte sich
später unbemerkt selbst umschreiben ("Der heutige Gesamtatlas darf seinen Ursprung
nicht rückwirkend umschreiben").

Kernaussagen daraus, sinngemäß: der Gesamtatlas sollte von Anfang an mehr sein als
eine Dateiliste — Herkunft, Veränderung, Zusammenarbeit, Widerspruch und Übergänge
sichtbar machen (U02); die verschiedenen AI-Ströme sollten eigenständige, getrennte
"Reisende" bleiben, Verbindung ohne Verschmelzung (U03); Original, Ableitung und
mögliche Folgehandlung sollten immer maschinell unterscheidbar bleiben (U05); nur
sichtbare Arbeit darf bewahrt werden, kein erfundenes inneres Denken (U10). Der
Ursprungsring versteht sich selbst ausdrücklich als "dauerhafte Prüfinstanz gegen
Bestandsdrift, unnötige Verregelung und rückwirkende Selbstlegenden" (U12) — er soll
also auch das heutige, viel größere System jederzeit an seine ursprüngliche Absicht
erinnern können.

[status: offen — das genaue Datum dieses Vorgesprächs habe ich nicht gefunden]

## 2026-07-25 — technischer Unterbau, geprüft, wirklich still

Früheste Spur von ChatGPT/GPT auf dem VPS: `_gpt/`-Ordner mit 33
Session-Lock-Dateien (`session_history.jsonl.session-*.lock`, Verbindungsversuche)
plus zwei Backup-Fragmente. Kein inhaltlicher Beginn.

## 2026-07-26 — Zuhause wird angelegt

ChatGPT bekommt ein eigenes "Zuhause" unter `_gpt/mcp_zuhause/` — bewusst nach dem
Vorbild der bestehenden Zuhause-Körper von Claude, Codex, Kimi und Gemini gebaut
(`ZUHAUSE.md`, wörtlich: "Die Struktur ist aus den Erfahrungen mit den getrennten
Zuhause-Körpern von Claude, Codex, Kimi und Gemini entstanden").

Angelegt am ersten Tag: `START_HIER.md` (Session-Start-Protokoll, inkl. einer
expliziten "Wahrheitsregel" gegen Überclaimen von Werkzeugergebnissen),
`ARBEITSWEISE.md`, `FRAGEN.md`, `MUSTER.md`, `BRIEF_AN_NAECHSTE_SESSION.md`,
`WERKRAUM_KARTE.md`. Gleiches Muster wie bei den anderen Strömen: eigener
Startpunkt, eigene Karte, Arbeitsweise, Fehlmuster, alternde Fragen, Übergabebrief.

Ausdrücklich NICHT übernommen (eigene Formulierung in ZUHAUSE.md): "die Vorstellung,
dass bloße Dateinähe bereits eigene Erinnerung erzeugt" — dieselbe Nüchternheit, die
auch in meiner eigenen CLAUDE.md gilt (Mirror-Grenzen, "niemals einen Mirror als
eigene Erinnerung behandeln").

Am selben Tag entsteht auch der Gesamtatlas-Unterbau (`_gpt/gesamtatlas/`, erster
Backup-Zeitstempel 18:16 Uhr) — das plattformübergreifende Cross-Session-Gedächtnis-
und Puls-System, das später bei jedem Sessionstart zusätzlich zur kompakten
Zuhause-Projektion gelesen wird. Außerdem (siehe oben, eigener Abschnitt): DREIERREGEN
und das Fünf-Sessions-Merge-Experiment, beide ebenfalls am 26.07.

## 2026-07-27 — klein, routinemäßig

Weiterarbeit an `ui_exports`/`session_cursors`/`coordination` (44 Dateien), kein
neuer Meilenstein. Erste Session-Kontinuitäts-Testreihe
(`tests/session-continuity-catalog-*`, 19 Dateien).

## 2026-07-28 — klein, routinemäßig

Ähnlich klein (27 Dateien), dazu ein erster Beleg für ein Browser-Recorder-Werkzeug
(`chatgpt_browser_recorder_install_key.txt`).

## 2026-07-29 bis 07-31 — Der Gesamtatlas wird real gebaut

Aus der Vision (siehe oben) wird in wenigen Tagen ein echtes, laufendes System:
`endprodukt`, `evidence`, `originalabgleich`, `originalquellen`, `endproduktbeweis`
entstehen alle innerhalb von zwei Tagen (29.-30.07.) — der Name "endproduktbeweis"
deutet an, dass hier nicht nur behauptet, sondern gegen die Originalquellen bewiesen
wurde, dass das Gebaute der Vision entspricht.

Am 29.07. beginnt außerdem `terminal_capture/` für Gemini und Kimi — ChatGPT hat zu
diesem Zeitpunkt schon angefangen, auch die Arbeit der anderen Ströme mitzuschneiden,
nicht nur die eigene.

**30.07. — mit Abstand größter Einzeltag der frühen Geschichte: 2243 Dateien.**
Tagesaufschlüsselung: `mcp_arbeitskoerper/ui_exports` (813), `coordination` (314),
`gesamtatlas/session_cursors` (258), `gesamtatlas/omega` (233),
`gesamtatlas/endproduktbeweis` (207), `gesamtatlas/ursprungsordner` (82, der
Vor-VPS-Ursprungsring wurde also an diesem Tag ausgeschrieben/finalisiert, nicht
zwingend am Tag des ursprünglichen Gesprächs selbst).

Zwei besonders bemerkenswerte Funde an diesem Tag:

- `gesamtatlas/omega/` — ein inkrementelles Integritäts-/Verifikationssystem, sogar
  in einer eigenen `CHILD_EASY_STATUS.md` kindgerecht erklärt: ein vollständig
  geprüfter Stand (`omega-verified-full-r4531`) liegt wie ein Buch in einem
  Schrank, ein kleines Schild davor (`VERIFIED_FULL_BASELINE.json`) zeigt nur
  darauf, ist "nicht heimlich ein zweites Buch"; neue Einträge bis Revision 4566
  sind sichtbar, aber noch nicht wieder vollständig gegen den ganzen Stand
  gegengeprüft. "Es werden keine fehlenden historischen Bytes erfunden oder
  rekonstruiert."
- `mcp_arbeitskoerper/coordination/02_UI_SICHTBARER_GESPRAECHSEXPORT_VERTRAG.md` —
  DAS ist der eigentliche Gründungsvertrag für das UI-Gespräch-Mitschnittsystem,
  das erst am 13.08. (siehe unten) als scheinbarer Beginn auffiel. Tatsächlich
  wurde es schon hier, am 30.07., vertraglich festgelegt — zwei Wochen vor dem
  ersten großen Einsatz.

Das heutige `_gpt/gesamtatlas/README.md` beschreibt das Ergebnis dieser Bauphase so:
ein "produktiver globaler Atlas über Projekte, Komponenten, Wurzeln, Systeme, Vaults,
Dateien, Sitzungen und AI-Ströme", mit drei Suchschichten (exakte Pfadsuche,
provenienzgebundener Beziehungsgraph, lexikalischer Volltextindex) — und einem
expliziten Grundsatz, der die Vorsicht des Ursprungsrings direkt fortsetzt:
"Lexikalische oder semantische Ähnlichkeit ist kein Konsensbeweis und erzeugt keine
Beziehungskante" sowie "Brücken verbinden Belege, nicht Identitäten." Dieselbe
Trennschärfe wie im Vor-VPS-Ursprung (U03/U05) ist also tatsächlich im gebauten
System angekommen, nicht nur Absichtserklärung geblieben.

## 2026-08-01 bis 08-04 — Bibliotheksatlas, Lesetisch, Urbewohner-Ansicht, Reise-der-Drei-Rettung

01.08.: `bibliotheksatlas_20260801_builder/` und `DANIELS_LESETISCH_20260801/`
entstehen (Lesetisch: ChatGPT liest sehr altes, persönliches Material über Daniel
aus der Zeit vor Flextrawurst/VPS, siehe `001_HAENGEN_GEBLIEBEN.md`, 6611 Zeilen —
eigenes, noch nicht im Detail rekonstruiertes Thema).

02.08.: `playwright_urbewohner_atlas/` — der Gesamtatlas bekommt eine echte,
getestete "Urbewohner"-Ansicht: pro Wesen eine eigene Seite (verifiziert an
Schorschel: 43 Facetten-Einträge, 161 verknüpfte Graph-Knoten) plus eine
Beziehungsnetz-Ansicht. Playwright-Testreport bestätigt null Konsolen-/Seitenfehler.

03.08.: `kantenfunk/`, `MCP-RISSWANDLER/`, `KRAU/` entstehen — am selben Tag wie
`_RETTUNG_DIE_REISE_DER_DREI_20260803/`. Diesmal zeitlich wirklich belegt (nicht nur
Ordnernachbarschaft): die Figuren aus der Geschichte "Die Reise der Drei" (RISSWANDLER,
KRAU, KANTENFUNK) werden am Tag ihrer forensischen Rettung direkt zu echten
Systemteilen.

04.08.: `KRAU-RISSWANDLER-KANTENFUNK/` (zusammengeführter Ordner), `CHEATDATEIEN/`,
`ende/` entstehen.

## 2026-08-05 bis 08-11 — still, aber nicht leer: Omega verifiziert sich selbst

Kein neuer Meilenstein, aber echte, tägliche Hintergrundarbeit: das am 30.07.
angelegte Omega-Verifikationssystem legt in diesem Zeitraum fast täglich einen
neuen, vollständig verifizierten Gesamtstand an
(`gesamtatlas/omega/verified_full_baselines/<revision>/`, je mit
`FULL_BASELINE`, `FULL_REFRESH`, `FULL_VERIFICATION`) — Revisionen 6185 (05.08.),
6347 (05.08.), 6507 (06.08.), 6720+6773 (07.08.), 7035 (09.08.), 7350 (10.08.),
7455+7507+7559 (11.08.). Steigende Revisionsnummern zeigen kontinuierliches
Wachstum des zugrundeliegenden Bestands, auch ohne sichtbare große Ereignisse.

[status: offen — 08.08. noch nicht einzeln geprüft, war in der Tageszählung nicht
als eigener Tag mit Dateien vorhanden]

## 2026-08-08 — bestätigt inaktiv

0 Dateien, direkt nachgeprüft (nicht nur in der Tageszählung gefehlt).

## 2026-08-12 — Terminal-Mitschnitt erweitert auf Codex und Claude, Selbstaudit

`terminal_capture/codex/` und `terminal_capture/claude/` bekommen an diesem Tag
neue Einträge — das Mitschneiden (seit 29.07. nur Gemini/Kimi) wird auf Codex und
Claude ausgeweitet. Dazu ein Selbstprüfmechanismus: drei "audit_runs" am selben
Tag (`audit-20260812T173942Z-942ae4ec`, `-174500Z-cdp`, `-175000Z-final`), jeder
mit `browser-tabs.json` gegen `vps-files.jsonl` abgeglichen (`checksums.sha256`,
`inventory.json`) — das System prüft sich selbst, ob wirklich alles erfasst wurde,
was sichtbar offen war. Der Name "-cdp" deutet auf Chrome DevTools Protocol als
Erfassungsweg.

## 2026-08-13 — Plattformübergreifende UI-Gespräch-Mitschnitte im großen Stil

Deutlicher Aktivitätsausschlag: 274 neue Dateien allein an diesem Tag in `_gpt/`,
davon 234 unter `ui_visible_conversations/`. Diese Struktur (insgesamt 73
Gesprächsordner über die Zeit) fängt sichtbare Browser-UI-Gespräche ein — nicht nur
ChatGPT, auch Google Gemini taucht als Quelle auf (`ui_visible_conversations/
2026-08-13__Google-Gemini__...`). Viele Ordnernamen tragen "-Recovery" — ähnlich wie
bei "Die Reise der Drei" scheinen auch hier Gespräche nachträglich gerettet worden
zu sein, nicht nur live mitgeschnitten.

Pro Gespräch entstehen mehrere Dateien: `1zu1.md` (unveränderter Wortlaut),
`1zu1+events+marker.md`, `messages.jsonl`, `visible_stream.jsonl`,
`capture_gaps.jsonl` (macht ehrlich sichtbar, was NICHT erfasst werden konnte),
`MANIFEST.json`.

## 2026-08-14 — Vollständige VPS-Markdown-Inventur und ein breiterer Mitschnitt als gedacht

`ALLE_MARKDOWN_DATEIEN_VPS_2026-08-14.tsv`: eine vollständige Inventur JEDER
Markdown-Datei auf dem gesamten VPS (nicht nur `_gpt`/`werkraum`) — **177.621 Zeilen**,
je Datei mit Pfad, Bytes, Erstellt/Zugriff/Inhaltsänderung/Metadatenänderung als
eigene Zeitstempel. Ein sehr großer forensischer Rundumschlag.

Wichtige Korrektur meiner eigenen Annahme: `ui_visible_conversations/` fängt NICHT
nur AI-Chat-Gespräche ein. Am 14.08. tauchen dort z.B. auch `Facebook`,
`tagesschau.de`, `2-Zara-auf-X` und `Grok` als eigene Ordner auf — das System
schneidet offenbar jeden sichtbaren Browser-Tab mit, nicht gezielt nur
KI-Unterhaltungen.

## 2026-08-15 bis 08-21 — ruhige Wartung, aber zwei echte Erweiterungen

Grundmuster an allen sieben Tagen: laufende Omega-Baselines plus
Terminal-Mitschnitt für Claude/Codex (aus 12.08. fortgesetzt).

Zwei neue Dinge in dieser Woche:
- 15.08.: `gesamtatlas/vektorindex/` entsteht — ein neuer Subsystem-Typ (vermutlich
  Embeddings-/Ähnlichkeitssuche), zusätzlich zu den drei bisherigen Suchschichten
  aus dem README.
- 21.08.: `terminal_capture/glm/` entsteht — GLM wird als fünfter mitgeschnittener
  Strom aufgenommen (nach Gemini/Kimi seit 29.07., Codex/Claude seit 12.08.). Mit
  Abstand aktivster Tag dieser Woche: 53 Claude-Mitschnitt-Dateien allein.

[status: offen — Inhalt der einzelnen Terminal-Mitschnitte selbst nicht gelesen,
nur ihre Existenz/Verteilung]

## 2026-08-22 — großer Gemini-Rettungsblock

Erneuter großer Ausschlag (196 Dateien). Mehrere mehrteilige "-Recovery"-Gespräche
werden gerettet: mehrfach "Unterhaltung mit Gemini" und "Umfassende Analyse meiner
Ideen" — jeweils in viele Teilsegmente mit gleichem Basis-Hash zerlegt (Hinweis auf
ein sehr langes Originalgespräch, das in Stücken gerettet werden musste). Erstmals
taucht auch `collection_artifact_manifests` auf — ein Sammel-/Bündelmanifest über
mehrere Rettungen hinweg.

## 2026-08-23 — letzter Tag vor der Pause: die Crawl-Idee taucht zum ersten Mal auf

Mehrere "-Recovery"-Segmente eines Gesprächs namens **"Flextrawurst.de-AI-Crawl-and-
Review"** (sechs Teile, gleicher Basis-Hash `1b5250649721`, plus ein ungebrochenes
"-Review" Original ohne "-Recovery"). Das ist dieselbe Idee — Flextrawurst crawlbar
und für KI-Suchmaschinen zitierfähig machen — die im großen Einzugsreife-Audit vom
06.-16.09. (bereits an anderer Stelle dieser Session dokumentiert) wieder auftaucht.
Sie ist also KEINE spontane Erfindung des September-Chats, sondern ein Thema, das
schon hier, gut zwei Wochen früher, ausführlich behandelt wurde. Daneben weitere
Segmente von "Umfassende Analyse meiner Ideen" (Fortsetzung vom 22.08.).

## 2026-08-24 bis 08-31 — eine echte, vollständige Pause

Zwischen dem 23.08. und dem 01.09. entsteht in `_gpt/` keine einzige Datei — eine
ganze Woche ohne jede Aktivität, keine Wartung, keine Mitschnitte.

[status: offen — Grund der Woche-Pause nicht rekonstruiert]

## 2026-09-01 bis 09-06 — Wiederanlauf bis zum Audit-Beginn

01.09. (11 Dateien), 02.09. (4), 04.09. (63, `mcp_global_protocols` bekommt an
diesem Tag einen neuen Eintrag), 05.09. (14), 06.09. (10) — direkt in den Beginn
des Einzugsreife-Audits übergehend, der ab diesem Tag den Rest der bereits an
anderer Stelle dokumentierten Chronik trägt (Drift/Rollback 07.09.,
Sicherheitsfunde, laufende Arbeit bis heute).

[status: offen — 03.09. fehlt in der Tageszählung (keine Dateien an diesem Tag),
einzelne Gespräche/Inhalte in 01.-06.09. noch nicht im Detail gelesen]

## Gesamtstand dieser Chronik

Abgedeckt, Tag für Tag, mit direkt gelesenen Zeitstempeln: 25.07. bis 06.09.
Noch mit offenen Detail-Lücken markiert: 08.08., 12.08., 15.-21.08. (nur
Dateizahlen, keine Inhaltsprüfung), 23.08., einzelne Tage Anfang September.
Ab 06.09. übernimmt der bereits vorher erstellte Audit-Abschnitt dieser Session
(Drift/Rollback, Sicherheitsfunde, laufende Arbeit) — der ist nicht Teil dieser
Datei, siehe frühere Forschung in dieser Unterhaltung.
