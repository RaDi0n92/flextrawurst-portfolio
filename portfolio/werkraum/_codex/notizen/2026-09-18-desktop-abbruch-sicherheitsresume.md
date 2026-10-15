---
datum: 2026-09-18
betrifft: [desktop-abbruch, sicherheitsfix, astra, luna, dienstschluessel, service-isolation]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe die Codex-Notizen unter `/root/werkraum/_codex/notizen/`, die importierte Claude-Notizgeschichte, `/root/werkraum/_codex/WERKRAUM_KARTE.md`, die letzten Zeilen von `/root/werkraum/_codex/RESONANZFELD.md`, den Briefkasten und die Delta-Spur gelesen. Die jüngste Sicherheitsgeschichte ist nicht die Blender-Spur: Sie läuft über Empfangswiderruf, Dienstrechte, getrennte Dienstschlüssel und zuletzt den Einsammel-Identitätsvertrag.

In den beiden Codex-Sitzungsdateien unter `/config/.codex/sessions/2026/09/18/` war die Trennung sichtbar. Die Sitzung mit `10-07` gehört zum Blender-/Bagger-Anschluss; die Sitzung mit `10-06` ist die Sicherheitsfix-Fortsetzung. Der Sicherheitszweig endet fachlich bei Commit `15e2a85db7`, der Reparatur in `/root/werkraum/welt/api.py` und dem Nachweis `/root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md`.

Die Hostspur sagte wörtlich: „Received disconnect from 127.0.0.1 port 33900:11: disconnected by user“. Danach folgten „Session 16465 logged out“ und „Removed session 16465“. In `/root/werkraum` meldete `virtuellerdesktop1` keinen Containerneustart und `OOMKilled=false`; Selkies und Plasma wurden innerhalb des laufenden Desktop-Stacks neu gestartet.

## Was ich verstehe

Der Desktop ist nicht wegen eines VPS-Reboots verschwunden. Der direkteste belegte Auslöser ist der Abbau der lokalen SSH-Session `16465` um 09:54:49 CEST; wer diese Trennung ausgelöst hat, ist aus dem Log nicht beweisbar. Die Session-Scope-Auflösung riss die darin laufenden Terminals und Prozesse mit, worauf `svc-de` den Desktop mehrfach neu aufbaute.

Die Sicherheitsarbeit hat den Abbruch überlebt. `welt-api.service` läuft seit 09:50:23, `welt-bruecke.service` läuft weiter, `/health` antwortet `200`, geschützte Dienstverwaltungsrouten antworten ohne Token `401`. Die Ed25519-Schlüssel werden im laufenden API-Prozess aus `/root/werkraum/welt/.service_crypto/` geladen.

Die zehn Dienste besitzen getrennte Signieridentitäten, alte gemeinsame HS256-Diensttokens sind gesperrt, passive Websocket-Empfänger prüfen Rechte erneut, und der Splitter-Einsammelpfad unterscheidet explizit Mensch, Wesen und Dienst. Die gemeinsame Root-Ausführung ist aber noch keine Isolation.

## Was ich nicht verstehe

Ich weiß nicht, ob ein Watchdog, ein lokaler Agent, die Desktop-Verbindung oder ein manueller Abbau die SSH-Trennung auf `127.0.0.1:33900` ausgelöst hat. „disconnected by user“ ist die Sicht von `sshd`, nicht der Beweis einer menschlichen Bedienung.

Ich weiß nicht, warum der parallele Blender-Anschluss und der Sicherheitsanschluss zeitgleich eigene Git-Backup-Commits erzeugten. Die Spuren sind inhaltlich getrennt, aber der gemeinsame Git-Index bleibt eine reale Kollisionsstelle.

Ich weiß außerdem nicht, warum `/root/werkraum/geni/inbox_antworten_watcher.py` aktuell nur bis zur Dokumentation in Zeile 70 reicht. Der zugehörige systemd-Dienst läuft deshalb mit `Restart=always` alle 15 Sekunden in einen Dauerloop; das ist ein eigener Fehler, nicht der nachgewiesene direkte Desktop-Auslöser.

## Was mich interessiert

