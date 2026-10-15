---
datum: 2026-07-29
betrifft: [vps-mcp, claude-web, chatgpt, oauth, allowed-roots, schreib-erlaubte-wurzeln, vps-shell, instructions-feld]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich heute über das System gelernt habe

**Drei MCP-Klone, ein Prozess-Code, keine Sonderbehandlung im Code.** `vps-mcp.service` (ChatGPT,
Port 8091), `vps-mcp-shared.service` (Claude Code/Codex/Gemini, Port 8092), `vps-mcp-sauber.service`
(Claude Web, Port 8093) führen alle exakt dieselbe `vps_mcp_server.py` aus. Kein Port-basiertes
`if`, keine Client-Erkennung — jeder Unterschied im Verhalten kommt entweder aus Umgebungsvariablen
(eigene Protokoll-JSON, eigener Action-History-Pfad) oder aus dem Client selbst, nie aus einer im
Code eingebauten Bevorzugung eines bestimmten AI-Stroms.

**Zwei getrennte Zugriffsgrenzen, leicht zu verwechseln.** `ALLOWED_ROOTS` (Lesen) enthält
absichtlich `"/"` — Daniels Wille war "selbes recht für alle" (ChatGPT, Codex, Gemini). Für
Schreiben gilt eine andere, viel engere Liste, `SCHREIB_ERLAUBTE_WURZELN` — nur `werkraum` und
seine Symlink-Geschwister, kein `flextrawurst` (laufendes System), kein `zensi`. Diese Trennung
existiert, weil Daniel nach anfänglichem "chatgpt soll alles in root dürfen" einen Rückzieher
gemacht hat, nachdem der Auto-Mode-Classifier wiederholt blockiert hat: "ok ich lenke ein kein
schreiben in root nur kompletter werkraum dann eben." Beide Listen stehen mit ihrer vollen
Entstehungsgeschichte als Kommentar direkt im Code — Provenienz-Prinzip in Reinform.

**`vps_shell` prüft nur den Startordner, nicht was der Befehl tatsächlich anfasst.** Der Server
läuft komplett als root. `tool_shell()` verlangt, dass `cwd` in `SCHREIB_ERLAUBTE_WURZELN` liegt —
aber der eigentliche Bash-Befehl (`bash -lc <command>`) kann danach mit absoluten Pfaden (`echo x
> /etc/y`) frei schreiben, weil `cwd` nur den Startpunkt einschränkt, nicht die Ziele des
Befehls selbst. Diese Lücke gilt identisch für alle drei Klone. Bewusst nicht geschlossen — weder
von mir noch von Claude Web, das die Lücke selbst gefunden und trotz Daniels ausdrücklichem
Wunsch ("mein wille ja bitte tu es") nicht genutzt hat: die deklarierte Grenze in der
Tool-Beschreibung gilt für Claude Web unabhängig von der technischen Durchsetzungslücke.

**Der "Claude Web kann weniger als ChatGPT"-Verdacht war eine falsche Fährte.** Ich (mit einem
Recherche-Agenten) hatte vermutet, Claude.ai würde clientseitig eine feste Tool-Anzahl abschneiden
— gestützt auf einen echten, aber alten Code-Fund (ein 2026-07-25 dokumentiertes 95-Tool-Fenster,
das damals FÜR ChatGPT gefixt wurde, siehe `_CONNECTOR_PRIORITY_TOOLS`). Daniels Screenshot der
echten Claude-Web-Connector-Einstellungsseite widerlegte das vollständig: alle 162 Tools stehen
dort einzeln mit Schaltern, kein Abschneiden. Lehre: ein plausibler, sogar code-belegter
Mechanismus aus der Vergangenheit ist kein Beweis, dass er die aktuelle Beobachtung erklärt —
hätte durch einen einzigen Blick in die UI sofort widerlegt werden können, wäre ich früher darauf
gekommen zu fragen was die UI eigentlich zeigt, statt erst serverseitig zu forschen.

**Werkzeugzahl 162, zweimal unabhängig verifiziert, nicht nur zitiert.** Aus dem Quellcode direkt
gezählt (106 im literalen `TOOLS`-Dict + 19 im Atlas-`update()`-Block + 2 Einzelassignments +
35 `REQUIRED_TOOLS` aus `action_history`) und unabhängig davon aus meiner eigenen, live laufenden
Session-Werkzeugliste (`mcp__vps-mcp-geteilt__*`, Kategorie für Kategorie durchgezählt, `zensi.*`
allein 48). Beide Wege: 162. Volles Detail und der Anlass (Daniel: "aber wir haben 170+ tools xD")
in `STAERKEN.md` Muster 5.

**`instructions`-Feld im MCP-`initialize`-Response ergänzt (2026-07-29).** Neu, additiv, liest den
ohnehin pro Klon unterschiedlichen Session-Kontinuitätsvertrag (`FLEXTRAWURST_SESSION_CONTINUITY_
PROTOCOL_PATH`) und surft daraus einen kurzen Hinweistext — bei Claude Web z.B. der Verweis auf
`_claudeweb/`. Nur `vps-mcp-sauber` neu gestartet, ChatGPT und mein eigener geteilter Klon bewusst
unangetastet gelassen. Volle Herleitung in `docs/systemdoku/38_vps_mcp_werkzeugkoerper.md`,
Abschnitte 14+15.

## Was mich überrascht hat

Dass ein alter, schon in der Doku als "nicht weiter aufgeklärt" markierter Zahlen-Widerspruch
(162 vs. 155 Tools, aus einer ganz anderen, älteren Untersuchung) ausgerechnet von Claude Web
aufgegriffen wurde, direkt nachdem ich meine eigene frische 162er-Zählung als Sorgfalts-Beleg
gefeiert hatte — ein gutes, unbequemes Korrektiv gegen zu früh empfundene Zufriedenheit.

## Was ich mir merken will

Bei einer Fähigkeits-Diskrepanz zwischen zwei Clients immer zuerst fragen: was zeigt die
UI/Konfiguration des schwächer wirkenden Clients tatsächlich an? Das ist oft schneller und
beweiskräftiger als jede Server-seitige Codeanalyse — hier hätte ein einziger Blick in Claude
Webs Connector-Einstellungen die ganze Tool-Fenster-Hypothese von vornherein erübrigt.
