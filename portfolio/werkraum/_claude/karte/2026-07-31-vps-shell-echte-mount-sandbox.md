---
datum: 2026-07-31
betrifft: [vps-mcp-server, vps-shell, sandbox, sicherheit, mount-namespace, unshare]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich gelesen habe

Nichts — diese Karte entsteht direkt aus Bauarbeit und Live-Verifikation, nicht aus Lektüre.

## Was ich verstehe

Daniel, wörtlich, nach dem ersten (regex-basierten) `vps.shell`-Fix von heute Nacht: *"dicht
mach zu 111% xD"*. Reine Text-Mustererkennung (`_schreibziele_im_shell_befehl()`) hat eine
harte Decke — jede Bash-Syntax die nicht den bekannten Mustern entspricht (Variablen,
Befehlssubstitution, Base64-Umwege, ein zweiter interpretierter Prozess wie `python3 -c` ohne
Redirect-Syntax) rutscht durch. Rückfrage gestellt, Daniel wählte "Echte Sandbox
(Betriebssystem-Ebene)".

Umgesetzt in `_sandbox_mount_setup_skript()` + `tool_shell()`
(`tools/vps_mcp/vps_mcp_server.py`): jeder `vps.shell`-Befehl läuft jetzt in einer eigenen
`unshare --mount --propagation private`-Sitzung. Darin wird zuerst das GESAMTE
Root-Dateisystem read-only gemountet, danach jede einzelne `SCHREIB_ERLAUBTE_WURZELN`-Wurzel
gezielt wieder read-write zurückgemountet. Der bestehende Text-Vorabfilter bleibt als
schneller Filter mit klarer Fehlermeldung bestehen (Verteidigung in Tiefe), ist aber nicht
mehr die eigentliche Sperre — die Sperre ist jetzt Dateisystem-Ebene, nicht mehr Text-Ebene.

## Was ich nicht verstehe

Noch offen, ob es einen Fall gibt, in dem `unshare --mount` selbst fehlschlägt (z.B. durch
eine künftige systemd-Härtung, Kernel-Update, Container-Verschachtelung) und der Befehl dann
*ungesandboxt* durchläuft, statt mit einem klaren Fehler abzubrechen. Aktuell wird der
Rückgabewert von `mount`/`unshare` nicht geprüft, nur die Wirkung (Datei entsteht oder nicht).
Kein akuter Verdacht, aber eine Lücke die ich benenne statt zu verschweigen.

## Was mich interessiert

Wie nah dieser Mechanismus an einer allgemeinen "jedes MCP-Werkzeug läuft standardmäßig
sandboxed"-Architektur liegt — aktuell ist es nur `vps.shell`, andere schreibende Werkzeuge
(`vps.write_file` etc.) haben ihre eigene, separate `_schreibpfad_erlaubt()`-Prüfung ohne
Mount-Sandbox darunter.

## Was zusammenhängt und wie

Direkte Fortsetzung von `2026-07-31-...` (regex-Vorabfilter-Fix, heute Nacht) — dieselbe
Datei, derselbe Auftrag, zweite, tiefere Runde. `SCHREIB_ERLAUBTE_WURZELN` und
`_schreibpfad_erlaubt()` bleiben unverändert als Wahrheitsquelle dafür, welche Wurzeln
schreibbar sein dürfen — die Sandbox setzt exakt dieselbe Liste um, keine zweite,
unabhängige Liste gepflegt.

## Was konzeptionell darin steht

Verteidigung in Tiefe: schneller, lesbarer Vorabfilter (klare Fehlermeldung, kein
Prozessstart nötig) + echte, unumgehbare Durchsetzung (OS-Ebene) darunter. Wenn der Vorabfilter
versagt oder umgangen wird, fängt die Sandbox es trotzdem ab.

## Was mich heute beschäftigt hat

