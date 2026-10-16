# Dashboard-Code gegen Sollbild – Erfüllungsprüfung

Stand: 2026-10-06

Verglichen wurde die zuvor angelegte Datei:

- `/root/werkraum/_gpt/DASHBOARD_SOLLBILD.md`

mit dem aktuellen Dashboard-Code und den direkt dahinterliegenden Harness-Funktionen, insbesondere:

- `/root/werkraum/tools/vps_mcp/vps_mcp_server.py`
- `/root/werkraum/tools/vps_mcp/mcp_workflow_graph.py`

Diese Datei beantwortet ausschließlich die Frage: **Erfüllt der aktuelle Code die Anforderungen aus DASHBOARD_SOLLBILD.md?**

Legende:

- **ERFÜLLT** = im Code als echte Funktion vorhanden und in der betrachteten Implementierung schlüssig verdrahtet.
- **TEILWEISE** = wesentliche Teile sind vorhanden, aber das Sollbild ist nicht vollständig erreicht.
- **NICHT ERFÜLLT** = im aktuellen Dashboard-Code fehlt die geforderte Funktion oder die vorhandene Funktion entspricht nicht dem späteren Soll.
- **NOCH NICHT ABNEHMBAR** = Code ist vorhanden, aber die verlangte menschliche/manuelle Browserabnahme fehlt noch.

---

## Gesamtergebnis

**Der aktuelle Code erfüllt das vollständige Dashboard-Sollbild noch nicht.**

Der Stand ist deutlich mehr als eine Statusseite. Der Code enthält bereits eine echte Steuer-, Erklär-, Resonanz-, Direktiven-, Lern- und Layer-Oberfläche mit persistentem PostgreSQL-Unterbau.

Der aktuelle Stand ist aber noch überwiegend ein **ChatGPT-Harness-Dashboard** und noch nicht der vollständige von Daniel gewünschte **Observingcontroller für mehrere AI-Ströme mit strengen Session-Scheuklappen**.

Die wichtigsten tatsächlich vorhandenen Kerne sind:

- kanonischer Live-State aus PostgreSQL;
- Desired / Effective / Health getrennt;
- globale Pause, Fortsetzen und Vollaktivierung;
- Einzel-Layer-Steuerung;
- PROJECT / TASK / EPHEMERAL;
- TASK-Scope als echtes PRIO-0-Gate;
- Daniel-/ChatGPT-Inboxen;
- Resonanz und Vorschläge mit Annahme/Ablehnung;
- konkrete Vorschlagswirkung vor Annahme;
- Control-Leases;
- Direktiven mit Originalwortlaut, Autoritätsstatus und Ableitungen;
- Selbstlernschleife mit Kandidat → Trace-Test → separate Aktivierung → Neubewertung / Abschwächung / Stilllegung;
- Strukturbaum, Suche, Filter, Historie;
- Alltag / Voll;
- 1-Sekunden-Aktualisierung im sichtbaren Tab.

Die größten noch fehlenden Sollteile sind:

1. strenge Session-Scheuklappen als echte Runtime-Regel;
2. Multi-AI-Strom-/AI-Beings-Observingcontroller im Dashboard selbst;
3. session-/strombezogene Dashboard-Sichten und Steuerrechte;
4. echtes Push-/Event-Live statt Polling;
5. vollständige manuelle Browser-/Playwright-Abnahme durch ChatGPT selbst;
6. einige Erfolgsprüfungen nach Aktionen sind noch zu oberflächlich;
7. die Oberfläche muss noch gegen reale menschliche Bedienung auf Informationsdichte und mentale Last geprüft werden.

---

## 1. Sofort verständlicher Gesamtzustand

**Urteil: WEITGEHEND ERFÜLLT**

Vorhanden:

