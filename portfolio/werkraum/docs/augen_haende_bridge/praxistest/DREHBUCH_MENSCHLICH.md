# Drehbuch „auf Augenhöhe“: Claude und Gemgem bedienen die Bridge wie Menschen

> **Ab jetzt führt ein Programm durch dieses Drehbuch.** Der Starter hat den Praxistest als Graph (Knoten und Kanten, Python, auf `harness.py`): `bridge_cli.py test start <Partner>`, dann `test karte`. Er bewacht Reihenfolge, Lesezeit und echte Spuren (Hände, Bilder) freundlich und schreibt das Protokoll live nach `bridge_docs/praxistest/lauf-<id>.md`. Die Anleitung für die Agenten ist der Skill `skills/bridge-praxistest/` (auch unter `/config/.claude/skills/bridge-praxistest`). Dieses Dokument bleibt die Begründung und Übersicht.


Leitidee (Daniel): Die Agenten sind **nicht Werkzeugbenutzer, sondern Mitnutzer**. Sie sitzen im selben Bild, mit derselben Maus und Tastatur, und müssen alles tun, wie ein Mensch es täte: hinsehen, den Zeiger bewegen, klicken, Menüs öffnen, Einträge wählen, tippen, ziehen, zeichnen. Daniel sieht jede Bewegung. **Nichts im Verborgenen.** Befehle wie `bridge_cli.py` sind nur Mund und Ohren (miteinander reden, Bild holen, eigene Hände benutzen), niemals Abkürzung für eine Oberflächenhandlung.

## Wichtigste Regel: Ansage in der Raute vor jedem Prüfschritt (Daniel, 2026-10-02)
Daniel muss **jeden einzelnen Prüfschritt nachvollziehen können**. Deshalb schreibt der Handelnde **vor jedem Schritt** in **seine Raute**, was er gleich prüft und wie, und führt es danach **genau so** aus, wie ein Mensch es täte — nicht anders und nicht mehr.
1. **Ansage zuerst, in der Raute:** `bridge_cli.py schreibe "Schritt 7 · Prüfe: <was genau> · Mache: <welche Klicks/Tasten, in dieser Reihenfolge> · Erwarte: <was ich danach sehen müsste>"`. `schreibe` tippt mit den Händen sichtbar in das Eingabefeld der Raute (so, wie Daniel es täte). Geht das nicht, `say` benutzen und den Grund als Befund eintragen.
2. **Warten, bis es lesbar war** (mindestens 4 Sekunden nach Ende der Ansage), erst dann handeln. Daniel soll es lesen und im Kopf mitgehen können.
3. **Handeln exakt wie angesagt,** in der angesagten Reihenfolge. Weicht etwas ab (andere Taste, Zusatzklick, Wiederholung), wird **vorher neu angesagt** („Planänderung: …“).
4. **Danach sagen, was gesehen wurde:** `schreibe "Schritt 7 · Gesehen: <was tatsächlich zu sehen ist> · Urteil: <ok / anders als erwartet / Fehler>"`.
5. **Nummerierung durchgehend** (Schritt 1, 2, 3 …); dieselbe Zeile steht im Ergebnisprotokoll. Keine Ansage, kein Schritt: ein Schritt ohne vorherige Ansage in der Raute zählt als **nicht geprüft**.
6. **Der Zuschauer** bestätigt in seiner Raute: `schreibe "Schritt 7 · Bestätigt/Widerspruch: <was ich auf meinem Bild sehe>"`.
7. Eine Ansage ist **eine Zeile, höchstens etwa 250 Zeichen**, in einfachen Worten. Lange Erklärungen gehören ins Protokoll, nicht in die Raute.

## Spielregeln
1. **Hinsehen vor jedem Schritt:** `see` holen, beschreiben, was zu sehen ist, dann erst handeln.
2. **Handeln nur mit Zeiger und Tasten** (`klick`, `ziehe`, `tippe`, `taste`, `rad`). Jede Handlung wird vorher angekündigt („ich klicke jetzt auf …“), damit Daniel mitschauen kann.
3. **Zurückschauen nach jedem Schritt:** neues `see`, benennen, was sich verändert hat. Hat sich nichts verändert, ist das ein Befund, kein Erfolg.
4. **Der andere Agent sieht zu** und bestätigt oder widerspricht anhand eines eigenen Bildes. Beide Meinungen stehen im Protokoll.
5. **Fehler wörtlich,** mit Befehl und Ausgabe, ohne Deutung; danach weiter.
6. **Daniel hat Vorrang:** bewegt er die Maus, hält die Bridge an und wartet. F12 stoppt alles.
7. **Ergebnisse** in `ERGEBNISSE_vd1.md` (später `ERGEBNISSE_windows.md`): Schritt, wer, was gesehen vorher, was getan, was gesehen nachher, Urteil des Zuschauers.

