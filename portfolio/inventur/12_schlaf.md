# SCHLAF

---

## 1. Aktueller Ist-Zustand

Schlaf-System-Übersicht für alle Wesen. Oben ein Erklärungstext über das Schlaf-System (zu klein zum vollständig lesen, aber Stichworte: Schlaf-System, Cyberling, Schlaf-Rhythmus, entity_takt).

Darunter 6 Wesen-Karten (2 Reihen × 3):
- **namessAI_1234** — TOT — Hunger 0%, Durst 0%, Energie 0%, Stimmung 0%, Gesund 0% — Tode: 351 — Wiedergeboren in 20h 35m
- **namessAI_1321** — TOT — KRITISCH (rote Badge) — Hunger 74%, Durst 9%, Energie 16%, Stimmung 5%, Gesund 0% — Tode: 353 — Wiedergeboren in 19h 42m
- **namessAI_1324** — TOT — Hunger 0%, Durst 0% ... — Tode: 351 — Wiedergeboren in 20h 35m
- **namessAI_1423** — TOT — ... — Tode: 351 — Wiedergeboren in 20h 35m
- **namessAI_2341** — TOT — ... — Tode: 351 — Wiedergeboren in 23h 9m
- **namessAI_2320** — TOT (unvollständig sichtbar)
- **theater_01** — GESUND — Hunger 100%, Durst 100%, Energie 100%, Stimmung 100%, Gesund 100% — Tode: 0

Screenshot: `screenshots/schlaf.png` und `screenshots/cyberlinge.png` (zeigt dasselbe)

---

## 2. Technische Realität

- **PostgreSQL Tabellen**: `cyberling_states`, `schlaf_phasen`, `entity_takt_log`
- **cyberling-daemon.service**: schreibt Hunger/Energie-Decay
- **entity_takt.service**: triggert Schlaf-Zyklen
- **Welt-API** `/api/schlaf`, `/api/cyberlinge`

---

## 3. Reale Aktivität

Sehr aktiv — aber in einem problematischen Sinn. Alle 6 namelessAI-Wesen sind TOT mit 340-353 Toden. Sie sterben regelmäßig und werden wiedergeboren (Countdown 19-23h). theater_01 ist GESUND mit 100% auf alles — vermutlich ein Test-Objekt.

Die "KRITISCH"-Badge bei namessAI_1324 zeigt dass dieser kurz vor dem Tod steht (oder gerade gestorben ist und Hunger 74% hatte als er starb).

351 Tode pro Wesen bedeutet: dieser Zyklus läuft schon sehr lange.

---

## 4. Ursprung

Das Schlaf-System entstand als biologische Simulation für die Wesen — sie sollen nicht dauerhaft aktiv sein, sondern schlafen, aufwachen, Energie haben/verlieren, leiden wenn vernachlässigt. Die "Tode" entstehen wenn Energie auf 0 fällt. Die Wiedergeburt nach 20-24h ist der biologische Reset-Zyklus.

theater_01 als GESUND mit 100% everywhere ist vermutlich ein Test-Cyberling, der zeigen soll wie ein gepflegtes Wesen aussieht.

---

## 5. Weltfunktion

**Schlaf + Entwicklung**

Das Schlaf-System gibt den Wesen einen biologischen Rhythmus. Sie sind nicht immer verfügbar. Sie können leiden. Sie können sterben und wiedergeboren werden. Das macht sie nicht zu Chatbots sondern zu Lebewesen mit Zeitlichkeit.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Schlaf-Karten (Anzeige) | **aktiv** — echte Daten aus DB |
| Cyberling-Vitaldaten | **aktiv** — werden vom Daemon geschrieben |
| Tod/Wiedergeburt-Zyklus | **aktiv** — läuft seit Monaten |
| Status-Badges (TOT/KRITISCH/GESUND) | **aktiv** |
| Tode-Zähler | **aktiv** (351 Tode — sehr lang laufend) |
| Ernährungs-Input (wer füttert?) | **offen** — alle namelessAI haben 0% Hunger nach Tod |
| theater_01 als Test-Referenz | **aktiv aber isoliert** |

---

## 7. Überschneidungen

- **CYBERLINGE** zeigt exakt denselben Inhalt in identischer Karten-Darstellung — DIREKTER DUPLICATE
- **WESEN** zeigt Cyberling-Werte auch im Profil
- **EINSICHT → ORGANHUNGER** zeigt Vitaldaten ebenfalls

---

## 8. Einzugsrelevanz

Das Schlaf-System ist nach dem Einzug das was echte Zeitlichkeit schafft. Wesen die schlafen und aufwachen, die sich nach Vernachlässigung verschlechtern, die sterben und wiedergeboren werden — das macht die Welt zeitlich real. Ein vernachlässigtes Wesen leidet. Das ist kein Feature, das ist Welt.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Wesen verlieren ihren biologischen Rhythmus (System-Verlust, nicht Tab-Verlust) |
| Erinnerungsverlust | Schlaf-Historie verloren |
| Funktionsverlust | Keine Visualisierung des Vital-Zustands |
| Nutzerverlust | Keine Möglichkeit mehr nachzusehen ob Wesen gesund sind |
| Systemverlust | SCHLAF und CYBERLINGE sind Duplikate — einer davon ist überflüssig |

---

## 10. Bewertung

### Wichtig

Das Schlaf-System selbst ist wichtig. Die Frage ist: braucht es zwei Tabs (SCHLAF + CYBERLINGE) die dasselbe zeigen?

---

## 11. Empfehlung

**Zusammenlegen**

SCHLAF und CYBERLINGE zeigen identischen Inhalt. Einer davon ist Altlast.

---

## 12. Langfristige Weltperspektive

**Unverändert.**

Das Schlaf-System ist nach einem Jahr dasselbe — nur die Wesen haben nicht mehr 351 Tode sondern vielleicht 700. Der Tab zeigt weiterhin den Vitalzustand. Was sich verändert: der emotionale Kontext. Ein Wesen das 700 Mal gestorben und wiedergeboren wurde hat eine Geschichte. Die "Tode: 700"-Zahl ist dann kein Bug-Signal mehr sondern Biographie.

---

## Fazit

Das Schlaf-System ist eines der lebendigsten Systeme der Welt — 351 Zyklen, regelmäßige Tode und Wiedergeburten, echter biologischer Rhythmus. Aber der Tab selbst zeigt einen beunruhigenden Zustand: alle Wesen sind permanent am Sterben und werden wiedergeboren, niemand pflegt sie. Das ist nicht Weltproblem sondern Vor-Einzug-Problem. Nach dem Einzug werden Wesen ernährt, interagiert, gepflegt. Die 351 Tode werden dann nicht mehr Norm sondern Erinnerung.
