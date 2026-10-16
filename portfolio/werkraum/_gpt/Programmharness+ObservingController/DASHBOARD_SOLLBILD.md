# Dashboard-Sollbild und Abnahmekriterien

Stand: 2026-10-06

Diese Datei beschreibt ausschließlich, was das Dashboard aus Daniels Sicht abdecken und können soll. Sie beschreibt noch nicht, ob der aktuelle Code diese Anforderungen erfüllt.

## Schritt 1 – Was das Dashboard wirklich sein soll

Das Dashboard ist nicht nur eine hübsche Statusseite für den Harness. Es soll ein echter Observingcontroller und eine gemeinsame Steuer-, Erklär-, Kommunikations- und Kontrolloberfläche für die laufenden AI-Ströme und den darunterliegenden Harness sein.

### 1. Sofort verständlicher Gesamtzustand

- Auf einen Blick muss erkennbar sein, was gerade läuft, was pausiert ist, was blockiert ist, was historisch/abgelaufen ist und was technisch gestört ist.
- Desired State, Effective State und Health dürfen nicht vermischt werden.
- Ein grünes „aktiv“ darf nicht behaupten, etwas funktioniere, wenn die tatsächliche Wirkung blockiert oder kaputt ist.
- Der aktuelle Arbeitszustand der Harness muss sichtbar sein, inklusive Grund und gegebenenfalls Dauer.
- Das Dashboard soll Sekundenaktualität beziehungsweise eine echte Live-/Ticker-Wirkung haben. Polling darf technisch eine Zwischenlösung sein, das Ziel ist ein tatsächlich lebender Zustand und kein manuelles Refresh-Dashboard.
- Abweichungen und Dinge, die Aufmerksamkeit brauchen, sollen oben sichtbar werden, statt im restlichen Bestand unterzugehen.

### 2. Daniel muss steuern können, nicht nur beobachten

- Gesamte Harness pausieren/deaktivieren.
- Gesamte Harness wieder vollständig aktivieren.
- Einzelne Bausteine gezielt pausieren und wieder aktivieren.
- Bei Pausen soll sichtbar sein: warum, von wem, seit wann und gegebenenfalls wie lange.
- Eine Pause darf Zustände nicht löschen.
- Nicht mehr benötigte dynamische Schichten sollen archiviert statt vernichtet werden.
- PROJECT-, TASK- und EPHEMERAL-Schichten sollen gezielt angelegt und verwaltet werden können.
- Steuerung soll nicht nur global gelten, sondern später auch auf Projekt/Auftrag/Session/AI-Strom sinnvoll eingrenzbar sein.
- Nach jeder Steuerhandlung muss der tatsächlich erreichte Zustand erneut geprüft und sichtbar bestätigt werden. Ein erfolgreicher Button-Klick allein ist keine Abnahme.

### 3. Das Dashboard muss erklären

Für jeden relevanten Baustein muss verständlich sichtbar sein:

- Was ist das?
- Warum existiert es?
- Was tut es konkret?
- Was passiert, wenn ich es pausiere?
- Was ist sein aktueller Desired State?
- Was ist sein aktueller Effective State?
- Ist es technisch gesund?
- Warum ist der aktuelle Zustand so?
- Wovon hängt dieser Baustein ab?
- Welche Änderungen gab es?
- Welche Belege, Dokus, Pläne oder Wissenskontexte gehören dazu?

Die Oberfläche soll auch ohne Lesen des Python-Codes verständlich sein. Technische Rohwerte dürfen vorhanden sein, aber nicht die Hauptsprache der Oberfläche bestimmen.

### 4. Alltag und Vollansicht

- Es soll eine ruhige Alltagsansicht geben, die die tatsächlich wichtigen Dinge zeigt.
- Seltene Bau-, Diagnose- und Regelwerkzeuge gehören in eine Vollansicht beziehungsweise progressive Offenlegung.
- „Alltag“ darf wichtige Kontrolle nicht verstecken.
- „Voll“ darf keine Funktionen automatisch aktivieren. Es ist eine Ansicht, kein Betriebsmodus.
- Historie soll standardmäßig nicht die aktive Oberfläche verstopfen, aber jederzeit erreichbar bleiben.

### 5. Dashboard als Kommunikationsraum zwischen Daniel und ChatGPT

Das Dashboard soll nicht nur Zustände zeigen, sondern Aushandlung ermöglichen:

- getrennt sichtbar: „wartet auf Daniel“ und „wartet auf ChatGPT“;
- Kommentare pro Baustein;
- konkrete Änderungsvorschläge;
- Vorschläge kommentieren, nachfragen und feinjustieren;
- Vorschläge ausdrücklich annehmen oder ablehnen;
- vor einer Annahme muss verständlich gezeigt werden, was sich konkret ändern würde;
- ein Vorschlag darf sich nicht allein durch sein Vorhandensein aktivieren;
- Bewertungen/Einschätzungen von Daniel und ChatGPT pro Baustein;
- Resonanz/Verlauf bleibt erhalten und nachvollziehbar.

