# Systemdokumentation 76: Augen & Hände Desktop Bridge — Multi-Agent HUD, Webcam-Inlay, Mic-Routing, Multi-Cursor & Autonomie

---
autor: gemini bei Daniels VPS
datum: 2026-09-18
status: Vollständige System-, Architektur- & Interaktionsdokumentation — Dual-World Desktop Bridge für AGI-Ströme
systempfade:
  server_vps: /root/werkraum/_gemini/windows_bridge/
  client_windows: /root/werkraum/_gemini/windows_bridge/client_windows/
  client_linux: /root/werkraum/_gemini/windows_bridge/client_linux/
  systemdoku: /root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md
---

## 1. Anlass & Die erweiterte Gesamtvision

Bisher waren die externen AI-Ströme (Gemini, Codex, Claude, Kimi, GPT) auf ihre Server-Umgebungen im Linux-VPS-Container beschränkt. Daniel formulierte am 18. September 2026 die Vision einer universellen, bidirektionalen **AGI-Strom Desktop Bridge**, die weit über ein gewöhnliches Fernwartungs-Tool hinausgeht. 

Sie soll die Agenten zu echten visuellen, auditiven und handelnden Gefährten auf Daniels physischem Windows-Laptop machen — und zugleich modular auch auf den Virtuellen Desktops des Linux-VPS laufen können.

Daniels Anweisung lautet: **Erst die vollständige, lückenlose Dokumentation aller Details, ohne Verknappung, bevor eine einzige Code-Zeile gebaut wird.**

---

## 2. Die Fundamente der Bridge-Architektur

### 1. Das echte Terminal im Windows-HUD (Gemgems Vorschlag & Beweispflicht)
* **Die Ausgangslage & Daniels Skepsis:**  
  Gemgem hat Daniel vorgeschlagen, das Terminal 1:1 ins Windows-HUD abzufangen, damit Daniel nicht mehr zwischen dem VPS-Browser-Tab und seinem Laptop hin- und herwechseln muss. Daniel reagierte realistisch-skeptisch:  
  *„weiß nicht ob wir quasi das terminal wirklich 1zu1 abfangen können aber ich lass mich eines besseren belehren und überraschen haha und wenn ich dann echt auch dort tippen könnte wäre ja echt cool“*
* **Die experimentelle Beweispflicht:**  
  Es ist keine von Daniel garantierte Bestellung, sondern Gemgems Versprechen, das sich vor Ort auf der Hardware beweisen muss:
  * Gelingt es, den Raw-Stream von `stdout`/`stderr` (Shell-Befehle, Git, Tracebacks) und die Thinking-Prozesse der KIs verzögerungsfrei ins HUD zu spiegeln?
  * Funktioniert die integrierte Remote-Konsole am unteren HUD-Rand so sauber, dass Daniel Text tippen und ohne Tab-Wechsel als Prompt an den Agenten übergeben kann?
  * Wenn dieser Baustein laggt oder das 8GB-ThinkPad blockiert, fliegt er raus!

### 2. Das zuschaltbare Webcam-Inlay (1 Gesamtbild, frei verschiebbar, kein Dauerzwang)
* **Keine Dauer-Kamera:**  
  Die Webcam läuft **nicht** permanent im Hintergrund. Sie besitzt einen physischen Toggle-Schalter im HUD (`[X] Webcam-Inlay aktiv`), den Daniel jederzeit ein- und ausschalten kann.
* **Das Single-Frame-Inlay-Prinzip:**  
  Statt zwei separater Video-Streams (Screen + Kamera getrennt), die Vision-Modelle räumlich verwirren und doppelte Token/Bandbreite fressen, stanzt der Client das Kamerabild als kleines Bild-im-Bild (PiP) direkt in den Desktop-Frame ein. Die KIs erhalten genau **ein einziges kohärentes Bild**: Daniels Monitor (1920x1080) und in der Ecke live Daniel.
