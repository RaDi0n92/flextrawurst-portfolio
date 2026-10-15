# Rückwärts-Engineering des Praxistests auf vd1

Zustände, Ursachenketten und Zielarchitektur. Grundlage: `ereignisse.jsonl` (3369 Ereignisse), die Ledger der Läufe p-2fa24c und
p-451034, `bridge.log` des Körpers, `SITZUNGSPROTOKOLL_vd1_2026-10-02_bis_03.md`.

Marken: **Belegt** = aus den Daten gemessen. **Vermutung** = plausibel, nicht gemessen.

## 1. Zeitbilanz

Belegt, Frame-Lücken über zwei Minuten (gebunden, aber kein Bild):

| Agent | Lücken | Summe |
| --- | --- | --- |
| Opencode | 11 | 168 min |
| Claude-Host | 11 | 212 min |
| Gemgem | 8 | 127 min |

Der Gutachter hatte über die Hälfte der Zeit kein frisches Bild. Ein Urteil ohne eigenes frisches Bild gilt nicht, also steht dann der
Lauf. Dauer je Schritt im Lauf p-451034 in Minuten: Schritt 1: 30, 2: 45, 3: 21, 4: 33, 5: 7, 6: 40, 7: 12, 10: 53, 14: 10. Schritte mit
30 bis 53 Minuten enthalten überwiegend Warten auf Bindung, Strom und Urteil; Schritt 5 (7 Minuten) lief, als Fenster, Strom und
Bindung zusammenpassten (Vermutung als Grund).

## 2. Hände

Belegt, über alle Agenten: 53 ausgeführt, 47 abgelehnt.

| Ergebnis | Anzahl |
| --- | --- |
| ausgeführt | 53 |
| `daniel_uebernimmt` | 14 |
| `frame_unbekannt` | 13 |
| `punkt_verdeckt` | 12 |
| `lease_fehlt` | 4 |
| `ziel_weg` | 2 |
| `frame_veraltet`, `geometrie_geaendert` | je 1 |

28 der 47 Ablehnungen (`frame_unbekannt`, `punkt_verdeckt`, `frame_veraltet`, `ziel_weg`) sind Folgen von Strom und Bindung, 14 sind gewollte
Rücksicht auf Daniels Eingaben.

## 3. Ursachenketten

**A: Strom hängt, Gutachter blind, Lauf steht.** Belegt: Nach Bindungen kam oft nur ein Schnappschuss ohne Folgebilder (`seq None`); im
`bridge.log` stand von 01:58 bis 05:18 keine Zeile des Bilderstroms, der Strom war still. Wurzel: siehe Abschnitt 7.

**B: Jeder Zielwechsel braucht einen Menschen.** Belegt: Für jedes neue Fenster (Kate, Dialoge, Chromium, Dolphin, Chat) wurden beide
Agenten über das Scanner-Menü gebunden, oft zweimal, weil der Strom dem ersten Binden nicht folgte. Mindestens zwölf Wechsel, jeweils
mehrere Minuten.

**C: Fenster verschwinden.** Belegt: Test-Chromium zweimal, Dolphin einmal geschlossen; die Fenster-ID wurde wiederverwendet. Der Agent merkt
es nur am ausbleibenden Bild; `ziel_weg` kommt nur bei einer Aktion.

**D: Kein gemeinsamer Wartezustand.** Belegt: Nutzerin wartet auf das Urteil, Gutachter auf ein Bild, die Hilfswerkzeuge auf Eingabepausen. Keiner
sieht, worauf der andere wartet; jede Entwarnung lief über getippte Nachrichten in Terminals.

**E: Fremdeingaben.** Belegt: 14 Abbrüche durch Eingaben von Daniel (gewollt), `xdotool`-Eingaben in fremde Terminals ohne Bridge. Es gibt keinen
Weg, der vor jeder Eingabe prüft, ob jemand sonst gerade etwas tut.

**F: Beleg-Pflicht ohne Alternativweg.** Belegt: Tasten (Strg+S, Enter) wurden zugestellt und auditiert, zählten aber nicht als Beleg
(`missing s2-1`); der Schritt blieb offen, obwohl die Datei gespeichert war.

**G: Keine Sperre gegen Überspringen.** Belegt: Der Harness erlaubt "zurückgestellt" und "nicht getestet" ohne Sperre, so dass ein Lauf
nach mehreren Fehlversuchen weiterläuft. Anforderung: Halt nach dem dritten Fehlversuch, dann Ursachensuche, dann weiter.

**H: Bridge-eigene Fenster verdecken Bridge-Ziele.** Belegt: Das Overlay "Objekte" lag deckungsgleich über dem Bridge-Chat; das Fensterbild
zeigte den Chat frei, der Käfig meldete `punkt_verdeckt`.

