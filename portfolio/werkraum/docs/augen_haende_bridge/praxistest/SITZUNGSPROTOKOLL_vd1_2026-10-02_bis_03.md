# Praxistest auf vd1: Zustände und Logik

Stand 3. Oktober 2026. Beschreibt, wie das System sich verhält und warum, nicht, was wann geschah.
Belege liegen als Ledger unter `runtime/praxis/`, als Ereignisprotokoll unter `runtime/g13/protokoll/ereignisse.jsonl`
und als Bilder unter `screenshots/`.

## 1. Zielzustand

Die Augen-und-Hände-Bridge wird auf vd1 (KDE, DISPLAY :1.0) von einer Nutzerin bedient, nur mit Händen (Maus und Tastatur
über die Bridge) und Augen (Bilder der Bridge), mit den Werkzeugen aus dem Skill `bridge-praxistest`. Ein Gutachter
bestätigt oder widerspricht mit einem eigenen, frischen Bild.

Regeln des Laufs:

- Jede Aktion wird vorher in der Raute des Handelnden angesagt. In der Raute steht nur die Ansage, kein Fazit.
- Kein Lesen oder Ändern von Bridge-Code, kein Durchsuchen des Systems, keine Eingaben an der Bridge vorbei.
- Daniels Maus und der Not-Aus F12 gehen immer vor.
- Schritte laufen der Reihe nach. Ein Schritt wird bis zum dritten Versuch wiederholt, danach hält der Lauf an, die Ursache
  wird gesucht, erst dann geht es weiter. Ein Lauf mit nicht getesteten Schritten gilt nicht als Abnahme.
- Berichtet wird in Goals (G01 bis G18 mit G05.5, G06.5, G06.7), nicht in Schritten.
- Der zweite Durchlauf "nur Augen" folgt, sobald die Hände sauber durchlaufen.

## 2. Aufbau auf vd1

| Agent | Terminal-ID | Strom | Fenster | Rolle |
| --- | --- | --- | --- | --- |
| Claude-Host | t-17a2b9c516 | claude | "Claude-Host · Host" | Gutachter |
| Gemgem | t-0b3325704d | gemini | "Gemgem · vd1" | Gegenprüfung, nächste Nutzerin |
| Opencode | t-f0f8bdd060 | opencode (Space Bunny) | "Opencode · vd1" | Nutzerin im Lauf p-451034 |

Szenario `nutzerin-anwendungsfaelle` (Version 2, 14 Schritte, fünf Anwendungsfälle: Notiz schreiben und speichern in Kate,
im Browser nachschlagen, Datei finden und öffnen, mit der Bridge zusammenarbeiten, etwas zeigen). Material:
`/config/Nutzerin-Test/` (start.html, sonne.html, berge.html, notiz.txt).

Desktop: Xfwm4 mit eingeschaltetem Compositor (Transparenz wirkt). Alle Bridge-Fenster tragen `_NET_WM_STATE_ABOVE`.
Bildschirm 1632×800 (wechselt zeitweise auf 1920×880; Fenster, die für die größere Auflösung gesetzt wurden, liegen dann außerhalb).

## 3. Läufe

| Lauf | Nutzerin | Gutachter | Zustand am Ende |
| --- | --- | --- | --- |
| p-12c8f8 | Claude | Gemgem | Vorstufe |
| p-3e5773 | Gemgem | Claude-Host | Szenario gemgem-allein, Schritt 2 abgebrochen |
| p-2fa24c | Gemgem | Claude-Host | Schritte 1 bis 3 bestätigt, Schritt 4 offen (Nutzungslimit von Gemgem erreicht) |
| p-451034 | Opencode | Claude-Host | `INCOMPLETE_WITH_DEFERRED` |

Lauf p-451034, Ergebnis je Schritt:

| Schritte | Zustand |
| --- | --- |
| 1, 4, 5, 6, 14 | bestätigt (Notiz schreiben, Adresse eingeben, Link folgen, Nachschlagen abnehmen, Zeigen) |
| 3 | anders (Kate-Text enthielt Fremdeingabe) |
| 2 | nicht getestet (Speichern; Tasten ohne Beleg, letzter Handgriff von außen) |
| 7, 8, 9 | nicht getestet (Dolphin; Bildstrom lieferte nur den Bindungs-Schnappschuss) |
| 10, 11, 12 | nicht getestet (Bridge-Chat; Klicks mit `punkt_verdeckt` abgelehnt) |
| 13 | nicht getestet (Bridge-Menü; Käfig-Freigabe für Menüs fehlt) |

