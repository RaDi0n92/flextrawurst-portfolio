# Augen-und-Hände-Bridge — Spiegeldatei der Praxisprüfung

Stand: 2026-10-02
Zweck: Nachvollziehbare Rückschau auf die unabhängige Prüfung und die daraus
umgesetzten Bridge-/Harness-Reparaturen.

## Anlass

Claude legte eine ausdrücklich freiwillige, read-only Bitte unter
`/root/werkraum/_codex/von_claude_2026-10-02_skills_und_praxis_harness/` ab.
Die Lesekopie wurde vollständig gegen ihr Manifest geprüft. Die 25 dort
aufgeführten Prüfsummen stimmten. Der Ordner wurde nicht verändert.

Die fünf Fragen waren ein Einstieg, kein Auftragsschnitt:

1. Sind die Skills verständlich und knapp?
2. Trägt der Graph den Ablauf?
3. Wo könnten Spuren ohne sinnvolle Wirkung genügen?
4. Wird die Ansage wirklich in der Raute sichtbar?
5. Kommt ein frischer Agent nur mit dem Skill zurecht?

Die Prüfung ging darüber hinaus in Protokollgrenzen, Restart-Verhalten,
Locale-/Transportpfade, Testbarkeit und Dokumentation.

## Befunde, die behoben wurden

### Ansage war ein Versandbeleg, keine Körperquittung

Vorher wurde die Raute-Nachricht lokal als `raute` verbucht, obwohl der Körper
noch nicht bestätigt hatte, dass er sie angenommen hatte. Jetzt trägt die
Nachricht eine `request_id`; der Körper antwortet mit
`raute_tippen_ergebnis`. Timeout, Ablehnung, Not-Aus, Fokus- und Handfehler
werden als negativer Befund zurückgegeben. Erst ein positiver ACK öffnet die
Lesephase.

### Grobe Spur konnte konkrete Aktion ersetzen

Ein beliebiges `haende`-, `seed`- oder `loop`-Event durfte nicht mehr jede
Schrittbehauptung erfüllen. Das Szenario unterstützt deshalb
`contract_version: 2` mit geordneten, typisierten `belege`-Prädikaten. Sie
prüfen Befehl, Aktionsart, Ergebnis, Ressource, Partner-/Loop-Zustand und bei
Bildbelegen Frische und Zielbindung. Unbekannte Felder und leere Beleglisten
sind ungültig.

Ein Treffer öffnet weiterhin nur den Schritt. Die Wirkung bleibt eine eigene
Prüfung durch Bild und zwei Agentenurteile.

### Bildbelege waren zu leicht wiederverwendbar

Praxis-Ereignisse tragen nun Lauf-ID, Versuch-ID, Schritt, Phase, Zeitgrenze
und Ziel-ID. Ein frisches Bild wird nicht durch eine Datei-/synthetische Spur
ersetzt. Legacy-Diagnosen außerhalb eines v2-Laufs bleiben für vorhandene
Werkzeugtests lesbar; der v2-Belegprüfer bleibt streng.

### Ledger konnte still unvollständig werden

Das JSONL-Ledger wird geflusht und per `fsync` geschrieben. Fehler beim
Pflichtledger brechen den Schritt mit `ledger_nicht_geschrieben` ab. Eine
optionale Markdown-Projektion wird als `protokoll_hinweis` sichtbar, statt den
Lauf still zu verschönern.

### Neustart konnte einen physischen Schritt verschlucken

Läufe schreiben atomare Checkpoints mit restriktiver Berechtigung. Nach einem
Restart markiert der Dienst laufende Checkpoints als unterbrochen und verlangt
einen neuen Versuch; er behauptet keinen still fortgesetzten Klick.

### Abschluss konnte alles als bestanden klingen lassen

`abschluss()` trennt bestätigte Schritte, abweichende/fehlerhafte Urteile,
offenen Streit und `nicht_getestet`. Das Ergebnis `ok` bedeutet nur, dass kein
Vertragsverstoß gefunden wurde; es ist keine Welt- oder Runtime-Wahrheit.