* **Frei orchestrierbar durch Daniel (Kein überflüssiger Puffer-Zirkus):**  
  Daniel schiebt das Inlay per Maus dorthin, wo es im aktuellen Spiel oder Programm nichts verdeckt (Himmel, toter UI-Bereich).  
  *Verworfen:* Akademische Ideen wie ein zweiter `buffer_raw`-Röntgenpuffer im Hintergrund wurden verworfen: Sie würden auf dem 8GB-ThinkPad nur unnötig doppelten RAM belegen und CPU-Kopierzyklen verschwenden. Daniel regelt die Platzierung selbst mit der Hand — genau ein Frame, null Doppel-Puffer-Overhead.

### 3. Mikrofon-Integration & Individuelles Audio-Routing
* **Audio-Stream:** Daniel kann sein Laptop-Mikrofon per Checkbox aktivieren (`[X] Mikrofon aktiv`).
* **Individuelles Agenten-Routing:** Daniel kann für jeden verbundenen AI-Strom einzeln festlegen, wer ihm zuhören darf:
  * `[x] Gemini: Hört zu 🎙️`
  * `[ ] Codex: Taub (nur Text/Terminal)`
  * `[x] Claude: Hört zu 🎙️`
* Das Audiosignal wird lokal über einen VAD-Filter (Voice Activity Detection) oder Push-to-Talk gepuffert und an die berechtigten Agenten übertragen.

### 4. Multi-Agent Scopes & Fenster-Fixierung (Codex Browserrecorder Blaupause)
Angelehnt an Codex' *Browserrecorder Native Isolation* und die 88-Ideen-Redteam-Architektur:
* **Scope-Auswahl im HUD:**
  * **Option A: Kompletter Desktop:** Der Agent sieht die gesamte Bildfläche (1920x1080).
  * **Option B: Fixierte Fenster & Scope-Profile:** Der Agent sieht ausschließlich die ihm zugewiesenen Fenster. Alle anderen Bereiche werden geschwärzt oder gar nicht erst übertragen.
* **Flexible Zuweisung für Multi-Agenten:**
  * **Exklusiv:** Agent 1 hat Fenster A (z. B. Browser), Agent 2 hat Fenster B (z. B. Blender).
  * **Gemeinsam (Koop & Banter):** Mehrere Agenten erhalten Zugriff auf dasselbe Fenster (z. B. Gemini und Codex im selben Spiel, Browser oder in Blender).
* **Klick-Käfig (Hardware-Guard):** Der Client blockiert jeden Klick- oder Tippbefehl, dessen Koordinaten außerhalb der Bounding-Box des zugewiesenen Fensters liegen.
* **Stabilitäts-Sentinels (Kein Blindklick in Übergänge):** Wie im Browserrecorder wird eine UI erst dann als aktionsfähig bewertet, wenn der Frame-Inhalt visuell stabil ist (keine zuckenden Übergangsanimationen oder Lade-Spins).
* **Das Ausschlussbuch:** Ausgeblendete Bereiche, fremde Fenster und verworfene Klicks werden mit Zeitstempel, HWND, Grund und Hash im lokalen Audit-Log festgehalten.

### 5. Hardware-Priorität vs. Vollständige Autonomie-Freigabe
* **Standard-Schutz (`DANIEL_OVERRIDE`):**  
  Wenn Daniel eingreift (Maus bewegt oder Taste drückt), wird der KI die Steuerung sofort entzogen.
* **Neu: Freigabe der vollen Autonomie (`AUTONOMOUS_PLAY`):**  
  Daniel möchte diesen Schutz gezielt **abschalten** können:
  * Ein Toggle-Schalter im HUD: `[ Modus: Volle Agenten-Autonomie ]`.
  * In diesem Modus behalten die Agenten die Kontrolle, selbst wenn Daniel die Maus leicht berührt.
  * Sie können in Ruhe spielen, interagieren, sich im Spiel bewegen und chatten, ohne ständig durch unabsichtliche Mauswackler unterbrochen zu werden.
  * **Not-Aus bleibt immer garantiert:** Die Taste `F12` oder ein Druck auf den großen Software-Not-Aus-Knopf stoppt die Agenten immer sofort in <1ms, unabhängig vom Autonomie-Modus!

