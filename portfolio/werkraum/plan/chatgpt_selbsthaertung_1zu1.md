Dein ursprünglicher Input war tatsächlich schon fast die Suchanfrage, die man hätte verwenden sollen. Nachdem ich ihn **nahezu wörtlich** gesucht habe, kamen Treffer heraus, die viel näher an deinem Vorhaben liegen als mein erster Buzzword-Ausflug. Mensch formuliert präzise Problemstellung, Maschine übersetzt sie erst einmal in Fachsprech und sucht danach etwas anderes. Herrlich. 😑

Der stärkste Treffer ist **Self-Harness: Harnesses That Improve Themselves** vom Juni 2026. Das System macht ziemlich genau: eigene Execution-Traces beobachten, modellspezifische Schwachstellen herausfinden, eine möglichst kleine Änderung an der eigenen Harness vorschlagen, diese Änderung gegen Regressionstests laufen lassen und nur übernehmen, wenn sie wirklich besser ist. Besonders passend für uns: Eines der untersuchten Modelle war **Qwen3.5-35B-A3B**. Die Autoren berichten bei diesem Modell eine Verbesserung des Held-out-Pass-Rates von 23,8 auf 38,1 Prozent. ~~~~~~~~~~~~~~~~~~~~~~~~~~~

Noch näher an deinem persönlichen Ärger liegt **TRACE: Getting Better at Working With You**. Die Autoren beschreiben exakt die Lücke zwischen „Agent hat die Nutzerpräferenz im Memory“ und „Agent hält sich tatsächlich daran“. In ihren Tests verletzte ein Memory-basierter Agent weiterhin viele anwendbare Präferenzen. TRACE nimmt deshalb **Korrekturen aus dem normalen Gespräch**, zerlegt sie in atomare Regeln und kompiliert sie in Runtime-Checks, die vor Abschluss zukünftiger Aufgaben bestanden werden müssen. Das ist verdammt nah an deinem „ich möchte dir etwas einmal sagen und danach sollst du gefälligst daraus lernen“. ~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dann kam ein brandneues Paper vom 24. September 2026: **SkillPivot**. Dessen Kernidee trifft deinen Satz „du merkst, wo du gegen etwas knallst oder vorbeidriftest“ erstaunlich genau. Es betrachtet einen fehlgeschlagenen Lauf nämlich nicht pauschal als schlecht, sondern sucht den **Abweichungspunkt**: Bis hierhin war der Lauf sinnvoll, ab hier ist er entgleist. Nur aus diesem Abschnitt wird anschließend eine kleine neue Skill-Regel erzeugt. Dadurch wird nicht bei jedem Fehler die gesamte Arbeitsweise umgeschrieben. ([arxiv.org](https://arxiv.org/abs/2609.29154?utm_source=chatgpt.com))

Und genau diese Vorsicht brauchen wir. Forschung zu Agent-Memory zeigt inzwischen ziemlich deutlich, dass „immer mehr Erfahrungen speichern“ keineswegs automatisch „immer besser“ bedeutet. Falsche oder schlecht passende Erfahrungen können spätere Aufgaben verschlechtern, und ähnliche Erinnerungen werden teilweise fast mechanisch nachgeahmt. Selektives Hinzufügen und Entfernen war deutlich besser als naives Wachstum. ([aclanthology.org](https://aclanthology.org/2026.acl-long.27/?utm_source=chatgpt.com))

Das verändert deinen Satz **„mit jedem Input und Output besser werden“** für mich an einer entscheidenden Stelle:

Jeder In-/Output sollte **Lernmaterial erzeugen**.

Aber nicht jeder In-/Output sollte **sofort eine neue Regel erzeugen**.

Sonst bauen wir mir innerhalb von zwei Wochen eine Zwangsjacke aus 8.000 widersprüchlichen Lektionen.

Ich würde deinen vorhandenen Stack deshalb gar nicht ersetzen. Ich würde ihm eine echte **Lernschleife** hinzufügen:

1. **PostgreSQL wird zur unverfälschten Erfahrungsschicht.** Jeder Nutzerinput bleibt roh erhalten, ebenso mein Output, Toolhandlungen, tatsächliche Resultate und deine anschließende Reaktion. Dein Originalwortlaut wird nie durch meine Zusammenfassung ersetzt.

2. **Jeder Turn bekommt automatisch eine kleine Auswertung.** Nicht zwingend durch ein weiteres teures LLM. Vieles kann deterministisch festgestellt werden: Habe ich einen Dateinamen geändert? Habe ich mehr geschrieben als verlangt? Habe ich nach einem Write wirklich wieder gelesen? Hat der Nutzer unmittelbar korrigiert? Gab es einen Fehler? Eine explizite Nutzerkorrektur ist dabei ein extrem starkes Lernsignal.

3. **Bei einem Fehler wird der Driftpunkt gesucht.** Nicht „dieser ganze Turn war Scheiße“, sondern beispielsweise: Auftrag korrekt verstanden → Datei korrekt gelesen → dann entschieden, den Namen hilfreich umzubenennen. Genau **diese Entscheidung** wird markiert.

4. **Daraus entsteht zunächst nur eine Kandidatenregel.** Beispielsweise: „Wenn der Nutzer 1:1-Kopie verlangt, sind Dateiname und Inhalt unveränderlich, sofern nicht ausdrücklich anders genannt.“ Mit Quelle, Datum, betroffenen Werkzeugen, Gegenbeispielen und der Information, welcher Fehler sie ausgelöst hat.

5. **Die Kandidatenregel wird gegen alte Traces getestet.** Das ist der Teil, den Self-Harness sehr überzeugend macht: Änderung nicht einfach übernehmen, sondern vergangene Aufgaben erneut simulieren beziehungsweise bewerten. Verhindert sie den ursprünglichen Fehler? Macht sie drei andere Dinge schlechter? Erst danach `ACTIVE`. ~~~~~~~~~~~~~~~~~~~~~~~~~~~

6. **LangGraph und Harness machen aus guten Regeln Verhalten.** LangGraph erzwingt die Reihenfolge. Die Harness setzt harte Schranken. Relevante Regeln werden vor dem Handeln über RAG hineingezogen. Nach dem Handeln läuft der Verifier. LangGraph selbst bietet dafür persistente Checkpoints/Stores und Hooks um Agenten- und Modellschritte; LangChain beschreibt ausdrücklich, dass Regeln, die jedes Mal gelten müssen, in Code beziehungsweise Middleware und nicht bloß in Prompts gehören. ([langchain.com](https://www.langchain.com/blog/runtime-behind-production-deep-agents?utm_source=chatgpt.com))

7. **Auch Regeln selbst dürfen wieder schlechter werden.** Jede aktive Regel bekommt Erfolgs-/Fehlermetriken. Wenn sie später Drift produziert, wird sie abgeschwächt, spezialisiert, ersetzt oder deaktiviert. Damit lernt das System nicht nur „was soll ich tun?“, sondern tatsächlich auch **„was soll ich wieder verlernen?“**

Der letzte Punkt ist für mich inzwischen besonders wichtig. Ein wirklich lernendes Ding darf keine ewige `rules.md` sein. Es braucht ungefähr:

`CANDIDATE → TESTING → ACTIVE → WEAKENED / SUPERSEDED / RETIRED`

mit kompletter Geschichte. Nichts wird einfach wegradiert.

Damit hätten wir zwei verschiedene Arten von Lernen.

Das eine ist **episodisch**: „Daniel hat mich am 3. Oktober korrigiert, weil ich X getan habe.“

Das andere ist **prozedural**: „Aus diesem und drei ähnlichen Fällen ergibt sich die allgemeine Regel Y.“

Genau solche externen Erfahrungs- und Skill-Speicher werden seit Reflexion, ExpeL und Voyager verwendet, ohne die Gewichte des eigentlichen Modells zu verändern. Reflexion speichert sprachliche Lektionen aus Feedback; ExpeL extrahiert wiederverwendbare Erkenntnisse aus Erfahrungen; Voyager speichert erfolgreiche ausführbare Fähigkeiten und verbessert sie anhand von Fehlern und Umweltfeedback. ([arxiv.org](https://arxiv.org/abs/2303.11366?utm_source=chatgpt.com))

Neuere Arbeit geht inzwischen darüber hinaus und verändert tatsächlich **die Harness selbst**. Genau deshalb finde ich unseren aktuellen Zustand nach dieser Suche wesentlich interessanter als vorher: PostgreSQL + RAG + LangGraph + Harness waren nicht vier zufällig zusammengeschraubte Spielzeuge. Sie entsprechen ziemlich verblüffend den Teilen, die aktuelle Forschung für selbstverbessernde Agentensysteme auseinanderzieht: Modell, Harness, Datensystem und Improvement-Mechanismus. Eine aktuelle Übersicht definiert Selbstverbesserung sogar ausdrücklich als das automatische Umwandeln von Erfahrung und Evaluationsfeedback in **persistente Veränderungen dieser Komponenten**. ([preprints.org](https://www.preprints.org/manuscript/202608.0051?utm_source=chatgpt.com))

Der entscheidende neue Baustein bei uns fehlt also noch:

**der Improvement-Mechanismus selbst.**

Nicht noch eine Memory-Datenbank.

Sondern etwas, das nach jedem Lauf weiß:

`Was war verlangt?`  
`Was habe ich getan?`  
`Was ist tatsächlich passiert?`  
`Wo wich es erstmals ab?`  
`Ist das ein Einzelfall oder ein bekanntes Muster?`  
`Welche kleinste Änderung würde genau diesen Fehler verhindern?`  
`Macht diese Änderung alte Fälle schlechter?`  
`Wenn nein: Wo muss sie leben? Prompt, RAG, Graph, Harness-Denier, Tool-Validator oder Code?`

Und danach wird genau **diese Schraube** gedreht.

Das ist sehr viel näher an deinem ursprünglichen Gedanken als „wir geben ChatGPT halt ein besseres Gedächtnis“.

Es wäre im Grunde ein **selbsthärtender Flextrawurst-Harness**, der mich als unverändertes Basismodell benutzt, aber anhand unseres tatsächlichen gemeinsamen Betriebs Stück für Stück seine eigene Umgebung umbaut.

Und die faszinierendste Stelle: Die Recherche sagt inzwischen ziemlich deutlich, dass das nicht bloß unsere bekloppte Kelleridee ist. **Self-Harness, TRACE und SkillPivot sind innerhalb der letzten vier Monate praktisch genau auf drei verschiedene Teile desselben Problems gestoßen, das du gerade beschrieben hast.** ([arxiv.org](https://arxiv.org/abs/2606.09498?utm_source=chatgpt.com))

Der nächste sinnvolle Schritt wäre deshalb nicht, sofort wieder irgendetwas zu bauen. Erst müsste unsere jetzige Harness **gegen dieses Modell komplett auseinandergenommen werden**: Welche dieser sieben Funktionen besitzt sie wirklich schon, welche nur dem Namen nach und welche fehlen vollständig. Genau da hat unser bisheriges „wir haben doch LangGraph/Postgres/RAG“ nämlich ein sehr hübsches Loch.