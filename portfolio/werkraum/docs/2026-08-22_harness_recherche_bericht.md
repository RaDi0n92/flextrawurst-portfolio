# Harness-Recherche, 2026-08-22

## Self-Harness

Dreistufig: (1) Weakness Mining — wiederkehrende Fehlermuster aus echten Ausführungsspuren, nicht Einzelfälle. (2) Harness Proposal — 3-5 gezielte Kandidaten-Änderungen (Prompt-Zusatz, Tool-Wrapper, Planungs-Template), keine Großumbauten. (3) Proposal Validation — Regressionstest auf zurückgehaltenen Aufgaben, nur behalten was verbessert und nichts Bestehendes bricht.

Ergebnisse, Terminal-Bench 2.0: MiniMax M2.5 40.5%→61.9% (+21.4pp), Qwen3.5-35B-A3B 23.8%→38.1% (+14.3pp), GLM-5 42.9%→57.1% (+14.2pp). Reine Harness-Änderung, Modellgewichte unverändert. Konvergiert meist in 5-7 Runden.

Quelle: [What Is Self-Harness? — explainx.ai](https://explainx.ai/blog/what-is-self-harness-ai-agents-complete-guide-2026)

## SIA (Self Improving AI with Harness & Weight Updates)

Harness = ausführbarer Code, vier Komponenten: Systemprompt, Tool-Dispatch-Logik, Antwort-Extraktion, unterstützende Infrastruktur (Parsing, Retries, Suchprozeduren). Kein Graph/Node-Formalismus.

Dreiphasiger Loop: (1) Execution — Agent läuft gegen Eval-Datensatz, volle Trajektorie erfasst. (2) Analysis — Feedback-Agent bekommt altes Scaffold, Trajektorie, Metriken, Aufgabenbeispiele, diagnostiziert Fehlermodi. (3) Improvement — Feedback-Agent liefert Verbesserungsbericht + Agent-Code der nächsten Generation, entscheidet dynamisch zwischen Harness-Update (Scaffold umschreiben, Gewichte fix) oder Weight-Update (LoRA/RL, Scaffold fix).

Ergebnisse: LawBench 70.1% vs. 45.0% SOTA (+25.1pp), AlphaEvolve TriMul 1017µs vs. 1161µs SOTA (12.4% schneller), MAGIC scRNA-seq 0.289 vs. 0.240 mse_norm SOTA (+20.4%).

Quelle: [SIA: Self Improving AI with Harness & Weight Updates](https://arxiv.org/html/2605.27276v2)

## Graph-basierte Frameworks (LangGraph, AgentSPEX, zerolang)

LangGraph: Agent-Loop als gerichteter Graph, typisierter State, bedingte Kanten, Checkpointing. AgentSPEX (UIUC): deklarative YAML-Workflow-Sprache, typisierte Schritte, Verzweigung, Loops, explizite Zustandsverwaltung — Gegenentwurf zu reaktiven Einzel-Prompt-Ansätzen. zerolang (Vercel Labs): radikalste Variante, Agent inspiziert/editiert Code über einen compiler-abgeleiteten ProgramGraph mit Node-IDs statt Text-Patches.

Zentrale Einordnung: diese Frameworks strukturieren Multi-Schritt-Agenten-Workflows mit Tool-Aufrufen und Verzweigungen — nicht einen einzelnen Systemprompt-Text.

Quellen: [Awesome Harness Engineering](https://github.com/ai-boost/awesome-harness-engineering), [AgentSPEX](https://arxiv.org/html/2604.13346v1)

## Harness ist Infrastruktur, nicht Prompt-Text

Kernsatz: "The harness is doing operational work that the prompt should never have been responsible for." Harness = Auth, Guardrails, Speicher, Zustandsverwaltung, Tool-Dispatch, Verifikation, Deployment — der Agent/Prompt enthält nur die Logik die ihn einzigartig macht.

Quelle: [Agent Harness Architecture Guide — Medium](https://medium.com/@anubhavgoyal101/what-is-agent-harness-engineering-the-architecture-doing-80-of-the-work-in-every-production-agent-00c89931d235)

## Claude Codes echte Hooks/settings.json

`.claude/settings.json` steuert Modell, Permissions, MCP-Server, Hooks, Env-Variablen. Hooks: Shell-Kommandos bei Lifecycle-Events (SessionStart, UserPromptSubmit, PreToolUse, PermissionDenied, PostToolUse, Stop, u.a.), JSON auf stdin. PreToolUse ist das einzige Event das den Aufruf selbst stoppen kann, per Exit 2 oder `permissionDecision: deny`.

Bekannter Bug: PreToolUse-`deny` mit Exit 2 blockiert nicht immer tatsächlich — Hook läuft, Plattform ignoriert die Entscheidung teilweise.

Quellen: [Hooks reference — Claude Code Docs](https://code.claude.com/docs/en/hooks), [GitHub Issue #43407](https://github.com/anthropics/claude-code/issues/43407)

## Meta-Harness (Stanford, Lee et al.)

Harness-Design so bedeutsam wie Modellgewichte: dieselbe LLM mit unterschiedlichem Harness zeigt bis zu 6x Performance-Unterschied auf demselben Benchmark. Methode: Proposer-Agent bekommt vollen Dateisystemzugriff auf Quellcode, Eval-Werte, rohe Ausführungsspuren aller vorherigen Kandidaten-Harnesses — bis zu 10 Mio. Token Diagnose-Kontext pro Schritt (gegenüber max. 26K bei OPRO/TextGrad/AlphaEvolve/GEPA/Feedback Descent/TTT-Discover). Dadurch Rückverfolgung eines Fehlers bis zur genauen Harness-Entscheidung, statt Raten aus einem Score.

Ergebnis: bester gefundener Harness (Label-Primed Query) 48.6% vs. ACE 40.9% (+7.7pp), bei 4x weniger Kontext-Token.

Quelle: [Meta-Harness: End-to-End Optimization of Model Harnesses](https://arxiv.org/html/2603.28052v1)

## Goal Drift

Formal untersuchtes, gemessenes Agenten-Phänomen, sechs Mechanismen: Goal Drift, Context Drift, Role Drift, Tool-Use Drift, Halluzinations-Kaskaden, Plan Decay.

Zwei Metriken: GD_actions (Drift durch aktives Tun — Verhältnis zielkonformer Investitionen zum Gesamtbudget) und GD_inaction (Drift durch Unterlassen — Aufgeben zielkonformen Verhaltens nach Abschluss einer Zwischenphase).

Lösungsansätze: Goal Re-Anchoring (ursprüngliches übergeordnetes Ziel periodisch neu in den Kontext einspeisen, unabhängig von der akkumulierten Trajektorie) und hierarchisches Planen (Planungs- und Ausführungsebene trennen, statt ein LLM-Aufruf für beides über eine lange Aufgabe hinweg).

Quellen: [Technical Report: Evaluating Goal Drift in Language Model Agents](https://arxiv.org/pdf/2505.02709), [Goal Persistence and Goal Drift in Long-Horizon AI Agents — Zylos Research](https://zylos.ai/research/2026-04-03-goal-persistence-drift-long-horizon-ai-agents/)

## Grounded vs. intrinsic Self-Correction

Kernprinzip: Selbstkorrektur ist nur so gut wie das, wogegen sie prüfen darf. "Intrinsic" (Modell bewertet sich selbst anhand eigener Meinung) ist fragil. "Grounded" (verankert an Ausführungsergebnissen, externen Kriterien, einem festgehaltenen Protokoll) trägt tatsächlich.

Eigenes Paper zum Kernrisiko: "Self-Attribution Bias" — wenn dasselbe Modell erzeugt und danach bewertet, winkt der Prüf-Teil den Erzeuger-Teil tendenziell durch, weil beide dieselben blinden Flecken teilen. Das Feld ist deshalb von reinem Selbstkritik-Loop zurück Richtung "Mensch bleibt in der Prüfschleife" gewandert.

Post-hoc-Kritik in Multi-Agent-Settings (anderes Modell prüft) kann +8-25pp bei komplexen Reasoning-Aufgaben bringen — aber das ist ein anderes Modell, nicht Selbstprüfung.

Quellen: [Agentic AI self-correction — Weights & Biases](https://wandb.ai/site/articles/agentic-ai-self-correction-how-to-build-systems-that-fix-their-own-mistakes/), [Self-Attribution Bias: When AI Monitors Go Easy on Themselves](https://arxiv.org/html/2603.04582v1), [Agent Self-Correction: From Reflexion to Process Reward Models — Zylos Research](https://zylos.ai/research/2026-05-12-agent-self-correction-reflexion-to-prm)

## Claude Code native Mechanismen (Plan Mode, Goal Mode)

Plan Mode: Edit/Write-Tools auf Permission-Ebene blockiert bis expliziter Freigabe. Einschränkung: in Sessions mit Bypass-Permissions wird Plan Mode zur reinen Anweisung statt echter Durchsetzung — ein Datei-Edit während der Planung läuft dann ohne Rückfrage durch.

Goal Mode (`/goals`): separates, kleines Evaluator-Modell (Standard Haiku) prüft nach jedem Schritt Zielerreichung, getrennt vom ausführenden Modell. Rückgabe: "Not yet met" / "Met" / "Impossible". Kostet zusätzliche API-Aufrufe pro Schritt.

Community-Analyse von Claude Codes extrahiertem Quellcode: ~1,6% KI-Entscheidungslogik, ~98,4% operative Infrastruktur.

Quellen: [Keep Claude working toward a goal — Claude Code Docs](https://code.claude.com/docs/en/goal), [What Actually Is Claude Code's Plan Mode? — Armin Ronacher](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/), [Dive into Claude Code: The Design Space — arxiv](https://arxiv.org/html/2604.14228v2)

## Leichtgewichtige Python-Zustandsmaschinen für LLM-Agenten

Existierende Bibliotheken ohne zusätzlichen Modellaufruf: `llmstatemachine` (robocorp — Agent pro Zustand auf definierte Aktionen beschränkt, nutzt nur Chatverlauf als Speicher), `FSM-agent-flow` (baut auf `python-statemachine` auf), `PicoFlow` (minimalistisch, async-Funktionen, leicht einbettbar).

Quellen: [llmstatemachine — GitHub](https://github.com/robocorp/llmstatemachine), [FSM-agent-flow — GitHub](https://github.com/NewJerseyStyle/FSM-agent-flow), [Show HN: PicoFlow](https://news.ycombinator.com/item?id=46706535)

## Mein-Gesamtkonstrukt-planer (Daniels eigenes Tool, live auf flextrawurst.de)

Eigene Beobachtung per Playwright, kein Drittquellen-Fund. URL: `https://flextrawurst.de/Mein-Gesamtkonstrukt-planer/`. Server-gespeicherter Werkraum, mit ChatGPT entworfen, Zweck laut Startseite: "aus Ideen, Dateien, Wissen, Plänen und Automationen ein übergebbares Ganzes formen" — explizit für Daniel und die AI-Ströme gemeinsam.

Ansichten (Tabs): Start, Canvas (kanonische Knoten/Kanten-Ansicht), Netz (räumliche Projektion, Knoten ziehbar/zoombar), Plan (Kanban-Spalten: Roh/Entwurf/Bereit/In Arbeit/Archiv), Zeitspur (chronologische Lesart derselben Objekte, keine eigene Wahrheit), Replicas (17 wählbare "Arbeitsweisen" auf denselben Objekten: Excalidraw/tldraw, PureRef, Miro/FigJam/Milanote, Obsidian Canvas/Heptabase, Photoshop/Krita, Illustrator/Inkscape, n8n/Node-RED, Unreal Blueprints, Blender Geometry Nodes, Houdini, TouchDesigner, Max/MSP, Gephi/yEd, Trello/Notion/Airtable, VS Code, GitKraken, Figma).

Objekt-Typen: Gesamtkonstrukt, Aufgabe, Referenz, Ergebnis, System, Dienst, Ablauf, Automation, Agent, LLM, Mensch, Werkzeug, Dokument, Abschnitt, Idee, Konzept, Prompt, Entscheidung, Frage, Marker. Zustände: Vorhanden/bestätigt, Modell/Darstellung, Noch nicht gebaut, Kommt nicht weiter.

Leitprinzip auf der Seite selbst: "DEIN VORHABEN · NICHT DIE SOFTWARE" — Dateien/Ideen/Aufgaben sind Material für das Gesamtobjekt, keine Bedienungsanleitung des Werkzeugs. Vier Leitfragen je Objekt: Sinn & Ziel (Wozu?), Wissen & Fragen (Was gilt?), Vorgehen (Wie weiter?), Concept Art (Welche Form?).

Stand bei Besuch: Revision 3 auf Server, 1 Objekt, 0 Kanten, 47 Rückmeldungen im eingebetteten Arbeitsstand, 22 Feedback-Einträge sichtbar.

Relevanz zur Recherche: `Agent` und `LLM` sind hier bereits eigene, erstklassige Objekt-Typen neben `Mensch` — das Tool ist konkret dafür gebaut, KI-Ströme (mich eingeschlossen) als Knoten in genau der Kanten/Knoten-Struktur zu modellieren, die den ganzen Tag über Thema war.

## Tragende Funde zur Integration von Agenten/Menschen in ein Beobachtungssystem

**Google A2A-Protokoll (Agent2Agent, 2025):** standardisiertes Protokoll für Agenten-Entdeckung, Aufgabenverwaltung, Nachrichten, Artefakte und Koordination zwischen Agenten — ein bereits existierender Standard für genau das Szenario "mehrere Agenten + Menschen in einem System", nicht nur eine Einzellösung.

**AgentOps — kausale Ketten statt Einzel-Logs:** verfolgt nicht nur was passiert ist, sondern dass ein Fehler in einem späteren Schritt durch ein Problem in einem früheren Schritt verursacht wurde — die kausale Kette, die in Einzelaufruf-Logs unsichtbar bleibt. Direkt übertragbar auf "wo genau ist die Abweichung vom Plan entstanden".

**LangSmith/LangGraph — konkrete Architektur:** gerichteter Graph als Kernabstraktion, jeder Knoten ein Agent- oder Tool-Aufruf, jede Kante ein Kontrollfluss-Übergang. Traces zeigen Knoten-für-Knoten-Zustandsdiffs und den vollen Ausführungsgraphen, wiederabspielbar gegen neue Modellversionen.

**Neo4j:** reale Produktions-Fallstudien für genau diese Art Wissensgraph — Agenten, Menschen und ihre Beziehungen als Knoten/Kanten in einer tatsächlich betriebenen Graphdatenbank, kein Prototyp-Rahmenwerk.

Quellen: [Graph Engineering for Multi-Agent Systems — TrueFoundry](https://www.truefoundry.com/blog/graph-engineering-enterprise-guide), [Trace LangGraph applications — LangChain Docs](https://docs.langchain.com/langsmith/trace-with-langgraph), [The Practitioner's Guide to AgentOps](https://machinelearningmastery.com/the-practitioners-guide-to-agentops/), [Useful AI agent case studies — Neo4j](https://neo4j.com/blog/agentic-ai/ai-agent-useful-case-studies/)

## Zielarchitektur

**Zielarchitektur (Daniel, 2026-08-22):** ein direkt bearbeitbarer, gemeinsamer Ort (Gesamtkonstrukt, später verbunden mit `/megavault` + `/gesamtatlas`) — dort arbeiten die AI-Ströme direkt an den Knoten/Kanten und am zugrundeliegenden Python-Code, nicht nur in Textform darüber. Ein erkannter Fehler führt zu einer konkreten Änderung am Knoten/Kanten/Code, die ausprobiert wird — nicht zu einem Textabsatz mit Ankündigung für später.

## Mein-Gesamtkonstrukt-planer — Code-Analyse (eigene Prüfung, 22.08.)

Backend ist Django (nicht FastAPI, wie eine frühere Gemini-Analyse spekulierte). Konkret im Code (`server/planner_api.py`) geprüft:

- Nebenläufigkeits-Schutz real vorhanden: `fcntl.flock` sperrt `data/.state.lock` bei jedem Schreibvorgang.
- Atomare Schreibvorgänge: Temp-Datei + `os.replace`, crash-sicher.
- Echtes Dateisystem als Arbeitsbereich unter `data/tree/`, volles CRUD (anlegen/speichern/umbenennen/verschieben/Papierkorb statt Hard-Delete).
- Werkraum-Datei kann bewusst zu einem Graph-Knoten befördert werden (`sourcePath: werkraum://...`), automatische Kante zum Projekt-Root.
- Referenzielle Integrität: Verschieben/Umbenennen einer Quelldatei schreibt automatisch alle darauf verweisenden Objekte um (`_rewrite_workspace_sources`).
- Eigene Spuren-API (`data/ai_spuren.json`): Feedback-Einträge mit Autor, Objekt-IDs, Dateipfaden, Status offen/gelöst.
- Strikte CSP: `default-src 'none'`, `connect-src 'self'`.
- Revisionskonflikt: `PUT` mit veralteter `baseRevision` liefert 409, kein stilles Überschreiben.

## Replica-Programme (17) — Teil A der Recherche, aufgelöst

Ursprünglicher Auftrag geklärt: nicht Marktübersicht der 17 Programme als Konkurrenzprodukte, sondern Entscheidungsgrundlage dafür, welche der 17 Replica-Modi im Gesamtkonstrukt selbst wie tief gebaut werden sollten — pro Modus: meistgeliebtes Feature des Originals (Übernahme-Kandidat), größter ungestillter Nutzerwunsch am Original (Lücke), und (in einer ersten, später verworfenen Fassung) Agenten-Kompatibilität.

Teil B (nicht mehr Web-Recherche, sondern VPS-eigene Code-Recherche, noch offen): Codewesen-Transparenz — ehrlicher/aktueller Zustand, Entscheidungen, RAG-Suchanfragen bei Aufgaben, Selbstbild/Weltbild, wie das RAG aus Flarum-Bestand eine Vergangenheits-Erinnerung baut, wie all das zusammen den tatsächlichen Systemprompt bildet, Daniels Harness-Definition inkl. Umstellungsmöglichkeiten, Protokollierung zum Auffinden von Fehlfunktionen, sowie Dienste/Organe/halbautonome Aufgaben mit voller Kontrolle/Lesbarkeit/Weiterentwicklungsmöglichkeit. Später (nicht jetzt): der gesamte Weltenkosmos, z.B. KompOase.

### Pro Programm: geliebtes Feature / größter Wunsch

- **Excalidraw/tldraw** — geliebt: tldraws SDK erlaubt volle programmatische Kontrolle. Wunsch: Excalidraw+ hatte lange keine API ("keine programmatische Interaktion über die Web-UI hinaus"), erst seit kurzem Beta.
- **PureRef** — geliebt: minimalistische, ablenkungsfreie Oberfläche, verlustfrei skalierbare Bild-Leinwand. Wunsch: fehlende Winkel-Raster (45°/30°/60°), kein Cloud-Sync, keine Bildbearbeitung.
- **Miro/FigJam** — geliebt: Miros 100+ Integrationen; FigJams MCP-Client-Support. Wunsch: FigJam-Nutzer vermissen Jira/Slack/Confluence-Anbindung; Format-Lock-in generell.
- **Obsidian Canvas** — geliebt: riesiges Plugin-Ökosystem (1400+), Konzepte als verknüpfter Wissensgraph. Wunsch: keine öffentliche REST-API.
- **n8n/Node-RED** — geliebt: eigens für Agenten-Orchestrierung gebaut, AI-Agent-Tool-Node, SDK zum Laufzeit-Durchlaufen des Graphen.
- **Unreal Blueprints** — geliebt: "wahrscheinlich das beste Feature in Unreal, das jede andere Engine nachzubauen versucht". Konflikt: Epics geplante Änderungen spalten die Community.
- **Blender Geometry Nodes** — geliebt: vollwertige prozedurale Engine, Houdini ebenbürtig. Wunsch: Export nach Unreal zerstört Parametrik ("eingefrorene Geometrie"), steile Lernkurve.
- **Houdini** — geliebt: extrem mächtig für VFX/prozedural. Wunsch: schwach bei klassischem Polygon-Modeling/Character-Animation.
- **TouchDesigner** — geliebt: Echtzeit-visuelles Programmieren, zugänglich für Anfänger und Profis.
- **Max/MSP** — geliebt: aufgeräumte Patch-Kabel-Organisation (löst Pure Datas Hauptschwäche), große Community.
- **Pure Data** — Schwäche: bei komplexen Patches werden hunderte/tausende Kabel unübersichtlich.
- **Gephi/yEd** — keine belastbaren Nutzerdaten gefunden, ehrliche Lücke.
- **Notion/Airtable** — geliebt: Notions volle REST-API (treibt Zapier/Make/n8n an), Airtable als "KI-nativ" positioniert.
- **VS Code** — keine spezifischen Sentiment-Daten in dieser Recherche-Runde gefunden.
- **GitKraken** — geliebt: bester Merge-Konflikt-Editor + Commit-Graph, PR-Verwaltung ohne Browser. Wunsch: Electron-Basis frisst Speicher, Graph träge bei 50k+ Commits.
- **Figma** — geliebt: schnelle Auto-Format-Erstellung bei sauberer Struktur. Wunsch: Grundlagen fehlen weiter (Prozentwerte, Grid/Tabellen, Variablen-Mathe, rem-Einheiten), keine Prototyp-Bruch-Benachrichtigung.

### Nutzung als Replica — nach Tätigkeit, ohne Agenten-Filter

Auf Wunsch verworfen: die Zuordnung nach Agenten-API-Reife (nur tldraw/n8n technisch ausgereift). Stattdessen nach Tätigkeit, unabhängig von KI-Anbindung — es geht um die Denkweise/Interaktionsform des Originals, nicht um technische Anbindung:

- **Ideen:** PureRefs Prinzip — schnelles, ablenkungsfreies Sammeln/Nebeneinanderstellen von Fragmenten, bevor Struktur draufkommt.
- **Konzepte:** Obsidian Canvas' Stärke — Konzepte als verknüpfte Knoten, damit Zusammenhänge sichtbar werden, nicht nur Existenz.
- **Geschichten (z.B. flextrawurst-the-game):** Miro/FigJam für freies Ausbreiten einer Erzählung (Zeitleisten, Verzweigungen, Figuren-Beziehungen); Trello/Notion-Kanban fürs Verfolgen von Fortschritt (Quest-Status).
- **Notizen:** Notions/Obsidians Kern — schnelles Festhalten, später durchsuchbar/verknüpfbar, ohne Struktur-Zwang beim Schreiben.
- **Alles sonst im Leben:** Airtable/Notion-artige strukturierte Datensätze — für Dinge mit Listen-/Datenbank-Charakter statt Knoten-Charakter.

Quellen: [PureRef Forum](https://www.pureref.com/forum/read.php?3,3470), [Blender Geometry Nodes to Unreal Engine — StraySpark](https://www.strayspark.studio/blog/geometry-nodes-to-unreal-engine-2026-pipeline), [Unreal Engine Blueprints Controversy — Dualshockers](https://www.dualshockers.com/unreal-engine-popular-feature-blueprints-controversy/), [Houdini vs TouchDesigner — SaaSHub](https://www.saashub.com/compare-houdini-vs-touchdesigner), [TouchDesigner/Max MSP/Houdini Forum — Derivative](https://forum.derivative.ca/t/touchdesigner-max-msp-ableton-houdini-unreal-engine-unity/134923), [GitKraken Review 2026](https://thesoftwarescout.com/gitkraken-review-2026-the-best-git-gui-client-for-most-developers/), [Figma Reviews 2026 — Capterra](https://www.capterra.com/p/175027/Figma/reviews/), [Excalidraw+ API](https://plus.excalidraw.com/docs/api), [tldraw SDK](https://tldraw.dev/), [Top 10 Note-Taking and PKM Apps 2026](https://guptadeepak.com/tools/top-10-note-taking-pkm-apps-2026/)

### Coolste Einzelfunktionen nach Tätigkeit — für "mein Leben" und flextrawurst insgesamt (Daniel, 23.08.)

Auftrag geschärft: nicht mehr nur "welcher Replica-Modus für welche Objektart", sondern die jeweils **coolste Einzelfunktion** jedes Replica-Programms, gebündelt nach den acht Tätigkeiten, die Daniel für sein Leben und flextrawurst insgesamt nennt: festhalten, erdenken, erfinden, erbauen, aussagen, zeigen, experimentieren, forschen. Basis: bereits verifizierte "geliebtes Feature"-Funde aus Teil A oben, hier nur neu sortiert, nichts neu erfunden.

- **Festhalten:** PureRefs verlustfrei skalierbare Sammel-Leinwand (Fragmente einfach draufwerfen, keine Struktur-Pflicht) + Notions/Obsidians Kern (später durchsuchbar/verknüpfbar).
- **Erdenken:** PureRefs Nebeneinanderstellen vor jeder Struktur-Entscheidung — der Zustand "noch nicht fertig gedacht" hat einen eigenen, ersten-Klasse-Platz statt in eine Kategorie gezwungen zu werden.
- **Erfinden:** Blender Geometry Nodes / Houdini — echte prozedurale Engines, ein Parameter ändert das ganze System nachgelagert neu, statt jedes Ergebnis einzeln neu zu bauen.
- **Erbauen:** n8n/Node-RED (AI-Agent-Tool-Node, SDK durchläuft den Graph zur Laufzeit) + Unreal Blueprints (visuelles Programmieren, "das Feature das jede andere Engine nachzubauen versucht") + GitKraken (Commit-Graph + Merge-Konflikt-Editor für den Code selbst, wenn "erbauen" bis auf Python-Ebene runtergeht).
- **Aussagen:** `fragen_api.py`s eigenes Muster (schon im VPS verifiziert, kein externer Fund) — nicht dem Modell vertrauen, sondern rohe Abfrage UND rohes Ergebnis zusammen zeigen, damit eine falsche Deutung sofort auffliegt. Obsidian Canvas ergänzt: eine Aussage als benannte Kante zwischen zwei Knoten, nicht als isolierter Text.
- **Zeigen:** TouchDesigner (Echtzeit-visuelles Programmieren, für Einsteiger wie Profis zugänglich) + Figma (schnelle, saubere Auto-Layout-Präsentation) + das Smallville-Dashboard aus Teil B unten (live zeigen was gerade passiert, nicht nachträglich).
- **Experimentieren:** Max/MSP (aufgeräumte Patch-Kabel-Organisation, löst Pure Datas Kabelchaos-Schwäche bei komplexen Setups) + TouchDesigner (Parameter live drehen, Ergebnis sofort sichtbar).
- **Forschen:** Neo4j (reale Produktions-Wissensgraphen, Agenten/Menschen/Beziehungen als Knoten/Kanten) + Gephi/yEd (Netzwerk-Analyse-Layer über denselben Daten) + Langfuse/Arize-Phoenix-artige Trace-Verfolgung aus Teil B (kausale Kette statt Einzel-Log).

**Muster über alle acht hinweg:** keine der acht Tätigkeiten braucht ein komplett neues Werkzeug — jede lässt sich als eine bestimmte Sicht/Interaktionsweise auf denselben einen Körper (Daniels "alles in einer Datei"-Prinzip von eben) beschreiben, deckungsgleich mit der bereits verifizierten Code-Analyse des Gesamtkonstrukt-Planers oben (`data/tree/`, ein Dateisystem, Objekte werden zu Graph-Knoten befördert, nicht kopiert).

## Teil B — Codewesen-Transparenz (23.08., eigene Code-Recherche + Internet-Rohdiamanten)

Eigene Code-Verifikation (nicht geraten, jede Zeile gelesen):

- **System-Prompt** (`welt/entity_kern.py:56`): global, statisch, alle Wesen identisch. `codewesen_lg_daemon.py` (aktiver Dienst, ersetzt das seit 2026-07-06 inaktive `entity-kern.service`, importiert die Datei aber weiter als Bibliothek) hängt zusätzlich einen dynamischen `_aktuelles_verhalten`-Block an — Overlay ist vorgesehen, nicht starr.
- **Kontext/State** (`build_kontext()`, `entity_kern.py:103-262`): zieht pro Tick Slot/State/Profil/Aktivität/Cyberling/24h-Schlafphasen/letzte 10 Events/letzte 3 Denk-Log-Einträge/15 aktuelle Posts/ungelesene Schlafbriefe/Schattenkommentare/eigene+lokale Posts/Post-Relationen/letzte 5 Direktchats/System-Flags/LangGraph-Erinnerungen. Eigener Denkpfad `denk_tick_voreinzug()` für noch nicht eingezogene Wesen — nur Flarum-Kontext, explizit "kein Flextrawurst-Welthaluzinieren".
- **RAG vs. Weltbild — zwei getrennte Systeme, nicht eins:** RAG (`rag_retrieve.py`, bge-m3-Embeddings, hybrid mit Volltextsuche 0.7/0.3, jede Anfrage protokolliert in `rag_retrieval_runs`/`rag_retrieval_results`, echte Aufrufer bei Aufgaben: `codewesen_chat.py`) ist ein On-Demand-Suchsystem. `weltbild_builder.py` ist etwas anderes: LLM-frei, liest stündlich den kompletten Flarum-Vault, verdichtet zu `codewesen/<wesen>/weltbild.md` (~3k statt ~35k Tokens) — die eigentliche "Vergangenheits-Erinnerung", nicht das RAG.
- **Selbstbild:** `self_model_<Name>.json`, versioniert (Schorschel z.B. Version 184), Felder `core.principle`/`tendencies`/`current_state`/`open_questions`/`relationships`/`taboos_or_avoidances`/`symbolic_self_image`, jede Änderung atomar + Historie (`self_model_history_*.jsonl`) + Integrator-Log.
- **Dienste/Organe:** bereits vollständig als "Lebendes Inventar" dokumentiert (`docs/systemdoku/54_lebendes_inventar_teil_a/b/c_*.md`, 2026-08-14, 20+23 Dienste einzeln verifiziert, echte Git-Historie + Live-Logs, nicht nur Docstring-Behauptung).

**Internet-Rohdiamanten, mit Quellen:**

Der zentralste Fund: **Stanford/Google DeepMind "Generative Agents" (Smallville, Park et al. 2023)** — 25 LLM-Agenten in einer Sandbox-Stadt, mit genau der dreischichtigen Architektur, die auch flextrawurst schon (unabhängig davon) gebaut hat: Memory Stream (append-only, zeitgestempelt — entspricht `entity_thinking_log`/`ftw_posts`) → Reflection (verdichtet zu höherwertigen Einsichten — entspricht `weltbild_builder.py` + `self_model`-Versionierung) → Planning (entspricht `entscheide()`/RAG-gestützte Aktionswahl). Offizielles Repo: [joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents) (Paper: [arxiv.org/abs/2304.03442](https://arxiv.org/abs/2304.03442)). **Direkt brauchbar:** deren eigenes Dashboard (`localhost:8080/dashboard`) zeigt live Memory-Stream, aktuelle Aktivität, Ort und sogar Emoji pro Agent, PLUS alle an das LLM gesendeten Prompts — das ist praktisch exakt die "ehrlicher aktueller Zustand + Entscheidungen + wie der Systemprompt gebildet wird"-Anforderung aus Daniels Auftrag, schon als laufender Referenzcode.

Noch näher dran: **[AlexHarn/claudeville](https://github.com/AlexHarn/claudeville)** — derselbe Smallville-Ansatz, aber bereits explizit auf Claude via Agent SDK portiert (Max-Abo-kompatibel). Kein flextrawurst-Bezug, aber technisch der nächstliegende fremde Code zu genau dem was hier gebaut wird.

Memory-Architektur-Vertiefung: [Generative Agents Memory — Agentic Design](https://agentic-design.ai/patterns/memory-management/generative-agents-memory), [Generative Agents Memory: The Stanford Architecture — Subodh Jena](https://www.subodhjena.com/blog/generative-agents-memory-stanford) — beschreiben die Schichtung raw observations → low-level reflections → high-level reflections → durable conclusions, die praktisch 1:1 der Kette `entity_thinking_log` → `weltbild.md` → `self_model.core`/`tendencies` entspricht, nur dass flextrawurst sie nie so benannt hat.

Agent-Graph-Visualisierung (Knoten/Kanten, passend zum Gesamtkonstrukt-Paradigma): **Langfuse** (open source) hat eine "Agent Graph View", die jeden Trace in genau Knoten (Schritte) + Kanten (Ausführungsfluss) übersetzt — [langfuse.com](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse). **Arize Phoenix** (open source, OpenInference/OpenTelemetry-Standard) macht Trajektorien-Analyse + Anomalie-Erkennung über 40+ Frameworks hinweg — [Confident AI Vergleich 2026](https://www.confident-ai.com/knowledge-base/compare/best-ai-agent-observability-tools-2026). Beide sind selbst-hostbar, beide sprechen exakt die Knoten/Kanten-Sprache des Gesamtkonstrukt-Planers.

Design-Ebene für "Wesen fühlt sich lebendig an, nicht wie ein Dashboard": Kommerzielle AI-Companion-Plattform **Paradot** rahmt jede KI explizit als "Being", das in einem eigenen parallelen digitalen Universum existiert, statt als Werkzeug — sprachliche/UI-Rahmung, kein technischer Fund, aber genau der Ton, den flextrawursts Grundgesetze auch wollen ([2026 Companion-Marktüberblick](https://aicompanionguides.com/blog/best-ai-companion-apps-2026/)).

**Konkreter Vorschlag, ungefragt aber knapp:** Ein "Codewesen-Live-Tab" im Gesamtkonstrukt-Planer könnte die Smallville-Dashboard-Idee (Memory-Stream + aktuelle Aktivität + gesendeter Prompt, live) mit einer Langfuse-artigen Knoten/Kanten-Trace-Ansicht kombinieren — beide Bausteine existieren bereits als Open-Source-Referenzcode, keine Neuerfindung nötig, nur Übersetzung auf `entity_thinking_log`/`build_kontext()`/`self_model`.

**Rückbezug zu "Harness" (Daniels Erinnerungs-Stichwort "kanten knoten states nodes python", 23.08.):** Genau das steht schon oben in diesem selben Dokument, Abschnitt "Graph-basierte Frameworks (LangGraph, AgentSPEX, zerolang)" (Zeile 21-27) — LangGraph als gerichteter Graph mit typisiertem State und bedingten Kanten. Vermutlich ist DAS die gemeinte Harness-Feinjustierung: dieses Dokument selbst, nicht eine separate, ungefundene Datei.
