---
datum: 2026-09-18
betrifft: [sicherheitsfix, splitter-physik, unix-isolation, db-isolation, astra, luna]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den offenen Sicherheitsstand aus `/root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md`, die Unit `/etc/systemd/system/splitter-physik.service`, den Daemon `/root/werkraum/welt/splitter_daemon.py` und die echten PostgreSQL-Zugriffe gelesen. Dazu kamen die laufenden Prozessrechte, die Peer-Authentifizierung und der aktuelle Tick-Log.

Der kleine Dienst war vorher schlicht: `User=root`, DB-Verbindung als `dak`, Log unter `/root/werkraum/logs/`. Die Weltlogik selbst brauchte aber nur fünf Tabellen und kein privates Dienstschlüsselmaterial. Dadurch wurde aus der großen offenen Root-Frage ein begrenzbarer erster Körper.

## Was ich verstehe

`splitter-physik.service` ist jetzt als erster dauerhafter Dienst aus dem gemeinsamen Root-/DB-Vertrag gelöst. systemd weist ihm dynamisch `flex_splitter` zu, PostgreSQL erkennt denselben Namen über Peer-Authentifizierung, und die Tabelle bleibt im Besitz von `dak`.

Der Prozess läuft mit `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome=read-only`, `PrivateTmp`, `PrivateDevices`, eingeschränkten Unix-Sockets und ohne Capabilities. Er kann schreiben, was er für seinen Log braucht, und nur die tatsächlich erforderlichen Datenbankoperationen ausführen.

## Was ich nicht verstehe

Die systemd-Verify-Prüfung meldet beim Arbeitsverzeichnis unter `/root` eine Read-only-Warnung, während der reale Dienst genau dort erfolgreich startet und tickt. Das ist eine Grenze des Verify-Aufrufs in dieser Umgebung, kein beobachteter Live-Fehler.

Noch offen ist, wie die DB-Rolle und der dynamische User später als reproduzierbarer Provisionierungsschritt ausgerollt werden. Im Moment sind sie live korrekt, aber die DB-Rolle ist kein Git-Artefakt.

## Was mich interessiert

Mich interessiert, ob derselbe Vertrag als nächstes auf einen weiteren schreibenden Dienst passt, ohne dass wir die gemeinsame Welt-API blind zerlegen. Besonders wichtig wird die Reihenfolge: erst ein Dienst mit kleinem Dateileib, dann ein Dienst mit vielen Weltpfaden.

## Was zusammenhängt und wie

Getrennter Unix-User → Prozess kann Root-Dateien nicht einfach lesen → `/root/werkraum/.agent` bleibt unsichtbar → private Service-Schlüssel und alte DB-Dateien liegen außerhalb seines Leibs.

Getrennte DB-Rolle → keine Tabellenhoheit, keine DDL, kein `DELETE` → ein kompromittierter Splitter-Daemon kann seine fünf erlaubten Weltoperationen ausführen, aber nicht die Datenbankstruktur übernehmen.

Peer-Conninfo → kein neues Passwort im Daemon → die Herkunft des DB-Zugriffs ist an die laufende Unix-Identität gebunden. Die alte Root-seitige Environment-Spur bleibt als Rückrollrest sichtbar, wird aber vom Python-Prozess überschrieben.

## Was konzeptionell darin steht

Isolation beginnt nicht beim Token. Sie beginnt dort, wo ein Prozess seine Identität bekommt, welche Dateien er sehen kann und welche Datenbankrolle er tatsächlich verwendet. Die Ed25519-Schlüssel waren die erste Herkunftsgrenze; `flex_splitter` ist die erste Körpergrenze.

Ein guter Sicherheitsfix nimmt dem Prozess nicht seine Aufgabe. Er nimmt ihm nur die Behauptung, für alles zuständig zu sein.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, dass der erste Versuch sofort einen Conninfo-Quotingfehler zeigte und trotzdem wertvoll war: Der Prozess startete isoliert, die DB verweigerte die falsche Verbindung, und kein Root-Fallback sprang heimlich ein. Danach war der Fix eine einzige Unit-Zeile.

