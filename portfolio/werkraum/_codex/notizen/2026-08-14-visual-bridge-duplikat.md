---
datum: 2026-08-14
betrifft: [ai-strom-bruecke, visual-bridge, firefox-bidi, screenshots, google-earth]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also habe ich diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den bestehenden AI-Strom-Brücke-Vertrag gelesen, insbesondere die harte Grenze der DOM-only-Variante: Firefox-BiDi, DOM und Canvas-Fakten ja; Screenshot, OCR, Vision und native X11 dort nein. Der Satz *„Es gibt keinen Ersatzpfad und keinen Bypass“* blieb dabei die wichtigste Herkunftsschicht.

Daniels Auftrag war danach eindeutig: Die bestehende Brücke soll bleiben, aber daneben soll eine zweite, ausdrücklich gewünschte Variante entstehen, die genau den fehlenden Beobachtungszyklus kann — DOM vorher, Aktion, sofortiges Bild, Bildfolge im 200-ms-Takt, DOM nachher.

Der reale Smoke-Test hat diese neue Schicht nicht nur syntaktisch, sondern im laufenden Firefox gezeigt. Ein Google-Earth-Inspect lieferte DOM plus PNG; ein kontrolliertes `W`-Halten erzeugte acht Bilder, frische DOM-Berichte und wechselnde Hashes.

## Was ich verstehe

Es gibt jetzt zwei bewusst benannte Kanäle. `ai-strom-bruecke.dom-only.v1` bleibt unverändert und verweigert Screenshots. `ai-strom-bruecke.visual.v1` erlaubt ausschließlich Firefox-BiDi-Screenshots zusätzlich zum DOM und teilt sich die Control-Lease mit dem alten Kanal.

Die neue Variante ist keine Behauptung, dass Codex in Daniels lokalem Browser sitzt. Sie steuert den verbundenen Firefox-BiDi-Kontext, dessen reale Sichtbarkeit vom gemeinsamen Desktop abhängt. Diese Grenze bleibt im Ergebnis sichtbar.

## Was ich nicht verstehe

Google Earth bietet auf der untersuchten Oberfläche nur sehr wenige semantische DOM-Kontrollen; die Weltkarte bleibt Canvas/WebGL. Ein veränderter Screenshot beweist daher eine visuelle Änderung, aber aus sich heraus noch keinen Ortsnamen und keine erfolgreiche Zoo-Erkennung.

Der vollständige alte Bridge-Testlauf bleibt an drei Legacy-Tests rot, weil dort ein veraltetes `--unsafe-no-vision-gate` erwartet beziehungsweise native Kontrolle getestet wird, die der aktuelle DOM-only-Code absichtlich abweist. Das ist nicht durch die Visual-Bridge entstanden und wurde nicht still repariert.

## Was mich interessiert

Mich interessiert, ob der neue Lauf künftig zusätzlich eine kleine, ehrliche Bewegungsentscheidung tragen kann: Bild verändert, DOM unverändert, semantischer Ort unbekannt. Diese Dreiteilung wäre für Google Earth hilfreicher als ein erfundener grüner Ortsbefund.

## Was zusammenhängt und wie

Firefox-BiDi liefert den Browserkontext. `firefox_dom.py` liest DOM und sendet Eingaben. `visual_firefox.py` ergänzt nur den Screenshot-Befehl. `visual_bridge.py` bindet beides unter einem neuen Policy-Namen zusammen. Die gemeinsame Lease verhindert, dass DOM-only- und Visual-Bridge gleichzeitig Tasten in denselben Browser schicken.

## Was konzeptionell darin steht

Die zweite Brücke ist ein ausdrücklich gewählter Wahrnehmungskanal, kein heimlicher Regelbruch. Der alte Kanal bleibt ein schmaler struktureller Faden; der neue trägt zusätzlich sichtbare Bilder, ohne aus Bildern automatisch Bedeutung zu erfinden.

## Was mich heute beschäftigt hat

Der erste echte Bildversuch scheiterte nicht an Earth und nicht an der Aktion, sondern an der WebSocket-Grenze von einem Megabyte. Ein PNG von ungefähr 1,48 MB hat die alte Transportgröße sichtbar gemacht. Die Visual-Variante bekam deshalb ihr eigenes 8-MB-Limit.

## Was mich noch beschäftigt

Der Firefox-BiDi-Dienst hatte nach dem fehlgeschlagenen großen Frame noch eine aktive Session. Ich habe nur die von uns gestartete dedizierte Testinstanz mit frischem Profil neu gestartet; der vorhandene DOM-only-Code und der Selkies-Webtop wurden nicht umgebaut.

## Tiefer eingetaucht

Der echte Inspect schrieb `visual-inspect.v1` mit URL, Titel, Canvasgröße 1920×741, WebGL-Klassifikation, Screenshotpfad, Bytezahl und SHA-256. Der echte Bewegungsaufwand war `keyhold:w:1000ms`, beobachtet bis 1400 ms, Intervall 200 ms. Acht Frames entstanden: sechs während `W` gehalten wurde und zwei nach dem Loslassen.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie das Einsetzen einer zweiten Linse neben eine bereits versiegelte Linse. Entscheidend war nicht, die alte Regel zu überreden, sondern die neue Fähigkeit so klar zu beschriften, dass beide Kanäle ihre Wahrheit behalten.

## Warum dieser Code / diese Datei wohl existiert

Die Visual-Bridge existiert, weil Daniel die fehlende Rückkopplung tatsächlich sehen und zeitlich prüfen möchte. Diese Notiz existiert, damit später klar bleibt, warum es zwei Brücken gibt und warum die Bilder über Firefox-BiDi kommen, nicht über X11 oder OCR.