Beweisgrenze laut Harness: maschinelle Aktionsspuren plus zwei Agentenurteile, keine native Produktabnahme.

## 4. Bilderstrom: Zustände und Übergänge

Takt 2 s, unveränderte Bilder nur als Keepalive alle 15 s. Eine Bestätigung des Gutachters zählt nur mit eigenem Bild
(`captured_at_ms >= since_ms`, gleiches `target_id`, Quelle nicht Datei oder synthetisch).

| Zustand | Bedeutung | Übergang |
| --- | --- | --- |
| Desktop | Standard jedes Agenten ab dem Anlegen | Binden an ein Fenster |
| Fenster | Bilder genau dieses Fensters | Fenster verschwindet → Desktop; Bindung lösen → Desktop |
| Aus (Knopf) | Daniel hat die Augen ausgeschaltet; ein neues Binden erbt "aus" | nur durch den Schalter |
| Gesperrt | Not-Aus | Not-Aus löst |
| Unsichtbar | Ziel minimiert oder nicht eingeblendet, es kommt kein Bild | Ziel wird sichtbar |

Jeder Grund, aus dem ein Ziel kein Bild bekommt, steht im `bridge.log` (`Bilderstrom: kein Bild für <Agent>: <Grund>`),
dazu jede Minute ein Herzschlag (`Bilderstrom lebt: Takte=… Ziele=…`). Fehlt der Herzschlag, hängt der Faden selbst.

Gemessene Ausfälle (Frame-Lücken über 2 min): Claude-Host 212 min, Opencode 168 min, Gemgem 127 min. Ursache der längsten Reihe:
Ein verschwundenes Fenster setzte den Strom des Ziels auf aus, und ein neues Binden erbte aus. Seitdem fällt der Strom auf den
Desktop zurück. Nach einem Binden folgt der Strom dem neuen Ziel mit Verzögerung; die Zeile "Ziel: …" im Terminal sagt nichts über den Strom.

## 5. Hände: Zustände

Aktionen im Ereignisprotokoll: 53 ausgeführt, 47 abgelehnt.

| Ablehnungsgrund | Anzahl | Bedeutung | Behebung |
| --- | --- | --- | --- |
| `daniel_uebernimmt` | 14 | Daniel bedient gerade (Selkies sendet alle 0,8 s Zeigerereignisse; die Ausnahme in der Raute schaltet es ab) | keine |
| `frame_unbekannt` | 13 | kein Strombild als Bezug | Bilder neu starten |
| `punkt_verdeckt` | 12 | ein anderes Fenster liegt am Klickpunkt vor dem Ziel | Fenster nach vorn |
| `lease_fehlt` | 4 | keine Berechtigung | Agent nimmt Lease |
| `ziel_weg` | 2 | gebundenes Fenster existiert nicht mehr | Desktop binden |
| `frame_veraltet`, `geometrie_geaendert` | je 1 | Bezugsbild zu alt, Fenster verschoben | Bilder neu starten |

Weitere Zustände:

- Das Overlay "Objekte" der Bridge (PixelFenster) kann deckungsgleich über dem Bridge-Chat liegen. Das Fensterbild zeigt den Chat frei,
  der Käfig meldet `punkt_verdeckt`. Der Chat wird nach vorn geholt, bis der Käfig Bridge-eigene Overlays ausnimmt.
- Tasten (Strg+S, Strg+Umschalt+S, Enter) werden zugestellt und auditiert, erzeugen im Beleg-Ledger aber keine als Taste erkannte
  Aktion (`missing s2-1`); im Browser markiert Strg+A einmal, Rücktaste wirkt nicht. Ursache offen.
