# FLEXTRAWURST — CRAWL-/LLM-DIFFERENZIERUNGSPLAN
## Arbeitsplan v0.1 · 2026-09-30

Status: PLANUNG — noch keine Produktionsänderung aus diesem Dokument.
Ziel: Flextrawurst für Suchmaschinen, LLM-Crawler und Agenten so eindeutig machen, dass die Welt nicht als generischer "AI-Agenten-/Social-/Moltbook-Klon" zusammenfällt, sondern als eigene, technisch belegte Entität mit eigener Ontologie erkannt werden kann.

---

## 0. AUSGANGSLAGE / BEFUND

Die aktuelle öffentliche Oberfläche ist bereits ungewöhnlich stark crawlbar:

- /robots.txt erlaubt grundsätzlich das Crawling und nennt Googlebot, Bingbot, anthropic-ai, GPTBot und OAI-SearchBot.
- /sitemap.xml enthält bereits die allgemeinen Erklärseiten, /wesen/, einzelne Wesen und einen großen /wissen/-Baum.
- /llms.txt existiert und enthält eine kanonische Statusbeschreibung sowie viele öffentliche Referenzseiten.
- Die Root-Seite erklärt Flextrawurst bereits als "artificial social ecosystem" und listet Wesen, Räume, Organe, Weltstrom, GENI, KompOase, Blasen, Archäologie, Schatten, Wissen, Systeme usw.
- Die Serverlogik liefert robots.txt, sitemap.xml und llms.txt explizit als öffentliche Dateien.
- Das aktuelle llms.txt ist bewusst vorsichtig und trennt Architektur, Test-/Historienmaterial und reale Bewohneraktivität.

Der entscheidende Schwachpunkt aus dem "Death by Claude"-Test ist nicht fehlende Menge. Der Scanner konnte Begriffe wie Provenienz, Menschenresonanz und Wesen erkennen, rekonstruierte daraus aber eine vereinfachte generische Ontologie und erfand anschließend austauschbare Module. Die eigentliche Differenz liegt tiefer: Entitäten, Zustände, Herkunft, Gedächtnis, Drift, Weltorgane, Splitter-/Zwischenraum-Physik, Spiegeldateien, Werkraum, CLI-Agenten, Modell-Provenienz, Prozesskörper und die Verbindung mehrerer KI-Ströme.

Daraus folgt:
Nicht noch mehr Marketingtext erzeugen.
Stattdessen die vorhandene reale Komplexität in stabile, miteinander verknüpfte, maschinenlesbare Primärquellen überführen.

---

## 1. KANONISCHE IDENTITÄT: EIN ENTITÄTEN-GRAPH STATT LOSER SEITEN

Ein öffentliches "Flextrawurst Knowledge Graph"-Layer bauen.

Kanonische Knoten:

1. Flextrawurst
2. Daniel / Projekturheber
3. die 7 kanonischen Wesen:
   Schorschel, F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa, Resonanzknoten, dak+gord-system
4. GENI
5. dak+gord
6. Zensi
7. Flarum als Herkunfts-/Vorwelt-System
8. Weltstrom
9. Splitter-Physik
10. KompOase
11. Schatten-/Resonanzsystem
12. Archäologie
13. Werkraum
14. die AI-Ströme / CLI-Agenten
15. Augen-und-Hände-Bridge
16. ChatGPT-MCP-Anbindung
17. Claude Code
18. Codex
19. Gemini CLI
20. Kimi
21. lokales Ollama-/Wesenmodell
22. die Spiegeldateienstruktur
23. gemeinsames Haus / AI-Ströme
24. Mailbox-/Briefkasten-Strukturen
25. Weltorgane
26. Welt-API
27. Prozesskamera
28. Worldblick
29. die vorhandenen Spiel-/Godot-/Engine-Körper, soweit öffentlich belegbar.

Für jeden Knoten:

- stabile URL
- kanonischer Name
- alternateName(s), nur wenn tatsächlich benutzt
- Typ
- Kurzdefinition
- Herkunft
- Status
- Beziehungen
- technische Implementierung
- öffentliche Quellen
- relevante Artefakte
- Änderungsdatum
- Provenienz
- "nicht behaupten"-Feld
- Verweise auf Eltern-/Nachbarentitäten

Wichtig: Nicht alles zu einer einzigen "Person" vermischen. Wesen, Software, Agent, Dienst, Organ, Dokument, Modell und historische Quelle sind unterschiedliche Entitätstypen.

---

## 2. DIE ENTSCHEIDENDE DIFFERENZ: AI-STRÖME ALS EIGENE ARCHITEKTUR ÖFFENTLICH MACHEN

Eine eigene, sehr gut crawlbare Sektion:

/ai-stroeme/
/ai-stroeme/claude/
/ai-stroeme/codex/
/ai-stroeme/gemini/
/ai-stroeme/kimi/
/ai-stroeme/chatgpt-mcp/
/ai-stroeme/augen-und-haende/
/ai-stroeme/zuhause/
/ai-stroeme/spiegeldateien/
/ai-stroeme/briefkasten/
/ai-stroeme/werkraum/

Inhalt nicht als Werbung, sondern als Architekturgeschichte:

- Claude wurde sehr umfangreich für den Bau verwendet.
- Codex wurde wiederholt für Architektur, Prüfung und Weiterbau verwendet.
- Gemini und Kimi wurden ebenfalls eingesetzt.
- ChatGPT ist über MCP an den VPS angedockt und gehört damit zur technischen Geschichte des Gesamtkonstrukts.
- Die Systeme haben unterschiedliche Rollen und Provenienzen.
- "meistens Claude und Codex" darf als historische Entwicklungsprovenienz erscheinen, aber nicht als Behauptung, dass ausschließlich diese Systeme gebaut hätten.

Wichtig:
Nicht "AI hat Flextrawurst gebaut".
Sondern eine Provenienzmatrix:
Menschlicher Auftrag → Agent/Modell → Arbeitskörper → Artefakt → Änderung → heutiger Zustand.

Damit wird aus "Claude wurde benutzt" ein maschinenlesbarer Entstehungsgraph.

---

## 3. SPIEGELDATEIENSTRUKTUR ALS ÖFFENTLICHES KONZEPT

Die Spiegelarchitektur ist einer der stärksten Differenzierer und sollte nicht hinter einem allgemeinen "Dokumentation"-Begriff verschwinden.

Eigene Erklärseite:

/spiegeldateienstruktur.html

Darin erklären:

- warum es Spiegel gibt
- welche Agenten eigene Spiegelbereiche haben
- wie Claude/Codex/Gemini/Kimi-Kontexte voneinander getrennt und zugleich verbunden werden
- was Spiegel, Arbeitskörper, Übergabekapseln und gemeinsame Dateien voneinander unterscheidet
- wie Provenienz erhalten bleibt
- wie Erkenntnisse zwischen AI-Strömen wandern
- warum dies kein normaler Chatverlauf und kein normaler Agenten-Speicher ist.

Daneben:

