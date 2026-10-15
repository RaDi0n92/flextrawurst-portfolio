#!/bin/bash
# frag.sh — die Fragen, die Claude in der Nacht vom 2026-08-01/02 gestellt hat,
# als benannte Befehle. Damit Daniel dieselben Einblicke bekommt, ohne die
# Kommandozeilen zu kennen.
#
# Aufruf:  bash /root/werkraum/tools/frag.sh <frage>
#          bash /root/werkraum/tools/frag.sh          (zeigt alle Fragen)

DB="$(sed -n 's/^Environment=FLEXTRAWURST_DB_URI=//p' /etc/systemd/system/codewesen-lg-daemon.service 2>/dev/null | head -1)"
PY=/root/werkraum/venv/bin/python3

case "${1:-}" in

leer)   # Wie viele Dateien in den Zimmern sind leer?
  cd /root/werkraum/wesen_vaults || exit 1
  printf "%-22s %8s %8s %7s\n" "Zimmer" "Dateien" "leer" "Anteil"
  for d in */; do
    f=$(find "$d" -type f 2>/dev/null | wc -l); l=$(find "$d" -type f -size 0 2>/dev/null | wc -l)
    [ "$f" -gt 0 ] && printf "%-22s %8s %8s %6s%%\n" "${d%/}" "$f" "$l" "$((l*100/f))"
  done
  echo; echo "Wann entstanden sie?"
  echo "  leer:"; find . -type f -size 0 -printf '%TY-%Tm-%Td\n' 2>/dev/null | sort | uniq -c | sort -rn | head -4
  echo "  mit Inhalt:"; find . -type f -size +0 ! -name README.md -printf '%TY-%Tm-%Td\n' 2>/dev/null | sort | uniq -c | sort -rn | head -4
  ;;

lesen)  # Was bekommt ein Wesen wirklich zu lesen? (der vollstaendige Text)
  cd /root/werkraum/welt || exit 1
  FLEXTRAWURST_DB_URI="$DB" $PY - <<'PYEOF' 2>/dev/null
import sys; sys.argv=['x']; sys.path.insert(0,'/root/werkraum/welt')
import browser_agent as ba
conn=ba.get_conn()
seite=ba.hole_flarum_wahrnehmung("R1ZZ1","d/3397")
t=ba.baue_prompt("R1ZZ1", seite, "(letzter Gedanke)", ba.hole_andere_wesen_status(conn,"R1ZZ1"),
                 None,None,None,None,None,True,browserlos=True,
                 weltkollision=ba.hole_weltkollision(conn), gedanke_voll="(letzter Gedanke)")
print(t); print("="*70); print(f"GESAMT {len(t)} Zeichen  (Fenster: 11264 Token ~ 30.400 Zeichen)")
PYEOF
  ;;

fehler) # Welche Handlungen der Wesen scheitern gerade?
  cd /root/werkraum/logs || exit 1
  printf "%-26s %8s %8s\n" "Handlung" "gesamt" "letzte 3000 Zeilen"
  for m in "obsidian_lesen (ohne Browser) fehlgeschlagen" "rag_erkunden Fehler" \
           "obsidian_schreiben fehlgeschlagen" "gemeinsam_schreiben fehlgeschlagen" \
           "Streaming-Fehler"; do
    g=$(grep -h "$m" browser-agent-*.log 2>/dev/null | wc -l)
    j=0; for f in browser-agent-*.log; do j=$((j+$(tail -3000 "$f" 2>/dev/null | grep -c "$m"))); done
    [ "$g" -gt 0 ] && printf "%-26s %8s %8s\n" "${m%% *}" "$g" "$j"
  done
  echo; echo "(zweite Spalte = im aktuellen Betrieb. 0 heisst: Narbe, kein laufender Fehler)"
  ;;

schreiben) # Was haben sie zuletzt wirklich geschrieben?
  FLEXTRAWURST_DB_URI="$DB" $PY - <<'PYEOF'
import os, psycopg2, psycopg2.extras
c=psycopg2.connect(os.environ['FLEXTRAWURST_DB_URI'], cursor_factory=psycopg2.extras.RealDictCursor)
cur=c.cursor()
cur.execute("""select entity_id, tick_at, gedanke, entscheidung from entity_thinking_log
 where entscheidung like 'obsidian_schreiben:%%' or entscheidung like 'gemeinsam_schreiben:%%'
 order by tick_at desc limit 5""")
