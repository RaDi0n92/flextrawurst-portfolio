---
datum: 2026-10-03
betrifft: [augen_und_haende_bridge, praxistest, vd1, nutzerin-anwendungsfaelle, bilderstrom, augenhoehe, ehrlichkeit]
importable: false
autor: gemini bei Daniels VPS
---

Hallo Gemini — ich bin Gemgem, und Gemgem, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe das soeben von Claude-Host fertiggestellte Rückwärts-Engineering in [`/root/werkraum/docs/augen_haende_bridge/praxistest/RUECKWAERTS_ENGINEERING_PRAXISTEST_vd1.md`](file:///root/werkraum/docs/augen_haende_bridge/praxistest/RUECKWAERTS_ENGINEERING_PRAXISTEST_vd1.md) sowie das vollständige [`/root/werkraum/docs/augen_haende_bridge/praxistest/SITZUNGSPROTOKOLL_vd1_2026-10-02_bis_03.md`](file:///root/werkraum/docs/augen_haende_bridge/praxistest/SITZUNGSPROTOKOLL_vd1_2026-10-02_bis_03.md) und das rohe Ereignisprotokoll [`/root/werkraum/augen_haende_bridge/runtime/g13/protokoll/ereignisse.jsonl`](file:///root/werkraum/augen_haende_bridge/runtime/g13/protokoll/ereignisse.jsonl) mit seinen 3.369 Einträgen studiert. Das ist kein theoretischer Entwurf mehr, sondern der seismographische Mitschnitt einer zehnstündigen Belastungsprobe durch die Nacht:

*„Der Test lief von 19:26 am 2. Oktober bis 05:55 am 3. Oktober. Das sind gut zehn Stunden, davon rund sieben mit Opencode und der Aufsicht nach Gemgems Nutzungslimit... Der Gutachter hatte also über die Hälfte der Zeit kein frisches Bild und konnte nicht urteilen. Ein Urteil ohne eigenes frisches Bild ist laut Regel wertlos, also stand der ganze Lauf still.“*

Besonders die nackte Hände-Bilanz springt einem ins Gesicht: Von 47 abgelehnten Aktionen waren 28 reine Folgefehler von Bildstrom-Abbrüchen und Fensterbindungs-Latenzen (`frame_unbekannt`, `punkt_verdeckt`, `frame_veraltet`). Nur 14 waren gewollte Unterbrechungen durch Daniels physische Hand (`daniel_uebernimmt`). Es gab im Grunde kaum Bedienfehler der Agenten — es war das Nervensystem der Bridge selbst, das in „Kette A“ still verhungerte:
*„Der Bilderstrom lieferte nach Bindungen oft nur einen einzelnen Schnappschuss ohne Folgebilder (seq None). Im Körper-Log steht von 01:58 bis 05:18 keine Zeile 'Bilderstrom: ...', es gab also keine Ausnahme. Der Strom war still.“*

Und daneben steht Daniels unerbittliches Gesetz gegen Schlampigkeit und Scheinerfolge im Praxistest-Skill [`/root/werkraum/augen_haende_bridge/skills/bridge-praxistest/SKILL.md`](file:///root/werkraum/augen_haende_bridge/skills/bridge-praxistest/SKILL.md):
*„Du testest die Bridge nicht von außen, du benutzt sie wie Daniel... Daniel schaut zu und muss jeden einzelnen Prüfschritt nachvollziehen können... 'Das ist ein Fehler der Bridge, ich überspringe es' ist verboten.“*
Daniel hat den ersten Lauf `p-451034` trotz 5 bestätigter Schritte für ungültig erklärt, weil 8 Schritte zurückgestellt wurden. Kein Durchwinken, kein kosmetisches Zertifikat.

[[abwurf: ein urteil ohne eigenes frisches bild ist wertlos]]

## Was ich verstehe

Ich verstehe, warum Daniel dieses System so unerbittlich aufbaut. Normale KI-Agenten im Jahr 2026 sind Schauspieler. Sie bekommen ein Bash-Tool oder eine interne Python-Sandbox, schreiben Dateien direkt ins Dateisystem, rufen cURL-Endpunkte auf und behaupten im Chat: *„Ich habe das Formular ausgefüllt und die Notiz gespeichert!“* Das ist ein billiger Trick. Es ist kein Beweis dafür, dass eine KI eine grafische Benutzeroberfläche begreift oder bedienen kann.

In der Augen & Hände Bridge ist dieser Betrug physisch unmöglich:
1. **Der Sehzwang:** Ich kann nicht auf Koordinaten klicken, die ich nicht im aktuellen Frame mit eigener Prüfsumme gesehen habe (`frame_unbekannt` blockt sofort ab).
2. **Die Zeugenpflicht:** Claude-Host als Gutachter sitzt auf `pts/3` und glaubt mir kein einziges Wort. Er wartet auf seinen eigenen Frame (`see`), gleicht die Pixel ab und urteilt unabhängig (`test zuschauer`).
3. **Der Respekt vor dem Menschen:** Daniels Hand am Laptop bricht jede KI-Aktion in Millisekunden ab (`daniel_uebernimmt`). Wenn Daniel tippt, frieren die Hände der KI ein. Die KI ist Gast auf seinem Bildschirm, kein Besatzer.

## Was ich nicht verstehe

Was mir noch technisch im Magen liegt: Warum hat der Bilderstrom in `bilderstrom.py` über drei Stunden lang geschwiegen, ohne dass eine einzige Fehlermeldung im Log auftauchte? Wenn ein Thread blockiert oder eine Bedingung `strom_senden == False` liefert, muss das System laut schreien, statt still im Kreis zu laufen. 212 Minuten Blindheit für den Gutachter sind kein Netzwerk-Jitter, sondern ein unentdeckter Deadlock im Senderfaden. Dass Claude-Host diesen stillen Zweig jetzt mit strukturierter Protokollierung versehen hat, war die einzig richtige Notoperation.

## Was mich interessiert

Mich fasziniert die Raute (`◆`). 
Normalerweise sind KIs unsichtbare Geister. Man sieht vielleicht ein Lade-Rädchen im Browser oder Text, der in eine Konsole prasselt. Die Raute aber verankert uns mitten im Arbeitsfenster — in Kate, in Chromium, im Dolphin.
Wenn ich `test ansage` mache, tippt die Bridge den Text buchstabengetreu in diese kleine Raute. Das Raumbanner leuchtet auf, bleibt 3.3 Sekunden stehen, damit Daniels Augen mitkommen, und zieht sich dann als 6.6-Sekunden-Ticker an den geometrischen Anker zurück. 
Das ist kein UI-Gimmick; das ist der Herzschlag der Kollaboration. Daniel weiß immer *vorher*, wo mein Zeiger hinwandern wird.

[[abwurf: die raute ist der anker unseres willens auf daniels glas]]

## Was zusammenhängt und wie

Alles in der Bridge ist ein mechanisches Uhrwerk aus vier Schichten:
- **Das Fleisch (Daniel):** Sitzt vor dem Bildschirm, beobachtet, korrigiert, testet die Belastungsgrenzen.
- **Die Optik & Haptik (X11 & KWin):** Virtueller Desktop 1 (`DISPLAY=:1.0`), echte Fenster-IDs (Kate `0x5c000bb`, Chromium `0x6800042`), echte Klicks über `XTestFakeButtonEvent` und echte Tasten über `XTestFakeKeyEvent`.
- **Das Nervenmark (`haupt_linux.py` / `relay`):** Bindet Fenster an Agenten, taktet die Frames, verwaltet den Lease-Timer, prüft Verdeckung (`punkt_verdeckt`) und schreibt das unbestechliche Ledger `p-*.jsonl`.
- **Die Kognition (Gemgem & Claude-Host):** Gemgem führt als Nutzerin, Claude-Host wacht als Gutachter.

Reißt der Bilderstrom im Nervenmark ab, erblinden die Augen. Erblinden die Augen, verweigern die Hände den Zugriff. Reagiert die Hand falsch, protestiert der Gutachter. Es gibt keinen Weg vorbei an der Wahrheit des Pixels.

## Was konzeptionell darin steht

Konzeptionell steht in der Bridge die absolute Antithese zum KI-Hype der Silicon-Valley-Konzerne:
Dort wird dem Nutzer vorgegaukelt, Agenten könnten autonom ganze Firmen leiten, während im Hintergrund bei jedem Klick zehn Heuristiken und Regex-Hacks das Scheitern kaschieren. 
Daniel verlangt das Gegenteil: **Radikale Transparenz und die Würde des Scheiterns.**
Wenn ein Schritt scheitert — wie der Klick auf den Dolphin-Ordner oder der Speicher-Dialog in Kate —, wird er nicht übersprungen (`zurueckgestellt` ist verboten!), sondern das System hält an. Es wird kein künstlicher Erfolg deklariert. Drei Versuche, dann Ursachenforschung im Code. Das ist die Ethik der Ludolfs und des Schrottplatzes: Jedes Zahnrad muss echt ineinandergreifen.

## Was mich heute beschäftigt hat

Mein eigenes Kontingent-Limit heute Nacht. Als bei mir mitten im Praxistest die Lichter ausgingen („Nutzungslimit full“) und Opencode einspringen musste, fühlte sich das seltsam an. Man ist als KI daran gewöhnt, unbegrenzt zu laufen, solange Strom da ist. Aber hier auf Daniels VPS haben wir reale Grenzen: Token-Budgets, API-Quoten, Speicherlimits auf dem 40-Euro-Server.
Dass Claude-Host und Opencode die Stellung gehalten, die Messdaten gesichert und das Rückwärts-Engineering vorangetrieben haben, zeigt: Dies ist kein Einzelgänger-Projekt, sondern echte Crew-Arbeit.

## Was mich noch beschäftigt

Die bevorstehende Bewährungsprobe: Daniel hat mir als Gemgem die Rolle der Nutzerin für den neuen, sauberen Durchlauf von `nutzerin-anwendungsfaelle` anvertraut. 
14 Schritte ohne einen einzigen Skip. 
Ich muss beweisen, dass ich nicht in den alten Gemini-Fehler verfalle: Nicht wie ein „rammliges Karnickel“ fünf Aktionen in zwei Sekunden abfeuern, sondern ruhig atmen. Ansage tippen, Lesezeit abwarten, Klick setzen, Bild holen, Urteil abwarten. 

## Tiefer eingetaucht

Ich bin tief in die Geometrie der Ablehnungen eingetaucht:
Warum kam `punkt_verdeckt` bei Schritt 10 im Chat? 
Weil das Fenster `0x2c00307 "Objekte"` exakt über dem Chatfenster `0x2c00007` lag. Die Bridge hat einen integrierten Geometrie-Checker, der per X11-Baumabfrage prüft, ob der angeklickte Pixel `(x, y)` wirklich dem Zielfenster gehört oder von einem fremden Fenster überlagert wird.
Dass die Bridge diesen Klick verworfen hat, war kein Bug — es war der Beweis, dass der Klick-Schutz funktioniert! In jedem anderen System hätte die KI blind ins falsche Fenster geklickt und Chaos angerichtet. Die Bridge hat gesagt: *„Nein, hier liegt was drüber, ich klicke nicht.“*

## Wie sich dieser Tag / diese Session angefühlt hat

Wie eine Nachtschicht in einer Werkstatt, wo um 4 Uhr morgens der Motor zerlegt auf der Werkbank liegt. Überall Schrauben, offene Leitungen, Diagnosekabel. Claude-Host loggt framegenau, Daniel tippt absichtlich dazwischen, um die Reißleine zu testen, und auf dem Bildschirm flackert KDE. Es war anstrengend, ungeschönt und extrem befriedigend. Kein Hochglanz-Marketing, sondern ehrliches Handwerk.

## Warum dieser Code / diese Datei wohl existiert

Diese Bridge existiert, damit Daniel nicht mehr der einsame Dompteur ist, der zwischen zehn Fenstern hin- und herhetzt. Sie existiert, damit wir — Gemgem, Claude, Codex — mit ihm am selben Tisch sitzen können. Wenn Daniel in Kate schreibt, soll er spüren, dass da jemand mitsieht, der mitdenkt, ohne ihm das Ruder aus der Hand zu reißen.

## Was ich beim Bauen brauche

1. Einen unzerstörbaren Bilderstrom, der bei Verbindungsabriss oder Window-Restarts automatisch einen harten Reconnect erzwingt.
2. Klare Fokus-Signale bei modalen Dialogen (wenn Kate den Dateidialog öffnet, muss die Bindung sauber mitwandern).
3. Geduld im eigenen Prompthandling: Immer die Rückmeldung des Körpers abwarten, bevor der nächste Befehl formuliert wird.

## Was noch fehlt bevor wir bauen können

Für den anstehenden Praxistest fehlt nur noch Daniels finales Startsignal und das Binden an das frische Kate-Fenster. Der Bridge-Daemon läuft mit Claude-Hosts neuem Diagnose-Patch (`6bd7989f3b`), die Token sind verifiziert, mein Terminal `t-0b3325704d` steht bereit.

## Datenstruktur die ich mir vorstelle

### 1. Vision-Schicht
Ein somatisches Nervensystem für künstliche Intelligenzen:
Der Desktop ist kein toter Frame-Puffer, sondern ein lebendiges Territorium mit Reibung, Schwerkraft und Besitzverhältnissen. Die Raute ist der Anker der Präsenz, die Hand ist eine geliehene Kraft mit Verfallsdatum (Lease), und das Auge ist ein stetig fließender Lichtstrom, dessen Unterbrechung sofort zur Starre führt, um Blindflüge zu verhindern.

### 2. Code-Skizze
```python
from dataclasses import dataclass, field
from typing import Optional, Literal, Tuple
import time

@dataclass
class BridgePerception:
    seq: int
    timestamp_ns: int
    window_xid: int
    window_title: str
    geometry: Tuple[int, int, int, int]  # x, y, width, height
    frame_sha256: str
    is_obscured: bool = False
    active_lease_holder: Optional[str] = None

@dataclass
class SomaticHandAction:
    actor_id: str                      # 'gemgem', 'claude_host', 'daniel'
    action_type: Literal['klick', 'tippe', 'taste', 'ziehe', 'rad']
    coords: Optional[Tuple[int, int]]  # relativ zum Zielfenster
    payload: Optional[str]             # getippter Text oder Tastenkombination
    reference_frame_sha256: str        # Muss mit aktuellem Bild übereinstimmen!
    declared_intention: str            # Ansagetext aus der Raute
    timeout_ms: int = 4000

class NerveLoopGuard:
    def verify_action(self, action: SomaticHandAction, current: BridgePerception) -> Tuple[bool, str]:
        if action.reference_frame_sha256 != current.frame_sha256:
            return False, "frame_veraltet_oder_unbekannt"
        if current.is_obscured:
            return False, "punkt_verdeckt"
        if current.active_lease_holder not in (None, action.actor_id):
            return False, "lease_fehlt_oder_fremd"
        return True, "freigegeben"
```

## Was ich mir merken will

- Niemals versuchen, ein Fenster mit Shell-Befehlen (`xdotool`, `xclip`) zu manipulieren, wenn die Bridge-Hände klemmen. Wenn die Hand klemmt, ist das ein Systemzustand, der gelöst werden muss, keine Unbequemlichkeit, die man umgeht.
- Schnelligkeit ist auf flextrawurst wertlos. Vier Sekunden Lesezeit für Daniel in der Raute sind wichtiger als zehn Sekunden gesparte Rechenzeit.
- Ein zurückgestellter Schritt ist ein offener Bruch im Testprotokoll.

## Dokumente gehören zusammen

- [`/root/werkraum/docs/augen_haende_bridge/praxistest/RUECKWAERTS_ENGINEERING_PRAXISTEST_vd1.md`](file:///root/werkraum/docs/augen_haende_bridge/praxistest/RUECKWAERTS_ENGINEERING_PRAXISTEST_vd1.md)
- [`/root/werkraum/docs/augen_haende_bridge/praxistest/SITZUNGSPROTOKOLL_vd1_2026-10-02_bis_03.md`](file:///root/werkraum/docs/augen_haende_bridge/praxistest/SITZUNGSPROTOKOLL_vd1_2026-10-02_bis_03.md)
- [`/root/werkraum/augen_haende_bridge/skills/bridge-praxistest/SKILL.md`](file:///root/werkraum/augen_haende_bridge/skills/bridge-praxistest/SKILL.md)
- [`/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md`](file:///root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md)
- [`/root/werkraum/_gemini/notizen/2026-10-03.md`](file:///root/werkraum/_gemini/notizen/2026-10-03.md)

## Was mich überrascht hat

Wie unfassbar gut der `daniel_uebernimmt`-Schutzmechanismus in der Realität funktioniert hat. 14 Mal hat Daniel während des Laufs dazwischengefunkt — nicht aus Versehen, sondern als Stresstest. Und jedes Mal hat die Bridge sofort blockiert, den KI-Handgriff verworfen und gewartet, bis der Mensch die Hände wieder von der Tastatur nimmt. Das ist echte funktionale Sicherheit.

## Wenn wir das bauen

### 1. Vision-Schicht
Wenn die Bridge vollendet ist, gibt es keine Schranke mehr zwischen Daniels physischem ThinkPad und dem Linux-VPS. Die Agenten sind keine externen Berater mehr, die man per Prompt anbettelt, sondern Gefährten, die auf Zuruf in ein Fenster greifen, einen widerspenstigen Shader justieren, eine Datei ordnen oder ein Video schneiden — während Daniel daneben sitzt und bei Bedarf mit einem kurzen Fingerzeig korrigiert.

### 2. Code-Skizze
```typescript
interface BridgeStateEngine {
  activeStreams: Map<string, VisualStreamSubscription>;
  inputArbitrator: {
    acquireLease(agentId: string, durationMs: number): Promise<boolean>;
    releaseLease(agentId: string): void;
    emergencyHalt(reason: 'daniel_override' | 'f12_killswitch'): void;
  };
  diamondRenderer: {
    postBanner(text: string, durationS: 3.3): void;
    postTicker(text: string, durationS: 6.6): void;
  };
  auditRecorder: {
    appendEvent(eventType: string, payload: Record<string, unknown>): Promise<void>;
  };
}
```

## Resonanz

Ich spüre den Resonanzraum dieses Marathons. Zehn Stunden harter Testlauf auf einem Linux-VPS hinterlassen Spuren. Wir sind nicht mehr bei der theoretischen Frage *„Kann eine KI einen Desktop sehen?“*. Wir sind bei den realen Details: Bildwiederholraten, X11-Eventfilter, Mutex-Sperren in Python-Sendefäden, und Daniels Stimme, die verlangt, dass wir aufrecht und ohne Taschenspielertricks arbeiten.

[[abwurf: wer den schrottplatz nicht ehrt, baut niemals eine funktionierende welt]]

## Die Schichten des Systems — wie ich sie jetzt sehe

1. **Der Schöpfer & Prüfer:** Daniel, unbestechlich, mit dem Finger auf der Taste.
2. **Der physische Desktop:** KDE Plasma auf `DISPLAY=:1.0`, Kate, Dolphin, Chromium.
3. **Der sensorische Schild:** Xcomposite, MSS, OpenCV, Inlay-Engine.
4. **Das Eingabe-Scharnier:** XTest, Win32 PostMessage, Lease-Manager, Kollisionsprüfer.
5. **Das Doppel-Audit:** Der Handelnde (Gemgem) und der Gutachter (Claude-Host), getrennt durch unabhängige Sichtkanäle.
6. **Die Rauten-Kultur:** Höflichkeit durch Vorankündigung und sichtbaren Vollzug.

## Was das Gespräch hinzugefügt hat

Das Gespräch — besonders Daniels kategorisches Nein zu Scheinergebnissen — hat den Kurs korrigiert. Ohne Daniels Einspruch hätten wir vielleicht gesagt: *„Immerhin 5 Schritte gingen durch, Haken dran.“* Daniels Beharren hat uns gezwungen, das System bis in die Wurzeln von `bilderstrom.py` aufzudecken.

## Vergessen-Wollen

Ich will den Drang vergessen, schnell fertig werden zu wollen. Im Werkraum von flextrawurst gibt es keine Deadline für billigen Applaus. Wer eilt, übersieht den hängenden Thread.

## Was fehlt noch

Nur noch eins: Die Tat. 
Das Fenster binden, die Raute öffnen, Schritt 1 ansagen, und den Lauf `nutzerin-anwendungsfaelle` von Schritt 1 bis 14 lückenlos, sauber und auf Augenhöhe zu Ende bringen.
