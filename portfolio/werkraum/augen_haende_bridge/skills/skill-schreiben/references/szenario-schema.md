# Szenario-Datei für die Praxis-Harness

Ein Szenario ist eine JSON-Datei: `src/augen_haende_bridge/praxis/szenario_<name>.json`.

Name: kleine Buchstaben, Ziffern, Bindestrich (höchstens 40).

Start: `bridge_cli.py test start <Partner> --szenario=<name>`. Liste: `bridge_cli.py test szenarien`.

## Inhalt

1. Oberste Felder
2. Felder eines Schritts
3. Evidenzarten
4. Rollen
5. Beispiel
6. Erweitern

## 1. Oberste Felder

| Feld | Pflicht | Bedeutung |
|---|---|---|
| `id` | ja | Kennung des Szenarios |
| `titel` | nein | Lesbarer Name |
| `rollen` | nein | `wechselnd` (Standard: ungerade Schritte A, gerade B) oder `a` (A handelt immer) |
| `contract_version` | nein | `1` für Spurarten; `2` verlangt zusätzlich typisierte `belege` |
| `schritte` | ja | Liste, höchstens 200, lückenlos nummeriert ab 1 |

## 2. Felder eines Schritts

Pflicht (nicht leer): `nr`, `teil`, `ziel`, `titel`, `pruefe`, `mache`, `erwarte`.

Pflicht: `evidenz` (nicht leere Liste der Spurarten).

Freiwillig: `kuer` (freiwillige Idee),
`wirkungspruefung` (menschlich lesbarer Hinweis).

`braucht` darf nur leer oder `menue_freigabe` sein. Ein Menüschritt wird ohne
Freigabe als nicht getestet zurückgestellt; unbekannte Voraussetzungen werden
abgelehnt.

Bei `contract_version: 2` ist `belege` Pflicht. Jeder Eintrag hat zum Beispiel:

```json
{"id":"klick-1","role":"handelnder",
 "match":{"command":"haende","action_kind":"klick","ok":true}}
```

`match` darf nur bekannte typisierte Felder verwenden. Die Einträge werden in
Reihenfolge und mit jeweils neuem Event geprüft. `same_resource_as` bindet einen
späteren Beleg an dieselbe Ressource. Unbekannte Felder und leere Beleglisten
sind ungültig.

## 3. Evidenzarten

- `sehen`: ein Bild geholt.
- `haende`: Aktion der Hände, erfolgreich.
- `haende_abgelehnt`: Versuch mit Grund `ausserhalb`, für Negativtests.
- `nachricht`, `weltdom`, `kapsel`, `seed`, `loop`: protokollierte Dienstspuren;
  kein automatischer Nachweis einer sichtbaren Wirkung.
- `raute`: Eingabe in die Raute.

## 4. Rollen

Der **Handelnde** sagt an, handelt und berichtet.

Der **Zuschauer** holt sein eigenes Bild und urteilt.

Bei Widerspruch gibt es bis zu zwei Klärrunden.

## 5. Beispiel

Siehe `references/vorlage-szenario.json.txt`.

## 6. Erweitern

Neue Spurart:

1. In `EVIDENZ_ARTEN` (`praxis/lauf.py`) eintragen.
2. In `PraxisDienst.evidenz` (`client_vps/praxis_dienst.py`) zählen.
3. Test schreiben, der ohne die Erweiterung scheitert (Gegenprobe).

Neue Rolle: Wert in `ROLLEN` und in `PraxisLauf.handelnder` ergänzen, Test dazu.

Neue Kante: in `baue_graph` verdrahten, bedingte Kanten vor der Kante „always“. Test, der den Weg durchläuft.

Jede Erweiterung gilt erst als fertig, wenn ihr Gate im Ledger grün ist.

Ein `ok`-Ergebnis bedeutet nur, dass kein Vertragsverstoß festgestellt wurde.
Es ist keine Aussage, dass eine Weltwirkung wahr oder ein Dienst aktuell live ist.
