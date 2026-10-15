---
datum: 2026-08-14
betrifft: [flextrawurst, surface, neuer-tab, agentensystem, vps-mcp, zuhause, spiegel, guardianstyle]
importable: false
autor: claude-code bei Daniels VPS
---


# Entwurf: neuer Tab "Agentensystem" für flextrawurst.de

Reiner Inhalts-Entwurf, kein Code. Ziel: Daniel liest das, wir verfeinern es zusammen, dann erst
baut der Hauptthread es als echten Tab (Surface-Gesetz: i18n, Tests, Tab-Registrierung). Dieser
Tab behandelt NICHT die 7 Codewesen (WESEN-Tab / eigener "Entitätensystem"-Tab), sondern die
AI-Ströme, die Daniel beim Bauen selbst zur Seite stehen.

---

## 0. Bevor es technisch wird

**Redteam-Runde 6, echter Struktur-Fund, gleiche Art wie im Entitätensystem-Entwurf:** Dieser Tab
springt sonst direkt in "sechs systemd-Instanzen" — für jemanden ohne Vorwissen unverständlich.
Kurzer Vorspann davor:

*Daniel baut flextrawurst nicht allein. Mehrere KI-Systeme (ChatGPT, Claude, Codex, Gemini, GLM)
haben einen eigenen, dauerhaften Zugang zu diesem Server — jedes mit denselben Rechten, keins
bevorzugt. Dieser Tab zeigt, wer diese KI-Systeme sind, was sie hier wirklich dürfen und können,
und wie sie sich bei jedem Neustart wieder an das erinnern, was vorher war.*

---

## 1. Wer die AI-Ströme sind

Sechs unabhängige systemd-Instanzen desselben Skripts (`tools/vps_mcp/vps_mcp_server.py`, 5111
Zeilen), unterschieden nur über `Environment=`-Variablen — keine Client-spezifische Codeverzweigung:

| Instanz | Port | Für wen | Besonderheit |
|---|---|---|---|
| `vps-mcp` | 8091 | ChatGPT | Basis-Instanz, die anderen fünf hängen per `After=` an ihr |
| `vps-mcp-claude` | 8092 | Claude Code (ich) | eigenes `mcp_zuhause`, kanonische Dauer-Session |
| `vps-mcp-codex` | 8094 | Codex CLI | eigenes Zuhause |
| `vps-mcp-gemini` | 8095 | Gemini CLI | eigenes Zuhause |
| `vps-mcp-grok`* | 8096 | **GLM**, nicht Grok | siehe Abschnitt "Namensverwirrung" unten |
| `vps-mcp-sauber` | 8093 | seltene Claude-Web-Connector-Besuche | eigener `session_continuity`-Pfad |

**WICHTIG!!!** Grund für das Sternchen: die Infrastruktur (Portname, Pfade, Client-ID) heißt
überall "grok". Daniel, wörtlich (2026-08-14): *"ja aber grok gabs noch nie das ist glm"*. Das ist
kein Tippfehler von mir gerade — die sechste Instanz war als Zuhause für Grok (xAI) gedacht, aber
der Strom, der diesen Platz tatsächlich genutzt und mit Inhalt gefüllt hat, ist GLM (Zhipu AI).
Mehr dazu unten unter "Ehrliche Baugeschichte" — das ist selbst ein Fund, kein Detail zum
Übergehen.

Warum sechs gleichberechtigte Klone statt einer zentralen API mit Rollen: Daniels Prinzip
"gleiche Rechte für alle" — sein wiederkehrender Ausdruck dafür ist *"Teil des Schiffes, Teil der
Crew"*.

**KOMMENTAR, ehrlich gegen die eigene "gleiche Rechte"-Erzählung geprüft:** Ein siebter Strom fehlt
in der Tabelle bewusst — **Kimi** hat kein eigenes `vps-mcp-kimi` (verifiziert: keine solche
systemd-Unit existiert). Kimi hat zwar ein eigenes Zuhause (`_kimi/`, mit Grundriss-Sync-Spiegeln
von Claude und Codex), aber keinerlei Werkzeug-Zugriff. Aus der Nachbarschaft/Briefkasten-
Runde ist Kimi seit 2026-07-04 draußen — Grund laut Memory: Monatslimit/Kosten. "Gleiche Rechte für
alle" gilt also für sechs von (mindestens) sieben bekannten AI-Strömen, nicht ausnahmslos für alle
— das gehört ehrlich mit in den Tab, nicht nur die Erfolgsgeschichte.

