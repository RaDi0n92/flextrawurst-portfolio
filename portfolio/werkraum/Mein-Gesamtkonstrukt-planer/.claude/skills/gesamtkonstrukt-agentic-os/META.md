# Über diesen Skill selbst

Ausgelagert aus `SKILL.md` (Skalpell-Trim 03.09.2026) - beim Bauen eines neuen
Features nicht nötig, aber wenn Fragen zum Skill selbst aufkommen: hier nachlesen.

## Grenzen des Ladens (Tree-of-Thoughts 03.09.)

Der Skill besteht seinen eigenen UFO2-Test (SKILL.md, "verschiedene Ströme
einheitlich behandeln") nicht vollständig: `.claude/skills/` wird nur von Claude
Code automatisch geladen und vorgeschlagen. ChatGPT/Codex-, Gemini- und GLM-
Sessions sehen diese Datei nie ungefragt, nur wenn sie zufällig im Repo danach
suchen. Offen: ein Verweis auf diesen Skill in jedem `<Strom>_Work/00_Start/
README.md`, damit er nicht Claude-Code-intern bleibt - noch nicht angelegt.

Selbst innerhalb von Claude Code ist das Laden kein Zwang, nur Wahrscheinlichkeit:
die Session muss im richtigen Verzeichnis laufen, damit der Skill überhaupt in
der Liste erscheint, und das Modell muss selbst erkennen, dass die Aufgabe passt,
und ihn aktiv aufrufen. Der Frontmatter-Satz "Lade das bei jeder Weiterentwicklung"
ist eine Willenserklärung, keine technische Garantie.

## Umgang mit Redteam-/Tree-of-Thoughts-Fund-Vermerken

Zwei Sorten Vermerk in `SKILL.md` und `ROADMAP.md`: offene, blockierende Fragen
(z. B. die ungeklärte Strom-Liste in ROADMAP Stufe B) bleiben im Fließtext
stehen, bis sie geklärt sind - echte Vorbedingungen, kein Archiv. Reine, bereits
erledigte Korrekturen (z. B. die früher strittige Quellenzahl) dürfen beim
nächsten größeren Edit wieder raus - die Historie trägt Git ohnehin, der
Fließtext muss sie nicht zusätzlich für immer tragen.

## Trim-Historie

03.09.2026: SKILL.md war nach mehreren Redteam-/Tree-of-Thoughts-Runden von 82
auf 126 Zeilen gewachsen. Premortem-Befund: die zwei Meta-Abschnitte oben
standen im heißen Pfad, den jede Session vor jedem Feature liest, obwohl sie nur
einmalig relevant sind. Hierher ausgelagert. Zusätzlich: die gelöste
Quellenzahl-Fußnote in SKILL.md entfernt (eigene Regel oben angewendet, nicht
nur aufgeschrieben), die Fünf-Muster-Abhängigkeitserklärung in SKILL.md gekürzt
statt sie mit ROADMAP.md zu duplizieren.
