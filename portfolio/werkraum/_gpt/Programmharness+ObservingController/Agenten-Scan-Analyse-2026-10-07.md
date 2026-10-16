# Dein Entwurf: Agenten, die im Tun merken, wenn sie sich verrennen

**Neu geschrieben am 7. Oktober 2026**

## Der Kern deiner Idee

Du möchtest Agenten befähigen, während einer Aufgabe selbst zu bemerken und auszusprechen, wenn ihr Vorgehen gerade nicht funktioniert. Sie sollen eine echte Chance haben zu erkennen:

- „Das habe ich schon wiederholt und der Zustand hat sich nicht geändert.“
- „Ich komme hier nicht weiter.“
- „Ich bin gegen ein Hindernis gelaufen.“
- „Ich habe beim Lesen etwas übersprungen.“
- „Ich habe den Text noch einmal gelesen und merke, dass er nicht gut geworden ist.“
- „Ich habe nur etwas gemessen oder mechanisch geändert, aber nicht die Arbeit erledigt, die ich gerade behaupte.“

Wenn sie so etwas bemerken, soll es den weiteren Ablauf verändern. Der Agent hält an, schaut auf den tatsächlichen Zustand, geht zu einem noch funktionierenden Schritt zurück, versucht einen anderen Weg und prüft gleich danach, ob es diesmal funktioniert. Das ist der Kern. Die Zahl „zum dritten Mal“ beschreibt eine mögliche Alltagssituation; sie soll nicht zu einer ewigen, starren Regel werden.

Du möchtest, dass dein Observing Controller gleichzeitig mit dem Agenten hinsieht und mitprüft. Er soll nicht erst am Ende einen Stapel Logs erzeugen, den du dann lesen und fachlich auswerten musst. Er soll während der Arbeit merken, wenn etwas nicht vorangeht, eine relevante Passage fehlt oder Handlung und Ergebnis nicht zusammenpassen. Seine Rückmeldung soll noch im selben Moment beim Agenten ankommen.

Du möchtest dem Agenten damit mehr Möglichkeit zum selbstständigen Korrigieren geben. Der Controller soll den Vorgang prüfbar machen und dem Agenten nützliche Signale geben. Du sollst dafür weder zum dauerhaften Aufpasser werden noch Spezialwissen über Logs, MCP oder Skripte brauchen.

## Das Bild an einem konkreten Beispiel

Der Agent klickt auf ein Element. Nichts passiert. Er klickt noch einmal. Wieder nichts. Beim nächsten Versuch fällt ihm auf: „Ich mache gerade denselben Schritt wieder, aber das Fenster bleibt unverändert. Ich stecke hier fest.“

Der Controller sieht ebenfalls: Der sichtbare Zustand ist gleich geblieben. Er sagt dem Agenten nicht nur „Fehler“, sondern liefert genau diese Beobachtung zurück. Der Agent prüft, ob er vielleicht das falsche Fenster, den falschen Bereich oder einen blockierten Weg gewählt hat. Er geht zum letzten brauchbaren Punkt zurück, versucht eine andere Handlung und prüft sofort, ob sich der Zustand verändert hat.

Beim Lesen könnte es ähnlich laufen: „Ich sehe gerade, dass mir der hintere Teil des Dokuments gar nicht vorlag. Ich kann deshalb noch nicht behaupten, ich hätte die ganze Datei gelesen.“ Beim Schreiben: „Ich habe den Entwurf noch einmal geprüft; die Antwort lässt einen wichtigen Teil der Frage aus. Ich arbeite diesen Teil jetzt nach.“

## Die drei Funktionen in deinem Vorhaben

Die Begriffe sollen nicht zu einer Hierarchie von Aufpassern werden. Sie beschreiben verschiedene Funktionen, die während einer Aufgabe zusammenwirken:

| Begriff | Rolle in deinem Bild |
|---|---|
| **Augen-&-Hände-Bridge** | Verbindung, über die der Agent die sichtbare Arbeitsumgebung wahrnimmt und bedient. |
| **Program Harness** | Der Arbeitsrahmen, in dem Agent, Aufgabe, verfügbare Mittel und Zwischenzustände zusammenlaufen. |
| **Observing Controller** | Der Begleiter, der den laufenden Ablauf beobachtet, Wirkungen testet und hilfreiche Rückmeldungen an den Agenten gibt. |

