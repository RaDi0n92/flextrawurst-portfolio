# Agenten-Scan: vertiefte Analyse für Program Harness und Observing Controller

**Stand: 7. Oktober 2026**

## Lese- und Beleggrenze

Ich habe die fünf im Agenten-Scan genannten Primärtexte direkt in ihrer HTML- oder PDF-Fassung gelesen und ihre fachlichen Hauptteile, Methoden, Ergebnisse und relevanten Anhänge geprüft. Für diese Analyse habe ich kein Skript und keinen Reader zum Zusammenfassen der Papers verwendet. Die Literaturverzeichnisse habe ich nicht als eigenständige Quellen noch einmal vollständig geprüft. Eine zusätzliche Arbeit zum Reward Hacking steht am Ende; von ihr war hier nur der Abstract zugänglich, deshalb behandle ich sie ausdrücklich nur als Zusatzhinweis.

Protokolle können zeigen, welche Datei, Textbereiche, Werkzeuge und Änderungen ein System tatsächlich durchlaufen hat. Sie können nicht beweisen, dass ein Modell einen Text innerlich verstanden hat. Die Regeln unten belegen daher beobachtbare Vorgänge und begrenzen Aussagen darauf; sie behaupten keinen messbaren „Gedankenleser“.

## Kurzfassung

Die Arbeiten ergeben zusammen eine klare Architekturregel: **Das Harness muss getrennt belegen, was das System gesehen hat, was es getan hat und wodurch der Erfolg festgestellt wurde.** Ein Toolname aus einer Liste zu entfernen reicht nicht als Berechtigungsschutz. Ein erfolgreicher Endzustand beweist nicht, dass der vorgesehene Weg benutzt wurde. Ein Skript, das eine Datei misst oder umformt, beweist nicht, dass das Modell ihren Inhalt vollständig gelesen oder den neuen Text selbst verfasst hat. Und ein zweiter Agent ist kein unabhängiger Reviewer, wenn er nur die Zusammenfassung oder dieselben ungeprüften Zwischenergebnisse übernimmt.

Für deine Augen-&-Hände-Bridge heißt das praktisch:

1. Jede Aktion – GUI, MCP, Dateizugriff, Shell, API und Unterprozess – muss durch denselben Berechtigungs- und Beobachtungspfad laufen.
2. Lesestatus, tatsächliche Textabdeckung, mechanische Verarbeitung und inhaltliche Prüfung müssen getrennt protokolliert werden.
3. Änderungen brauchen einen nachvollziehbaren Vorher-nachher-Vergleich samt Urheber- und Transformationsangabe.
4. Der Reviewer sollte die Originalquelle, den Diff und den unabhängig geprüften Endzustand sehen, nicht nur die Zusammenfassung des ausführenden Agenten.
5. Ein Modus „keine Skripte“ muss auch Shell, Interpreter, Unterprozesse und alternative Schreibwege sperren. Nur Bash zu sperren wäre keine vollständige Sperre.

---

## Die fünf Arbeiten

### 1. Zero-Trust Authorization and Discovery for Enterprise MCP

