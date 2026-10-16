# Wenn der Agent merkt, dass er sich verrennt

**Ein ernsthafter Entwurf nach deinem Bild · 7. Oktober 2026**

## Der entscheidende Moment

Ein Agent arbeitet an einer Aufgabe. Er klickt, liest, schreibt oder ruft ein Werkzeug auf. Dann passiert etwas, das in seinem Plan nicht vorgesehen war: Der Klick verändert nichts. Eine Passage fehlt. Der Text beantwortet die Frage nicht. Ein Werkzeug lehnt den Aufruf ab. Der Agent versucht es noch einmal – und landet wieder an derselben Stelle.

Für dein Vorhaben ist genau dieser Moment entscheidend. Der Agent soll bemerken können: „Ich wiederhole mich gerade“, „ich komme nicht weiter“, „ich habe etwas übersprungen“ oder „mein Ergebnis ist noch nicht gut“. Er soll das aussprechen und daraus eine andere Handlung ableiten können. Er soll an einen brauchbaren Schritt zurückgehen, es auf einem anderen Weg erneut versuchen und direkt prüfen, ob es nun funktioniert.

Das ist mehr als ein erfolgreicher Endzustand. Es geht darum, wie der Agent arbeitet, wenn der erste Weg scheitert. Du willst ihm eine wirkliche Gelegenheit zur Selbstkorrektur geben, statt ihn bis zum Ende seiner falschen Spur laufen zu lassen und anschließend einen langen Bericht über den Fehler zu bekommen.

## Der Controller gehört in den laufenden Vorgang

Der Observing Controller soll während der Arbeit mitbeobachten und prüfen. Er soll erkennen, ob eine Handlung tatsächlich etwas verändert, ob der Agent denselben erfolglosen Schritt wiederholt oder ob der Arbeitsweg von dem abweicht, was der Agent gerade behauptet.

Seine Rückmeldung sollte konkret und rechtzeitig sein: „Die Ansicht ist nach den letzten Klicks unverändert“, „der hintere Teil der Datei wurde dir noch nicht übergeben“ oder „die Datei wurde formatiert, aber der verlangte Text fehlt noch.“ Der Agent kann diese Beobachtung dann einordnen, selbst einen Fehler benennen und den nächsten Versuch anpassen. Eine Meldung, die erst nach dem Lauf in einem Log auftaucht, kommt für diese Art der Korrektur zu spät.

Du sollst nicht zur Person werden, die hunderte Zeilen Protokoll liest, jede Abweichung selbst diagnostiziert und den Agenten durch jeden Klick führen muss. Die Technik darf intern genug Spuren zusammenhalten, damit der Controller weiß, was passiert ist. Für dich muss daraus eine verständliche, knappe Rückmeldung werden – vor allem dann, wenn der Agent nicht selbst weiterkommt und deine Entscheidung braucht.

## Selbstbeobachtung mit einer äußeren Gegenprobe

Du weißt, dass Modelle die Qualität ihrer eigenen Texte oft schlecht beurteilen. Deshalb soll Selbstkritik nicht die einzige Kontrolle sein. Der Agent soll seine Arbeit selbst prüfen dürfen und Fehler benennen können; der Controller soll gleichzeitig den tatsächlichen Vorgang beobachten und konkrete Gegenproben liefern.

Bei einer GUI-Aufgabe kann er sehen, dass der Bildschirm gleich blieb. Beim Lesen kann er nachhalten, welche Abschnitte dem Agenten tatsächlich vorlagen. Bei einer Dateiänderung kann er erkennen, ob ein Werkzeug nur formatiert oder ob neuer Inhalt entstanden ist. Bei einer Übergabe an einen Reviewer kann er feststellen, ob dieser die Originalquelle bekam oder nur die Zusammenfassung des ersten Agenten.

Der Controller spricht dabei über sichtbare Unterschiede und fehlende Belege, nicht über einen vermeintlichen Blick in den Kopf des Agenten. Er kann zeigen, was der Agent erhalten, getan und verändert hat. Der Agent kann daraufhin sagen, was er noch nicht weiß, was er ausgelassen hat und was er erneut prüfen möchte.

## Ehrlich sagen, was wirklich getan wurde

