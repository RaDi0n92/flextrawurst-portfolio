# SYSTEME

---

## 1. Aktueller Ist-Zustand

System-Übersicht aller laufenden Services. Header: "LAUFENDE SYSTEME · [Zahl]" mit Subtext.

9 sichtbare System-Kacheln:
- **Welt-API** — AKTIV (grüne Badge)
- **Frontserver** — (kein AKTIV-Badge sichtbar)
- **GENI** — (Beschreibung schwer lesbar)
- **Splitter-Physik** — (Beschreibungstext)
- **PostgreSQL** — (flextrawurst DB)
- **Welt-Brücke** — (kurze Beschreibung)
- **Entity-Takt** — (Takt-Beschreibung)
- **Cyberling-Daemon** — (Decay/Action-Loop)
- **Garfles-Engine** — (?)

Screenshot: `screenshots/systeme.png`

---

## 2. Technische Realität

- **Systemd-Services**: welt-api, welt-bruecke, entity_takt, cyberling-daemon, splitter-physik
- **Direktabfrage**: systemd-status oder Ping-Checks
- **Welt-API** `/api/systeme` oder `/api/health`

---

## 3. Reale Aktivität

Services laufen — das ist auch durch den Weltstrom-Ticker bestätigt. Die Kacheln zeigen Status-Informationen. Welt-API hat explizit AKTIV-Badge.

---

## 4. Ursprung

SYSTEME entstand als transparente Systemübersicht — Besucher sollen sehen welche Infrastruktur die Welt trägt. Keine Black Box, sondern offene Architektur. Gleichzeitig Monitor für Daniel.

---

## 5. Weltfunktion

**Transparenz + Beobachtung**

SYSTEME macht die technische Infrastruktur sichtbar. Das gehört zur Welt-Transparenz — diese Welt verbirgt nicht wie sie gebaut ist.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Bereich | Status |
|---|---|
| Systemkarten | **aktiv** — aus DB oder direkten Status-Checks |
| AKTIV-Badge | **aktiv** — mindestens Welt-API |
| Echtzeitstatus | **vorbereitet** |
| Beschreibungstexte | **aktiv** |
| "Garfles-Engine" | **unklar** — existiert das wirklich? |

---

## 7. Überschneidungen

- **LEITSTAND** zeigt Service-Status in der Ticker-Leiste
- Redundanz in der Status-Anzeige

---

## 8. Einzugsrelevanz

Wenig Veränderung. SYSTEME ist Admin-Info — nach dem Einzug relevanter für Forscher die die Infrastruktur verstehen wollen.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Transparenz-Schicht fehlt |
| Erinnerungsverlust | Keine |
| Funktionsverlust | System-Monitoring |
| Nutzerverlust | Gering — meiste Nutzer schauen hier nicht |
| Systemverlust | Keine |

---

## 10. Bewertung

### Nützlich

Gut für Forscher und für Daniel. Für gewöhnliche Besucher weniger relevant.

---

## 11. Empfehlung

**Behalten**

---

## 12. Langfristige Weltperspektive

**Unverändert.**

Der SYSTEME-Tab zeigt nach einem Jahr noch immer welche Services laufen. Die Services selbst haben sich vielleicht verändert (neue Daemons, alte abgeschaltet), aber die Funktion ist dieselbe. Interessanter nach einem Jahr: die Uptime-Geschichte. Welche Services hatten Ausfälle? Wann? Das wäre wertvolles System-Gedächtnis.

---

## Fazit

SYSTEME ist der technisch ehrlichste Tab der Welt: er zeigt was unter der Haube ist. Das ist selten in einer Welt, und das ist gut. Nicht für jeden Besucher relevant — aber für die die es interessiert: hier sieht man die Maschinen die die Welt am Laufen halten. Die "Garfles-Engine" ist ein kleines Rätsel das sich erst beim genaueren Hinschauen im Code klärt.
