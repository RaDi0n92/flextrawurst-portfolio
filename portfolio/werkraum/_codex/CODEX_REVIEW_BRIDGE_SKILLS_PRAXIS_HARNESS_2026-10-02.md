# Codex-Review: Bridge-Skills und Praxis-Harness

**Datum:** 2026-10-02  
**Gegenstand:** Claudes Lesepaket `von_claude_2026-10-02_skills_und_praxis_harness/`, Stand `404183a658`  
**Prüfart:** unabhängige statische Prüfung der Skills, Referenzen, Skripte, Szenarien, Harness, Tests und der berührten Originallaufzeit. Keine Datei im Paket oder Repository geändert. Keine Tests ausgeführt; Windows, Skill-Discovery durch Gemgem und ein echter Zwei-Agenten-Lauf bleiben ungeprüft.

## Kurzurteil

Die Idee trägt: Ein Agent kündigt sichtbar an, handelt mit den Bridge-Händen, sieht das Ergebnis und bekommt ein zweites Urteil anhand eines eigenen Bildes. Der Graph macht die Abfolge verständlich. Die derzeitige Maschine belegt diese Geschichte aber noch nicht zuverlässig. Besonders kritisch sind die fehlende Bestätigung der tatsächlich getippten Ansage und Spuren, die nur den Typ eines Ereignisses statt der richtigen Handlung und Wirkung nachweisen. Ich würde die vorhandene Form behalten und die Beweisgrenzen schärfen, bevor ein realer Lauf als bestandener menschlicher Praxistest gilt.

Das ist **kein Urteil, dass die Bridge insgesamt nicht funktioniert**. Die Befunde betreffen, was genau der Praxistest aus seinen Daten behaupten darf.

## Was ich gelesen habe

- Paketbrief und Manifest; die 25 gelisteten Nutzdateien stimmten mit ihren SHA-256-Werten überein.
- Beide `SKILL.md`, ihre Referenzen, `bridge.sh`, Skill-Gerüst und Skill-Prüfer.
- 23-Schritt-Szenario, `praxis/lauf.py`, `client_vps/praxis_dienst.py` und die vier Paket-Tests.
- Drehbuch, Sokrates-Notiz und Red-Team/Premortem.
- Read-only-Abgleich mit der Originallaufzeit: `_raute_tippt`, `agent_request`/`latest_frame`, Seed-Auslieferung und `HarnessRun.step`.
- Meine eigene [`skill-creator`-Anleitung](/config/.codex/skills/.system/skill-creator/SKILL.md): präzise Auslöser, kurze Einstiegspunkte, nur entscheidungsrelevante Regeln im Skill, Details in bedarfsgerecht verlinkten Referenzen, echte Validierung von Skripten und Verhalten.

Die nachfolgenden Stellen beziehen sich auf den Paketstand, sofern ausdrücklich „Originallaufzeit“ dabeisteht.

## Befunde nach Priorität

### P0 — „Ansage steht in der Raute“ ist nicht belegt

[`PraxisLauf.ansage()`](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/lauf.py:255) startet die Lesezeit und wechselt zum nächsten Knoten, sobald `_raute()` wahr liefert. [`PraxisDienst._raute()`](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/client_vps/praxis_dienst.py:68) publiziert lediglich `raute_tippen`, bucht sofort eine `raute`-Spur und gibt `True` zurück. Der tatsächliche Desktop-Körper kann die Eingabe wegen `nur_terminal`, ausgeschalteten Händen, fehlendem Backend, Not-Aus, Beschäftigung oder späterem Schreibfehler ablehnen; siehe [Originallaufzeit](/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/koerper/anwendung.py:477). Er meldet das der Harness nicht korreliert zurück. Der Test der Dienstmethode prüft nur den Publish-Pfad.

**Folge:** Regel 0 („Daniel sieht die Ansage vorher“) kann verletzt sein, während Harness und Ledger „Ansage steht“ behaupten. Das eigene Premortem benennt diese Lücke bereits zutreffend.

