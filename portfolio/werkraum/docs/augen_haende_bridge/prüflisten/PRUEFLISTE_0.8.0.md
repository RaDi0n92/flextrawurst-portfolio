# Prüfliste für Daniel — Version 0.8.0-g02 (G04, G05, G05.5, G07)

Hake ab, was klappt; schreib bei jedem Fehler kurz, was du gemacht und gesehen hast. Alles hier ist nur auf dem VPS und unter Wine geprüft, **nativ bei dir noch nicht**.

## 0. Vorbereitung (einmal)
- [ ] Auf dem Host: `systemctl daemon-reload && systemctl restart bridge-relay && systemctl status bridge-relay --no-pager | head -8` → `active (running)`. (Ohne neuen Relay lehnt dieser `terminal_attach` ab.)
- [ ] Tunnel auf, auf Windows `C:\Bridge\bridge_wechseln.bat` ausführen. Das ZIP (0.8.0) und beide Dateien liegen schon dort, sie packt nach `C:\Bridge\v080` aus und startet die Bridge.
- [ ] Version prüfen: `C:\Bridge\v080\AugenUndHaendeBridge\AugenUndHaendeBridge.exe --version` zeigt `0.8.0-g02`.
- [ ] Selbsttest: `C:\Bridge\v080\selbsttest.bat` — Bericht schicken (neu: Zeile „Bridge-Fenster lassen sich aus der Aufnahme ausnehmen“).

## 1. G04 — Terminal (Wiederaufnahme, Eingaben, Anzeige)
- [ ] Einen Agenten starten (z. B. „Claude“ vd1), etwas schreiben lassen, bis das Terminal gut gefüllt ist (mehr als eine Bildschirmseite).
- [ ] Regie → „Bridge beenden“. Mit `bridge_starten.bat` neu starten. **Erwartung:** Das Terminal desselben Agenten erscheint wieder, **gefüllt**, mit dem Verlauf; es gibt keine zweite Raute/Sitzung.
- [ ] Mit Rollbalken und Rad im wiederaufgenommenen Terminal nach oben blättern: Der Verlauf ist da (die letzten 512 KB).
- [ ] Eine Eingabe tippen (Enter): erscheint **genau einmal** beim Agenten.
- [ ] Lange Eingabe einfügen (Rechtsklick → Einfügen, einige Zeilen): kommt vollständig an.
- [ ] Pfeiltasten und Strg+C im Agenten-Terminal tun das Übliche.
- [ ] Fenster größer und kleiner ziehen: Zeilen und Spalten passen sich an, der Agent läuft normal weiter.
- [ ] Ein Vollbildprogramm im Terminal (falls möglich, z. B. `top` über einen Host-Agenten): wird gezeichnet, Beenden bringt den Hauptbildschirm zurück.

## 2. G05 — Namen, Farben, Menüs
- [ ] Zwei Sitzungen desselben Eintrags starten (z. B. zweimal Codex): sie heißen „Codex“ und „Codex 2“, haben eigene Plätze.
- [ ] Raute (Bedientaste halten + Rechtsklick) → „Name ändern …“: neuen Namen eingeben, Enter. Raute, Terminaltitel und Chat zeigen ihn.
- [ ] Zu langen Namen (mehr als 24 Zeichen) und einen schon vergebenen Namen versuchen: es kommt eine Meldung, nichts ändert sich.
- [ ] „Farbe wählen …“: eine der acht Farben; Raute, Terminalrahmen, Banner und Chatname ändern sich; „Standardfarbe“ geht zurück.
- [ ] Bridge neu starten: Name und Farbe sind da, Positionen und Größen auch.
- [ ] Regie → „Fenster, Namen und Farben zurücksetzen …“ → Abbrechen: nichts passiert. Nochmal → Ja: alle Fenster auf den Standardplätzen, Namen und Farben zurück.
- [ ] Regie-Menü: Oben steht „Sprüche gehen an: …“ und stimmt zu „An: …“ im Chat.
- [ ] Mik und Cam zeigen unter dem Namen ein Wort (aus / an / … / Fehler).
- [ ] Scanner: ein Fenster binden, danach erscheint im Scanner-Menü „Bindung lösen (zurück zu ungebunden)“; es löst die Bindung (Terminal zeigt „Ziel: Desktop (ungebunden)“).
- [ ] Bei gebundenem Fenster: Banner eines Agenten erscheint im Bereich **dieses Fensters** und folgt ihm, wenn du es verschiebst.

## 3. G05.5 — „Nur Terminal“ und Ort der Elemente
**Nur Terminal**
- [ ] Im Terminal unten steht „A+H“ (grün). Klick (mit gehaltener Bedientaste): wird „nur T“ (gelb).
- [ ] Der Agent lässt etwas über die Raute sagen (`bridge_cli say …`): **kein** Banner, keine Box, kein Chateintrag für diesen Agenten.
- [ ] Mit dem Agenten ein Ziel gebunden und `bridge_cli see` aufrufen lassen: kommt **kein neues** Bild. Cam-Knopf: bleibt aus, Meldung „nur Terminal …“.
- [ ] `bridge_cli schreibe …`: es werden keine Tasten gedrückt.
- [ ] Mikrofon läuft weiter (falls es bei dir geht): Sprechtaste, Text kommt an.
- [ ] Zurück auf „A+H“: Bilder, Banner, Kamera, Hände gehen wieder.
- [ ] Raute-Menü → „Nur Terminal …“ und Regie → „Nur Terminal für alle Agenten“ gehen auch; Neustart merkt es sich.

**Ort der Elemente** (braucht ein einzelnes Fenster als Ziel, z. B. einen Browser)
- [ ] Ohne Fenster-Ziel: Knopf „Ort“ erklärt „Kein einzelnes Fenster als Ziel gebunden“ und ist gesperrt.
- [ ] Browser binden. „Ort“ → „Raute: ins Zielfenster“: Die Raute steht im Browserfenster.
- [ ] Browserfenster **verschieben**: die Raute geht an derselben Stelle mit. **Verkleinern**: sie bleibt drin. Raute aus dem Fenster **ziehen**: sie springt zurück in den Rahmen.
- [ ] Browser **minimieren**: die Raute verschwindet. **Wiederherstellen**: sie ist wieder da, an der gemerkten Stelle.
- [ ] Browser **schließen**: die Raute ist weg (sie geht nicht auf den Desktop). Ein neues Ziel binden: sie erscheint dort wieder (Wunsch bleibt).
- [ ] Terminal und Selbstbild getrennt umschalten: nur das gewählte Element wandert; das andere bleibt auf dem Desktop.
- [ ] „Bindung lösen“ im Scanner: Elemente stehen wieder auf dem Desktop.

## 4. G07 — Bilder
- [ ] Raute-Menü → „Bilddatei an den Agenten senden …“: Dialog, ein PNG/JPG wählen. Der Agent bekommt es (`bridge_cli see` zeigt eine Datei mit Quelle `file`).
- [ ] Raute-Menü „Bilder an den Agenten …“ zeigt „an, N gesendet“ und zählt hoch.
- [ ] Regie → „Bridge-Fenster im Bild der Agenten: aus“: Meldung; der Agent sieht in einem neuen Bild **keine** Bridge-Fenster. Wieder „an“.
- [ ] Selbstbild: Cam einschalten, Bild erscheint; „nur Terminal“ schaltet es ab.

## 5. Noch nicht gebaut (nicht prüfen)
- G06 KDE 1/2 (braucht eine Entscheidung zur Infrastruktur), G08 Zeichnen/Objekte, Bildfolge/Replay, Mikrofon (zum Schluss).