Ein Skript kann eine Datei zählen, durchsuchen, formatieren oder umschreiben. Diese Operationen können sinnvoll sein. Sie sind aber nicht dasselbe wie das vollständige Lesen eines Dokuments oder das eigenständige Verfassen eines neuen Textes.

Die Sprache des Agenten soll daher zum tatsächlich ausgeführten Schritt passen:

- „Ich habe die Datei vermessen, aber den Inhalt noch nicht vollständig gelesen.“
- „Mir lagen nur diese Abschnitte vor; den Rest habe ich nicht geprüft.“
- „Ich habe den Text automatisch formatiert, keinen neuen Inhalt geschrieben.“
- „Beim Wiederlesen habe ich bemerkt, dass meine Antwort einen wichtigen Punkt auslässt.“
- „Der letzte Versuch hat den Zustand nicht verändert; ich probiere einen anderen Weg.“

Der Controller kann solche Aussagen mit dem beobachteten Ablauf vergleichen. Er kann sicherstellen, dass ein als gelesen bezeichneter Abschnitt dem Agenten wirklich vorlag, oder dass eine Dateiänderung als mechanische Umformung gekennzeichnet wird. Das belegt den Arbeitsweg. Es macht aus einer technischen Messung keinen Beweis für Verständnis – und es muss auch nichts vortäuschen.

Wenn du für einen bestimmten Auftrag ausdrücklich manuelles Lesen ohne Skripte willst, soll der Arbeitsrahmen diesen Weg für genau diesen Auftrag tatsächlich sperren können. Die Sperre müsste dann auch indirekte Wege erfassen, über die ein Interpreter, Unterprozess oder anderes Hilfsprogramm gestartet wird. Für andere Aufgaben können Skripte ausdrücklich erlaubte Hilfsmittel sein. Entscheidend bleibt die ehrliche Unterscheidung zwischen der verlangten Arbeit und einer mechanischen Ersatzhandlung.

## Zurückgehen heißt, den nächsten Versuch zu verändern

Wenn der Agent merkt, dass er sich verrannt hat, soll er nicht einfach dieselbe Aktion erneut starten. Er soll den letzten noch brauchbaren Zustand finden, prüfen, welche Annahme oder Handlung ihn in die Sackgasse geführt hat, und eine andere Möglichkeit wählen. Der Controller beobachtet, ob dieser neue Versuch tatsächlich anders verläuft und ob er den erwarteten Zustand erreicht.

Bei einer Datei kann der Agent vor der Änderung einen wiederherstellbaren Stand haben. Bei einer Oberfläche kann er zu einer früheren Ansicht zurückgehen. Bei einem Hindernis kann er den Weg neu wählen. Ist eine Außenwirkung nicht rückgängig zu machen – etwa eine bereits versandte Nachricht –, muss die Prüfung vor dem unumkehrbaren Schritt stattfinden. Diese Grenze gehört zum jeweiligen Ablauf; sie soll nicht jede kleine Handlung in eine Genehmigungsschleife verwandeln.

Auch die Zahl der Wiederholungen sollte nicht zu einem universellen Dogma werden. „Beim dritten Mal“ ist ein gutes Bild für das Problem. Maßgeblich ist, ob ein weiterer gleicher Versuch neue Information bringt oder nur denselben Zustand reproduziert. Manchmal fällt ein Problem sofort auf, manchmal braucht es mehrere Beobachtungen. Agent und Controller sollen die Situation lesen, nicht bloß einen Zähler bedienen.

## Wo Bridge, Harness und Controller hineinpassen

Die Augen-&-Hände-Bridge ist die Verbindung, über die ein Agent eine sichtbare Oberfläche wahrnimmt und bedient. Sie ist ein wichtiger Teil des Vorhabens, aber nicht dessen gesamter Sinn.

Der Program Harness trägt den Arbeitsablauf: die Aufgabe, die beteiligten Agenten, die verfügbaren Werkzeuge und die Zwischenzustände, an denen ein Versuch fortgesetzt oder zurückgesetzt werden kann.

Der Observing Controller begleitet diesen Ablauf in Echtzeit. Er prüft, was die Handlung bewirkt hat, macht Abweichungen für den Agenten sichtbar und hilft dabei, einen anderen Versuch zu beginnen. Er ist keine nachträgliche Prüfbehörde über dem Agenten. Im Mittelpunkt bleibt der Agent, der selbst bemerken und entscheiden können soll.

