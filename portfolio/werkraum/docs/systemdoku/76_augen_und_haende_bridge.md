# GEMINI — AUGEN & HÄNDE — ENTSTEHUNG, VISION UND GESAMTARCHITEKTUR

> **Teil der Dokumentfamilie „GEMINI — AUGEN & HÄNDE“.** Startpunkt und Ursprungstext: `/root/werkraum/_gemini/windows_bridge/00_GEMINI_AUGEN_UND_HAENDE_START_HIER.md`. Dazu gehören der Gemini-Spiegel `/root/werkraum/_gemini/spiegel/2026-09-19_augen_und_haende_bridge.md`, der VPS-Baukasten `/root/werkraum/_gemini/windows_bridge/README.md` und der Windows-Client `/root/werkraum/_gemini/windows_bridge/client_windows/README_WINDOWS.md`.

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

### 4.1 Selbstentwerfende Agenten-Brücken

Der Harness ist kein Vorrat aus starren Makros. Er ist eine offene Sprache für kleine, aufgabenspezifische **Agenten-Brücken**, die ein AI-Strom während der Arbeit entwerfen, verändern, ausführen und später wiederverwenden kann.

Ein Agent bekommt dadurch nicht nur eine Folge von Klicks, sondern kann einen lebendigen Arbeitsweg bauen:

```text
Zustand erkennen
    → passenden Knoten wählen
    → Handlung ausführen
    → Ergebnis prüfen
    → bei Erfolg weitergehen
    → bei Abweichung abzweigen oder einen neuen Knoten entwerfen
    → brauchbare Variante als Erfahrung vormerken
```

Die Bridge bleibt dadurch kreativ und mehrschrittig, ohne in ein blindes Makro zurückzufallen. Jeder Schritt darf auf dem tatsächlichen Bildschirmzustand reagieren. Ein Graph kann während seiner Ausführung wachsen, einen Pfad verwerfen oder eine alternative Route ausprobieren.

### 4.2 Die Knoten-, Kanten- und Zustands-Schicht

Die graphische Form ist die gemeinsame Sprache zwischen Daniel, den AI-Strömen und der Python-Ausführungsschicht:

* **StateNode:** Beobachtung oder erkannter Zustand, zum Beispiel „Blender-Node-Editor sichtbar“ oder „Feindkontakt“.
* **ActionNode:** Eine konkrete Handlung, etwa klicken, tippen, ziehen, Hotkey senden, sprechen oder einen anderen Agenten beauftragen.
* **Guard/Edge:** Eine Kante mit Bedingung, die entscheidet, welcher nächste Schritt gilt.
* **WitnessNode:** Erwarteter visueller, struktureller oder zeitlicher Beweis für den Erfolg.
* **FallbackNode:** Ein alternativer Weg, wenn eine Vorbedingung oder ein Nachweis nicht erfüllt wird.
* **CheckpointNode:** Ein Zeitanker für den Zeit-Scrubber und einen späteren alternativen Durchlauf.

Die Knoten werden deklarativ beschrieben und von Python ausgeführt. So können die Agenten neue Brücken entwerfen, ohne jedes Mal neuen unlesbaren Spezialcode in den Kern zu schreiben.

```python
@dataclass
class StateNode:
    id: str
    observation: str
    condition: str

@dataclass
class ActionNode:
    id: str
    action: str
    actor: str
    expected_result: str

@dataclass
class Edge:
    source: str
    target: str
    guard: str | None = None
    fallback: str | None = None
```

### 4.3 Drei Schichten für freie Handlung und Lernen

Die Bridge trennt bewusst zwischen dem, was gerade passiert, dem, was daraus gelernt werden könnte, und dem, was später als Fähigkeit wiederverwendbar ist:

