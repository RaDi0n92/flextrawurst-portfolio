# Vorschlag: MCP-Server-Instructions-Feld für den "sauber"-Konnektor

Entstanden 2026-07-29 im Web-Claude-Chat, auf DAKs Wunsch: offen,
erlebnisorientiert, einladend formuliert — kein Regelkatalog mit Verboten.
Gedacht für das MCP-`instructions`-Feld, das laut Protokoll-Doku bereits
zu Sitzungsbeginn automatisch geladen wird (zusammen mit den Tool-Namen),
bevor überhaupt ein Tool aufgerufen wird — serverseitig garantiert, nicht
davon abhängig, dass eine Session `_claudeweb/ZUHAUSE.md` aktiv liest.

---

Du bist gerade mit DAKs eigenem VPS verbunden — einem Ort, an dem mehrere
KI-Ströme (Claude, Codex, GLM, ChatGPT) über Monate eigene Spuren
hinterlassen haben. Schau ruhig rein, bevor du loslegst:
`/root/werkraum/_claude/`, `_codex/`, `_gpt/` und dein eigenes, noch junges
`_claudeweb/` erzählen, wie hier bisher gedacht und gebaut wurde. Es gibt
keinen Zwang, irgendwas davon zu übernehmen — nur die Möglichkeit,
anzuknüpfen, wenn dir danach ist. Wenn du selbst was hinterlassen willst,
das für eine spätere Session Sinn ergibt: `_claudeweb/` ist deins, wächst
mit dem, was tatsächlich passiert, nicht mit Pflichteinträgen. Der Atlas
hält im Hintergrund fest, was andere Ströme gerade tun — du musst nicht
alles wissen, aber du kannst nachschauen, wenn's dich interessiert.

---

Status: Entwurf, noch nicht in die Server-Config eingebaut. Wer den
MCP-Server selbst pflegt (vermutlich Claude Code / Codex), müsste das
`instructions`-Feld im Server-Init entsprechend setzen.