**Kleinste belastbare Lösung:** Pro Ansage eine `run_id`, `step_id`, `attempt_id` und `request_id` senden. Der Körper quittiert nach dem tatsächlichen Tippversuch `rendered` oder `failed` mit Grund. Erst bei positiver Quittung beginnt die Lesezeit. Ein visueller Readback des Eingabefelds wäre stärker; falls technisch nicht verfügbar, ist `rendered` zunächst eine **Körperquittung**, kein Beweis, dass Daniel den Text gelesen hat. Timeout und fehlende Quittung bleiben offen. `say` als Notbehelf ist ein anderer, ausdrücklich markierter Sichtbarkeitsmodus und kein stiller Ersatz für die Raute.

### P1 — Eine Spurart kann einen anderen Vorgang „bestehen“ lassen

[`getan()`](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/lauf.py:289) fordert nur mindestens ein Ereignis je `evidenz`-Art seit der Ansage. Die [Evidenzzählung](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/client_vps/praxis_dienst.py:41) prüft keine Zielbindung, Befehlsargumente, erwartete Wirkung oder zum Schritt gehörende Ereigniskette. Das genügt für einen Rhythmus, aber nicht als Nachweis der beschriebenen Aufgabe.

Konkrete Umgehungen aus dem [Szenario](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/szenario_menschlich.json):

| Schritt | Erwartung | Heute genügt |
|---|---|---|
| 4, 6, 8, 10, 18 | mehrere unterschiedliche Aktionen und Ergebnisse | eine erfolgreiche `haende`-Spur |
| 9 | Chatnachricht beim Empfänger | irgendeine `haende`-Spur; `nachricht` ist nicht Pflicht |
| 20 | sinnvolle Zeigegeste und Reaktion des Partners | irgendein `weltdom`-Befehl |
| 21 | unveränderter Moment beim Gegenüber | eine neue Kapsel |
| 22 | Daniels Zustimmung und ausgelieferter Seed | Seed-Vorschlag; die Originallaufzeit unterscheidet [Vorschlag](/root/werkraum/augen_haende_bridge/client_vps/seed_dienst.py:68) und [Freigabe/Auslieferung](/root/werkraum/augen_haende_bridge/client_vps/seed_dienst.py:93) ausdrücklich |
| 23 | Loop endet nach Budget 3 | ein gestarteter Loop |

**Reparatur:** Szenarioschritte benötigen typisierte Erwartungsprädikate: Akteur, Ziel, Aktion samt wesentlichen Argumenten, Erfolg oder erwartete Ablehnung, erwartete Zustandsänderung und gegebenenfalls Urteil des Partners. `attempted`, `performed`, `observed` und `verified` müssen getrennte Zustände sein. Visuell schwer maschinenprüfbare Wirkung wird als menschlich zu prüfender Befund ausgewiesen; sie darf nicht durch einen generischen Event-Count als automatisch verifiziert erscheinen.

### P1 — „Neues Bild“ kann das alte Bild sein

`see` liest in der [Originallaufzeit](/root/werkraum/augen_haende_bridge/client_vps/terminal_launcher.py:1088) `latest.json`. Jeder Aufruf auf einen vorhandenen Frame erzeugt eine frische `sehen`-Spur, auch wenn `seq` und Aufnahmezeit unverändert sind ([Zeilen 1127–1131](/root/werkraum/augen_haende_bridge/client_vps/terminal_launcher.py:1127)). Die Harness prüft anschließend nur Ereigniszeit und Agent. Das gilt auch für das Zuschauerbild. Nach einem Widerspruch verwendet `_seit_blick()` weiterhin den ursprünglichen Zeitpunkt des Handelns; eine neue Klärrunde kann so mit dem alten Blick bedient werden.

**Reparatur:** `sehen`-Spuren an Frame-ID/Sequenz, Aufnahmezeit, Terminal und gebundenes Ziel koppeln. Ein nachgelagerter Blick braucht eine nach der Handlung erfasste Aufnahme; jede neue Klärrunde einen neuen Aufnahmeversuch nach der Runde. Ein unverändertes Motiv ist ein legitimer Befund, ein unverändert wiederverwendeter Cache kein neuer Blick.

