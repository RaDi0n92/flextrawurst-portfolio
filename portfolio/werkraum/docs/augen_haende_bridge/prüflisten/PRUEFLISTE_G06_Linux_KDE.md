# Prüfliste für Daniel — G06: Körper auf KDE 1 und KDE 2

Alles hier ist auf dem VPS (privater Xvfb, echter Relay-Prozess, Wine) belegt, **nativ auf deinen Desktops noch nicht**. Reihenfolge: erst der Relay, dann der Selbsttest, dann der Körper.

## 0. Vorbereitung
- [ ] **Relay neu starten** (neuer Code, legt die Zugangsdaten für KDE 1 und KDE 2 an): auf dem Host einzeln `systemctl daemon-reload`, `systemctl restart bridge-relay`, `systemctl is-active bridge-relay` → `active`. Danach gibt es unter `/root/werkraum/augen_haende_bridge/runtime/tokens/` vier Dateien `desktop-kde1.token`, `agent-kde1.token`, `desktop-kde2.token`, `agent-kde2.token` (Rechte 600; bitte nicht ansehen oder weitergeben).
- [ ] Der Windows-Körper (0.9.1) läuft mit dem neuen Relay unverändert weiter (er meldet sich wie bisher).

## 1. Selbsttest in vd1 (KDE 1)
In einem Terminal in vd1: `sh /vps_root/werkraum/augen_haende_bridge/client_vps/koerper_linux_starten.sh kde1 --selbsttest`
- [ ] Jede Zeile steht einzeln da; **nichts steht auf „fehlt“**. „Hinweis“ ist erlaubt (z. B. „kein Compositor“, F24).
- [ ] „Aufnahme“ sagt, ob XComposite geht („Fenster der Bridge lassen sich auslassen“). Wenn dort „läuft ein Compositor?“ steht: sag mir das, dann wird die Aufnahme anders gebaut.
- [ ] „Relay“ sagt „erreichbar, Zugangsdaten gelesen“.

## 2. Körper starten (KDE 1)
`sh .../koerper_linux_starten.sh kde1`
- [ ] Die Regieleiste, ein Chat und das Startmenü erscheinen wie unter Windows. Aussehen: gleiche Farben, Knöpfe und Abstände; die Buchstaben sehen anders aus (Noto Sans und DejaVu statt Segoe UI und Consolas).
- [ ] Einen Agenten starten (Regie → Startliste): **Raute, Terminal, Chat, Regie** da, Terminal gefüllt, Tastatur im Terminal geht (zuerst hineinklicken).
- [ ] Rechtsklick auf die Raute **mit gehaltener Bedientaste** (Strg+Alt): das Menü ist dasselbe wie unter Windows und zeigt neu **„Anzeigeort und Ziel (Desktops) …“**.
- [ ] Banner und Ticker (`bridge_cli say`) erscheinen, Zeichnen, Bild einblenden und Bild-Element gehen wie in der Prüfliste 0.9.1 (nur Durchsichtigkeit geht ohne Compositor nicht: die Fenster bleiben undurchsichtig).
- [ ] Hände: `bridge_cli schreibe "Test"` tippt in das Eingabefeld der Raute (Strg+Alt+Taste der Raute öffnet es).
- [ ] **F12** (Not-Aus) wirkt, auch wenn ein anderes Programm im Vordergrund ist; die Taste kommt dort trotzdem an.
- [ ] Ein Fenster binden (Scanner-Knopf im Terminal): die Liste zeigt deine echten KDE-Fenster; das gebundene Fenster liefert Bilder.

## 3. Anzeigeort wechseln
Zweiten Körper starten: `… koerper_linux_starten.sh kde2` in vd2.
- [ ] Raute-Menü → „Anzeigeort und Ziel“: oben vier Zeilen (Läuft auf / Angezeigt auf / Sitzung / Ziel), darunter „Anzeigeort wechseln zu KDE 2 …“ (nur wenn KDE 2 läuft).
- [ ] Auswahl: der Körper verschwindet auf KDE 1 und steht auf KDE 2; **der Agent läuft weiter, das Terminal zeigt den bisherigen Verlauf**.
- [ ] Zurück nach KDE 1 geht ebenso.
- [ ] „Arbeitsziel auf KDE 2 legen (ganzer Desktop)“: der Körper bleibt, der Agent sieht jetzt den Bildschirm von KDE 2 (der Körper dort meldet „Ziel für ein Terminal auf …“).
- [ ] Windows-Körper: erst mit dem neuen Paket (0.10.0) kann er Körper nach KDE schicken oder holen; mit 0.9.1 wird so ein Wunsch mit „dieser Körper kennt Anzeigeorte noch nicht“ abgelehnt.

## 4. Grenzen, die du kennen solltest
- Arbeitsziel auf anderem Desktop = ganzer Desktop; ein einzelnes Fenster dort zu wählen geht nur an dem Desktop selbst.
- Kein Compositor: Fenster sind undurchsichtig. Mit Compositor: echte Durchsichtigkeit, aber die Fensteraufnahme ohne Bridge-Fenster fällt weg (der Selbsttest sagt es).
- Mikrofon und ChatGPT sind zurückgestellt.