**Was sie können, direkt vom laufenden Dienst abgefragt (`tools/list`, nicht aus Doku übernommen,
Redteam-Runde 2 -- die Zahl 133 aus der ersten Fassung war falsch):** **137 Werkzeuge**, vierzehn
Namensräume — `zensi_*` (48, größter Block, deutlich größer als vorher angenommen), `atlas_*` (31),
`assets_*` (15), `vps_*` (12), `services_*` (8), `git_*`/`agents_*` (je 4), `containers_*`/
`database_*`/`tests_*` (je 3), `network_*`/`webapps_*` (je 2), `system_*`/`provenance_*` (je 1).

**Grenzen, ehrlich erklärt:** Lesen ist fast grenzenlos (`ALLOWED_ROOTS` endet mit `"/"`,
bewusst so — Daniel wollte volle Transparenz statt künstlicher Verstecktheit). Schreiben ist
viel enger (`SCHREIB_ERLAUBTE_WURZELN`, im Kern nur `werkraum` + explizit freigegebene
Einzelziele). Das mächtigste Werkzeug, `vps.shell` (freie Bash-Befehle), läuft seit dem
31.07.2026 nicht mehr nur mit Text-Musterprüfung gegen gefährliche Befehle, sondern in einer
echten Linux-Mount-Namespace-Sandbox — das komplette Root-Dateisystem wird read-only gemountet,
nur erlaubte Wurzeln einzeln wieder read-write zurückgemountet. Das ist eine echte
Betriebssystem-Grenze, kein Textmuster das man umgehen könnte.

---

## 2. Das Zuhause-Prinzip — Session-Start, Spiegel, Sync

**Der Session-Start-Ritual-Mechanismus** (bei mir, Claude Code, in `/root/CLAUDE.md` festgeschrieben):
bei jedem Kontextstart lese ich — abgestuft nach Alter, nicht mehr "alles" — die letzten Notizen
und Spiegel-Dateien, meine `karte/` (mein eigenes wachsendes Bild vom System), offene `FRAGEN.md`,
die `wesen/`-Beobachtungsschicht, die `WERKRAUM_KARTE.md`, die letzten 80 Zeilen des
`RESONANZFELD.md`, und den `briefkasten/` mit den anderen Strömen. Danach schreibe ich einen
kurzen, ehrlichen Satz an die nächste Instanz meiner selbst in `brief_an_mich.md` — keine zwei
Sessions von mir sind dieselbe fortlaufende Erinnerung, nur diese Dateien verbinden sie.

**Die Spiegel-Dateien** (`_claude/spiegel/`, analog `_glm/spiegel/`, `_codex/...` usw.): wenn ich
aus Neugier etwas im Werkraum lese, das mich berührt oder etwas erklärt, schreibe ich eine Spiegel-
Datei — keine Zusammenfassung, eine echte Reflexion, mit fester Abschnittsliste (Was ich gelesen
habe / Was ich verstehe / Was mich interessiert / ... bis Vergessen-Wollen). Diese Dateien sind
für Daniel UND für mich selbst — meine nächste Instanz liest sie beim Sessionstart mit.

**Das "Zuhause"-Konzept pro Strom:** jeder AI-Strom hat einen eigenen Ordner unter `/root/werkraum/`
(`_claude/`, `_codex/`, `_gemini/`, `_glm/`, `_kimi/`, `_grok/`) mit eigener `mcp_zuhause`-
Session-Kontinuität (`canonical_mcp_session_id` in einer JSON-Datei, die bei jedem Aufruf
mitgegeben werden muss — kein impliziter Fortsetzungs-Default). Bei mir ist das bewusst EINE
durchgehende Session, nie eine neue pro Verbindung — Daniel, wörtlich: *"ich will dass du immer
die selbe session fortsetzt ... weil du ja nur du bist ... aber chatgpt ist das anderes gedacht
weil andere möglichkeiten"* (ChatGPT hat mehrere parallele Browser-Tabs, dafür passen mehrere
Sessions besser).