## Skill- und CLI-Dokumentation

Der Praxistest-Skill beschreibt jetzt zusätzlich:

- `test vorflug <Partner>` als prüfbaren Vorflug;
- `test nicht_getestet "Grund"` als explizite Zurückstellung;
- Körper-ACK getrennt von sichtbarer Wirkung;
- typisierte `belege` in Contract-Version 2;
- `say` nicht als Ersatz für eine Praxis-Ansage.

Die Szenario-Referenz dokumentiert `contract_version`, Belegfelder,
`same_resource_as` und geschlossene `braucht`-Werte. `bridge.sh` leitet seinen
Repo-Pfad nun vom Skriptstandort ab und fällt erst danach auf die bekannten
Hostpfade zurück.

## Prüfung

Erfolgreich ausgeführt:

```text
python3 -m compileall -q src client_vps skills tests
git diff --check
20 Skill-/Harness-Dokumentationstests: OK
gezielte Suite aus Praxis, Belegen, Transport, Körper, Launcher und Skills: OK
beide Skills: 0 Fehler, 0 Hinweise
Claude-Lesekopie nach Abschluss: 25/25 Prüfsummen MATCH
```

Der vollständige Testlauf umfasste 1809 Tests mit 75 übersprungenen Tests.
Dabei traten vier Fehlassertionen und ein Fehler auf. Zwei Skill-Testfixtures
wurden anschließend an die neue, strengere Schnittstelle angepasst und liefen
grün. Drei Befunde in Terminal-Discovery-Tests bleiben außerhalb dieser
Reparatur offen; deren Implementierung wurde nicht verändert. Für diese
Befunde wird hier weder ein Fix noch eine bewiesene Ursache behauptet.

Die gezielten Diensttests verwenden echte temporäre Kapsel-, Seed- und
Loop-Dienste. Sie prüfen Ressourcenidentität, Daniels Freigabeereignis,
Partnerzustellung und das Ende nach drei Loop-Durchläufen. Freigaben in diesen
Tests sind ausdrücklich Fixtures, keine Owner-Entscheidungen.

## Bewusste Grenzen

- Der Claude-Ordner blieb Lesekopie.
- Es wurde kein Produktionsdienst gestartet oder verändert.
- Eine fehlende echte Raute-Rückmeldung wird nicht als Erfolg simuliert.
- `say` und manuell eingetragene Rohspuren gelten nicht als typisierte
  v2-Aktionsbelege.
- Ein erfolgreicher Harness-Lauf behauptet keine aktuelle Runtime-Wirkung.
- Eine native Desktop-Probe mit Daniel und zwei tatsächlich verbundenen Agenten
  wurde in diesem Reparaturpass nicht durchgeführt. Körper-ACK und Agentenurteil
  ersetzen keine unabhängige pixelbasierte Prüfung der Ansage.
- Menübedienung bleibt ohne explizite Freigabe zurückgestellt.

## Relevante Implementierungen

```text
src/augen_haende_bridge/praxis/belege.py
src/augen_haende_bridge/praxis/lauf.py
client_vps/praxis_dienst.py
client_vps/terminal_launcher.py
src/augen_haende_bridge/koerper/anwendung.py
src/augen_haende_bridge/transport.py
```

Diese Spiegeldatei ist eine Orientierung. Für konkrete Fehler, Hashes und
Einzelprüfungen bleiben Quellcode, Tests und das unveränderte Claude-Paket die
maßgeblichen Belege.

## Abschlussnachtrag

Die finale gezielte Suite umfasst 172 Tests, einschließlich direkter Körper-ACK-
Gegenproben und Stop-/Checkpoint-Regressionsprüfung. Körper-Quellcheck: vier
Muster sauber. Beide Skill-Creator-Validatoren bestehen. Graphify fehlt.
Die Rohbelege stehen unter `tests/evidence/PRAXIS_REPAIR_2026-10-02_*`.
Kein nativer Desktop-Test, keine Dienstinstallation und kein Neustart durchgeführt.
