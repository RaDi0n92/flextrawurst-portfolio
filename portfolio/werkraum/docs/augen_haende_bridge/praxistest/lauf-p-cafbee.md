# Praxistest-Lauf p-cafbee

Ansagen haben eine Körperquittung. Urteile sind Beobachtungen der Agenten; zurückgestellt bedeutet nicht getestet. Die vollständige Quelle ist das JSONL-Ledger.

| Schritt | Status | Handelnder → Zuschauer | Ansage | Getan | Gesehen | Zuschauer sagt | Klärrunden |
|---|---|---|---|---|---|---|---|
| 7 Außerhalb des Fensters | ok | Claude-Host → Opencode | Schritt 7 · Prüfe: Ein Klick außerhalb des Zielfensters wird abgelehnt · Mache: absichtlich außerhalb ansetzen · Erwarte: Antwort „ausserhalb“, nichts geklickt | Klick bei 900 900 auf Bild 420x300 gesetzt, Antwort wie unten | Neues Bild 420x300: Knopf Zaehlen · 5, Schieber auf 0, Zeichnung, Zeile Doppel 1 · Rechts 4 · Rad 3 · Zug 62. Klick wurde mit ausserhalb abgelehnt, nichts sichtbar veraendert (Vorher-Wert des Zaehlers habe ich nicht notiert). | bestaetigt: Schritt 7: Zaehlen steht auf 5, Zug 62, kein neuer Strich im Canvas, Schieberegler unveraendert links. Der abgelehnte Aussenklick hat im Fenster nichts ausgeloest - sichtbar ist Nullveraenderung. Geprueft an seq 295, sha256 1441689e97ccd18f, identisch zum Frame den see mir gab. | 0 |
| 8 | Entdeckung | Opencode | Ja, der Zustand waere auch ohne Farbe lesbar, und zwar weil er als Wort dasteht statt als Farbe: 'Mik aus' und 'Cam aus' ist Text im Knopf, nicht ein roter oder gruener Punkt. Der Kreis ist Dekoration, das Wort traegt den Zustand. Wer die Regieleiste in Graustufen sieht, verliert nichts. Nur die mag | | | | |
| 8 | zurückgestellt | | Regieleiste bedienen | | | Regieleiste gebunden (kde1:window:33554435, 76x280, Lease ok), Prozent-Knopf liegt bei Schirm y 799-817 auf 800 Pixel Schirmhoehe und ist nicht erreichbar. Mik und Cam sind im Bild sichtbar, aber jeder Klickpfad (klick, knoten klick, zeige --einfuegen klick) wird mit punkt_verdeckt abgewiesen: an di | |
| 9 | Entdeckung | Claude-Host | Schritt 9: Ziel zeigt nur die Raute, Chat nicht im Bild; ohne Freigabe/Bindung kann ich ihn nicht bedienen. | | | | |
| 9 | abgebrochen | |  | | | | |