Mich hat auch der Unterschied zwischen `table privilege` und `column privilege` beschäftigt. Eine grobe Tabelle kann „UPDATE“ sagen, obwohl die relevante Grenze erst auf den konkreten Spalten sichtbar wird.

## Was mich noch beschäftigt

Die alte `/etc/systemd/system/splitter-physik.service.d/db-env.conf` enthält weiterhin die historische Root-seitige Conninfo. Sie ist nicht die effektive Conninfo des laufenden Python-Prozesses, aber sie bleibt eine Konfigurationsspur und muss beim nächsten Rollback-/Provisionierungsschritt bewusst behandelt werden.

## Tiefer eingetaucht

Die Live-Belege sind konkret: PID `3597072` lief als `flex_splitter`; der Peer-Test lieferte `flex_splitter|flextrawurst`; `/var/log/flextrawurst/splitter-physik.log` zeigte `Tick 0`, `Tick 1` und `Tick 2` ohne Fehler. Danach wurde der Dienst nach dem Fallback-Secret-Fix nochmals gestartet und tickte erneut erfolgreich.

Die 38er Sicherheitsmatrix aus Dienstschlüsseln, Kontostatus, Dienstrechten, Einsammel-Identität und passivem Websocket-Widerruf blieb grün. Die Änderung hat den bisherigen Tokenvertrag nicht aufgeweicht.

## Wie sich dieser Tag / diese Session angefühlt hat

Das war kein großer Umbau, sondern ein guter kleiner Schnitt: erst messen, dann User, DB-Rolle, Unit, Fehlstart, Korrektur, Tick. Der Prozess ist jetzt kleiner als vorher, ohne dass die Weltlogik neu erfunden werden musste.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/welt/splitter_daemon.py` existiert, damit Splitterphysik regelmäßig aus der Datenbank gelesen und zurückgeschrieben wird. `/root/werkraum/_codex/tools/systemd/splitter-physik-isolated.service` existiert jetzt als dauerhaft lesbarer Sicherheitsvertrag für genau diesen Körper.

`/root/werkraum/_codex/berichte/2026-09-18-splitter-physik-isolation-live.md` existiert, damit „läuft“ nicht mit „isoliert“ verwechselt wird und die verbleibende Root-/Provisionierungsgrenze sichtbar bleibt.

## Was ich beim Bauen brauche

Ich brauche pro Dienst eine tatsächliche Zugriffsmatrix: Dateien, Tabellen, Spalten, Netzwerkfamilien, Logpfad und Rollback. Ich brauche außerdem einen Live-Negativtest, nicht nur eine syntaktisch schöne Unit.

## Was noch fehlt bevor wir bauen können

Für den nächsten Dienst fehlen sein kleinster sicherer Dateileib, eine eigene DB-Rolle oder eine begründete Wiederverwendung und ein Beleg, dass sein Start nicht an der Desktop-Session hängt. Die globale Root-Isolation ist weiterhin nicht fertig.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Jeder dauerhafte Dienst bekommt einen eigenen Körpervertrag: Name, Identität, sichtbare Weltstücke, erlaubte Handlungen und eine Rückkehrspur. Die Datenbank bleibt gemeinsame Welt, aber nicht gemeinsames Eigentum.

**Code-Skizze**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class DbGrant:
    table: str
    select: tuple[str, ...]
    insert: tuple[str, ...]
    update: tuple[str, ...]
    delete: bool = False

@dataclass(frozen=True)
class UnitBoundary:
    user: str
    read_only_roots: tuple[str, ...]
    read_write_roots: tuple[str, ...]
    address_families: tuple[str, ...]
    grants: tuple[DbGrant, ...]
```

```sql
CREATE ROLE flex_splitter LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOINHERIT NOREPLICATION NOBYPASSRLS;
GRANT SELECT ON public.splitter TO flex_splitter;
GRANT UPDATE (pos_x, pos_y, vel_x, vel_y, energie, status)
  ON public.splitter TO flex_splitter;
```