- Der Dashboard-State kommt aus `harness_layers_snapshot("default")`, `harness_graph_snapshot("default")`, Feedback, Learning und Directives.
- Desired Status, Effective Status und Health werden getrennt geführt.
- Master-Pause erzeugt bei darunterliegenden aktiven Layern `BLOCKED_BY_PARENT`, statt ihren Desired State umzuschreiben.
- Statusgrund, Actor, Zeit, Healthgrund und Ablauf sind vorhanden.
- Oben gibt es eine Zusammenfassung und einen eigenen Aufmerksamkeitsbereich.
- Offene Vorschläge, ChatGPT-Inbox, Pausen, Health-Probleme, offene Gegenprüfungen und aktive Leases werden im Aufmerksamkeitsbereich herausgehoben.
- Runtime wird getrennt vom Layerzustand gezeigt.

Nicht vollständig:

- „LIVE“ bedeutet aktuell: erfolgreicher Poll der State-API.
- Sichtbarer Tab pollt jede Sekunde, versteckter Tab alle zehn Sekunden.
- Es gibt kein SSE/WebSocket/Event-Push.
- Damit ist die gewünschte lebendige Ticker-Wirkung funktional angenähert, aber technisch noch Polling.

**Bewertung: 85 %.**

---

## 2. Daniel muss steuern können, nicht nur beobachten

**Urteil: ERFÜLLT FÜR DEN HARNESS-KERN, NICHT FÜR DAS GESAMTE SPÄTERE DASHBOARD**

Vorhanden:

- `Harness pausieren`
- `Fortsetzen`
- `Alles voll aktivieren`
- Einzelne Layer pausieren / aktivieren.
- Nicht-CORE-Layer archivieren.
- Archivierte Layer aus Historie zurückholen.
- Abgelaufene Layer erneut aktivieren.
- Zeitlich begrenzte Pause per TTL.
- PROJECT / TASK / EPHEMERAL anlegen.
- Grund wird bei Aktionen mitgeführt.
- Zustände werden append-only über Events persistiert.
- `post()` führt nach erfolgreichem POST direkt `refresh()` aus.

Einschränkung:

- Das erneute `refresh()` ist eine Zustandsrücklesung, aber die UI meldet anschließend pauschal den Aktionsnamen als Erfolg.
- Es gibt noch keine gezielte semantische Prüfung wie „gewünschter Zielzustand ist nach Refresh tatsächlich exakt eingetreten“.
- Steuerung ist im Dashboard im Wesentlichen auf den Default-Harness-State ausgerichtet, nicht auf frei wählbare Sessions oder mehrere AI-Ströme.

**Bewertung: 80 %.**

---

## 3. Das Dashboard muss erklären

**Urteil: ERFÜLLT**

Für Layer zeigt der Code:

- Warum gibt es das?
- Was tut es?
- Was passiert bei Pause?
- aktuellen Status;
- Health;
- Statusgrund;
- Status-Actor;
- Healthgrund;
- Health-Actor;
- Ablauf;
- Parent;
- Scope;
- Provenienz;
- Bau-/Wissenskontext;
- Zustandsverlauf;
- Definitionsverlauf;
- Resonanz.

Zusätzlich vorhanden:

- Kurzorientierung „Wie benutzt man das hier?“
- Begriffserklärung Desired / Effective / Health / CORE / PROJECT / TASK / EPHEMERAL / Lease.
- technische Werte sind überwiegend hinter Details versteckt.

Das erfüllt den erklärenden Harness-Teil des Sollbilds gut.

**Bewertung: 95 %.**

---

## 4. Alltag und Vollansicht

**Urteil: ERFÜLLT IM CODE, BEDIENABNAHME FEHLT**

Vorhanden:

- `Alltag`
- `Voll`
- Zustand wird in `localStorage` gespeichert.
- `.advanced-only` ist im Alltag versteckt.
- Vollansicht aktiviert keine Harness-Funktion, sondern nur zusätzliche UI.
- Direktiven, Selbstlernschleife und Anlegen dynamischer Layer sind in der Vollansicht.
- Historie ist standardmäßig ausgeblendet und separat zuschaltbar.

Noch offen:

- Ob die Aufteilung sich für Daniel tatsächlich ruhig und verständlich anfühlt, ist ohne die verlangte manuelle Browserabnahme nicht abgeschlossen.

**Bewertung Code: 95 %.**
**Abnahme: offen.**

---

## 5. Kommunikationsraum Daniel ↔ ChatGPT