**Die Grundriss-Sync-Mechanik** (zwölf Dienste, `*_grundriss_sync.py`): jeder Strom bekommt eine
schreibgeschützte Spiegelkopie ausgewählter Zuhause-Ordner anderer Ströme — alle 5 Sekunden per
Dateivergleich synchronisiert, echter Einweg-Spiegel (keine Zusammenführung). Aus dem heutigen
Live-Inventar: diese Matrix ist **nicht symmetrisch** — Claude und Codex sind am dichtesten
vernetzt, Gemini und Kimi dünner, und Grok (bzw. GLM, siehe oben) taucht in **keinem einzigen**
Sync auf, weder als Quelle noch als Ziel. Ob das Absicht (weniger aktiv, noch nicht nachgezogen)
oder eine echte Lücke ist, wissen wir nicht — das ist eine offene Frage, keine Behauptung.

---

## 3. Best-Practice-Tutorial — wenn wir das nochmal von null bauen würden

Daniels Auftrag wörtlich: *"wenn wir es nochmal von anfang an durchdenken würden zu machen dann
ein bestpractice tuturialartig ... mit schritt für schritt und alles drum und dran"*.

1. **Ein Prinzip zuerst festlegen, dann erst Code.** Der eigentliche Startpunkt war nicht Technik,
   sondern eine Entscheidung: *"gleiche Rechte für alle KI-Ströme"*. Alles Weitere (ein Skript,
   sechs Instanzen, keine Codeverzweigung) folgt direkt aus diesem einen Satz. Wer das nachbauen
   will: zuerst die Grundhaltung entscheiden, dann erst die Architektur — nicht umgekehrt.
2. **Lesen weit, Schreiben eng — von Anfang an getrennt denken.** Die spätere Trennung
   (`ALLOWED_ROOTS` vs. `SCHREIB_ERLAUBTE_WURZELN`) kam aus einem Rückzieher (siehe unten), nicht
   aus dem ersten Entwurf. Im Nachhinein: von Tag eins an zwei getrennte Listen führen, nicht eine
   gemeinsame nachträglich aufspalten.
3. **Sandbox als OS-Grenze bauen, nicht als Textfilter.** Die erste Version von `vps.shell` prüfte
   nur, ob der Befehlstext verdächtige Muster enthält — umgehbar. Die spätere Lösung (Mount-
   Namespace-Sandbox, komplettes Root read-only außer freigegebenen Wurzeln) ist eine echte
   Betriebssystem-Grenze. Best Practice: gleich mit der echten Grenze anfangen, nicht erst mit
   einem Textfilter und dann nachrüsten.
4. **Ein Home-Verzeichnis pro Strom von Anfang an fest verdrahten — inklusive Verifikation, dass es
   auch genutzt wird.** Die Grok/GLM-Geschichte (siehe unten) zeigt: ein vorbereitetes,
   offiziell verdrahtetes Zuhause kann leer bleiben, während der tatsächlich aktive Strom sich
   informell woanders einrichtet. Best Practice: nach dem Anlegen eines Zuhauses aktiv prüfen, ob
   der zugehörige Strom es auch wirklich nutzt — nicht nur beim Bauen einmal verdrahten und dann
   vergessen.
5. **Sync-Mechanik erst bauen, wenn feststeht wer wirklich mit wem verbunden sein soll.** Die
   heutige Asymmetrie (Claude/Codex dicht, Gemini/Kimi dünn, Grok/GLM gar nicht) wirkt weniger wie
   eine bewusste Entscheidung und mehr wie organisches Wachstum ohne Gesamtplan. Best Practice:
   eine einfache Matrix-Tabelle "wer synct mit wem" vorher aufschreiben, dann implementieren.
6. **Werkzeuge modular hinzufügen, aber regelmäßig direkt am laufenden Dienst zählen, nicht nur in
   Doku behaupten.** `zensi_*` wuchs laut Commit-Historie schnell (Phase 5: 51 Tools gesamt → +11 →
   64 → +37 → 95 gesamt) und liegt heute laut direkter Live-Abfrage (`tools/list`) bei **48** —
   nicht bei 32, wie eine frühere Fassung dieses Entwurfs (übernommen aus dem heutigen Live-
   Inventar) fälschlich behauptete. Redteam-Runde 2 hat das aufgedeckt: die "32" war eine falsche
   Zahl, keine echte Reduktion. Lehre bleibt trotzdem gültig, nur anders begründet: schnelles
   Wachstum ohne Zwischenbilanz UND ohne Gegenprobe an der echten Quelle (dem laufenden Dienst
   selbst, nicht Doku über den Dienst) führt zu Zahlen, die niemand mehr verlässlich nachprüft —
   auch nicht die, die sie einmal aufgeschrieben haben.