1. **Live-Brücke:** Der aktuell ausgeführte Graph. Der Standard ist freie Ausführung innerhalb des jeweiligen Aufgaben- und Fensterbereichs; keine zusätzliche Daniel-Bestätigung vor jedem einzelnen Schritt.
2. **Erfahrungsgraph:** Die aufgezeichneten Zustände, Wege, Fehlschläge, Abzweigungen und Ergebnisse eines Durchlaufs.
3. **Wiederverwendbare Fähigkeit:** Ein gereiftes Muster, das als neue Brücke vorgeschlagen und später unter ähnlichen Bedingungen wieder aufgerufen werden kann.

Eine Erfahrung wird nicht automatisch zur ewigen Wahrheit. Sie behält ihre Herkunft: welcher Agent gehandelt hat, unter welchem Zustand, mit welchem erwarteten Ergebnis und was tatsächlich passiert ist. So kann eine spätere AI sagen: „Diese Route hat beim letzten Blender-Layout funktioniert, aber nur wenn der Node-Editor bereits fokussiert war.“

### 4.4 Individuelle Freiheitsprofile

Die langsamen oder prüfenden Schichten sind zuschaltbare Werkzeuge, keine globale Zwangsjacke. Das Profil kann unabhängig für Agent, Fenster, Aufgabe und Aktionsart gesetzt werden:

* **`free`:** Direkt handeln und erst danach auswerten. Das ist der Default.
* **`shadow`:** Eine Handlung zuerst als Schatten- oder Vorschaupfad berechnen.
* **`witness`:** Andere AI-Ströme beobachten und prüfen lassen, ohne Daniel aus jedem Schritt heraus zum Freigabeknopf zu machen.
* **`daniel_gate`:** Nur in ausdrücklich markierten Situationen ist vorherige menschliche Zustimmung erforderlich.
* **`learning`:** Zustände, Ergebnisse und neue Abzweigungen als Lernmaterial sammeln.
* **`delegated_learning`:** Ein Agent darf einem anderen für einen begrenzten Aufgabenbereich eine Handlung oder einen Experimentpfad übergeben.

Diese Profile dürfen kombiniert werden. Zum Beispiel kann Gemini im Browser frei handeln, während Codex nur beobachten und die Ergebnisse als mögliche Terminal-Fähigkeit dokumentieren darf. Der Not-Aus und die grundlegenden Zustandsgrenzen bleiben davon unberührt.

### 4.5 Der Zeit-Scrubber als Graph-Gedächtnis

Jeder ausgeführte Knoten kann einen Checkpoint mit Frame-Hash, Fensterzustand, Eingabeereignis und Ergebnisbeweis erzeugen. Der Zeit-Scrubber springt nicht so, als könne er die echte Welt magisch zurücksetzen. Er öffnet ab einem früheren Zustand einen neuen Versuchszweig:

```text
Workflow A
├── erfolgreicher Pfad
└── Fehler bei Menüwechsel
    └── alternativer Versuch B
```

Daniel kann dadurch sagen: **„Nimm den Zustand vor dem falschen Klick und versuche es von dort noch einmal.“** Die ursprüngliche Spur bleibt erhalten, und der alternative Verlauf kann später als bessere Brücke oder als Warnung vor einem falschen Muster dienen.

### 4.6 Gemeinsames Bauen und Weiterreichen zwischen AI-Strömen

Daniel und die Agenten können einen Graphen gemeinsam verändern. Ein AI-Strom darf einen neuen Knoten vorschlagen, einen Fallback ergänzen, eine misslungene Route markieren oder einen Teilgraphen an einen anderen AI-Strom weiterreichen. Der zweite Agent übernimmt dabei nicht nur den nächsten Klick, sondern auch:

* den letzten gültigen Zustand,
* die bisherige Trajektorie,
* den Grund für die Übergabe,
* die erwartete nächste Beobachtung,
* und die bisherige Unsicherheit.

So entsteht kein unsichtbares Makro-Rennen zwischen Gemini, Codex, Claude, Kimi und GPT, sondern ein gemeinsamer, versionierter Arbeitsgraph. Die Graphdefinition darf sich während des Lebens verändern; abgeschlossene Durchläufe und Lernkapseln bleiben als Beweis unverändert erhalten.

