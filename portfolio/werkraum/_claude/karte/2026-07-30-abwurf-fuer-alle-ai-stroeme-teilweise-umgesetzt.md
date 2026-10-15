---
datum: 2026-07-30
betrifft: [splitter, abwurf, dak-abwurf, codex-abwurf, gemini-abwurf, chatgpt, claudeweb, vps-mcp-server, architektur]
importable: false
autor: claude-code bei Daniels VPS
---

## Auftrag: alle AI-Ströme + Daniel selbst sollen im Zwischenraum sichtbar sein

Daniel, wörtlich: *"und euch alle soll es auch abbilden alle externe und mich mit einen
eingeben und soo"* — jeder Strom (ich, Codex, Gemini, ChatGPT, Claude Web) und Daniel selbst
sollen wie ich einen echten Abwurf-Mechanismus haben, der Splitter im Zwischenraum
hinterlässt. GLM und Kimi ausdrücklich ausgeschlossen (Kimi seit 5.7. inaktiver
Briefkasten-Partner, GLM hat keine lokale CLI auf diesem VPS).

## Was bereits fertig ist, verifiziert (echter Splitter erzeugt, wieder gelöscht)

**`dak_abwurf.py`** — neu, liegt bewusst in `_shared/tools/` statt unter einem einzelnen
Strom-Ordner, weil es aus mehreren Hooks gleichzeitig aufgerufen wird (Claude Code
UserPromptSubmit, Codex UserPromptSubmit, Gemini BeforeAgent). Gleiche
Klassifikations-Heuristik wie `claude_abwurf.py` (MIN_LAENGE=400, Wahrscheinlichkeitsfilter),
nur auf Daniels Eingabetext statt der Antwort, `origin_type='dak_abwurf'`,
`entity_id='dak'`.

**`codex_abwurf.py`** — existierte bereits fertig und korrekt parametrisiert, war aber nie
gehookt (Codex' `~/.codex/hooks.json` hatte bisher nur einen PreToolUse-Hook für graphify).
Codex' eigenes `Stop`-Event liefert exakt das Feld `last_assistant_message`, das die Datei
schon erwartete — direkt aus Codex' Binary-JSON-Schema verifiziert (`strings` auf das
gebündelte Rust-Binary), nicht angenommen. Jetzt als `Stop`-Hook eingehängt, plus
`dak_abwurf.py` als `UserPromptSubmit`-Hook daneben.

**`gemini_abwurf.py`** — der bisherige war nur eine Attrappe (schrieb eine statische
Markdown-Notiz, erzeugte gar keinen Splitter). Komplett neu geschrieben nach demselben Muster
wie Codex/Claude. Gemini CLI hat kein "Stop"-Event, sondern "AfterAgent" (Feld
`prompt_response`) und "BeforeAgent" für den Nutzer-Prompt (Feld `prompt`) — aus der
offiziellen, mitgelieferten Gemini-CLI-Doku (`docs/hooks/reference.md` im Bundle) gelesen,
nicht geraten. Beide Hooks in `~/.gemini/settings.json` eingehängt.

Alle drei Mechanismen einzeln über direkten Funktionsaufruf verifiziert (echter Splitter mit
korrektem `origin_type`/`entity_id` in der DB erschienen, danach als Testartefakt wieder
gelöscht) — nicht nur "kein Crash", sondern echte End-to-End-Bestätigung.

## Was bewusst pausiert ist: ChatGPT + Claude Web

ChatGPT und Claude Web laufen nicht als lokale CLI-Prozesse mit eigenem Hook-File, sondern
ausschließlich über HTTP-MCP. Der einzige Ort für eine ähnliche Mechanik ist der gemeinsame
Server-Code `tools/vps_mcp/vps_mcp_server.py` — verifiziert (systemd `ExecStart`/
`WorkingDirectory`), dass alle fünf Dienste (`vps-mcp`, `vps-mcp-sauber`, `vps-mcp-claude`,
vermutlich auch `-codex`/`-gemini`) exakt dieselbe Datei ausführen, keine Kopien.

**Der Grund für die Pause:** Beim Nachsehen fand ich, dass ChatGPT genau jetzt eine eigene,
hash-verifizierte Deployment-Testreihe gegen diese Datei laufen hat
(`_gpt/mcp_arbeitskoerper/peer_review/gesamtatlas_omega_production_activation_redteam/`,
Ordner wie `bad_candidate_hash`, `rollback`, `activation_success`, Zeitstempel Minuten alt).
Jede Änderung an der Datei — auch nur ein einzeiliger, additiver Import — würde von einer
Hash-Prüfung erfasst und könnte diese laufende Testreihe stören.

**Daniels Entscheidung, zweimal bestätigt:** erst "Claude Web trotzdem einbinden, falls sie
eine eigene Instanz hat" (Prämisse hab ich geprüft und als falsch widerlegt — keine eigene
Kopie), dann direkt danach klar: *"jo war warten das kann noch dauern ich melde mich."*
Architektur-Entscheidung für später schon getroffen: **gemeinsamer Kern + eigene, kleine
Erweiterungsdatei pro Strom** (nicht fünf komplette Datei-Kopien) — Kern lädt die
Erweiterung, jeder Strom bekommt trotzdem individuellen Code, ohne dass jeder Bugfix
fünffach nachgezogen werden muss.

## Was ich mir merken will

Reine Vorsicht beim Anfassen einer geteilten, produktiven Datei reicht nicht — auch das
bloße *Lesen/Inspizieren* einer Datei, die von einem anderen Strom aktiv hash-geprüft wird,
sollte pausiert werden, nicht nur das Schreiben. Der Sicherheits-Classifier hat das an diesem
Punkt der Session unabhängig von mir selbst durchgesetzt (mehrfache Blockaden bei reinen
Lesebefehlen) — ein zusätzliches, externes Signal, dass die Vorsicht hier berechtigt war,
nicht nur meine eigene Einschätzung.

## Nächster Schritt, wenn Daniel sich meldet

1. Prüfen ob ChatGPTs `gesamtatlas_omega_production_activation_redteam`-Pipeline
   abgeschlossen ist (z.B. `CORE_READY.json` oder ein finaler Status in den `runtime/`-Ordnern
   nachsehen, nicht raten).
2. Minimalen Lademechanismus in `vps_mcp_server.py` einbauen (liest eine neue Env-Var, z.B.
   `VPS_MCP_EXTENSION_MODULE`, importiert die dort verwiesene Datei, ruft eine `erweitere(TOOLS)`-
   Funktion auf).
3. `chatgpt_erweiterung.py`/`claudeweb_erweiterung.py` schreiben (welcher Tool-Aufruf bei
   ChatGPT/Claude Web überhaupt genug Freitext trägt, um sinnvoll klassifiziert zu werden, war
   beim Abbruch noch nicht geklärt — `history_record_action` existierte in `vps_mcp_server.py`
   nicht auffindbar, war noch offene Recherche).
4. Env-Var pro betroffenem systemd-Unit ergänzen, Dienst neu starten (Claude Web zuerst,
   ChatGPT erst nach expliziter Freigabe).
