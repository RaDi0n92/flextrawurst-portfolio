# Aktionen / CLI-Agenten / Wartezustände · komprimierter Arbeitskörper

Status: reale Capability-Funde + wenige visuelle Impulse.

Nicht aus jedem Tool eine Weltklasse bauen.

## 1. Die CLI-/Runtime-Körper sind verschieden

### Claude Code
Reale Besonderheiten u. a.:
- Sessions fortsetzen/forken
- Background-Arbeit
- Custom Agents/Subagents
- Tool-Allow/Deny / Permissionmodi
- Hooks/Streamausgabe
- Browser-/IDE-/Cloudanschlüsse

Designimpuls:
- Background-Arbeit kann als fortbestehende Maschine/Arbeitsstelle sichtbar bleiben, während die Vordergrundinstanz weiterzieht.

### Codex
Reale Besonderheiten u. a.:
- `exec`
- eigener Reviewmodus
- Sandbox-/Approvalmodi
- resume/fork/archive
- MCP/App-/Remote-Control-Anschlüsse

Designimpuls:
- Review, Fork und Sandbox dürfen besonders klar getrennte Arbeitsformen sein.

### Gemini CLI
Reale Besonderheiten u. a.:
- Worktrees
- Plan/Auto-Edit/YOLO-/Policy-Modi
- Hooks, Skills, Extensions, MCP/ACP

Wichtig: **Gemini CLI/Modellfamilie nicht mit Gravityy oder Gemgem gleichsetzen.**

Designimpuls:
- Worktree = temporäre Nebenbaustelle; Plan = Augen/Karte aktiv, Hände zurückhaltender.

### Kimi CLI
Reale Besonderheit: AFK-Modus kann ohne anwesenden Menschen weiterarbeiten und Fragen anders behandeln als normaler `human_input`-Flow.

Designimpuls:
- `AFK` darf anders aussehen als normal `running` oder `waiting`.

### GPT / ChatGPT über VPS-MCP
Arbeitskörper entsteht hier vor allem durch konkrete Toolaufrufe, Dateien, Browser/CDP, Dienste, DB, Assets und Handoffs.

Mehrere GPT-Instanzen dürfen gleichzeitig verschiedene mobile Arbeitskörper besitzen.

### Zensi
Zensi ist **eigene Gattung**, nicht normaler CLI-Agent:
- Sandbox/LIVE
- Version/Diff
- Aufgabenloops
- Traum/Schlaf
- Symposien
- Chronobranches usw.

Nicht still auf Claude/Codex/Gemgem übertragen.

## 2. Toolkatalog ist nicht gleich verfügbare Handlung

Unterscheiden:
- Tool/Capability wird beworben
- Implementierung existiert
- aktuelle Runtime kann sie erreichen
- konkrete Aktion ist erlaubt
- Wirkung wurde tatsächlich bestätigt

Live wurde bereits gefunden, dass einzelne im Toolvertrag sichtbare History-Funktionen trotzdem `Unbekanntes Tool` liefern.

Darstellung darf deshalb keine Fähigkeit allein aus einem Katalogeintrag behaupten.

## 3. Wenige Handlungsbilder reichen als Heuristik

Nicht als Schema, nur als visuelle Denkhilfe:

**Sonde / Auge**
- lesen, suchen, prüfen, vergleichen

**Hand / Werkzeug**
- schreiben, editieren, umbauen

**Maschine**
- Prozess, Test, Dienst, Background-Arbeit

**Tor / Schlüssel / Plombe**
- Permission, Approval, Sandbox-/LIVE-Grenze, irreversible Handlung

**Bote / Übergabestück**
- Handoff, Proposal, Reviewauftrag, gerichtete Nachricht

Wenn diese fünf irgendwann nicht reichen: nicht automatisch Nummer sechs erfinden; zuerst konkrete Szene ansehen.

## 4. Handlung sitzt am betroffenen Material

Nicht jeder Zustand muss über dem Agenten schweben.

Beispiel Review:
- Werkstück am Prüfstand
- Reviewer dort angeschlossen
- Ergebnis/Beleg bleibt am Material, auch wenn Reviewer weggeht

Beispiel Approval:
- konkretes Änderungsstück wartet bei Daniel
- der Rest des Arbeitskörpers kann ggf. weiterarbeiten

## 5. Wartezustand braucht Grund **und Scope**

`waiting=true` ist zu grob.

Mögliche reale Gründe:
- human approval
- human input
- permission policy
- dependency
- anderer Strom
- Prozess
- Queue
- Review
- Retry/Backoff
- externe Welt

Wichtigste Regel:

> **Zeige zuerst das wartende Ding. Nur wenn dadurch wirklich die ganze Arbeit blockiert ist, wird auch der gesamte Arbeitskörper als wartend dargestellt.**

## 6. Arbeit kann den Akteur verlassen

Sichtbar eigenständig werden sollte Arbeit nur, wenn ihr Fortbestand relevant ist.

Gute Kandidaten:
- Background-Session
- längerer Prozess/Test
- laufender Dienstjob
- Approval/Handoff
- Review/Queue, wenn real belegt

Kein Weltobjekt für jeden kurzen Shellcall.

## 7. Parallelität ohne Klonarmee

Mehrere konkrete Instanzen desselben Stroms können gleichzeitig an verschiedenen Orten arbeiten.

Beispiel GPT:
- Wagen A an Haufen X
- Wagen B am Atlas
- Proposal von A bei Daniel
- gemeinsames Zuhause bleibt woanders

Das sind Arbeitskörper/Zustände, keine neuen Persönlichkeiten.

Fork/Worktree/Background/AFK dürfen ähnlich aussehen, bleiben aber technisch verschieden.

## 8. Eingriffstiefe darf sich körperlich unterscheiden

Ungefährer Machtverlauf:

`sehen → prüfen → Vorschlag → Sandbox → echte Quelle → Dienst/LIVE → irreversibel`

Nicht als sieben Levels manifestieren.

Nur die im aktuellen Ausschnitt vorkommenden Grenzen sichtbar machen.

Besonders tiefe Eingriffe sollten sich nicht genauso leicht anfühlen wie `read_file`.

## 9. MCP als Maschinenpark, nicht Toolmenü

Der reale MCP bündelt u. a.:
- History/Provenienz
- Dateisystem
- Dienste/Prozesse/Netz
- Git
- Assets/3D/Bild/Audio
- Agentensessions
- Container
- PostgreSQL
- Tests
- Zensi

Designimpuls:
- diese Fähigkeiten eher an Materialprüfständen, Maschinen, Cockpits oder Inspektionsgesten sichtbar machen
- nicht 120 Buttons/Schuppen erzeugen

## 10. Schemaexistenz ist keine Aktivität

Beispiel DB:
- `llm_warteschlange` kann existieren und leer sein
- `entity_wuensche` kann existieren und leer sein

Kein Förderband voller Phantomjobs rendern, nur weil eine Tabelle vorgesehen ist.

## Für erste Szenen reicht

Eine Szene muss nicht alle Agenten-/Toolzustände darstellen.

Genug ist:
- eine konkrete reale Handlung
- ein relevanter fortbestehender Arbeitskörper
- ein konkreter Wait/Gate, falls er wirklich vorkommt
- ein belegter Effekt

Alles Weitere erst nach Bedarf.