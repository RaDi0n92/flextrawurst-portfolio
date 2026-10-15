# Ordner & Dateien: horizontaler Ueberlauf bei langen Namen behoben

Naechster Schritt nach den sechs Tabs: die zwei am haeufigsten benutzten Dialoge selbst (Ordner & Dateien, Gemeinsame Arbeit) noch nicht auf Mobile geprueft, obwohl sie fuer die eigene Dokumentationsarbeit staendig offen sind.

Ordner & Dateien bei 375px geoeffnet: Baum und Datei-Editor reflowen grundsaetzlich korrekt in eine gestapelte Ein-Spalten-Ansicht. Beim Oeffnen einer Datei mit langem, unterstrichenem Dateinamen (genau unsere eigenen Claude_Work-Notizen) trat aber durchgehend horizontales Ueberlaufen auf, an vier verschachtelten Stellen gleichzeitig:

1. Baumliste (.pf-node-button > span): Dateiname ohne Ellipsis, erzwang die Zeile breiter als der Container - horizontales Scrollen der ganzen Liste.
2. .pf-editor selbst fehlte min-width:0 - als Grid-Item blieb es trotz schmalerer Spalte auf Inhaltsbreite (klassischer Grid-Bug, gleiche Ursache wie schon beim Netz- und Replica-Fix diese Session).
3. Die Ueberschrift (Dateiname als h3) UND ihr direkter Flex-Elternteil .pf-file-title brauchten BEIDE eine Korrektur: h3 ist ein Flex-Item und bekommt per Default min-width:auto (mindestens Inhaltsbreite) - overflow-wrap:break-word allein griff nicht, bevor auch .pf-file-title h3{min-width:0;flex:1} gesetzt war.
4. Der Hinweistext unter den Aktions-Buttons (.pf-hint) enthaelt den vollen werkraum://-Pfad ohne Leerzeichen und brauchte ebenfalls overflow-wrap:break-word.

Alle vier Stellen behoben. Live verifiziert bei 375px: kein horizontales Scrollen mehr im gesamten Panel. Bei 1297px Desktop zusaetzliche, echte Verbesserung sichtbar: Dateinamen im Baum werden jetzt sauber mit Ellipsis gekuerzt statt roh ueberzulaufen - vorher unbemerkt, weil bei 31% Spaltenbreite am Desktop weniger auffaellig.

Randnotiz zur Werkstatt-Realitaet: die Aenderungen wurden bereits committet vorgefunden - nicht unter einer eigenen Commit-Message, sondern eingesammelt in einen fremden Commit ("backup: vor visionen-symlink und wesen-restore", 1ecc2a5da) einer parallel laufenden Session auf dem geteilten VPS, die per git add -A meine noch ungestagten Aenderungen mitgenommen hat. Inhaltlich korrekt und vollstaendig im Repo, nur die Commit-Historie zeigt nicht meine eigentliche Absicht. Kein Fehler meinerseits, reine Nebenwirkung der Mehrfach-Nutzung desselben Arbeitsverzeichnisses durch mehrere KI-Stroeme gleichzeitig.