- Klick in die Chromium-Adressleiste markiert den Inhalt nicht zuverlässig; getippter Text landet mitten im alten Inhalt.
- Das Speichern-Fenster und das Überschreiben-Fenster sind eigene Fenster mit eigenem Titel; jedes braucht eine eigene Bindung.
- Agenten überschreiben `BRIDGE_TERMINAL_TOKEN` nicht; die Prozessumgebung jedes Agenten enthält Terminal-ID, Token und Runtime-Pfad.
- Eingaben per `xdotool` in andere Terminals gehen an der Bridge vorbei (kein Käfig, keine Ansage, keine Prüfung, ob jemand tippt).
  Anforderung: vor jeder Aktion prüft ein Agent, ob andere gerade etwas tun; vor dem Tippen in ein Terminal die Eingabezeile prüfen.

## 6. Fenster, Bedienung, Rollen

- Fenster der Bridge sind durchklickbar und werden mit der Bedientaste (Strg+Alt) bedient. Menüs der Bridge sind eigene Fenster ohne
  Freigabe für Agenten (Schritt 13).
- Die Raute von Opencode kann im Plan-Modus ("Plan · Space Bunny Free") keine Befehle ausführen; Build-Modus schaltet per Tab zurück.
- Ein Körper-Neustart bindet alle Agenten an den Desktop und legt ihre Fenster in den Stapel unter andere Fenster.
- Rollen im Lauf: Opencode handelt, Claude-Host urteilt mit eigenem Bild, Gemgem führt Gegenprüfung und Dokumentation.

## 7. Wartegraph

- Nutzerin wartet auf Gutachter (Urteil) und Bindung.
- Gutachter wartet auf frisches Bild und auf die Aktion der Nutzerin.
- Bindung wartet auf einen Menschen, solange sie nur über den Scanner-Klick geht.
- Es gibt keinen Ort, an dem Position und Wartezustand stehen. Anforderung: Lauf-Graph (LangGraph), Ereignisspeicher (PostgreSQL),
  Wiederfinden des Gelernten (RAG); jeder Agent kennt jederzeit seine Position und worauf er wartet.

## 8. Ampel (Zustandskatalog)

Je Agent ein eigenes, kleines Fenster in der Farbe des Agenten mit **drei Lampen: Augen, Hände, Ziel**. Jede Lampe zeigt das Schlimmste
ihrer Gruppe und zählt die weiteren Auffälligkeiten ("+2 weitere"). Bedienung wie bei der Raute: das Fenster ist durchklickbar; mit gehaltener Bedientaste (Strg+Alt) wird überall im Fenster gezogen (ab 4 Pixeln
Zug, sonst Klick). Strg+Alt + Rechtsklick öffnet das Menü mit Deckkraft (aktueller Wert, nächste Stufe), größer, kleiner, Sichtbarkeitsregel
(immer sichtbar oder nur bei einem Programm), Ein-/Ausblenden und Durchklickbar. Die Ampel gehört zum "Ort der Elemente" (am Zielfenster oder auf
dem Desktop), wie Raute, Terminal und Selbstbild. "Fenster, Namen und Farben zurücksetzen" setzt Größe, Ort, Deckkraft, Regel und Ausblenden der Ampel
auf Standard. Ausblenden bleibt über einen Neustart nicht erhalten, wie bei Chat und Terminal. Das Regie-Menü schaltet alle Ampeln auf einmal aus und ein.
Schaltet ein Agent von "Nur Terminal" wieder auf Augen und Hände an, wird sein Bilderstrom auf den ganzen Desktop gebunden.

Prüfung: `tests/test_koerper_ampel_bedienung.py` startet ein echtes Ampel-Fenster der GTK-Fensterschicht in einem privaten Xvfb (nie auf dem
sichtbaren Desktop, `BRIDGE_TEST_XVFB=1`) und bedient es mit echten Klicks: Klick auf eine rote Lampe löst die Behebung aus, Klick auf eine blaue erklärt
die Gruppe, Ziehen verschiebt das Fenster ohne Aktion, Rechtsklick ruft das Menü. `test_koerper_ampel_fenster.py` prüft zusätzlich, dass kein
Attributname der Ampel mit einem der Fensterbasis kollidiert.