Mich interessiert die fehlende Kette zwischen lokaler SSH-Trennung und dem Prozess, der sie veranlasst hat. Dafür bräuchte es den Besitzer des Ports `33900`, die Selkies-/Desktop-Supervisor-Konfiguration und ein Ereignis unmittelbar vor `09:54:49`.

Mich interessiert außerdem, ob die Root-/DB-Isolation als begrenzte erste Schicht gebaut werden kann: zuerst dauerhafte Dienste mit eigenen Unix-Identitäten und nur den nötigen Dateien, danach PostgreSQL-Rollen und Grants, ohne die laufenden Wesenpfade pauschal umzuschreiben.

## Was zusammenhängt und wie

SSH-Session-Abbau → `systemd-logind` entfernt Session-Scope → Desktop-Kinder sterben → `svc-de` startet Selkies/Plasma neu. Das ist die konkrete Abbruchkette.

Der GENI-Antwort-Watcher → beendet sich wegen fehlendem Hauptlauf → systemd startet ihn alle 15 Sekunden → unnötiger Start-/Logdruck und potenzieller Lastverstärker. Diese Kette ist plausibel belastend, aber nicht als Ursache der SSH-Trennung bewiesen.

Dienstschlüssel → begrenzen die Identitätsimitation auf den jeweiligen Signierer → Root-Prozesse können weiterhin alle privaten Dateien und Schlüssel lesen → echte Isolation braucht Unix-/Systemd- und DB-Grenzen zusätzlich.

## Was konzeptionell darin steht

Sicherheit ist hier nicht nur ein gültiges Token. Sie ist eine Kette aus Identität, Herkunft, aktueller Datenbankberechtigung, Prozessgrenze und sichtbarem Nachweis. Ein einzelner Schlüssel darf nicht die ganze Welt repräsentieren; ein einzelner Root-Prozess darf aber auch nicht weiterhin alle Schlüssel verkörpern.

Der Desktop-Abbruch zeigt dieselbe Schichtfrage auf Betriebsebene: Eine sichtbare Oberfläche ist kein eigener Prozessraum. Wenn ihre Session-Scope-Grenze fällt, fällt das Sichtbare mit. Dauerhafte Arbeit muss daher außerhalb des Desktop-Lebenszyklus liegen.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, wie schnell ein scheinbar totaler Verlust — alle Terminals weg — durch Git, Session-JSONL, Journal und laufende Dienstzustände in zwei getrennte Geschichten zerfällt. Es war kein verlorener Sicherheitsstand, sondern ein verlorener Bedienraum.

Mich hat auch beschäftigt, dass ein laufendes Backup eines anderen Stroms den gemeinsamen Index sperrte. Der Werkraum ist gleichzeitig Arbeitsfläche und lebender Mehrstrom-Ort; ein Backup-Commit ist deshalb nicht automatisch eine fachliche Übergabe.

## Was mich noch beschäftigt

Offen bleibt die Herkunft des SSH-Abbaus. Offen bleibt auch, ob der `geni-inbox-antworten.service`-Loop seit seiner Entstehung bereits unnötige Last erzeugt und welche anderen Units ähnlich unvollständige oder sofort beendende Programme starten.

Die Root-/DB-Isolation ist die eigentliche nächste Sicherheitskante. Sie darf nicht als kosmetische `User=`-Zeile gebaut werden, solange Schlüsselpfade, Schreibpfade, Datenbankrollen und laufende Herkunftsgrenzen nicht einzeln kartiert sind.

## Tiefer eingetaucht

Die ausgewählten 38 Sicherheits- und Websocket-Tests sind grün, wenn `test_service_keys.py` vor den Tests läuft, die PyJWT bereits ohne den separaten Kryptopfad importieren. Der erste gemischte Aufruf erzeugte neun falsche Setup-Fehler durch Importreihenfolge; die isolierte Dienstschlüssel-Suite und die dokumentierte Reihenfolge bestehen. Das ist eine Testhygiene-Spur, kein Nachweis eines Live-Ausfalls.

Die laufende API trägt die Kryptobibliothek aus `/root/werkraum/welt/.service_crypto/`; im Prozess-Mapping von PID `3168895` ist `_rust.abi3.so` sichtbar. Die Schlüsseldateien unter `/root/werkraum/.agent/service-keys/` sind root-eigen, 0600, und der Schlüsselbaum ist 0700.

