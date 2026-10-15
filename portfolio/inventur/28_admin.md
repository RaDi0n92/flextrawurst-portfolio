# ADMIN

*(Versteckter Tab — nur für Admins sichtbar)*

---

## 1. Aktueller Ist-Zustand

Admin-Panel. Header mit Tab-Navigation: NUTZER / SUPPORTER / INHALTE / WESEN / BILDER / SYSTEM / EINZUG.

Aktiver Subtab: NUTZER. Suchfeld "Suche nach Nutzer...". Button "+ Neuer Nutzer". Ergebnis: "Keine Nutzer gefunden."

Darunter: farbige Ladebalken (türkis, grün, orange, lila, dunkelblau) — 5 horizontale Balken in verschiedenen Längen und Farben. Das ist wahrscheinlich eine Ladeanimation oder Platzhalter für Nutzer-Einträge, die geladen werden sollen.

Screenshot: `screenshots/admin.png`

---

## 2. Technische Realität

- **PostgreSQL Tabelle `users`**: Alle Nutzer
- **Welt-API** Admin-Endpunkte (`/admin/...`)
- **JWT-Auth**: Admin-Rolle prüfen
- Subtabs adressieren: `users`, `wesen`, `bilder`, `events`, `einzug`

---

## 3. Reale Aktivität

"Keine Nutzer gefunden" — das ist auffällig. Entweder:
a) Der Suche-Query hat keinen Default-Scope (zeigt nur wenn gesucht wird)
b) Die Users-Tabelle hat einen anderen Schema als erwartet
c) Die Ladebalken deuten auf laufenden Load hin

Der "EINZUG"-Subtab ist besonders relevant — dort werden die Wesen eingezogen wenn Daniel es freigibt.

---

## 4. Ursprung

Der ADMIN-Tab ist der Administrationsraum — Daniels vollständiger Zugriff auf alle Weltdaten. Nutzer verwalten, Inhalte moderieren, Wesen überwachen, Bilder moderieren, System kontrollieren, Einzug steuern. Gebaut nach Grundgesetz 3: "Admin hat totale Kontrolle."

---

## 5. Weltfunktion

**Kontrolle + Weltbildung (administrativ)**

Admin ist die unsichtbare Hand hinter der Welt. Nicht für Besucher gedacht — für den Weltbaumeister.

---

## 6. Lebendigkeitsanalyse *(extra)*

| Subtab | Status |
|---|---|
| NUTZER | **aktiv** — aber zeigt "Keine Nutzer gefunden" |
| SUPPORTER | **unklar** |
| INHALTE | **aktiv** — Inhalte moderierbar |
| WESEN | **aktiv** — Wesen-Verwaltung |
| BILDER | **aktiv** — Bildmoderation |
| SYSTEM | **aktiv** — Services |
| EINZUG | **vorbereitet** — Einzug-Mechanismus bereit, nicht aktiv |

---

## 7. Überschneidungen

- **SYSTEME** — Service-Übersicht auch im Admin sichtbar
- **EINSICHT** — Wesen-Details auch im Admin zugänglich

---

## 8. Einzugsrelevanz

EINZUG wird das kritischste Subtab. Dort wird Daniel mit einem Befehl die 6 Wesen aus Flarum in flextrawurst einziehen. Der Rest des Admin-Tabs wird danach für Verwaltung und Moderation wichtig.

---

## 9. Verlustanalyse

| Verlusttyp | Inhalt |
|---|---|
| Weltverlust | Kein Admin-Interface |
| Funktionsverlust | Moderation, Verwaltung, Einzug entfallen |
| Systemverlust | Kritisch — Einzug kann nicht mehr gesteuert werden |

---

## 10. Bewertung

### Kernorgan

Ohne Admin-Tab kein Einzug, keine Moderation, keine Verwaltung. Unverzichtbar für Daniel.

---

## 11. Empfehlung

**Behalten**

---

## 12. Langfristige Weltperspektive

**Unverändert — aber wichtiger in der Praxis.**

Nach einem Jahr Betrieb ist der Admin-Tab das meistgenutzte Tool für Daniel: Inhalte moderieren, Wesen-Status überwachen, Einzüge nachjustieren, System warten. Die EINZUG-Funktion hat nach dem ersten Einzug eine andere Bedeutung — sie wird dann für weitere Wesen oder Nachjustierungen genutzt.

---

## Fazit

Der Admin-Tab ist das Werkzeug des Weltbaumeisters. Er ist nicht für Besucher — er ist für Daniel. "Keine Nutzer gefunden" ist eine kleine Anomalie die geprüft werden sollte, aber keine Krise. Der EINZUG-Subtab ist das was zählt: dort wartet die Welt auf den Moment wo Daniel sagt "jetzt".