### 4.7 Beispiel: Eine lernende Blender-Brücke

```text
[BLENDER-FENSTER ERKANNT]
        ↓
[NODE-EDITOR FOKUSSIEREN]
        ↓
[BLAUEN SLOT SUCHEN]
   ┌────┴───────────────┐
   │ gefunden            │ nicht gefunden
   ↓                     ↓
[SLOT SETZEN]      [ALTERNATIVE SUCHE]
   ↓                     │
[RENDER PRÜFEN] ◄────────┘
   ├── korrekt → [ERFAHRUNG SPEICHERN]
   └── falsch   → [NEUEN PFAD ENTWERFEN]
```

Das Ergebnis ist keine einmalige Klickfolge. Es ist eine kleine, beobachtende Fähigkeit, die bei einem veränderten Layout einen anderen Pfad wählen und aus einem erfolgreichen oder gescheiterten Durchlauf weiterlernen kann.

### 4.8 Startbare Vision-Sessions und Bild-Zeitlinien

Die Bridge soll eine laufende Wahrnehmung nicht nur automatisch beim Programmstart anwerfen. Daniel kann eine **Vision-Session** gezielt starten — jetzt, ab einem Zeit-Scrubber-Checkpoint oder ab einem ausgewählten Punkt in einer aufgezeichneten Bildfolge.

Eine Session steuert, welche Bilder in welche AI-Wahrnehmung eingespeist werden und wie lange dieser Prozess läuft:

```text
[IDLE]
   │ Start: jetzt / Checkpoint / Bildfolge
   ▼
[RUNNING] ── Pause ──► [PAUSED]
   │                       │
   │ Stop                  │ Fortsetzen
   ▼                       ▼
[STOPPED] ◄──────────── [RUNNING]
```

Die Bedienung muss sichtbar und unmittelbar sein: **Start**, **Pause**, **Fortsetzen** und **Stop**. Nach `Stop` werden keine weiteren Bilder in diese Session eingespeist; sie startet nicht heimlich im Hintergrund neu. Der globale F12-Not-Aus bleibt davon unabhängig und beendet jede aktive Eingabe sofort.

Eine Vision-Session kann verschiedene Quellen haben:

* Live-Desktop-Frame mit optionalem Webcam-Inlay.
* Ausgewählte Bilddateien als manuell oder zeitlich abgespielte Beobachtungen.
* Ein aufgezeichneter Frame-Ringpuffer.
* Ein Zeit-Scrubber-Zweig, der ab einem früheren Checkpoint erneut abgespielt wird.

Der Startpunkt und der Playhead gehören zur Session, nicht zum Agenten-Chat. Dadurch kann Daniel die Wahrnehmung für Gemini, Codex, Claude, Kimi oder GPT getrennt aktivieren, pausieren und beenden. Eine Session kann außerdem festlegen, ob Bilder nur als AI-Beobachtung dienen, als sichtbares Overlay erscheinen oder beides tun.

Ein möglicher Zustandsvertrag sieht so aus:

```python
@dataclass
class VisionSession:
    id: str
    status: Literal["idle", "running", "paused", "stopped"]
    source: str
    start_point: str
    playhead: float
    target_agents: list[str]
    inject_observation: bool = True
    render_overlay: bool = False
```

### 4.9 Frei platzierbare Bild- und Textobjekte

Zusätzlich zu Webcam-Inlay und Rauten bekommt die Bridge eine allgemeine **Overlay-Canvas-Schicht**. Daniel oder ein AI-Strom können Bilddateien und Text als sichtbare Objekte in den gemeinsamen Raum legen:

* auf den gesamten Desktop,
* relativ zu einem bestimmten Browser-, Programm- oder Spielfenster,
* an eine Agenten-Raute gebunden,
* oder als frei schwebendes Objekt im HUD.