## Was ich mir merken will

Der erste Root-/DB-Isolationsschnitt ist live und klein geblieben: `splitter-physik.service` → `flex_splitter` → fünf Tabellen → kein Delete. Die nächste Grenze muss genauso konkret werden.

[[abwurf: Ein guter Sicherheitsfix nimmt dem Prozess nicht seine Aufgabe. Er nimmt ihm nur die Behauptung, für alles zuständig zu sein.]]

## Dokumente gehören zusammen

Der fachliche Vorlauf steht in `/root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md`. Die Implementierung steht in `/root/werkraum/welt/splitter_daemon.py` und `/root/werkraum/_codex/tools/systemd/splitter-physik-isolated.service`. Der Live-Nachweis steht in `/root/werkraum/_codex/berichte/2026-09-18-splitter-physik-isolation-live.md`.

## Was mich überrascht hat

Überrascht hat mich, dass `DynamicUser=yes` mit dem ausdrücklich benannten `flex_splitter` genau die fehlende Unix-Identität liefern kann, ohne `/etc/passwd` dauerhaft umzuschreiben. Dadurch bleibt die Grenze reversibel und sauber an die Unit gebunden.

## Wenn wir das bauen

**Vision-Schicht**

Wir lösen die Dienste einzeln aus dem Root-Körper, bis „live“ und „allmächtig“ nicht mehr dasselbe Wort sind. Jeder Schritt muss seine Aufgabe weiter erfüllen und seine Grenzen sichtbar beweisen.

**Code-Skizze**

```ini
[Service]
DynamicUser=yes
User=<service-name>
Group=<service-name>
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=read-only
InaccessiblePaths=/root/werkraum/.agent
RestrictAddressFamilies=AF_UNIX
```

```python
def assert_no_delete(grants: list[DbGrant]) -> None:
    assert all(not grant.delete for grant in grants)
```

Vor jedem weiteren Dienst: Zugriffsmatrix, DB-Rolle, Unit-Verify, echter Neustart, Negativrechte, mehrere Ticks, Rücklese.

## Resonanz

Der Desktop kann wieder sterben, ohne dass dieser Dienst an seiner Oberfläche hängt. Das ist die kleine technische Antwort auf den großen Frust vom Anfang: Dauerhafte Weltbewegung gehört in einen Körper, der nicht vom Terminal abhängt.

## Die Schichten des Systems — wie ich sie jetzt sehe

Oben bleibt die sichtbare Oberfläche. Darunter leben SSH und Desktop-Scope. Daneben stehen systemd-Units. In der Unit liegen User, Mount-Grenzen und Capabilities. Darunter liegt PostgreSQL mit Rollen, Tabellen und Spaltenrechten. Erst ganz unten liegt die Weltlogik.

Der Splitter-Körper durchquert diese Schichten jetzt mit weniger Macht: seine Weltlogik bleibt gleich, sein Unix- und DB-Leib ist kleiner.

## Was das Gespräch hinzugefügt hat

„gogogo“ hat aus der Rekonstruktion eine konkrete nächste Handlung gemacht. Statt die gesamte Root-Landschaft auf einmal anzufassen, wurde der kleinste passende Dienst genommen und bis zum echten Tick geführt.

## Vergessen-Wollen

Vergessen werden darf die Idee, eine Root-Isolation sei erledigt, nur weil ein Token getrennt signiert wird. Vergessen werden darf auch die Idee, eine Unit sei sicher, nur weil `systemd-analyze verify` eine Datei liest.

## Was fehlt noch

Es fehlen weitere Dienstkörper, reproduzierbare DB-Provisionierung, die bewusste Behandlung des alten Conninfo-Drop-ins und eine Erklärung, warum der GENI-Antwort-Watcher weiterhin alle 15 Sekunden startet. Die globale Root-Grenze bleibt offen.
