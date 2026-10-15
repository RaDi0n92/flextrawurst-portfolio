# Gute und schlechte Ansagen

Eine Ansage steht **vor** dem Handeln in deiner Raute.

Sie ist eine Zeile mit vier Teilen: Nummer, **Prüfe**, **Mache**, **Erwarte**.

Daniel liest sie, bevor sich etwas bewegt.

## Gut

```
Schritt 2 · Prüfe: Klick auf die Schaltfläche erhöht den Zähler · Mache: Zeiger auf die Schaltfläche, einmal klicken, neues Bild · Erwarte: Zähler steht auf 1
Schritt 9 · Prüfe: Chat-Nachricht kommt an · Mache: in den Chat klicken, Hallo tippen, Enter · Erwarte: Text steht im Chat des anderen
Planänderung: Schritt 3 · Prüfe: Text im Feld · Mache: Feld hat Fokus, ich tippe direkt · Erwarte: Hallo Welt steht im Feld
```

## Schwach (und warum)

- `Teste das Feld.` — es fehlt, *was* genau geprüft und *wie*. Daniel kann nicht mitgehen.
- `Schritt 3 · Mache alles Mögliche.` — kein Erwartungswert, danach lässt sich nichts bestätigen.
- Fünf Absätze Erklärung — die Raute ist keine Dokumentation, das Lange kommt ins Protokoll.

## Nach dem Schritt (gesehen)

`test gesehen "Zähler zeigt 1, Schaltfläche leicht eingedrückt" ok`

Beschreibe, was **auf dem Bild** ist. „Wie erwartet“ allein sagt nichts.

## Als Zuschauer

`test zuschauer "Auf meinem Bild steht der Zähler auf 1" bestaetigt`

Immer erst ein eigenes Bild holen.

Siehst du etwas anderes, ist `widerspruch` die hilfreichste Antwort.
