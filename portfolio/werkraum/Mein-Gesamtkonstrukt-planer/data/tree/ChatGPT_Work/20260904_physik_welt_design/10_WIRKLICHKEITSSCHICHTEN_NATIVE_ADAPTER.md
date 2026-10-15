# Wirklichkeitsschichten / native Adapter · dünner Vertrag

Ziel: verschiedene Quellen gemeinsam **darstellbar** machen, ohne sie technisch oder identitär gleichzuschalten.

## 1. Eine Aussage über die Welt braucht mehr als `true/false`

Für wichtige operative Aussagen sind mindestens relevant:
- **Quelle** – woher wissen wir das?
- **Frische** – wann wurde es beobachtet?
- **Reichweite** – was konnte die Quelle überhaupt sehen?
- **Art** – gemessen, abgeleitet, modelliert, unbekannt?

Nicht jedes UI-Element braucht diese Felder sichtbar. Maschinenblick/Inspektion sollte sie bei Bedarf erreichbar machen.

## 2. Quelle, Capability und Wirkung auseinanderhalten

Beispiel:
- Tool steht im Katalog
- Runtime kann Tool vielleicht erreichen
- konkreter Actor darf es vielleicht benutzen
- Aufruf lief vielleicht
- gewünschte Wirkung ist vielleicht trotzdem nicht eingetreten

Darum nicht vermischen:

`advertised → available → attempted → executed → effect confirmed`

Diese Kette ist Denkstütze, kein neues Pflichtschema.

## 3. Native Adapter bleiben nativ

Gemeinsame Weltsemantik gehört **oberhalb** der nativen Quellen.

Nicht alle Systeme zwingen, identische Logs zu schreiben.

Muster:

`native Quelle → kleiner Adapter/Übersetzer → gemeinsame Darstellung`

Provenienz zum nativen Ursprung erhalten.

## 4. Claude-Familie nicht normalisieren

### Claude Code
Mögliche native Quellen:
- Claude-Sessiondateien
- Hooks/Toolergebnisse
- Terminal-/Dateispuren

### Haiku
Eigener Stromkörper `_haiku` mit eigener nativer Claude-Sessionwurzel.

Nicht jede Claude-Code-Session, die Modell Haiku benutzt, wird dadurch automatisch zum Haiku-Strom.

### Anthropic_Claude
Eigene `_Anthropic-Claude`-/historische `/config`-Linie.

Aktuellen Livezugriff auf historische `/config`-Quellen vor Verwendung neu prüfen.

**Claude Code ≠ Anthropic_Claude ≠ Haiku.**

## 5. Gemini-Familie nicht normalisieren

### Gemgem
Primärer Werkraum-Strom mit `_gemini/` als eigenem Zuhause-/Spurenkörper.

### Gravityy
Eigene Antigravity-/Desktop-/Brain-Linie.

Der aktuelle Atlas-`gemini`-Eintrag ist deshalb problematisch: Gemgems Zuhause wurde mit Gravityys Antigravity-Sessionquelle verbunden.

**Gemgem ≠ Gravityy.**

Die normale Gemini CLI ist wiederum ein technischer Runtime-/CLI-Körper und nicht automatisch einer dieser beiden Ströme.

## 6. Codex / Kimi / GPT-MCP ebenfalls aus ihrer echten Quelle lesen

### Codex
Native Rollout-/Sessiondateien, CLI-Review/Fork/Sandbox usw.

### Kimi
Eigene Kimi-CLI-/Session-/Zuhause-Spuren.

### GPT / ChatGPT über VPS-MCP
Toolantworten, Connectorprovenienz, konkrete Dateien/Browser-/Dienst-/DB-Aktionen und Handoffs.

Mehrere GPT-Instanzen dürfen gleichzeitig existieren.

## 7. Browser / Desktop sind keine Actorbeweise

Ein geöffneter Tab oder laufender Desktop beweist nicht automatisch:
- welcher Strom ihn gerade benutzt
- wer die letzte Aktion ausgelöst hat
- wer „Besitzer“ ist

Wenn Actor-Provenienz wichtig ist, separate Belege benutzen.

## 8. Vorhaben, Ausführung und Wirkung trennen

### Vorhaben / Vorschlag
`Ich möchte X tun.`

Noch keine Weltwirkung.

### Ausführung
Ein nativer Tool-/Prozess-/CLI-Körper versucht die Handlung.

### Wirkung
Die Welt/Zieldatei/der Dienst wurde tatsächlich verändert oder geprüft.

Wirkung braucht eigenen Beleg, wenn sie wichtig ist.

Ein Agententext „fertig“ reicht nicht.

## 9. Correlation nur dort, wo sie gebraucht wird

Es kann nützlich sein, Proposal, Prozess, Effect, Review oder Run zusammenzuhalten.

Aber keine universelle Correlation-ID-Welt auf Vorrat bauen.

Erst konkrete vertikale Szene beobachten:
> Welche zwei Spuren müssen wir wirklich zuverlässig wieder zusammenfinden?

Dann minimal verbinden.

## 10. Adapterfrische ist selbst wichtig

Eine Quelle kann:
- frisch/live
- historisch
- stale
- partiell
- kaputt/unreachable

sein.

Darstellung darf das zeigen, statt aus altem Material aktuelle Aktivität zu erfinden.

Beispiel: große alte Codex-Rollouts bedeuten nicht `Codex arbeitet gerade`.

## 11. Scanänderung ohne beobachteten Actor ist zulässig

Wenn Atlas/Dateiscan sieht:
> zwischen zwei Beobachtungen hat sich etwas geändert

aber keine konkrete Handlung belegt ist, dann genau das zeigen.

Keinen Täter/Agenten erfinden.

## 12. Normalisierung nur so weit wie nötig

Gemeinsame Begriffe können helfen:
- aktuelle Aktivität
- fortbestehende Arbeit
- Wait/Gate
- belegter Effect
- Herkunft

Aber native Unterschiede dürfen sichtbar bleiben.

Claude Background ≠ Kimi AFK ≠ Gemini Worktree ≠ Codex Fork.

Sie können ähnlich dargestellt werden, ohne dass die Quelle identisch behauptet wird.

## 13. UI-Folge

Normalansicht:
- verständliche Weltwirkung

Bei Nähe/Fokus:
- Actor/Arbeitskörper, wenn belegt
- relevante Quelle/Frische

Maschinenblick:
- native Session-/Tool-/Pfad-/Hash-/Logdetails

So bleibt die Welt lesbar, ohne Provenienz zu verstecken.

## Nicht jetzt

- alle Anbieter/CLIs auf ein universelles Eventformat zwingen
- Master-Actor-ID erfinden
- Atlasregister zur Identitätswahrheit erklären
- jede native Aktivität dauerhaft materialisieren
- vollständigen Adapter für jeden möglichen Strom bauen, bevor eine Szene ihn braucht