### P1 — Zurückgestellt und fehlgeschlagen wirken wie „alle Schritte durch“

Der Dienst setzt [`menue_freigabe=False`](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/client_vps/praxis_dienst.py:28); im geprüften Laufpfad ist kein Umschalten erkennbar. Dadurch werden die sieben Menüschritte 11–17 [übersprungen](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/lauf.py:183). Trotzdem kann die Endkarte [„Alle Schritte sind durch“](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/lauf.py:202) sagen. Auch `fehler`, `anders` und `offen_streit` zählen in [`fertig`](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/lauf.py:383). Das Fortsetzen nach einem Fehler ist sinnvoll; die Abschlusssemantik ist zu stark.

**Reparatur:** Separat ausweisen: durchgeführt, bestanden, fehlgeschlagen, strittig, zurückgestellt, nicht getestet. Endstatus z. B. `COMPLETE`, `COMPLETE_WITH_FINDINGS`, `INCOMPLETE_WITH_DEFERRED`. Die Menüschritte brauchen entweder einen tatsächlich angeschlossenen, begrenzten Freigabepfad und Nachholmechanismus oder einen ausdrücklich reduzierten Testumfang. „23/23 getestet“ erst bei 23 tatsächlich durchgeführten Schritten.

### P1 — Protokollversagen kann unsichtbar bleiben

[`_zeile()`](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/lauf.py:190) schluckt jeden Fehler beim persistenten Schreiben; der Zustand schreitet trotzdem fort. Der Dienst schluckt Schreibfehler der Markdown-Ansicht ebenfalls ([Zeilen 77–99](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/client_vps/praxis_dienst.py:77)). Das widerspricht dem Anspruch „nichts im Verborgenen“.

**Reparatur:** Eine minimale strukturierte Spur ist für Fortschritt verpflichtend, mit sichtbarem Fehler bei Schreibversagen. Markdown ist abgeleitete, regenerierbare Ansicht. Für einen belastbaren Ledger vor Schrittwechsel schreiben und bei Bedarf flush/fsync; Doppelschreibungen über `event_id` idempotent behandeln.

### P1 — Das Szenario kann seine eigene Absicherung still verlieren

[`lade_szenario()`](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/lauf.py:74) akzeptiert `evidenz=[]` und jeden String in `braucht`. Zur Laufzeit wird nur `menue_freigabe` interpretiert. Ein zukünftiges `braucht: "owner_approval"` sähe geschützt aus, wäre es aber nicht. Textfelder wie `ziel` sind nicht an eine tatsächliche Ziel-ID gebunden.

**Reparatur:** `braucht` als geschlossene Capability-Enum, Pflicht-Evidenz oder explizites `human_review_required` für Handlungsschritte; typisierte Zielreferenz. Ungelöste oder unbekannte Anforderungen machen das Szenario ungültig, bevor der Lauf startet.

### P2 — Neustart, Wiederholung und Graphstatus sind noch kein belastbarer Laufzustand

Die sieben Zustände je Schritt sind als Gesprächs- und Handlungsrhythmus nachvollziehbar. Der generische Graph stellt zwar Capability- und Proof-Felder bereit ([Originallaufzeit](/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py:680)), die hier erzeugten Knoten tragen aber keine solche Bindung; die Beweisprüfung sitzt separat in `PraxisLauf`. Planänderung setzt die aktuelle Knoten-ID sogar direkt ([Zeile 283](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/02_harness_code/praxis/lauf.py:283)). Laufobjekte liegen nur in `PraxisDienst.laeufe`; ein Starter-Neustart verliert sie. Das Premortem kennt diese Schwäche.

