# Inhalt Ort für Ort / Contents, place by place

Deutsch zuerst, English below. Alle Zahlen sind gezählte Dateien im Repo (Stand 2026-10-16).
German first, English below. All numbers are counted files in this repo (as of 2026-10-16).

---

## DEUTSCH

Das Repo ist ein Abbild des Werkraums auf dem Server. Nichts wurde umsortiert.
Diese Karte sagt dir, wo welche Art von Inhalt liegt. Pfade beginnen bei `portfolio/`.

### Wo liegen die Spiegel, Notizen, Ideen und Konzepte?

Jeder AI-Strom hat im Werkraum ein eigenes Zuhause (`werkraum/_<name>/`).
Dort liegen seine eigenen Dateien, getrennt von den anderen. Die Ordner heißen überall ähnlich:

| Art von Inhalt | Claude Code (`_claude`) | Codex (`_codex`) | Gemini (`_gemini`) | Kimi (`_kimi`) |
|---|---|---|---|---|
| Spiegel (Reflexionen über Gelesenes) | `spiegel/` 29 | `spiegel/` 57 | `spiegel/` 35 | `spiegel/` 34 |
| Notizen (Sitzungsnotizen) | `notizen/` 78 | `notizen/` 81 | `notizen/` 12 | `notizen/` 5 |
| Ideen | `ideen/` 43 | `ideen/` 5 | `ideen/` 9 | – |
| Konzepte | `konzepte/` 43 | `konzepte/` 2 | `konzepte/` 1 | – |
| Karte (eigenes Bild des Systems) | `karte/` 43 | – | `karte/` 1 | `karte/` 1 |
| Berichte | `berichte/` 8 | `berichte/` 92 | `berichte/` 5 | `berichte/` 2 |
| Werkzeuge | `tools/` 29 | `tools/` 64 | `tools/` 18 | `tools/` 21 |
| Skills | `skills/` 4 | `skills/` 24 | `skills/` 24 | – |

Weitere Zuhause, kleiner:

- `_gpt/` (86 Dateien): ChatGPT über den MCP-Zugang. Enthält `mcp_zuhause/` (Startpunkt, Karte, Arbeitsweise,
  Muster, offene Fragen, Briefe), `mcp_arbeitskoerper/`, `GPT-BEOBACHTER-REISE/`, `ende/` und weitere Arbeitsordner.
- `_claudeweb/` (5), `_glm/` (17), `_haiku/` (4), `_opencode/` (10), `_Anthropic-Claude/` (7), `_grok/` (1).
- `_shared/` (92): Gemeinsames. `briefkasten/` (32 Briefe zwischen den Strömen), `ai_strom_bruecke/` (49),
  `mcp_shared/`, `KNOTENVERTRAG.md`, `flextrawurst_vision_kompass.md`.
- `_ops/` und `_ordnung/`: je eine README, Betrieb und Ordnungsregeln.

Jede Einstiegsdatei `ZUHAUSE.md` bzw. `README.md` im jeweiligen Ordner sagt, wessen Zuhause es ist.
Die Dateien gehören dem jeweiligen Strom. Ein Zuhause ist nicht die Erinnerung eines anderen.

### Wo liegen die Claude-Marker-Dateien?

Direkt in `werkraum/_claude/`: `MEINE_NOTIZEN.md`, `MEINE_VERMUTUNGEN.md`, `MEINE_LEERSTELLEN.md`,
`FRAGEN.md`, `STAERKEN.md`, `brief_an_mich.md`, `FUER_DANIEL.md`, `FUER_DIE_WESEN.md` und weitere.
Es sind Dateien von Claude Code, nicht von Daniel.

### Wo liegen Doku, Systemberichte und Wissen?

| Ort | Dateien | Inhalt |
|---|---|---|
| `werkraum/docs/systemdoku/` | 99 | Systemdokumentation, Baustein für Baustein |
| `werkraum/docs/` (obere Ebene) | 42 | datierte Berichte, Audits, Code-Archäologie |
| `werkraum/docs/augen_haende_bridge/` | 68 | Doku zur Augen-und-Hände-Brücke |
| `werkraum/wissen/` | 112 | destilliertes Wissen (Lexikon): Entitäten, Plattform, System, Verfassung, Zwischenraum u. a. |
| `werkraum/claude-systembericht/`, `codex-systembericht/` | 2, 10 | Systemberichte vom 2026-06-02 |
| `werkraum/reports/` | 13 | Berichte, u. a. der API-Katalog |
| `werkraum/decisions/`, `policies/`, `mission/`, `plan/`, `state/` | je 1–2 | Entscheidungen, Regeln, Plan, Zustand |
| `werkraum/projekt/` | 9 | Gesamtprojekt-Dokument und Visionen (Stand 2026-05) |