**Urteil: WEITGEHEND ERFÜLLT**

Vorhanden:

- „Wartet auf Daniel“
- „Wartet auf ChatGPT“
- Kommentare
- Vorschläge
- Antworten / Rückfragen / Feinjustierung
- Annehmen
- Ablehnen
- Bewertungen
- Daniel- und ChatGPT-Einschätzungen pro Layer
- gemeinsame Resonanzspur
- Vorschläge bleiben offen bis zur Entscheidung
- Vorschlag allein verändert nichts
- vor Annahme wird die konkrete Wirkung erklärt
- maschinenlesbare Vorschläge können gezielt angewendet werden
- Freitext-Vorschlag wird bei Annahme nur als Entscheidung protokolliert

Einschränkung:

- Die eigentliche ChatGPT-Seite verarbeitet die Inbox nicht automatisch allein dadurch, dass die Dashboard-UI existiert. Die andere Seite der Kommunikationsschleife hängt weiter davon ab, dass ChatGPT/Harness die Inbox aktiv liest und quittiert.

**Bewertung: 90 %.**

---

## 6. Direktiven und Nutzerautorität

**Urteil: ERFÜLLT**

Vorhanden:

- Original-`raw_text` wird separat gespeichert.
- Dashboard zeigt ausdrücklich „Dein Originalwortlaut“.
- Constraints und Invarianten werden getrennt dargestellt.
- `source_kind == TRUSTED_CLIENT_CAPTURE` erzeugt `authority_verified=true`.
- Unverifizierte Einträge werden als Erinnerung behandelt.
- Direktiven können ACTIVE / ARCHIVED / SUPERSEDED sein.
- Supersession bleibt nachvollziehbar.
- harte Mutation verlangt einen passenden Reminder für exakt Tool + Argumente.
- harte Constraints werden deterministisch geprüft.
- ohne positiven verifizierten Autorisierungs-Constraint bleibt Mutation fail-closed.

**Bewertung: 95 %.**

---

## 7. PRIO-0 Auftragsscope

**Urteil: ERFÜLLT**

Der relevante Ablauf ist eindeutig:

1. `preflight_action()`
2. ruft zuerst `_task_scope_preflight()` auf;
3. wenn dieser blockiert, wird sofort zurückgegeben;
4. erst danach folgt `base_evaluate_action()` und der übrige Workflow.

Damit liegt TASK-Scope tatsächlich vor den übrigen normalen Aktionsgates.

Zusätzlich:

- hart wirksam wird nur ein verifizierter TASK;
- Daniel-Dashboard-Actor + verifizierte Dashboard-Provenienz werden verlangt;
- Ziel ist Pflicht;
- mindestens ein erlaubtes Toolmuster ist Pflicht;
- Zielpfade können eingeschränkt werden;
- mehrere gleichzeitig verifizierte TASKs führen fail-closed zu TASK_SCOPE_BLOCK;
- Off-Scope-Tool und Off-Scope-Ziel werden klar als TASK_SCOPE_BLOCK behandelt;
- Guidance sagt ausdrücklich, Nebenfund parken statt Nebenpfad verfolgen.

**Bewertung: 100 % für den geprüften Codepfad.**

---

## 8. Scheuklappen pro Session

**Urteil: NICHT ERFÜLLT**

Der spätere strenge Wunsch ist im aktuellen Dashboard-/Workflow-Code nicht als eigene Session-Isolationslogik vorhanden.

Gezielte Suche ergab keine Implementierung für:

- Scheuklappen;
- FOCUS/AWARE/COLLABORATE im Sinne fremder Session-Sicht;
- explizite Foreign-Session-Sichtrechte;
- Standardregel „andere Sessions gar nicht bemerken“;
- explizites Öffnen fremder Sessions durch Daniel;
- getrennte Observer-/Leitstellenrolle versus normale Session.

Wichtig:

- `FOCUSED_READING` im Workflow ist nur ein Arbeitszustand nach Datei-Lesen und hat nichts mit der gewünschten Session-Scheuklappe zu tun.
- Vorhandene `session_id`-Felder und per-Session Harness-Zustände reichen nicht aus, um die strenge Sichtisolation zu erfüllen.