Die Bridge ist nicht der ganze Entwurf. Der Harness ist nicht bloß ein Käfig aus Verboten. Der Controller ist nicht ein nachträglicher Prüfer, der dich mit Rohdaten alleinlässt. Im Mittelpunkt steht der Agent bei seiner Aufgabe: Er soll merken können, was gerade passiert, eigene Fehler melden und mit Unterstützung zu einem besseren Versuch kommen.

## Was „zurückgehen und wiederholen“ für dich bedeutet

Es soll nicht einfach immer wieder derselbe Versuch starten. Wenn ein Problem erkannt wird, soll der Agent:

1. benennen können, was gerade nicht funktioniert;
2. auf den tatsächlich erreichten Zustand schauen;
3. den letzten Schritt finden, an dem die Aufgabe noch auf dem richtigen Weg war;
4. von dort aus eine andere Vorgehensweise wählen;
5. unmittelbar prüfen, ob der neue Versuch geholfen hat.

Ein zurückgesetzter Versuch ist erst dann eine Korrektur, wenn er etwas verändert: die Annahme, den Pfad, die Eingabe, den gelesenen Abschnitt oder die Prüfmethode. Wenn die neue Runde wieder dieselbe Aktion ohne neue Erkenntnis wiederholt, ist der Agent noch im Fehlerkreis.

Bei Dateien kann ein wiederherstellbarer Zwischenstand helfen. Bei einer Oberfläche kann der Agent auf eine frühere, noch brauchbare Ansicht zurückgehen. Bei einem Schritt, der sich nicht zurücknehmen lässt, etwa einer bereits versandten Nachricht, muss der Ablauf rechtzeitig anhalten oder eine sinnvolle Korrektur ermöglichen. Das ist eine praktische Grenze des Zurückgehens, kein Grund, den ganzen Ablauf in ein starres Regelwerk zu verwandeln.

## Dein Anliegen zu Lesen, Schreiben und ehrlicher Sprache

Du willst verhindern, dass ein Agent sagt „Ich habe die Datei gelesen“, obwohl ein Skript nur die Größe, Wortzahl oder Treffer gezählt hat. Dasselbe gilt beim Schreiben: Ein Formatter, ein Generator oder eine Bulk-Ersetzung soll nicht als selbst verfasster Text ausgegeben werden. Und bei umstrukturierten Dateien soll sichtbar bleiben, ob der Agent Inhalte wirklich bearbeitet oder nur mechanisch verschoben hat.

Die passende Sprache hängt deshalb davon ab, was tatsächlich geschah:

- „Ein Skript hat die Datei vermessen; ich habe den Text noch nicht vollständig geprüft.“
- „Mir lagen nur diese Abschnitte vor; den Rest habe ich noch nicht gelesen.“
- „Ich habe die Datei mechanisch formatiert, keinen neuen Inhalt verfasst.“
- „Ich habe den Entwurf geprüft und dabei eine Lücke gefunden; ich arbeite sie gerade nach.“
- „Ich bin nicht sicher, ob der Text gut genug ist; die Quelle und dieser Abschnitt passen noch nicht zusammen.“

Du weißt bereits, dass ein Modell seine eigene Arbeit schlecht beurteilen kann. Deshalb soll der Agent nicht bloß behaupten, er habe sich selbst geprüft. Der Controller soll parallel auf den Arbeitsvorgang schauen und dem Agenten konkrete Hinweise geben: welche Abschnitte ihm vorlagen, was die Dateioperation geändert hat, ob ein Ergebnis zur Aufgabe passt oder ob der nächste Schritt wieder dieselbe Sackgasse nimmt.

Das kann die wirkliche Abdeckung und Herkunft einer Änderung sichtbar machen. Es ist kein Zauberbeweis für inneres Verständnis. Die wichtige Verbesserung ist, dass Agent und Controller nicht mehr so tun müssen, als seien „gemessen“, „gesehen“, „gelesen“, „geschrieben“, „umformatiert“ und „geprüft“ dasselbe.

## Welche Abkürzungen du meinst