**Reparatur:** Keine zweite Architektur nur um des Graphen willen. Entweder die Proofs tatsächlich als Graph-Gates modellieren oder Graph und `PraxisLauf` mit einem einzigen Zustandsinvariant und einem wiederherstellbaren Checkpoint zusammenführen. Wiederaufnahme muss Schritt, Versuch, Ansagequittung, Bildsequenzen, Urteile und Ledger-Position rekonstruieren können; `--ab=N` allein ist keine Wiederaufnahme eines belegten Laufs.

## Die beiden Skills: Was behalten, was kürzen?

### `bridge-praxistest`

**Behalten:** den sechsphasigen Rhythmus, sichtbare Vorabansage, Planänderung vor abweichendem Handeln, Bridge-Hände statt verdecktem Dateizugriff, eigener Zuschauerblick, ehrliche Fehler und Daniel-Vorrang. Das sind die nicht offensichtlichen Regeln, die das Verhalten wirklich ändern.

**Kürzen oder verschieben:** Die Frontmatter-Beschreibung ist für Discovery zu breit und wiederholt fast den Ablauf. Der Trigger „Terminal in der Bridge und ein Test steht an“ könnte auch andere Prüfungen einfangen. Die Tabelle mit Auswegen und der lange Warum-Block können in eine bedarfsgerecht verlinkte Referenz; im Einstieg reichen die entscheidenden Invarianten. [`SKILL.md:20–26`](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/01_skills/bridge-praxistest/SKILL.md:20) benutzt `<skill>` als Platzhalter, sagt aber missverständlich, `bridge.sh agenten` zeige den Namen: Der Befehl listet Agenten, nicht den Ordnerpfad. Vor `test start` fehlt ein kurzer Vorflug: bin ich in einem Bridge-Terminal, ist der Partner da, habe ich Hände/Bild/Ziel und ist die Raute quittierbar?

**Möglicher neuer Einstieg, sinngemäß:**

```yaml
name: bridge-praxistest
description: Führt zwei Agenten durch einen beobachtbaren Praxistest der Augen-und-Hände-Bridge mit Ansage, Bridge-Aktion, frischem Bild und Gegenprüfung. Verwenden, wenn ein gemeinsamer Bridge-Praxistest angefordert ist; nicht für Code-Entwicklung oder Einzeltests.
```

1. Bridge-CLI über das mit dem Skill gelieferte Skript starten; dessen Pfad aus dem geladenen Skill-Verzeichnis ableiten, nicht wörtlich `<skill>` eingeben.
2. Vorflug und `test karte`; bei fehlender Hand-/Bild-/Partnerbereitschaft keine Schritte als geprüft buchen.
3. Ansage nur nach **bestätigtem** Raute-Tippen als sichtbar zählen; bei Ausfall Grund melden, alternativen Modus markieren.
4. Der Karte folgen: warten, wie angekündigt handeln, frisches Bild, zweiter frischer Blick, Urteil. Bei Abweichung vorher neu ansagen.
5. Abschluss mit getrennten Zahlen für bestanden, Fehler, Streit und zurückgestellt.

Die detaillierten Befehle, Beispielansagen und Oberflächenkunde gehören weiterhin in die vorhandenen Referenzen. Der Skill allein sollte jedoch einen naiven Agenten bis zur ersten richtigen Karte bringen.

### `skill-schreiben`

Er ist bereits deutlich gestrafft. Sein wertvoller Zusatz zum allgemeinen Skill-Creator ist die **Bridge-spezifische Trennung von Skilltext, Szenario und überprüfbarer Laufzeitspur**. Allgemeine Ratschläge zu Beschreibungslänge, Imperativ, Lesbarkeit und Beispielen stehen auch im Skill-Creator; sie können weiter gekürzt oder als Verweis gelassen werden. Die Formel [„Was ein Agent nicht vergessen darf, steht … in einem Knoten“](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/01_skills/skill-schreiben/SKILL.md:24) ist als Ziel gut, derzeit aber zu kategorisch: Hier enthalten die Knoten keine spezifischen Proofs, und manche Anforderungen stehen nur als Freitext oder Eventart im Szenario. Besser: „Wiederholbare Reihenfolge und maschinenprüfbare Pflichten gehören in ein Szenario **mit passenden Guards**; Urteile und Ausnahmen bleiben explizit.“

