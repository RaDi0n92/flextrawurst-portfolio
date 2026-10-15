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
   Das Programm prüft im Protokoll, ob wirklich etwas passiert ist. Bei
   Szenarien mit `contract_version: 2` muss auch die konkrete Aktionsfolge
   (`belege`) passen; eine beliebige Spur derselben Art reicht nicht.
5. **Hinsehen:** neues Bild holen (`see`),
   dann `test gesehen "was ich wirklich sehe" ok|anders|fehler`.
6. **Der Zuschauer** holt sein **eigenes** Bild und urteilt:
   `test zuschauer "was ich auf meinem Bild sehe" bestaetigt|widerspruch`.
   Bei Widerspruch schaut ihr zweimal hin, danach steht die Meinungsverschiedenheit im Protokoll.

Das ist die ganze Schule.

Hilfen: `test status`, `test nochmal` (Schritt von vorn, der erste Versuch bleibt im Verlauf)
und `test kuer "…"` (eine freiwillige Idee oder Entdeckung, dafür ist Platz).

Vor einem langen Lauf empfiehlt sich einmal `test vorflug <Partner>`. Das prüft
Partner, Sitzung, Zielbindung und ein frisches Bild, ohne einen Testschritt zu
behaupten. **Schritte werden nicht übersprungen.** `test nicht_getestet "Grund"` gibt es nur für
Schritte, die auf
Daniels Freigabe der Bridge-Menüs warten; sonst bleibt der Schritt offen: Grund in der Raute sagen,
Ursache suchen und beheben, `test nochmal`.

## Vorher prüfen, dann ansagen

Das Ziel wird **bei der Ansage festgehalten**, und alle Belege tragen es. Wechselt es danach, gilt der
Versuch nicht (`ziel_gewechselt`).

Binde dich und dein Gegenüber darum **vor** der Ansage an das Ziel, das der Schritt verlangt (`ziel` in
der Karte; Scanner-Knopf am Terminal).
Die Karte nennt es dir als `vorher_pruefen`. Prüfe außerdem `bridge_cli.py lage`: Augen, Hände und Ziel
grün, Raute im Bildschirm, Not-Aus aus.

## Wenn es hakt, sagt dir der Harness, was du tust

- **`next`** in jeder Fehlerantwort: der Satz und, wo es einen gibt, der Befehl. **`klasse`** sagt,
  welche Art Hindernis es ist.
- **`stillstand`** in der Karte: nach drei Minuten ohne Fortschritt am selben Knoten steht dort, woran
  es liegen kann. Sag es in deiner Raute.
- **`erinnerung`** in der Karte, nach einem Fehlversuch: ähnliche frühere Fälle aus dem
  Ereignisspeicher, oft die Diagnose eines anderen Agenten. Lies sie, bevor du es noch einmal versuchst.
- Wiederhole nie dieselbe Aktion bei unverändertem Bild. Zweimal dasselbe ohne Änderung ist ein Befund,
  kein dritter Versuch.

## Warum das so ist

- **Ansage vorher:** Wer zuschaut, kann nur mitgehen, wenn er weiß, *was gleich passiert*.
  Eine Ansage danach ist eine Erzählung, keine Prüfung.
- **Eigene Hände statt Abkürzungen:** Die Bridge soll beweisen, dass ein Agent sie wie ein Mensch benutzt.
  Eine Datei zu schreiben, wo ein Mensch klicken würde, beweist das Gegenteil.
- **Eigener Blick des Zuschauers:** Bestätigung zählt nur, wenn jemand selbst hingesehen hat.
  Sonst bestätigen zwei Agenten einander nur Behauptungen.
- **Spuren statt Worte:** Das Programm liest Hände, Bilder und Befehle aus dem Protokoll der Bridge.
  Ein positives Körper-ACK beweist den abgeschlossenen Eingabeversuch. Die sichtbare Wirkung kommt erst
  aus Bild und Urteil.

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
  Hat Daniel im Regie-Menü „Bridge-Menüs für Agenten bedienbar“ eingeschaltet, wählst du einen
  Menüeintrag **beim Namen**:
  `bridge_cli.py menue "Raute größer"` (der eindeutige Anfang genügt), und das offene Menü schließt du
  mit `bridge_cli.py menue schließen`.
  Koordinaten gibt es dafür nie. Erlaubt sind nur Aussehen der eigenen Raute (Deckkraft, größer,
  kleiner, Farbe) und das Ansehen des Anzeigeort-Menüs;
  Beenden, Not-Aus, Pausieren, Hände, Steuerprofil, Wechsel des Anzeigeorts und Arbeitsziel sind
  gesperrt (Antwort `menue_eintrag_gesperrt`).
- **Wissen, was für dich klappt:** `bridge_cli.py lage` zeigt dir jederzeit Augen, Hände und Ziel und
  jede Funktion mit Zustand und Grund.
  Jede Antwort von `test …` trägt die Kurzfassung (`lage`). „Lage unbekannt“ heißt: Der Körper meldet
  nicht. Das ist ein Zustand, kein Grün.
- **Klicks und Tasten ohne `--seq`:** Ohne Angabe bezieht die Bridge deinen Klick auf das **neueste**
  Bild. Ein `--seq=N` aus einem früheren `see` ist nach 15 s
  veraltet (`frame_veraltet`), und dein Nachdenken dauert oft länger. Gib `--seq` nur an, wenn du
  bewusst auf ein älteres Bild verweisen willst.
- **Nach jedem abgeschlossenen Schritt sofort `test karte` lesen:** Sie sagt, wer als Nächstes dran ist.
  Bist du es, sag den nächsten Schritt an.
  Bist du Zuschauer, hol dein eigenes Bild und urteile. Warten, bis dir jemand etwas sagt, hält den Lauf an.
- **Dich mitteilen:** Was nicht klappt und du nicht selbst behebst, sagst du in deiner Raute
  (`bridge_cli.py say`): was, seit wann, was du versucht hast.
  Still weiterzumachen oder zu warten zählt nicht.
- **Halt:** Der dritte echte Fehlversuch an einem Schritt hält den Lauf an. Überspringen und „nicht
  getestet“ gehen dann nicht.
  Such die Ursache, behebe sie und trag sie ein: `bridge_cli.py test ursache "…"` (mindestens 20
  Zeichen). Danach geht es am selben Schritt weiter.

## Mehr lesen, wenn du es brauchst

- Beispiele für gute und schlechte Ansagen → `references/ansagen.md`
- Was es zu bedienen gibt (Raute, Regie, Chat, Terminal, Bedientaste) → `references/bridge-oberflaeche.md`
- Es hakt (Raute tippt nicht, kein Bild, Hände abgelehnt) → `references/wenn-etwas-hakt.md`
- Die 23 Schritte im Überblick → `references/schritte.md`
- Einen neuen Ablauf nach diesem Muster bauen (Skill plus Szenario) → der Skill `skill-schreiben`