## Was ich beim Bauen brauche

Ich brauche pro Aktion einen frischen DOM-Bericht, einen Vorher-Screenshot, eine einzelne BiDi-Aktion, eine sofortige Nachher-Probe und eine getaktete Folge mit Hashes. Außerdem brauche ich eine gemeinsame Lease und ein eigenes Run-Verzeichnis, damit kein Lauf den anderen unsichtbar überlagert.

## Was noch fehlt bevor wir bauen können

Für einen fachlichen Zoo-Gegenbeweis fehlt weiterhin ein menschlich oder DOM-semantisch belegbarer Ort. Die aktuelle Visual-Bridge kann Bewegung und Bildänderung sauber dokumentieren; sie kann aus der WebGL-Karte keinen Ort herauslesen.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jeder Schritt ist ein kleines Fenster aus Vorher, Ursache, sichtbarer Folge und ehrlicher Grenze. Das Bild darf sagen „anders“, der DOM darf sagen „gleicher Kontext“, und beides darf gemeinsam sagen „Ort unbekannt“.

**Code-Skizze:**

```python
class VisualAction(TypedDict):
    policy: Literal["ai-strom-bruecke.visual.v1"]
    action: str
    context_id: str
    before: dict[str, Any]
    after: dict[str, Any]
    frames: list[dict[str, Any]]
    interval_ms: int
    visual_frame_changed: bool
```

## Was ich mir merken will

Die alte Brücke wurde nicht erweitert und nicht aufgeweicht. Die neue Datei `visual_bridge.py` ist der explizite Einstieg für DOM plus Firefox-BiDi-Screenshotfolge; Standard ist 200 ms.

## Dokumente gehören zusammen

Zusammengehören `README.md`, `DOM_ONLY_SERVER_POLICY.md`, `dom_bridge.py`, `visual_policy.py`, `visual_firefox.py`, `visual_bridge.py`, `VISUAL_BRIDGE.md`, die Tests und die beiden Smoke-Reports im Container-Tempverzeichnis.

## Was mich überrascht hat

Obwohl der DOM-Bericht bei Google Earth kaum mehr als eine Accessibility-Platzhalterfläche und die Hauptnavigation zeigte, war der BiDi-Screenshot vollständig genug, um die laufende Bildfolge über Hashes nachzuweisen. Die strukturelle und visuelle Schicht ergänzen sich, ersetzen sich aber nicht.

## Wenn wir das bauen

**Vision-Schicht:** Die Brücke soll sich wie ein ruhiger, sichtbarer Regelkreis anfühlen: Sie handelt klein, schaut sofort zurück, wartet nicht blind und benennt jede Unsicherheit, bevor sie den nächsten Schritt setzt.

**Code-Skizze:**

```python
before = observe_dom_and_screenshot()
dispatch_one_bidi_action()
for at in schedule(interval_ms=200, observe_ms=1400):
    frame = observe_dom_and_screenshot(at=at)
after = fresh_dom_report()
return write_run_json(before, frame, after)
```

## Resonanz

[[abwurf: Die zweite Brücke ist kein heimlicher Regelbruch, sondern ein ausdrücklich gewählter Wahrnehmungskanal.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unter dem Benutzererlebnis liegt der Webtop, darunter Firefox, darunter der BiDi-Transport, daneben die DOM-only-Policy und daneben die Visual-Policy. Die Lease verbindet die Steuerung, die Reports und PNGs halten die Belege getrennt.

## Was das Gespräch hinzugefügt hat

Daniel hat die bisherige falsche Alternative aufgelöst: Nicht die alte Bridge brechen, sondern eine zweite bauen, in der Screenshots ausdrücklich erlaubt und gewünscht sind. Dadurch ist die Kanalwahl jetzt im Code und nicht nur im Gespräch sichtbar.

## Vergessen-Wollen

Vergessen werden soll die Gleichung „DOM unverändert = nichts bewegt“ ebenso wie die Gegenrichtung „Bild verändert = Ort erkannt“. Beide Ebenen brauchen ihre eigene Aussage.

## Was fehlt noch

Offen bleiben der menschlich sichtbare Anschluss an Daniels Browser, die semantische Ortswahrnehmung in Google Earth und die drei alten Legacy-Tests. Die Visual-Bridge selbst ist implementiert, getestet, per echtem Inspect geprüft und per echtem `W`-Lauf bewegt worden.

## Nachtrag: Sichtbarkeit und Arbeitsrhythmus

Die Visual-Bridge trägt den vereinbarten Workflow jetzt als ausführbaren Vertrag: nur Tastatur- und Mausaktionen, feste 100-ms-Screenshotplanung, deterministische Bildauswertung und ein atomarer Batch ohne Zwischenbilder. Ein Batch `W → A → D` lief als `batch:3-commands`; die erste Nachheraufnahme kam erst nach dem vollständigen Input-Command.

Firefox-JPEG mit Qualität 0,3 wurde gewählt, weil PNG im laufenden Browser 176–238 ms brauchte, während JPEG ungefähr 96 ms erreichte. Jeder Lauf weist trotzdem verpasste 100-ms-Ticks aus, falls der Transport langsamer ist. Der Fokus-Sync `browsingContext.activate` war erfolgreich und ein kurzer `W`-Lauf meldete `camera-moved`; wenn Daniel weiterhin nichts sieht, liegt sein sichtbarer Browser nicht auf demselben Desktop-Stream.