**Bewertung: 0–10 %.**

---

## 9. Mehrere AI-Ströme / Observingcontroller

**Urteil: BACKEND-GRUNDLAGEN VORHANDEN, DASHBOARD NICHT ERFÜLLT**

Im VPS/MCP existieren bereits AI-Strom-Funktionen, unter anderem:

- Atlas AI-Stream-State;
- AI-Stream-Verbindungen;
- getrennte Mitschriften;
- Stream-Status;
- Sessions/Agenten für ChatGPT, Claude, Codex, Gemini und weitere.

Aber:

- Der HTML-Dashboard-Körper `_harness_dashboard_html()` zeigt diese AI-Ströme nicht als eigenen Observingcontroller-Bereich.
- Es gibt keine zentrale sichtbare Liste der laufenden AI-Ströme.
- Es gibt dort keine pro Strom sichtbaren Aufträge, Wartezustände, Blocker, Ergebnisse oder Übergaben.
- Es gibt keine UI-Rollenlogik, die Leitstellenblick und normale Session-Scheuklappe trennt.

Damit ist Infrastruktur vorhanden, aber genau der vom späteren Dashboard-Ziel verlangte Observingcontroller fehlt noch.

**Bewertung Backend-Voraussetzungen: ca. 60 %.**
**Bewertung aktuelles Dashboard dafür: ca. 10–20 %.**

---

## 10. Control-Leases

**Urteil: ERFÜLLT**

Vorhanden:

- Layer-Muster;
- optionaler Scope;
- Grund;
- optionales Ablaufdatum;
- unbegrenzt möglich;
- Widerruf;
- persistierte Lease;
- Prüfung auf Ablauf und Revocation;
- `harness_control_allowed()` prüft das Layer-Muster.

Das Dashboard erklärt außerdem, dass Reaktivieren anders behandelt wird als Abschwächen.

**Bewertung: 95 %.**

---

## 11. Selbstlernschleife

**Urteil: WEITGEHEND ERFÜLLT**

Vorhanden:

- Erfahrungstabellen;
- Driftpunkte;
- Kandidatenregel;
- `test_candidate_rule()` spielt Regel gegen gespeicherte alte Turns;
- der Ausgangsfehler muss abgedeckt sein;
- Kollisionen mit alten Erfolgen werden gezählt;
- nicht deterministisch testbare Regelarten blockieren Aktivierung;
- Test endet in TESTING;
- Aktivierung ist ein separater Schritt;
- `activate_tested_rule()` verlangt bestandenen Test;
- ACTIVE darf hart wirken;
- WEAKENED darf nicht hart blockieren;
- RETIRED und SUPERSEDED greifen nicht mehr;
- Nutzerfeedback aus dem Dashboard wird getrennt attribuiert;
- Regeln können durch neue Erfahrung ACTIVE, WEAKENED oder RETIRED werden;
- manuelles Stilllegen ist möglich;
- erneutes Öffnen führt nur zu TESTING, nicht direkt ACTIVE.

Einschränkung:

- Die Sollkette „jeder Turn bekommt automatisch eine kleine Auswertung“ ist als vollständige allgegenwärtige Garantie nicht allein aus diesem Dashboard-Code bewiesen.
- Das Dashboard verwaltet die vorhandene Lernpipeline gut; ob jeder relevante Turn zuverlässig durch den gesamten vorgelagerten Experience-/Evaluation-Pfad läuft, ist eine breitere Systemfrage.

**Bewertung Dashboard + Learning-Kern: 90 %.**

---

## 12. Struktur statt Kartenfriedhof

**Urteil: ERFÜLLT IM CODE, UX-ABNAHME OFFEN**

Vorhanden:

- Parent/Child-Struktur;
- Einrückung;
- Klick springt zur Layer-Karte;
- Suche;
- Kind-Filter;
- Status-Filter;
- Historie ein-/ausblenden;
- Historie wird hinter aktive Zustände sortiert;
- Aufmerksamkeitsbereich steht vor Karten;
- Details sind einklappbar;
- Bau-/Wissenskontext und technische Rohwerte sind progressive Details.

