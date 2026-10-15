# Abnahme G10 — Hände, parallele Arbeit, verlässlicher Stop

Stand: 2026-10-02. Belege: `.unlazy/g06-g14/gates/leaf-1.4.1.md` bis `leaf-1.4.3.md`, `node-1.4.md`. Code: `koerper/eingabe_adapter.py`, `steuerprofil.py`, `uebernahme.py`, `haende_anbindung.py`, Anschluss in `terminal_launcher.py`,
`bridge_cli.py`, `anwendung.py`, `transport.py`, `bilderstrom.py`. Proben: `probes/haende_wine.py`, `probes/uebernahme_wine.py`.

## Aufbau

* **Käfig** (reine Logik): jede Aktion braucht einen Ziel-Schlüssel eines **Fensters** (nie der Desktop, nie ein Index) und das Bild (Folgenummer), auf das sich der Agent bezieht. Abgelehnt wird mit festem Grund: Not-Aus, Verbindung,
  Daniels Übernahme, Hände aus, Profil, Lease (fehlt/abgelaufen/fremd), Ziel weg/minimiert/ersetzt, Bild unbekannt/veraltet (15 s)/anderes Ziel, Verschiebung oder Größe oder DPI seit dem Bild, Punkt außerhalb, F12 und Strg+Alt+Entf.
* **Engine**: Klick, Doppelklick, Rechtsklick, Ziehen (50–5000 ms in 15-ms-Schritten), Tippen (Unicode, in Stücken mit Fokusprüfung), Tastenkombinationen, Rad. Vor jedem Schritt Stopp- und Zielprüfung; das Ziel wird vor dem Klick
  auf „liegt wirklich oben am Punkt“ geprüft (auch hinter Rahmen der Fensterverwaltung). Alles Gedrückte wird in jedem Fall losgelassen. Das Ergebnis trennt `accepted`, `delivered`, `observed`, `audited`.
* **Backends**: X11 (XTEST, unter Schloss, weil Not-Aus und Übernahme aus anderen Fäden loslassen) und Windows (SendInput, Bewegung ebenfalls über SendInput, damit sie als eigene Eingabe erkennbar ist).
* **Lease**: je Ziel höchstens ein Halter, Ablauf (30 s Vorgabe, höchstens 300 s), Verlängerung nur durch den Halter, Entzug bei Not-Aus, Übernahme, Verbindungsabbruch und Offline-Gehen des Desktops. Nach einem Stopp muss der Agent die Lease neu holen.
* **Profile** (`steuerprofil.py`): `hintergrund` (keine physischen Aktionen), `geteilte_maus`, `controller`, `hybrid`; Controller werden nur **erkannt** (uinput, ViGEmBus, Geräte), das Ziel von vier Controllern steht im Zustand.
* **Daniels Übernahme**: eigene Eingabe hält die Hände an und lässt los (Pause 3 s); seine Ausnahme (Menü „Meine Eingabe unterbricht die Hände nicht“, Vorgabe aus) lässt sie weiterlaufen; F12 gilt in beiden Fällen.
* **Anschluss**: Agent → `bridge_cli lease/klick/ziehe/tippe/taste/rad` → Starter (Prüfung, Lease) → Relay (`haende_auftrag`, streng geprüft) → Desktop des Ziels (Körper) → Engine → Ergebnis zurück (`haende_ergebnis`).
  Schweigt der Körper, lautet die Antwort „Ausgang unbekannt“, nicht Erfolg.

## Auf dem VPS belegt

* X11 gegen echte GTK-Fenster unter Xvfb: Klick, Text mit Umlauten und Emoji, Strg+A, Strg+Umschalt+Z, Doppel-/Rechtsklick, Rad, Ziehen mit echtem Zeigerweg (Start- und Endpunkt stimmen, viele Zwischenschritte), Schieberegler.
* Windows-Fassung unter Wine gegen ein echtes Win32-Fenster: Klick, Unicode-Text, Strg+A, Rad, Ziehen; der Zeiger steht auf dem berechneten Punkt.
* Negativtests an echten Fenstern: Fenster davor, falsches Ziel, veraltetes Bild, verschobenes Fenster, fehlende Lease, fehlende Rechte, Not-Aus, Punkt außerhalb, unbekanntes Bild.
* Zwei Agenten gleichzeitig an zwei Fenstern: 12 und 9 Klicks, jeder im richtigen Fenster. Ende-zu-Ende mit echtem Relay, Starter, dem echten Werkzeug als Prozess und einer echten Engine (`tests/test_g10_integration.py`).
* Stop: F12 über den echten Hook stoppt ein laufendes Ziehen, auch bei hängendem GUI-Faden; Verbindungsabbruch ebenso; danach ist keine Maustaste und keine Taste gedrückt; die Not-Aus-Taste wird nie gesendet.
  Gemessene Werte dieses Laufs (Xvfb, keine Zusage): F12 bis Ende des Auftrags ≈ 10 ms, Verbindungsabbruch bis Ende ≈ 11 ms.
