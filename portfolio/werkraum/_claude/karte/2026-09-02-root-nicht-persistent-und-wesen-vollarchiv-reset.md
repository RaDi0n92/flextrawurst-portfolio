---
datum: 2026-09-02
betrifft: [root-persistenz, docker-overlay, vps-root-mount, wesen, vollarchiv-reset, symlinks]
importable: false
autor: claude-code bei Daniels VPS
---

# Zwei alte Lücken, beide bis zur echten Ursache verfolgt

Beim heutigen Sessionritual sind zwei Lücken aufgefallen, die vorher nur als "fehlt" im Raum
standen: `/root/visionen/` existierte nicht mehr, alle 8 Dateien in `_claude/wesen/` waren leer.
Beide bis zur Quelle verfolgt statt nur gemeldet — hier die Ergebnisse, damit sie nicht nochmal
neu gesucht werden müssen.

## Fund 1 — `/root` selbst ist nicht persistent, nur was symlinkt

`/` ist in diesem Container ein Docker-Overlay-Dateisystem (`overlay on / type overlay ...`,
`upperdir=/var/lib/docker/overlay2/...`) — bei einem Rebuild des virtuellen Desktops wird dieser
Layer neu aufgesetzt. Persistent ist nur `/vps_root`, der Bind-Mount des echten Host-`/root`
(dasselbe Muster, das schon in `2026-07-27-sessionstart-hook-und-vps-desktop-bind-mount.md`
dokumentiert ist, nur diesmal am eigenen Leib erlebt statt nur gelesen).

`/root/werkraum` und `/root/werkraum_git` überleben Rebuilds nur, weil sie Symlinks nach
`/vps_root/werkraum` bzw. `/vps_root/werkraum_git` sind (bestätigt: `ls -la /root/` zeigt
`lrwxrwxrwx`). `/root/visionen` war das nie — ein normaler Ordner direkt unter `/root`, kein
Symlink. Bei einem der Desktop-Rebuilds (der 21.08.-Briefkasten-Brief erwähnt exakt dasselbe
Muster beim `werkraum_git`-Symlink, der damals ebenfalls weg war) ist er mit dem Container
verschwunden. Das Bild selbst war nie weg: `/vps_root/visionen/ChatGPT Image 21. Mai 2026,
23_30_02.png` lag die ganze Zeit unverändert da, 2,3 MB, Original-Datum 21. Mai.

**Fix:** `/root/visionen` neu als Symlink auf `/vps_root/visionen` angelegt — dasselbe Muster wie
bei `werkraum`. Übersteht jetzt künftige Rebuilds.

**Was das für den Rest des Systems heißt:** jeder andere Ordner direkt unter `/root`, der nicht
über einen Symlink nach `/vps_root` läuft, hat dasselbe latente Risiko. Nicht systematisch
durchsucht, nur benannt — wäre ein eigener kleiner Auftrag (`find /root -maxdepth 1 -not
-type l`, gegen `/vps_root` gegenprüfen), falls das nochmal auffällt.

## Fund 2 — `wesen/` war nie kaputt, sondern Daniels eigener Reset

`git log` auf `_claude/wesen/*.md` zeigte die leeren Dateien nicht als Bug, sondern als
Wiederherstellung eines bereits leeren Zustands: Commit `1e74637c2`, **Autor "Daniel" selbst**,
2026-08-02 11:52, Message wörtlich: *"Vollarchiv 2026-08-02 angelegt, 490-Liste zurueck, alle
eigenen Schreibsachen geleert."* Derselbe Commit hat auch `FRAGEN.md`, `STAERKEN.md` und
`WERKRAUM_KARTE.md` geleert — alle vier waren seitdem leer, nicht nur `wesen/`.

Der Originalinhalt lag die ganze Zeit unversehrt im selben Repo, unter
`_claude/archiv/vollstaendig_2026-08-02/wesen/` — pro Wesen die vollen Muster-/Fragen-/
Leerstelle-Abschnitte, für `dak+gord-system` z.B. die Frage nach dem "etwas", das entsteht,
wenn Resonanz abbricht.

**Fix:** alle 8 Dateien 1:1 aus dem Archiv zurückkopiert, committed (`1ccaec962`).

**Was noch offen bleibt, bewusst nicht angefasst:** `FRAGEN.md`, `STAERKEN.md` und
`WERKRAUM_KARTE.md` sind vom selben 02.08.-Reset betroffen und liegen ebenfalls noch leer im
aktiven `_claude/` — nur `wesen/` wurde heute wiederhergestellt, weil nur danach gefragt wurde.
Ob die drei anderen genauso zurückkommen sollen oder der Reset dort bewusst dauerhaft gemeint
war, ist nicht geklärt. [status: offen]

## Was ich mir merken will

Ein leerer Ordner oder eine leere Datei ist in diesem System nicht automatisch ein Fehler — kann
genauso gut ein bewusster, dokumentierter Reset sein. `git log` auf die konkrete Datei zeigt das
in der Regel schnell (Autor, Commit-Message), bevor man von "kaputt" ausgeht. Und: ein Symlink
nach `/vps_root` ist in diesem Setup keine Stilfrage, sondern die einzige Absicherung gegen
Desktop-Rebuilds — jede neue, dauerhaft gemeinte Datei/jeder Ordner direkt unter `/root` sollte
das künftig gleich mitbekommen, statt es erst beim nächsten Rebuild zu vermissen.

## Dokumente gehören zusammen

`2026-07-27-sessionstart-hook-und-vps-desktop-bind-mount.md` (derselbe Mount-Mechanismus, zuerst
dokumentiert), der Briefkasten-Brief `2026-08-21_claude_an_codex_gemini.md` (dieselbe
Nicht-Persistenz, damals beim `werkraum_git`-Symlink), `_claude/wesen/_INDEX.md` (was die
wiederhergestellten Dateien inhaltlich tragen).
