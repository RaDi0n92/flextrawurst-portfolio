# Mehrstrom-Briefkasten: jeder AI-Strom bekommt einen eigenen Ort

Fortsetzung des Megaplans (Stage "1a" in der Validator-Empfehlung von heute Vormittag) -
Daniels konkretester ursprünglicher Wunsch: jeder Strom (Claude, ChatGPT/Codex, Gemini,
GLM) soll einen eigenen Briefkasten haben, nicht nur den fest verdrahteten ChatGPT_Work.

## Was vorher da war

`INBOX = "ChatGPT_Work/00_Start"` war in `human_start.js` hart codiert. `workspace.js`s
"Start hier"-Knopf suchte ausschließlich `ChatGPT_Work/00_Start/README.md`. `Claude_Work`
existierte nur als Ad-hoc-Ordner auf der Platte, nirgends im Code verankert. Kein
"neu angekommen"-Indikator.

## Was jetzt gebaut ist

Eine kleine, in `workspace.js` und `human_start.js` bewusst duplizierte
`STREAMS`-Registry (kein Modul-System in dieser Codebase, jede Datei ist eine
eigenständige IIFE - Duplikation ist hier der bestehende Stil, siehe die API-Konstante,
die genauso mehrfach unabhängig steht):

```js
const STREAMS = [
  { id: "claude", label: "Claude Code", folder: "Claude_Work" },
  { id: "chatgpt", label: "ChatGPT / Codex", folder: "ChatGPT_Work" },
  { id: "gemini", label: "Gemini", folder: "Gemini_Work" },
  { id: "glm", label: "GLM", folder: "GLM_Work" },
];
```

**Identität pro Browser-Profil, nicht pro Server-Account:** jeder Strom läuft ohnehin in
einem eigenen virtuellen Desktop/Browser-Profil - `localStorage` reicht, kein neuer
Server-Mechanismus nötig. Ein `<select>` in der Topbar (`#planner-stream-select`, Stil
wie das bestehende `#pf-root`-Select) merkt "wer bin ich gerade".

**"Start hier"** ist jetzt strom-bewusst: öffnet `<Strom>_Work/00_Start/README.md`,
legt Ordner + Seed-README automatisch an falls der Strom zum ersten Mal dran ist
(gleiches `op:"create"`-Muster wie überall sonst im Code), merkt sich
"zuletzt gesehen" pro Strom lokal.

**"Neu angekommen"-Indikator:** roter Punkt (`.briefkasten-badge`) am "Start hier"-Knopf,
sichtbar wenn der neueste `modifiedAt`-Zeitstempel unter dem Strom-Ordner jünger ist als
das lokal gemerkte "zuletzt gesehen". Kein Server-Push nötig (SSE/Stage 3 ist noch nicht
gebaut) - ein einmaliger Check beim Laden plus ein 60-Sekunden-Intervall reicht für
"beim nächsten Hinschauen sichtbar", auch ohne echtes Live-Update.

**Schnellerfassung** (`human_start.js`, Daniels eigenes Schnell-Ablegen) hat jetzt
ebenfalls ein Ziel-Dropdown (`.hs-target`) - er wählt, für welchen Strom die Notiz
gedacht ist, statt dass alles blind nach ChatGPT_Work fällt. Textarea-Inhalt bleibt beim
Ziel-Wechsel erhalten (extra behandelt, da `render()` das ganze Panel-HTML neu baut).

## Eigener Bug gefunden und behoben, bevor er committet wurde

Erste Fassung von `refreshBriefkastenBadge()` holte per `request("GET")` frische
Baumdaten, warf das Ergebnis aber weg statt es der Modul-Variable `tree` zuzuweisen -
`streamHasUnseen()` prüfte dadurch immer gegen einen veralteten Stand. Beim Live-Test
(GLM-Badge blieb fälschlich versteckt trotz frisch abgelegter Datei) aufgefallen, sofort
korrigiert (`tree = result.tree` ergänzt), erneut getestet: GLM zeigt jetzt korrekt
"ungesehen", Claude (schon geöffnet) korrekt "gesehen".

## Live verifiziert, echte Klicks über CDP

1. Dropdown auf "Claude Code" → "Start hier" → `Claude_Work/00_Start/README.md` frisch
   angelegt und geöffnet, Badge danach versteckt.
2. Dropdown auf "Gemini" gewechselt → "Start hier" → `Gemini_Work/00_Start/README.md`
   frisch angelegt (Ordner existierte vorher nicht).
3. Schnellerfassung aufgeklappt, Ziel auf "GLM" gestellt, Text abgelegt →
   `GLM_Work/00_Start/Testauftrag fuer GLM ueber Schnellerfassung.md` entstanden (beide
   Ordnerebenen automatisch angelegt, existierten vorher gar nicht).
4. Nach Fix: GLM-Badge zeigt "ungesehen" (rot), Claude-Badge "gesehen" (versteckt) -
   korrekt unterschieden.

Testdatei aus Schritt 3 bewusst nicht gelöscht (kein Lösch-Op im System, wie schon bei
früheren Testkörpern in diesem Codebase üblich - bleibt als echter Beleg liegen).

## Was noch offen ist vom Megaplan

- Live-Updates (SSE) - der 60-Sekunden-Poll hier ist ein Behelf, kein Ersatz
- Echter VPS-Dateisystem-Schreibzugriff - braucht von Daniel benannte Pfade
- "Sichtbar LIVE" (Daniels expliziter Zusatzwunsch zum Briefkasten) hängt an SSE, nicht
  Teil dieses Schritts