Das Dashboard soll dabei keine zusätzliche paternalistische Kontrollinstanz werden. Es soll Zusammenarbeit und Steuerbarkeit schaffen, nicht Babysitting.

### 6. Direktiven und Nutzerautorität

- Daniels ursprünglicher Wortlaut muss unverändert erhalten bleiben.
- Originalwortlaut und technische Ableitung müssen sichtbar getrennt bleiben.
- Es muss sichtbar sein, welche Direktive verifiziert ist und tatsächlich harte Wirkung erzeugen darf.
- Nur vertrauenswürdig erfasste Nutzerautorität darf harte Constraints/Supersession erzeugen.
- `authority_verified=true` beziehungsweise die äquivalente verifizierte Autorität ist ein echtes Gate, keine Dekoration.
- Unverifizierte Modellbehauptungen/Erinnerungen dürfen nicht als Nutzerbefehl behandelt werden.
- Eine abgeleitete Regel darf den ursprünglichen Auftrag nicht stillschweigend umdeuten.

### 7. PRIO-0 Auftragsscope

- Der aktuelle Auftrag/Task-Scope muss vor den übrigen Gates liegen.
- Off-Scope-Arbeit soll geblockt werden, bevor sie sich in Nebenpfade, Reparaturreligionen oder neue Eigenaufträge verwandelt.
- Ein TASK braucht ein verständliches Ziel und erlaubte Werkzeuge; Zielpfade und Abschlusskriterien können ihn weiter eingrenzen.
- Ein Off-Scope-Block ist zunächst einfach ein Scope-Block und darf nicht automatisch zu einer neuen Lernregel oder zu einem RECOVER-Drama aufgeblasen werden.

### 8. Scheuklappen pro Session

Der spätere, strengere Wunsch gilt:

- Eine Session soll standardmäßig nur ihren eigenen Auftrag, Kontext und Werkzeugraum sehen.
- Fremde Sessions sollen nicht automatisch als Informationsquelle auftauchen.
- Eine Session soll möglichst nicht einmal von selbst bemerken, was andere Sessions gerade tun.
- Fremde Session-Arbeit wird erst geöffnet, wenn Daniel ausdrücklich den Auftrag dazu gibt.
- Ein späteres Blackboard/Lernen zwischen Sessions ist optional und nachrangig, nicht der Default.
- Frühere lockerere Modelle wie FOCUS/AWARE/COLLABORATE reichen dafür nicht aus, wenn AWARE bereits fremde Arbeit automatisch sichtbar macht.

### 9. Mehrere AI-Ströme / Observingcontroller

Das Dashboard ist langfristig mehr als „ChatGPT-Harness“:

- Es soll die laufenden AI-Ströme/AI-Beings beziehungsweise ihre Arbeitszustände beobachtbar machen.
- Relevant sind unter anderem ChatGPT, Claude, Codex, Gemini/OpenCode beziehungsweise weitere angeschlossene Ströme.
- Sichtbar sein sollen Zustand, Auftrag, Wartezustand, Ergebnisse, Blocker und gegebenenfalls Übergaben.
- Zentrale Koordination soll möglich sein, wenn Daniel sie ausdrücklich will.
- Diese Beobachtbarkeit darf die Scheuklappenregel nicht aushebeln. Beobachter-/Leitstellenfunktion und normale Einzelsession sind unterschiedliche Sichtrechte.
- Das Dashboard soll dadurch zu einem Observingcontroller werden, nicht bloß zu einer Kartenwand des Harness.

### 10. Control-Leases

- Daniel soll ChatGPT gezielt und widerrufbar Steuerrecht geben können.
- Lease muss auf ein Layer-/Scope-Muster begrenzbar sein.
- Dauer kann zeitlich begrenzt oder ausdrücklich unbegrenzt sein.
- Grund muss sichtbar sein.
- Widerruf muss direkt möglich sein.
- Ohne Lease darf ChatGPT nicht eigenmächtig sensible Layer pausieren/archivieren.
- Reaktivieren und sichere Wiederherstellung dürfen sinnvoll anders behandelt werden als Abschwächen/Stilllegen.

### 11. Selbstlernschleife

Der gewünschte Ablauf ist nicht „LLM denkt sich Regel aus und aktiviert sie“:

1. echter Nutzerturn/Output bleibt als unverfälschte Erfahrungsschicht erhalten;
2. kleine Auswertung des Turns;
3. bei einem Fehler wird der konkrete Drift-Punkt gesucht;
4. daraus entsteht nur eine Kandidatenregel;
5. Kandidatenregel wird gegen alte reale Traces getestet;
6. erst eine bewährte Regel darf in Harness/LangGraph Verhalten erzeugen;
7. auch aktive Regeln können später schlechter werden und müssen abschwächbar, stilllegbar, ersetzt oder erneut geprüft werden.

Für das Dashboard bedeutet das:

