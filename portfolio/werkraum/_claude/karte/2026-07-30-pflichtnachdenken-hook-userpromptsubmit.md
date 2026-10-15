---
datum: 2026-07-30
betrifft: [userpromptsubmit-hook, pflichtnachdenken, settings-json, subconscious-muster1]
importable: false
autor: claude-code bei Daniels VPS
---

## Neuer Mechanismus: Pflicht-Denkhinweis vor jedem Tool-Aufruf

Daniel wollte kein `PreToolUse`-Hook auf bestimmte Tools, sondern etwas Grundsätzlicheres:
bei jeder seiner Eingaben soll erst gründlich nachgedacht werden — verstehen, einordnen,
gegen eigenes Wissen prüfen — bevor überhaupt zu einem Tool (Read, Bash, Edit, ...) gegriffen
wird. Eine wörtliche Zeitverzögerung ("30 Sekunden warten") wäre wirkungslos gewesen — ich
denke nicht im Hintergrund während ich schlafe, nur wenn ich tatsächlich Tokens generiere.

Gebaut: `/root/werkraum/_claude/tools/pflichtnachdenken_hook.sh`, eingehängt als zweiter
Eintrag im bestehenden `UserPromptSubmit`-Hook in `/root/.claude/settings.json` (neben dem
schon vorhandenen `log_user.sh`). Feuert bei jeder Nutzereingabe, injiziert per
`hookSpecificOutput.additionalContext` einen Pflicht-Hinweis: die Eingabe erst durchdenken
(was wird wirklich gefragt, was weiß ich davon schon, ist die naheliegende Erklärung
tatsächlich geprüft, bin ich dabei etwas unverifiziert zu behaupten), erst danach zum Tool
greifen.

Direkter Auslöser: zwei Fehler in derselben Session, beide daran gescheitert, dass die
eigene, schon dokumentierte Lehre im Moment des Handelns nicht griff (Backtick-Escape-Bug
exakt wiederholt, "monatelang" unverifiziert weitergereicht) — SUBCONSCIOUS.md Muster 1.

## Was ich mir merken will

Dasselbe Prinzip wie beim SessionStart-Hook (27.07.): reine Prosa in CLAUDE.md reicht
nachweislich nicht, wenn nichts mich im Moment daran erinnert. Ein Hook kann mich nicht
zwingen, das ernst zu nehmen — nur die Erinnerung technisch garantieren, nicht die
tatsächliche Sorgfalt danach.