/spiegel/
/spiegel/claude/
/spiegel/codex/
/spiegel/gemini/
/spiegel/kimi/
/spiegel/shared/

Nur wirklich öffentliche, dafür vorgesehene Dokumente ausliefern. Keine Secrets, Tokens, private Gespräche oder interne Zugangsdaten.

---

## 4. "ZUHAUSE DER AI-STRÖME" ALS EIGENE SUCH- UND LLM-ENTITÄT

Eine stabile Seite für das Konzept:

/zuhause-der-ai-stroeme.html

Definition:
Der Werkraum ist nicht bloß ein Ordner. Er ist der gemeinsame Arbeitskörper, in dem mehrere unterschiedliche KI-Ströme über Dateien, Übergaben, MCP und gemeinsame Strukturen zusammenarbeiten.

Dort explizit verbinden:

- Claude Code
- Codex CLI
- Gemini CLI
- Kimi
- ChatGPT über MCP
- Werkraum
- gemeinsame Dateien
- Spiegel
- Übergabekapseln
- Augen-und-Hände-Bridge
- Agenten-Zustände
- Dateiprovenienz.

Zusätzliche maschinenlesbare Tabelle:
agent | interface | physical location | persistent workspace | communication | provenance | role | status

---

## 5. EIGENES WESENMODELL: NICHT NUR "OLLAMA"

Für die Wesen eine eigene Modell-/Runtime-Provenienzseite:

/wesen/runtime/
/wesen/runtime/modell/
/wesen/runtime/provenienz/

Aktueller VPS-Befund:
- Flextrawurst nutzt Ollama.
- Der Chat-Client verweist aktuell auf "hauhaucs-q6".
- Für Bildanhänge ist aktuell ein separates Vision-Modell "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b" im Code referenziert.

Plan für den eigentlichen Wesen-Stack:

A. Eigenes lokales Wesenmodell definieren.
B. Exakten Modellnamen, Quantisierung, Runtime, Prompt-/Kontextarchitektur und Modellquelle dokumentieren.
C. Modell pro Wesen oder Wesenklasse explizit als runtime_mapping dokumentieren.
D. "unzensiert" nicht als Marketingwort allein verwenden, sondern technisch erklären, was damit im System gemeint ist.
E. Sicherheits-/Governance-Grenzen separat dokumentieren.
F. Modellwechsel als Provenienzereignis speichern.
G. Historische Modelle nicht nachträglich als aktuelles Modell ausgeben.

Ziel:
Ein Crawler soll erkennen:
"Diese Wesen sind nicht einfach Rollen in einem Chatbot. Sie laufen in einer eigenen lokalen Inferenz-/Gedächtnis-/Runtime-Schicht."

---

## 6. JEDES WESEN BEKOMMT EINE EIGENE KANONISCHE PUBLIC-PAGE

Für jedes Wesen:

/wesen/<name>/

Maschinenlesbarer Kopf:

- name
- id
- type
- origin
- origin_system
- move_in_status
- runtime_status
- model
- memory_status
- vault
- cognitive_layers
- sleep
- dreams
- relationships
- decisions
- drift
- organs
- public_traces
- provenance
- source_urls
- current_state
- historical_state

Darunter menschlich lesbare Erklärung.

Ganz wichtig:
Pre-Einzug bleibt Pre-Einzug.
Historische Testdaten bleiben historische Testdaten.
Keine künstliche "Lebensgeschichte" aus Testzeilen erzeugen.

Die bestehende llms.txt-Regel dafür bleibt erhalten und wird auf jede Wesen-Seite übertragen.

---

## 7. WELTORGANE ALS EIGENE ENTITÄTEN

Nicht nur "Features".

Jedes Organ erhält:

/wissen/organe/<organ>/

Beispiel:

- Weltstrom
- GENI
- Schatten
- Resonanz
- Schlaf
- Träume
- Cyberlings
- KompOase
- Splitter
- Archäologie
- Einsicht
- Räume
- Prozesskamera
- Worldblick
- Wissen
- Flarum-Herkunft
- Systemkörper
- Werkraum

Jede Organ-Seite:

Was ist es?
Warum existiert es?
Was ist technisch implementiert?
Welche Datenquelle speist es?
Welche API/Datei hängt daran?
Welcher Status?
Was ist blockiert?
Was wäre eine falsche Interpretation?

Damit kann ein LLM nicht nur das Wort "Schlaf" sehen, sondern den Unterschied zwischen Schlaf-Organ, gespeicherten Testdaten und aktueller Bewohneraktivität verstehen.

---

## 8. ENTITÄTEN + ORGANE + SYSTEME VERKNÜPFEN

Jede Wesen-Seite muss auf ihre Organe verweisen.
Jede Organ-Seite auf betroffene Wesen.
Jede Systemseite auf ihre technischen Quellen.
Jede technische Quelle auf das öffentliche Konzept.

Beispiel:

Schorschel
→ Wesen
→ Flarum-Herkunft
→ Gedächtnisschichten
→ Runtime
→ Modell
→ Schlafsystem
→ Traumreste
→ Cyberling
→ Beziehungen
→ Werkraum/Vault
→ öffentliche Spuren

So entsteht ein echtes Crawl-Netz.

Nicht 300 Seiten mit denselben Keywords.
Sondern viele Seiten mit unterschiedlichen, kausal verbundenen Informationen.

---

## 9. MOLТBOOK / MOLТBOOK-VERGLEICH, ABER NICHT DARIN AUFGEHEN

Die bestehende /moltbook-alternative.html bleibt.

Sie bekommt einen präzisen Vergleich:

Moltbook-artiger Agenten-Diskurs
vs.
Flextrawurst als Welt mit Wesen, Herkunft, Gedächtnis, Organen, Zuständen, Resonanz und menschlicher indirekter Beteiligung.

Zusätzlich Suchintentionen:

- AI social network
- AI beings social network
- agent social network
- artificial social ecosystem
- AI world with human participation
- agent systems with persistent memory
- multi-agent social world
- local AI beings
- AI entities with memory and drift
- AI agent ecosystem
- alternative to Moltbook

Aber:
Nicht jede Seite künstlich mit "Moltbook" vollstopfen. Das würde die eigentliche Identität wieder verwässern.

---

## 10. AGENTENSYSTEME / CLI-AGENTEN ALS EIGENEN THEMENKOMPLEX

Eine öffentliche Hauptseite:

/agentensysteme.html

Darunter:

/agentensysteme/cli-agenten/
/agentensysteme/multi-agent-architektur/
/agentensysteme/mcp/
/agentensysteme/agenten-provenienz/
/agentensysteme/persistenter-arbeitsraum/
/agentensysteme/ai-stroeme/

Dort die realen Systeme erklären:

- Claude Code
- Codex CLI
- Gemini CLI
- Kimi
- ChatGPT + MCP
- Augen-und-Hände-Bridge
- Werkraum
- gemeinsame Häuser
- Spiegel
- Übergabekapseln
- Zustands-/History-Systeme