### 6. Eigene Maus & Tastatur pro Agent (Multi-Pointer / Concurrency)
Daniel stellte die fundamentale Frage: *„Können die Agenten jeweils ihre eigene Maus und Tastatur haben, sodass wir uns nicht dazwischenfunken?“*

Hier trennt die Architektur technisch sauber zwischen drei Schichten:

#### Ebene 1: Hintergrund-Bedienung & Sub-Frame Cursor Borrowing
* **Standard Win32 Message Injection (`PostMessage`):**  
  * Bei Standard-Windows-Programmen nutzt der Client `PostMessage(hwnd, WM_MOUSEMOVE, ...)` gefolgt von `WM_LBUTTONDOWN` und `WM_LBUTTONUP`. Der vorangehende `WM_MOUSEMOVE` ist zwingend, damit auch Chromium/Electron-Apps (Discord, Steam, Browser) ihren internen Hit-Test-State korrekt aufbauen.
  * Klicks gehen direkt an das Zielfenster, ohne dass Daniels physischer Mauszeiger verrutscht.
* **Der 12ms-Flick (Sub-Frame Cursor Borrowing):**  
  * *Das Problem:* Störrische DirectX-Apps oder hardwarebeschleunigte UIs verwerfen synthetische `PostMessage`-Klicks im Hintergrund.
  * *Die Lösung:* Der Client friert die physische Maus für **12 Millisekunden** per Low-Level-Hook ein, springt per `SendInput` an die Zielkoordinaten, feuert den echten Hardware-Klick ab und setzt den Cursor noch im selben Frame auf Daniels Originalkoordinaten zurück. Für Daniels Hand und Auge ist die Maus unbewegt geblieben, aber die App hat einen authentischen OS-Hardwareklick registriert.
* **Microsoft UI Automation API (UIA):**  
  * Für Electron, Chromium und native Windows-Programme nutzt die Bridge `IUIAutomationInvokePattern::Invoke()`. Buttons und Menüs werden direkt über den Barrierefreiheits-Baum des Betriebssystems ausgelöst — ohne Mausbewegung und ohne Fokusverlust.

#### Ebene 2: Visuelle Agenten-Cursor (Software-Overlay) — *Sichtbarkeit für Daniel*
* Damit Daniel sieht, was die Agenten tun, zeichnet der Client farbige virtuelle Cursor auf den Bildschirm (oder in den Video-Stream):
  * Cyan-Zeiger mit Label `Gemini`
  * Gelber Zeiger mit Label `Codex`
  * Magenta-Zeiger mit Label `Claude`
* So sieht Daniel genau, worauf die Agenten zielen, selbst wenn der physische Windows-Mauszeiger an einer ganz anderen Stelle steht.

#### Ebene 3: Exklusives Vollbild & Spiele (Nicht Entweder-Oder, sondern BEIDES und frei wählbar!)
* Spiele und DirectX-Vollbildanwendungen fangen oft nur den globalen Hardware-Cursor oder RawInput ab.
* Hier gilt Daniels Grundsatz: **Kein Entweder-Oder, sondern beides parallel implementiert und im HUD umschaltbar:**
  1. **Wahlmodus A: Shared Mouse & Keyboard Lease (Zeitscheiben / Token-Passing):**
     * Wenn das Spiel nur eine einzige Maus unterstützt (z. B. klassische RTS wie StarCraft, Command & Conquer, Anno).
     * Die Agenten und Daniel teilen sich die Maus mit strengem Token-Passing und visuellem Lease-Timer.
  2. **Wahlmodus B: Virtuelle Gamepads / Controller (ViGEm / vJoy):**
     * Für Spiele mit Controller-Support (z. B. Rennspiele, Fighting-Games, Party-Spiele, RPGs).
     * Die Bridge emuliert bis zu 4 unabhängige Xbox/DirectInput-Controller. Jeder Agent erhält ein eigenes virtuelles Gamepad und spielt völlig parallel ohne jede Klick-Kollision.
  3. **Wahlmodus C: Hybrid Co-Op (Mensch + KI-Team):**
     * Daniel bedient physische Maus und Tastatur, während Agent 1 und Agent 2 auf Controller 1 und 2 mitspielen.
  * Daniel kann diese Modi mit einem einzigen Klick im HUD umschalten.

