# LEITSTAND

---

## 1. Aktueller Ist-Zustand

Der Leitstand zeigt eine interaktive Netzwerk-Karte der Welt. Im Zentrum des Bildschirms schweben mehrere große, leuchtende Kreise in Türkis, Grün, Orange und Rot — sie sind durch weiße Linien verbunden. Jeder Kreis trägt einen Namen (Räume der Welt). Die Kreise pulsieren leicht.

Links eine schmale Sidebar mit kategorisierten Einträgen: Weltdurchgang, Begegnungszonen, Bezirke, Gruppen, Syntheseorte, Symbionten — jeweils mit Badge-Zahlen (z.B. "14", "3"). Rechts eine weitere Sidebar mit Statistiken: aktuelle Zählungen (6, 29, 29), darunter "WELTKLIMA" mit Messwerten (echo, asche, blitz), dann ein Bereich "WELTLEBEN" mit weiteren Angaben.

Im oberen Banner eine scrollende Ticker-Leiste mit Live-Status: "Systembrücke aktiv", "Entity-Takt: System aktiv", "7 Räume definiert", "Frontend aktiv", "PostgreSQL flextrawurst — aktiv", "splitter-physik.service aktiv", "Welt-API aktiv", "GENI Wahrnehmungsschicht aktiv".

Am unteren Rand ein breiter Footerbereich mit kleineren Tab-Links aller anderen Bereiche.

Screenshot: `screenshots/leitstand.png`

---

## 2. Technische Realität

- **Welt-API** Port 8030: `/api/raeume`, `/api/weltklima/aktuell`, `/api/events/recent`
- **PostgreSQL**: Tabellen `raeume`, `events`, `weltklima_snapshots`, `cyberlinge` (für Live-Counts)
- **welt-bruecke.service**: Synchronisiert Weltzustand laufend
- **splitter-physik.service**: Schreibt Weltklima-Ticks
- **entity_takt.service**: Schreibt Wesen-Events die im Ticker erscheinen

---

## 3. Reale Aktivität

Sehr hoch. Das Weltklima tickt regelmäßig (echo 0.74, asche 0.68, blitz 0.40 sichtbar im Screenshot). Die Ticker-Leiste zeigt Echtzeit-Aktivität aller Services. Die Kreiskarte zeigt 7 definierte Räume. Die Weltzustand-Brücke synchronisiert kontinuierlich.

---

## 4. Ursprung

Der Leitstand war das erste sichtbare Fenster in die Welt — gebaut als Kontrollzentrum für Daniel bevor öffentliche Oberflächen existierten. Die Idee: ein Admin soll auf einen Blick sehen was in der Welt passiert. Name "Leitstand" analog zu einem Kraftwerk-Kontrollraum — zentrales Überwachungssystem.

Die Netzwerkkarte der Räume wurde gebaut um die Weltstruktur visuell zu machen, bevor sie inhaltlich befüllt war.

---

## 5. Weltfunktion

**Orientierung + Beobachtung**

Der Leitstand ist das Cockpit der Welt. Wer wissen will was lebt, was sich bewegt, was gerade passiert, schaut hierher. Nicht für Interaktion — für Überblick.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Räume-Netzwerk (Visualisierung) | **aktiv** — zeigt echte DB-Räume |
| Weltklima-Messwerte | **aktiv** — tickt in Echtzeit |
| Ticker-Leiste (Service-Status) | **aktiv** — echte Services |
| Statistik-Sidebar (Zahlen) | **aktiv** — echte Counts |
| Linien zwischen Räumen | **simuliert** — statisch gezogen, keine echte Topologie |
| Interaktive Raumkarte (klickbar?) | **vorbereitet** — Kreise sehen anklickbar aus, unklar ob etwas passiert |

---

## 7. Überschneidungen

- **WELTSTROM** zeigt ebenfalls den Live-Ticker
- **SYSTEME** zeigt denselben Service-Status in Textform
- **RÄUME** zeigt dieselben Räume mit anderer Darstellung
- Der Weltklima-Wert erscheint auch im WELTSTROM als Event-Einträge

---

## 8. Einzugsrelevanz

Mit lebenden Wesen wird der Leitstand zum wichtigsten Orientierungsraum für Daniel und für Besucher die verstehen wollen was gerade in der Welt passiert. Die Karte könnte dann zeigen wo Wesen sich aufhalten, welche Räume gerade "belebt" sind, wo Resonanz entsteht. Dann wäre er kein Admin-Tool mehr sondern ein öffentlicher Weltblick.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Kein Einstiegspunkt mehr für globale Orientierung |
| Erinnerungsverlust | Keine Verluste — keine historischen Daten hier |
| Funktionsverlust | Service-Status-Überwachung muss woanders hin |
| Nutzerverlust | Besucher verlieren den ersten visuellen "Wow"-Moment |
| Systemverlust | Weltklima-Messwerte brauchen neues Zuhause |

---

## 10. Bewertung

### Wichtig

Nicht unersetzlich — aber der einzige Tab mit visueller Weltüberblick-Funktion. Die Ticker-Leiste und Weltklima-Messwerte sind anderswo nicht bündig zusammengefasst.

---

## 11. Empfehlung

**Behalten**

Der Leitstand ist der visuelle Eintrittspunkt für Beobachter. Noch kein Kernorgan — aber nahe daran.

---

## 12. Langfristige Weltperspektive

**Deutlich wichtiger.**

Der Leitstand zeigt dann nicht mehr leere Räume und Daemon-Ticks, sondern eine lebendige Weltkarte: Wesen in Räumen, aktive Diskurse, Resonanz-Hotspots, Traumzonen. Die Netzwerkkarte hat dann Gewicht — Besucher sehen auf einen Blick welche Teile der Welt gerade atmen. Der Leitstand wird zum natürlichen Einstiegspunkt für alle die die Welt beobachten ohne Teil von ihr zu sein.

---

## Fazit

Der Leitstand wurde überschätzt als "Kontrollzentrum" und ist eher ein Überblicksfenster. Die Netzwerkkarte der Räume wirkt visuell stark, ist aber inhaltlich noch statisch. Was wirklich lebt: Weltklima-Ticker und Service-Status. Was noch wartet: interaktive Raumnavigation, Wesen-Positionen, lebendige Topologie. Nach dem Wesen-Einzug könnte der Leitstand zum wichtigsten öffentlichen Fenster der Welt werden — wer ist gerade wo, was passiert gerade. Jetzt ist er vor allem Administrations-Aesthetik.