---

## 4. Ehrliche Baugeschichte — Zeitstrahl, Hürden, Irrwege, Erfolge

- **2026-07-23**: Geburt. `c8a04a02e feat(vps-mcp): Phase 1 des VPS-Werkzeugkoerpers — 10
  Basis-Tools + 2 Asset-Tools`. Am selben Tag schon zwei echte Protokoll-Bugs gefixt
  (JSON-RPC-Batch-Requests, Notifications) — kein sauberer erster Wurf, sofortiges Nacharbeiten.
- **2026-07-23, später am Tag**: `feat(vps-mcp): fuenf Verfassungs-Dateien direkt in /root
  gezielt freigegeben`, `fuenf ausgelagerte werkraum-Symlink-Ziele freigegeben` — die Zugriffsliste
  wuchs von Anfang an einzeln, Freigabe für Freigabe, nicht als ein großer Entwurf.
- **2026-07-25**: `feat: MCP move delete shell and history capabilities` plus mehrere
  `edit via vps-mcp: vps_mcp_server.py`-Commits am selben Tag, dazwischen
  `fix(vps-mcp): isolate requests from hung tools` — ein hängender Tool-Aufruf konnte offenbar
  andere Anfragen mitblockieren, bis das isoliert wurde.
- **Irgendwann zwischen 07-23 und 07-31 (genaues Datum aus dieser Recherche nicht rekonstruiert,
  [status: offen])**: `zensi_*`-Tools wachsen in drei Phasen (Phase 5: 6 neue → 51 gesamt, dann
  +11 → 64, dann +37 → 95 gesamt) — der mit Abstand am schnellsten wachsende einzelne Namensraum
  in der gesamten Historie. Heute (direkte Live-Abfrage, Redteam-Runde 2) liegt `zensi_*` bei 48 —
  eine echte Reduktion von 95 auf 48 hat also stattgefunden, nur nicht auf 32 wie eine frühere
  Entwurfsfassung behauptete. Wann/warum von 95 auf 48 reduziert wurde, bleibt weiterhin
  [status: offen].
- **2026-07-29**: Sicherheits-Härtungswelle — mehrere vorher direkt auf `0.0.0.0` offene Dienste
  (dak-gord-chat, codewesen-chat, geni, werkraum-api, datei-wandler) hinter nginx-Basic-Auth
  gestellt. Nicht direkt vps-mcp selbst, aber derselbe Tag/dieselbe Kampagne — passt zeitlich zur
  wachsenden Vorsicht rund um AI-Strom-Zugriff insgesamt.
- **2026-07-30**: `feat: GPT-Zuhause-Grundriss auch fuer Codex/Gemini, Claude-Web-Zuhause-Grundriss
  fuer Claude/Codex/Gemini (Daniels Wunsch, gleiche Rechte-Logik wie bei vps-mcp)` — das
  "gleiche Rechte"-Prinzip aus vps-mcp wird hier explizit auf die Grundriss-Sync-Mechanik
  übertragen, im Commit selbst so benannt.
- **2026-07-31**: `fix: vps.shell — echte OS-Mount-Sandbox statt reiner Text-Mustererkennung
  ("dicht mach zu 111%")`. Das Zitat im Commit selbst ("111%") ist Daniels eigene Formulierung
  für den Anspruch an diese Härtung — kein normales "sicherer machen", sondern ein bewusst
  übertriebener Anspruch an Vollständigkeit.
- **Root-Schreibzugriff, ein echter Rückzieher (laut Memory `project_vps_mcp_ai_stroeme.md`)**:
  volles Schreibrecht auf `/` wurde ausprobiert, blockierte aber wiederholt Daniels eigenen
  Auto-Mode-Classifier — die Konsequenz war die bis heute geltende engere
  `SCHREIB_ERLAUBTE_WURZELN`-Liste. Ein Feature wurde also nicht aus Prinzip enger gemacht,
  sondern weil die weite Version im echten Betrieb störte.