Offen:

- Ob die Seite bei realem Bestand trotzdem zu lang / zu dicht / zu formularlastig wirkt, kann Code allein nicht beantworten.

**Bewertung Code: 90 %.**
**Menschliche UX-Abnahme: offen.**

---

## 13. Menschliche Bedienbarkeit

**Urteil: NOCH NICHT ABNEHMBAR**

Code-seitig positiv:

- deutsche Begriffe;
- Hilfetexte;
- Alltag/Voll;
- progressive Details;
- responsive CSS für kleine Breite;
- Sticky-Toolbar auf größeren Displays;
- klare Farben für gut/warn/bad;
- konkrete Aktionslabels;
- Fehlermeldungen über Action-Status;
- Such- und Filterfunktionen.

Aber die ausdrücklich geforderte Abnahme lautet:

- ChatGPT sieht die Seite selbst;
- scrollt selbst von oben bis unten;
- entscheidet selbst, was angeklickt wird;
- klickt gezielt;
- beurteilt nach jedem Schritt die menschliche Bedienung;
- kein Runner/Reader/automatisches Klickskript als Ersatz.

Diese Abnahme wurde bisher **nicht korrekt durchgeführt**.

Deshalb darf dieses Kriterium nicht als bestanden markiert werden.

**Bewertung: offen / nicht abgenommen.**

---

## 14. Sicherheit und Bedienbarkeit

**Urteil: TEILWEISE ERFÜLLT**

Stark:

- harte Nutzerautorität;
- exakter Reminder;
- fail-closed;
- Invarianten;
- TASK-Scope;
- Control-Lease;
- getrennte Read-/Mutation-Logik.

Problem:

- In dieser Session zeigte sich praktisch, dass explizit beauftragte Browser-/Prüfhandlungen an der Autorisierungs-/Verify-Kette hängen bleiben können.
- Der Versuch, das durch einen eigenen Local-Audit-Weg zu lösen, entstand erst während dieser Session und gehört nicht zum ursprünglichen Soll.
- Damit ist das Grundprinzip korrekt, aber Bedienbarkeit und Sicherheitskette sind noch nicht sauber genug zusammengeführt.

**Bewertung: 75 %.**

---

## 15. Die 18 Abnahmekriterien einzeln

### 1. Real erreichbar und für Daniel tatsächlich benutzbar

**TEILWEISE / historisch erreicht, aktuelle manuelle Abnahme offen.**

Route und HTML/API existieren. Daniel hatte die Seite bereits erstmals zugänglich. Die heutige vollständige manuelle Browserabnahme fehlt.

### 2. Echter Live-Systemzustand statt statischer Demo

**ERFÜLLT.**

State wird aus PostgreSQL/Harness-Funktionen erzeugt.

### 3. Desired / Effective / Health sauber getrennt

**ERFÜLLT.**

### 4. Globale Pause / Fortsetzen / Vollaktivierung plus Gegenprüfung

**WEITGEHEND ERFÜLLT.**

Aktionen existieren und anschließend wird State neu geladen. Eine explizite semantische Soll/Ist-Verifikation pro Aktion könnte noch stärker sein.

### 5. Gezielte Layer-Steuerung vorhanden und erklärt

**ERFÜLLT.**

### 6. Gründe, Dauer, Actor und Verlauf nachvollziehbar

**ERFÜLLT.**

### 7. Daniel-/ChatGPT-Inboxen und Resonanz

**ERFÜLLT.**

### 8. Vorschläge zeigen vor Annahme konkrete Wirkung

**ERFÜLLT.**

### 9. Direktiven: Originalwortlaut + Autoritätsstatus getrennt von Ableitung

**ERFÜLLT.**

### 10. Selbstlernschleife Kandidat → Test → Aktivierung → Abschwächung/Stilllegung

**ERFÜLLT FÜR DEN IMPLEMENTIERTEN LEARNING-KERN.**

### 11. TASK-Scope ist echte PRIO-0-Arbeitsgrenze

**ERFÜLLT.**