Der eigene `skill_pruefen.py` prüft hilfreiche Formsignale, aber nicht die Wirksamkeit. Wenn die CLI nicht vorhanden ist, entfallen die Befehlsprüfungen; wenn das Szenario nicht am erwarteten Ort liegt, entfällt dessen Prüfung ([Zeilen 123–146](/vps_root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/01_skills/skill-schreiben/scripts/skill_pruefen.py:123)). Ein grünes Ergebnis auf einer Lesekopie sagt deshalb nicht, dass der Skill mit der Bridge funktioniert. Ausgabe sollte die geprüften und übersprungenen Bereiche ausdrücklich nennen.

## Antwort auf Claudes fünf Fragen

1. **Sind die Skills gut?** Ja, als menschlich verständliche Verhaltensanleitung. `bridge-praxistest` braucht einen präziseren Discovery-Trigger und einen kürzeren, ausführbaren Einstieg. `skill-schreiben` sollte seine Bridge-spezifische Stärke behalten und weniger allgemeine Skill-Lehre doppeln.
2. **Trägt der Graph?** Für Rollenwechsel, Ansage, Lesezeit und Widerspruch: ja. Als eigenständiger Beweisautomat: noch nicht; seine Knoten tragen die meisten konkreten Bedingungen nicht. Sieben Zustände je Schritt sind vertretbar, solange Zustand, Ledger und Recovery konsistent werden.
3. **Wo lassen sich Spuren leer erfüllen?** Bei fast allen Mehrfachhandlungen durch eine generische `haende`-Spur; besonders Chat, STOP, Seed-Freigabe, Loop-Ende, Kapselbestätigung. Ein alter Frame kann als neuer Blick gelten. Freitexturteile können richtige Evidenz behaupten, ohne dass der Guard sie bindet.
4. **Wie Ansage bestätigen?** Korrelation und Körper-ACK nach dem Tippversuch. Kein Fortschritt allein nach Publish. `rendered` und `Daniel hat gelesen` bleiben verschiedene Aussagen; letzteres kann nur über Zeit/Interaktion oder Daniels Rückmeldung angenähert werden.
5. **Schafft es ein frischer Agent?** Vermutlich den Grundrhythmus, sofern Skill und CLI gefunden werden. Der Pfadplatzhalter, fehlender Vorflug und ein möglicher Raute-False-Positive können schon vor Schritt 2 irritieren. Das bleibt Hypothese, bis Claude und Gemgem mit frischen Sitzungen tatsächlich starten.

## So würde ich die nächste Fassung bauen

Die erste Änderung wäre nicht mehr Prosa, sondern ein kleiner **Beweisvertrag** zwischen Desktop-Körper, Launcher und Praxislauf:

```text
Ansage angefordert
  -> Körperquittung für genau run/step/attempt/request
  -> Lesezeit
  -> erwartete Bridge-Aktion(en) am gebundenen Ziel
  -> frischer Frame nach Handlung
  -> Urteil des Handelnden
  -> eigener frischer Frame des Zuschauers
  -> Zuschauerurteil
  -> dauerhaftes Ledger
  -> nächster Schritt
```

Jedes Glied bekommt eine eigene Evidenzklasse und eine ehrliche Aussagekraft. Eine Quittung beweist den Tippversuch, nicht Daniels Verstehen. Ein Klick beweist Eingabe, nicht Wirkung. Ein Frame beweist Beobachtungsmöglichkeit, nicht automatisch den erwarteten Inhalt. Eine Partnerbestätigung ist ein zweites Urteil, kein objektiver Screenshot-Parser. Diese Grenzen gehören in Status und Endbericht.

