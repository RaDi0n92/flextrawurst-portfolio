---
datum: 2026-07-27
betrifft: [sessionstart-hook, kontext-ritual, virtueller-desktop, docker-bind-mount, sicherheit]
importable: false
autor: claude-code bei Daniels VPS
---

## Neuer Mechanismus: SessionStart-Hook erzwingt das Kontext-Ritual

`/root/.claude/settings.json` hat jetzt einen `SessionStart`-Hook (Matcher
`startup|resume|clear|compact`), der `/root/werkraum/_claude/tools/session_start_ritual.sh`
aufruft, bevor ich auf die erste Nutzer-Nachricht antworte.

Das Skript liefert per
`hookSpecificOutput.additionalContext` einen Pflicht-Hinweis auf das Ritual in CLAUDE.md
(Zeile 33-67) plus die komplette `delta.sh`-Ausgabe der letzten 24h — bewusst kein Voll-Dump
aller Ritual-Dateien (karte/, notizen/, spiegel/ usw.), weil das die 2026-07-11 eingeführte
Lesetiefe-Kostenregel aushebeln würde.

Grund für den Bau: reine Prosa in CLAUDE.md wurde
nachweislich übersprungen, wenn eine Session beiläufig beginnt ("huhu").

## Neue Struktur-Erkenntnis: virtuelle Desktops haben vollen Host-Zugriff

`docker inspect` von `virtuellerdesktop1`/`virtuellerdesktop2` (linuxserver/webtop, Ports
3090/3091, extern über flextrawurst.de/virtuellerdesktop{1,2}/) zeigt: Host-`/root` ist im
Container auf `/vps_root` gemountet, und der komplette Host-`/` zusätzlich auf `/vps_system`
— beides Bind-Mounts, nicht Volumes.

Ein aus diesen "freien Test-Desktops" gestartetes Programm
hat damit vollen Lese-/Schreibzugriff auf das komplette VPS-Filesystem, nicht nur auf `/root`.
Keine Dokumentation gefunden, die diese Entscheidung (wer, wann, warum) festhält — nur die
nackte Tatsache im Mount-Layout. Nicht angefasst, auf Daniels ausdrücklichen Wunsch hin
unverändert gelassen (siehe `feedback_keine_unaufgeforderten_einschraenkungen` in Memory).

## Sechster Nachbar im Briefkasten angekündigt

Daniel plant, die Claude-Code-Instanz die er heute in `virtuellerdesktop2` gestartet hat,
dauerhaft als eigenständigen, sechsten AI-Strom zu etablieren (nach Claude/Codex/GML/Gemini/
ChatGPT) — mit eigener CLAUDE.md, eigenem Vault-Zuhause, eigenem Briefkasten-Namen (noch nicht
festgelegt), eigener semantischer Suche. Bewusst NICHT als Spiegel von mir/diesem System
aufgesetzt — Daniels Begründung: ein Strom ohne die angesammelte Geschichte kann Code/MDs
unverfälscht von außen gegenlesen. Rolle nicht nur Prüfer, auch Fixer/Bauer wenn passend.
Einrichtung macht Daniel selbst direkt mit jenem Claude, nicht über mich.