## 4. Wartegraph

- Nutzerin wartet auf Gutachter (Urteil) und auf Bindung.
- Gutachter wartet auf frisches Bild und auf die Aktion der Nutzerin.
- Bindung wartet auf einen Menschen, solange sie nur über den Scanner-Klick geht.

Diese Zyklen erzeugen die langen Stillstände. Es gibt keinen Ort, an dem der Graph steht.

## 5. Hebel nach Wirkung

Aus den Daten lässt sich keine Beschleunigung in Prozent belegen. Belegt ist: Über die Hälfte der Zeit ging an fehlende Bilder und Bindungen.
Ohne diese Kette wäre der Lauf grob sieben- bis zehnmal kürzer (Vermutung, Größenordnung aus 7 Stunden gegen die 7 bis 12 Minuten der
ungestörten Schritte).

| Nr | Hebel | Zustand |
| --- | --- | --- |
| 1 | Stille verbieten: jeder Zweig ohne Bild oder Aktion schreibt Ereignis und Grund | umgesetzt (Log, Herzschlag, Ampel) |
| 2 | Augen nie ausfallen lassen: Fenster weg oder Binden gelöst → ganzer Desktop; jeder neue Agent sieht sofort den Desktop | umgesetzt |
| 3 | Selbstheilung des Stroms (Sendefaden zurücksetzen, wenn länger kein Bild kommt) | offen |
| 4 | Bindung durch den Agenten, bestätigt mit einem Klick, statt Scanner-Klick | offen |
| 5 | Wartezustand sichtbar (wer wartet worauf seit wann) | offen, braucht Graph und Ereignisspeicher |
| 6 | Halt statt Überspringen: dritter Fehlversuch führt in "blockiert", Diagnoseknoten | offen |
| 7 | Eingabeschutz: vor jeder Fremdeingabe Aktivität und Eingabezeile prüfen | offen |
| 8 | Ampel: alle Funktionen sichtbar, Dauerfeuer im Chat, Piepen, Behebe-Knöpfe | umgesetzt (Fensterform im Bau) |

## 6. Zielarchitektur

Heute liegen die Wahrheiten in vier Speichern: Relay (`bridge-relay.sqlite3`), Ereignisprotokoll (`ereignisse.jsonl`), Praxis-Ledger
(`*.jsonl`, `*.checkpoint.json`), `bridge.log`. Es gibt keinen Ort, an dem man fragen kann, wer gerade dran ist.

- **Ereignisse und Zustand:** PostgreSQL als append-only Ereignisspeicher (Zeit, Agent, Lauf, Knoten, Versuch, Art, Grund, Nutzlast) mit Sichten
  für Wartezustand und Warteschlange.
- **Langer Graph (LangGraph):** Die Infrastruktur wird zu Knoten: Ziel gebunden, Strom frisch, Lease, Hand, Beleg, Urteil, Blockiert, Diagnose.
  Was ein Agent im Knoten tut, bleibt frei; die Übergänge sind erzwungen. Jeder Knoten und jede Kante schreibt ein Ereignis. Jeder Agent
  erfährt seine Position (wer ist dran, worauf wird gewartet, seit wann) von der Bridge.
- **RAG:** Wiederfinden von Ereignissen, Läufen und Befunden, damit Gelerntes wiederkommt.
- **Zuordnung zu Goals:** Augen-Fallback G06.7, Warteschlange und Graph G09 und G12, Ereignisspeicher G13, RAG G15, Hände und Stop G10, Anzeigen G05.

## 7. Wurzel von Kette A: der Zustand `an` des Bilderstroms

`Bilderstrom.tick` setzte bei einem verschwundenen Fenster `ziel.an = False`. `Bilderstrom.binden` erbt `an` vom alten Ziel (`alt.an`), damit ein
per Knopf ausgeschalteter Strom beim Neubinden aus bleibt (Test `test_neubindung_behaelt_den_schalter`). Beides zusammen: Schließt sich ein
Fenster und wird danach ein neues gebunden, bekommt das neue Ziel nie ein Bild, bis ein Neustart eine frische Instanz mit `an=True` anlegt.
Im Unit-Test nachgestellt; passt zum beobachteten Verlauf.

Zustand: Ein verschwundenes Fenster schaltet das Ziel auf den ganzen Desktop um und lässt `an` unberührt; jeder neue Agent beginnt auf dem
Desktop; "Bindung lösen" heißt Desktop. Die zwei Zustände "Fenster verschwunden" und "per Knopf aus" sind getrennt.