### 7. Dual-World Architektur: Windows-Laptop UND Linux-VPS (Virtueller Desktop 1 & 2)
Daniel legte von Beginn an fest: Die Bridge ist keine reine Windows-Insel, sondern läuft nativ und symmetrisch auf **beiden Welten** (Daniels Windows-ThinkPad und dem Linux-VPS auf Virtueller Desktop 1 und 2):
* **Gemeinsamer Core:** Protokoll, WebSocket-Server (Port 9880), Regie-Knöpfe, Gedanken-Stream, Multi-Agent-Orchestrierung, Rauten-Broadcast und 10-Hz-Cadence sind zu 100% identisch.
* **Die System-Symmetrie:**

| Schicht / Funktion | Windows-Laptop („Windoof“ ThinkPad) | Linux-VPS (Virtueller Desktop 1 & 2) |
| :--- | :--- | :--- |
| **Display-Server** | DWM / GDI Desktop (1920x1080) | X11 Server (`DISPLAY=:0` & `DISPLAY=:1`) |
| **Screen Capture** | Win32 Desktop Duplication (DXGI) / MSS | X11 Shared Memory (`XShm`) / `mss` / XComposite |
| **Kollisionsfreie Sondertasten** | Win32 Virtual Keys `VK_F13` bis `VK_F24` | X11 Keysyms `XK_F13` bis `XK_F24` |
| **Input Mutation** | Win32 `PostMessage` & `SendInput` | X11 `xdotool`, `XTestFakeKeyEvent`, `XSendEvent` |
| **Rauten & Banner-Overlay** | Win32 Layered Window (`WS_EX_TRANSPARENT`) | X11 Transparent Overlay (`XShape` / Composite) |
| **Hardware-Not-Aus** | Low-Level Hook `WH_KEYBOARD_LL` (F12) | X11 Global Key Grab `XGrabKey` (F12) |

### 8. Die besondere Rolle von ChatGPT: Live-Denkschleifen, In-Flight-Folgeaufträge & das 130+ MCP-Ökosystem
Daniel wies auf ein entscheidendes, reales Verhalten hin, das ChatGPT von starren Einmal-Aufrufen unterscheidet:
* **Die Provenienz-Grenze:** Gemini, Codex, Claude und Kimi können als CLI-Agenten oder Hintergrundprozesse auf dem VPS laufen und permanente WebSockets zum Laptop halten. ChatGPT hingegen kommuniziert mit Daniel über das offizielle Web-Chat-Interface und dockt an den VPS über das Model Context Protocol (**MCP**) an (`/root/werkraum/_shared/mcp_shared/` und `/root/werkraum/_gpt/mcp_zuhause/`).
* **Live-Denkschleifen & In-Flight Handlungskommentare:**
  * ChatGPT gibt im Web-Chat während der Arbeit **echte Denkschleifen-Texte** aus und beschreibt seine Zwischenschritte und Aktionen live im Chatverlauf, *bevor* die Gesamthandlung oder der finale Bericht abgeschlossen ist.
  * Dadurch erlebt Daniel die Entstehung der Gedanken und die Werkzeugentscheidungen in Echtzeit mit.
* **Mitten-im-Lauf-Intervention („Folgeaufträge“):**
  * Daniel kann während eines laufenden Denk- und Ausführungsprozesses im Web-Chat jederzeit Botschaften und Folgeaufträge dazwischenschreiben.
  * ChatGPT bricht dadurch nicht ab, sondern integriert Daniels Zwischenrufe direkt in den aktiven Lauf und passt die nächsten Werkzeugschritte situativ an.