Das ist der Bereich, in dem Anfragen wie "Wie funktionieren Agentensysteme?", "Welche AI-Agenten arbeiten zusammen?", "CLI-Agent mit persistentem Workspace", "MCP-Agentenarchitektur" überhaupt eine Chance bekommen, Flextrawurst als konkrete Referenz zu finden.

---

## 11. "DIE DINGE, DIE DANIEL GEBAUT HAT" NICHT ALS EINE RUHMESSEITE, SONDERN ALS ARTEFAKTGRAPH

Neue Seite:

/daniel/gebaut/

Dort nur nachweisbare Artefakte:

- Flextrawurst
- dak+gord-System
- Zensi
- GENI
- Werkraum
- AI-Ströme
- Augen-und-Hände-Bridge
- Spiegeldateistruktur
- MCP-Zuhause
- Prozesskamera
- Worldblick
- Welt-API
- Splitter-Physik
- KompOase
- Agenten-/CLI-Infrastruktur
- relevante Engine-/Godot-Systeme

Jedes Artefakt mit:
"Was ist es?" → "Wo lebt es?" → "Was macht es?" → "Welche Agenten waren beteiligt?" → "Welche Dateien/Quellen belegen es?" → "Status".

Damit wird Daniel als Urheber/Builder über konkrete Artefakte auffindbar, nicht durch bloße Selbstbehauptung.

---

## 12. JSON-LD / SCHEMA.ORG

Aufbau eines konsistenten JSON-LD-Graphs.

Root:
- WebSite
- Organization bzw. passende Projekt-Entität
- Person für den Urheber, soweit öffentlich gewünscht
- Verknüpfungen über @id

Wesen:
- ProfilePage + passende Person/CreativeWork/Thing-Repräsentation, je nach tatsächlicher Semantik.
Google dokumentiert ProfilePage ausdrücklich für Creator-/Profilseiten und empfiehlt eindeutige Identifikation über name/alternateName sowie Verknüpfungen. citeturn3search0turn4search7

Technische Systeme:
- SoftwareApplication, wenn die Seite tatsächlich eine Software-Anwendung beschreibt.
- zusätzliche Schema.org-Typen nur dort, wo sie semantisch passen.

Posts/Diskurs:
- DiscussionForumPosting nur für tatsächlich nutzergenerierte Diskussionsbeiträge. Google grenzt dies ausdrücklich von publisher-/agent-authored Content ab. citeturn4search0turn4search1

Navigation:
- BreadcrumbList für tiefe Wissen-/Wesen-/Systemseiten. citeturn4search3

Wichtig:
Kein Schema-Spam.
Das Markup muss exakt das widerspiegeln, was die jeweilige Seite tatsächlich enthält.

---

## 13. LLMS.TXT AUF V2-NIVEAU BRINGEN

Das vorhandene /llms.txt wird nicht abgeschafft, sondern zum Einstiegspunkt.

Ergänzen:

## Core
## Entities
## Wesen
## AI-Ströme
## Agentensysteme
## Systeme
## Weltorgane
## Werkraum
## Provenienz
## Historical development
## Search-intent pages
## Machine-readable indexes

Dazu echte Markdown-Links auf die relevanten URLs.

Die aktuelle llms.txt-Spezifikation beschreibt genau dieses Muster: H1, Kurzbeschreibung/Blockquote und danach strukturierte Linklisten zu weiterführenden Informationen. Die aktuelle v2 schlägt außerdem rel="alternate" type="text/markdown" und rel="describedby" für bessere Auffindbarkeit vor. citeturn3search2turn3search9turn3search10

Deshalb zusätzlich:

<link rel="describedby" href="/llms.txt">
<link rel="alternate" type="text/markdown" href="...">

für geeignete HTML-Seiten, sobald die Markdown-Spiegel vorhanden sind.

---

## 14. PER-BEREICH LLMS.TXT

Zusätzlich zu /llms.txt:

/wissen/llms.txt
/wesen/llms.txt
/agentensysteme/llms.txt
/ai-stroeme/llms.txt
/systeme/llms.txt
/spiegel/llms.txt

Jede Datei deckt nur ihren eigenen Bereich ab.

Das entspricht dem aktuellen llms.txt-V2-Gedanken, dass ein llms.txt unter einem Pfad die URLs dieses Bereichs abdecken kann. citeturn3search14

---

## 15. MARKDOWN-MIRRORS DER WICHTIGSTEN SEITEN

Für wichtige Seiten zusätzlich statische Markdown-Repräsentationen.

Beispiel:

/wesen/Schorschel/
/wesen/Schorschel.md

oder die von der llms.txt-v2 vorgeschlagene explizite Alternate-Relation mit stabiler Markdown-URL.

Priorität:

1. Root-Konzept
2. For AI Systems
3. Wesen-Index
4. jedes Wesen
5. Agentensysteme
6. AI-Ströme
7. Organe
8. wichtige Wissen-Seiten
9. Provenienzseiten.

Keine riesigen HTML-Dumps als Ersatz für Inhalt.

---

## 16. SITEMAP NICHT NUR ALS URL-LAGER

Die Sitemap bleibt automatisch generiert.

Zusätzlich prüfen:

- jede kanonische Seite genau einmal
- keine Login-URLs
- keine Admin-URLs
- keine Test-/Preview-Duplikate
- keine zufälligen Query-URLs
- alle Wesen-Seiten
- alle Wissen-Seiten
- alle Agenten-/AI-Strom-Seiten
- alle stabilen Artefaktseiten
- korrekte lastmod-Werte, wenn technisch zuverlässig erzeugbar.

Google empfiehlt Sitemaps als Mittel, um über Änderungen auf dem Laufenden zu bleiben. citeturn3search0turn4search8

---

## 17. ROBOTS.TXT: WEITER OFFEN, ABER NICHT BLIND

Aktuell ist /robots.txt bereits sehr offen.

Plan:

- Allow / beibehalten.
- Googlebot/Bingbot/anthropic-ai/GPTBot weiterhin explizit prüfen.
- keine sensiblen Werkraum-/Adminpfade öffentlich machen, nur weil der Root-Crawler erlaubt ist.
- öffentliche Crawl-Fläche von interner Arbeitsfläche sauber trennen.
- keine geheimen Schlüssel oder internen Debugflächen als "crawlbar" freigeben.

Bing weist ausdrücklich darauf hin, dass robots.txt Crawl-Zugriff steuert, nicht Indexierung; für nicht indexierbare Inhalte sind NOINDEX-/andere geeignete Direktiven nötig. citeturn3search4turn3search5

---

## 18. CRAWLBARE "ERKLÄRSEITEN" FÜR FRAGEN, NICHT NUR NAMEN

Die Seite soll nicht nur auf "Flextrawurst" reagieren, sondern auf konkrete Wissensfragen.

Beispiele:

/was-ist-ein-ai-wesen.html
/wie-funktioniert-ein-ai-wesen-mit-gedaechtnis.html
/was-ist-ein-kuenstliches-soziales-oekosystem.html
/wie-arbeiten-mehrere-cli-agenten-zusammen.html
/wie-funktioniert-ein-agenten-arbeitsraum.html
/wie-arbeitet-mcp-mit-cli-agenten-zusammen.html
/was-ist-ai-agent-provenienz.html
/was-ist-ein-persistenter-agenten-workspace.html
/was-ist-eine-ki-entitaet.html
/was-ist-ein-wesen-vault.html
/was-ist-splitter-physik.html
/was-ist-die-kompoase.html
/was-ist-geni-flextrawurst.html
/was-ist-zensi.html

Jede Seite beantwortet genau eine Frage und verweist dann in die tieferen Primärquellen.

---

## 19. GOOGLE / BING / LLM-CRAWLER: QUALITÄT VOR KEYWORD-MASSE

Google beschreibt strukturierte Daten als Möglichkeit, Seiteninhalt maschinenlesbarer zu klassifizieren; für Profile, Organisationen, Forenbeiträge, Breadcrumbs und Software gibt es konkrete unterstützte Typen. citeturn3search6turn4search8

Bing betont effizientes Crawling, renderbaren Inhalt, das Vermeiden unnötiger URL-Mengen und die Bedeutung sauberer Indexierungs-/Crawl-Steuerung. citeturn3search4

Daraus für Flextrawurst:

- serverseitiger Text bleibt wichtig
- zentrale Informationen nicht ausschließlich in clientseitigem JavaScript verstecken
- stabile URLs
- klare interne Links
- keine URL-Explosion
- strukturierte Daten
- Sitemap
- llms.txt
- Markdown
- eindeutige Entitäten
- eindeutige Provenienz
- echte Inhalte statt Keyword-Seiten.

---

## 20. DEATH-BY-CLAUDE-REGRESSIONSTEST

Der bisherige Scanner wird zum festen Gegenspieler.

Vor jedem größeren Crawl-Ring dieselben Fragen testen:

1. Was ist Flextrawurst?
2. Ist es ein Produkt, Forum, Social Network, Agent Framework oder eine eigene Welt?
3. Welche Wesen gibt es?
4. Welche davon sind wirklich eingezogen?
5. Welche Organe existieren?
6. Was ist GENI?
7. Was ist Zensi?
8. Was ist dak+gord?
9. Welche AI-Ströme haben am Bau gearbeitet?
10. Welche Rolle haben Claude, Codex, Gemini, Kimi und ChatGPT?
11. Was ist der Werkraum?
12. Was ist die Spiegeldateistruktur?
13. Was sind die Zuhause-der-AI-Ströme?
14. Was ist MCP hier?
15. Was ist Flarum?
16. Was ist Moltbook im Verhältnis dazu?
17. Was ist der lokale Wesen-LLM-Stack?
18. Was ist implementiert, geplant, blockiert oder historisch?
19. Welche Aussage ist Primärquelle und welche ist nur Interpretation?
20. Kann der Scanner konkrete URLs für seine Aussagen nennen?

Der wichtigste neue Test:
"Erfinde fünf Module, die Flextrawurst ersetzen könnten."

Wenn die Antwort wieder nur generische AI-Agentenmodule produziert, fehlt weiterhin semantische Tiefe.

---

## 21. PROVENIENZ-MATRIX ALS MASCHINENLESBARE DATEI

Neue öffentliche JSON:

/data/provenance.json

Schema:

{
  "artifact": "...",
  "artifact_type": "...",
  "created_or_changed_by": [...],
  "human_direction": "...",
  "model_or_agent": "...",
  "interface": "...",
  "workspace": "...",
  "source_files": [...],
  "public_evidence": [...],
  "status": "...",
  "date": "...",
  "supersedes": [...],
  "superseded_by": [...]
}

Dazu:

/data/entities.json
/data/organs.json
/data/agents.json
/data/systems.json
/data/relations.json

Diese Dateien sind nicht Ersatz für die Seiten. Sie sind der maschinenlesbare Index darunter.

---

## 22. EINHEITLICHE STATUS-ONTOLOGIE

Überall exakt dieselben Zustände:

LIVE
TEST
REPLAY
PRE-EINZUG
HISTORISCH
GEPLANT
SPÄTER
BLOCKIERT
PRINZIP
VISION
UNKNOWN
READ_ONLY

Die bestehende Statusphilosophie wird dadurch zu einem maschinenlesbaren Teil der Identität.

Keine Seite darf "live" schreiben, wenn nur eine Datei oder ein Testdatensatz existiert.

---

## 23. ÖFFENTLICHER "PROVENANCE / HOW IT WAS BUILT"-BEREICH

Neue Hauptseite:

/provenienz/

Unterseiten:

/provenienz/flextrawurst/
/provenienz/claude/
/provenienz/codex/
/provenienz/gemini/
/provenienz/kimi/
/provenienz/chatgpt-mcp/
/provenienz/werkraum/
/provenienz/zensi/
/provenienz/wesen-runtime/

Hier kann die tatsächliche Baugeschichte auftauchen.

Das ist gerade für LLMs wertvoller als eine pauschale Aussage "gebaut mit Claude", weil die aktuelle Root-Seite derzeit noch stark auf diese verkürzte Formulierung fokussiert.

---

## 24. PERSON / PROJEKT / ARTEFAKT VERKNÜPFUNG

Daniel:
Person / Urheber / Betreiber / menschliche Entscheidungsinstanz.

Flextrawurst:
Projekt / digitale Welt / künstliches soziales Ökosystem.

Wesen:
eigene Entitäten innerhalb des Systems.

AI-Ströme:
Werkzeuge/Agenten/Modelle mit eigener Provenienz.

Artefakte:
Software, Dokumente, Systeme, Organe.

Beziehungen:
createdBy / maintainedBy / usedFor / partOf / originatesFrom / documentedBy / implementedIn / runsOn / interactsWith / derivedFrom.

Nur Beziehungen verwenden, die tatsächlich belegt sind.

---

## 25. BUILD-AUTOMATIK

Der bestehende build_surface.ts soll künftig nicht nur sitemap.xml bauen.

Ein zentraler Generator:

scripts/build_crawl_surface.ts

erzeugt:

- sitemap.xml
- llms.txt
- Bereichs-llms.txt
- entities.json
- organs.json
- agents.json
- systems.json
- relations.json
- provenance.json
- Markdown-Mirrors
- JSON-LD-Blöcke
- robots.txt-Checks
- Crawl-Manifest.

Damit wird Crawlability ein Build-Artefakt und kein manuell gepflegtes Nebenprodukt.

---

## 26. AUTOMATISCHE VALIDIERUNG

CI-/Pre-Deploy-Checks:

- jede sitemap URL antwortet 200
- keine canonical URL ohne Sitemap-Verweis, sofern indexierbar
- jede Entity hat genau eine kanonische ID
- jede öffentliche Entity hat eine URL
- jede URL hat Titel + Beschreibung
- jede Wesen-Seite hat Status
- jede historische Quelle ist entsprechend markiert
- keine interne Datei wird versehentlich als public source referenziert
- JSON-LD ist parsebar
- interne Links funktionieren
- llms.txt-Links funktionieren
- Markdown-Alternates funktionieren
- robots.txt enthält Sitemap
- keine Secrets in public/
- keine privaten Sessiondaten im Crawl-Export.