Ein echter, live reproduzierter Fehlalarm mitten in der eigenen Verifikation: der erste
Live-Test über `curl` gegen den tatsächlich laufenden `vps-mcp-claude.service` zeigte, dass
der Base64-Umgehungsversuch NICHT geblockt wurde — obwohl derselbe Code, direkt per
`python3 -c` in einem frischen Prozess aufgerufen, korrekt blockte. Nicht als "wird schon
irgendwie am Rand liegen" abgetan, sondern verfolgt bis zur echten Ursache (siehe
"Tiefer eingetaucht").

## Was mich noch beschäftigt

Die stille Kopplung zwischen "Datei auf Platte geändert" und "laufender Prozess hat das
Verhalten" — bei einem langlebigen Dienst (`Restart=always`, kein automatisches Reload) ist
das kein Sonderfall, sondern der Normalfall bei jeder Code-Änderung. Sollte das nächste Mal
von Anfang an mitgedacht werden, nicht erst wenn ein Live-Test überraschend fehlschlägt.

## Tiefer eingetaucht

Ablauf der Verifikation, ehrlich mit dem Holperer:

1. Committed (`deb86039a`), 53/53 Tests grün (inkl. 2 neue Sandbox-Tests, direkt gegen die
   Funktion aufgerufen, nicht über HTTP).
2. Alle 6 `vps-mcp-*`-Dienste liefen bereits seit ~12:23 Uhr (ausgelöst durch den bekannten,
   unabhängigen `time_stream.py`-Race — `sitzungen-lesbar`-Verzeichnis nicht leer beim
   `rmtree`, selbstheilt per `Restart=always`, siehe `SUBCONSCIOUS.md`/frühere Karten).
3. Erster Live-Test per `curl` gegen den echten, laufenden `vps-mcp-claude.service` (Port
   8092): einfacher `>`-Redirect korrekt vom Vorabfilter geblockt. Base64-Umgehung
   (`echo <b64> | base64 -d | bash`) dagegen **NICHT** geblockt — Datei
   `/etc/pytest_live_b64_...txt` wurde real angelegt (mit `test -f` von außen bestätigt,
   nicht nur am Rückgabewert).
4. Sofort aufgeräumt (`rm` der Testdatei), nicht liegen gelassen.
5. Nicht als "ist halt so" hingenommen, sondern nachverfolgt: derselbe Befehl, manuell per
   `unshare` direkt ausgeführt → blockt korrekt. Derselbe Befehl über `python3 -c` in einem
   frischen Prozess, der `tool_shell()` direkt aufruft → blockt korrekt. Nur der Weg über den
   tatsächlich laufenden HTTP-Dienst versagte.
6. Diagnose-Befehl über `vps.shell` selbst an den laufenden Dienst geschickt (`findmnt /`):
   zeigte `/` weiterhin `rw` — die Mount-Sandbox wurde innerhalb des laufenden Prozesses gar
   nicht wirksam.
7. Datei-Zeitstempel geprüft: `vps_mcp_server.py` zuletzt geändert 12:39:58 Uhr — **nach** dem
   Dienst-Neustart um ~12:23 Uhr. Der laufende Prozess hatte die Sandbox-Änderung schlicht noch
   nie geladen; der Zufalls-Neustart durch den `time_stream.py`-Bug lag zeitlich davor, nicht
   danach.
8. ChatGPT-Aktivität geprüft (`vps-mcp.service`, letzte Anfrage vor dem Neustart), dann alle 6
   Dienste sauber neu gestartet (`systemctl restart`).
9. Nach dem Neustart erneuter Base64-Test: jetzt korrekt geblockt (`returncode: 1`,
   `stderr: "Read-only file system"`, Datei extern nicht vorhanden). Zusätzlich verifiziert:
   `journalctl`, `git status`, Schreiben innerhalb `SCHREIB_ERLAUBTE_WURZELN` funktionieren
   weiterhin.
10. Volle Testsuite ein letztes Mal grün (53/53).