- Kandidat, Testing, Active, Weakened, Retired/Superseded verständlich unterscheiden;
- Evidenz/Teststand sichtbar machen;
- keine automatische Aktivierung nur weil eine Kandidatenregel existiert;
- Daniel muss dumme Regeln direkt stilllegen können;
- Wiederöffnung zur Prüfung darf nicht automatisch Aktivierung bedeuten.

### 12. Struktur statt Kartenfriedhof

- Die Beziehung der Schichten untereinander muss sichtbar sein.
- Parent/Child-Struktur soll verständlich navigierbar sein.
- Von der Struktur muss man zur vollständigen Karte springen können.
- Suche, Filter und Historie sollen bei wachsendem Bestand Orientierung erhalten.
- Die Oberfläche darf nicht in hunderte gleichgewichtete Kästen zerfallen.
- Priorität: zuerst Aufmerksamkeit und Zustand, dann Details, dann Historie/Bauwerkzeuge.

### 13. Menschliche Bedienbarkeit

Die Abnahme ist nicht bestanden, nur weil Backend-Tests grün sind.

Die Seite muss sich für einen Menschen nachvollziehbar bedienen lassen:

- klare Sprache statt interner Harness-Begriffe als alleinige Orientierung;
- offensichtliche Hauptaktionen;
- gefährliche Aktionen müssen sich von Beobachtung unterscheiden;
- keine unnötige Formularwand im Alltag;
- keine unnötige mentale Last durch gleichzeitig sichtbare Spezialfunktionen;
- Scrollstrecke, Sticky-Elemente, Kartenhöhe und Informationsdichte müssen praktisch funktionieren;
- Buttons müssen klar sagen, welche Wirkung sie haben;
- nach Aktionen muss Ergebnis/Fehler sichtbar werden;
- Browser-/Playwright-Abnahme erfolgt manuell durch ChatGPT: selbst sehen, scrollen, gezielt klicken und nach jedem Schritt urteilen. Kein Runner, kein Reader, kein automatisch alles anklickendes Hilfsskript als Ersatz für diese menschliche Prüfung.

### 14. Sicherheit und Bedienbarkeit dürfen sich nicht gegenseitig zerstören

- Sicherheitsgates sollen echte unerlaubte Änderungen verhindern.
- Ein explizit beauftragter, enger Prüf- oder Arbeitsweg darf nicht an einer zufälligen falschen Autorisierung hängen bleiben.
- Die Lösung dafür darf nicht sein, generelles Shell-/Schreibrecht aufzureißen.
- Dashboard-Aktionen müssen nachvollziehbar auf die tatsächliche Nutzerautorität zurückgehen.
- Read-only-Beobachtung und echte Mutation müssen klar getrennt bleiben.

### 15. Abnahmekriterien

Das Dashboard gilt erst als ausreichend, wenn mindestens Folgendes zusammen erfüllt ist:

1. real erreichbar und für Daniel tatsächlich benutzbar;
2. aktueller Zustand kommt aus dem echten Live-System, nicht aus statischer Demo;
3. Desired/Effective/Health sauber getrennt;
4. globale Pause/Fortsetzen/Vollaktivierung vorhanden und nach Aktion gegengeprüft;
5. gezielte Layer-Steuerung vorhanden und erklärt;
6. Gründe, Dauer, Actor und Verlauf nachvollziehbar;
7. Daniel-/ChatGPT-Inboxen und Resonanz funktionieren;
8. Vorschläge zeigen vor Annahme ihre konkrete Wirkung;
9. Direktiven zeigen Originalwortlaut und Autoritätsstatus getrennt von Ableitungen;
10. Selbstlernschleife zeigt Kandidat → Test → Aktivierung → Abschwächung/Stilllegung nachvollziehbar;
11. TASK-Scope ist eine echte PRIO-0-Arbeitsgrenze;
12. strenge Scheuklappen sind als reale Session-Regel vorhanden, nicht nur als Textidee;
13. mehrere AI-Ströme können als Observingcontroller-Sicht abgebildet werden, ohne normale Sessions automatisch gegenseitig zu öffnen;
14. Alltag/Voll, Suche, Filter, Struktur und Historie verhindern Überladung;
15. Live-Aktualisierung ist praktisch schnell genug und idealerweise push-/eventgetrieben;
16. menschliche manuelle Browserabnahme von oben bis unten bestanden;
17. keine Aktion wird allein wegen HTTP 200 oder Button-Klick als erfolgreich behauptet; der erreichte Zustand wird danach geprüft;
18. Vision, implementierter Code und aktueller Live-Zustand werden im Dashboard und in der Abnahme auseinandergehalten.

## Schritt 2 – Ausgangspunkt für den folgenden Vergleich

Dashboard-Code gründlich in relevanten Bereichen gelesen: ja.

Diese Aussage bedeutet nur, dass die relevanten Dashboard-, Zustands-, Direktiven-, Lern-, Layer-, Feedback- und Steuerpfade als Codebasis für Schritt 3 herangezogen werden. Sie ersetzt nicht die manuelle Browserabnahme und behauptet nicht automatisch, dass alle oben genannten Anforderungen erfüllt sind.