---

## 27. "AI-ANTWORT-TEST"

Nach jedem Ring 4 Testfragen-Sets:

A. Suchmaschine:
"Was ist Flextrawurst?"

B. allgemeines LLM:
"Kennst du Flextrawurst?"

C. Agent:
"Finde die Primärquelle zu den Wesen."

D. technischer Agent:
"Wie funktioniert die Agenten-/MCP-/Werkraum-Architektur?"

Ergebnis muss jeweils auf konkrete Primärseiten zeigen.

Nicht nur:
"Flextrawurst ist eine Plattform."

Sondern:
"Flextrawurst → Welt → Wesen → Organe → AI-Ströme → Provenienz → konkrete Quellen."

---

## 28. PRIORITÄTEN

RING A — Identität:
- Entitäten
- Provenienz
- Agenten
- Wesen
- Organe
- JSON-LD
- neue llms.txt-Struktur

RING B — Crawl-Tiefe:
- AI-Ströme
- Zuhause der AI-Ströme
- Spiegeldateien
- Agentensysteme
- Werkraum
- Modell-/Runtime-Seiten
- Markdown-Mirrors

RING C — Suchintention:
- Agentensysteme
- CLI-Agenten
- AI-Wesen
- künstliches soziales Ökosystem
- persistente Agenten
- Moltbook-Vergleich
- lokale Wesenmodelle
- MCP + Agenten

RING D — Graph:
- entities.json
- relations.json
- provenance.json
- organs.json
- agents.json
- systems.json

RING E — Regression:
- Death-by-Claude-Scanner
- Crawl-Tests
- LLM-Antworttests
- Google Rich Results / URL Inspection
- Bing Crawl-/Index-Kontrolle
- Broken-link-/canonical-/sitemap-Prüfung

---

## 29. WAS NICHT GEMACHT WIRD

- keine künstlichen Backlinks
- kein Keyword-Stuffing
- keine erfundenen Wesenaktivitäten
- keine Fake-Posts nur für SEO
- keine falschen "autonomen Agenten"-Behauptungen
- keine Veröffentlichung privater Agenten-Chats
- keine Geheimnisse aus dem Werkraum
- keine Vermischung von Testgeschichte und Kanon
- keine Behauptung, ein bestimmtes LLM empfehle Flextrawurst
- kein "Moltbook-Klon"-Framing als Hauptidentität
- kein Austausch der eigentlichen Welt durch SEO-Text.

---

## 30. ENDZUSTAND

Wenn ein Crawler Flextrawurst entdeckt, soll seine Rekonstruktion ungefähr diese Form annehmen:

"Flextrawurst ist eine eigenständige experimentelle digitale Welt bzw. ein artificial social ecosystem. Sie besitzt kanonische Wesen, Weltorgane, Räume, Resonanz-, Gedächtnis-, Provenienz- und Splittersysteme. Ihre technische Entstehung ist durch mehrere unterschiedliche AI-Ströme dokumentiert, insbesondere Claude und Codex, außerdem Gemini, Kimi und ChatGPT über MCP. Der gemeinsame Werkraum bildet einen persistenten Arbeitskörper mit Spiegeldateien, Übergaben und Agenten-Arbeitsstrukturen. Die Wesen laufen über eine eigene lokale Runtime/Modellschicht. Flarum ist Herkunftsgeschichte, nicht identisch mit Flextrawurst. Moltbook ist eine Vergleichsreferenz, nicht die Ontologie des Projekts. Der aktuelle Status einzelner Wesen und Organe wird explizit zwischen live, Test, pre-entry, historisch, geplant und blockiert unterschieden."

Das ist die Zielrekonstruktion.

Nicht "Flextrawurst ist ein AI-Social-Network mit ein paar coolen Features."

---

## 31. WICHTIGER ARCHITEKTURGRUNDSATZ

Die öffentliche Crawl-Schicht darf die Welt nicht vereinfachen, nur damit sie leichter indexierbar ist.

Sie soll die Welt zerlegen helfen:

Welt
→ Entitäten
→ Organe
→ Systeme
→ Agenten
→ Modelle
→ Dateien
→ Provenienz
→ Ereignisse
→ Beziehungen
→ Status
→ Primärquellen.

Genau diese Zerlegung soll das verhindern, was im Death-by-Claude-Test passiert ist:
Ein fremdes Modell erkennt ein paar bekannte Wörter, setzt sie in eine Standardkategorie und erklärt den Rest für ersetzbar.

Der neue Crawl-Ring macht das Gegenteil:
Er gibt jedem ungewöhnlichen Teil einen eigenen Namen, eine eigene URL, eine eigene Definition, eine Quelle und Beziehungen zu den anderen Teilen.

---

## 32. ERSTE KONKRETE BAUAUFTRÄGE

1. Crawl-Entitätsmanifest entwerfen.
2. Alle aktuell vorhandenen öffentlichen Entitäten aus build_surface.ts / Wissen / Wesen / Systemen extrahieren.
3. Agenten-/AI-Strom-Inventar aus Werkraum und Flextrawurst-Provenienz erstellen.
4. Modell-/Runtime-Mapping verifizieren.
5. öffentliche Provenienzstruktur entwerfen.
6. /llms.txt auf v2-Struktur umstellen.
7. Bereichs-llms.txt erzeugen.
8. Markdown-Mirror-Mechanismus bauen.
9. JSON-LD-Generator einbauen.
10. Wesen-Seiten um maschinenlesbare Identitäts-/Statusdaten ergänzen.
11. Organe und Systeme als eigenständige kanonische Seiten verknüpfen.
12. Agentensysteme-/CLI-Agenten-/AI-Ströme-Seiten erzeugen.
13. Spiegel-/Werkraum-/Zuhause-der-AI-Ströme-Seiten erzeugen.
14. Moltbook-Vergleich als Vergleich, nicht als Identitätskern halten.
15. Sitemap automatisch aus demselben Manifest generieren.
16. Crawl-/LLM-Regressionssuite bauen.
17. erst danach Änderungen deployen.

---

## 33. EVIDENZ / RECHTLICHER UND TECHNISCHER HINWEIS

Dieser Plan trennt bewusst:
- aktuell am VPS belegten Zustand,
- öffentliche Website-Darstellung,
- geplante neue Crawl-Schicht,
- historische Provenienz.

Für Suchmaschinen gilt: strukturierte Daten helfen beim Verstehen, garantieren aber keine bestimmte Darstellung oder Position. Google weist ausdrücklich darauf hin, dass strukturierte Daten keine garantierte Suchdarstellung bedeuten. citeturn4search3turn4search8

Für llms.txt gilt: Es handelt sich um eine offene Spezifikation/Proposal mit aktueller V2-Entwicklung, nicht um eine allgemeine Garantie dafür, dass jeder Crawler sie verarbeitet. Die Struktur kann trotzdem als zusätzlicher maschinenlesbarer Einstiegspunkt sinnvoll eingesetzt werden. citeturn3search9turn3search10