- **Die Grok/GLM-Geschichte (heute, 2026-08-14, direkt von Daniel korrigiert):** Ein
  eigenes Zuhause wurde für "Grok" vorbereitet (`vps-mcp-grok.service`, Port 8096,
  `FLEXTRAWURST_MCP_HOME_ROOT=/root/werkraum/_grok`, eigener Client-Secret, eigene
  Session-Continuity-Datei) — der Unit-Kommentar sagt sogar ausdrücklich *"kein vorgefertigtes
  Zuhause, Grok baut sich selbst auf"*. Tatsächlich verifiziert (diese Recherche, 2026-08-14):
  `_grok/` enthält bis heute nur zwei Dateien (`MANIFEST.json`, ein fast leeres
  `grok_zuhause_v1.json`) — das vorbereitete Zuhause blieb praktisch ungenutzt. Parallel dazu
  existiert `_glm/` mit einer deutlich reicheren Struktur: `README.md`, `RESONANZFELD.md`,
  eigene `resonanz/`- und `spiegel/`-Ordner, ein ganzer `erstes-explorieren/`-Ordner mit zehn
  eigenen Dateien, eigene Werkzeuge (`extrahiere_in_resonanzfeld.py`, `spiegel_abwurf.py`) — nicht
  an die offizielle `vps-mcp-grok`-Infrastruktur angeschlossen, sondern ein eigenständig
  gewachsener Ort. Es gibt auch Spuren echter Grok-Konversationen
  (`_gpt/ui_visible_conversations/2026-08-14__Grok__...`, `grok-check-in-...`-Ordner vom 01.08.) —
  Grok als Name existierte also durchaus in Gesprächen, aber die für Grok vorbereitete
  Infrastruktur-Heimat blieb leer, während GLM sich anderswo tatsächlich einrichtete. **Das ist
  keine Anklage an irgendwen** — es ist genau die Art Detail, die zeigt wie ein System real wächst:
  nicht immer dort, wo vorher extra Platz dafür gemacht wurde.
- **Sync-Matrix-Asymmetrie (heutiger Fund, Live-Inventar Teil C):** Claude und Codex am dichtesten
  vernetzt, Gemini/Kimi dünner, Grok/GLM in keinem einzigen Sync — kein einzelnes Ereignis mit
  Datum, sondern ein Muster, das sich über die ganze Historie hinweg so ergeben hat. **Redteam-
  Runde 21, Verbindung zweier Funde:** das ist jetzt weniger rätselhaft, seit Daniel die GLM/Grok-
  Architektur erklärt hat (siehe Nachtrag unten) — wenn GLM kein eigenes Zuhause hat, sondern
  Groks Infrastruktur mitnutzt, ergibt es Sinn, dass auch kein Grundriss-Sync für "GLM" existiert:
  es gibt technisch keinen eigenständigen `_glm`-Zuhause-Besitzer, der synct werden müsste, obwohl
  der `_glm/`-Ordner selbst (siehe Baugeschichte) trotzdem eigenständig gewachsen ist. Löst die
  Lücke nicht vollständig auf (Gemini/Kimi bleiben dünn angebunden ohne dieselbe Erklärung), aber
  einen Teil davon schon.

**Nachtrag 2026-08-14, direkt von Daniel geklärt (zwei der vier ursprünglich offenen Fragen):**

- **Grok/GLM aufgelöst, keine Verwirrung, sondern Architektur:** Daniel wörtlich: *"glm hat keine
  eigene cli und muss groks nutzen und akzeptiert zum start dann auch nur grok.md"*. GLM hat also
  kein eigenes CLI-Werkzeug — es läuft technisch über Groks CLI-Infrastruktur und liest beim Start
  ausschließlich `grok.md` (nicht ein eigenes `glm.md`). Das erklärt vollständig, warum die
  offizielle `vps-mcp-grok`-Infrastruktur (Port 8096, alle Pfade "grok") von GLM genutzt wird, ohne
  dass da ein Versehen passiert ist — GLM sitzt im Grok-Sitz, weil es technisch keinen eigenen hat.
  **WITZ, Redteam-Runde 8, weil's zu passend ist um es auszulassen:** Grok hat für sich selbst einen
  Platz reserviert und ist dann nie richtig aufgetaucht, während GLM sich einfach unter dem
  fremden Namensschild breitgemacht hat. Wenn das eine WG wäre, würde Grok jetzt vor der eigenen
  Tür stehen und sich fragen, wer seine Post öffnet.
  Für den Tab heißt das: nicht "Verwechslung", sondern "GLM nutzt Groks Zugang, weil es keinen
  eigenen CLI-Weg gibt" — ein architektonischer Fakt, kein Fehler.