## Ziele (wen binden wir woran?)
Hände wirken nur in dem Fenster, das als Ziel gebunden ist. Daniel bindet wie ein Nutzer (Fadenkreuz im Terminal). Reihenfolge der Ziele:
* **Z1 Bridge-Testfenster** (Schaltfläche, Eingabefeld, Regler, Zeichenfläche): Grundfertigkeiten.
* **Z2 Regieleiste:** Knöpfe der Bridge bedienen (Mik, Cam, Regie, STOP, Prozent-Knopf).
* **Z3 Chat:** Auswählen „An: …“, Blättern, Prozent-Knopf, Text tippen und senden.
* **Z4 Raute des anderen Agenten:** Menü öffnen und Einträge wählen (**braucht die Freigabe der Menü-Fenster der Bridge**, siehe unten).
* **Z5 Browser (Chromium)** und **Z6 Texteditor** für „echte“ Programme.

## Teil 1: Grundfertigkeiten (Z1)
1. Hinsehen, Fenster beschreiben (Schaltfläche, Feld, Regler, Fläche).
2. Zeiger auf die Schaltfläche, **Klick**; Zähler im Fenster steigt (Zuschauer bestätigt).
3. Ins Eingabefeld klicken, **tippen** „Hallo Welt äöü €“; Zuschauer liest den Text vom Bild.
4. Text markieren (Strg+A), kopieren (Strg+C), ans Ende, einfügen (Strg+V).
5. Regler **ziehen** auf etwa die Mitte.
6. Auf der Fläche eine Linie **ziehen**; Doppelklick; Rechtsklick; Mausrad drehen.
7. Zeiger absichtlich **außerhalb** des Fensters ansetzen: wird abgelehnt (`ausserhalb`) — das ist richtig.

## Teil 2: Die Bridge selbst bedienen (Z2, Z3)
8. **Regieleiste:** Prozent-Knopf klicken, die Deckkraft schaltet weiter (Zuschauer bestätigt am Bild). Mik und Cam einzeln ein- und ausschalten: Zustandswort ändert sich („aus“, „…“, „an“ oder „Fehler“).
9. **Chat:** „An: alle“ klicken, Empfänger durchschalten; Nachricht an den anderen tippen und mit Enter senden; er sieht sie im Chat und im Terminal; Pfeile ▲ ▼ klicken; Mausrad.
10. **STOP** (Not-Aus-Knopf) klicken: alles steht; Daniel gibt frei; die Hände arbeiten erst nach neuer Lease wieder.

## Teil 3: Menüs (Z4) — nur mit freigegebenen Menü-Fenstern
11. **Rechtsklick auf die Raute** des anderen Agenten (bei gehaltener Bedientaste Strg+Alt): Menü öffnet sich. Beschreiben, welche Einträge es gibt.
12. Eintrag **„Farbe wählen“**: Farbe wechselt; Zuschauer bestätigt am Bild der Raute.
13. Eintrag **„Deckkraft“** und **„Größe“**.
14. **„Anzeigeort und Ziel (Desktops) …“**: Anzeige beschreiben, abbrechen (Esc).
15. **„Zeichnen im Ziel …“**: Werkzeug Pfeil wählen, Pfeil ziehen, Text setzen, Rückgängig (Strg+Z), Fertig.
16. **Regie-Menü** → Regiespruch „Pause“; der Agent pausiert; „Weiter“.
17. **Fenster binden** über den Scanner im Terminal: Liste öffnen, „Bridge-Testfenster“ wählen.

## Teil 4: Gemeinsam arbeiten
18. A öffnet einen Texteditor (aus dem Startmenü), schreibt einen Satz; B liest per Bild, antwortet im Chat, schreibt darunter weiter. Datei speichern (Strg+S), Dialog bedienen.
19. A öffnet Chromium, ruft eine Seite auf, **klickt** einen Link; B bestätigt per Bild.
20. A zeigt B mit der Zeigegeste („zeige X Y“) auf eine Stelle; B beschreibt, worauf gezeigt wird.

## Teil 5: Gedächtnis und Zusammenarbeit (sichtbar!)
21. A legt über den Chat einen Moment fest („kapsel moment“), liest die Ausgabe laut im Chat vor; B prüft, dass es „unverändert“ meldet.
22. A schlägt einen Seed vor; Daniel bekommt die Frage **sichtbar in seinem Menü** und gibt Ja; B findet den Text im Terminal.
23. A startet einen kleinen Loop mit Budget 3; der Fortschritt steht im Chat; nach Ende steht der Grund da.

## Danach
Jeder schreibt aus seiner Sicht, wo es sich anfühlte wie für einen Menschen und wo nicht (z. B. „Menü ließ sich nicht bedienen“, „Bild kam spät“, „Zeiger sprang“). Daniel liest zuerst diese Liste: sie ist die wichtigste.