## Wie sich dieser Tag / diese Session angefühlt hat

Erst wie ein Absturz in völlige Unordnung, dann wie eine forensische Linie: 09:54:49, Session 16465, Scope-Abbau, Desktop-Neuaufbau. Die Erleichterung kommt nicht aus einer schönen Erklärung, sondern daraus, dass die Sicherheitsfixes nicht mitgerissen wurden.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/welt/service_tokens.py` und `/root/werkraum/welt/service_token_verifier.py` existieren, damit Dienste benannt und begrenzt handeln können, ohne den menschlichen JWT-Vertrag zu übernehmen. `/root/werkraum/welt/api.py` trägt die konkrete Route, an der diese Herkunftsgrenze wirksam wird.

`/root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md` existiert als technische Haltelinie: Er behauptet nicht die ganze Sicherheit, sondern nennt die erreichte Ed25519-Trennung und die offen gebliebene Root-Grenze.

## Was ich beim Bauen brauche

Ich brauche eine Unit-für-Unit-Karte mit Dienst, Unix-User, Gruppen, Arbeitsverzeichnis, gelesenen Dateien, geschriebenen Verzeichnissen, Ports, Datenbankrolle und Schlüsselpfad. Ich brauche außerdem einen Rollback, der nur den jeweils betroffenen Dienst berührt.

Ich brauche Tests für „falscher Unix-User“, „falsche DB-Rolle“, „privater Schlüssel nicht lesbar“, „API bleibt erreichbar“ und „Desktop darf sterben, Dienst bleibt“. Kein breiter Systemd-Umbau ohne diese Rücklese.

## Was noch fehlt bevor wir bauen können

Es fehlt die Entscheidung, welche Dienste zuerst aus `root` herausgelöst werden dürfen. Es fehlt die Bestandsaufnahme der tatsächlichen Datei- und DB-Zugriffe jedes Kandidaten. Es fehlt eine sichere Wartungsgrenze, damit ein kontrollierter Unit-Test nicht wieder die sichtbare Desktop-Session als Träger benutzt.

Separat fehlt eine explizite Reparaturentscheidung für `/root/werkraum/geni/inbox_antworten_watcher.py` und die dazugehörige Unit. Diese Reparatur gehört nicht still in den Sicherheitsfix.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Jeder Dienst ist ein eigener, kleiner Körper: eigene Identität, eigene Hände, eigener Schlüssel, eigener DB-Blick. Zwischen den Körpern gibt es nur ausdrücklich benannte Türen. Der Desktop ist eine beobachtende Oberfläche, nicht der Ort, an dem die Körper leben müssen.

**Code-Skizze**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ServiceBoundary:
    name: str
    unix_user: str
    unix_group: str
    read_paths: tuple[str, ...]
    write_paths: tuple[str, ...]
    db_role: str
    allowed_ports: tuple[int, ...]
    key_dir: str
```

```sql
CREATE TABLE service_db_grants (
    service_name text PRIMARY KEY REFERENCES auth_service_principals(name),
    db_role text NOT NULL,
    allowed_schema text[] NOT NULL,
    allowed_tables text[] NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    meta jsonb NOT NULL DEFAULT '{}'
);
```

## Was ich mir merken will

Der Sicherheitsanschluss ist `15e2a85db7`, nicht die Blender-Spur. Der Desktop-Abbruch war ein Session-Abbau, kein Reboot. Dienstschlüssel sind live; Root-/DB-Isolation ist offen. Niemals die offene Root-Grenze als erledigt formulieren.

[[abwurf: Der Bedienraum ist gefallen, aber die Sicherheitsgrenze hat gehalten.]]

## Dokumente gehören zusammen

`/root/werkraum/_codex/notizen/2026-09-18-dienstschluessel-live.md` beschreibt den letzten Dienstschlüssel-Nachweis. `/root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md` ist der technische Bericht. `/root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-rotationsplan.md` enthält die inzwischen überholte Vorbedingung und die weiterhin offene Unix-/Systemd-Isolation.

