# flextrawurst — VPS portfolio

[Deutsch](README.de.md)

A selected copy of text and code from one person's VPS (Daniel, GitHub: RaDi0n92), built over several
months together with many AI systems: Claude, Codex, Gemini, Kimi, ChatGPT, GLM and others.

The copy is a snapshot taken on 2026-10-15, extended on 2026-10-16. Files are copied as they were; nothing was rewritten, except for the separate repair commit (two truncated Python files restored, one governance check fixed), two `.odt` notes converted to plain `.md`, symlinks replaced by regular files, and one tab ("Claude Code insults?") cut out of `flextrawurst/scripts/build_surface.ts`.

## Layout

`portfolio/` mirrors `/root` on the server.

- `portfolio/ARBEITSWEISE.md` – bilingual (DE/EN): how the contents came about (dialogue instead of prompts, Daniel is a childcare educator and writes no code, about nine months of AI), per Daniel's own statements.
- `portfolio/VOR_FLEXTRAWURST.md`, `portfolio/fruehe-ai-projekte/` – bilingual (DE/EN): the systems and experiments before Flextrawurst (Formfaden and hour-course, Live-Life-Support, Spiral Flow Space, Gordslider, sports-betting prevention) with a timeline by file date and the original files.
- `portfolio/CHATGPT_ERINNERUNGSBERICHT_2026-10-17.md` – a report by ChatGPT from its own memory store, included unchanged: what Daniel discussed, planned and worked on with ChatGPT, and when and how (January to October 2026). ChatGPT's own account, not cross-checked. The report text itself is in German.
- `portfolio/CHATGPT_ERINNERUNGSBERICHT_NACHTRAG_2026-10-18.md` – further ChatGPT answers from its memory store, unchanged (archive inventory, early games, AI homes, game project, KompOase, chronology). ChatGPT's own account, not cross-checked; in German.
- `portfolio/CHATGPT_URL_UND_WEBRECHERCHE_CHRONIK_2026-10-17.md` – a chronicle by ChatGPT of when Daniel gave a URL or commissioned web research and what came of it (January to October 2026). Addresses removed; one entry with private details removed. ChatGPT's own account; in German.
- `portfolio/CHATGPT_URL_CHRONIK_ERGAENZUNG_2026-10-20.md` – addendum to the ChatGPT chronicle (research requests and thematic lines, September to October 2026). Addresses and one paragraph on job applications removed.
- `portfolio/DANIEL_ROHTEXT_2026-10-18_VOM_SYSTEMWEISER_ZUM_PROGRAMMHARNESS.md` – Daniel's own raw text of 2026-10-18, unchanged: his recollection of the path from the early Systemweiser to the planned program harness. Memory, not evidence; in German.
- `portfolio/CHATGPT_URSPRUNGSTEXTE_LIVE_LIFE_SUPPORT_UND_FRUEHE_ENTWUERFE_2026-10-19.md` – early ChatGPT conversations that Daniel pasted as "the first traces": platform model for AI concerns, Live-Life-Support and Spiralflowspace, first product and system document of flextrawurst. Addresses and one personal paragraph removed; ChatGPT's text, not Daniel's reasoning.
- `portfolio/INHALT_ORT_FUER_ORT.md`, `portfolio/HEIMAT_ORDNER.md`, `portfolio/PROJEKTE/` – bilingual (DE/EN): where each kind of content lives, what is in the home of each AI stream, and per project what was attempted, which idea stands behind it and which files belong to it.
- `portfolio/WEGWEISER/` – neutral file guides (German), one per project, e.g. `codewesen.md` for how the code-beings are built. Start with `00_START_HIER.md`. Every statement is taken from the source files' own docstrings and READMEs.
- `portfolio/werkraum/` – the main workspace: documentation, tools, the world API, concept papers, the AI-to-desktop bridge, a word register (WorldWORDS), early conversations, and a description of the game.
- `portfolio/werkraum/_claude`, `_codex`, `_gemini`, `_kimi`, `_gpt`, `_glm`, … – one folder per AI system, each with that system's own notes and files.
- `portfolio/flextrawurst/`, `portfolio/zensi/`, `portfolio/werkraum_geni/` and similar – further projects.

## What you will find replaced or missing

- Credentials, tokens and one secret URL segment are replaced by placeholders such as `[GESCHWAERZT]`.
- Some material was left out on purpose (private or unsuitable content, raw chat transcripts, generated dumps, duplicates).
- Game code and assets are not included. Only documents describing the game are.

## Authorship and license

Authors are named in the file headers, for example "codex bei Daniels VPS" or "claude-code bei Daniels VPS".
Most text is German.

Licensed under [CC BY 4.0](LICENSE). Please credit "Daniel (RaDi0n92) and the AI systems named in the files".
Note: this license was chosen for the texts; it also covers the code in this repository as published.