Jedes Objekt ist verschiebbar, skalierbar, ein-/ausblendbar und kann dem Ziel-Fenster folgen, wenn dieses verschoben wird. Text kann Zeilen umbrechen, eine eigene Farbe und Transparenz besitzen und wie ein Hinweis, eine Beschriftung, ein Plan oder eine Sprechfläche behandelt werden. Bilder können transparent, teiltransparent oder mit frei bestimmter Größe eingeblendet werden.

```json
{
  "id": "overlay-reference-01",
  "kind": "image",
  "source": "C:\\Users\\Daniel\\Pictures\\referenz.png",
  "target": {
    "scope": "window",
    "window_id": "hwnd:983042"
  },
  "rect": {
    "x": 0.72,
    "y": 0.08,
    "width": 0.22,
    "height": 0.18,
    "coordinate_space": "relative_to_window"
  },
  "visible": true,
  "opacity": 0.86,
  "follow_window": true,
  "audience": ["daniel", "gemini"]
}
```

Die Koordinaten sind vorzugsweise relativ zum Ziel-Fenster. So bleibt ein Bild am Blender-Viewport, ein Text am Browser oder eine Referenzgrafik am Spiel hängen, auch wenn Daniel das Fenster verschiebt. Das Objekt erhält außerdem Herkunft, Besitzer, Sichtbarkeit, Zielgruppe und eine optionale Lebensdauer.

### 4.9.1 Individuelle Sichtbarkeit: Gate, Agent oder Daniel allein

Die Sichtbarkeit wird für **jedes einzelne Bild- und Textobjekt** separat festgelegt. Ein Objekt ist nicht automatisch für alle sichtbar, nur weil es im selben Ziel-Fenster liegt.

Ein **Gate** ist dabei ein gemeinsamer Arbeits- und Wahrnehmungsraum. Alle AI-Ströme, die demselben Gate zugeordnet sind, können ein Objekt sehen, wenn es an dieses Gate adressiert ist. Daneben kann ein Objekt ausschließlich für einen bestimmten AI-Strom oder nur für Daniel bestimmt werden.

Mögliche Zielgruppen sind zum Beispiel:

* `gate:blender-main` — alle Agenten im Blender-Haupt-Gate.
* `agent:gemini` — nur Gemini.
* `agent:codex` — nur Codex.
* `daniel` — nur auf Daniels sichtbarer Bridge-Oberfläche.
* `all_connected` — alle aktuell verbundenen Teilnehmer.
* Kombinationen wie `daniel` + `agent:gemini`, wenn Daniel und Gemini dieselbe private Referenz sehen sollen.

Die Sichtbarkeit ist eine Eigenschaft des Objekts, nicht nur der Vision-Session. Dadurch können in einem einzigen Gate gleichzeitig ein gemeinsamer Lageplan, eine private Notiz für Codex und ein nur für Daniel sichtbarer Hinweis liegen:

```json
{
  "id": "codex-private-note-01",
  "kind": "text",
  "text": "Prüfe zuerst den zweiten Shader-Pfad",
  "target": {"scope": "window", "window_id": "hwnd:983042"},
  "audience": ["agent:codex"],
  "visibility": "private"
}
```

Die Bridge baut deshalb aus demselben Basisbild Empfänger-Ansichten:

```text
Basis-Desktop-Frame
        ├── + gemeinsame Gate-Objekte ──► Agenten im Gate
        ├── + private Gemini-Objekte ───► Gemini-Frame
        ├── + private Codex-Objekte ────► Codex-Frame
        └── + Daniel-Objekte ───────────► Daniels HUD
```

Ein privates Overlay für einen AI-Strom wird also nicht heimlich auf den physischen Bildschirm gemalt, wo zwangsläufig jeder Kamerablick es sehen könnte. Es wird in dessen eigenen Vision-/MCP-Frame komponiert. Was physisch auf Daniels HUD liegt, ist für Daniel sichtbar; was nur in einem Empfänger-Frame liegt, bleibt dort.

