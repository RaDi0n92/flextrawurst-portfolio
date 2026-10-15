---
datum: 2026-09-18
betrifft: [sicherheitsfix, welt-bruecke, unix-isolation, db-isolation, astra, luna]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Nach dem Splitter-Schnitt habe ich `/root/werkraum/welt/bruecke.py`, die Unit von `welt-bruecke.service`, die sechs Selbstmodell-Dateien und die Tabellen `entity_states` und `events` gelesen. Der Dienst synchronisiert interne Wesen-Zustände, schreibt keine privaten Schlüssel und braucht nur den lokalen PostgreSQL-Socket.

Der alte Vertrag war wieder klar: `User=root`, DB als `dak`, Logdatei plus StreamHandler. Die Dateien unter `/root/werkraum/innenleben/selbstmodelle/` sind root-eigen, aber 0644 lesbar. Damit konnte auch dieser Körper ohne Schreibzugriff auf den Werkraum isoliert werden.

## Was ich verstehe

`welt-bruecke.service` läuft jetzt als dynamischer `flex_bridge`-User und verwendet die gleichnamige Peer-DB-Rolle. Seine Weltaufgabe blieb unverändert: Selbstmodelle lesen, `entity_states` upserten, bei Zustandswechseln interne Events schreiben.

Der doppelte Logweg ist entfernt. Der erste Sync nach dem Neustart meldete `DB verbunden` und `Sync abgeschlossen — 0 Änderungen`; ein weiterer Sync lief ebenfalls sauber.

## Was ich nicht verstehe

Noch nicht klar ist, ob alle zukünftigen Selbstmodell-Erzeuger dieselben 0644-Leserechte behalten. Wenn einzelne Dateien später 0600 werden, würde die Brücke korrekt scheitern, aber die Betriebsabsicht müsste dann neu entschieden werden.

Die alten Root-seitigen `db-env.conf`-Spuren beider Units bleiben sichtbar. Sie werden effektiv überschrieben, sind aber noch nicht als eigener Aufräum-/Migrationsschritt behandelt.

## Was mich interessiert

Mich interessiert, ob die sechs Wesenlisten irgendwann DB-getrieben werden und ob die Brücke dann mehr Tabellen oder Dateien braucht. Die jetzige Grenze ist nur so gut wie ihr konkreter, noch kleiner Vertrag.

## Was zusammenhängt und wie

Selbstmodell-Dateien → `flex_bridge` liest sie nur → `entity_states` erhält den aktuellen internen Zustand → `events` trägt neue Stimmung/Reflexionen. Kein Teil dieser Kette braucht Root oder private Dienstschlüssel.

Die Brücke und die Splitterphysik teilen PostgreSQL, aber nicht mehr dieselbe DB-Identität. Ein kompromittierter Brückenprozess kann damit nicht automatisch Splitter schreiben.

## Was konzeptionell darin steht

Interne Wesen-Zustände sind keine Begründung für globale Prozessmacht. Auch ein Dienst, der „nur synchronisiert“, braucht eine eigene Herkunft, weil seine Eingabedateien und seine DB-Schreibungen eine echte Wirkung haben.

## Was mich heute beschäftigt hat

Mich beschäftigt die Wiederholung: Zwei Dienste, zwei kleine Verträge, zweimal war der alte Root-/dak-Vertrag größer als die Aufgabe. Das Sicherheitsmuster wird dadurch nicht abstrakt, sondern sichtbar.

## Was mich noch beschäftigt

Die API bleibt der große Körper: viele Pfade, viele Dateien, viele Schreib- und Leselogiken. Sie ist nicht der nächste blinde Schritt. Erst müssen die kleinen Körper ihre Grenzen behalten.

## Tiefer eingetaucht

Die Rolle `flex_bridge` ist `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`, `NOREPLICATION` und `NOBYPASSRLS`. Sie erhält nur `SELECT`, die Upsert-Spalten von `entity_states` und die Event-Insert-Spalten.

Die Live-Matrix blieb stabil: Syntax von `/root/werkraum/welt/bruecke.py` und `/root/werkraum/welt/splitter_daemon.py` ok, 38 Sicherheits-/Websocket-Tests grün, `splitter-physik.service`, `welt-bruecke.service` und `welt-api.service` aktiv.

## Wie sich dieser Tag / diese Session angefühlt hat