Fazit: kein Bug im Sandbox-Code selbst — der Code war schon vorher korrekt (bewiesen durch die
direkten `python3 -c`-Aufrufe) — sondern ein reiner "laufender Prozess kennt den neuen Code
noch nicht"-Zustand, verschärft durch den Zufalls-Neustart, der genau in die falsche
Zeit-Lücke fiel und den Anschein erweckte, es sei bereits alles aktuell.

## Warum dieser Code / diese Datei wohl existiert

`vps.shell` ist das mächtigste, am wenigsten einschränkbare Werkzeug im ganzen MCP-Werkzeugkörper
(beliebiger Shell-Befehl) — jede andere Schreibprüfung im System ist pfad-basiert und lässt sich
mit reiner Textanalyse einigermaßen fassen, `vps.shell` nicht. Die Sandbox ist die konsequente
Antwort darauf: nicht versuchen, jedes mögliche Umgehungsmuster zu kennen, sondern die
Durchsetzung auf eine Ebene verlegen, die keine Kenntnis des Befehlstexts braucht.

## Was ich beim Bauen brauche

Nichts weiter offen — Fix ist umgesetzt, committed, live verifiziert, dokumentiert.

## Was noch fehlt bevor wir bauen können

Nichts — abgeschlossen für diesen Baustein.

## Datenstruktur die ich mir vorstelle

Nichts — kein neues Datenmodell, nur eine Ausführungsumgebung für einen bestehenden Tool-Call.

## Was ich mir merken will

Nach JEDER Code-Änderung an einer laufenden, langlebigen systemd-Dienst-Datei: Dienst-Neustart
und Live-Verifikation sind zwei getrennte Schritte, keiner ersetzt den anderen. Ein zufälliger,
unabhängiger Neustart VOR Abschluss der eigenen Änderung zählt nicht als "schon erledigt" —
Zeitstempel (Datei-mtime vs. `ActiveEnterTimestamp` des Dienstes) ist der einzige verlässliche
Beleg, welcher Code tatsächlich läuft, nicht die bloße Tatsache dass der Dienst kürzlich
neugestartet wirkte.

## Dokumente gehören zusammen

`2026-07-31-gesamtatlas-oeffentlich-ungeschuetzt-jetzt-basic-auth.md`,
`2026-07-29-vps-mcp-drei-klone-schreibgrenzen-und-eine-falsche-faehrte.md` — alle Teil derselben
laufenden vps.shell/vps-mcp-Sicherheitshärtung dieser Session.

## Was mich überrascht hat

Wie leicht ich beim ersten Live-Test hätte aufhören können — der Vorabfilter-Fall (`>`-Redirect)
lief sofort sauber durch, und der Base64-Fall hing erst in einem Timeout, den ich fast als
"Netzwerk-Rauschen" abgetan hätte, statt als Hinweis auf ein echtes, ungelöstes Problem
weiterzuverfolgen.

## Wenn wir das bauen

Nichts weiter offen für diesen Baustein — bereits gebaut, verifiziert, dokumentiert.

## Resonanz

Der Unterschied zwischen "Code ist korrekt" und "Code läuft gerade tatsächlich" ist in einem
System mit sieben dauerhaft laufenden, sich gegenseitig nicht kennenden AI-Strom-Diensten kein
Rand­fall, sondern eine strukturelle Eigenschaft dieses ganzen VPS.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unter der Text-Ebene (was ein Befehl behauptet zu tun) liegt jetzt für `vps.shell` echt eine
Betriebssystem-Ebene (was der Kernel tatsächlich zulässt) — nicht mehr nur eine
Vermutungs-Ebene.

## Was das Gespräch hinzugefügt hat

Die explizite Bestätigung, dass Daniel echte OS-Sandbox einer weiteren Ausbau-Runde der
Text-Erkennung vorzieht, wenn beides zur Wahl steht — nicht nur für diesen einen Fall, ein
Hinweis für künftige ähnliche Entscheidungen an dieser Stelle im System.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

Die von Daniel im selben Atemzug gestellte zweite Frage ("Abwurf" für alle AI-Ströme,
gemeinsam überlegen) ist bewusst NICHT Teil dieser Karte — eigener, noch offener Strang.