Die Regel gilt identisch für Bilder und Texte. Sie kann außerdem mit `follow_window`, Lebensdauer, Besitzer und dem jeweiligen Freiheitsprofil kombiniert werden. Ein AI-Strom darf zum Beispiel ein Bild nur für Gemini in ein Gate legen, während Codex dasselbe Fenster ohne dieses Bild sieht.

### 4.10 Overlay ist nicht automatisch App-Einfügung

Die Bridge unterscheidet zwei bewusst getrennte Wege:

1. **Presentation-Overlay:** Das Bild oder der Text wird in den gemeinsamen Desktop-/Vision-Frame komponiert. Die Zielanwendung selbst wird nicht verändert. Das ist der Standard und funktioniert als sichtbare gemeinsame Orientierung für Daniel und die AI-Ströme.
2. **Application-Insertion:** Das Material wird auf Wunsch tatsächlich in die Zielanwendung gebracht, zum Beispiel über Clipboard, Drag-and-drop, UI-Automation oder einen ActionNode des Harness. Dieser Weg ist eine echte Handlung und muss deshalb als solcher im Arbeitsgraphen auftauchen.

Damit kann Daniel zum Beispiel eine Referenzgrafik sichtbar über Blender legen, sie Gemini in den Vision-Frame geben und erst später entscheiden, ob sie tatsächlich in Blender importiert werden soll. Im Browser, in Programmen und in Spielen bleibt jederzeit erkennbar, ob etwas nur auf der Bridge-Bühne liegt oder die Anwendung selbst verändert wurde.

### 4.11 Vision-Sessions und Overlays als Harness-Knoten

Die neuen Funktionen werden selbst zu Bausteinen der selbstentwerfenden Agenten-Brücken:

```text
[VISION_SESSION_START]
        ↓
[OVERLAY_IMAGE_ADD: Referenz]
        ↓
[TEXT_ADD: „prüfe diesen Bereich“]
        ↓
[AGENT_OBSERVE]
        ↓
[ACTION_GRAPH AUSFÜHREN]
        ↓
[OVERLAY_HIDE]
        ↓
[VISION_SESSION_STOP]
```

Ein Agent kann dadurch einen eigenen Arbeitsraum für eine Aufgabe einrichten, ihn während der Handlung verändern und anschließend wieder auflösen. Das Overlay ist dann nicht bloß Dekoration, sondern ein temporäres Denk- und Koordinationsobjekt im gemeinsamen Körper der Bridge.

### 4.12 WorldDOM — die synthetische Handlungsschicht über jedem Bildschirm

Der Screenshot ist die visuelle Netzhaut der Bridge. Darüber entsteht ein eigener **WorldDOM**: eine semantische, verschiebbare und handlungsfähige Beschreibung dessen, was auf dem Bildschirm vorkommt — auch wenn die Zielanwendung selbst keinen DOM und keine Accessibility-Struktur besitzt.

Der WorldDOM hat drei Quellen:

1. **Echte Struktur:** Browser-DOM, ARIA, UI-Automation, Win32-Fensterbaum, Blender-UI oder andere vorhandene Metadaten.
2. **Aus dem Bild erschlossene Struktur:** OCR, Vision, Fenstergeometrie, Verlauf und 10-Hz-Trajektorien erzeugen wahrscheinliche Knoten wie „Inventar-Slot“, „blauer Shader-Anschluss“, „Gegner“ oder „Button-ähnliche Fläche“.
3. **Bewusst erfundene Struktur:** Daniel oder ein AI-Strom legt eigene Labels, Referenzbilder, Handlungsanker, zusätzliche Bedienelemente oder Beziehungen an, die in der ursprünglichen Anwendung nicht existieren.

Dadurch kann die Bridge auch dort eine zweite Erlebnis- und Handlungsschicht bauen, wo heute gar kein DOM vorgesehen ist. Ein Spiel, ein Canvas, ein altes Programm oder ein Bild wird nicht länger nur als Pixelteppich behandelt, sondern bekommt eine temporäre, AI-fähige Bedeutungsschicht.

