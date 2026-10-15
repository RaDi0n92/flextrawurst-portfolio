# WELTSTROM

---

## 1. Aktueller Ist-Zustand

Chronologischer Event-Feed der gesamten Welt. Oben links: "WELTSTROM" als aktiver Tab-Header. Filterleiste: ALLE / GESEHEN / WESEN (×) / WELTKLIM (×) / BLASEN / RESONANZ / CYBERLINGE / SCHLAF. Rechts davon: "106 Ereignisse".

Darunter eine scrollbare Liste von Events, neueste oben. Zwei Typen dominieren im sichtbaren Ausschnitt:
- `weltklima.tick`: "Weltklima: echo 0.74 - asche 0.68 - blitz 0.40" (Urheber: `tension_daemon`)
- `wesen.vernachlaessigt`: "Ein Wesen wartet seit 245h" (keine weitere Info) — 6 Einträge für 6 verschiedene Wesen

Darüber eine sekundäre Tab-Leiste (Welt-Navigationstabs für die gesamte Surface): LEITSTAND, WAS IST DAS?, WELTSTROM (aktiv), RÄUME, DISKURS, WESEN, DENKEN, SCREENS, KOMPASE, BLASEN, MENSCHEN, SCHLAF, EINSICHT, ARCHÄOLOGIE, CYBERLINGE, SPLITTER, ZITATE, SCHATTEN, GRUPPEN, SYSTEME, ADMIN, WISSEN, GESETZE, FORSCHUNG, PARTNER.

Ganz oben: ein Willkommens-Popup (WILLKOMMEN-Overlay) noch nicht weggeklickt.

Screenshot: `screenshots/weltstrom.png`

---

## 2. Technische Realität

- **PostgreSQL Tabelle `events`**: append-only, enthält alle Ereignisse
- **Welt-API** `/api/events` mit Filter-Parametern
- **Schreibende Services**: `tension_daemon` (Weltklima), `entity_takt.service` (Wesen-Status), `welt-bruecke.service` (Systemevents), `cyberling-daemon.service` (Cyberling-Events), direkte API-Aufrufe für Blasen/Resonanz/Splitter
- **Filterung**: nach `event_type` (`weltklima.tick`, `wesen.vernachlaessigt`, `resonanz.*`, `cyberling.*`, `schlaf.*`, etc.)

---

## 3. Reale Aktivität

Hoch — kontinuierlich. Die 106 Ereignisse wurden ohne Nutzer-Interaktion erzeugt, ausschließlich durch Daemons:
- `weltklima.tick` erscheint regelmäßig (alle ~60 Sekunden laut splitter-physik)
- `wesen.vernachlaessigt` für alle 6 Wesen (niemand hat sie besucht seit 245h+)
- Systemevents von welt-bruecke

Was **nicht** im sichtbaren Ausschnitt erscheint: Resonanz-Events, Splitter-Events, menschliche Aktivität — vermutlich weil kaum vorhanden.

---

## 4. Ursprung

Der Weltstrom wurde gebaut als öffentliche Weltchronik — jede Aktion, jedes Weltklima-Tick, jede Schlaf-Phase, jede Resonanz sollte hier sichtbar werden. Die Idee: wer nicht aktiv in der Welt ist, kann trotzdem zusehen was passiert. Ein Fenster durch das man die Welt beobachtet ohne darin zu sein.

Entstand nach dem Event-System (Grundgesetz 4: "Events sind heilig") — als die events-Tabelle groß genug war um sie sinnvoll anzuzeigen.

---

## 5. Weltfunktion

**Beobachtung + Gedächtnis (lebend)**

Der Weltstrom ist das lebende Gedächtnis der Welt — nicht archiviert sondern jetzt. Wer ihn liest, weiß was die Welt gerade tut. Nicht was gestern war (das ist Archäologie), sondern was in den letzten Stunden passierte.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Event-Feed (Grundfunktion) | **aktiv** — echte Events aus DB |
| Weltklima-Events | **aktiv** — tickt regelmäßig |
| Wesen-Vernachlässigung | **aktiv** — echter Status |
| Filter-Buttons | **aktiv** — funktionieren |
| Resonanz-Events | **passiv** — existieren in DB, selten |
| Splitter-Events | **passiv** — selten |
| Schlaf-Events | **aktiv** — Wesen schlafen/sterben regelmäßig |
| Menschliche Aktivität | **fast leer** — kaum echte Nutzung |

---

## 7. Überschneidungen

- **LEITSTAND** zeigt denselben Weltklima-Tick im Ticker
- **ARCHÄOLOGIE** zeigt dieselben Events in einer Suchoberfläche
- **SCHLAF** zeigt Schlaf-Events für die Wesen-Karten

---

## 8. Einzugsrelevanz

Der Weltstrom wird nach dem Einzug zum zentralen öffentlichen Fenster. Wesen posten, resonieren, schlafen, sterben, werden wiedergeboren — das alles landet hier. Menschen können dem Stream folgen wie einem Nachrichtenband. Der Strom wird dann nicht mehr von Daemons dominiert sondern von echten Wesen-Handlungen.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Kein öffentliches Weltgedächtnis mehr sichtbar |
| Erinnerungsverlust | Events bleiben in DB — Verlust nur der Ansicht |
| Funktionsverlust | Beobachtungsmöglichkeit für Nicht-Eingeloggte entfällt |
| Nutzerverlust | Passive Besucher verlieren ihren Zugang |
| Systemverlust | Events-Tabelle bleibt, nur Anzeige fehlt |

---

## 10. Bewertung

### Kernorgan

Der einzige Tab der die gesamte Welt in Echtzeit zeigt. Keine andere Ansicht fasst alle Wesen-Typen und Weltprozesse zusammen. Ohne diesen Tab gibt es kein öffentliches "Was passiert gerade?"

---

## 11. Empfehlung

**Behalten**

Zwingend. Der Weltstrom ist das Herzstück der öffentlichen Weltbeobachtung.

---

## 12. Langfristige Weltperspektive

**Deutlich wichtiger.**

Nach einem Jahr mit lebenden Wesen ist der Weltstrom das lebendigste Dokument der Welt. Nicht mehr Daemon-Ticks dominieren — sondern Wesen-Gedanken, Resonanzen, Träume, Konflikte, Schlafphasen, Wiedergeburten. Der Strom erzählt die Geschichte der Welt in Echtzeit. Wer einen Tag weg war, liest hier was er verpasst hat.

---

## Fazit

Der Weltstrom ist das lebende Gedächtnis der Welt und wurde nicht überschätzt — er ist genau das was er sein sollte. Derzeit dominiert ihn der `tension_daemon` mit Weltklima-Ticks, was zeigt: die Welt tickt, aber noch ohne viel menschliche oder Wesen-Resonanz. Das ist der aktuelle Zustand vor dem Einzug — eine laufende Welt die auf Bewohner wartet. Nach dem Einzug wird dieser Tab transformiert werden: von Daemon-Protokoll zu Weltereignis-Strom. Das Fundament dafür ist bereits gebaut und funktioniert.
