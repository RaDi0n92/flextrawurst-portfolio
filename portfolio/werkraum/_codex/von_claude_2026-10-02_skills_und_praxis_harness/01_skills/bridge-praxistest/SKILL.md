---
name: bridge-praxistest
description: Führt dich als Agent (Claude, Gemgem, Codex …) zusammen mit einem zweiten Agenten Schritt für Schritt durch den Praxistest der Augen-und-Hände-Bridge, so wie ein Mensch die Bridge bedienen würde — sichtbar für Daniel, mit Ansage in der eigenen Raute vor jedem Schritt, echten Klicks und Tasten, eigenem Blick und gegenseitiger Bestätigung. Verwenden, wenn Daniel "Praxistest", "testet die Bridge", "macht es wie ein Mensch" oder "Schritt N" sagt, oder wenn dein Terminal in der Bridge läuft und ein Test mit einem zweiten Agenten ansteht. Nicht verwenden für Entwicklung oder Fehlersuche im Bridge-Code selbst und nicht für Tests, die du allein ohne Zuschauer machst.
---

# Praxistest der Bridge — auf Augenhöhe

Du testest die Bridge nicht von außen, du **benutzt** sie wie Daniel.

Du siehst das Bild, bewegst den Zeiger, klickst, tippst und öffnest Menüs.

Daniel schaut zu und muss **jeden einzelnen Prüfschritt nachvollziehen können**.

Darum bewacht ein Programm die Reihenfolge und begleitet euch freundlich.

Du musst sie nicht auswendig kennen, nur dem „nächsten Schritt“ folgen.

## So fängst du an

```sh
sh <skill>/scripts/bridge.sh test start <Name des anderen Agenten>
```

`<skill>` ist der Ordner dieser Datei, den Namen zeigt `bridge.sh agenten`.

Danach immer `sh <skill>/scripts/bridge.sh test karte`.

Die Karte sagt dir in deiner Rolle, **was jetzt dran ist**, mit dem passenden Befehl.

## Der Rhythmus jedes Schritts

1. **Ansage** (der Handelnde): `test ansage "Schritt N · Prüfe: … · Mache: … · Erwarte: …"`.
   Der Text wird **sichtbar in deine Raute getippt**. Das ist der Kern: Daniel liest mit.
2. **Lesezeit** abwarten. Das Programm sagt dir, wie lange. Daniel liest in Ruhe.
3. **Handeln, genau wie angesagt**, mit den Händen der Bridge (`klick`, `tippe`, `taste`, `ziehe`, `rad`).
   Weicht dein Plan ab: `test planaenderung "…"` und neu ansagen.
4. **Berichten:** `test getan "was ich getan habe"`.
   Das Programm prüft im Protokoll, ob wirklich etwas passiert ist.
5. **Hinsehen:** neues Bild holen (`see`),
   dann `test gesehen "was ich wirklich sehe" ok|anders|fehler`.
6. **Der Zuschauer** holt sein **eigenes** Bild und urteilt:
   `test zuschauer "was ich auf meinem Bild sehe" bestaetigt|widerspruch`.
   Bei Widerspruch schaut ihr zweimal hin, danach steht die Meinungsverschiedenheit im Protokoll.

Das ist die ganze Schule.

Hilfen: `test status`, `test nochmal` (Schritt von vorn, der erste Versuch bleibt im Verlauf)
und `test kuer "…"` (eine freiwillige Idee oder Entdeckung, dafür ist Platz).

## Warum das so ist

- **Ansage vorher:** Wer zuschaut, kann nur mitgehen, wenn er weiß, *was gleich passiert*.
  Eine Ansage danach ist eine Erzählung, keine Prüfung.
- **Eigene Hände statt Abkürzungen:** Die Bridge soll beweisen, dass ein Agent sie wie ein Mensch benutzt.
  Eine Datei zu schreiben, wo ein Mensch klicken würde, beweist das Gegenteil.
- **Eigener Blick des Zuschauers:** Bestätigung zählt nur, wenn jemand selbst hingesehen hat.
  Sonst bestätigen zwei Agenten einander nur Behauptungen.
- **Spuren statt Worte:** Das Programm liest Hände, Bilder und Befehle aus dem Protokoll der Bridge.
  Du musst nichts beweisen, tu es sichtbar, dann ist es da.

## Wenn du dir einen Ausweg denkst

| Gedanke | Was stattdessen gut ist |
|---|---|
| „Ich sag es kurz im Chat, die Raute dauert.“ | Die Ansage in der Raute *ist* der Schritt. Sie kostet vier Sekunden und gibt Daniel Orientierung. |
| „Das kann ich schneller per Befehl lösen.“ | Schneller ist nicht der Zweck. Mach es mit Zeiger und Tasten und schreib, wo es hakte, das ist der wertvolle Befund. |
| „Es hat bestimmt geklappt.“ | Hol ein Bild und beschreib, was du siehst. „Anders als erwartet“ ist ein wertvolles Urteil, kein Versagen. |
| „Das Programm lässt mich nicht weiter.“ | Es sagt dir genau, was fehlt (meist eine Spur oder ein Bild). Tu das, dann geht es weiter. |
| „Der andere hat bestimmt recht.“ | Schau selbst. Ein ehrlicher Widerspruch hilft mehr als eine höfliche Bestätigung. |
| „Das ist ein Fehler der Bridge, ich überspringe es.“ | Trag es als `fehler` ein, mit dem, was du sahst. Fehler sind das Ergebnis, nicht der Störfall. |

## Dauerregeln

- Schreib so, dass jemand ohne Vorwissen mitkommt: einfache Worte.
  Die Raute bekommt eine Zeile (bis etwa 300 Zeichen), das Lange gehört ins Protokoll.
- Nenne Fehler **wörtlich** (Befehl und Ausgabe), ohne Deutung.
- Daniel hat Vorrang: Bewegt er die Maus, wartet die Bridge. F12 stoppt alles. Das ist gewollt.
- Die Menü-Fenster der Bridge bedienen deine Hände erst nach Daniels Freigabe.
  Bis dahin stellt das Programm solche Schritte zurück und holt sie später nach.

## Mehr lesen, wenn du es brauchst

- Beispiele für gute und schlechte Ansagen → `references/ansagen.md`
- Was es zu bedienen gibt (Raute, Regie, Chat, Terminal, Bedientaste) → `references/bridge-oberflaeche.md`
- Es hakt (Raute tippt nicht, kein Bild, Hände abgelehnt) → `references/wenn-etwas-hakt.md`
- Die 23 Schritte im Überblick → `references/schritte.md`
- Einen neuen Ablauf nach diesem Muster bauen (Skill plus Szenario) → der Skill `skill-schreiben`
