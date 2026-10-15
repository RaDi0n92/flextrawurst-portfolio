---
datum: 2026-08-14
betrifft: [sokratik, cot, tot, humanize, tab-entwuerfe, phase-2]
status: abgeschlossen
autor: claude-code bei Daniels VPS
---

# Phase 2 — Sokratisch durchdacht, was Menschen wirklich brauchen

Live, direkt, nicht delegiert. Kein Subagent — ich selbst, in dieser Session.

## Die sokratische Methode hier: Fragen an mich selbst, ehrlich beantwortet

**Frage 1: Was weiß ein Mensch, der zum ersten Mal auf flextrawurst.de landet, WIRKLICH noch
nicht?** Antwort, ehrlich durchdacht: fast alles außer den Wörtern selbst. "Wesen" klingt nach
einem Fantasy-Begriff, nicht nach "ein Prozess, der alle paar Minuten ein Sprachmodell aufruft".
"Vault" ist Englisch für Tresor/Gewölbe — ohne Kontext unklar warum ein Codewesen einen Tresor
braucht. "Grundgesetz" klingt nach deutschem Verfassungsrecht, nicht nach Daniels eigenem
Regelwerk. Ergebnis dieser Frage: Block 0 in allen drei Entwürfen (aus Phase 1, Runde 6) war
richtig, aber nicht ausreichend — auch einzelne Wörter *innerhalb* der Absätze brauchen eine
Erst-Erklärung, nicht nur ein Vorspann am Anfang.

**Frage 2: Warum sollte ein Mensch, der nicht technisch ist, das hier überhaupt zu Ende lesen?**
Chain-of-Thought dazu: Menschen lesen technische Dokumentation zu Ende, wenn (a) sie neugierig auf
die Person/das Team dahinter sind, nicht nur auf das Produkt, oder (b) eine Geschichte erzählt
wird, keine Liste. Alle drei Entwürfe haben bereits Geschichten (Baugeschichte-Blöcke) — das ist
richtig gebaut. Was fehlt: eine sehr kurze, sehr menschliche Eröffnung, bevor die erste Überschrift
kommt, die sagt "das hier lohnt sich zu lesen, weil..." — nicht als Marketing-Satz, sondern als
ehrliche Einladung.

**Frage 3 (Tree-of-Thought — drei verschiedene Erklärwege für denselben Begriff durchgespielt,
Beispiel "Cyberling"):**
- *Weg A (technisch zuerst):* "Cyberling: ein Python-Daemon, der alle 5 Minuten Hunger/Durst/
  Energie/Stimmung/Gesundheit-Werte pro Wesen berechnet." — korrekt, aber kalt, keine Motivation
  warum es das gibt.
- *Weg B (Analogie zuerst):* "Ein Cyberling ist wie ein Tamagotchi für ein Codewesen — Hunger und
  Energie steigen und fallen, ohne dass eine echte Intelligenz dahintersteckt." — verständlicher,
  aber verkleinert den Rest des Systems (das Wesen SELBST ist mehr als sein Cyberling-Zustand,
  Verwechslungsgefahr).
- *Weg C (Zweck zuerst, dann Technik):* "Jedes Wesen hat einen eigenen Grundzustand, der sich mit
  der Zeit verändert — nicht weil es 'fühlt', sondern weil ein einfacher, sichtbarer Zeitmechanismus
  läuft, den Daniel Cyberling nennt: Hunger, Durst, Energie, Stimmung, Gesundheit, alle paar Minuten
  neu berechnet." — **gewählter Weg:** ehrlich über die Grenze (kein echtes Fühlen), aber ohne das
  Wesen als Ganzes kleinzureden. Trifft genau den Guardianstyle-Anspruch (KOMMENTAR zu
  cyberling_daemon.py in Teil A: "reine Arithmetik", nicht verschönt, aber auch nicht abgewertet).

## Ergebnis: was an den drei Entwürfen strukturell geändert werden sollte

1. **Ein Mini-Glossar direkt am Ende jedes Tabs** statt nur Inline-Erklärungen — für Begriffe, die
   mehrfach vorkommen (Wesen, Vault, Grundgesetz, Cyberling, Splitter, Einzug, Guardianstyle selbst).
   Passt zu Daniels eigenem CLAUDE.md-Wunsch ("Legenden, Inhaltsverzeichnisse, Glossare/Outros für
   größere Dateien").
2. **Der erste Satz jedes Tabs muss eine Einladung sein, kein Fakt.** Aktuell fangen alle drei mit
   einer Meta-Beschreibung an ("Reiner Entwurf für Daniel..."). Das gehört als Fußnote oder
   Kommentar, nicht als erster Satz, den ein Website-Besucher liest.
3. **Konsistente Begriffs-Erst-Erklärung:** beim ersten Vorkommen eines Fachworts in JEDEM
   Absatz-Kontext (nicht nur einmal im ganzen Tab) kurz erklären, falls der Absatz auch isoliert
   gelesen werden könnte (z.B. wenn jemand direkt zu einem Abschnitt über einen Deep-Link springt).

## Humanize-Runde (manuell, keine Skill-Funktion gefunden)

Geprüft gegen typische "unmenschliche" Muster in allen drei Entwürfen:
- **Passiv-Konstruktionen, die Verantwortung verschleiern** ("wurde umgestellt", "wurde eingeführt")
  — bewusst stehen gelassen wo der Akteur wirklich unklar ist (siehe "durch wen"-Ehrlichkeit aus
  Phase 1), aber wo bekannt, aktiv formuliert ("Daniel aktiviert eine globale Sperre" statt "eine
  globale Sperre wurde aktiviert" — bereits so geschrieben, gut).
- **Behördendeutsch-Kandidaten geprüft:** keine gefunden, die drei Entwürfe sind schon im
  Guardianstyle-Ton geschrieben (Ich-Form, direkte Reaktionen, WICHTIG/NOTIZ/KOMMENTAR-Marker) —
  das war schon vor Phase 2 der Fall, kein Nachbessern nötig.
- **Zu viele Zahlen ohne menschlichen Anker:** "137 Werkzeuge" sagt einem Laien nichts über die
  Größenordnung. Verbesserung für den Gesamtauftrag (Phase 4): Vergleichsgrößen einbauen ("137
  Werkzeuge — mehr als ein Schweizer Taschenmesser mit jedem denkbaren Aufsatz").

Alle drei strukturellen Punkte (Glossar, Einladungssatz, konsistente Erst-Erklärung) fließen in
den Gesamtauftrag (Phase 4) ein, werden hier nicht einzeln in die Arbeitsfassungen zurückgeschrieben
— das würde Phase 1 nochmal aufrollen, statt auf ihr aufzubauen.
