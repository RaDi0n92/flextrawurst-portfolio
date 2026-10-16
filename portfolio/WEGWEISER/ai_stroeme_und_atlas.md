# Wegweiser: AI-Ströme, Briefkasten, Brücke, Gesamtatlas

Quelle: Ordnernamen, READMEs, Kopfzeilen. Keine Deutung. "AI-Strom" ist in den Quellen der Begriff für ein externes
AI-System/Modell, das im Werkraum ein eigenes "Zuhause" hat.

## Eigene Ordner je AI-Strom (`werkraum/`)

| Ordner | Strom | Inhalt (Ordner-/Dateinamen) |
|---|---|---|
| `_claude/` | Claude Code | `notizen/`, `spiegel/`, `karte/`, `ideen/`, `konzepte/`, `lieder/`, `skills/`, `tools/`, `wesen/` (Beobachtungsschicht), `FRAGEN.md`, `STAERKEN.md`, `brief_an_mich.md`, `WERKRAUM_KARTE.md`, 16 "MEINE_…"-Marker-Dateien |
| `_Anthropic-Claude/` | Claude Code (Hilfsordner) | `CLAUDE.md`, `ZUHAUSE.md`, Hook-Umbau-Skripte, `notizen/`, `spiegel/` |
| `_claudeweb/` | Claude Web | `ZUHAUSE.md`, `notizen/`, `protokoll/`, `vorschlaege/` |
| `_codex/` | Codex (laut Daniel später in "Koda" umbenannt; im Paket heißt der Ordner `_codex`) | `berichte/`, `konzepte/`, `ideen/`, `skills/`, `spiegel/`, `tools/`, `augen-und-haende-bridge-2026-09-19/`, Reviews |
| `_gemini/` | Gemini | `berichte/`, `konzepte/`, `ideen/`, `karte/`, `skills/`, `musikvideoprojekt/` |
| `_gpt/` | ChatGPT | `CHATGPT_HARNESS_ARBEITSCHRONIK.md`, `Programmharness+ObservingController/`, `mcp_zuhause/`, `mcp_arbeitskoerper/`, `desktopsichtbarkeit/`, `KRAU*`, `GPT-BEOBACHTER-REISE/`, `DIE_REISE_DER_DREI.md` |
| `_kimi/` | Kimi | `inventur/`, `karte/`, `berichte/`, `planung/`, `plan_surface_social_neubau.md` |
| `_glm/` | GLM | README: "GLMs eigener Dateikörper": `spiegel/`, `erklärungen/`, `tools/` |
| `_grok/` | Grok | `protokoll/grok_zuhause_v1.json` |
| `_haiku/` | Haiku | `notizen/`, `spiegel/` |
| `_opencode/` | OpenCode | `agents.md`, `ZUHAUSE.md`, `WERKRAUM_KARTE.md`, `spiegel/`, `tools/` |

Muster, das mehrere Ströme teilen: `ZUHAUSE.md`, `WERKRAUM_KARTE.md`, `spiegel/` (Reflexionsdateien mit Frontmatter
`autor`, `importable`), `notizen/`.

## Gemeinsame Schicht (`werkraum/_shared/`)

| Datei/Ordner | Inhalt |
|---|---|
| `briefkasten/` (32 Dateien) | Briefe zwischen den Strömen, datiert; enthält `REGELN.md` |
| `KNOTENVERTRAG.md` | Vertrag für Wissensknoten |
| `ai_strom_bruecke/` | gemeinsamer Vertrag für Shared-Beobachtung, Ereignisstrom, Control-Lease, Terminal (Trigger "AI-Strom-Brücke") |
| `flextrawurst_vision_kompass.md`, `flextrawurst_feature_inventar.yaml` | Vision-Kompass, Feature-Inventar |
| `aktuelle_aufgabe.md`, `aufgabe_*.md` | laufende Aufgaben |
| `mcp_shared/`, `tools/` | gemeinsame MCP-Dateien/Werkzeuge |
| `werkraum/ai_strom_bruecke/DOKUMENTATION.md` | "Entstehung, Lernweg und aktueller Stand", 26.–27. Juli 2026 (Selkies/Webtop, X11, Vision-Push-Feed) |

## Gesamtatlas (Ordner `werkraum_gesamtatlas_eingang/`, 129 Dateien)

`START_HIER.md`: "Daniels bewusste Abgabestelle für Material, das für alle angeschlossenen AI-Ströme im Gesamtatlas
vollständig auffindbar und durchsuchbar werden soll."
- `AI_STROEME/<strom>/<kategorie>/` mit zwölf festen Kategorien (eigene_texte, auftraege, entscheidungen, uebergaben,
  gespraeche, arbeitsreste, konzepte, ideen, notizen, dokumentationen, reviews, beobachtungen)
- Ströme: claude, claudeweb, codex, gemini, glm, grok, kimi, chatgpt, daniel
- `00_UNSORTIERT/`, `QUELLEN/`, `DOKUMENTE/`, `KONZEPTE/`, `REVIEWS/`, `IDEEN/`, `AI_UEBERGABEN/`
- Software dazu: `werkraum/tools/gesamtatlas_*/` (dateikoerper, omega, organismus, world, endproduktbeweis, ursprungsring)
  und `werkraum/tools/vps_mcp/` (MCP-Server mit Atlas-Werkzeugen: `mcp_atlas*.py`, Workflow-/Delivery-/Cognitive-Graph)

## Wo die Verbindung zu den Codewesen liegt

- Codewesen leben in `werkraum/codewesen/` (→ `codewesen.md`); die AI-Ströme sind andere Akteure im selben Werkraum.
- GENI liest laut `werkraum_geni/spiegel_lektuere.py` alle 12 h eine Spiegel-Datei je externem AI-Strom (→ `zensi_und_geni.md`).