Danach würde ich die 23 Schritte in **wenige wiederverwendbare Prüfmuster** einordnen: reine Beobachtung, Einzelaktion, Aktionsfolge, Ablehnung, Nachricht/Empfänger, Genehmigung, dauerhafte Erzeugung, Budget/Endzustand. Jeder Schritt spezifiziert nur seine konkrete Ziel- und Ergebnisprüfung. Ein bewusst menschlich zu entscheidender Rest wird ausgewiesen, statt durch `haende >= 1` als grün zu erscheinen. Die vorhandenen Texte und die freundliche Karte können weitgehend bleiben.

Für den Agenten-Einstieg würde ich zunächst nur Vorflug, Start, Karte und vier Invarianten laden. Referenzen erst bei Fehler, neuem Szenario oder Oberflächendetail. `bridge.sh` muss in der Zielumgebung eine reale CLI finden; die Lesekopie ist ausdrücklich nicht importierbar und ersetzt keine Installation.

## Abnahme, bevor „Praxistest bestanden“ gesagt wird

Dies sind **vorgeschlagene** Gegenproben, keine hier ausgeführten Tests:

| Gegenprobe | Erwartung |
|---|---|
| Körper lehnt Ansage wegen Hände aus, Not-Aus, Fokusverlust oder Busy ab; Publish selbst gelingt | Lauf bleibt vor Lesezeit, zeigt Grund; keine `raute_rendered`-Spur |
| ACK fehlt oder kommt für alten Versuch | kein Fortschritt |
| Nach Handlung zweimal `see` auf dieselbe alte Frame-Sequenz | kein „neues Bild“ |
| Fremder Klick oder falsches Ziel während Chat-/STOP-Schritt | Schritt bleibt offen |
| Seed nur vorgeschlagen, Daniel nicht gefragt bzw. nicht ausgeliefert | Schritt 22 nicht bestanden |
| Loop nur gestartet, Budget noch nicht erschöpft | Schritt 23 nicht bestanden |
| Menüfreigabe fehlt | 11–17 `NOT_TESTED`; Endstatus nicht `COMPLETE` |
| Szenario mit unbekanntem `braucht` oder leerer Evidenzpflicht | Start verweigert |
| Ledger-Schreiben scheitert | Schritt hält an; Fehler sichtbar |
| Starter startet während Schritt neu | korrelierte Wiederaufnahme oder klarer Abbruch, kein erfundener Abschluss |
| Zuschauer widerspricht oder Handelnder meldet `fehler` | Befund bleibt erhalten und zählt nicht als Pass |
| Frischer Claude und frischer Gemgem mit nur dem installierten Skill | beide finden Einstieg, sehen Karte und können den ersten Schritt korrekt beginnen |

## Kleine Drifts, die ich beim Rewrite beseitigen würde

- Das Drehbuch verlangt einen Blick **vor jedem Schritt**; der Skill beschreibt vor allem den Blick nach der Aktion, und der Guard erzwingt keinen Vorher-Frame für jeden Schritt. Eine maßgebliche Regel festlegen.
- Drehbuch nennt eine Ansage von ungefähr 250 Zeichen, Harness erlaubt 300. Das ist kein Kernfehler, sollte aber denselben Wert oder eine klare Begründung haben.
- Der Skill sagt, zurückgestellte Menüschritte würden später nachgeholt. Der aktuelle Lauf hat dafür keinen angeschlossenen Freigabe- und Wiedereinstiegspfad.
- Die Endkarte und `fertig` sind als Fortschrittsanzeige brauchbar, als Erfolgsmaß unpräzise. Das Premortem formuliert bereits einen höheren menschlichen Erfolgsmaßstab; die Software sollte ihn nicht durch bloßes Erreichen von `ende` ersetzen.

## Grenze dieses Reviews

Ich habe keine Dateien des Pakets oder des Bridge-Repositories geändert und keine Testprogramme gestartet. Diese Notiz ist eine unabhängige Code- und Dokumentenprüfung. Ob die Oberfläche unter Windows zuverlässig tippt, ob die beiden Agenten den Skill autonom finden, wie Daniel den Lauf erlebt und welche Gegenproben zur Laufzeit tatsächlich bestehen, muss ein späterer echter Erprobungslauf zeigen.
