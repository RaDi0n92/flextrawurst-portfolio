#!/bin/bash
# UserPromptSubmit-Hook: erzwingt bei JEDER Nutzereingabe einen Pflicht-Denkhinweis,
# bevor der erste Tool-Aufruf (Read, Bash, Edit, ...) passiert.
# Auslöser (2026-07-30): zwei Fehler in derselben Session, die beide daran scheiterten,
# dass die eigene, schon dokumentierte Lehre im Moment des Handelns nicht zur Wirkung kam
# (Backtick-Escape-Bug exakt wiederholt, "monatelang" unverifiziert weitergereicht).
# Kein Zeit-Delay (Schlaf macht ein LLM nicht gruendlicher) -- stattdessen ein
# unuebersehbarer Hinweis, der bei jeder Eingabe neu ins Gedaechtnis geholt wird.

read -r -d '' CONTEXT <<'EOF'
PFLICHT VOR DEM ERSTEN TOOL-AUFRUF: Diese Eingabe erst gruendlich durchdenken, dann erst
zu einem Werkzeug (Read, Bash, Edit, Grep, ...) greifen.

Konkret pruefen, nicht nur ueberfliegen:
- Was wird hier wirklich gefragt/verlangt -- nicht nur der erste plausible Lesart folgen.
- Was weiss ich davon schon (eigene Doku, SUBCONSCIOUS.md-Muster, bereits gemachte Fehler
  an aehnlicher Stelle)? Wurde das schon einmal dokumentiert, und hab ich es gerade
  wirklich im Kopf, nicht nur "irgendwo abgelegt"?
- Ist die naheliegende Erklaerung tatsaechlich geprueft oder nur plausibel angenommen?
- Bin ich dabei, etwas zu behaupten (Zahl, Zeitspanne, Ursache), das ich noch nicht
  verifiziert habe?

Erst wenn das beantwortet ist: zum passenden Tool greifen.
EOF

python3 - "$CONTEXT" <<'PYEOF'
import json, sys
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": sys.argv[1]
    }
}))
PYEOF
