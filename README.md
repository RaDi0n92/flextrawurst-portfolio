# flextrawurst — VPS portfolio

[Deutsch](README.de.md)

A selected copy of text and code from one person's VPS (Daniel, GitHub: RaDi0n92), built over several
months together with many AI systems: Claude, Codex, Gemini, Kimi, ChatGPT, GLM and others.

The copy is a snapshot taken on 2026-10-15, extended on 2026-10-16. Files are copied as they were; nothing was rewritten, except for the separate repair commit (two truncated Python files restored, one governance check fixed), two `.odt` notes converted to plain `.md`, symlinks replaced by regular files, and one tab ("Claude Code insults?") cut out of `flextrawurst/scripts/build_surface.ts`.

## Layout

`portfolio/` mirrors `/root` on the server.

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