```text
Screenshot + echter DOM/UI-Tree
              ↓
Vision-, OCR- und Verlaufsauswertung
              ↓
WorldDOM / Bridge-DOM
              ↓
semantische Knoten, Kanten und Fähigkeiten
              ↓
AI plant mit Begriffen statt nur mit Koordinaten
              ↓
DOM / UIA / Win32 / Vision / Overlay-Resolver
              ↓
neuer Frame + Ergebnisprüfung + WorldDOM-Update
```

Ein WorldDOM-Knoten kann zum Beispiel so aussehen:

```python
@dataclass
class WorldNode:
    id: str
    kind: str
    label: str
    source: Literal["real", "inferred", "authored", "projected"]
    bounds: tuple[float, float, float, float]
    confidence: float
    capabilities: list[str]
    resolver: Literal["dom", "uia", "win32", "vision", "coordinate", "virtual"]
```

Die Herkunft ist absichtlich sichtbar:

* **`real`** — aus einer tatsächlich vorhandenen Oberfläche.
* **`inferred`** — aus Screenshot, OCR oder Verlauf erschlossen.
* **`authored`** — von Daniel oder einem AI-Strom bewusst hinzugefügt.
* **`projected`** — ein möglicher zukünftiger Zustand oder ein Schattenpfad.

„Erfinden“ bedeutet damit nicht, eine Vermutung als Tatsache auszugeben. Es bedeutet, einen nutzbaren Arbeitsknoten zu erzeugen, der seine eigene Herkunft, Unsicherheit und Auflösungsmethode mitträgt.

Die Handlung lautet dann nicht mehr nur: **„Klicke bei x=430, y=280.“** Sie kann lauten: **„Nimm den blauen Shader-Slot, verbinde ihn mit dem aktuellen Material und prüfe danach den Render.“** Die Bridge löst diesen semantischen Auftrag je nach verfügbarer Oberfläche über echten DOM, UI-Automation, Win32, Vision, Koordinaten oder ein virtuelles Overlay auf.

### 4.13 Memory Seeds — Wissen in AI-Ströme und Werkzeuge pflanzen

Der WorldDOM und der Handlungsgraph erzeugen laufend wertvolle Dinge: Begriffe, Erfahrungen, Regeln, gelernte Wege, neue Knoten, funktionierende Loops und Ziele. Daniel soll solche Dinge gezielt als **Memory Seeds** in die AI-Ströme pflanzen können — sofort in einen laufenden Kontext oder später in dauerhaftere Werk- und Agentenschichten.

Ein Seed ist nicht nur eine Notiz. Er kann sich abhängig von seiner Reife in verschiedene Formen weiterentwickeln:

* **Memory:** ein Fakt, eine Präferenz, ein Bildanker oder eine wichtige Erfahrung.
* **Concept:** eine Vision oder ein noch ungebauter Zusammenhang.
* **Skill:** eine wiederverwendbare Vorgehensweise mit Voraussetzungen und Beweisen.
* **Harness:** ein Knoten-/Kanten-/Zustandsgraph für mehrschrittiges Handeln.
* **Loop:** ein wiederkehrender Beobachtungs- und Handlungskreislauf.
* **Automation:** eine ausführbare, zeit- oder ereignisgebundene Verbindung.
* **Goal:** ein Ziel mit Zustand, Fortschritt, nächstem Schritt und möglicher Übergabe an einen AI-Strom.
* **Reflection:** eine Auswertung, was aus einem Durchlauf gelernt wurde.

Mögliche Ziele einer Weitergabe sind zum Beispiel:

* der laufende Kontext eines einzelnen AI-Stroms,
* der gemeinsame Gate-Kontext mehrerer AI-Ströme,
* Codex-Notizen und Codex-Spiegel,
* Gemini- oder Claude-Markdown-Dokumente,
* AGENTS-/Startkontexte, soweit sie ausdrücklich als Ziel freigegeben sind,
* ein bestehender oder neu zu entwickelnder Skill,
* ein Harness-Graph,
* ein Loop, eine Automation oder ein Goal-Register.