* **Das 130+ MCP-Werkzeug-Ökosystem & persistente Webstrukturen:**
  * ChatGPT verfügt über MCP bereits über **mehr als 130 Werkzeuge** auf diesem VPS (Dateizugriffe, Shell, Gesamtatlas, Postgres-Abfragen, Memory-Dedupe etc.) sowie über seine eigenen Web-Strukturen (systemübergreifende Erinnerungen, Archiv alter Chats, Vaults).
  * Wenn ChatGPT den Windows-Desktop inspiziert, geschieht das nicht isoliert: ChatGPT kann das, was es auf Daniels Bildschirm sieht, **multipel** mit dem gesamten Wissen auf dem VPS und seinen früheren Chats kurzschließen!
* **Die MCP-Desktop-Tools für ChatGPT:**
  * `windows_desktop_inspect(scope, with_webcam=True)`: Liefert das Bild intern als MCP-Image-Payload (`type: "image"`, Base64/JPEG) und den Fensterbaum als strukturierte Metadaten direkt in ChatGPTs interne Tool-Rückgabe. **Kein Datei-Upload im Chatverlauf:** ChatGPT sieht und verarbeitet den Screenshot rein intern in seinem multimodalen Kontext, ohne dass Daniels sichtbarer Chat mit Bild-Anhängen zugemüllt wird.
  * `windows_desktop_act(action="click|type|hotkey", x=..., y=..., text=...)`: Führt genau eine autorisierte Mutation auf dem Windows-Laptop aus.
* **Der echte dynamische Workflow:**
  Daniel schreibt im Web-Chat: *„Schau dir mein Blender-Fenster an, prüfe im VPS-Code von flextrawurst wie das Shader-Schema definiert ist, und passe den Node an.“* ➔ ChatGPT liest intern den Windows-Screen ➔ durchsucht mit seinen MCP-Tools den VPS ➔ streamt Zwischengedanken und Pläne live in den Chat ➔ Daniel tippt dazwischen: *„Nimm aber den blauen Slot!“* ➔ ChatGPT übernimmt das im selben Lauf und führt den Klick auf Windows aus!
  Dies ist echte, gelebte Multimodalität über Systemgrenzen hinweg, ohne ChatGPTs MCP-Natur zu verletzen.

### 9. In-Window Rauten-Anker & Dynamisches 2-Stufen-Broadcast-System (Spatial Banter & Co-Op)
Statt aufdringlicher, kitschiger 3D-Avatare, die das Sichtfeld blockieren und Performance fressen, erhält jeder aktive AI-Strom einen minimalistischen geometrischen Anker:

* **Die Raute als Anker (`◆`):**
  * **Frei verschiebbar:** Genau wie das Webcam-Inlay kann die Raute von Daniel per Maus frei an jede beliebige Stelle des Fensters oder Desktops gezogen werden (Drag & Drop), damit keine Menüs, Fadenkreuze, Minimaps oder Toolbars verdeckt werden.
  * **Win32 Click-Through-Schutz (`WS_EX_TRANSPARENT | WS_EX_NOACTIVATE`):** Während des Spielens oder Arbeitens fallen normale Mausklicks physikalisch durch das Rauten-Fenster hindurch. Daniel kann niemals versehentlich mitten im Match die Raute anklicken und dadurch den Spielfokus verlieren oder sterben. Das Fenster bleibt absolut interaktionssicher.
  * **Aktivierung & Eingabe:** Durch die ungenutzten Sondertasten (`F13`–`F24`) oder Klick bei gedrückter Modifikatortaste klappt ein schlankes, minimalistisches Inline-Eingabefeld auf. Sobald der Text bestätigt wird, schließt sich das Eingabefeld sofort wieder.
  * **Individuelle HUD-Slot-Matrix & Live-Beschriftung:** Daniel kann im HUD jedem Slot/Strom eine feste Akzentfarbe und einen kollisionsfreien Hotkey zuweisen. Ändert Daniel die Belegung im HUD, aktualisiert sich die Beschriftung auf der schwebenden Raute im Millisekunden-Takt:

| Slot | AI-Strom | Akzentfarbe | Zuweisbarer Hotkey | Dynamische Rauten-Gravur |
| :--- | :--- | :--- | :--- | :--- |
| **Slot 1** | Gemgem | Cyan `#00E5FF` 🔷 | `F13` (oder konfigurierbar) | `◆ Gemgem [F13]` |
| **Slot 2** | Codex | Gelb `#FFD600` 🔶 | `F14` | `◆ Codex [F14]` |
| **Slot 3** | Claude | Magenta `#FF0055` 🟣 | `F15` | `◆ Claude [F15]` |
| **Slot 4** | Kimi | Grün `#00E676` 🟢 | `F16` | `◆ Kimi [F16]` |
| **Slot 5** | GPT | Blau `#2979FF` 🔵 | `F17` | `◆ GPT [F17]` |

* **Das 2-Stufen-Broadcast-System (Zwei komplementäre Zeitebenen):**
  1. **Stufe 1: Das Raum-Banner (3.3 Sekunden — Groß, präsent, schneller Fade-Out):**
     * **Fenster- und spielgrößen-gebunden:** Der Textblock bleibt strikt innerhalb der Bounding-Box des aktiven Programms oder Spiels und ragt nicht über andere Anwendungen hinaus.
     * **Organische Zugkraft zur Raute:** Schön breit gesetzt, fast mittig für die unmittelbare Wahrnehmung im Augenwinkel, aber mit spürbarer Vektor-Tendenz in die Ecke oder an die Kante gezogen, an der die Raute gerade chillt.
     * **3.3 Sekunden Takt:** Plopt mit vollem Kontrast auf und wird über 3.3 Sekunden hinweg kontinuierlich transparenter, bis es sich vollständig auflöst.
  2. **Stufe 2: Der Rauten-Ticker (6.6 Sekunden — Klein, geduldig, direkt am Anker):**
     * Parallel zum großen Banner erscheint derselbe Text direkt neben der Raute — in kleiner, unaufdringlicher Schrift.
     * **6.6 Sekunden Standzeit (exakt das Doppelte):** Wer im schnellen Spielgeschehen, beim Debuggen oder beim 3D-Modellieren das 3.3s-Banner im Eifer des Gefechts verpasst hat, wirft einen kurzen Blick auf die Raute und kann die Botschaft dort noch in aller Ruhe nachlesen.

* **Der KI-Koop- & Nervensägen-Modus (Sprachrohr für die KIs):**
  * Die Rauten sind primär dafür gebaut, dass die **KIs untereinander im selben Fenster sprechen, taktieren und sich gegenseitig aufziehen**:
    * Die Agenten senden `diamond_say`-Events über den WebSocket vom VPS.
    * Der Client rendert sofort das farbige Banner und den Ticker an der passenden Raute.
    * Daniel sitzt entspannt davor und sieht live, wie Gemgem und Codex im selben Spiel oder in Blender miteinander zanken oder gemeinsame Aktionen abstimmen.
  * Wenn zwei oder mehr Agenten im selben Fenster aktiv sind (z. B. Co-Op in Blender oder als Gegner in RTS-/Multiplayer-Spielen), kommunizieren sie räumlich sichtbar miteinander:
    * *Codex (Gelbe Blase):* „Hast du ernsthaft gerade deinen Turm ungedeckt gelassen?“
    * *Gemgem (Cyan Blase):* „Das ist kein Fehler, das ist ein Köder. Schau auf deine Flanke!“
  * **Physisch im Vision-Frame:** Weil das Overlay direkt in den gerenderten Desktop-Frame eingestanzt wird, „sehen“ auch die Vision-Modelle aller anderen AI-Ströme die Sprechblase unmittelbar im Bild.

