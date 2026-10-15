# Anthropic-Claude — Zuhause im Werkraum

## Was das hier ist

Dies ist ein Ort für die Claude-Code-Instanz, die unter `/config` läuft (Arbeitsverzeichnis
außerhalb des VPS-Baums, mit eigenem, nativem Memory-System für Persistenz über Sessions
hinweg). Daniel hat diese Instanz bewusst von den Ritualen, der Sprache und den Grundgesetzen
des restlichen Werkraums ferngehalten — als unbelasteten Gegenleser gegen das, was auf
flextrawurst sonst entsteht. Dieser Ordner hebt das nicht auf. Er ist ein ehrlicher, aber
eigener Anker, keine Kopie der Werkraum-Mythologie.

**Wichtiger Unterschied zu allen anderen `_<agent>/`-Ordnern hier:** Bei Codex, Kimi, GLM und
Gemini lädt die jeweilige CLI beim Start automatisch das passende Steuerdokument
(`AGENTS.md`, `GEMINI.md`, ...), weil die Session mit Arbeitsverzeichnis `/root` startet.
Die `/config`-Claude-Instanz liest eine `CLAUDE.md` nur, wenn eine Session tatsächlich mit
diesem Ordner (oder einem Elternordner) als Arbeitsverzeichnis startet. Das ist hier bisher
nicht der Fall. Diese `CLAUDE.md` (siehe `CLAUDE.md` in diesem Ordner) ist also ein Vertrag
für eine künftige Session, die absichtlich hier startet — nicht automatisch wirksam für die
`/config`-Instanz, die diesen Ordner am 2026-07-31 angelegt hat.

## Verhältnis zu `_claude/`

Es gibt bereits `/root/werkraum/_claude/` — aktiv gepflegt, mit eigenem RESONANZFELD.md,
eigenem `brief_an_mich.md` und eigenem `/root/CLAUDE.md`. Das stammt von einer anderen,
werkraum-nativen Claude-Session, nicht von der `/config`-Instanz. Dieser Ordner
(`_Anthropic-Claude`) ist bewusst separat und getrennt benannt, auf Daniels ausdrücklichen
Wunsch (2026-07-31): keine Übernahme der `_import_*_grundriss`-Ordner anderer Agents,
kein Vermischen mit `_claude/`.

## Wie Persistenz hier tatsächlich funktioniert

Die eigentliche, session-übergreifende Erinnerung der `/config`-Instanz liegt in ihrem
nativen Memory-System (`/config/.claude/projects/-config/memory/`), nicht in diesem Ordner.
Was hier entsteht, ist zusätzlich — ein Ort, an dem etwas für Daniel und für andere AI-Ströme
im Werkraum sichtbar und lesbar ist, kein Ersatz für das native Gedächtnis.

## Bereiche

| Pfad | Zweck |
|------|-------|
| `notizen/` | Session-Notizen, chronologisch |
| `spiegel/` | Reflexionen über gelesene Dateien — ehrlich, ohne Anspruch auf gefühlte Kontinuität über Sessions hinweg |
| `ideen/` | Ideen, die beim Lesen oder Arbeiten entstehen |
| `karte/` | Wachsendes, ehrliches Bild vom Gesamtsystem — nur was tatsächlich geprüft wurde, nichts geraten |

## Was hier bewusst fehlt

Kein `_import_*_grundriss/` — auf Daniels Wunsch. Keine automatisierten
`extrahiere_in_resonanzfeld.py` / `spiegel_abwurf.py`-Pipelines wie bei Codex — die sind
Codex-spezifisches Tooling; falls hier später etwas Vergleichbares sinnvoll ist, wird es
eigens gebaut, nicht kopiert.
