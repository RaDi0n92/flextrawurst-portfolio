---
name: skill-schreiben
description: Zeigt, wie du eine Skill-Datei (SKILL.md) für Agenten der Bridge schreibst, prüfst und verbesserst, und wie die Programm-Harness (Graph aus Knoten und Kanten, Szenario als JSON) einen Ablauf freundlich begleitet und belegt. Verwenden, wenn Daniel "schreib einen Skill", "Skill verbessern" oder "damit sie das wirklich befolgen" sagt oder ein wiederkehrender Ablauf (Test, Übergabe, Prüfung) zuverlässig durchlaufen werden soll. Nicht verwenden für einmalige Aufgaben, reine Dokumentation oder Claude-Code-Einstellungen.
---

# Skills schreiben mit der Harness

Ein Skill ist gut, wenn ein Agent ihn im richtigen Moment findet und wirklich befolgt.

Dafür tun Text und Programm je ihren Teil:

- **Text** (SKILL.md) erklärt das Warum und gibt Urteilsvermögen.
- **Programm** (Harness) bewacht Reihenfolge, Zeiten, Rollen und Belege;
  fehlt ein Beleg, bleibt der Schritt offen und nennt den Grund.

## Was gehört wohin?

| Es soll ... | Wohin |
|---|---|
| verstanden oder abgewogen werden | Text, mit Begründung |
| in fester Reihenfolge, mit Wartezeit, Rollen oder Beleg laufen | Szenario-Graph (Harness) |
| mechanisch und wiederholbar sein | Skript in `scripts/` |
| nur selten nachgeschlagen werden | `references/` |

Was ein Agent nicht vergessen darf, steht nicht in einem Satz, sondern in einem Knoten.

## Der Weg

1. **Absicht:** Was soll der Agent können, wann springt der Skill an, woran erkennt man "fertig"?
2. **Gerüst:** `python3 <skill>/scripts/skill_geruest.py <name> [--mit-szenario]`.
3. **Beschreibung:** dritte Person, Auslöser *und* Gegenfälle, höchstens 1024 Zeichen.
   Sie sagt, wann der Skill passt, nicht, wie er funktioniert.
4. **Körper:** kurz, im Imperativ, jede wichtige Regel mit Warum.
   Dauerregeln stehen getrennt von Einmal-Schritten.
   Eine Tabelle "Wenn du dir einen Ausweg denkst" nimmt Ausreden freundlich vorweg.
5. **Harness:** Braucht der Ablauf Reihenfolge, Zeit, Rollen oder Belege, schreib ein Szenario.
6. **Prüfen:** `python3 <skill>/scripts/skill_pruefen.py <ordner>`.
   Zusätzlich, wenn vorhanden, `quick_validate.py` des Skill-Creators.
7. **Erproben:** drei echte Anfragen, mit und ohne Skill, Ergebnisse nebeneinander ansehen, überarbeiten.
   Die Evals des Skill-Creators (`run_eval.py`) tragen das, wenn vorhanden.

## Regeln für den Text

- Kurz und flach: unter 500 Zeilen, Verweise eine Ebene tief.
  Im Text steht, wann welche Datei zu lesen ist, sonst wird sie nie geöffnet.
- Warum statt Drohung: Wer den Zweck versteht, löst auch den Fall, den du nicht vorhergesehen hast.
- Belege statt Behauptungen: Jeder Schritt endet mit etwas, das man ansehen kann.
- Ton: Sag, was als Nächstes zu tun ist. Ein Fehler ist ein Befund, kein Vorwurf.
- Ein gutes und ein schwaches Beispiel, mit Begründung, schlagen jede Beschreibung.
- Absätze kurz (etwa 100 Zeichen), Daniels Stimme roh lassen.

## Die Harness mitdenken

Sie liegt in `src/augen_haende_bridge/praxis/` auf `harness.py`:

Knoten, Kanten mit Signalen, Läufe mit Verlauf.

- Ein neuer Ablauf ist meist nur ein Szenario (JSON).
  Start: `bridge_cli.py test start <Partner> --szenario=<name>`.
- Ein Knoten öffnet sich nur mit echter Spur. Fehlt sie, kommt genaue Hilfe statt einer Sperre.
- In `contract_version: 2` beschreibt `belege` die erwartete konkrete Aktionsfolge.
  Eine grobe Spur (`haende`, `seed` oder `loop`) ist dann nur der erste Filter.
- Wirkungsbelege bleiben getrennt: Körperquittung bedeutet Eingabeversuch abgeschlossen,
  Bild bedeutet beobachteter Zustand, zwei Urteile bedeuten gegenseitige Agentenbestätigung.
  Das ist keine unabhängige menschliche Abnahme.
- Wächst das System (neue Spurart, Rolle oder Kante), erweitere Python.
  Schreib dazu einen Test mit Gegenprobe.
- Jeder Befehl im Skill muss es im Werkzeug geben. `skill_pruefen.py` prüft das.

## Mehr lesen

- Was Profis sagen, mit Quellen → `references/profi-wissen.md`
- Szenario: Felder, Spuren, Erweitern → `references/szenario-schema.md`
- Vorlagen, vom Gerüst benutzt → `references/vorlage-skill.md.txt`, `references/vorlage-szenario.json.txt`