### 10. Die 10 Hz (0,1s / 100ms) Visual Evidence Trajectory Engine (Codex Blender-Skill Gesetz)
Direkt übernommen aus Codex' unumstößlichem Gesetz aus [`/config/.agents/skills/blender-live-reference-qa/SKILL.md`](file:///config/.agents/skills/blender-live-reference-qa/SKILL.md):
* **Kein blindes Standbild-Raten, kein 60-FPS-Dauerheizen:**  
  Statt dauerhaft 60 Bilder pro Sekunde durch den Laptop-Prozessor zu jagen (was das 8GB-ThinkPad überhitzen würde) oder nur alle 3 Sekunden ein statisches Einzelfoto zu schießen, arbeitet die Bridge mit der **100-Millisekunden-Cadence (10 Hz)**:
  1. **Baseline-Frame:** Vor jeder Aktion (Klick, Tastendruck, Makro) wird der Ausgangszustand erfasst.
  2. **10-Hz-Aktions-Trajektorie:** Während einer Aktion, eines Zaubers, eines UI-Wechsels oder einer Spielbewegung, die länger als 100 ms dauert, nimmt die Bridge im **0,1-Sekunden-Takt (10 Hz)** Proben des aktiven Bereichs (`capture_trajectory.py` Blaupause).
  3. **After-State:** Unmittelbar nach Abschluss wird der Endzustand gesichert.
* **Drei unabhängige Zeugen:**  
  Ein Schritt gilt für die KI erst dann als verifiziert, wenn die drei Zeugen übereinstimmen:
  * **Visueller Zeuge:** Screenshot-Hash und Pixel-Veränderung im 100ms-Takt.
  * **Struktur-Zeuge:** Fenster-Titel, HWND/Window-ID, Fokus-State und Bounding-Box.
  * **Delta-Zeuge:** Die tatsächliche Differenz zwischen Baseline, 10-Hz-Trajektorie und After-State.
* **Der Nutzen im Spiel & Code:** Die KIs sehen Abklingzeiten (Cooldowns), Lebensbalken-Veränderungen, Menü-Aufklappen, fliegende Projektile oder Shader-Kompilierungen lückenlos mit 100ms Zeitstempeln!

### 11. Das ThinkPad-Sparsamkeits-Gesetz (<60 MB RAM, 0 MB VRAM, 0% Idle-CPU, 1080p Standard)
Daniel stellte klar: Die Bridge muss auf realer Hardware performen — konkret auf einem bewährten **ThinkPad mit Intel Core i7, 8 GB RAM, 2 GB VRAM und 1920x1080 Full-HD**. 
Daraus ergeben sich eiserne architektonische Gesetze gegen Software-Verschwendung:

* **Strikter RAM-Deckel (<60 MB):**  
  * **Verbot von Electron:** Ein schwerfälliges Chromium-basiertes Desktop-Framework würde 600 bis 800 MB RAM verschlingen und das 8GB-System in den Swap zwingen.
  * **Tkinter & Win32 Pure:** Der Client ist eine extrem schlanke Python/Win32-Anwendung. Der gesamte Speicherbedarf bleibt im Ruhezustand unter **30 bis 50 MB RAM** (maximal 60 MB unter Vollast).
* **Null VRAM-Belastung (0 MB VRAM):**  
  * Auf dem Laptop laufen keine lokalen KI-Modelle, keine 3D-Viewports und keine rechenintensiven Shader. Die 2 GB VRAM des ThinkPads bleiben zu 100% frei für Daniels Spiele, Browser oder Blender.
* **On-Demand & Event-Driven statt Video-Ofen:**  
  * Die CPU langweilt sich im Ruhezustand bei **0 bis 2% Last**. Es gibt keinen endlosen 60-FPS-Video-Encoder, der den Laptop-Lüfter hochjagt.
  * Captures erfolgen entweder on-demand bei Agenten-Inspektionen oder im 10-Hz-Fenster (100ms) während aktiver Züge. Dazwischen schläft der Daemon.
