# flextrawurst — VPS-Portfolio

[English](README.md)

Eine Auswahl an Text und Code vom VPS einer Person (Daniel, GitHub: RaDi0n92), entstanden über mehrere
Monate gemeinsam mit vielen KI-Systemen: Claude, Codex, Gemini, Kimi, ChatGPT, GLM und weiteren.

Die Kopie ist ein Stand vom 2026-10-15, ergänzt am 2026-10-16. Dateien sind so kopiert, wie sie waren; nichts wurde umgeschrieben, außer im separaten Reparatur-Commit (zwei abgeschnittene Python-Dateien wiederhergestellt, eine Governance-Prüfung korrigiert), zwei `.odt`-Notizen als reiner Text in `.md` umgewandelt, Symlinks durch normale Dateien ersetzt und ein Tab („Claude Code beleidigt?“) aus `flextrawurst/scripts/build_surface.ts` herausgeschnitten.

## Aufbau

`portfolio/` spiegelt `/root` auf dem Server.

- `portfolio/ARBEITSWEISE.md` – zweisprachig (DE/EN): wie die Inhalte entstanden sind (Dialog statt Prompts, Daniel ist Erzieher und schreibt keinen Code, rund neun Monate KI), nach Daniels eigenen Angaben.
- `portfolio/VOR_FLEXTRAWURST.md`, `portfolio/fruehe-ai-projekte/` – zweisprachig (DE/EN): die Systeme und Versuche vor Flextrawurst (Formfaden und Stundenverlauf, Live-Life-Support, Spiral Flow Space, Gordslider, Sportwetten-Prävention) mit Zeitlinie nach Dateidatum und den Originaldateien.
- `portfolio/CHATGPT_ERINNERUNGSBERICHT_2026-10-17.md` – ein Bericht von ChatGPT aus dessen Erinnerungsspeicher, unverändert übernommen: was Daniel wann und wie mit ChatGPT besprochen, geplant und gearbeitet hat (Januar bis Oktober 2026). Wiedergabe von ChatGPT, nicht gegengeprüft.
- `portfolio/INHALT_ORT_FUER_ORT.md`, `portfolio/HEIMAT_ORDNER.md`, `portfolio/PROJEKTE/` – zweisprachig (DE/EN): wo welche Art von Inhalt liegt, was in den Zuhause der AI-Ströme liegt, und pro Projekt, was versucht wurde, welche Idee dahintersteht und welche Dateien dazugehören.
- `portfolio/WEGWEISER/` – neutrale Dateiwegweiser, einer pro Projekt, z. B. `codewesen.md` dazu, wie die Codewesen gebaut sind. Einstieg: `00_START_HIER.md`. Jede Aussage stammt aus den Docstrings und READMEs der Quelldateien selbst.
- `portfolio/werkraum/` – der Hauptarbeitsraum: Dokumentation, Werkzeuge, Welt-API, Konzepte, die Bridge zwischen KI und Desktop, ein Wortregister (WorldWORDS), frühe Gespräche und eine Beschreibung des Spiels.
- `portfolio/werkraum/_claude`, `_codex`, `_gemini`, `_kimi`, `_gpt`, `_glm`, … – ein Ordner pro KI-System, jeweils mit den eigenen Notizen und Dateien.
- `portfolio/flextrawurst/`, `portfolio/zensi/`, `portfolio/werkraum_geni/` und ähnliche – weitere Projekte.

## Was ersetzt ist oder fehlt

- Zugangsdaten, Tokens und ein geheimer URL-Teil sind durch Platzhalter wie `[GESCHWAERZT]` ersetzt.
- Einiges wurde bewusst weggelassen (Privates oder Ungeeignetes, rohe Chat-Transkripte, generierte Dumps, Duplikate).
- Spiel-Code und -Assets sind nicht enthalten, nur Dokumente, die das Spiel beschreiben.

## Urheberschaft und Lizenz

Die Autoren stehen in den Dateiköpfen, zum Beispiel "codex bei Daniels VPS" oder "claude-code bei Daniels VPS".
Der Großteil des Textes ist deutsch.

Lizenz: [CC BY 4.0](LICENSE). Bitte nennen: "Daniel (RaDi0n92) und die in den Dateien genannten KI-Systeme".
Hinweis: Die Lizenz wurde für die Texte gewählt; sie gilt in dieser Veröffentlichung auch für den enthaltenen Code.