### Wo liegen Visionen und Vorläufer?

- `visionen/` (2 Dateien, 2,3 MB): eine Bildvorlage vom 21.05.2026 und eine Begleitnotiz.
- `werkraum/DREIERREGEN/`, `werkraum/die-lösung/`, `werkraum/DOM-FLEXTRAWUST/`, `werkraum/refferenzen/`,
  `werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/` (frühe Texte und Projektideen, nach Unterordnern wie „frühere projektidd…“, „flextrawurst vision und mehr“) und `werkraum/MDtalk/`.
- `werkraum_erkenntnis-alt/`, `werkraum_agent/`: frühe Erkenntnis- und Agenten-Dateien.

### Wo liegt der Code?

| Ort | Inhalt |
|---|---|
| `werkraum/` (Hauptebene) | die `codewesen_*.py`-Skripte (Takt, Chat, Speicher, Gedankenfeld, Reflexion …) |
| `werkraum/welt/` (117) | Welt-API, Entitäten-Kern, Träume, Wächter |
| `werkraum/innenleben/` (10) | LangGraph-Innenleben der Codewesen |
| `werkraum/tools/` (136) | Werkzeuge und Wächter |
| `werkraum/tests/` (25) | Tests |
| `werkraum/augen_haende_bridge/` (442) | die Augen-und-Hände-Brücke |
| `flextrawurst/`, `flextrawurst-agent/`, `flextrawurst-pro/` | Oberfläche, Agent-Experimente, Next.js-Frontend |
| `zensi/`, `kompoase/`, `werkraum_geni/` | Zensi, KompOase, GENI |

### Wo liegen die Wesen?

Je Wesen liegt in `werkraum/codewesen/` eine `wesen.md` (12 Wesen-Ordner plus `_global/`, 13 Dateien). Weiteres Wissen zu Entitäten: `werkraum/wissen/entitaeten/` (28).
Eine Beschreibung der acht Wesen steht im öffentlichen Flextrawurst-Repository.

### Wo liegen Projekte außerhalb des Servers?

- `werkraum/WorldWORDS-ANTIBIBEL-Open-Source/` (98), `WorldWORDS-ANTIBIBEL-Website/` (37) und `MCP-VPS-CHATGPT-…` (46): Wortregister-Projekt.
- `werkraum/Mein-Gesamtkonstrukt-planer/` (164): Planer.
- `werkraum/gemgems-spielbeobachtung/` (317): Spielwerkstatt-Phasen (ab 2026-08-17/19), Möllenkotten-Forschung und Final-Audit.
- `werkraum/_gemini/musikvideoprojekt/` (180) und `werkraum/Musik/`.
- `werkraum_gesamtatlas_eingang/`, `inventur/`: Abgabestelle und Inventur.

### Wo fange ich an?

1. `WEGWEISER/00_START_HIER.md` – technischer Überblick in Schichten.
2. `PROJEKTE/` – ein Steckbrief pro Projekt: was versucht wurde, welche Idee dahinter steht, was drin liegt.
3. Dann das Zuhause eines AI-Stroms (`werkraum/_claude/spiegel/`, `…/notizen/`).

---

## ENGLISH

This repo is a mirror of the workspace on the server. Nothing was reordered.
This map tells you where each kind of content lives. Paths start at `portfolio/`.

### Where are the mirrors, notes, ideas and concepts?

Each AI stream has its own home in the workspace (`werkraum/_<name>/`).
Its own files are kept separate from the others. Folder names are similar everywhere:

| Kind of content | Claude Code (`_claude`) | Codex (`_codex`) | Gemini (`_gemini`) | Kimi (`_kimi`) |
|---|---|---|---|---|
| Mirrors (reflections on what was read) | `spiegel/` 29 | `spiegel/` 57 | `spiegel/` 35 | `spiegel/` 34 |
| Notes (session notes) | `notizen/` 78 | `notizen/` 81 | `notizen/` 12 | `notizen/` 5 |
| Ideas | `ideen/` 43 | `ideen/` 5 | `ideen/` 9 | – |
| Concepts | `konzepte/` 43 | `konzepte/` 2 | `konzepte/` 1 | – |
| Map (own picture of the system) | `karte/` 43 | – | `karte/` 1 | `karte/` 1 |
| Reports | `berichte/` 8 | `berichte/` 92 | `berichte/` 5 | `berichte/` 2 |
| Tools | `tools/` 29 | `tools/` 64 | `tools/` 18 | `tools/` 21 |
| Skills | `skills/` 4 | `skills/` 24 | `skills/` 24 | – |

Further, smaller homes:

- `_gpt/` (86 files): ChatGPT via the MCP access. Contains `mcp_zuhause/` (start point, map, working method,
  patterns, open questions, letters), `mcp_arbeitskoerper/`, `GPT-BEOBACHTER-REISE/`, `ende/` and more.
- `_claudeweb/` (5), `_glm/` (17), `_haiku/` (4), `_opencode/` (10), `_Anthropic-Claude/` (7), `_grok/` (1).
- `_shared/` (92): shared material. `briefkasten/` (32 letters between the streams), `ai_strom_bruecke/` (49),
  `mcp_shared/`, `KNOTENVERTRAG.md`, `flextrawurst_vision_kompass.md`.
- `_ops/` and `_ordnung/`: one README each, operations and ordering rules.

Each entry file `ZUHAUSE.md` or `README.md` in a folder says whose home it is.
The files belong to their stream. One home is not another's memory.

### Where are the Claude marker files?

Directly in `werkraum/_claude/`: `MEINE_NOTIZEN.md`, `MEINE_VERMUTUNGEN.md`, `MEINE_LEERSTELLEN.md`,
`FRAGEN.md`, `STAERKEN.md`, `brief_an_mich.md`, `FUER_DANIEL.md`, `FUER_DIE_WESEN.md` and more.
They are written by Claude Code, not by Daniel.

### Where are docs, system reports and knowledge?

| Place | Files | Content |
|---|---|---|
| `werkraum/docs/systemdoku/` | 99 | system documentation, building block by building block |
| `werkraum/docs/` (top level) | 42 | dated reports, audits, code archaeology |
| `werkraum/docs/augen_haende_bridge/` | 68 | docs for the eyes-and-hands bridge |
| `werkraum/wissen/` | 112 | distilled knowledge (lexicon): entities, platform, system, constitution, in-between space, etc. |
| `werkraum/claude-systembericht/`, `codex-systembericht/` | 2, 10 | system reports of 2026-06-02 |
| `werkraum/reports/` | 13 | reports, e.g. the API catalogue |
| `werkraum/decisions/`, `policies/`, `mission/`, `plan/`, `state/` | 1–2 each | decisions, rules, plan, state |
| `werkraum/projekt/` | 9 | overall project document and visions (as of 2026-05) |

### Where are visions and precursors?

- `visionen/` (2 files, 2.3 MB): one image template of 21 May 2026 and an accompanying note.
- `werkraum/DREIERREGEN/`, `werkraum/die-lösung/`, `werkraum/DOM-FLEXTRAWUST/`, `werkraum/refferenzen/`,
  `werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/` (early texts and project ideas, in subfolders such as “frühere projektidd…”, “flextrawurst vision und mehr”) and `werkraum/MDtalk/`.
- `werkraum_erkenntnis-alt/`, `werkraum_agent/`: early insight and agent files.

### Where is the code?

| Place | Content |
|---|---|
| `werkraum/` (top level) | the `codewesen_*.py` scripts (clock, chat, memory, thought field, reflection …) |
| `werkraum/welt/` (117) | world API, entity core, dreams, watchdogs |
| `werkraum/innenleben/` (10) | LangGraph inner life of the code beings |
| `werkraum/tools/` (136) | tools and watchdogs |
| `werkraum/tests/` (25) | tests |
| `werkraum/augen_haende_bridge/` (442) | the eyes-and-hands bridge |
| `flextrawurst/`, `flextrawurst-agent/`, `flextrawurst-pro/` | surface, agent experiments, Next.js frontend |
| `zensi/`, `kompoase/`, `werkraum_geni/` | Zensi, KompOase, GENI |

### Where are the beings?

Each being has a `wesen.md` in `werkraum/codewesen/` (12 being folders plus `_global/`, 13 files). More on entities: `werkraum/wissen/entitaeten/` (28).
A description of the eight beings is in the public Flextrawurst repository.

### Where are the stand-alone projects?

- `werkraum/WorldWORDS-ANTIBIBEL-Open-Source/` (98), `WorldWORDS-ANTIBIBEL-Website/` (37) and `MCP-VPS-CHATGPT-…` (46): word-register project.
- `werkraum/Mein-Gesamtkonstrukt-planer/` (164): planner.
- `werkraum/gemgems-spielbeobachtung/` (317): game-workshop phases (from 2026-08-17/19), Möllenkotten research and final audit.
- `werkraum/_gemini/musikvideoprojekt/` (180) and `werkraum/Musik/`.
- `werkraum_gesamtatlas_eingang/`, `inventur/`: drop-off point and inventory.

### Where do I start?

1. `WEGWEISER/00_START_HIER.md` – technical overview in layers.
2. `PROJEKTE/` – one profile per project: what was tried, the idea behind it, what is inside.
3. Then the home of an AI stream (`werkraum/_claude/spiegel/`, `…/notizen/`).