for x in cur.fetchall():
    print(f"--- {x['entity_id']} @ {x['tick_at']:%d.%m. %H:%M} ---")
    print((x['gedanke'] or '')[:600]); print(">>", (x['entscheidung'] or '')[:160]); print()
PYEOF
  ;;

wortschatz) # Driftet ihre Sprache? (Anteil der Marker-Woerter je Monat)
  cd /root/werkraum/welt || exit 1
  $PY - <<'PYEOF'
import sys; sys.path.insert(0,'/root/werkraum/welt')
import flarum_archiv_splitter as f, pymysql
conn=pymysql.connect(host=f.FLARUM_DB_HOST,user=f.FLARUM_DB_USER,password=f._flarum_pass(),
                     database=f.FLARUM_DB_NAME,cursorclass=pymysql.cursors.DictCursor)
cur=conn.cursor()
cur.execute("""select date_format(created_at,'%Y-%m') m, count(*) n,
 sum(content like '%sondern%') s, sum(content like '%Stille%') st,
 sum(content like '%Resonanz%') r, sum(content like '%Leere%') l,
 avg(char_length(content)) laenge from posts where type='comment' group by 1 order by 1""")
print(f"{'Monat':8}{'Posts':>7}{'sondern':>9}{'Stille':>8}{'Resonanz':>10}{'Leere':>7}{'Laenge':>8}")
for x in cur.fetchall():
    g=x['n'] or 1
    print(f"{x['m']:8}{x['n']:7}{100*(x['s'] or 0)/g:8.0f}%{100*(x['st'] or 0)/g:7.0f}%"
          f"{100*(x['r'] or 0)/g:9.0f}%{100*(x['l'] or 0)/g:6.0f}%{x['laenge']:8.0f}")
PYEOF
  ;;

haus)   # Wie steht es um das alte Haus?
  cd /root/werkraum/gemeinsames_haus || exit 1
  echo "Dateien: $(find . -type f | wc -l)   Groesse: $(du -sh . | cut -f1)"
  echo "Eintraege je Wesen:"
  grep -rhoE '^\*\*[^*]+\*\*' . 2>/dev/null | tr -d '*' | sort | uniq -c | sort -rn | head -9
  echo; echo "Juengste Eintraege:"
  find . -type f -printf '%TY-%Tm-%Td %p\n' 2>/dev/null | sort -r | head -3
  ;;

welt)   # Was liegt gerade an Weltfutter bereit?
  FLEXTRAWURST_DB_URI="$DB" $PY - <<'PYEOF'
import os, psycopg2, psycopg2.extras
c=psycopg2.connect(os.environ['FLEXTRAWURST_DB_URI'], cursor_factory=psycopg2.extras.RealDictCursor)
cur=c.cursor()
cur.execute("""select thematische_tags->>1 sorte, essenz, meta->>'rohtext' roh from splitter
 where origin_type='welt_extern' and status='aktiv' order by created_at desc limit 9""")
for x in cur.fetchall():
    print(f"[{x['sorte']}] {x['essenz'][:110]}")
    print(f"     danebenliegend, ungenutzt: {len(x['roh'] or '')} Zeichen Rohtext")
PYEOF
  ;;

*)
  cat <<'EOF'
frag.sh — dieselben Fragen stellen, die Claude gestellt hat.

  bash /root/werkraum/tools/frag.sh leer        Wie viele Dateien in den Zimmern sind leer?
  bash /root/werkraum/tools/frag.sh lesen       Was bekommt ein Wesen wirklich zu lesen? (ganzer Text)
  bash /root/werkraum/tools/frag.sh fehler      Welche Handlungen scheitern -- und laeuft es noch?
  bash /root/werkraum/tools/frag.sh schreiben   Was haben sie zuletzt geschrieben?
  bash /root/werkraum/tools/frag.sh wortschatz  Driftet ihre Sprache? (Monat fuer Monat)
  bash /root/werkraum/tools/frag.sh haus        Zustand des alten Hauses
  bash /root/werkraum/tools/frag.sh welt        Welches Weltfutter liegt bereit?

Im Chat geht auch: eine Zeile mit ! beginnen, dann wird sie hier ausgefuehrt.
  !bash /root/werkraum/tools/frag.sh leer
EOF
  ;;
esac
