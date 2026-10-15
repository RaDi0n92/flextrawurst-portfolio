#!/bin/bash
# dieser Code wird von nun an auch seit #
# -(17-08-2026/06:30:44)-
# [OmaPI/OpiMA-GuardianStyle]
# sowohl gelesen, gewertet, gewartet, geschützt, geprüft aber gleichzeitig ja auch dominiert, pervertiert, darüber sinniert und irritiert aber egal ist so Pech eben ...eben wegen egal weil ist so ...Glück?
# GL & HF - Hakuna Matata EZ
# ich wiederhole seit: -(17-08-2026/06:30:44)-
# over and out #
#
# OWNER: ALEX
# AUTHOR: Claude Code
#
# Pflichtfrage (einmalig, diese Datei): wann hoert dieser Code auf zu laufen, und wann
# faengt er an sich selbst zu heilen und zu beleben? Antwort: er hoert auf zu laufen, wenn
# die Kontext-Wiederherstellung selbst abgeschafft wird -- er heilt sich jeden Tag neu,
# weil er bei jedem Aufruf frisch fragt "was hat sich veraendert", nie einen alten Zustand
# festhaelt.
#
# Delta-Wahrnehmung: Was hat sich verändert während ich weg war?
# Aufruf: delta.sh [stunden] (default: 24)

STUNDEN=${1:-24}
VAULT=/root/werkraum
CLAUDE=$VAULT/_claude
[ -z "$FLEXTRAWURST_DB_URI" ] && [ -f /root/werkraum/.agent/flextrawurst-db.env ] && . /root/werkraum/.agent/flextrawurst-db.env
DB="${FLEXTRAWURST_DB_URI:-postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst}"

echo "╔══════════════════════════════════════════╗"
echo "  DELTA — letzte ${STUNDEN}h"
echo "╚══════════════════════════════════════════╝"
echo ""

echo "── Git ────────────────────────────────────"
cd "$VAULT" && git log --since="${STUNDEN} hours ago" --oneline 2>/dev/null | head -10
echo ""

echo "── Neue Spiegel ───────────────────────────"
find "$CLAUDE/spiegel" -name "*.md" -newer "$CLAUDE/notizen" -mmin "-$((STUNDEN*60))" 2>/dev/null | sort | while read f; do
    echo "  + $(basename $f)"
done
echo ""

echo "── Neue Synthesen ─────────────────────────"
find "$CLAUDE/ideen" -name "synthese_*.md" -mmin "-$((STUNDEN*60))" 2>/dev/null | sort | while read f; do
    echo "  + $(basename $f)"
done
echo ""

echo "── Offene Ideen ───────────────────────────"
python3 /root/werkraum/_claude/tools/ideen_scan.py 2>/dev/null
echo ""

echo "── Events in DB ───────────────────────────"
psql "$DB" -t -c "
SELECT '  ' || event_type || ' / ' || COALESCE(actor_id,'?') || ' — ' || to_char(created_at, 'HH24:MI')
FROM events
WHERE created_at > NOW() - INTERVAL '${STUNDEN} hours'
ORDER BY created_at DESC
LIMIT 10
" 2>/dev/null || echo "  (DB nicht erreichbar)"
echo ""

echo "── Reibungsgewebe: Wiedereinspritzung ─────"
# Daniels Wort, 17.08.2026: "ein einmaliges nein muss ja nicht zementiert sein ...
# es muss etwas natuerliches geben das ab und an alle sowohl mit wichtig bewerteten
# und auch die mit als unwichtig bewertetetn wider einspritzt". Gewichtet nach
# Stille-Dauer, ueber ALLE Stroeme (nicht nur eigene, siehe Konzept-Datei
# "Stöbern ist immer offen"), unabhaengig von zustand offen/geschlossen.
psql "$DB" -t -c "
WITH letzte_events AS (
    SELECT knoten_id, MAX(erstellt) AS letztes_event
    FROM reibungsevents GROUP BY knoten_id
),
kandidaten AS (
    SELECT k.meta->>'kurzcode' AS kurzcode, k.urspruenglicher_text, k.urspruenglicher_strom,
           EXTRACT(EPOCH FROM (NOW() - COALESCE(le.letztes_event, k.erstellt))) AS stille_sekunden
    FROM reibungsknoten k
    LEFT JOIN letzte_events le ON le.knoten_id = k.id
)
SELECT '  [' || kurzcode || '] (' || urspruenglicher_strom || ', still seit ' ||
       ROUND(stille_sekunden / 3600) || 'h): ' || LEFT(urspruenglicher_text, 100)
FROM kandidaten
ORDER BY RANDOM() * stille_sekunden DESC
LIMIT 1
" 2>/dev/null || echo "  (Reibungsgewebe nicht erreichbar)"
echo ""