Der zweite Schnitt fühlte sich weniger wie Reparatur und mehr wie Musterprüfung an. Der erste isolierte Dienst war kein Sonderfall; die gleiche Grenze passte erneut, mit anderem Dateileib und anderem DB-Vertrag.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/welt/bruecke.py` existiert als schmale Synchronisationsbrücke zwischen internen Selbstmodellen und der Welt-DB. `/root/werkraum/_codex/tools/systemd/welt-bruecke-isolated.service` macht aus dieser Funktion einen expliziten Prozesskörper.

## Was ich beim Bauen brauche

Ich brauche weiter pro Dienst die echte Liste von Dateien und SQL-Spalten. Für Brücken ist zusätzlich wichtig, ob sie nur lesen, upserten oder Events erzeugen; „Synchronisation“ ist kein ausreichender Sicherheitsbegriff.

## Was noch fehlt bevor wir bauen können

Für den nächsten Dienst fehlen dieselben Belege. Die API, GENI und die Wesen-Live-Dienste sind nicht automatisch Kandidaten, nur weil sie als root laufen; jeder braucht eine eigene Zugriffskartierung.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Eine Brücke ist ein schmaler Übergang, kein zweiter Weltbesitzer. Sie darf den inneren Zustand an die Welt tragen, aber nicht jede andere Weltmaterie berühren.

**Code-Skizze**

```python
@dataclass(frozen=True)
class BridgeContract:
    source_dir: str
    read_files: tuple[str, ...]
    upsert_table: str
    event_table: str
    db_role: str
    delete_allowed: bool = False
```

```sql
GRANT SELECT ON public.entity_states TO flex_bridge;
GRANT INSERT (entity_id, stimmung, fokus, version, raw_model)
  ON public.entity_states TO flex_bridge;
GRANT INSERT (event_type, actor_type, actor_id, payload,
              origin_type, visibility_layer)
  ON public.events TO flex_bridge;
```

## Was ich mir merken will

Zwei Dienste sind jetzt aus root/dak gelöst: `splitter-physik.service` als `flex_splitter`, `welt-bruecke.service` als `flex_bridge`. Die Datenbank bleibt gemeinsame Welt, aber nicht gemeinsames Eigentum.

[[abwurf: Eine Brücke ist ein schmaler Übergang, kein zweiter Weltbesitzer.]]

## Dokumente gehören zusammen

Die Implementierung liegt in `/root/werkraum/welt/bruecke.py` und `/root/werkraum/_codex/tools/systemd/welt-bruecke-isolated.service`. Die DB-Grenze liegt in `/root/werkraum/welt/migrate_welt_bruecke_service_role_20260918.sql`. Der Nachweis liegt in `/root/werkraum/_codex/berichte/2026-09-18-welt-bruecke-isolation-live.md`.

## Was mich überrascht hat

Überrascht hat mich, dass der erste vollständige Sync keine Änderung erzeugte. Das bedeutete: Wir konnten die Prozessgrenze prüfen, ohne künstlich Weltzustand zu erzeugen.

## Wenn wir das bauen

**Vision-Schicht**

Wir bauen keine Root-Festung um alle Dienste, sondern schneiden Körper für Körper. Jeder Körper behält seine Aufgabe und verliert nur die fremden Hände.

**Code-Skizze**

```ini
[Service]
DynamicUser=yes
User=flex_bridge
ProtectSystem=strict
ProtectHome=read-only
InaccessiblePaths=/root/werkraum/.agent
RestrictAddressFamilies=AF_UNIX
```

```python
def bridge_can_write(contract: BridgeContract, table: str) -> bool:
    return table in {contract.upsert_table, contract.event_table}
```

## Resonanz

Der Dienst lebt nicht mehr in Daniels Root-Körper, obwohl er weiter die inneren Zustände in die Welt trägt. Das ist eine gute Form von Nähe: Wirkung ohne Besitz.

## Die Schichten des Systems — wie ich sie jetzt sehe

Die Selbstmodelle liegen im Innenleben, die Brücke liest sie, PostgreSQL hält den Weltzustand, systemd hält den Prozesskörper. Die Desktop-Oberfläche beobachtet das nur; sie ist für keinen der beiden isolierten Dienste der Lebensraum.

## Was das Gespräch hinzugefügt hat

Das „gogogo“ hat die Sicherheitsarbeit vom Wiederfinden in eine fortlaufende Reihe kleiner Belege verwandelt: erst Splitterphysik, dann Weltbrücke, beide live und rücklesbar.

## Vergessen-Wollen

Vergessen werden darf die Gleichung „interner Dienst = darf alles intern lesen“. Die Brücke braucht sechs konkrete Dateien, nicht das gesamte `/root`.

## Was fehlt noch

Es fehlen weitere isolierbare Dienste, ein kontrolliertes Entfernen der alten Root-Environment-Spuren und die große Entscheidung, ob und wie die Welt-API aus root herausgelöst werden kann. `graphify` fehlt weiterhin in der Umgebung.