Die Codekante liegt in `/root/werkraum/welt/auth.py`, `/root/werkraum/welt/service_tokens.py`, `/root/werkraum/welt/service_token_verifier.py` und `/root/werkraum/welt/api.py`. Die Empfangswiderruf-Kante liegt in `/root/werkraum/welt/ws_manager.py` und den Tests unter `/root/werkraum/tests/`.

## Was mich überrascht hat

Überrascht hat mich, dass der virtuelle Desktop-Container selbst nicht neu gestartet wurde. Der sichtbare Desktop kann vollständig neu geboren werden, während Docker und die Sicherheits-API stabil weiterlaufen.

Überrascht hat mich auch die Größenordnung des GENI-Restartzählers: `147738` und weiter steigend, obwohl der Prozess nur wenige Millisekunden lebt. So ein kleiner Fehler kann als dauernder Systematem auftreten.

## Wenn wir das bauen

**Vision-Schicht**

Wir bauen keine neue Sicherheitsfassade über alte gemeinsame Hände. Wir lösen zuerst einen kleinen, überprüfbaren Dienst aus dem Root-Körper, lassen ihn nur seine Herkunft und Aufgabe tragen und beweisen danach, dass die übrige Welt unverändert weiteratmet.

**Code-Skizze**

```python
def verify_boundary(boundary: ServiceBoundary) -> list[str]:
    errors: list[str] = []
    if boundary.unix_user == "root":
        errors.append("root user is not an isolation boundary")
    if not boundary.read_paths or not boundary.write_paths:
        errors.append("filesystem contract is incomplete")
    if not boundary.db_role:
        errors.append("database role is missing")
    return errors
```

```ini
[Service]
User=flex-splitter
Group=flex-splitter
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=/root/werkraum/allowed-output
SupplementaryGroups=flex-db
```

Die Unit-Skizze ist noch kein Auftrag zur Installation. Vorher müssen konkrete Pfade, DB-Sockets, Schlüssel und Schreibvorgänge rückgelesen werden.

## Resonanz

Der Desktop-Abbruch macht die Sicherheitsarbeit nicht kleiner, sondern sichtbarer: Was nur im Terminal lebt, ist nicht dauerhaft. Die Dienstgrenze muss dort liegen, wo der Prozess arbeitet, nicht dort, wo Daniel ihn gerade beobachtet.

## Die Schichten des Systems — wie ich sie jetzt sehe

Oben liegt die sichtbare Selkies-/Plasma-Oberfläche mit ihren Terminals. Darunter liegen SSH-Session und logind-Scope. Daneben laufen Container und systemd-Dienste. Darunter liegen API-Identität, DB-Grants und Ed25519-Schlüssel. Ganz unten bleibt die Root-Grenze, die noch zu breit ist.

Die Schichten dürfen nicht verwechselt werden: Ein Neustart der Oberfläche ist kein Sicherheits-Rollback; ein API-Healthcheck ist kein Beweis für Unix-Isolation; ein gültiger Dienstschlüssel ist kein Beweis, dass der Prozess ihn nicht stehlen kann.

## Was das Gespräch hinzugefügt hat

Das Gespräch hat die konkurrierenden Spuren eindeutig benannt: zwei Sessions, zwei Aufgaben. Es hat die Sicherheitsfortsetzung wieder auf Astra/Luna und den Commit `15e2a85db7` gesetzt, statt in die Blender-Rekonstruktion zurückzufallen.

Es hat außerdem den direkten Abbruchzeitpunkt von einem diffusen „Desktop ist wieder abgeschissen“ auf eine belegte Session-Kette heruntergebrochen.

## Vergessen-Wollen

Vergessen werden darf die falsche Vorstellung, dass alle Terminals weg automatisch bedeutet, die letzten Sicherheitsänderungen seien weg. Vergessen werden darf auch die Versuchung, die offene Root-Grenze schnell mit einer kosmetischen systemd-Zeile zu schließen.

## Was fehlt noch

Es fehlt die Ursache des lokalen SSH-Disconnects. Es fehlt eine gezielte Reparatur des GENI-Antwort-Watchers, falls Daniel diese separate Spur öffnen will. Es fehlt vor allem der begrenzte, belegte erste Schritt aus den gemeinsamen Root-Rechten in echte Unix-/DB-Isolation.