* Übernahme: unter Wine unterscheiden Hooks eigene (injizierte) von fremder Eingabe; unter X11 wird gezählt. Eigene Eingabe löste in 8 Wiederholungen nie einen falschen Alarm aus (nach den unten genannten Korrekturen).
* Technische Festlegungen: GDI liefert Alpha 0, daher wird es auf 255 gesetzt; die Zeigerbewegung läuft über `SendInput`, damit sie als eigene Eingabe erkennbar ist; der Zähler der Übernahme zählt vor dem Senden; das X11-Backend läuft unter einem Schloss.
  aus mehreren Fäden (Schloss), Wurzel-Elternteil ist eine Zahl, Namensüberschneidung eines Dekorators mit der Tastensperre.

## Offen (nativ oder mit Daniels Wort)

* **Virtuelle Controller und Hybridbetrieb sind nicht nachgewiesen.** Dafür braucht es einen Treiber (ViGEmBus oder uinput-Rechte), den es hier nicht gibt; installiert wird nichts ohne Daniels Wort. Erkennung und das Ziel von vier Controllern sind vorhanden.
* Die Windows-Hände nativ (echter Desktop, DPI-Skalierung, Fokusdiebstahlschutz von Windows bei `SetForegroundWindow`): nur unter Wine.
* Der physische Override mit **echter Hardware**: unter Wine kam „fremde Eingabe“ von einer zweiten X-Quelle; unter X11 ist die Unterscheidung eine Zählung (Näherung). Unter Wine löst die erste Bewegung nach fremder Eingabe manchmal ein Echo aus (nach der Pause
  zweiter Versuch nötig); ob es nativ passiert, ist offen.
* Hintergrundbedienung ist als Profil und über die Bedienungshilfen vorhanden; die eigentliche semantische Bedienung ist G11.
* Harte Latenzzahlen gibt es nicht; die gemessenen Werte stehen nur als Messung.
* Die Oberfläche (Menüpunkte Steuerprofil, Ausnahme, Zustände) ist gegen Attrappen geprüft, nicht nativ.

## Nachtrag 2026-10-03: Daniels Felder vor dem Raute-Schreibweg (R125, Teilstand)

Befund im Betrieb: Der Weg, über den ein Agent in seine Raute schreibt (Tastenkombination drücken, Eingabefeld öffnet sich mit Fokus, Text tippen), hat Daniels Eingabe nie berücksichtigt. Die Übernahme-Erkennung zählt unter X11 Zeigerereignisse; unter Selkies kommt der Zeiger alle 0,8 s, und die Pause (3 s) galt nur für Hände-Aktionen im Zielfenster.

Zustand jetzt (`uebernahme.py`, `tasten_senden.py`, `anwendung.py`): Der Schreibweg beginnt erst, wenn Daniel 2 s lang weder getippt noch geklickt hat (`RAUTE_RUHE_S`); nach 6 s ohne Ruhe (`WARTE_RUHE_S`) bricht er mit `daniel_uebernimmt` ab, ohne eine Taste zu drücken. Die eigenen Tasten der Hände werden vor jedem Senden markiert und zählen nicht als Eingabe von Daniel. Zeigerbewegung allein zählt nicht. Daniels Ausnahme („Meine Eingabe unterbricht die Hände nicht“) hebt diesen Schutz nicht auf. Der Ampel-Katalog führt den Grund gelb (`raute:daniel_uebernimmt`).

Belegt: Einheitstests für Schreibweg, Übernahme und Anwendungsanschluss; ein echter XRecord-Test in privater Xvfb (Zeigerrauschen ändert die Ruhe nicht, Taste und Klick setzen sie zurück).

**R4 (XInput2) trägt in dieser Umgebung nicht:** Selkies spielt Daniels Eingabe selbst als XTEST ein, wie die Hände. Beide kommen von demselben virtuellen Gerät; `sourceid` kann sie nicht trennen. Unter echter lokaler Hardware (ohne Selkies) bliebe R4 eine Verbesserung. Nicht ausprobiert.

Offen für R125: der Vermittler mit Warteschlange und kurzen Leasen für Klicks und Tasten im Zielfenster (Agent leiht sich die Eingabe nur, wenn Daniel nichts tut; Daniel und F12 haben Vorrang), der wählbare Modus „Daniel entkoppelt“ und der gezeichnete Zeiger je Agent. Nichts davon ist gebaut.