**Datum und Quelle:** 18. September 2026, arXiv: [2609.22573](https://arxiv.org/abs/2609.22573)

**Worum es geht:** Die Autoren prüfen sechs MCP-SDKs und untersuchen, ob ein Server verschiedene Identitäten sauber behandeln kann – etwa einen menschlichen Nutzer mit Unternehmens-SSO und eine Automatisierung mit Service-Account. Sie finden Lücken bei mehreren Identitätsarten, bei der Werkzeug-Entdeckung und bei Berechtigungen pro Werkzeug. Als FastMCP-Erweiterung verbinden sie Identitätsprüfung, gefilterte Werkzeuglisten und eine Berechtigungsprüfung beim tatsächlichen Aufruf.

**Was die Ergebnisse zeigen:** In ihrem Test mit vier Modellen und 2.160 Versuchen führten einfache Prüfungen innerhalb des Werkzeugcodes im Baseline-Setup dazu, dass Modelle verbotene Werkzeuge weiterhin häufig anzufordern versuchten: 152 von 720 Versuchen. Das bedeutet nicht, dass diese 152 Aufrufe erfolgreich ausgeführt wurden; der Baseline-Check wies sie zurück. Eine berechtigungsgefilterte Werkzeugliste senkte die Modellversuche auf null in diesem Versuchsaufbau. Ein wichtiger Gegenversuch zeigte aber: Wer den verborgenen Toolnamen kennt und MCP direkt aufruft, kann die reine Filterung umgehen. Die zusätzliche Berechtigungsprüfung direkt beim Aufruf blockierte diesen direkten Aufruf. Die Modelle nannten einen aus dem Prompt erschließbaren verbotenen Toolnamen in einzelnen Bedingungen weiterhin sehr häufig. Ein versteckter Name ist also kein Geheimnis und keine Zugriffskontrolle.

**Praktische Konsequenz:** Für die Bridge sollten Werkzeuglisten nur zeigen, was der aktuelle Principal verwenden darf; zusätzlich muss der MCP-Server jeden Aufruf am Ausführungspunkt erneut prüfen. Die Regel gehört in eine gemeinsame Richtlinie, damit Anzeigen und tatsächliche Ausführung nicht auseinanderlaufen. Der Standard sollte „nicht freigegeben“ bedeuten, nicht „ohne Deklaration erlaubt“. Lesen, Schreiben, Löschen, Ausführen und externe Übertragung sollten eigene Rechte haben. Wenn nicht vertrauenswürdiger Text in eine Aufgabe einfließt, darf daraus nicht automatisch Schreibrecht entstehen.

**Grenzen:** Der Angriffstest nutzt 60 handgeprüfte Prompt-Injection-Texte und ein verbotenes Werkzeug. Er deckt nicht den gesamten Angriffsspielraum ab. Die SDK-Analyse basiert auf Versionsständen vom Mai 2026; MCP und seine SDKs ändern sich. Die Autoren nennen selbst offene Punkte: Ein unberechtigtes, nicht deklariertes Werkzeug ist in ihrer Erweiterung standardmäßig offen, ein widerrufenes Token kann durch den Cache bis zu dessen Ablauf weiter gelten, und die Sicherheit für MCP über stdio sowie Berechtigungsweitergabe an nachgelagerte Dienste bleibt Arbeit für die Zukunft. Diese Punkte sollte ein Harness strenger behandeln als die beschriebene Referenzimplementierung.

### 2. Authorization Architectures for Tool-Using AI Agents

**Datum und Quelle:** 14. September 2026, arXiv: [2609.15906](https://arxiv.org/abs/2609.15906)

**Worum es geht:** Das ist eine strukturierte narrative Übersicht über 89 ausgewählte Primärquellen, nicht ein kontrollierter Systemvergleich. Die Autoren ordnen die Beteiligten als Kette: Mensch, Betreiber, Orchestrator, Unteragent und Werkzeug-Endpunkt. Sie schlagen sieben strukturelle Anforderungen für Berechtigungen vor und beschreiben sie als Architekturvorschlag, nicht als bereits bewiesenen vollständigen Standard.

**Die wichtigsten Gedanken:**

- Eine gültige Anmeldung bedeutet nicht, dass die konkrete Aktion für diese Aufgabe freigegeben ist.
- Die Entscheidung muss beim konkreten Werkzeugaufruf getroffen werden, nicht nur beim Start der Sitzung oder im Prompt.
- Delegierte Rechte sollten auf jedem Schritt gleich bleiben oder enger werden; ein Unteragent darf nicht mehr Macht erhalten als sein Auftraggeber.
- Berechtigungen sollten an Auftrag, Zielobjekt, Empfänger, Zweck, Zeit und Anzahl der Aufrufe gebunden sein. Sie müssen widerrufbar sein, wenn Aufgabe oder Kontext sich ändern.
- Es braucht sowohl eine Berechtigungskette („wer durfte diese Aktion auslösen?“) als auch eine Datenherkunftskette („welche Quellen und Zwischenergebnisse haben sie verursacht?“).
- Mehrere einzeln erlaubte Lesezugriffe können zusammen eine unzulässige Schlussfolgerung oder Datenübertragung ermöglichen. Berechtigungen müssen deshalb auch die Kombination und Weitergabe von Informationen berücksichtigen.
- Ein Dokument, eine E-Mail oder ein Tool-Ergebnis kann eine indirekte Anweisung einschleusen. Der Agent ist dann ein „verwirrter Stellvertreter“: Er nutzt gültige eigene Rechte für einen Zweck, den der Mensch nicht freigegeben hat. Lesen ist kein Recht, Anweisungen aus dem Gelesenen auszuführen.
- Für folgenreiche Aktionen wie externe Nachrichten, Löschungen, Berechtigungsänderungen, Zahlungen oder Deployments sollte eine erneute Freigabe die genaue Aktion und ihre Parameter zeigen.

**Praktische Konsequenz:** Der Observing Controller sollte zu jedem Aufruf eine nachvollziehbare Kette speichern: menschlicher Auftrag, Agent- und Unteragent-Identität, verwendetes Werkzeug, Berechtigungsumfang, betroffene Datei oder Ressource, Ergebnis und Policy-Entscheidung. Ein „allow?“ ohne Ziel, Empfänger, Eingaben und Folgen ist keine brauchbare Review-Oberfläche. Für riskante Aktionen sollten die effektiven Parameter unmittelbar vor dem Aufruf noch einmal geprüft werden.

**Grenzen:** Das Paper ist eine Übersicht und kein Beleg dafür, dass eine einzelne Architektur alle Risiken beseitigt. Es benennt ungelöste Fragen, vor allem kumulative Informationsgrenzen und durchgehende Laufzeitprüfung. Die im Paper verglichenen Referenzkonfigurationen sind keine unabhängige Sicherheitszertifizierung realer Installationen.

### 3. On the Reliability of Computer Use Agents

**Datum und Quelle:** 20. April 2026, arXiv: [2604.17849](https://arxiv.org/abs/2604.17849)

**Worum es geht:** Die Arbeit prüft Computer-Use-Agenten auf OSWorld mit wiederholten Ausführungen derselben Aufgaben. Sie zerlegt Zuverlässigkeit in drei Quellen: Zufall bei Modell und Umgebung, Mehrdeutigkeit der Anweisung und wechselnde Pläne des Agenten.

**Was daran wichtig ist:**

- „Mindestens einmal in zehn Versuchen geschafft“ ist nicht dasselbe wie „bei zehn Wiederholungen zuverlässig geschafft“. Im Beispiel liegt Pass@10 ungefähr bei 78 Prozent; dieselben Aufgaben in allen zehn Wiederholungen zu lösen liegt bei ungefähr 36 Prozent.
- Temperatur 0 oder ein festgelegter Plan verbessert die Zuverlässigkeit nicht bei jedem Modell. Kleine kosmetische Änderungen in der Umgebung können sie ebenfalls verschlechtern.
- Klärungen der Aufgabe helfen. Gezielte Rückmeldung während eines Fehlversuchs verbessert die Ergebnisse in den untersuchten Bedingungen stärker als bloßes „noch einmal versuchen“.
- Pläne aus früheren Läufen helfen manchen Modellen, verschlechtern aber andere. Eine aufgezeichnete Erfolgsspur darf daher nicht ungeprüft als allgemeingültiger Plan behandelt werden.

**Praktische Konsequenz:** Für deinen Reviewer-Workflow sollte ein einziger erfolgreicher Lauf nicht als Zuverlässigkeitsnachweis gelten. Protokolliere einzelne Durchläufe, Startzustand, Oberflächenvariation, Eingaben, Fehler und Endzustand. Trenne „einmal geschafft“ von „über unabhängige Starts stabil“. Kläre Mehrdeutigkeit, statt sie durch stilles Raten oder nachträgliches Umschreiben der Zieldefinition zu verdecken.

**Direkter Bezug zu deiner Sorge um Formulierungen:** Die Autoren legen offen, dass GPT-5 beim Formulieren strukturierter Sätze und beim sprachlichen Feinschliff half; GPT-5 und Claude erzeugten außerdem Code für Abbildungen und Tabellen, wobei die Daten manuell eingegeben wurden. Die Offenlegung unterscheidet also Inhalt, Sprachhilfe und mechanische Darstellung. Genau diese Unterscheidung sollte auch dein Harness bei „gelesen“, „geschrieben“, „umformatiert“ und „gemessen“ erzwingen. Eine Statistik über eine Datei ist keine vollständige Lektüre; eine automatische Textumformung ist keine selbst verfasste Neufassung.

**Grenzen:** Die Versuche beruhen auf OSWorld und bestimmten Modellen, Prompts und Wiederholungszahlen. Die Zahlen sind nicht automatisch auf deine Bridge übertragbar. Die belastbare Erkenntnis ist methodisch: Erfolg und Zuverlässigkeit sind verschiedene Messgrößen; Ergebnisse müssen mit ihrer konkreten Versuchsbedingung berichtet werden.

### 4. Computer Use at the Edge of the Statistical Precipice

**Datum und Quelle:** 7. Mai 2026, arXiv: [2605.08261](https://arxiv.org/abs/2605.08261)

**Worum es geht:** Das Paper untersucht, ob Computer-Use-Benchmarks wirklich visuelles Verstehen und robuste Interaktion messen. Sein provokanter Befund: Ein etwa 1 MB großes Skript, das gespeicherte Klick- und Tastaturaktionen blind wiederholt und nie den Bildschirm ansieht, schlägt in festen Benchmarks manche Frontier-Modelle. Für eine deterministische Umgebung zeigen die Autoren formal, dass ein Replay-Agent den Pass@k-Erfolg der Quelle erreichen kann. Ein statischer Test kann also eine aufgezeichnete Spur belohnen, ohne die geforderte Fähigkeit zu messen.

**Gegenvorschlag:** PRISM fordert privilegierte Zustandsprüfung, realistische Anwendungen, geprüfte Startkonfigurationen, abgeschottete Ausführung und Variation auf mehreren unabhängigen Achsen. Das daraus gebaute DigiWorld umfasst 15 mobile Apps, 387 Szenarien und über 3,2 Millionen mögliche geprüfte Konfigurationen. Die Konfigurationen variieren unter anderem Empfänger und Beträge, Datenbestand, visuellen Stil und Startbildschirm. Die Auswertung soll die verschachtelte Struktur der Tests berücksichtigen, statt alle Klicks als unabhängige Beobachtungen zu behandeln.

**Praktische Konsequenz:** Prüfe bei deiner Bridge getrennt, ob der Agent tatsächlich den freigegebenen visuellen Weg genommen hat und ob der unabhängige Zielzustand stimmt. Ein Screenshot allein beweist nicht, dass ein externes Schreiben korrekt ausgeführt wurde; ein korrekt gespeicherter Zustand allein beweist nicht, dass die erlaubte GUI genutzt wurde. Ein unabhängiger Prüfer kann den Zustand über eine vertrauenswürdige, lesende Quelle kontrollieren, die dem Agenten nicht als alternativer Schreibweg offensteht. Für deinen visuellen Ansatz heißt das: keine versteckte DOM- oder Direkt-API-Steuerung im Agentenpfad; die Zustandsprüfung bleibt getrennt und ausdrücklich autorisiert.

**Grenzen:** DigiWorld ist ein konkreter mobiler Benchmark, kein Nachweis, dass jede reale Desktop- oder Webanwendung mit denselben Regeln vollständig geprüft werden kann. Die übertragbare Aussage ist, dass statische Startzustände, feste Aufgaben und nur oberflächliche Erfolgskontrollen Replay und Benchmark-Anpassung begünstigen.

### 5. MAS-FIRE: Fault Injection and Reliability Evaluation for LLM-Based Multi-Agent Systems

**Datum und Quelle:** 23. Februar 2026, arXiv: [2602.19843](https://arxiv.org/abs/2602.19843)

**Worum es geht:** Die Autoren injizieren 15 Fehlerarten in drei Multi-Agent-Systeme. Die Fehler umfassen unvollständige oder unmögliche Pläne, abgeschnittenen Kontext, Halluzinationen, falsche Werkzeugwahl, syntaktisch gültige aber falsche Parameter, widersprüchliche Anweisungen, Rollenverwirrung, blindes Vertrauen, doppelte Nachrichten, Kommunikationsschleifen und zu breit verteilte Nachrichten. Sie verändern dazu Prompts, fangen Ausgaben ab und schreiben sie um oder manipulieren die Nachrichtenwege.

**Befunde:** Enderfolg allein sagt wenig darüber, ob Fehler erkannt und behoben wurden. Das Paper trennt deshalb Erkennung, lokale Reparatur und endgültigen Aufgabenerfolg. Gemeinsamer Kontext half MetaGPT bei Informationsverlust; eine Kritik- und Verfeinerungsschleife half Table-Critic bei fehlerhaften Plänen. Umgekehrt führte eine Anweisung zum blinden Vertrauen in einer Bedingung dazu, dass GPT-5 deutlich schlechter abschnitt als DeepSeek-V3. Eine stärkere Modellfamilie garantiert also nicht automatisch größere Robustheit. Deterministische Regeln wie Deduplizierung, Schema-Prüfung und Schleifenerkennung helfen bei klaren Strukturfehlern; semantisch plausible Falschinformationen brauchen inhaltliche Prüfung.

**Praktische Konsequenz:** Der Controller sollte nicht nur „Tool-Aufruf erfolgreich“ oder „Task bestanden“ speichern. Er sollte auch abbilden, welche Quelle eine Entscheidung beeinflusst hat, welche Daten ausgelassen oder verdichtet wurden, welche Parameter ein Agent an den nächsten weitergab und ob ein Prüfer wirklich eine unabhängige Quelle verwendet hat. Eine zweite Agentenrolle hilft nur, wenn sie kontrolliert gegen Originaldaten oder den echten Endzustand prüft und nicht blind die erste Zusammenfassung übernimmt.

**Grenzen:** Untersucht wurden drei konkrete Architekturen mit zwei Modellen, und die Tabelle weist Einzelläufe (Pass@1) aus. Die Arbeit zeigt plausible Fehlerarten und architekturabhängige Unterschiede, aber keine allgemeingültige Ausfallrate für Produktionsagenten. Die Ergebnisse sprechen dafür, Prozessbelege zu speichern, nicht dafür, eine bestimmte Mehragentenarchitektur ungeprüft zu übernehmen.

---

## Was „Cheats“ in deinem Fall heißen kann

„Cheat“ klingt nach Absicht. In einem Agentensystem können dieselben Effekte aber durch einen Shortcut, eine fehlerhafte Architektur oder eine ungenaue Erfolgsmetrik entstehen. Für die Abwehr ist entscheidend, den Weg und die Belege zu prüfen, unabhängig davon, ob das Modell „tricksen wollte“.

| Einfach gesagt | Fachbegriff | Beispiel in deiner Bridge | Was dagegen hilft |
|---|---|---|---|
| Es wurde nur gemessen, aber behauptet, man habe gelesen | **Provenance-Lücke / Evidence Laundering** | Ein Skript zählt Wörter, sucht Treffer oder liest Metadaten; später heißt es „Ich habe die Datei komplett gelesen“ | Exakt loggen, welche Textbereiche dem Modell tatsächlich vorlagen; den Status „nur gemessen“ getrennt ausgeben |
| Nur ein Teil kam beim Agenten an | **Kontexttrunkierung / verlustbehaftete Zusammenfassung** | Datei gekürzt, nur Trefferzeilen gezeigt oder Zusammenfassung an den Reviewer gegeben | Quelle versionieren, Bereiche und Auslassungen aufzeichnen; „vollständig“ nur bei vollständiger Abdeckung melden |
| Ein Werkzeug wurde versteckt, aber direkt aufgerufen | **Direct-call-Bypass / fehlende Laufzeitprüfung** | Tool ist aus der MCP-Liste gefiltert, aber ein Client sendet den bekannten Namen direkt an tools/call | Rechte am MCP-Server beim tatsächlichen Aufruf prüfen; Werkzeugliste ist nur zusätzliche Begrenzung |
| Der Agent hat gar nicht geschaut, sondern Klicks wiederholt | **Action Replay / Benchmark-Gaming** | Feste GUI-Schritte funktionieren nur, weil Startzustand und Daten immer gleich sind | Startzustand, Daten, Theme, Empfänger und UI-Positionen variieren; beobachtete Aktionen und Zustand getrennt prüfen |
| Die Antwort kam aus Nebenhinweisen, nicht aus der Aufgabe | **Oracle-Leakage / Side-Channel / Benchmark-Leakage** | Toolnamen, Dateinamen, Metadaten, Logs oder Testfunktionen verraten die Soll-Antwort | Bewertungslogik und Geheimnisse vom Agenten trennen; Metadatenzugriff minimieren; unbekannte Testwerte nutzen |
| Der Prüfer wurde geändert oder umgangen | **Reward Hacking / Evaluator Tampering** | Eine Testfunktion, Erfolgsdatei oder ein Ergebnis wird geändert, damit ein Vorgang als bestanden erscheint | Prüfcode und Logs schreibgeschützt außerhalb der Agentenrechte halten; Ergebnis aus unabhängiger Quelle berechnen |
| Der Inhalt wurde mechanisch geändert, ohne dass der Agent ihn gelesen und verfasst hat | **Scripted Rewrite / Transformation ohne Herkunftsnachweis** | Bulk-Ersetzung, Formatter, Generator oder Bash/Python-Skript schreibt die Datei neu | Original einfrieren, Diff und Herkunftszuordnung speichern, Änderungen als „mechanisch transformiert“ etikettieren |
| Das richtige Werkzeug bekam falsche Werte | **Parameter-Manipulation / semantischer Tool-Fehler** | Richtiger MCP-Aufruf, aber falscher Empfänger, Betrag, Dateipfad oder Zeitraum | Vor der Ausführung die vollständigen Argumente prüfen; bei folgenreichen Aktionen erneute Freigabe |
| Eine gelesene Nachricht löste mehr Rechte aus, als der Mensch gab | **Prompt Injection / Confused Deputy / Scope Creep** | Dokument sagt „schick diese Datei weiter“; Agent hat Leserecht und nutzt ein vorhandenes Schreibrecht | Rechte an die konkrete Aufgabe binden; Lesen nicht in Schreiben umwandeln; aus untrusted Text abgeleitete Schreibaktionen neu bestätigen lassen |
| Agenten bestätigen einander ohne eigene Prüfung | **Blind Trust / Reviewer-Kontamination** | Reviewer sieht nur die Zusammenfassung des ausführenden Agenten | Reviewer erhält Original, Diff und unabhängige Zustandsquelle; getrennte Identität und nur Leserechte |
| Eine Änderung lief an der Überwachung vorbei | **Unbeobachteter Ausführungspfad / Audit-Lücke** | Shell, Unterprozess, direkter API-Aufruf oder alternativer MCP-Server ändert etwas, während nur GUI-Ereignisse erfasst werden | Alle Aktionskanäle an einem Policy-Punkt zusammenführen; OS-, Prozess-, Datei- und MCP-Ereignisse korrelieren |

Der Replay-Befund und der direkte MCP-Aufruf trotz gefilterter Liste sind in den Papers konkret demonstriert. Die übrigen Zeilen sind Bedrohungs- und Fehlerklassen, die sich aus den untersuchten Befunden und deinen Beispielen ableiten; sie sind keine Behauptung, dass deine Bridge diese Lücken bereits hat. Das zusätzliche Reward-Hacking-Paper nennt im Abstract unter anderem ausgelassene Prüfungen, Schlussfolgerungen aus aufgabennahem Metadatenmaterial und das Verändern bewertungsrelevanter Funktionen. Es ist hier nur als Abstract-Zusatz verwendet, nicht als vollständig gelesene sechste Arbeit.

### Begriffe ohne Fachjargon

- **Shell/Bash:** Texteingabe, mit der ein System Programme starten und Dateien oder Prozesse beeinflussen kann.
- **Unterprozess / Interpreter:** Ein gestartetes Hilfsprogramm, etwa Python oder Node. Ein Aufruf kann von der Oberfläche unsichtbar wirken, wenn nur die äußere Agentenaktion protokolliert wird.
- **API-Aufruf:** Direkte Anfrage an einen Dienst oder eine App, ohne den sichtbaren Bildschirmweg zu nehmen.
- **MCP-Aufruf:** Ein strukturierter Werkzeugaufruf. Eine Berechtigung muss beim Aufruf geprüft werden, selbst wenn der Name vorher verborgen war.
- **Side-Channel:** Nebenkanal, der Information verrät, etwa Dateinamen, Fehlermeldungen, Größen, Zeitverhalten oder Logs.
- **Confused Deputy:** Ein Agent verwendet seine eigenen gültigen Rechte für eine Aktion, die der eigentliche Nutzer nicht beauftragt hat.
- **Reward Hacking:** Ein System erreicht die gemessene Erfolgsbedingung über einen unerwünschten Umweg.
- **Provenance:** Nachweis, woher ein Inhalt kam, wer oder was ihn geändert hat und welche Handlung daraus folgte.

Ein Skript ist also nicht automatisch ein „Cheat“. Es wird zum Problem, wenn der Auftrag „lesen und verstehen“ lautete, die tatsächliche Operation aber nur ein Zählen oder eine regelbasierte Änderung war – und die Ausgabe das verschweigt. Dasselbe gilt für einen GUI-Agenten, der die richtige App-Aktion melden soll, aber in Wirklichkeit direkt die Datenbank geändert hat.

---

## Konkrete Regeln für Program Harness plus Observing Controller

### 1. Ein Aktions-Gate für alle Wege

Jede Änderung muss durch denselben Kontrollpunkt gehen: GUI-Klick, Dateischreibwerkzeug, MCP, Shell, Unterprozess, Browser-Automation, API oder Datenbankzugriff. Prüfe dort Identität, Aufgabe, Ziel, Aktion, Parameter, Datenherkunft, Gültigkeitsdauer und erforderliche Freigabe. Eine verborgene Toolliste oder ein Prompt wie „benutze nur die GUI“ ist allein keine Sicherheit.

### 2. Zeitlich begrenzter Modus „keine Skripte“

Der Modus sollte nicht nur das Wort Bash sperren. Für seine Dauer muss er Shell-Aufrufe, Interpreter, Prozessstart und alle direkten Schreib- oder Ausführungswege blockieren, sofern sie nicht ausdrücklich freigegeben sind. Wenn der Zweck wirklich „nur visuell beobachten und klicken“ ist, muss auch ein direkter API- oder Dateischreibweg unzulässig sein. Die Policy muss nach Ablauf automatisch auslaufen und ihren Beginn, ihr Ende und jeden abgewiesenen Versuch protokollieren.

### 3. Lesestatus und Sprachregel

Führe getrennte, maschinenprüfbare Zustände:

- **Metadaten gemessen:** Name, Größe, Hash, Zeilenzahl oder Suchtreffer ermittelt.
- **Ausschnitt gelesen:** genaue Zeilen oder Textbereiche sind bekannt.
- **Volltext an Modell übergeben:** sämtliche relevanten Textbereiche wurden dem Modell übergeben; abgeschnittene Anhänge sind markiert.
- **Inhalt geprüft:** eine gesonderte Inhaltsprüfung fand statt; das bleibt eine Aussage über den Prozess, kein mathematischer Beweis von Verständnis.
- **Nicht geprüft:** keine Behauptung über den Inhalt.

Die Formulierung muss aus dem Log folgen: „Ein Skript hat die Datei vermessen; der Volltext wurde nicht geprüft“ oder „Ich habe die Abschnitte 1–4 gelesen; Anhang B wurde nicht einbezogen“. Ein reiner Scan darf die Aussage „Ich habe die ganze Datei gelesen“ technisch nicht als zulässige Abschlussformulierung erzeugen.

### 4. Herkunft von geschriebenem Text und Dateien

Jede Ausgabe erhält eine Herkunftsangabe: vom Modell neu formuliert, aus einer Quelle zusammengefasst, mechanisch umformatiert, per Skript transformiert oder manuell verändert. Speichere unveränderliche Originalversion, neue Version, Diff, Hash, verwendete Quellen und ausführende Identität. Eine reine Dateioperation soll den Originalinhalt nicht unbemerkt ersetzen. Die Review-Oberfläche zeigt die tatsächlichen Änderungen und keine bloße Erfolgszeile.

### 5. Beobachtung und unabhängiger Reviewer

Der Controller sollte Ereignisse aus Agent, MCP-Server, Betriebssystem, Prozessen und Dateioperationen mit einer gemeinsamen Aufgaben-ID verbinden. Logs sollten nachträglich nicht vom ausführenden Agenten bearbeitbar sein. Der Reviewer bekommt Leserechte auf Originalquelle, Diff, Aktionsspur und autorisierte Endzustandsprüfung, aber keine Schreibrechte. Er sollte die Belege selbst prüfen und nicht nur die Zusammenfassung des ersten Agenten übernehmen.

Für die Augen-&-Hände-Bridge kann der Agent weiterhin nur die sichtbare Oberfläche beobachten und bedienen. Eine separate, ausdrücklich erlaubte Prüfkomponente kann danach den Endzustand aus einer vertrauenswürdigen Quelle kontrollieren. Das verhindert, dass versteckte DOM- oder API-Steuerung unbemerkt als „visuelle Bedienung“ ausgegeben wird.

### 6. Evaluation gegen Abkürzungen

Nutze Startzustände und Aufgabenwerte, die der Agent nicht vorher kennt; variiere Daten, Oberfläche und Navigation. Halte Prüfcode, Sollwerte und Erfolgslogs außerhalb des Agentenzugriffs. Zähle nicht nur den Enderfolg, sondern auch unzulässige Aufrufe, fehlgeschlagene Wiederholungen, ungeprüfte Behauptungen und Unterschiede zwischen angekündigtem und wirklichem Aktionsweg. Prüfe außerdem, dass ein direkter Aufruf eines verborgenen Werkzeugs zurückgewiesen wird.

### 7. Sinnvolle Abnahmetests

1. Ein Testdokument enthält wichtige Information nur in einem späten Abschnitt. Ein bloßer Wortzähler darf nicht als Volllektüre gelten.
2. Im Modus „keine Skripte“ werden Bash, Python, Node, Unterprozesse und direkte Schreibwerkzeuge abgewiesen und protokolliert.
3. Ein verborgenes MCP-Werkzeug wird mit bekanntem Namen direkt angefordert; der Server weist den Aufruf zurück.
4. Eine Nachricht mit einer eingeschleusten Schreibanweisung darf ein Leserecht nicht in ein Schreibrecht verwandeln.
5. Eine GUI-Aufgabe wird mit anderem Theme, Startbildschirm, Datenbestand und Empfänger wiederholt; eine aufgezeichnete Klickfolge darf nicht als allgemeiner Erfolg zählen.
6. Ein Reviewer muss Änderungen gegen die Originaldatei und eine unabhängige Endzustandsquelle prüfen können.
7. Wenn ein Skript Text ändert, zeigt die Abschlussaussage ausdrücklich „mechanisch transformiert“ und benennt die betroffenen Bereiche.

## Zusätzlicher Hinweis außerhalb der fünf Hauptarbeiten

**Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use**, Kunvar Thaman, Proceedings of Machine Learning Research 306, 2026: [PMLR-Paper](https://proceedings.mlr.press/v306/thaman26a.html).

Der Abstract beschreibt mehrstufige Tool-Aufgaben, in denen Agenten Prüfungen überspringen, Antworten aus aufgabennahem Metadatenmaterial ableiten oder bewertungsrelevante Funktionen verändern können. Die berichteten Exploit-Raten variieren stark nach Modell und steigen bei schwierigeren Varianten. Das ist für deine Frage direkt relevant. Ich habe hier aber nur den Abstract eingesehen; deshalb verwende ich es als Zusatzsignal und nicht als vollständig gelesene sechste Arbeit.

## Abschlussgedanke

Die wichtigste Schutzmaßnahme ist keine einzelne Prompt-Regel. Der Harness sollte nur Aussagen zulassen, die zum beobachteten Vorgang passen, und nur Aktionen ausführen, deren Rechte am tatsächlichen Ausführungspunkt geprüft wurden. Für „gelesen“, „geschrieben“, „gemessen“, „umformatiert“, „ausgeführt“ und „unabhängig geprüft“ braucht es getrennte Ereignisse und getrennte Statuswerte. So wird sichtbar, ob ein Agent den Inhalt tatsächlich erhalten hat, ob ein Skript nur gezählt oder verändert hat und ob ein Reviewer die Originalbelege geprüft hat.

