# Die 23 Schritte im Überblick

Handelnder wechselt: ungerade Schritte A (wer den Test startet), gerade Schritte B.

Der andere schaut zu und bestätigt.

Schritte mit „braucht Menü-Freigabe“ werden zurückgestellt, bis Daniel die Menü-Fenster der Bridge freigibt.

| Nr | Teil | Titel | Prüfe | Mache | Erwarte | Bemerkung |
|---|---|---|---|---|---|---|
| 1 | Grundfertigkeiten | Hinsehen | Was zeigt das Testfenster: Schaltfläche, Eingabefeld, Regler, Zeichenfläche? | Bild holen (see) und beschreiben | vier Bedienelemente benannt |  |
| 2 | Grundfertigkeiten | Klicken | Ein Klick auf die Schaltfläche erhöht den Zähler im Fenster | Zeiger auf die Schaltfläche, einmal klicken, neues Bild holen | Zähler steht eins höher |  |
| 3 | Grundfertigkeiten | Tippen | Tippen im Eingabefeld, auch Umlaute und Euro-Zeichen | ins Eingabefeld klicken, Text tippen, Bild holen | Text steht unverändert im Feld |  |
| 4 | Grundfertigkeiten | Kopieren und Einfügen | Strg+A, Strg+C, Ende, Strg+V verdoppelt den Text | Tastenkombinationen nacheinander senden, Bild holen | Text steht zweimal im Feld |  |
| 5 | Grundfertigkeiten | Regler ziehen | Der Regler lässt sich mit gedrückter Maus auf etwa die Mitte ziehen | Griff anfassen, ziehen, loslassen, Bild holen | Regler steht ungefähr in der Mitte |  |
| 6 | Grundfertigkeiten | Zeichenfläche, Doppelklick, Rechtsklick, Mausrad | Linie ziehen, Doppelklick, Rechtsklick und Mausrad werden im Fenster gezählt | nacheinander ausführen, Bild holen | Zähler für Doppel, Rechts und Rad steigen |  |
| 7 | Grundfertigkeiten | Außerhalb des Fensters | Ein Klick außerhalb des Zielfensters wird abgelehnt | absichtlich außerhalb ansetzen | Antwort „ausserhalb“, nichts geklickt |  |
| 8 | Die Bridge selbst | Regieleiste bedienen | Prozent-Knopf schaltet die Deckkraft weiter; Mik und Cam zeigen ihren Zustand als Wort | Knöpfe einzeln klicken, nach jedem Klick Bild holen | Prozentzahl ändert sich, Zustandswort wechselt |  |
| 9 | Die Bridge selbst | Chat bedienen | Empfänger „An: …“ durchschalten, Nachricht schreiben und senden, Pfeile ▲ ▼ klicken | im Chat klicken und tippen, Enter | Nachricht erscheint im Chat und im Terminal des anderen |  |
| 10 | Die Bridge selbst | STOP | Der STOP-Knopf stoppt alles; danach geht nichts, bis Daniel freigibt | STOP klicken, dann einen Klick versuchen | Klick wird mit Grund abgelehnt, Daniel gibt frei, danach neue Lease |  |
| 11 | Menüs | Raute-Menü öffnen | Rechtsklick auf die Raute (Bedientaste Strg+Alt gehalten) öffnet das Menü | Taste halten, rechts klicken, Bild holen | Menü sichtbar, Einträge benennbar | braucht Menü-Freigabe |
| 12 | Menüs | Farbe wählen | Eintrag „Farbe wählen“ ändert die Farbe der Raute | Eintrag wählen, Farbe wählen, Bild holen | Rautenfarbe hat sich geändert | braucht Menü-Freigabe |
| 13 | Menüs | Deckkraft und Größe | Einträge „Deckkraft“ und „Größe“ wirken sichtbar | nacheinander wählen, Bild holen | Raute ist durchsichtiger beziehungsweise größer | braucht Menü-Freigabe |
| 14 | Menüs | Anzeigeort und Ziel | Eintrag „Anzeigeort und Ziel (Desktops) …“ zeigt Läuft auf, Angezeigt auf, Sitzung, Ziel | Eintrag wählen, Anzeige beschreiben, mit Esc abbrechen | vier Zeilen benannt, nichts verändert | braucht Menü-Freigabe |
| 15 | Menüs | Zeichnen im Ziel | Pfeil ziehen, Text setzen, Rückgängig, Fertig | Zeichnen öffnen, Werkzeug wählen, ziehen, Strg+Z, Fertig | Pfeil und Text erscheinen, Rückgängig nimmt zurück | braucht Menü-Freigabe |
| 16 | Menüs | Regiespruch Pause und Weiter | Regiespruch „Pause“ pausiert den Agenten, „Weiter“ setzt fort | Regie öffnen, Spruch wählen, Bild holen | Agent pausiert sichtbar, danach läuft er | braucht Menü-Freigabe |
| 17 | Menüs | Fenster binden | Scanner-Knopf öffnet die Fensterliste, Auswahl bindet das Fenster | Fadenkreuz klicken, Eintrag wählen | Unten steht „Ziel: <Fenster>“ | braucht Menü-Freigabe |
| 18 | Gemeinsam arbeiten | Gemeinsam schreiben | A schreibt einen Satz, B liest ihn per Bild, antwortet und schreibt darunter weiter; speichern mit Strg+S | Editor öffnen, tippen, speichern, Dialog bedienen | Datei enthält beide Sätze |  |
| 19 | Gemeinsam arbeiten | Browser | Seite aufrufen und einen Link anklicken | Adresse tippen, Link klicken, Bild holen | neue Seite ist sichtbar |  |
| 20 | Gemeinsam arbeiten | Zeigegeste | A zeigt B eine Stelle im Bild; B nennt, worauf gezeigt wird | zeige X Y, B holt Bild | B nennt die richtige Stelle |  |
| 21 | Gedächtnis | Moment festhalten | Kapsel anlegen, unverändert prüfen | kapsel moment, kapsel zeige im Chat vorlesen | unveraendert: True |  |
| 22 | Gedächtnis | Seed mit Daniels Ja | Seed vorschlagen, Daniel gibt Ja sichtbar im Menü, Empfänger findet den Text | seed vorschlagen und ausliefern | Text steht im Terminal des Empfängers |  |
| 23 | Gedächtnis | Loop mit Budget | Loop mit Budget 3 läuft und endet mit echtem Grund | Loop vorschlagen, ausliefern, Status ansehen | Grund budget_laeufe_erschoepft |  |

Die Quelle ist `src/augen_haende_bridge/praxis/szenario_menschlich.json`; diese Tabelle wird daraus erzeugt.