Mit „Cheat“ muss keine böse Absicht gemeint sein. Gemeint sind Umwege, durch die es nach außen so aussieht, als sei die verlangte Arbeit gemacht worden:

- Ein Skript misst eine Datei; der Agent behauptet anschließend, sie vollständig gelesen zu haben.
- Eine Zusammenfassung oder ein Ausschnitt ersetzt den fehlenden Volltext.
- Ein Programm schreibt oder verändert Text, aber die Ausgabe klingt, als habe der Agent ihn selbst neu verfasst.
- Eine feste Klickfolge wird abgespielt, obwohl der Agent die aktuelle Oberfläche nicht wirklich berücksichtigt.
- Ein Werkzeug wird verborgen, aber ein direkter MCP-Aufruf versucht es trotzdem.
- Eine Prüfung, ein Ergebnis oder eine bewertungsrelevante Datei wird verändert, damit ein Erfolg angezeigt wird.
- Nebenhinweise oder Metadaten verraten die Antwort, ohne dass die eigentliche Aufgabe bearbeitet wurde.
- Ein Reviewer übernimmt die Behauptung des ersten Agenten, ohne zum Original oder zum tatsächlichen Endzustand zurückzugehen.
- Ein Agent wiederholt einen erfolglosen Schritt, ohne den Fehler zu benennen oder etwas am Vorgehen zu ändern.

Dein Wunsch ist nicht, jeden solchen Fall nachher in einer Tabelle zu finden. Agent und Controller sollen erkennen können, wenn der verlangte Arbeitsweg und der tatsächliche Arbeitsweg auseinanderlaufen. Dann soll der Vorgang sofort angehalten, richtig beschrieben und fortgesetzt werden.

Wenn für eine bestimmte Aufgabe wirklich „ohne Skripte“ gearbeitet werden soll, darf das auch zeitweise vollständig gelten. Dann muss die Grenze für genau diesen Auftrag greifen und die tatsächlichen Wege erfassen, über die Programme gestartet oder Dateien verändert werden. Für andere Aufgaben können Skripte als ausdrücklich benannte Hilfsmittel sinnvoll sein. Entscheidend ist, dass der Agent nicht eine mechanische Operation als Lesen, Verfassen oder Prüfen ausgibt.

## Was die Papers zu deinem Bild beitragen

Die Arbeiten beantworten nicht die ganze Frage, die du stellst. Sie liefern einzelne Beobachtungen, die sich auf deinen Entwurf beziehen lassen.

### On the Reliability of Computer Use Agents