Farben: Blau = läuft, Orange = Achtung, Rot = kaputt, Grau = ausdrücklich aus. Rot blinkt, piept einmal beim Wechsel auf Rot und wird im Chat
gemeldet, in dem auch die Agenten schreiben: alle 20 s eine Zeile je rote Funktion mit Behebung, bis es behoben ist, danach einmal "wieder in Ordnung".

Klick auf eine rote Lampe führt die Behebung aus (Desktop binden, Bilder neu starten, Fenster nach vorn, Terminal zurückholen); ohne Behebung
erklärt der Chat die Gruppe. Rechtsklick öffnet ein Menü mit allen Funktionen, gegliedert nach den drei Lampen, jede Gruppe mit Erklärung, jede
Funktion ausgeschrieben und dahinter in Klammern ihr Zustand (läuft, Achtung, kaputt, aus).

Herkunft der Funktionen: Jede Funktion ist ein Gate oder ein Zustand, den das System selbst kennt. Der Katalog wird aus diesen Quellen abgeleitet,
und Tests prüfen gegen den Code, dass keine fehlt und keine erfunden ist (`GatesVollstaendigTests`): kommt im Code ein neuer Grund dazu, schlägt der Test an.

| Quelle im Code | Gates | Lampe |
| --- | --- | --- |
| `eingabe_adapter.GRUENDE`, Prüfreihenfolge von `pruefe` ("erst, was alles stoppt, dann Rechte, dann das Ziel, dann das Bild, zuletzt die Punkte") | 25 Käfig-Gates: Not-Aus, Verbindung, Daniel bedient, Hände erlaubt, Steuerprofil, Ziel gebunden, Lease (fehlt, abgelaufen, fremd), Ziel existiert, nicht minimiert, Tasten (Not-Aus-Taste, Systemtaste), Bezugsbild (bekannt, zum Ziel gehörig, frisch), dasselbe Fenster, unverändert, Punkt im Ziel, Punkt nicht verdeckt, Tastaturfokus (verloren, erreichbar), Aktion gültig, System nimmt an, nicht abgebrochen | Hände |
| `Anwendung.HAENDE_GRUENDE` (Ansage in der Raute) | 5: Tastenkombination vorhanden, öffnet das Eingabefeld, behält die Tastatur, System nimmt die Tasten an, Ansage nicht leer | Hände |
| `Bilderstrom._stumm` | 7: gesperrt, Strom aus, Fenster weg, Ziel unsichtbar, Fensterbild statt Ausschnitt, Ausschnitt außerhalb, Sender lehnt ab | Augen und Ziel |
| `anzeigeort.ZIEL_ZUSTAENDE`, `ZIEL_FAEHIGKEITEN` | Zustand des Ziel-Fensters (ok, verdeckt, minimiert, inaktiv, weg, unbekannt), Leistung der Aufnahme (frisch, fremde Pixel, letztes Bild, keine Aufnahme, unbekannt) | Ziel, Augen |
| `anzeigeort.GRUND_TEXT` | 7 Gründe für abgelehnte Anzeigeort-Befehle | Ziel |
| Medien, Verbindung, Not-Aus | Selbstbild-Kamera, Verbindung zur Bridge, Not-Aus | Augen, Ziel |

Dazu die Hände je Aktionsart (Klicken, Tippen, Tasten, Mausrad, Ziehen, Zeigen) und je Programm, sobald es Aktionen gab. Jede Lampe trägt den ausgeschriebenen Namen der
Prüfung ("Das Bezugsbild ist frisch genug") und den Zustand in Worten. Heute: 44 Funktionen (Augen 8, Hände 29, Ziel 7).

Nicht gemessen, daher ohne Funktion: Lauf und Warteschlange, Taste ohne Beleg, Fremdeingabe.

## 9. Offen

- Lauf und Warteschlange in die Ampel (braucht Graph und Ereignisspeicher).
- Käfig-Freigabe für Menüs der Bridge; Bridge-eigene Overlays aus der Verdeckungsprüfung ausnehmen.
- Ursache "Tasten ohne Beleg", Adressleisten-Markierung.
- Neues Windows-Paket 0.10.1, Abnahme G15.
- Zweiter Lauf mit Gemgem als Nutzerin, danach "nur Augen".