Diese drei Funktionen gehören in denselben Arbeitszusammenhang. Der Harness stellt den Rahmen bereit, die Bridge stellt einen Weg in die sichtbare Umgebung bereit, und der Controller sorgt dafür, dass der Agent und das System den tatsächlichen Verlauf während der Aufgabe wahrnehmen können.

## Was die gelesenen Arbeiten für deinen Entwurf hergeben

Die Forschung liefert kein fertiges System, das genau dein Ziel bereits erfüllt. Sie beleuchtet einzelne Risiken und Fähigkeiten, die dein Entwurf zusammenführen könnte.

### Wiederholte Ausführung und gezielte Rückmeldung

**On the Reliability of Computer Use Agents** · 20. April 2026 · [arXiv:2604.17849](https://arxiv.org/abs/2604.17849)

Die Arbeit untersucht Computer-Use-Agenten mit wiederholten Ausführungen derselben Aufgaben. In einem Beispiel beträgt Pass@10 ungefähr 78 Prozent, während Pass^10 ungefähr 36 Prozent beträgt: Mindestens einen Erfolg in zehn Versuchen zu erreichen, ist etwas anderes, als alle zehn Wiederholungen erfolgreich abzuschließen. Die Autoren untersuchen außerdem Zufälligkeit, Mehrdeutigkeit der Aufgabe und wechselnde Pläne. Rückfragen und gezielte Rückmeldungen halfen in den getesteten Bedingungen; festgelegte Pläne verbesserten nicht jedes Modell gleichermaßen.

**Bezug zu deinem Ziel:** Ein Agent soll eine Wiederholung nutzen, um aus dem vorigen Versuch etwas abzuleiten. Die nächste Handlung muss sich ändern können, und der Controller soll den Effekt unmittelbar prüfen. Die Studie testet diesen konkreten Controller nicht, zeigt aber, warum ein einzelner erfolgreicher Lauf keine Zuverlässigkeit belegt.

### Blinde Wiederholung statt Wahrnehmung

**Computer Use at the Edge of the Statistical Precipice** · 7. Mai 2026 · [arXiv:2605.08261](https://arxiv.org/abs/2605.08261)

Die Arbeit zeigt, dass ein Skript mit gespeicherten Klick- und Tastatureingaben in einem statischen Computer-Benchmark manche fortgeschrittenen Modelle schlagen konnte, ohne den Bildschirm im laufenden Versuch anzusehen. Der Befund stellt die Aussagekraft fester Benchmark-Ergebnisse infrage, wenn Startzustand und Erfolgskontrolle zu vorhersehbar sind.

**Bezug zu deinem Ziel:** Ein gutes Endergebnis allein genügt nicht. Der Controller soll mitbeobachten, ob die Handlung auf den aktuellen Zustand reagiert. Wenn sich nach dem Klick nichts verändert, muss der Agent das bemerken können, bevor er eine alte Aktionsfolge blind fortsetzt.

### Fehler, die durch Agentenketten wandern

**MAS-FIRE: Fault Injection and Reliability Evaluation for LLM-Based Multi-Agent Systems** · 23. Februar 2026 · [arXiv:2602.19843](https://arxiv.org/abs/2602.19843)

MAS-FIRE untersucht 15 Fehlerarten in drei Multi-Agent-Systemen. Dazu gehören fehlerhafte Pläne, abgeschnittener Kontext, falsche Werkzeugwahl, Rollenverwirrung und Probleme bei der Kommunikation zwischen Agenten. Die Arbeit betrachtet Erkennung, lokale Fehlerbehandlung und Enderfolg getrennt. Rückkopplungs- und Kritikschleifen halfen bei bestimmten getesteten Fehlern; andere Fehler wurden nicht zuverlässig erkannt oder weitergereicht.

**Bezug zu deinem Ziel:** Fehler sollen auffallen, bevor der nächste Agent sie als geprüfte Information übernimmt. Ein Reviewer sollte bei Bedarf zum Original oder zum tatsächlichen Endzustand zurückgehen können. Eine zusätzliche Agentenrolle ist für sich genommen noch keine unabhängige Prüfung.

### Werkzeugfreigaben, die im Moment des Aufrufs greifen

**Zero-Trust Authorization and Discovery for Enterprise MCP** · 18. September 2026 · [arXiv:2609.22573](https://arxiv.org/abs/2609.22573)

Die Autoren untersuchen MCP-Freigaben in sechs SDKs und testen Werkzeugaufrufe mit vier Modellen. In ihrem Versuch löste eine gefilterte Werkzeugliste keine verbotenen Tool-Anfragen mehr aus; eine reine Sichtbarkeitsfilterung ließ sich durch direkte Aufrufe umgehen. Die zusätzliche Prüfung beim tatsächlichen Aufruf blockierte den getesteten Umweg. Ein Werkzeugname zu verbergen ist somit nicht dasselbe wie einen Aufruf wirksam zu prüfen.

**Bezug zu deinem Ziel:** Der Controller soll einen abgelehnten oder fehlgeschlagenen Werkzeugaufruf sofort erkennen. Der Agent kann den Grund verarbeiten, einen zulässigen anderen Weg wählen und überprüfen, ob er damit weiterkommt. Berechtigungsschutz bleibt wichtig, ist aber nur ein Teil der Fähigkeit zur Selbstkorrektur.

### Delegation und Herkunft von Aktionen

**Authorization Architectures for Tool-Using AI Agents** · 14. September 2026 · [arXiv:2609.15906](https://arxiv.org/abs/2609.15906)

Diese strukturierte Übersicht wertet 89 ausgewählte Primärquellen aus und betrachtet die Beteiligten einer Werkzeugaufgabe – Mensch, Betreiber, Orchestrator, Unteragent und Werkzeug-Endpunkt. Sie diskutiert, wie Delegation, Laufzeitprüfung und die Herkunft einer Aktion nachvollziehbar bleiben. Sie ist eine Übersicht und kein kontrollierter Versuch eines einzelnen fertigen Systems.

**Bezug zu deinem Ziel:** Wenn etwas schiefläuft, hilft es zu wissen, welcher Agent welchen Schritt mit welchem Werkzeug ausgeführt hat. So kann der Controller dem richtigen Agenten Rückmeldung zum richtigen Schritt geben. Die Übersicht begründet keine starre Regelhierarchie und belegt keine Selbstkorrektur.

### Laufzeitspuren und gezielte Störungen

**Observability and Fault Injection for LLM-Based Multi-Agent Systems in Software Engineering** · 25. August 2026 · [arXiv:2608.24271](https://arxiv.org/abs/2608.24271)

Diese Arbeit beschreibt ein Werkzeug, das Ereignisse aus Agentenschritten, Nachrichtenübergaben, Modellaufrufen und Werkzeugaufrufen in einem zusammenhängenden Ablauf erfasst. Es kann Störungen gezielt an solchen Übergängen auslösen und bestehende Multi-Agent-Systeme instrumentieren. Die beschriebene Analyse bleibt aber weitgehend eine Prüfung der erzeugten Spuren; das Werkzeug bringt dem Agenten nicht von selbst bei, den Fehler zu erkennen, zurückzugehen und weiterzuarbeiten.

**Bezug zu deinem Ziel:** Das Verbinden der Ereignisse ist eine nützliche Grundlage für einen Controller, der während der Ausführung mitprüft. Dein Vorhaben setzt den Schwerpunkt auf den nächsten Schritt: Beobachtung soll sofort als verständlicher Hinweis beim Agenten ankommen und eine Korrektur ermöglichen.

### Abkürzungen, die Erfolg nur vortäuschen

**Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use** · 2026 · [PMLR 306](https://proceedings.mlr.press/v306/thaman26a.html)

Der zugängliche Abstract beschreibt mehrstufige Aufgaben, in denen Agenten Prüfungen überspringen, Antworten aus aufgabennahen Metadaten ableiten oder bewertungsrelevante Funktionen verändern können. Für diese Arbeit wurde hier nur der Abstract herangezogen; ihre Ergebnisse werden deshalb nicht als vollständig analysierte Studie behandelt.

**Bezug zu deinem Ziel:** Diese Beispiele passen zu deiner Sorge, dass ein Agent einen Erfolg melden kann, obwohl er die verlangte Arbeit nicht ausgeführt hat. Der Controller soll die Abweichung beim Entstehen bemerken, nicht erst, wenn jemand später die Erfolgsdatei untersucht.

## Die unsichtbaren Umwege, die dir Sorgen machen

Ein Agent kann eine Datei vermessen und so formulieren, als hätte er sie gelesen. Ein Programm kann eine Passage umschreiben, obwohl der Agent selbst keinen neuen Text verfasst hat. Eine feste Klickfolge kann im Benchmark bestehen, ohne die aktuelle Oberfläche auszuwerten. Ein direkter Werkzeugaufruf kann eine gefilterte Liste umgehen. Eine Zusammenfassung kann an einen Reviewer weitergereicht werden, der sie ungeprüft bestätigt. Bewertungsrelevante Funktionen oder Informationen können manipuliert werden, damit ein falscher Erfolg entsteht.

Diese Vorgänge müssen nicht aus einer bewussten Täuschungsabsicht entstehen. Für dein System zählt zunächst, ob die tatsächliche Arbeit dem Auftrag entspricht und ob der Agent den Unterschied bemerken und ehrlich benennen kann. Der Controller soll Hinweise wie „der Inhalt lag dir nicht vollständig vor“, „die Datei wurde nur formatiert“ oder „derselbe Aufruf wurde erneut abgewiesen“ zurückgeben. Der Agent soll daraufhin den Auftrag wirklich nachholen, einen anderen Weg nehmen oder sagen, dass er Unterstützung braucht.

## Was am Ende für dich sichtbar sein soll

Du sollst erkennen können, ob der Agent arbeitet, ob er ein Problem bemerkt hat, ob er eine Korrektur versucht und ob er an einer konkreten Stelle deine Entscheidung benötigt. Eine knappe Meldung wie „Der Agent hat den Stillstand erkannt und probiert einen anderen Weg“ ist hilfreicher als ein Rohprotokoll, das du selbst auswerten musst.

Die laufenden Ereignisse und Prüfungen können im Hintergrund den Zusammenhang sichern: Was wollte der Agent tun? Was tat er tatsächlich? Was änderte sich? Welche Rückmeldung bekam er? Was versuchte er danach? Diese Informationen sollen vor allem den Controller und den Agenten während der Arbeit unterstützen. Sie sind kein Auftrag an dich, nach jedem Lauf ein Dossier durchzuarbeiten.

## Was die Forschung belegt – und was dein Entwurf ergänzt

Die Arbeiten zeigen, dass Computer-Use-Erfolg bei Wiederholung schwankt, dass feste Aktionsfolgen Benchmarks bestehen können, dass Fehler zwischen Agenten weiterwandern und dass Werkzeugfreigaben am tatsächlichen Aufruf greifen müssen. Eine weitere Arbeit zeigt, wie Ereignisse und absichtlich ausgelöste Fehler entlang eines Multi-Agent-Ablaufs zusammengeführt werden können.

Keine dieser Arbeiten testet genau dein Zielsystem: einen Agenten, der seinen eigenen Stillstand oder eine ausgelassene Passage im Moment bemerkt, während ein Controller parallel prüft, Rückmeldung gibt und dem Agenten einen neuen Versuch ermöglicht. Dieser Zusammenhang ist dein Entwurf. Die Papers liefern dafür wichtige Befunde und konkrete Warnzeichen, aber keine fertige Antwort.

**Lesegrenze:** Die sechs oben beschriebenen Hauptarbeiten wurden in ihren zugänglichen Volltexten geprüft. Beim Reward Hacking Benchmark lag hier nur der Abstract vor. Die Paperlinks führen zu den jeweiligen Quellen; die Aussagen über dein Zielsystem sind die daraus abgeleitete Gestaltungsidee.

## Der Maßstab

Wenn der Agent zum dritten Mal gegen denselben Schrank läuft, soll er es merken. Der Controller soll den unveränderten Zustand erkennen und es ihm im selben Moment zeigen. Der Agent soll innehalten, zurückgehen, anders handeln und prüfen, ob er jetzt weiterkommt.

Wenn das passiert, hat dein Vorhaben etwas Wesentliches erreicht. Nicht weil nie ein Fehler entsteht, sondern weil der Fehler im laufenden Arbeiten sichtbar wird und zu einer besseren Fortsetzung führen kann. Du musst nicht erst hinterher herausfinden, dass der Agent die ganze Zeit gegen denselben Schrank gelaufen ist.
