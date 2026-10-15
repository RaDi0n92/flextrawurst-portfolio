# Drehbuch Praxistest: Claude und Gemgem testen die Bridge gegenseitig (vd1, später Windows)

Zweck: alles von G01 bis G15 mit echter Maus, Tastatur und Fenstern der Reihe nach durchspielen und **belegen**, nicht behaupten. Zwei Agenten (Claude, Gemgem) wechseln sich ab: einer handelt, der andere beobachtet und bestätigt oder widerspricht.

## Regel 0 — nichts im Verborgenen (Daniel, 2026-10-02, „rule no1 bei der bridge“)
Jeder Schritt wird so ausgeführt, **wie ein Mensch ihn ausführen müsste, und so, dass Daniel es auf dem Bildschirm sieht**: Mauszeiger bewegt sich, es wird sichtbar geklickt, getippt, gezogen, Fenster öffnen und schließen sich, Banner und Menüs erscheinen. Dasselbe Bild für Daniel, Handelnden und Beobachter.
* Ein Schritt, der nur per Befehlsausgabe, Datei oder Protokoll „belegt“ ist, gilt als **„nicht sichtbar geprüft“** und nicht als ok. Das gilt auch für Schritte, die eine Oberfläche betreffen (Banner, Raute, Chat, Zeichnen, Menüs, Klicks, Tippen, Ziehen, Fokus).
* Der Handelnde führt **mit den Händen der Bridge** aus (`klick`, `tippe`, `taste`, `ziehe`, `rad`), nicht über Abkürzungen (keine Dateien schreiben, wo ein Mensch klicken würde, kein direktes Setzen von Zuständen).
* Der Beobachter bestätigt **anhand eines Bildes** des Bildschirms (`see` oder ein von Daniel sichtbares Ergebnis), nennt Bildpfad und beschreibt, was er sieht.
* Datenschritte (z. B. Reihenfolge von Nachrichten, Dateiinhalt, Kapsel-Hash) dürfen zusätzlich per Ausgabe belegt werden, **aber die Oberfläche dazu muss mitgezeigt sein** (Nachricht erscheint im Chat und im Terminal des Empfängers, sichtbar).
* Kann ein Schritt nicht sichtbar gemacht werden, steht das als **Fehler** mit Grund da, nicht als ok.
* Die **Bindung** eines Testfensters macht Daniel wie ein Nutzer (Scanner-Knopf im Terminal); vorher gibt es kein Ziel und die Hände melden „kein_fenster_ziel“.

## Regeln
1. Jeder Schritt bekommt eine Zeile im Ergebnisprotokoll `praxistest/ERGEBNISSE_<ort>.md` (`vd1` oder `windows`): `| Schritt | Handelnder | Beobachter | Ergebnis (ok / Fehler / offen) | Beleg |`. Beleg = Befehlsausgabe, Bildpfad (`see`), Dateiinhalt. Ohne Beleg gilt ein Schritt als **offen**.
2. „ok“ nur, wenn der **Beobachter** es bestätigt hat. Der Handelnde allein genügt nicht.
3. Ein Fehler wird **genau so** eingetragen, wie er auftrat (Befehl, Ausgabe), ohne Deutung. Danach weiter mit dem nächsten Schritt.
4. Nichts außerhalb der Testfenster anfassen. F12 (Not-Aus) und Daniels Maus gehen immer vor.
5. Daniel kann jederzeit eingreifen; wenn er die Maus bewegt, wartet die Bridge. Das ist gewollt, kein Fehler.
6. Windows: dieselben Schritte; was dort nicht geht, wird als „Fehler“ mit Ausgabe eingetragen, nicht umgangen.

## Rollen
- **Claude:** handelt in den Schritten mit ungerader Nummer, beobachtet in den geraden.
- **Gemgem:** umgekehrt.
- Zum Beobachten: `bridge_cli.py see` (Bild des Ziels des anderen anfordern geht nur über dessen Ausgabe: der Handelnde nennt den Bildpfad im Chat, der Beobachter liest ihn), `bridge_cli.py agenten`, Dateien lesen.

## Ablauf
### A. Körper und Terminal (G01–G05)
1. Raute, Terminal, Chat und Regieleiste sind sichtbar; Name und Farbe stimmen. (Beobachter beschreibt, was er sieht.)
2. Im Terminal tippen: `echo ä€😀` → erscheint unverändert (Umlaute, Sonderzeichen).
3. `bridge_cli.py say "Hallo vom <Name>"` → Banner und Box erscheinen, überdecken sich nicht.
4. Chat: Nachricht an den anderen Agenten; sie kommt im Terminal des anderen an.

### B. Anzeigeorte, Bild (G06, G06.7, G08)
5. Ziel binden (Scanner) auf ein Testfenster (z. B. ein Texteditor); `bridge_cli.py see` nennt Pfad, Alter, Quelle „fenster“.
6. Das Fenster teilweise verdecken; `see` zeigt trotzdem das ganze Fenster.
7. Zeichnen im Ziel: ein Pfeil und ein Text; der andere sieht es im Bild.

