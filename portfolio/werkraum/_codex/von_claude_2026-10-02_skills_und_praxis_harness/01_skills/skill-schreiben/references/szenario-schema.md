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
| `schritte` | ja | Liste, höchstens 200, lückenlos nummeriert ab 1 |

## 2. Felder eines Schritts

Pflicht (nicht leer): `nr`, `teil`, `ziel`, `titel`, `pruefe`, `mache`, `erwarte`.

Freiwillig: `evidenz` (Liste der Spurarten), `kuer` (freiwillige Idee).

`braucht` (zum Beispiel `menue_freigabe`): Der Schritt wird zurückgestellt, solange das Gewünschte fehlt.

## 3. Evidenzarten

- `sehen`: ein Bild geholt.
- `haende`: Aktion der Hände, erfolgreich.
- `haende_abgelehnt`: Versuch mit Grund `ausserhalb`, für Negativtests.
- `nachricht`, `weltdom`, `kapsel`, `seed`, `loop`: der jeweilige Befehl hat gewirkt.
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
