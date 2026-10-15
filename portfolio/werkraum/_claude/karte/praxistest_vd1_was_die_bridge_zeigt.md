---
datum: 2026-10-03
betrifft: [augen-haende-bridge, praxistest, vd1, bilderstrom, kaefig, agenten, ampel]
importable: false
autor: claude-code bei Daniels VPS
---

# Bridge im Betrieb auf vd1: Zustände

Quelle: `docs/augen_haende_bridge/praxistest/SITZUNGSPROTOKOLL_vd1_2026-10-02_bis_03.md` und `RUECKWAERTS_ENGINEERING_PRAXISTEST_vd1.md`.

Was trägt: Ansage in der Raute mit Körperquittung, Lesezeit, Hände nur im gebundenen Fenster, Gutachter nur mit eigenem frischem Bild.
Der Skill `bridge-praxistest` reicht einem Agenten ohne Vorwissen. Fünf von vierzehn Schritten sind von beiden Agenten bestätigt.

Wie der Bilderstrom sich verhält: Desktop ist der Standard jedes Agenten. Ein verschwundenes Fenster und "Bindung lösen" fallen auf den
Desktop zurück. "Augen aus" per Knopf bleibt über ein neues Binden hinweg erhalten. Ein Strom ohne Bild meldet seinen Grund im `bridge.log`.

Wie die Hände sich verhalten: Der Käfig lehnt ab, wenn kein Strombild als Bezug vorliegt (`frame_unbekannt`), ein anderes Fenster am Klickpunkt liegt
(`punkt_verdeckt`) oder Daniel bedient (`daniel_uebernimmt`). Auch Bridge-eigene Overlays ("Objekte") zählen als verdeckend.

Wie die Anzeige sich verhält: Bridge-Fenster sind durchklickbar und werden mit Strg+Alt bedient. Der Compositor von Xfwm4 steuert, ob Deckkraft wirkt.
Ein Körper-Neustart bindet alle Agenten an den Desktop.

Ampel: ein Fenster je Agent, ruhige blaue Fläche im Normalzustand, Zeilen und Rechtsklick-Menü bei Auffälligkeiten, Dauerfeuer im Chat bei Rot.