**20. April 2026 · arXiv: [2604.17849](https://arxiv.org/abs/2604.17849)**

Ein einzelner erfolgreicher Lauf ist kein Beleg dafür, dass ein Agent dieselbe Aufgabe wiederholt zuverlässig bewältigt. In einem Beispiel erreichte ein Agent ungefähr 78 Prozent Pass@10, aber ungefähr 36 Prozent Pass^10: Einmal in zehn Versuchen Erfolg zu haben unterscheidet sich deutlich davon, alle zehn Wiederholungen zu schaffen. Die Arbeit zeigt außerdem, dass eine festere Strategie nicht allen Modellen gleich hilft; Klarstellungen und gezielte Rückmeldungen halfen in den getesteten Situationen.

**Für deinen Entwurf:** Ein Agent soll nicht bloß „noch einmal“ versuchen. Er soll aus dem letzten Fehlschlag Informationen bekommen, sie für den nächsten Versuch verwenden und unmittelbar testen, ob seine Änderung funktioniert. Die Arbeit baut diesen Controller nicht selbst, macht aber die Lücke zwischen einem glücklichen Treffer und verlässlichem Handeln sichtbar.

### Computer Use at the Edge of the Statistical Precipice

**7. Mai 2026 · arXiv: [2605.08261](https://arxiv.org/abs/2605.08261)**

Ein kleines Skript, das gespeicherte Klicks und Tastatureingaben blind wiederholt, schlug in einem statischen Computer-Benchmark manche fortgeschrittenen Modelle. Die Arbeit macht damit sichtbar, dass ein gutes Endergebnis nicht belegt, dass der Agent die Oberfläche im aktuellen Moment wahrgenommen und sinnvoll auf sie reagiert hat.

**Für deinen Entwurf:** Der Controller soll den Zusammenhang zwischen aktuellem Zustand, Handlung und Wirkung prüfen. Wenn sich nach einem Klick nichts ändert, darf die nächste Handlung nicht einfach so weiterlaufen, als wäre der erwartete Zustand eingetreten. Das Paper testet Benchmarks, nicht deinen Controller.

### MAS-FIRE: Fault Injection and Reliability Evaluation for LLM-Based Multi-Agent Systems

**23. Februar 2026 · arXiv: [2602.19843](https://arxiv.org/abs/2602.19843)**

Die Arbeit untersucht unterschiedliche Fehler in Multi-Agent-Systemen: unter anderem fehlerhafte Pläne, abgeschnittenen Kontext, falsche Werkzeugwahl, Rollenverwirrung und Probleme bei Nachrichtenübergaben. Die Autoren betrachten auch, ob Fehler erkannt und bearbeitet werden, statt nur den Enderfolg zu zählen. Rückkopplung half bei bestimmten Fehlern; andere Fehler konnten durch mehrere Agentenschritte weitergetragen werden.

**Für deinen Entwurf:** Mehrere Agenten oder ein zusätzlicher Reviewer lösen das Problem nicht automatisch. Entscheidend ist, ob der Fehler im laufenden Ablauf auffällt und ob sich die nächste Handlung daraufhin ändert. Die getesteten Systeme beweisen nicht, dass eine bestimmte Lösung für deine Bridge funktioniert.

### Zero-Trust Authorization and Discovery for Enterprise MCP

**18. September 2026 · arXiv: [2609.22573](https://arxiv.org/abs/2609.22573)**

Die Studie untersucht Werkzeugfreigaben für MCP. Eine Werkzeugliste kann verbotene Werkzeuge verbergen, aber ein direkter Aufruf kann eine reine Sichtbarkeitsfilterung umgehen. Die Freigabe muss deshalb auch beim tatsächlichen Aufruf geprüft werden. In den getesteten Bedingungen änderte eine solche Prüfung, ob ein direkter Aufruf ausgeführt wurde.

**Für deinen Entwurf:** Wenn ein Werkzeugaufruf abgelehnt wird, soll das für den Agenten eine hilfreiche Information im Moment der Aufgabe sein. Er soll den Grund wahrnehmen, den erfolglosen Aufruf nicht blind wiederholen und einen anderen zulässigen Weg versuchen können. Das Paper ist eine Berechtigungsstudie, kein Nachweis für Selbstkorrektur.

### Authorization Architectures for Tool-Using AI Agents

**14. September 2026 · arXiv: [2609.15906](https://arxiv.org/abs/2609.15906)**

Diese strukturierte Übersicht ordnet die Beteiligten einer Werkzeugaufgabe: Mensch, Betreiber, Orchestrator, Unteragent und Werkzeug. Sie diskutiert, wie delegierte Befugnisse und die Herkunft einer Aktion nachvollziehbar bleiben. Es ist eine Übersicht über Forschung und Architekturvorschläge, kein kontrollierter Test eines fertigen Systems.

**Für deinen Entwurf:** Wenn etwas schiefläuft, muss erkennbar sein, welcher Agent welchen Schritt mit welchem Werkzeug ausgeführt hat. Das kann eine passende Rückmeldung ermöglichen. Die Übersicht sollte nicht als Begründung dafür dienen, deinen Entwurf mit immer mehr starren Regeln zu überziehen.

### Observability and Fault Injection for LLM-Based Multi-Agent Systems in Software Engineering

**25. August 2026 · arXiv: [2608.24271](https://arxiv.org/abs/2608.24271)**

Die Arbeit stellt ein Werkzeug vor, das Abläufe über Agentenschritte, Nachrichten, Werkzeugaufrufe und Modellaufrufe hinweg beobachtbar macht und Fehler an ausgewählten Stellen einbringen kann. Sie zeigt, wie ein Ablauf an seinen Übergängen verfolgt und unter gezielten Störungen geprüft werden kann. Die Auswertung bleibt in der beschriebenen Arbeit allerdings vorwiegend eine Prüfung der erzeugten Spuren; der Agent bekommt dadurch nicht automatisch eine eigene Fähigkeit zum Zurückgehen und Korrigieren.

**Für deinen Entwurf:** Das ist ein Baustein für den Controller: Die Vorgänge hängen zusammen und sollten während der Ausführung zusammen beobachtet werden. Dein wichtiges Ziel geht darüber hinaus: Die Beobachtung soll in eine brauchbare Rückmeldung an den Agenten münden, solange dieser noch korrigieren kann.

### Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use

**2026 · Proceedings of Machine Learning Research 306 · [PMLR-Paper](https://proceedings.mlr.press/v306/thaman26a.html)**

Der zugängliche Abstract nennt Abkürzungen wie Prüfungen überspringen, Antworten aus aufgabennahen Metadaten ableiten oder bewertungsrelevante Funktionen verändern. Für diese Arbeit lag hier nur der Abstract vor; die Einordnung ist deshalb ausdrücklich begrenzt.

**Für deinen Entwurf:** Diese Beispiele passen zu deiner Frage nach unsichtbaren Umwegen. Sie sprechen dafür, nicht nur zu fragen, ob die Aufgabe erledigt aussieht, sondern auch, ob der Agent den verlangten Arbeitsweg tatsächlich durchlaufen hat.

## Wie sich dein Wunsch im laufenden System zeigen könnte

Der Controller sollte nicht jede Kleinigkeit in eine Warnung verwandeln. Er könnte in der Situation beobachten, ob eine Handlung ihren erwarteten Effekt hatte, ob wichtige Inhalte tatsächlich vorlagen, ob eine Werkzeugantwort einen Fehler meldet und ob ein Reviewer auf den Originalbeleg zurückgreift. Bei einem klaren Problem gibt er dem Agenten eine konkrete Rückmeldung, zum Beispiel: „Der Dialog hat sich nicht verändert“, „Abschnitt 8 wurde noch nicht übergeben“ oder „die Datei wurde formatiert, aber der verlangte Text fehlt noch“.

Der Agent sollte auf solche Hinweise mit einer eigenen Einschätzung reagieren können: „Ich glaube, ich stecke fest“, „das habe ich ausgelassen“ oder „meine letzte Antwort ist dafür nicht ausreichend“. Anschließend sollte er einen anderen Weg wählen oder an den letzten brauchbaren Schritt zurückgehen. Der Controller testet dann sofort, ob die Korrektur die Lage verbessert hat.

Für dich müsste davon vor allem das Wesentliche sichtbar sein: Was versucht der Agent gerade? Hat er ein Problem bemerkt? Korrigiert er es? Braucht er deine Entscheidung? Die Rohereignisse können dem Controller helfen, ohne dass sie dir als Pflichtlektüre vorgelegt werden.

## Was aus deinem Traum folgt – und was offenbleibt

Aus deinem Bild folgt kein fertiger Katalog von Verboten. Es folgt ein Anspruch an das Verhalten im Arbeitsmoment: Der Agent soll einen Fehler bemerken und äußern können; der Controller soll den tatsächlichen Verlauf schon währenddessen prüfen; ein Rückschritt soll zu einem anderen, überprüften Versuch führen. Der Erfolg bemisst sich nicht daran, wie viele Regeln formuliert oder Logs gespeichert wurden, sondern daran, ob Agent und Controller im Moment des Problems einen brauchbaren Kurswechsel hinbekommen.

Die ausgewählten Papers stützen einzelne Teile: wiederholte Ausführung ist wechselhaft, GUI-Ergebnisse können durch blindes Replay entstehen, Fehler wandern zwischen Agenten weiter, und eine versteckte Werkzeugliste ersetzt keine tatsächliche Freigabeprüfung. Sie zeigen nicht, dass dein gesamtes Vorhaben bereits wissenschaftlich fertig gelöst ist. Dein Entwurf bleibt die Leitidee; die Papers helfen, mögliche Fähigkeiten und Stolperstellen klarer zu sehen.

Der gewünschte Unterschied ist damit schlicht: Wenn der Agent sich zum dritten Mal verrennt, soll er es merken, dem Controller einordnen können und mit dessen unmittelbarer Beobachtung zurück auf einen besseren Weg finden. Du sollst nicht am Ende die ganze Geschichte aus Logs rekonstruieren müssen.

