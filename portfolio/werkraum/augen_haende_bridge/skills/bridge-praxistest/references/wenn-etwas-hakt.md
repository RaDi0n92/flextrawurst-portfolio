# Wenn etwas hakt

Trage es als **Befund** ein, mit Befehl und Ausgabe wörtlich.

Jede Antwort des Harness nennt unter `next` die nächste Handlung und unter `klasse` die Art des Hindernisses
(`wahrnehmung`, `planung`, `ausfuehrung`, `erholung`). Lies zuerst `next`, dann diese Tabelle.

Überspringen gibt es nicht: Such die Ursache, behebe sie, trag sie ein (`test ursache`) und mach am
selben Schritt weiter.
Ein Befund ist ein Ergebnis, kein Grund zum Weiterziehen.

| Du siehst | Bedeutung | Was du tust |
|---|---|---|
| `kein_fenster_ziel` | Es ist noch kein Fenster gebunden; Hände wirken nur in einem Fenster. | Bitte Daniel, das Testfenster zu binden (Fadenkreuz im Terminal). |
| `lease_fehlt` | Du hast die Erlaubnis für dieses Ziel nicht genommen. | `lease` ausführen, dann erneut. |
| `ausserhalb` | Dein Punkt liegt außerhalb des Fensters. | Neues Bild holen, Punkt im Bild wählen. |
| `frame_veraltet` | Dein Bild ist zu alt. | Neues Bild holen (`see`) und neu zielen. |
| `daniel_uebernimmt` | Daniel bedient gerade selbst. | Warten; es geht von selbst weiter. |
| `not_aus` | F12 oder STOP wurde ausgelöst. | Daniel gibt frei; danach Lease neu nehmen. |
| `no_frame_yet` | Es gibt noch kein Bild deines Ziels. | Ziel binden lassen; Bild abwarten. |
| `raute_nicht_erreichbar` | Die Ansage kam nicht in der Raute an. Der Grund steht in `next.grund` (Körperquittung). | `feld_nicht_geoeffnet`: Raute liegt teils außerhalb des Bildschirms, in der Ampel „Terminal und Raute zurückholen“. `daniel_uebernimmt`: 6 s Ruhe abwarten. `fokus_verloren`: kein Fremdfenster dazwischen. `gesperrt`: Not-Aus aktiv. Sonst `bridge_cli.py lage`. |
| `ziel_gewechselt` | Dein Ziel (oder das des anderen) hat sich seit der Ansage geändert. Die Belege tragen das alte Ziel. **Kein Fehlversuch.** | Beide an das Ziel des Schritts binden, `test nochmal`, neu ansagen. |
| `raute_quittung_fehlt` | Die Bridge hat die Ansage gesendet, aber der Körper hat sie nicht bestätigt. | Hände, Fokus, Not-Aus und Verbindung prüfen; nicht einfach im Chat wiederholen. |
| `schrittbeleg_fehlt` | Die grobe Spur passt, die für diesen Schritt erwartete konkrete Aktionsfolge fehlt. | `test karte` lesen und die fehlende Handlung mit den Händen wiederholen. |
| `ledger_nicht_geschrieben` | Der JSONL-Beleg konnte nicht dauerhaft geschrieben werden. | Nicht weiterlaufen; Speicher-/Pfadfehler beheben und den Lauf neu starten. |
| `vorflug_fehlt` | Der Vorflug konnte eine Voraussetzung nicht bestätigen. | Die genaue Liste im Ergebnis abarbeiten; ein Vorflug ersetzt keinen Praxisschritt. |
| `jetzt_<knoten>` | Du bist an einer anderen Stelle des Ablaufs. | `test karte` zeigt, was dran ist. |
| `nicht_dein_zug` | Der andere Agent ist dran. | Zuschauen; dein Bild zählt bei der Bestätigung. |

Erscheint die Ansage nicht in der Raute, sag das **als Befund**:

`test kuer "Ansage kam nicht in der Raute an"`

Nutze `say` höchstens als sichtbaren Notbehelf. Es erfüllt keine Körperquittung
für `test ansage` und darf einen fehlenden Praxistest-Beleg nicht überdecken.