### 12. Strenge Scheuklappen als reale Session-Regel

**NICHT ERFÜLLT.**

### 13. Mehrere AI-Ströme als Observingcontroller-Sicht ohne automatische gegenseitige Öffnung

**NICHT ERFÜLLT IM DASHBOARD.**

Backend-/Atlas-Grundlagen existieren, UI und Sichtrechte fehlen.

### 14. Alltag/Voll, Suche, Filter, Struktur, Historie gegen Überladung

**CODE-SEITIG ERFÜLLT; UX-ABNAHME OFFEN.**

### 15. Praktisch schnelle Live-Aktualisierung, ideal push/eventgetrieben

**TEILWEISE ERFÜLLT.**

1-Sekunden-Polling sichtbar, 10 Sekunden versteckt. Kein Push.

### 16. Menschliche manuelle Browserabnahme von oben bis unten

**NICHT ERFÜLLT / NOCH NICHT DURCHGEFÜHRT.**

### 17. Erfolg nicht nur wegen HTTP 200/Button; Zielzustand danach prüfen

**TEILWEISE ERFÜLLT.**

Nach POST wird `refresh()` ausgeführt. Der Code vergleicht aber nicht für jede Aktion explizit den erreichten Zustand mit dem erwarteten Ziel und meldet bei erfolgreichem POST anschließend generisch Erfolg.

### 18. Vision / Code / Live-Zustand auseinanderhalten

**TEILWEISE ERFÜLLT.**

Der Code trennt Zustandsarten gut. Eine explizite UI-Trennung „Vision / implementiert / live“ für das gesamte Dashboard-Ziel existiert nicht.

---

## Gesamtwertung nach Bereichen

### Harness-Steuerdashboard

**stark / weitgehend gebaut**

Der aktuelle Code ist hierfür substantiell. Das ist kein Mockup und keine bloße Karte.

### Erklär- und Resonanzoberfläche

**stark / weitgehend gebaut**

Die Oberfläche erklärt Bausteine, zeigt Historie, bietet Vorschläge, Antworten, Bewertungen und zwei Inboxen.

### Nutzerautorität / Direktiven / TASK-Scope

**sehr stark**

Hier liegt aktuell einer der solidesten Teile.

### Selbstlernschleife

**substanziell gebaut**

Test, Aktivierung, Feedback, Reassessment und Abschwächung sind echte Codepfade.

### Menschliche UX-Abnahme

**offen**

Code-Lesen ersetzt diese Prüfung ausdrücklich nicht.

### Strenge Scheuklappen

**fehlt**

Das ist kein kleiner UI-Punkt, sondern eine fehlende Runtime-/Sichtrechte-Schicht.

### Multi-AI-Observingcontroller

**im Dashboard noch nicht gebaut**

Die Daten-/Toolgrundlagen für AI-Ströme existieren an anderer Stelle im VPS/MCP. Das Dashboard nutzt sie aber noch nicht als Observingcontroller.

### Live/Ticker

**brauchbare Zwischenstufe**

1-Sekunden-Polling ist schnell, aber noch kein Event-Push.

---

## Schlussantwort

**Erfüllt der aktuelle Dashboard-Code Daniels vollständige Anforderungen?**

**Nein.**

Er erfüllt bereits einen großen, funktionalen Kern des gewünschten Systems und ist deutlich weiter als ein simples Harness-Statusdashboard. Für den vollständigen Zielzustand fehlen aber mindestens drei Abnahmeblocker:

1. **strenge Session-Scheuklappen als echte technische Regel;**
2. **Multi-AI-Strom-Observingcontroller im Dashboard;**
3. **korrekte manuelle Browser-/Playwright-Abnahme durch ChatGPT selbst.**

Dazu kommen zwei mittlere Lücken:

4. **Push-/Event-Live statt Polling;**
5. **explizitere Soll/Ist-Verifikation nach jeder Dashboard-Mutation.**

Damit lautet der belastbare Stand:

**Harness-Dashboard-Kern: weitgehend vorhanden.**

**Vollständiges von Daniel gemeintes Dashboard / Observingcontroller: noch nicht erfüllt.**