### C. Mehr-Agenten (G09)
8. `bridge_cli.py agenten` listet beide mit Strom und Zustand.
9. `bridge_cli.py sende <anderer> "Test 1"` bis „Test 5“ hintereinander: Reihenfolge 1–5 im Terminal des anderen.
10. `bridge_cli.py auftrag <anderer> "Schreibe ok in /tmp/praxistest_auftrag.txt"`; der andere meldet `auftrag-status … fertig`; der Handelnde prüft die Datei.

### D. Hände (G10)
11. Ohne Lease: `bridge_cli.py klick 100 100` → abgelehnt „lease_fehlt“.
12. `bridge_cli.py lease`, dann `tippe "Hallo"` in einen Editor und `taste "Strg+A"`, `taste "Strg+C"`: Text steht im Editor, Beobachter bestätigt per Bild.
13. `klick` auf eine Schaltfläche des Testfensters; die Wirkung tritt ein (Beobachter bestätigt).
14. Daniel bewegt kurz die Maus: die Bridge hält an und läuft danach weiter (Daniel meldet es).
15. F12 drücken (Daniel): alles steht, `klick` ist danach abgelehnt, bis die Lease neu genommen ist.
16. Controller (nur wenn Treiber/Gerät da): `controller knopf a`; sonst als „offen“ mit Grund eintragen.

### E. WorldDOM (G11)
17. `bridge_cli.py weltdom`: Knoten mit Herkunft, Alter und Vertrauen.
18. `knoten <ID> lesen` für einen Knopf; Text stimmt mit dem Bild überein (Beobachter prüft).
19. `anker "Marke" 200 200`, dann `weltdom --herkunft=authored`: Anker steht in der Liste.
20. `profil speichern "Praxis" --programm=<Name des Testprogramms>`, Fenster schließen und neu öffnen, `profil laden "Praxis"`: Anker steht an derselben relativen Stelle.
21. `markiert`, danach `see`: nummerierte Rahmen im Bild, Tabelle stimmt zu mindestens einem Knoten.

### F. Abläufe (G12)
22. Einen kleinen Ablauf mit `ablauf neu` speichern (zwei Zustandsknoten), zweimal ändern: zwei Versionen.
23. `ablauf start <id> --modi=shadow`: nichts passiert; `--modi=daniel_gate`: Daniel bekommt die Frage; Nein → nichts.
24. Ablauf mit `erwartet` (ein Knopf, der nicht da ist): Start meldet `ablauf_gealtert`.

### G. Kapseln, Zeitlinie, Hauhaucs (G13, G14)
25. `kapsel moment --art=agent "Praxistest"`, `kapsel zeige K`: „unverändert“ ist True; Lücken stehen mit Grund da.
26. `kapsel zeitlinie`: Marken vorhanden; dabei kommt nichts im Terminal an.
27. `chat "Hallo"` und `chat "Was habe ich eben gefragt?"`: das Modell kennt den ersten Austausch (nur wenn der Chat-Server erreichbar ist, sonst „offen“ mit Ausgabe).
28. `pult zeige`, `pult halbieren`, `pult zurueck`.
29. `beobachtung start <anderer>`, ein paar Nachrichten, `beobachtung status`: „aufgezeichnet“ steigt, „verarbeitet“ bleibt 0; `beobachtung stop`.

### H. Wissen und Handeln (G15)
30. `seed vorschlagen kontext "Hinweis" --inhalt="Bitte zuerst messen." --an=<anderer> --kapseln=<K aus Schritt 25>`.
31. `seed ausliefern <id>`: Daniel bekommt die Frage und sagt Ja; der andere findet den Text in seinem Terminal.
32. Daniel zieht den Seed über sein Menü zurück; `seed zeige <id>` meldet „zurueckgezogen“.
33. `seed vorschlagen loop "Zaehler" --inhalt=<Ablauf-ID> --budget='{"max_laeufe":3,"intervall_s":1}'`, ausliefern (Daniel Ja), `loop status`: endet mit Grund „budget_laeufe_erschoepft“; ein zweiter Loop wird mit `loop stopp` beendet, danach beginnt nichts Neues.

## Nach dem Test
Beide Agenten schreiben je eine Zusammenfassung (nur Belegtes) an das Ende der Ergebnisdatei: Anzahl ok, Fehler, offen; die Liste der Fehler mit Befehl und Ausgabe. Daniel liest zuerst die Fehlerliste.

## Vorbereitung für Schritt 5 bis 16 (Hände, Bild, WorldDOM)
Diese Schritte brauchen ein **gebundenes Testfenster**; ohne Bindung antwortet die Bridge mit „kein_fenster_ziel“ (kein Fehler der Bridge, sondern fehlende Vorbereitung). Auf vd1 läuft dafür das Programm „Bridge-Testfenster“ (Schaltfläche, Eingabefeld, Regler, Zeichenfläche; sein Stand steht laufend in `/tmp/bridge_testfenster_stand.json` auf dem Host und in vd1). Daniel bindet es je Agent: in dessen Terminal mit gehaltener Strg+Alt auf den Scanner-Knopf (Fadenkreuz unten rechts) klicken und „Bridge-Testfenster“ wählen.