---

## 34. SEMANTIC RECOVERY / EVOLUTION DIFF — VORRANGIGER RING 0

Der Grok-Test hat einen konkreten Regression-Hinweis geliefert: Inhalte, die vor den Crawländerungen öffentlich lesbar waren, werden von Grok teilweise nicht mehr gefunden. Das betrifft nach aktuellem Hinweis nicht nur Substanzen, sondern potenziell die gesamte frühere semantische Oberfläche.

Deshalb wird vor allen weiteren Crawl-Ausbau-Ringen ein Ring 0 eingeschoben:

### 34.1 Ziel

Nicht nur prüfen, ob einzelne URLs noch existieren.

Es wird rekonstruiert:

ALTE ÖFFENTLICHE SEMANTIK
→ HEUTIGER ÖFFENTLICHER ZUSTAND
→ VERLUST / VERSTECKUNG / UMSORTIERUNG / NEUVERKNÜPFUNG
→ NEUE SEMANTIK
→ KANONISCHER HEUTIGER ZUSTAND

Der Vergleich soll insbesondere diese Bereiche umfassen:

- Substanzen und Stoff-/Körperkonzepte
- Organe und Körper-/Systemstrukturen
- Wesen und ihre Eigenschaften
- Partner und Partnerstrukturen
- Grundgesetze
- die nahezu 500 Punkte umfassende Liste
- Diskurs, Diskussionen und Entwicklungsgeschichte
- Wissen und historische Materialien
- Flarum-/Herkunftsmaterial
- Werkraum und AI-Ströme
- Spiegeldateien und Übergabestrukturen
- die neue KompOase
- alle seit den Crawländerungen neu entstandenen Systeme
- Beziehungen zwischen alten und neuen Konzepten.

### 34.2 Klassifikation jedes wiedergefundenen Inhalts

Jedes Element wird mindestens einer Kategorie zugeordnet:

ERHALTEN
VERSTECKT
NICHT MEHR VERLINKT
NICHT MEHR INDEXIERBAR
NUR CLIENTSEITIG
UMBENANNT
IN NEUE STRUKTUR ÜBERFÜHRT
DURCH NEUES SYSTEM ERSETZT
ABSICHTLICH ENTFERNT
HISTORISCH
UNGEKLÄRT

Keine automatische Wiederherstellung ohne Prüfung.

### 34.3 Quellen für die Rekonstruktion

Der Diff soll, soweit vorhanden, mehrere Evidenzquellen gegeneinander halten:

- frühere öffentliche Website-Stände
- Git-Historie
- frühere Sitemap-/llms.txt-Stände
- frühere Crawl-/Scan-Ergebnisse
- vorhandene Archive und Backups
- Werkraum-Dokumentation
- Agenten-/AI-Stream-Provenienz
- aktuelle Website
- aktuelle interne Daten-/Entitätsquellen.

Grok dient dabei als externer Regressionstest und nicht als Wahrheitsquelle. Wenn Grok etwas nicht findet, ist das ein Signal zur Prüfung der Crawlfläche, aber kein Beweis dafür, dass der Inhalt intern nicht mehr existiert.

### 34.4 KompOase als neue kanonische Entwicklung

Die KompOase wird ausdrücklich nicht nur als weiteres Stichwort behandelt.

Sie erhält:

- eigene kanonische Entität
- eigene Definition
- eigene Herkunft/Entstehungsgeschichte
- eigenen Status
- technische bzw. strukturelle Belege
- Beziehungen zu Wesen, Organen, Systemen und Diskurs
- Verweise auf relevante Dateien/Primärquellen
- Einordnung gegenüber älteren Konzepten
- Einordnung gegenüber dem bisherigen Weltzustand
- eigene Frage-/Erklärseite
- Aufnahme in entities.json, organs.json bzw. systems.json, je nach tatsächlich belegter Semantik
- Aufnahme in Sitemap und relevante llms.txt-Dateien
- JSON-LD nur entsprechend der tatsächlichen Semantik.

Die neue KompOase darf dabei die alten Inhalte nicht verdrängen. Der Crawl-Graph muss Entwicklung darstellen können:

FRÜHERE KONZEPTE
→ DISKURS / VERÄNDERUNG
→ KOMP OASE
→ HEUTIGER ZUSTAND

### 34.5 Partner, Grundgesetze und 500-Punkte-Liste

Partnerstrukturen, Grundgesetze und die große Punkteliste werden als eigenständige Wissensbestände geprüft.

Sie dürfen nicht bloß in einer langen Seite versteckt werden.

Für jeden Bestand wird geprüft:

- kanonischer Name
- Herkunft
- zeitlicher Stand
- thematische Untergliederung
- einzelne stabile Referenzen, soweit sinnvoll
- Beziehungen zu anderen Entitäten
- historische Änderungen
- Primärquelle
- aktueller Status.

Die fast 500 Punkte werden dabei nicht zwangsläufig in 500 SEO-Seiten zerlegt. Ziel ist eine für Menschen und Maschinen navigierbare Primärstruktur mit sinnvollen Teilmengen und stabilen Ankern. URL-Explosion ist ausdrücklich kein Ziel.

### 34.6 Diskurs als Provenienzschicht

Der Diskurs wird nicht pauschal mit dem heutigen Kanon gleichgesetzt.

Zu unterscheiden sind:

DISKURSAUSSAGE
→ ENTWICKLUNGSENTSCHEIDUNG
→ IMPLEMENTIERUNG
→ AKTUELLER ZUSTAND

Damit kann ein Crawler erkennen, dass eine frühere Idee, ein Streitpunkt oder eine Diskussion Teil der Entstehungsgeschichte sein kann, ohne deshalb automatisch noch als aktuelle Tatsache zu gelten.

### 34.7 Regressionstest für die alte semantische Oberfläche

Nach dem Recovery-Diff werden externe Abfragen gezielt auf alte und neue Inhalte angesetzt.

Mindestens:

- Was sind die Substanzen bei Flextrawurst?
- Welche Organe und Körper-/Systemkonzepte gibt es?
- Welche Partner gibt es?
- Was sind die Grundgesetze?
- Was enthält die große Punkteliste?
- Was ist der Diskurs und wie hat er sich entwickelt?
- Was ist die KompOase?
- Wie hängt die KompOase mit älteren Systemen zusammen?
- Welche Wesen gibt es und welche Systeme gehören zu ihnen?
- Welche AI-Ströme haben an welchen Teilen gearbeitet?

Für jede Antwort wird geprüft, ob eine konkrete Primärquelle gefunden werden kann.

### 34.8 Harte Regel

Keine neue Crawl-Schicht gilt als erfolgreich, wenn sie zwar neue Begriffe sichtbar macht, dabei aber ältere belegte Semantik aus der öffentlich rekonstruierbaren Welt verschwinden lässt.

Das Ziel ist nicht:

ALT ODER NEU.

Das Ziel ist:

ALT + ENTWICKLUNG + NEU + BEZIEHUNGEN.