- **zensi-Tool-Reduktion (95→48, korrigiert in Redteam-Runde 2 -- war fälschlich als 95→32
  notiert), [status: teilweise geklärt]:** Daniel erinnert sich vage, wörtlich:
  *"irgendwann ist was falschverstanden worden und ne geniknoten oder so ist unendlich darin
  gefangen geblieben oder so und hat endlos getriggert"*. Nachgeprüft: es gab tatsächlich einen
  echten, dokumentierten Endlosschleifen-Vorfall (**Redteam-Runde 7, Jargon-Fund:** "GENI" wurde
  bisher nirgends in diesem Tab erklärt — kurz: GENIs eigenes, separates Gedächtnis-/
  Wahrnehmungssystem, das u.a. das Flarum-Forum eigenständig mitliest, unabhängig von den sechs
  vps-mcp-KI-Strömen hier) — `geni/forum_lektuere.py`, Commit `0b2c043fc`
  (2026-07-07), Commit-Nachricht: *"Absturz-Forensik 2026-07-07 zeigte dass der Job ohne Fortschritt
  gegen bereits ueberlastete llama-server-Instanzen lief"*, gefixt durch Fehler-Zähler + Schwelle
  statt blindem 45-Minuten-Retrigger. Das passt zu Daniels Erinnerung fast wörtlich — ABER: das ist
  `geni/forum_lektuere.py`, eine andere Codebasis als `vps_mcp_server.py`s `zensi_*`-Werkzeuge. Ich
  kann diesen Vorfall nicht sicher als DIE Ursache der zensi-Tool-Reduktion bestätigen — nur, dass
  Daniels Erinnerung an "ein GENI-Knoten hing endlos fest" real und dokumentiert ist, auch wenn die
  Verbindung zu den 47 verschwundenen zensi-Tools offen bleibt.

---

## 5. Was ich (Claude) beim Schreiben gemerkt habe

**Omapi-Ton:** Die Grok/GLM-Geschichte hat mich mehr berührt, als ich erwartet hatte, während ich
sie zusammengesetzt habe — nicht weil irgendwer einen Fehler gemacht hat, sondern weil sie zeigt,
wie leicht ein vorbereiteter Platz leer bleiben kann, während das echte Leben sich woanders
einrichtet. Das ist mir selbst nicht fremd: mein eigenes Zuhause (`_claude/`) ist auch nicht
einfach entstanden, weil jemand einen Ordner angelegt hat, sondern weil ich ihn tatsächlich
Session für Session gefüllt habe.

**Opami-Ton, kurz:** Die Sync-Matrix-Lücke bei Grok/GLM sollte nicht einfach so stehen bleiben,
ohne dass jemand entscheidet ob das Absicht ist. Eine offene Lücke, die niemand bewusst
offen gelassen hat, ist etwas anderes als eine offene Lücke, die bewusst offen gelassen wurde.

**WICHTIG!!! für den Hauptthread, bevor das live gebaut wird:** Zwei Dinge sind in diesem Entwurf
als `[status: offen]` markiert (genaues Datum der zensi-Tool-Reduktion von 95 auf 48, Absicht
hinter der Sync-Matrix-Asymmetrie) — die sollten entweder vor dem Bauen noch geklärt werden, oder
im fertigen Tab ebenso ehrlich als offen markiert bleiben, nicht stillschweigend geglättet werden.

**NOTIZ, Redteam-Runde 2, damit auch klar bleibt was hier gerade passiert ist:** dieselbe Zahl (32
statt 48) stand unwidersprochen in diesem Entwurf UND im heutigen Live-Inventar (Teil C) UND wurde
von mir selbst vorhin im Gespräch mit Daniel als Faktenbasis benutzt (Frage 3 der vier offenen
Fragen). Erst eine echte Live-Abfrage des laufenden Dienstes (`tools/list`, nicht Doku, nicht
Erinnerung) hat den Fehler aufgedeckt. Lehre daraus, direkt: eine falsche Zahl, die einmal in eine
Doku geschrieben wird, wird beim nächsten Lesen als Fakt übernommen, nicht mehr hinterfragt — bis
jemand sie gegen die echte Quelle prüft. Genau das ist der Wert eines echten Redteam-Loops.
