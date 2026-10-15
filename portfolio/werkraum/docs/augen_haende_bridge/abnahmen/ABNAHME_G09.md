# Abnahme G09 — Multi-Agent-Orchestrierung

Stand: 2026-10-02. Belege: `.unlazy/g06-g14/gates/leaf-1.3.1.md`, `leaf-1.3.2.md`, `node-1.3.md`. Code: `koerper/agentenregister.py`, `adapterwege.py`, `client_vps/terminal_launcher.py`, `client_vps/bridge_cli.py`.

## Was gebaut und auf dem VPS belegt ist

* **Register** (reine Logik, 23 Tests): jeder Agent ist eine von der Bridge gestartete Sitzung (Terminal-ID). Zwei Sitzungen desselben Stroms bleiben zwei Agenten („Codex“, „Codex 2“). Gruppen (bis 16 je Agent),
  Eltern/Kinder, Aufträge mit Status, Fähigkeitsmatrix je Strom, Speichern und tolerantes Laden (geladene Agenten gelten als beendet).
* **Nachrichten** an einen Agenten oder eine Gruppe werden wie getippt zugestellt (Text, Pause, Enter, je Sitzung nacheinander). Schutz vor Schleifen: nie an sich selbst, nie an nur gemeldete Kinder,
  Dubletten (5 s) und Rate (10 in 10 s) werden abgewiesen, eine Zustellung löst von selbst nichts aus.
* **Delegation**: `auftrag` tippt den Auftrag samt Meldeweg in die Sitzung des Empfängers. Der Status steigt nur, wenn der **Empfänger** ihn meldet (`gesendet → angenommen → laeuft → fertig/fehler`), nie zurück;
  Ergebnis und Unsicherheit stehen im Auftrag. Beide Beteiligte dürfen abbrechen, Dritte nicht.
* **Subagenten**: `kind NAME` meldet einen Unteragenten im eigenen Prozess. Er ist sichtbar, aber **nicht steuerbar** (kein Ansprechen, Anhalten, Beenden, Delegieren) und wird so gekennzeichnet.
* **Pause/Fortsetzen**: `terminal_steuern` (nur vom Desktop, der das Terminal zeigt) hält die ganze Prozessgruppe an (SIGSTOP, bei Docker-Orten auch im Container), Fortsetzen mit SIGCONT. Gemessen: Prozesszustand `T`, die
  PTY puffert Eingaben, nach dem Fortsetzen werden sie abgearbeitet. Beenden eines pausierten Agenten schickt SIGCONT mit SIGHUP. Der Zustand `paused` geht an Relay, Starter, Körper (Menü „pausieren/fortsetzen“).
* **Neu starten und Anbinden sind getrennt**: `terminal_start` erzeugt eine Sitzung, `terminal_attach` nimmt eine bestehende wieder auf (Verlauf wird noch einmal gespielt, keine neue Sitzung; auch bei pausierten). Fremde,
  nicht von der Bridge gestartete Terminals werden nicht angebunden (BE01).
* **Adapterwege** (`adapterwege.py`, Messung `probes/adapterweg_tui.py`, 2026-10-02): alle Ströme laufen über dieselbe PTY. Am echten Programm gemessen (Marke ohne Enter getippt, es entsteht keine Anfrage):

  | Strom | Programm | Ergebnis |
  |---|---|---|
  | codex | `codex` 0.159.2 | belegt: Text erscheint im Eingabefeld |
  | opencode | `opencode` 1.18.34 | belegt: Text erscheint im Eingabefeld |
  | gemini (`agy`) | `agy` 1.2.14 | Text erreicht die Eingabe, die Anzeige mischt die Statuszeile hinein (zerstückelt) |
  | claude | `claude` 2.1.287 | im Probelauf stand der Ordner-Vertrauensdialog: Tippen kam dort nicht an; nach Bestätigen nicht gemessen |
  | kimi, glm | — | auf diesem Rechner nicht installiert: **offen** |

  Kopflose Aufrufe (`claude -p`, `codex exec`, `opencode run`, `agy -p`) stehen nur, weil die Hilfe sie nennt; **keiner wurde ausgeführt** (jeder wäre eine echte Modell-Anfrage auf Daniels Konto).
* Technische Festlegung: „running“ und „exited“ eines Terminals werden unter einem Schloss gemeldet, in dieser Reihenfolge.

## Was nicht belegt ist (offen)

* Pause/Fortsetzen **in Docker-Orten (vd1/vd2)**: der Weg über `docker exec` ist wie bei SIGHUP vorhanden, auf diesem Rechner aber ohne Docker nicht gelaufen.
* Claude hinter dem Vertrauensdialog, Kimi und GLM: nicht gemessen. Bei Claude ist die Startnachricht-Ursache aus früheren Sitzungen weiter unbelegt.
* Die Oberfläche (Menüeintrag, Zustandsanzeige „pausiert“) ist gegen Attrappen geprüft, nicht nativ.
* Subagenten: die Bridge kennt nur, was der Agent selbst meldet. Eine automatische Erkennung von Unteragenten je Runtime gibt es nicht (nicht behauptet).