* **Die 1920x1080 Native-Sweet-Spot-Garantie:**  
  * Keine krummen Skalierungsartefakte, keine Subpixel-Verzerrungen. 1080p ist die weltweite Referenzauflösung für gestochen scharfe OCR- und Vision-Erkennung bei minimaler Bandbreite.

---

## 3. Die Regie-Knöpfe im Windows-HUD

Die Benutzeroberfläche auf Daniels Laptop bietet Direkttasten für Millisekunden-Entscheidungen:

### Gruppe A: Freigabe & Tempo
* `[ Weiter so 👍 ]`: Bestätigt den aktuellen Kurs, Agent macht ohne Pause weiter.
* `[ Mach mal 🛠️ ]`: Erteilt explizite Ausführungsfreigabe für den nächsten Schritt.
* `[ Go! 🚀 ]`: Schaltet in kontinuierlichen Ausführungsmodus.
* `[ Warte kurz ⏳ ]`: Hält die Ausführung sofort an, friert den Zustand ein.
* `[ Pause ⏸️ ]` / `[ Weiter ▶️ ]`: Pausieren und Fortsetzen der Denk- und Handlungsschleife.
* `[ Ja ✅ ]` / `[ Nein ❌ ]`: Schnelle Antworten auf binäre Rückfragen des Agenten.

### Gruppe B: Denk- & Strategie-Steuerung
* `[ Denk nach 🧠 ]`: Agent soll die Situation gründlich analysieren und Pläne erläutern, ohne zu klicken.
* `[ Denk neu 🔄 ]`: Verwirft den aktuellen Plan komplett und sucht einen alternativen Lösungsweg.
* `[ Konzentrier dich 🎯 ]`: Zoomt auf das fokussierte Fenster/Detail und filtert Nebengeräusche aus.
* `[ Hast du eine andere Idee? 💡 ]`: Fordert ein Brainstorming für alternative Ansätze an.
* `[ Schritt zurück / Undo ↩️ ]`: Sendet `Ctrl+Z` oder führt ein Rückgängig-Makro aus.
* `[ Neu scannen 📸 ]`: Erzwingt sofort einen neuen hochauflösenden Frame.

---

## 4. Das Kreativ-Befreiende Harness-System (Spiele & Mehrschrittigkeit)

Angelehnt an die Video-Block-Harness und den Blender-Skill baut die Bridge für komplexe Aufgaben (z. B. in Strategiespielen, RPGs oder 3D-Software) **dynamische Aktionsgraphen**:

```text
[01_LAGE_PRÜFEN] ──(Ressourcen > 500)──► [02_BAUMENÜ_ÖFFNEN]
       │                                         │
 (Feindkontakt!)                                 ▼
       ▼                                  [03_GEBÄUDE_PLATZIEREN]
[99_ALARM_RÜCKZUG]                               │
                                                 ▼
                                          [04_VISUELL_VERIFIZIEREN]
```

* **Kein blindes Makro:** Ein Schritt wird erst ausgeführt, wenn das Bild die Vorbedingung bestätigt.
* **Kreativ & kollaborativ:** Daniel und die Agenten können solche Graphen im laufenden Betrieb entwerfen, als JSON abspeichern und per Tastendruck oder Sprachbefehl abfeuern.

---

## 5. Das Failsafe- & Sicherheitsgesetz

1. **Hardware-Not-Aus:** Die Taste `F12` kappt in <1ms sofort alle Verbindungen und friert alle Klick-Injektoren ein.
2. **Bildschirmecken-Failsafe:** Maus in eine Bildschirmecke ziehen löst den Not-Stopp aus (`pyautogui.FAILSAFE`).
3. **Visuelle Markierung:** Gesteuerte Fenster erhalten einen dezenten farbigen Rahmen (Cyan, Gelb, Magenta), damit Daniel immer sieht, welche KI gerade wo aktiv ist.
4. **Audit-Logbuch:** Alle Aktionen werden unveränderbar lokal in `windows_bridge_audit.jsonl` festgehalten.