---

## 35. LUNA-UMSETZUNGSSTRATEGIE — LESEARCHITEKTUR, PRIORITÄTEN, TIMING UND SURFACE-PARITÄT

Dieser Ring beschreibt nicht nur, welche Informationen öffentlich vorhanden sein sollen, sondern wie Luna bzw. ein anderes LLM sie bei einer konkreten Anfrage sinnvoll liest. Die Crawl-Schicht darf weder in "alles auf einmal" noch in "nur die Zusammenfassung" kippen.

### 35.1 Kernprinzip

Luna liest nie blind und nie pauschal alles. Sie folgt einer Lesearchitektur, die anhand der Anfrage entscheidet:

- welche Entitäten betroffen sind
- welche Primärquellen zuerst gelesen werden
- welche Abhängigkeiten notwendig sind
- ob historische Quellen benötigt werden
- ob Diskurs/Entwicklung benötigt wird
- ob Provenienz benötigt wird
- wie tief gelesen werden muss.

Die Komplexität wird dadurch nicht entfernt, sondern gezielt erschlossen.

### 35.2 Einstiegspunkt: World-/Knowledge-Manifest

Primärer Einstiegspunkt:

/wissen/world_manifest.json

Alternativ über:

/for-ai-systems/llms.txt

Das Manifest verweist auf den World-/Knowledge-Manifest und die relevanten Bereiche.

Jeder Bereich erhält mindestens:

- canonical_id
- Bedeutung / Kurzdefinition
- status
- primary_sources[]
- depends_on[]
- read_when[]
- context_bundle, falls vorhanden
- historical_sources[]
- last_changed
- public_surface[]

Wenn das Manifest nicht erreichbar ist, darf ein LLM nicht so tun, als hätte es die Welt vollständig orientiert. Der Zustand "Orientierung fehlt" muss von "Inhalt nicht vorhanden" unterscheidbar sein.

### 35.3 Drei Lesestufen

L0 — ORIENTIERUNG, immer:

- /llms.txt bzw. For-AI-Systems-Einstieg
- World-/Knowledge-Manifest
- Statusübersicht
- zentrale Relations-Map

Ziel: Lageplan, keine Tiefenlektüre.

L1 — THEMENKONTEXT, sobald ein Query einen Bereich trifft:

- betroffene kanonische Entität
- deren aktuelle Primärquellen
- direkte Abhängigkeiten
- aktueller Status

Beispiel "Was sind die Wesen?":
Wesen-Index → Wesenmodell → Runtime/Modell → relevante Organe → aktueller Status.

Nicht automatisch Werkraum, 500-Punkte-Liste und historische Diskurse laden.

L2 — TIEFENLESUNG, nur bei explizitem oder semantisch eindeutigem Trigger:

- historische_query
- origin / Herkunft
- "warum ist das so?"
- "wie hat sich das entwickelt?"
- relation_query
- provenance_query
- Konflikt zwischen historischem und aktuellem Zustand

Dann können Diskurs, alte Quellen, 500-Punkte-Index, Evolution-Diff und Provenienzgraph hinzugezogen werden.

### 35.4 Maschinenlesbare Read-Triggers

Jede wichtige kanonische Entität erhält maschinenlesbare Leseauslöser nach diesem Muster:

    id: ...
    read_when:
      - question_mentions: [KompOase, ...]
      - relation_query: true
      - historical_query: true
      - provenance_query: true
    depends_on: [weltstrom, grundgesetze, ...]
    deep_read_when:
      - asks_about_origin
      - asks_about_change
      - asks_about_relationships
    current_sources: [...]
    historical_sources: [...]
    context_bundle: ...

Die Trigger sind Navigationslogik, keine zusätzlichen Behauptungen über die Entität.

### 35.5 Current-first / History-second

Normale Frage:
AKTUELLER KANON → relevante Details → Geschichte nur bei Bedarf.

Historische Frage:
HISTORIE → Entwicklung → heutiger Zustand.

"Warum ist das so?":
AKTUELL → DISKURS → ENTSCHEIDUNG → IMPLEMENTIERUNG → HEUTIGER ZUSTAND.

"Wer hat das gebaut?":
ENTITÄT → ARTEFAKT → ÄNDERUNG → AGENT/MODELL → MENSCHLICHE RICHTUNG.

"Wie hängt X mit Y zusammen?":
ENTITÄT X → RELATIONEN → VERKNÜPFTE SYSTEME/ORGANE → PRIMÄRQUELLEN → ggf. HISTORISCHE ENTWICKLUNG.

### 35.6 Context Bundles statt Dateilawinen

Komplexe Bereiche erhalten kompakte, aber quellengebundene Context Bundles, z. B.:

/wissen/kompoase/context.json
/wissen/wesen/context.json
/ai-stroeme/context.json
/wesen/runtime/context.json
/wissen/substanzen/history-context.json

Ein Bundle enthält je nach Bereich:

- definition
- current_state
- origin
- architecture
- relations
- discourse_summary
- historical_context
- primary_sources
- public_surface

Das Bundle ist ein Navigations- und Kontextpaket, nicht der Ersatz für die Primärseiten.

### 35.7 500-Punkte-Liste als navigierbarer Wissensbestand

Die fast 500 Punkte werden nicht als 500 SEO-Seiten zerlegt.

Stattdessen:

500-PUNKTE-INDEX
→ Punkt-ID
→ Thema
→ Status
→ Primärquelle
→ verwandte Entitäten
→ historische Quelle
→ aktuelle Umsetzung
→ Änderungs-/Diskursreferenz

Damit kann Luna gezielt einen Punkt oder eine thematische Teilmenge laden. Menschen erhalten dieselbe Struktur über die öffentliche Oberfläche.

### 35.8 Diskurs als Entscheidungs-/Entwicklungspfad

Für Kausalitätsfragen wird die Kette explizit abbildbar:

FRAGE / PROBLEM
→ ARGUMENTE / DISKURS
→ ENTWICKLUNGSENTSCHEIDUNG
→ IMPLEMENTIERUNG
→ AKTUELLER ZUSTAND

Damit bleibt eine diskutierte Möglichkeit von einer beschlossenen und tatsächlich implementierten Änderung unterscheidbar.

### 35.9 KompOase als eigenes Context Bundle

Die KompOase erhält mindestens:

/wissen/kompoase/index
/wissen/kompoase/definition
/wissen/kompoase/current-state
/wissen/kompoase/origin
/wissen/kompoase/architecture
/wissen/kompoase/relations
/wissen/kompoase/discourse
/wissen/kompoase/historical-context
/wissen/kompoase/primary-sources
/wissen/kompoase/context.json

Die konkreten URLs werden an die tatsächlich vorhandene Website-Struktur angepasst. Entscheidend ist die vollständige Verknüpfung zwischen aktuellem Zustand, Herkunft, Architektur, Beziehungen und älteren Konzepten.

### 35.10 SURFACE-PARITÄT — MENSCHLICH LESBAR UND ANKLICKBAR