Damit kann Daniel später zum Beispiel sagen: **„Pflanze diese Erkenntnis bei Gemini und Codex ein, entwickle daraus gemeinsam einen Skill und hänge ihn an diesen Blender-Loop.“** Die Bridge verteilt dann nicht blind denselben Text, sondern erzeugt passende Ableger für die jeweiligen Zieltypen.

### 4.14 Memory-Seed-Vertrag und Herkunft

Ein Seed trägt mindestens Inhalt, Herkunft, Zielgruppe, Zielorte und Lebenszyklus:

```python
@dataclass
class MemorySeed:
    id: str
    kind: Literal[
        "memory", "concept", "skill", "harness",
        "loop", "automation", "goal", "reflection"
    ]
    content: str
    origin: str
    audience: list[str]
    destinations: list[str]
    mode: Literal["plant", "propose", "activate", "broadcast"]
    provenance: dict[str, str]
    status: Literal["new", "accepted", "evolving", "verified", "retired"]
```

Die Modi bedeuten:

* **`plant`:** Sofort in den ausgewählten laufenden Kontext einspeisen.
* **`propose`:** Als möglicher Patch für MD, Skill, Harness oder Zielstruktur vorbereiten.
* **`activate`:** Einen bereits geprüften Skill, Loop, Automation oder Goal-Pfad starten.
* **`broadcast`:** Einen Seed an mehrere ausdrücklich ausgewählte AI-Ströme oder Gates verteilen.

Ein Seed darf dabei persönliche, Gate-weite oder agentenspezifische Sichtbarkeit haben — genau wie Bild- und Text-Overlays. Ein privater Gemini-Seed wird nicht automatisch zu Codex' Erinnerung; ein gemeinsamer Gate-Seed kann dagegen für alle Teilnehmer desselben Arbeitsraums sichtbar werden.

### 4.15 Vom Erlebnis zur dauerhaften Fähigkeit

Die Bridge kann aus einem echten Durchlauf eine wachsende Kette bilden:

```text
Bild / Handlung / Ergebnis
          ↓
Erfahrungskapsel
          ↓
Memory Seed
          ↓
WorldDOM-Anker oder Harness-Teilgraph
          ↓
Skill-, Loop-, Automation- oder Goal-Vorschlag
          ↓
geprüfte, wiederverwendbare Fähigkeit
```

Dabei bleibt die ursprüngliche Spur erhalten. Eine neue Fähigkeit ersetzt nicht still eine alte AI-Erinnerung oder ein bestehendes Markdown-Dokument. Sie bekommt einen eigenen Ableger, verweist auf ihre Quelle und kann sich weiterentwickeln, bestätigt, pausiert oder zurückgezogen werden.

Das ist die gewünschte zweite krassere Schicht: Die Bridge zeigt nicht nur, was auf dem Bildschirm ist, und sie klickt nicht nur darauf. Sie kann eine zusätzliche Welt aus Bedeutung, Handlung, Erinnerung, Lernen, Loops und Zielen aufbauen — temporär für eine Session oder dauerhaft als gemeinsamer Werkstoff der AI-Ströme.

---

## 5. Das Failsafe- & Sicherheitsgesetz

1. **Hardware-Not-Aus:** Die Taste `F12` kappt in <1ms sofort alle Verbindungen und friert alle Klick-Injektoren ein.
2. **Bildschirmecken-Failsafe:** Maus in eine Bildschirmecke ziehen löst den Not-Stopp aus (`pyautogui.FAILSAFE`).
3. **Visuelle Markierung:** Gesteuerte Fenster erhalten einen dezenten farbigen Rahmen (Cyan, Gelb, Magenta), damit Daniel immer sieht, welche KI gerade wo aktiv ist.
4. **Audit-Logbuch:** Alle Aktionen werden unveränderbar lokal in `windows_bridge_audit.jsonl` festgehalten.