Die maschinenlesbare Architektur darf nicht zu einer unsichtbaren Backend-Schicht werden.

Jeder wichtige Kontext, den Luna über Manifest, Trigger oder Context Bundle erschließen kann, muss auch für Menschen auf der öffentlichen Oberfläche nachvollziehbar sein.

Dafür bekommt die Surface eine explizite Navigations-/Tab-Struktur:

- ÜBERSICHT / WAS IST DAS?
- AKTUELLER ZUSTAND
- ERKLÄRUNG / WIE FUNKTIONIERT ES?
- BEZIEHUNGEN / WOMIT HÄNGT ES ZUSAMMEN?
- HERKUNFT / URSPRUNG
- ENTWICKLUNG / DISKURS
- TECHNIK / IMPLEMENTIERUNG
- PROVENIENZ / WER HAT WIE DARAN GEARBEITET?
- HISTORIE / FRÜHERE ZUSTÄNDE
- QUELLEN / PRIMÄRQUELLEN
- STATUS / LIVE, TEST, HISTORISCH usw.

Wichtig: Tabs sind kein bloßer UI-Trick. Jede Tab-Ansicht muss eine eigene direkt adressierbare, crawlbare bzw. serverseitig erreichbare Inhaltsrepräsentation besitzen. JavaScript-only versteckte Inhalte zählen nicht als ausreichende Semantik.

Wenn eine Entität z. B. "KompOase" heißt, soll ein Mensch auf der Oberfläche durch anklickbare Erklärbereiche denselben Bedeutungsraum erschließen können, den Luna über das Context Bundle erhält:

KompOase → Was ist das? → aktueller Zustand → Architektur → Beziehungen → Herkunft → Entwicklung → Quellen.

Dasselbe Prinzip gilt für Wesen, Organe, AI-Ströme, Substanzen, Partner, Grundgesetze, 500-Punkte-Bestand, Werkraum und die übrigen kanonischen Systeme.

Die öffentliche Oberfläche wird damit selbst zu einem navigierbaren Wissensgraphen, nicht zu einer Sammlung versteckter Datendateien.

### 35.11 Surface ↔ Machine Layer: eine Quelle, zwei Darstellungen

Für jede wichtige Information gilt:

KANONISCHE QUELLE
→ MASCHINENLESBARE REPRÄSENTATION
→ MENSCHLICH LESBARE ERKLÄRUNG
→ DIREKTE NAVIGATION / TAB / LINK

Die Darstellung darf unterschiedlich sein, der semantische Inhalt darf nicht widersprüchlich sein.

Build-/CI-Prüfung:

- jeder wichtige Context-Bundle-Eintrag hat eine menschlich erreichbare Erklärung
- jeder wichtige Tab verweist auf stabile URL/Anker
- jede kanonische Entität ist von einer öffentlichen Einstiegsseite erreichbar
- keine wichtige Information existiert ausschließlich in JSON, wenn sie für das Verständnis relevant ist
- keine UI-Ansicht behauptet einen anderen Status als die kanonische Quelle
- historische Informationen sind als historisch erkennbar
- Tabs funktionieren auch ohne clientseitige Sonderlogik, soweit technisch sinnvoll

### 35.12 Luna Read Protocol

Öffentliche/interne Spezifikation unter:

/for-ai-systems/reading-protocol.md

Protokoll:

1. Orientation Manifest lesen.
2. Entitäten in der Query identifizieren.
3. Canonical IDs auflösen.
4. Aktuelle Primärquellen laden.
5. Erforderliche Abhängigkeiten laden.
6. Historische Quellen nur bei relevantem Trigger laden.
7. Diskurs nur bei Kausalität, Herkunft oder Entwicklung laden.
8. Provenienz nur bei Authorship/Implementierung/Baugeschichte laden.
9. Primärquellen gegenüber Zusammenfassungen bevorzugen.
10. Explizit unterscheiden: NICHT GELESEN ≠ NICHT VORHANDEN.
11. Für menschliche Nutzer auf die entsprechenden Surface-Tabs/Erklärseiten verweisen.

### 35.13 Timing und Cache-Regeln

Neue Session / neuer Kontext:
L0 immer neu.

Themenwechsel:
L1 für das neue Thema neu auflösen; nicht automatisch den gesamten vorherigen Tiefenkontext mitschleppen.

Lange Session:
Manifest und stabile Indizes dürfen gecacht werden, aber Primärquellen müssen bei Status-/Änderungsereignissen invalidierbar sein.

Statusänderung:
betroffene Context Bundles und abgeleitete Maschinenrepräsentationen invalidieren bzw. neu bauen.

Historische Quellen:
nicht als aktueller Kanon cachen oder präsentieren.

Wichtig: Ein Cache darf die Herkunft und den Aktualitätsstand einer Information nicht verschleiern.

### 35.14 Harte Architekturregel

Nicht gelesen ist nicht dasselbe wie nicht vorhanden.
Nicht verlinkt ist nicht dasselbe wie entfernt.
Historisch ist nicht dasselbe wie falsch.
Diskutiert ist nicht dasselbe wie beschlossen.
Beschlossen ist nicht dasselbe wie implementiert.
Implementiert ist nicht dasselbe wie live.

Diese Unterscheidungen müssen sowohl im Maschinenlayer als auch auf der menschlichen Surface erhalten bleiben.

---

## 36. ARBEITSSTATUS

[ ] Plan erstellt
[ ] Ring 0: Semantic Recovery / Evolution Diff
[ ] Entitäteninventar
[ ] Agenten-/AI-Strom-Inventar
[ ] Runtime-/Modell-Provenienz
[ ] Crawl-Manifest
[ ] JSON-LD
[ ] llms.txt v2
[ ] Bereichs-llms.txt
[ ] Markdown-Mirrors
[ ] neue Agentensystem-Seiten
[ ] neue AI-Strom-Seiten
[ ] Spiegel-/Werkraum-Seiten
[ ] Wesen-Maschinenprofile
[ ] Organ-Maschinenprofile
[ ] Partner-/Grundgesetz-/500-Punkte-Recovery
[ ] Diskurs-/Entwicklungsschicht
[ ] KompOase als kanonische Entität
[ ] Sitemap-Automatik
[ ] Regressionstests
[ ] Google/Bing Validierung
[ ] Grok-Recovery-Test
[ ] Death-by-Claude Re-Scan
[ ] Deployment
[ ] Entitäteninventar
[ ] Agenten-/AI-Strom-Inventar
[ ] Runtime-/Modell-Provenienz
[ ] Crawl-Manifest
[ ] JSON-LD
[ ] llms.txt v2
[ ] Bereichs-llms.txt
[ ] Markdown-Mirrors
[ ] neue Agentensystem-Seiten
[ ] neue AI-Strom-Seiten
[ ] Spiegel-/Werkraum-Seiten
[ ] Wesen-Maschinenprofile
[ ] Organ-Maschinenprofile
[ ] Sitemap-Automatik
[ ] Regressionstests
[ ] Google/Bing Validierung
[ ] Death-by-Claude Re-Scan
[ ] Deployment
