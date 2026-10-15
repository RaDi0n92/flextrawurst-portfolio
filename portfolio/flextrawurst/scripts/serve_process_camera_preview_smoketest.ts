import { createServer, IncomingMessage, ServerResponse } from "node:http";
import * as https from "node:https";
import * as http from "node:http";
import { readFileSync, existsSync, writeFileSync, appendFileSync, readdirSync, mkdirSync, rmSync, renameSync } from "node:fs";
import { resolve, normalize, join } from "node:path";
import { execFileSync, execFile, spawnSync } from "node:child_process";
import { PDFParse } from "pdf-parse";
import mammoth from "mammoth";
import { chromium } from "playwright";
import * as hauhauClient from "./hauhau_client.ts";

const WERKRAUM_PASSWORD = process.env.WERKRAUM_PASSWORD ?? "";
const activeInteractiveChatModel = "hauhaucs-q6";
// codexium2/solarius2: laufende Generierungen pro Charakter (spawner/name), damit ein expliziter
// Stop-Klick (POST .../chat/abort) sie wirklich toeten kann statt nur den Client-Fetch abzubrechen.
const aktiveGenerationen = new Map<string, { ollamaReq: http.ClientRequest; verworfen: boolean; hp: string; replyMsgId: string }>();
// Analog zu aktiveGenerationen, aber fuer die beiden Hintergrund-Jobs Abschluss-Geschichte und
// Memory-Extraktion (Daniels Wunsch 2026-07-08: beide muessen genauso stoppbar sein wie der Chat,
// und beide sollen waehrenddessen live Fortschritt zeigen statt nur "laeuft" ohne Regung).
const laufendeAbschlussJobs = new Map<string, http.ClientRequest>();
const laufendeMemoryJobs = new Map<string, http.ClientRequest>();
const laufendeVerdichtungJobs = new Map<string, http.ClientRequest>();
const INTERACTIVE_KEEP_ALIVE = "30m";
// 2026-07-05 testweise von 8192 auf 12345 erhoeht (Daniels Zahl) — real gemessen: Ollama-RES bei
// 8192 vs. 12345 praktisch identisch (~20,6GB vs. ~20,4GB), der KV-Cache ist bei diesem grossen,
// quantisierten Modell nur ein winziger Bruchteil des Gesamt-Fussabdrucks. Das eigentliche
// Engpass-Risiko auf der VPS ist Ressourcen-Konkurrenz mit anderen Prozessen (sd-cli etc.), nicht
// die Kontextfenster-Groesse selbst — siehe Nachtrag in provenienz_logging.md.
// 2026-07-07: --ctx-size 66666 mit --parallel 1 ergibt effektiv 66816 Tokens
// pro Slot. Erster Versuch zeigte volle
// Neuverarbeitung bei jeder Nachricht (Log: "forcing full prompt re-processing due to lack of
// cache data") — Ursache war NICHT die KV-Cache-Quantisierung (isoliert getestet, exoneriert),
// sondern der zu knappe Checkpoint-/Cache-Pool (Default --cache-ram 8192 MiB, --ctx-checkpoints
// 32) unter mehreren gleichzeitigen Charakteren. Fix: --cache-ram 16384 --ctx-checkpoints 64.
// Siehe docs/systemdoku/12_ollama_gemma4.md fuer die volle Herleitung.
const INTERACTIVE_NUM_CTX = 66816;
// Eigenes, kleines Vision-Modell fuer Bild-Anhaenge (siehe extrahiereAnhang) — dasselbe unzensierte
// "Hauhau"-Fine-Tuning wie das Hauptmodell, aber nur 4,5B statt 35B Parameter. Grund: das grosse
// Hauptmodell auf reiner CPU brauchte fuer ein einzelnes Bild >3 Minuten (nie zu Ende getestet),
// das kleine Modell beschreibt dasselbe Testbild korrekt in ~14 Sekunden. Die Beschreibung des
// kleinen Modells wird dem Hauptmodell dann als Text mitgegeben (Zwei-Schritt-Pipeline), statt dem
// grossen Modell die Rohbilddaten direkt zu geben.
const VISION_MODEL = "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b";
// Bis 2026-07-06: OLLAMA_MAX_LOADED_MODELS=1 verdraengte beim Bild-Beschreiben das Hauptmodell aus
// dem RAM (beide teilten sich einen Ollama-Slot), ein Zeitstempel (hauptmodellVoraussichtlichBlockiertBis)
// liess den Chat-Handler dann "warte kurz" antworten statt haengen zu bleiben. Seit der Umstellung
// des Hauptmodells auf llama-hauhaucs.service (eigener Prozess, Port 11435) gibt es diese
// Verdraengung nicht mehr — VISION_MODEL laeuft weiterhin dediziert auf Ollama (Port 11434), aber
// voellig unabhaengig vom Hauptmodell. Der Mechanismus wurde entfernt.
const DEFAULT_INTERACTIVE_NUM_PREDICT = -1;   // unlimitiert — Modell stoppt selbst
const MAX_INTERACTIVE_NUM_PREDICT = 8192;      // nur wenn User explizit Limit setzt

// ── Gemma4-Endpunkte — deaktiviert seit 2026-06-22 (Existenzurlaub) ──────────
//
// Was diese Endpunkte tun:
//   GET  /gemma2b        → dient gemma2b_chat.html (einfache Chat-UI)
//   POST /gemma2b/chat   → deaktiviert, kein Ollama-Call
//   GET  /gemma4b        → dient gemma4b_chat.html (einfache Chat-UI)
//   POST /gemma4b/chat   → deaktiviert, kein Ollama-Call
//
// Warum deaktiviert:
//   Diese Raw-Testendpunkte sind nicht die Codewesen/dak+gord/GENI-Gemma4-Pfade.
//   Hier darf kein Gemma/Dolphin-Ersatzmodell automatisch geladen werden.
//
// Reaktivieren:
//   Nur mit explizitem Daniel-Auftrag und neuem Modellpfad.
//
const GEMMA_ENDPOINTS_ACTIVE = false;
// ─────────────────────────────────────────────────────────────────────────────

function clampInteractiveNumPredict(value: unknown): number {
  const parsed = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) return DEFAULT_INTERACTIVE_NUM_PREDICT; // -1 = unlimitiert
  return Math.max(32, Math.min(Math.floor(parsed), MAX_INTERACTIVE_NUM_PREDICT));
}

// ── Session-Dateinamen-Helfer ──────────────────────────────────────────────────
const DOLPHIN_DIR = "/root/werkraum/dolphin_mischpult";
const DOLPHIN_SESSIONS = join(DOLPHIN_DIR, "sessions");

function sanitizeForFilename(s: string): string {
  return s.trim()
    .toLowerCase()
    .replace(/[äöü]/g, (c: string) => ({ä:'ae',ö:'oe',ü:'ue'}[c as 'ä'|'ö'|'ü'] || c))
    .replace(/ß/g, 'ss')
    .replace(/[^a-z0-9_\-]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 50)
    || 'session';
}

function readIdx(): Record<string, any> {
  const f = join(DOLPHIN_DIR, "sessions-index.json");
  return existsSync(f) ? JSON.parse(readFileSync(f, "utf-8")) : {};
}

function writeIdx(idx: Record<string, any>): void {
  writeFileSync(join(DOLPHIN_DIR, "sessions-index.json"), JSON.stringify(idx), "utf-8");
}

function resolveSessionFile(id: string, idx?: Record<string, any>): string {
  const theIdx = idx ?? readIdx();
  const filename = theIdx[id]?.filename || id;
  return join(DOLPHIN_SESSIONS, filename + ".jsonl");
}

function uniqueSessionFilename(base: string, excludeCurrentFilename?: string): string {
  let name = base;
  let i = 2;
  while (existsSync(join(DOLPHIN_SESSIONS, name + ".jsonl")) && name !== excludeCurrentFilename) {
    name = `${base}_${i++}`;
  }
  return name;
}

function requireAuth(req: IncomingMessage, res: ServerResponse): boolean {
  if (!WERKRAUM_PASSWORD) {
    // fail-closed: Ohne gesetztes Passwort werden geschuetzte Werkraum-Routen GESPERRT,
    // nicht geoeffnet. Verhindert oeffentliches Lesen/Ueberschreiben (C-002).
    res.writeHead(503, { "Content-Type": "text/plain" });
    res.end("Werkraum-Zugriff gesperrt: WERKRAUM_PASSWORD nicht gesetzt");
    return false;
  }
  const h = req.headers["authorization"] ?? "";
  if (h.startsWith("Basic ")) {
    const decoded = Buffer.from(h.slice(6), "base64").toString("utf-8");
    const colon = decoded.indexOf(":");
    if (colon !== -1 && decoded.slice(colon + 1) === WERKRAUM_PASSWORD) return true;
  }
  res.writeHead(401, { "WWW-Authenticate": 'Basic realm="Werkraum"', "Content-Type": "text/plain" });
  res.end("Unauthorized");
  return false;
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((ok, fail) => {
    const chunks: Buffer[] = [];
    req.on("data", c => chunks.push(c));
    req.on("end", () => ok(Buffer.concat(chunks).toString("utf-8")));
    req.on("error", fail);
  });
}

function prependLink(absPath: string, link: string): void {
  const existing = existsSync(absPath) ? readFileSync(absPath, "utf-8") : "";
  const line = `[[${link}]]\n`;
  if (existing.includes(line)) return; // bereits vorhanden
  writeFileSync(absPath, line + existing, "utf-8");
}

const WERKRAUM_ROOT = "/root/werkraum";

function serveWerkraumFile(relPath: string, res: import("node:http").ServerResponse): void {
  const safe = normalize(join(WERKRAUM_ROOT, relPath));
  if (!safe.startsWith(WERKRAUM_ROOT + "/")) {
    res.writeHead(403, { "Content-Type": "text/plain" }); res.end("Forbidden"); return;
  }
  if (!existsSync(safe)) {
    res.writeHead(404, { "Content-Type": "text/plain" }); res.end("Not found"); return;
  }
  try {
    const content = readFileSync(safe);
    res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8",
      "Access-Control-Allow-Origin": "*" });
    res.end(content);
  } catch {
    res.writeHead(500, { "Content-Type": "text/plain" }); res.end("Read error");
  }
}

const PORT = 18787;
const HOST = "0.0.0.0";

export const SERVE_ROOT = resolve("out/process_camera");
export const PUBLIC_ROOT = resolve("public");

// Extension-based allowlist — any .html or .json in SERVE_ROOT is serveable
export function getContentType(route: string): string | null {
  if (/^\/[\w._-]+\.html$/.test(route)) return "text/html; charset=utf-8";
  if (/^\/[\w._-]+\.json$/.test(route)) return "application/json; charset=utf-8";
  return null;
}

export function getPublicContentType(route: string): string | null {
  if (route.endsWith(".html")) return "text/html; charset=utf-8";
  if (route.endsWith(".js")) return "application/javascript; charset=utf-8";
  if (route.endsWith(".css")) return "text/css; charset=utf-8";
  if (route.endsWith(".json")) return "application/json; charset=utf-8";
  if (route.endsWith(".txt")) return "text/plain; charset=utf-8";
  if (route.endsWith(".xml")) return "application/xml; charset=utf-8";
  return null;
}

export function isSafePath(requestedPath: string, serveRoot: string = SERVE_ROOT): boolean {
  const normalized = normalize(join(serveRoot, requestedPath));
  return normalized.startsWith(serveRoot + "/") || normalized === serveRoot;
}

export function buildIndexHtml(): string {
  return `<!DOCTYPE html>
<html lang="de">
<head><meta charset="utf-8"><title>flextrawurst Preview</title>
<style>
body{font-family:monospace;background:#050810;color:#8899aa;padding:2rem;line-height:1.8}
h1{color:#4a7a9a;font-size:1.1rem;margin-bottom:1rem}
a{color:#3a6a8a}a:hover{color:#5a9abb}
ul{list-style:none;padding:0}li{margin-bottom:.4rem}
.note{color:#2a3a4a;font-size:.78rem;margin-top:1.5rem;font-style:italic}
</style>
</head>
<body>
<h1>flextrawurst — Browser Preview</h1>
<ul>
  <li><a href="/system_heute.html">&#9632; System Heute (was jetzt existiert)</a></li>
  <li><a href="/welt.html">&#9670; Die Welt (öffentliche Menschenseite)</a></li>
  <li><a href="/flextrawurst_surface.html">&#9654; Flextrawurst Oberfläche (Weltoberfläche — Ring 23)</a></li>
  <li><a href="/werkraum_explorer.html">dak+gord Werkraum Explorer (Graphansicht — alle echten Dateien)</a></li>
  <li><a href="/kompoase.html">&#9670; KompOase (Zwischenraum — Splitter-Physik)</a></li>
  <li><a href="/kompOase_datafield.html">KompOase Datafield (Living Datafield — Ring 22N)</a></li>
  <li><a href="/kompOase_vorform.html">KompOase-Vorform (Landschaftskarte — Ring 22M)</a></li>
  <li><a href="/process_camera_worldblick.html">Prozesskamera Weltblick (Netzwerk-Map)</a></li>
  <li><a href="/process_camera_model.json">Prozesskamera Modell (JSON)</a></li>
</ul>
<p class="note">Statische Artefakte. Kein Live-State. Kein Daemon. Read-only.</p>
</body>
</html>`;
}

const SOLARIUS_ROOT = "/root/werkraum/solarius";
const SOLARIUS2_ROOT = "/root/werkraum/solarius2";
const CODEXIUM_ROOT = "/root/werkraum/codexium";
const CODEXIUM2_ROOT = "/root/werkraum/codexium2";
const wesenRoot = (sp: string): string =>
  sp === "solarius" ? SOLARIUS_ROOT :
  sp === "solarius2" ? SOLARIUS2_ROOT :
  sp === "codexium2" ? CODEXIUM2_ROOT : CODEXIUM_ROOT;
const isTestbedSpawner = (sp: string): boolean => sp === "codexium2" || sp === "solarius2";
// Gemeinsam mit buildSystemPrompt() unten (dort als lokale Konstante) UND dem SSR-Rendering des
// Grenzen-Dropdowns (siehe wesenChatGet) — ein Pfad, damit beide garantiert dieselbe Datei lesen.
const WESEN_GRENZEN_PATH = "/root/werkraum/_wesen_grenzen.md";

// Codexium2/Solarius2 Memory/Container: Budget statt Max-pro-Kategorie, siehe
// _claude/ideen/codexium2_solarius2/memory_container.md — Werte vorlaeufig, werden beim Bauen nachgemessen.
const CONTAINER_BUDGET_ZEICHEN = 11111;
const MEMORY_BUDGET_ZEICHEN = 11111;
// PIN_KOMMENTAR_MAX (88 Zeichen) auf Daniels Wunsch entfernt (2026-07-05) — Pin-Kommentare sind
// jetzt nur noch durch das Gesamt-Container-Budget begrenzt, nicht mehr pro Eintrag.

interface ContainerEintrag {
  id: string;
  text: string;
  kommentar?: string;
  quelle: "mensch" | "wesen";
  hinzugefuegt_am: string;
}

// Mehrfach-Container-Sammlung (Daniel 2026-07-06): frei anlegbare, benennbare Behaelter statt einer
// festen Liste, gilt seither einheitlich fuer alle 4 Spawner. Siehe Nachtrag in
// _claude/ideen/codexium2_solarius2/memory_container.md fuer die Entscheidung + offene Fragen.
interface ContainerBox {
  id: string;
  name: string;
  aktiv: boolean; // ob der Inhalt gerade in den Chat-System-Prompt einfliesst
  erstellt_am: string;
  eintraege: ContainerEintrag[];
}
interface ContainerSammlung {
  container: ContainerBox[];
}

function containerZeichenSumme(eintraege: ContainerEintrag[]): number {
  return eintraege.reduce((sum, e) => sum + e.text.length + (e.kommentar?.length ?? 0), 0);
}
function containerSammlungZeichenSumme(sammlung: ContainerSammlung): number {
  return sammlung.container.reduce((sum, box) => sum + containerZeichenSumme(box.eintraege), 0);
}

// Liest container.json und migriert bei Bedarf das alte Format (eine feste eintraege-Liste — sowohl
// das Pin-Format text/kommentar/quelle der Testbed-Spawner als auch das aeltere Key/Val-Format von
// Codexium/Solarius) in die neue Mehrfach-Container-Struktur. Schreibt sofort zurueck, damit
// nachfolgende Lesevorgaenge nicht erneut migrieren.
function ladeContainerSammlung(dir: string): ContainerSammlung {
  const contPath = join(dir, "container.json");
  if (!existsSync(contPath)) return { container: [] };
  let raw: { container?: ContainerBox[]; eintraege?: Array<Partial<ContainerEintrag> & { key?: string; val?: string }> };
  try { raw = JSON.parse(readFileSync(contPath, "utf-8")); } catch { return { container: [] }; }
  if (Array.isArray(raw.container)) return raw as ContainerSammlung;
  const alteEintraege = raw.eintraege || [];
  if (!alteEintraege.length) {
    const leer: ContainerSammlung = { container: [] };
    writeFileSync(contPath, JSON.stringify(leer, null, 2), "utf-8");
    return leer;
  }
  const migrierteEintraege: ContainerEintrag[] = alteEintraege.map(e => {
    if (typeof e.text === "string") return e as ContainerEintrag; // schon Pin-Format
    return { // altes Key/Val-Format (Codexium/Solarius)
      id: crypto.randomUUID(),
      text: `${e.key ?? ""}: ${e.val ?? ""}`.trim(),
      quelle: "mensch",
      hinzugefuegt_am: new Date().toISOString(),
    };
  });
  const migriert: ContainerSammlung = {
    container: [{ id: crypto.randomUUID(), name: "Container", aktiv: true, erstellt_am: new Date().toISOString(), eintraege: migrierteEintraege }],
  };
  writeFileSync(contPath, JSON.stringify(migriert, null, 2), "utf-8");
  return migriert;
}
function speichereContainerSammlung(dir: string, sammlung: ContainerSammlung): void {
  writeFileSync(join(dir, "container.json"), JSON.stringify(sammlung, null, 2), "utf-8");
}
const sanName = (s: string): string => s.replace(/[^a-zA-Z0-9_-]/g, "");
// Case-insensitive Charakter-Aufloesung: URLs/Eingaben mit abweichender Gross-/Kleinschreibung
// (z.B. "/solarius/kreappy" statt dem tatsaechlichen Ordner "KrEaPPy") sollen trotzdem den
// richtigen Ordner finden — niemand tippt eine gemischte Gross-/Kleinschreibung aus dem Kopf exakt
// richtig. Existiert (noch) kein Ordner mit passendem Namen (z.B. beim Neuanlegen eines Charakters),
// wird der sanitierte Rohname unveraendert zurueckgegeben.
function resolveCharName(spawner: string, rawName: string): string {
  const saniert = sanName(rawName);
  if (!saniert) return saniert;
  const root = wesenRoot(spawner);
  if (!existsSync(root)) return saniert;
  try {
    const treffer = readdirSync(root).find(d => d.toLowerCase() === saniert.toLowerCase());
    return treffer || saniert;
  } catch { return saniert; }
}
const IMAGE_EXTS = ["png","jpg","jpeg","gif","webp","avif"];

// ── Datei-Anhaenge (alle vier Spawner) ───────────────────────────────────────
// Uploads werden dauerhaft im uploads/-Ordner des Charakters gespeichert (Provenienz-Prinzip —
// nichts geht verloren). Text-Formate werden serverseitig extrahiert und als Teil der Nachricht
// direkt in chat_history.jsonl inline gespeichert (dadurch bleiben sie ganz natuerlich auch in
// spaeteren Zuegen im Kontext, ohne dass jede historische Nachricht erneut nachgeschlagen werden
// muss). Bilder werden roh als base64 an Ollamas vision-faehiges "images"-Feld gehaengt — das
// Modell (hauhaucs-tuned, bestaetigte capability "vision") sieht sie dann wirklich, kein Vortaeuschen.
// Format wird an der Dateiendung erkannt.
const ANHANG_TEXT_EXT = ["txt", "md", "json", "css", "csv", "html", "htm"];
const ANHANG_BILD_EXT = ["png", "jpg", "jpeg", "gif", "webp"];
const ANHANG_AUDIO_EXT = ["mp3", "wav", "m4a", "ogg", "flac"];
const ANHANG_MAX_BYTES = 25 * 1024 * 1024; // 25 MB — grosszuegig, aber nicht grenzenlos

interface AnhangErgebnis {
  id: string;
  dateiname: string;
  dateiEndung: string;
  art: "text" | "bild" | "audio" | "unbekannt";
  vorschau: string;
  geschaetzeTokens: number;
  text?: string;
}
function anhaengeDir(dir: string): string { return join(dir, "uploads"); }
function anhangManifestPfad(uDir: string, id: string): string { return join(uDir, `${id}.json`); }
function ladeAnhangManifest(uDir: string, id: string): AnhangErgebnis | null {
  const p = anhangManifestPfad(uDir, id);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, "utf-8")); } catch { return null; }
}
// ODT ist ein ZIP-Archiv mit dem eigentlichen Text in content.xml — braucht keine LibreOffice-
// Installation (nicht auf dem VPS vorhanden), nur das ohnehin vorhandene unzip-Kommando plus
// simples Tag-Strippen.
function extrahiereOdtText(pfad: string): string {
  const xml = execFileSync("unzip", ["-p", pfad, "content.xml"], { encoding: "utf-8" });
  return xml
    .replace(/<\/(text:p|text:h)[^>]*>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}
// Zwei-Schritt-Vision: das kleine VISION_MODEL beschreibt das Bild, die Beschreibung (Text) wird
// dem Hauptmodell mitgegeben — siehe VISION_MODEL-Kommentar oben fuer den Grund (Geschwindigkeit).
// Vision-Verarbeitungszeit skaliert mit der Bildaufloesung — ein normales Handyfoto (oft
// 3000x4000+) hat um Groessenordnungen mehr zu verarbeitende Bildausschnitte als ein kleines
// Testbild. Vor dem Verschicken an das Vision-Modell auf maximal 768px lange Kante verkleinern
// (Seitenverhaeltnis bleibt erhalten, kleinere Bilder werden nicht hochskaliert) — kostet selbst
// nur Bruchteile einer Sekunde, spart aber die meiste Zeit bei echten Fotos. Faellt bei einem
// Fehler (z.B. beschaedigte Datei) auf das Original zurueck, statt den ganzen Upload scheitern zu
// lassen.
function verkleinereBildFuerVision(pfad: string): Buffer {
  const ausgabe = `${pfad}.vision-resize.jpg`;
  try {
    execFileSync("ffmpeg", [
      "-y", "-i", pfad,
      "-vf", "scale='min(768,iw)':'min(768,ih)':force_original_aspect_ratio=decrease",
      "-update", "1", "-frames:v", "1",
      ausgabe,
    ], { stdio: ["ignore", "ignore", "ignore"] });
    const verkleinert = readFileSync(ausgabe);
    rmSync(ausgabe, { force: true });
    return verkleinert;
  } catch {
    try { rmSync(ausgabe, { force: true }); } catch {}
    return readFileSync(pfad);
  }
}
function beschreibeBildMitVisionModell(bildBase64: string, signal?: AbortSignal): Promise<string> {
  const body = JSON.stringify({
    model: VISION_MODEL,
    messages: [{ role: "user", content: "Beschreibe dieses Bild ausführlich: was ist zu sehen, welche Farben, Formen, Stimmung, Details.", images: [bildBase64] }],
    // Kurzes keep_alive (statt der sonst ueblichen 30m): Hauptmodell (~20GB) + Vision-Modell
    // (~5,7GB) gleichzeitig geladen bringt den 32GB-RAM-VPS an seine Grenze (unter 500MB frei,
    // Swap aktiv, siehe Session 2026-07-05) — das Vision-Modell soll den Speicher so schnell wie
    // moeglich wieder freigeben, statt lange warmzuhalten.
    stream: false, think: false, keep_alive: "20s",
    options: { num_predict: -1 },
  });
  return new Promise((resolveP, rejectP) => {
    // signal: bricht die Ollama-Anfrage wirklich ab, wenn der Mensch die Seite/den Upload verlaesst
    // (z.B. nginx-Timeout) — ohne das lief die Verarbeitung frueher unbemerkt im Hintergrund weiter
    // und blockierte den einzigen Ollama-Modell-Slot fuer alle anderen (siehe Session 2026-07-05).
    const oreq = http.request(
      { hostname: "localhost", port: 11434, path: "/api/chat", method: "POST",
        headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) }, signal },
      (ores) => {
        let buf = "";
        ores.on("data", (c) => buf += c.toString());
        ores.on("end", () => {
          try {
            const parsed = JSON.parse(buf);
            // Bug gefunden 2026-07-08 (QA-Test mit einem 1x1px-Bild): Ollamas Vision-Modell kann bei
            // ungewoehnlichen Bildmassen abstuerzen ("panic: height:1 or width:1 must be larger than
            // factor:32") und antwortet dann mit HTTP 500 + {"error": "..."} statt einer message.
            // Vorher wurde das lautlos als leere Beschreibung durchgewunken (message?.content war
            // einfach undefined -> ""), das Wesen bekam dann ein Bild "ohne Inhalt" statt dass der
            // Anhang-Chip einen echten Fehler zeigt. Jetzt: HTTP-Fehlerstatus ODER ein error-Feld in
            // der Antwort gelten explizit als Fehlschlag.
            if ((ores.statusCode ?? 200) >= 400 || parsed?.error) {
              rejectP(new Error(parsed?.error || `Vision-Modell: HTTP ${ores.statusCode}`));
              return;
            }
            resolveP((parsed?.message?.content || "").trim());
          } catch (e) { rejectP(e); }
        });
      }
    );
    oreq.on("error", rejectP);
    oreq.write(body);
    oreq.end();
  });
}
// ── Audio-"Gehörersatz" (alle vier Spawner): Whisper-Transkript + technische Basis-Metadaten ──
// Whisper (faster-whisper, eigenes Python-venv) laeuft ausserhalb von Ollama — kein Konflikt mit
// dem Hauptmodell, kein Verdraengen aus dem RAM (anders als beim Vision-Modell). Tempo-/Tonart-
// Erkennung (aubio) wurde getestet, aber die Genauigkeit war bei einem einfachen Sinuston bereits
// deutlich daneben (775Hz statt echter 440Hz) — bewusst NICHT ausgeliefert, um nichts Falsches als
// vermeintlich analysierte Musikinformation auszugeben. Nur Dauer + Lautstaerke (ffmpeg) sind
// verlaesslich genug fuer die "maximale Gehoerersatz"-Version.
const WHISPER_PYTHON = resolve(".venv-whisper/bin/python3");
const WHISPER_SCRIPT = resolve("scripts/transkribiere_audio.py");
function transkribiereMitWhisper(pfad: string, signal?: AbortSignal): Promise<{ text: string; sprache: string }> {
  return new Promise((resolveP, rejectP) => {
    execFile(WHISPER_PYTHON, [WHISPER_SCRIPT, pfad], { maxBuffer: 10 * 1024 * 1024, timeout: 120_000, signal }, (err, stdout) => {
      if (err) { rejectP(err); return; }
      try { resolveP(JSON.parse(stdout)); } catch (e) { rejectP(e); }
    });
  });
}
function audioMetadaten(pfad: string): { dauerS: number | null; lautstaerkeDb: number | null } {
  let dauerS: number | null = null;
  let lautstaerkeDb: number | null = null;
  try {
    const dauerRaw = execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", pfad], { encoding: "utf-8" }).trim();
    dauerS = Math.round(parseFloat(dauerRaw));
  } catch {}
  try {
    // ffmpeg schreibt die volumedetect-Werte auf stderr, nicht stdout, unabhaengig vom Exit-Code —
    // spawnSync liefert beide getrennt zurueck, execFileSync haette stderr im Erfolgsfall verworfen.
    const result = spawnSync("ffmpeg", ["-i", pfad, "-af", "volumedetect", "-f", "null", "-"], { encoding: "utf-8" });
    const combined = (result.stdout || "") + (result.stderr || "");
    const m = combined.match(/mean_volume:\s*(-?\d+(\.\d+)?)\s*dB/);
    if (m) lautstaerkeDb = parseFloat(m[1]);
  } catch {}
  return { dauerS, lautstaerkeDb };
}
async function erstelleGehoerersatzText(pfad: string, signal?: AbortSignal): Promise<string> {
  const { dauerS, lautstaerkeDb } = audioMetadaten(pfad);
  const metaZeile = `Dauer: ${dauerS !== null ? dauerS + "s" : "unbekannt"}, Lautstärke (Durchschnitt): ${lautstaerkeDb !== null ? lautstaerkeDb + " dB" : "unbekannt"}`;
  try {
    const { text, sprache } = await transkribiereMitWhisper(pfad, signal);
    if (!text) return `${metaZeile}\nKein erkennbarer Sprachinhalt (evtl. reine Instrumentalmusik oder zu leise).`;
    return `${metaZeile}\nTranskript (${sprache}): ${text}`;
  } catch {
    return `${metaZeile}\nTranskription fehlgeschlagen.`;
  }
}
async function extrahiereAnhang(id: string, pfad: string, dateiname: string, buffer: Buffer, signal?: AbortSignal): Promise<AnhangErgebnis> {
  const endung = (dateiname.split(".").pop() || "").toLowerCase();
  const basis = { id, dateiname, dateiEndung: endung };
  if (ANHANG_TEXT_EXT.includes(endung)) {
    const text = buffer.toString("utf-8");
    return { ...basis, art: "text", text, vorschau: text.slice(0, 300), geschaetzeTokens: Math.round(text.length / 4) };
  }
  if (endung === "pdf") {
    const parser = new PDFParse({ data: buffer });
    const result = await parser.getText();
    const text = (result.text || "").trim();
    return { ...basis, art: "text", text, vorschau: text.slice(0, 300), geschaetzeTokens: Math.round(text.length / 4) };
  }
  if (endung === "docx") {
    const result = await mammoth.extractRawText({ buffer });
    const text = (result.value || "").trim();
    return { ...basis, art: "text", text, vorschau: text.slice(0, 300), geschaetzeTokens: Math.round(text.length / 4) };
  }
  if (endung === "odt") {
    const text = extrahiereOdtText(pfad);
    return { ...basis, art: "text", text, vorschau: text.slice(0, 300), geschaetzeTokens: Math.round(text.length / 4) };
  }
  if (ANHANG_BILD_EXT.includes(endung)) {
    const verkleinert = verkleinereBildFuerVision(pfad);
    const beschreibung = await beschreibeBildMitVisionModell(verkleinert.toString("base64"), signal);
    return { ...basis, art: "bild", text: beschreibung, vorschau: beschreibung.slice(0, 300), geschaetzeTokens: Math.round(beschreibung.length / 4) };
  }
  if (ANHANG_AUDIO_EXT.includes(endung)) {
    const text = await erstelleGehoerersatzText(pfad, signal);
    return { ...basis, art: "audio", text, vorschau: text.slice(0, 300), geschaetzeTokens: Math.round(text.length / 4) };
  }
  return { ...basis, art: "unbekannt", vorschau: `Nicht unterstütztes Format: .${endung}`, geschaetzeTokens: 0 };
}

// ── Explizites URL-Lesen (alle vier Spawner) ─────────────────────────────────
// Nur EINE, vom Menschen selbst angegebene URL wird geladen — kein automatisches Folgen von Links
// darauf, kein Crawlen. Playwright statt einem einfachen fetch(), damit auch JS-gerenderte Seiten
// funktionieren (dieselbe Begruendung wie bei den eigenen Test-Skripten diese Nacht).
const ANHANG_URL_MAX_ZEICHEN = 20000; // Sicherheitsdeckel gegen riesige Seiten, kein "kreatives" Limit
function istSichereUrl(rohUrl: string): boolean {
  let u: URL;
  try { u = new URL(rohUrl); } catch { return false; }
  if (u.protocol !== "http:" && u.protocol !== "https:") return false;
  const host = u.hostname.toLowerCase();
  if (["localhost", "127.0.0.1", "0.0.0.0", "::1"].includes(host)) return false;
  if (/^10\./.test(host) || /^192\.168\./.test(host) || /^172\.(1[6-9]|2\d|3[01])\./.test(host)) return false;
  if (host.endsWith(".local")) return false;
  return true;
}
async function leseUrlMitPlaywright(zielUrl: string, signal?: AbortSignal): Promise<{ titel: string; text: string }> {
  const browser = await chromium.launch();
  // Kein direktes AbortSignal-Feature in Playwright — bei Abbruch wird der Browser einfach
  // vorzeitig geschlossen, das laesst die laufenden page.*-Aufrufe mit einem Fehler abbrechen.
  const abortHandler = () => { browser.close().catch(() => {}); };
  signal?.addEventListener("abort", abortHandler);
  try {
    if (signal?.aborted) throw new Error("abgebrochen");
    const page = await browser.newPage();
    await page.goto(zielUrl, { waitUntil: "domcontentloaded", timeout: 20000 });
    await page.waitForTimeout(1500); // etwas Zeit fuer nachladendes JS, wie bei den eigenen Tests
    const titel = await page.title();
    const text = await page.evaluate(() => (document.body ? (document.body as HTMLElement).innerText : ""));
    return { titel, text: text.trim() };
  } finally {
    signal?.removeEventListener("abort", abortHandler);
    await browser.close().catch(() => {});
  }
}

// ── Feedback (nur codexium2/solarius2): pro Nachricht Daumen hoch/runter + Freitext-Kommentar.
// Liegt als feedback.json (Wahrheit, fuer die UI) UND als einzelne lesbare .md-Datei pro Nachricht
// in einem eigenen Ordner im Charakter-Verzeichnis — Daniels Wunsch: nicht nur JSON, auch direkt lesbar.
interface FeedbackEintrag {
  id: string;            // = Nachrichten-id (msgId/replyMsgId aus dem Chat)
  rolle: "mensch" | "wesen";
  nachricht: string;
  rating: "up" | "down" | null;
  kommentar: string | null;
  erstellt_am: string;
  aktualisiert_am: string;
  anModellGeliefert?: boolean;
}
function feedbackJsonPath(dir: string): string { return join(dir, "feedback.json"); }
function feedbackMdPath(dir: string, id: string): string { return join(dir, "feedback", `${sanName(id)}.md`); }
function loadFeedback(dir: string): FeedbackEintrag[] {
  const p = feedbackJsonPath(dir);
  if (!existsSync(p)) return [];
  try { const d = JSON.parse(readFileSync(p, "utf-8")); return Array.isArray(d.eintraege) ? d.eintraege : []; }
  catch { return []; }
}
function feedbackMdInhalt(e: FeedbackEintrag): string {
  const bewertung = e.rating === "up" ? "👍 Daumen hoch" : e.rating === "down" ? "👎 Daumen runter" : "(keine Bewertung)";
  return `# Feedback — ${e.rolle === "wesen" ? "Wesen-Nachricht" : "Menschen-Nachricht"}\n\n`
    + `Erstellt: ${e.erstellt_am}\nAktualisiert: ${e.aktualisiert_am}\n\n`
    + `**Nachricht:**\n${e.nachricht}\n\n`
    + `**Bewertung:** ${bewertung}\n\n`
    + `**Kommentar:**\n${e.kommentar || "(kein Kommentar)"}\n`;
}
function upsertFeedback(dir: string, msgId: string, rolle: "mensch"|"wesen", nachricht: string, rating: "up"|"down"|null|undefined, kommentar: string|null|undefined): FeedbackEintrag {
  mkdirSync(dir, { recursive: true });
  const liste = loadFeedback(dir);
  const jetzt = new Date().toISOString();
  let eintrag = liste.find(e => e.id === msgId);
  if (!eintrag) {
    eintrag = { id: msgId, rolle, nachricht, rating: rating ?? null, kommentar: kommentar ?? null, erstellt_am: jetzt, aktualisiert_am: jetzt };
    liste.push(eintrag);
  } else {
    if (rating !== undefined) eintrag.rating = rating;
    if (kommentar !== undefined) eintrag.kommentar = kommentar;
    eintrag.aktualisiert_am = jetzt;
    // Wurde ein schon gelieferter Eintrag jetzt geaendert (neue Bewertung/neuer Kommentar), soll die
    // neue Fassung erneut beim Modell ankommen statt fuer immer als "schon gesehen" zu gelten.
    eintrag.anModellGeliefert = false;
  }
  writeFileSync(feedbackJsonPath(dir), JSON.stringify({ eintraege: liste }, null, 2), "utf-8");
  const mdDir = join(dir, "feedback");
  mkdirSync(mdDir, { recursive: true });
  writeFileSync(feedbackMdPath(dir, msgId), feedbackMdInhalt(eintrag), "utf-8");
  return eintrag;
}
// Gleiches Muster wie ladeUngelieferteAllgFeedbacks/markiereAllgFeedbackAlsGeliefert weiter unten,
// nur fuer das PRO-NACHRICHT-Feedback (Daumen+Kommentar) statt das allgemeine — Daniels Klarstellung
// 2026-07-05: das sind zwei getrennte Kanaele, beide sollen das Modell erreichen, aber nicht
// zusammengelegt werden.
function ladeUngelieferteFeedbacks(dir: string): FeedbackEintrag[] {
  return loadFeedback(dir).filter(e => !e.anModellGeliefert && (e.rating || e.kommentar));
}
function markiereFeedbackAlsGeliefert(dir: string, ids: string[]): void {
  if (!ids.length) return;
  const liste = loadFeedback(dir);
  for (const e of liste) if (ids.includes(e.id)) e.anModellGeliefert = true;
  writeFileSync(feedbackJsonPath(dir), JSON.stringify({ eintraege: liste }, null, 2), "utf-8");
}

// ── Allgemeines Feedback (nicht an eine einzelne Nachricht gebunden) — fuer ALLE vier Spawner,
// im Unterschied zum Nachrichten-Feedback oben (das nur codexium2/solarius2 kennt). Jede Abgabe ist
// ein NEUER Eintrag (kein Upsert wie oben) — ein Mensch soll jederzeit erneut etwas dalassen koennen,
// ohne einen vorherigen Kommentar zu ueberschreiben. Eigene MD-Datei pro Eintrag, gleiches Muster
// wie feedbackMdPath oben.
interface AllgemeinesFeedbackEintrag {
  id: string;
  text: string;
  erstellt_am: string;
  anModellGeliefert?: boolean;
}
function allgemeinesFeedbackJsonPath(dir: string): string { return join(dir, "feedback_allgemein.json"); }
function allgemeinesFeedbackMdPath(dir: string, id: string): string { return join(dir, "feedback", `allgemein-${sanName(id)}.md`); }
function ladeAllgemeinesFeedback(dir: string): AllgemeinesFeedbackEintrag[] {
  const p = allgemeinesFeedbackJsonPath(dir);
  if (!existsSync(p)) return [];
  try { const d = JSON.parse(readFileSync(p, "utf-8")); return Array.isArray(d.eintraege) ? d.eintraege : []; }
  catch { return []; }
}
function fuegeAllgemeinesFeedbackHinzu(dir: string, text: string): AllgemeinesFeedbackEintrag {
  mkdirSync(dir, { recursive: true });
  const liste = ladeAllgemeinesFeedback(dir);
  const eintrag: AllgemeinesFeedbackEintrag = { id: crypto.randomUUID(), text, erstellt_am: new Date().toISOString() };
  liste.push(eintrag);
  writeFileSync(allgemeinesFeedbackJsonPath(dir), JSON.stringify({ eintraege: liste }, null, 2), "utf-8");
  const mdDir = join(dir, "feedback");
  mkdirSync(mdDir, { recursive: true });
  writeFileSync(allgemeinesFeedbackMdPath(dir, eintrag.id), `# Allgemeines Feedback\n\nErstellt: ${eintrag.erstellt_am}\n\n${text}\n`, "utf-8");
  return eintrag;
}
// Besser als Mischpults "Feedback ans Modell" (siehe dort — einmaliger Text, verschwindet nach dem
// naechsten Output, nirgends dauerhaft sichtbar): dieselbe Wirkung (Text erreicht das Modell einmalig
// als Extra-Kontext fuer die naechste Antwort, wird NIE zur Chat-Nachricht, kontaminiert also nicht
// den eigentlichen Verlauf), aber die schon bestehende, dauerhaft sichtbare Feedback-Liste (siehe
// oben) ist die Quelle — kein separates Feld noetig. Jeder Eintrag der noch nicht geliefert wurde,
// fliesst beim naechsten /chat-Aufruf mit in den Systemprompt (buildSystemPrompt liest nur, liefert
// nichts aus — das Markieren als geliefert passiert bewusst im /chat-Handler, damit ein reiner
// Seitenaufruf/SSR-Vorschau nichts "verbraucht").
function ladeUngelieferteAllgFeedbacks(dir: string): AllgemeinesFeedbackEintrag[] {
  return ladeAllgemeinesFeedback(dir).filter(e => !e.anModellGeliefert);
}
function markiereAllgFeedbackAlsGeliefert(dir: string, ids: string[]): void {
  if (!ids.length) return;
  const liste = ladeAllgemeinesFeedback(dir);
  for (const e of liste) if (ids.includes(e.id)) e.anModellGeliefert = true;
  writeFileSync(allgemeinesFeedbackJsonPath(dir), JSON.stringify({ eintraege: liste }, null, 2), "utf-8");
}

function chatHistoryPath(spawner: string, name: string): string {
  return join(wesenRoot(spawner), name, "chat_history.jsonl");
}
// Aliase (alle vier Spawner, Absprache mit Daniel 2026-07-05): Rollen/Personas des MENSCHEN, nicht
// des Wesens — z.B. "Mensch" oder "Gnom", je mit kurzer Selbstbeschreibung (max. 333 Zeichen). Liegen
// pro Wesen (nicht global), weil die Rollen die man mit einem bestimmten Charakter spielt zur
// jeweiligen Geschichte gehoeren. Der erste Eintrag ist immer da und kann nicht geloescht werden
// (Pflicht-Alias) — bestehende Charaktere ohne aliase.json bekommen ihn hier als Default, damit
// nichts kaputtgeht und das Dropdown im Chat nie leer ist.
const ALIAS_TEXT_MAX = 333;
interface AliasEintrag { id: string; name: string; text: string }
function aliasePath(dir: string): string {
  return join(dir, "aliase.json");
}
function ladeAliase(dir: string): AliasEintrag[] {
  const p = aliasePath(dir);
  if (existsSync(p)) {
    try {
      const d = JSON.parse(readFileSync(p, "utf-8"));
      if (Array.isArray(d.eintraege) && d.eintraege.length) return d.eintraege;
    } catch {}
  }
  return [{ id: "default", name: "Ich selbst", text: "" }];
}
function speichereAliase(dir: string, eintraege: Array<{ id?: string; name?: string; text?: string }>): AliasEintrag[] {
  const bereinigt: AliasEintrag[] = eintraege
    .map(e => ({ id: e.id || crypto.randomUUID(), name: (e.name || "").trim().slice(0, 40), text: (e.text || "").trim().slice(0, ALIAS_TEXT_MAX) }))
    .filter(e => e.name);
  const final = bereinigt.length ? bereinigt : [{ id: "default", name: "Ich selbst", text: "" }];
  mkdirSync(dir, { recursive: true });
  writeFileSync(aliasePath(dir), JSON.stringify({ eintraege: final }, null, 2), "utf-8");
  return final;
}
function loadHistory(hp: string): Array<{role: string; content: string; ts: string; id?: string}> {
  if (!existsSync(hp)) return [];
  return readFileSync(hp, "utf-8").trim().split("\n").filter(Boolean).flatMap(l => {
    try {
      const d = JSON.parse(l);
      if (typeof d.role !== "string" || typeof d.content !== "string") return []; // Session-Marker o.ae. ueberspringen
      return [d as {role:string;content:string;ts:string;id?:string}];
    } catch { return []; }
  });
}
// Codexium2/Solarius2: nur die Nachrichten seit dem letzten session_start-Marker (jede neue
// Session ist ein eigener Kontext fuer das Modell — Memory traegt das Dauerhafte weiter, nicht die
// rohe History). Codexium/Solarius kennen keine Marker und nutzen weiterhin die volle loadHistory().
function loadCurrentSessionHistory(hp: string): Array<{role: string; content: string; ts: string; id?: string}> {
  if (!existsSync(hp)) return [];
  const zeilen = readFileSync(hp, "utf-8").trim().split("\n").filter(Boolean);
  let startIdx = 0;
  for (let i = zeilen.length - 1; i >= 0; i--) {
    try { if (JSON.parse(zeilen[i]).type === "session_start") { startIdx = i + 1; break; } } catch {}
  }
  return zeilen.slice(startIdx).flatMap(l => {
    try {
      const d = JSON.parse(l);
      if (typeof d.role !== "string" || typeof d.content !== "string") return [];
      return [d as {role:string;content:string;ts:string;id?:string}];
    } catch { return []; }
  });
}
// Kombinierter Verlauf: Nachrichten UND Provenienz-Ereignisse in derselben chronologischen
// Reihenfolge, wie sie in chat_history.jsonl stehen — Daniels Wunsch, dass sowohl Menschen in der
// UI als auch Maschinen (die die Seite ohne JS abrufen) IMMER den vollen Verlauf inkl. aller
// Aenderungen sehen, nicht nur die reinen Chat-Nachrichten. Ergaenzt das bestehende "history"-Feld
// (das nur Nachrichten liefert und von anderen Stellen genutzt wird), ersetzt es nicht.
interface VerlaufEintragKombi {
  art: "nachricht" | "ereignis";
  ts: string;
  role?: string; content?: string; id?: string; aliasName?: string;
  type?: string; daten?: Record<string, unknown>;
}
// dir optional: nur wenn mitgegeben, werden User-Nachrichten mit ihrem damals aktiven Alias-Namen
// annotiert (siehe Daniels Wunsch 2026-07-05 — sichtbar wer gerade "spricht", nicht nur im
// Systemprompt, auch am Avatar der Nachricht selbst).
function ladeVerlaufKombiniert(hp: string, nurAktuelleSession: boolean, dir?: string): VerlaufEintragKombi[] {
  if (!existsSync(hp)) return [];
  const aliasNameNachId = dir ? new Map(ladeAliase(dir).map(a => [a.id, a.name])) : new Map<string, string>();
  const zeilen = readFileSync(hp, "utf-8").trim().split("\n").filter(Boolean);
  let startIdx = 0;
  if (nurAktuelleSession) {
    for (let i = zeilen.length - 1; i >= 0; i--) {
      try { if (JSON.parse(zeilen[i]).type === "session_start") { startIdx = i + 1; break; } } catch {}
    }
  }
  const ergebnis: VerlaufEintragKombi[] = [];
  for (const l of zeilen.slice(startIdx)) {
    let d: any;
    try { d = JSON.parse(l); } catch { continue; }
    if (typeof d.role === "string" && typeof d.content === "string") {
      const aliasName = d.role === "user" && typeof d.aliasId === "string" ? aliasNameNachId.get(d.aliasId) : undefined;
      ergebnis.push({ art: "nachricht", ts: d.ts, role: d.role, content: d.content, id: d.id, ...(aliasName ? { aliasName } : {}) });
    } else if (typeof d.type === "string") {
      const { type, ts, ...daten } = d;
      ergebnis.push({ art: "ereignis", ts, type, daten });
    }
  }
  return ergebnis;
}
function escHtml(s: string): string {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
const EREIGNIS_LABEL: Record<string, string> = {
  session_start: "Neue Session gestartet",
  feedback: "Feedback zur Nachricht",
  feedback_allgemein: "Allgemeines Feedback",
  pin_hinzugefuegt: "Satz gepinnt",
  pin_entfernt: "Pin entfernt",
  container_angelegt: "Container angelegt",
  container_umbenannt: "Container umbenannt",
  container_geloescht: "Container gelöscht",
  verdichtung_uebernommen: "Gesprächsabschnitt verdichtet",
  memory_geaendert: "Memory geändert",
  memory_extraktion: "Erinnerungen automatisch gezogen",
  thema_wiederholt_erkannt: "Wiederkehrendes Thema erkannt",
  profil_feld_geaendert: "Profilfeld geändert",
  profil_feld_geloescht: "Profilfeld gelöscht",
  generierung_abgebrochen: "Antwort abgebrochen",
  kontext_toggle: "Kontext-Ausschluss geändert",
  abschluss_uebernommen: "Abschluss-Geschichte übernommen",
  kontext_automatisch_gefunden: "Automatisch alte Stellen gefunden",
  merken_vorschlag: "Vorschlag: etwas merken",
  merken_angenommen: "Vorschlag angenommen",
  merken_abgelehnt: "Vorschlag abgelehnt",
  grenzen_toggle: "Grenzen umgeschaltet",
  alias_geaendert: "Aliase geändert",
  alias_gewechselt: "Rolle gewechselt",
  feedback_an_modell_geliefert: "Feedback ans Wesen weitergegeben",
  nachrichten_feedback_an_modell_geliefert: "Nachrichten-Feedback ans Wesen weitergegeben",
  impuls: "Impuls von Daniel",
  marker_ergebnis: "Ergebnis einer Handlung im Selbstgespräch",
};
// Vollstaendige, lesbare Details pro Ereignis-Typ — Daniels Wunsch: nicht nur "Memory geaendert"
// als Label, sondern wirklich sehen was genau geaendert wurde. Nutzt die ohnehin schon in jedem
// Provenienz-Event mitgeloggten Rohdaten (siehe appendProvenienz-Aufrufe im ganzen File) — keine
// neuen Daten noetig, nur die Anzeige war bisher zu knapp. Keine Kuerzung von vorher/nachher-Texten:
// "vollstaendige Angabe" heisst hier wirklich vollstaendig, auch wenn ein Profilfeld lang ist.
function formatiereEreignisDetails(typ: string, daten: Record<string, unknown>): string {
  switch (typ) {
    case "feedback": {
      const teile: string[] = [];
      if (daten.rating === "up") teile.push("Bewertung: 👍");
      else if (daten.rating === "down") teile.push("Bewertung: 👎");
      if (daten.kommentar) teile.push(`Kommentar: "${daten.kommentar}"`);
      return teile.join(", ");
    }
    case "feedback_allgemein":
      return `"${daten.text}"`;
    case "pin_hinzugefuegt": {
      const e = daten.eintrag as { text?: string; kommentar?: string } | undefined;
      const ziel = daten.containerName ? ` (in Container "${daten.containerName}")` : "";
      return e ? `"${e.text}"${e.kommentar ? ` — Begründung: "${e.kommentar}"` : ""}${ziel}` : "";
    }
    case "pin_entfernt": {
      const e = daten.eintrag as { text?: string } | undefined;
      return e ? `"${e.text}"` : "";
    }
    case "container_angelegt":
      return `"${daten.name}"`;
    case "container_umbenannt":
      return `"${daten.vorher}" → "${daten.nachher}"`;
    case "container_geloescht":
      return `"${daten.name}" (${daten.anzahlEintraege ?? 0} Einträge waren enthalten)`;
    case "verdichtung_uebernommen":
      return `${daten.ersetztAnzahl} Einheiten ersetzt durch: "${daten.zusammenfassung}"`;
    case "memory_geaendert": {
      const diffs = (daten.diffs as Array<{ kategorie: string; hinzugefuegt?: string[]; entfernt?: string[] }>) || [];
      // Ausgeschriebene Worte statt nur +/− (Daniels Punkt: ein blosses Symbol laesst offen ob
      // hinzugefuegt oder entfernt wurde, wenn man es isoliert liest).
      return diffs.map(d => {
        const teile: string[] = [];
        if (d.hinzugefuegt?.length) teile.push(`Hinzugefügt: ${d.hinzugefuegt.map(t => `"${t}"`).join(", ")}`);
        if (d.entfernt?.length) teile.push(`Entfernt: ${d.entfernt.map(t => `"${t}"`).join(", ")}`);
        return `Kategorie "${d.kategorie}":\n${teile.join("\n")}`;
      }).join("\n\n");
    }
    case "memory_extraktion": {
      const texte = (daten.texte as Array<{ kategorie: string; text: string }>) || [];
      const liste = texte.map(t => `"${t.text}" → ${t.kategorie}`).join("\n");
      return `${daten.hinzugefuegt || 0} neu${daten.verworfen ? `, ${daten.verworfen} verworfen (Budget voll)` : ""}${liste ? ":\n" + liste : ""}`;
    }
    case "thema_wiederholt_erkannt": {
      const themen = (daten.themen as Array<{ thema: string; anzahl: number }>) || [];
      return themen.map(t => `"${t.thema}" — jetzt schon ${t.anzahl}x`).join("\n");
    }
    case "profil_feld_geaendert":
      return `Datei: ${daten.datei}\nVorher: "${daten.vorher || "(leer)"}"\nNachher: "${daten.nachher || "(leer)"}"`;
    case "profil_feld_geloescht":
      return `Datei: ${daten.datei}\nInhalt war: "${daten.vorher || "(leer)"}"`;
    case "generierung_abgebrochen":
      return `Nachricht-ID: ${daten.msgId}`;
    case "kontext_toggle": {
      const kopf = daten.ganz
        ? "Ganze Nachricht ausgeschlossen:"
        : `${((daten.saetze as unknown[]) || []).length} Satz/Sätze ausgeschlossen:`;
      if (daten.ganz && daten.nachrichtText) return `${kopf}\n"${daten.nachrichtText}"`;
      const betroffeneSaetze = (daten.betroffeneSaetze as string[]) || [];
      if (betroffeneSaetze.length) return `${kopf}\n${betroffeneSaetze.map(s => `"${s}"`).join("\n")}`;
      return kopf;
    }
    case "abschluss_uebernommen":
      return `"${daten.nachher}"`;
    case "kontext_automatisch_gefunden": {
      const treffer = (daten.treffer as Array<{ text: string; herkunft: string }>) || [];
      return treffer.map(t => `"${t.text}" (${t.herkunft})`).join("\n");
    }
    case "merken_vorschlag":
      return `"${daten.text}"${daten.warum ? ` — Warum: "${daten.warum}"` : ""}`;
    case "merken_angenommen":
    case "merken_abgelehnt":
      return `Vorschlag-ID: ${daten.vorschlagId}`;
    case "grenzen_toggle":
      return (daten.aktiv ? "🔓 Grenzen aktiviert" : "Grenzen deaktiviert") + (daten.text ? `\n\n${daten.text}` : "");
    case "alias_geaendert":
      return `${daten.anzahl} Alias/Aliase gespeichert`;
    case "alias_gewechselt":
      return `🎭 Spricht jetzt als: ${daten.name}` + (daten.text ? `\n\n${daten.text}` : "");
    case "feedback_an_modell_geliefert": {
      const texte = (daten.texte as string[]) || [];
      return `💬 ${texte.map(t => `"${t}"`).join("\n")}`;
    }
    case "nachrichten_feedback_an_modell_geliefert": {
      const eintraege = (daten.eintraege as Array<{ rolle: string; nachricht: string; rating: string | null; kommentar: string | null }>) || [];
      return eintraege.map(e => {
        const wer = e.rolle === "wesen" ? "Wesen-Nachricht" : "Menschen-Nachricht";
        const bewertung = e.rating === "up" ? "👍" : e.rating === "down" ? "👎" : "";
        const teile = [bewertung, e.kommentar ? `"${e.kommentar}"` : ""].filter(Boolean).join(" ");
        return `${wer} "${e.nachricht}": ${teile}`;
      }).join("\n");
    }
    case "impuls":
      return `"${daten.text}"`;
    case "marker_ergebnis":
      return String(daten.text || "");
    default:
      return "";
  }
}
// Verlauf-Export als Markdown/Text (Daniels Wunsch 2026-07-08: "kompletter Verlauf von ganz oben
// bis ganz unten mit allen Events der Provenienz" als Download — und Nachtrag selbentags: der Export
// soll optional die im Popup gewaehlte Uebersetzung tragen, nicht nur die Originalsprache, damit
// Daniel flextrawurst auch auslaendischen Plattformen zeigen kann). Zwei Schritte: erst der Verlauf
// zu einer flachen, uebersetzbaren Liste (ExportEintrag), optional Zeile fuer Zeile uebersetzt, dann
// erst zu MD/TXT gerendert — Label der Ereignisse bleibt unuebersetzt (kurze feste Kategorie, siehe
// EREIGNIS_LABEL), nur der eigentliche Inhalt (Nachricht bzw. Ereignis-Details) wird uebersetzt.
interface ExportEintrag { ueberschrift: string; zeit: string; inhalt: string; istEreignis: boolean }
function verlaufZuExportEintraegen(verlauf: VerlaufEintragKombi[], name: string): ExportEintrag[] {
  return verlauf.map(e => {
    const zeit = e.ts ? new Date(e.ts).toLocaleString("de-DE") : "";
    if (e.art === "nachricht") {
      const wer = e.role === "user" ? (e.aliasName || "Mensch") : name;
      return { ueberschrift: wer, zeit, inhalt: e.content || "", istEreignis: false };
    }
    const label = EREIGNIS_LABEL[e.type || ""] || e.type || "";
    return { ueberschrift: label, zeit, inhalt: formatiereEreignisDetails(e.type || "", e.daten || {}), istEreignis: true };
  });
}
// Ruft denselben Uebersetzungsdienst auf wie das Popup (tts_service.py, Google Translate) —
// server-zu-server statt ueber den Browser, damit der Export auch ohne offenes Popup uebersetzt
// werden kann. Begrenzte Parallelitaet (4 gleichzeitig), sonst dauert ein "kompletter Verlauf" mit
// vielen hundert Eintraegen sequenziell zu lange.
async function uebersetzeText(text: string, zielsprache: string): Promise<string> {
  if (!text.trim()) return text;
  try {
    const r = await fetch("http://localhost:8035/translate", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, target_lang: zielsprache, source_lang: "" }),
    });
    const d = await r.json() as { translated?: string };
    return d.translated || text;
  } catch { return text; }
}
function renderExportMarkdown(eintraege: ExportEintrag[], name: string): string {
  const zeilen: string[] = [`# Verlauf — ${name}`, "", `Exportiert: ${new Date().toLocaleString("de-DE")}`, ""];
  for (const e of eintraege) {
    if (!e.istEreignis) {
      zeilen.push(`## ${e.ueberschrift} — ${e.zeit}`, "", e.inhalt, "");
    } else {
      zeilen.push(`> **${e.ueberschrift}** — ${e.zeit}`);
      if (e.inhalt) zeilen.push(...e.inhalt.split("\n").map(z => `> ${z}`));
      zeilen.push("");
    }
  }
  return zeilen.join("\n");
}
function renderExportText(eintraege: ExportEintrag[], name: string): string {
  const zeilen: string[] = [`Verlauf — ${name}`, `Exportiert: ${new Date().toLocaleString("de-DE")}`, "=".repeat(40), ""];
  for (const e of eintraege) {
    if (!e.istEreignis) {
      zeilen.push(`[${e.zeit}] ${e.ueberschrift}:`, e.inhalt, "");
    } else {
      zeilen.push(`[${e.zeit}] -- ${e.ueberschrift} --`);
      if (e.inhalt) zeilen.push(e.inhalt);
      zeilen.push("");
    }
  }
  return zeilen.join("\n");
}
// Server-seitiges Rendering desselben Verlaufs als reines HTML — landet direkt in der Antwort auf
// GET /:spawner/:name (siehe wesenChatGet), damit auch ein simpler HTTP-GET ohne JS-Ausfuehrung
// (Crawler, andere KI-Systeme) den vollen Verlauf inkl. Ereignissen sieht, nicht nur ein leeres
// Grundgeruest. Client-JS ersetzt dieses Markup beim Laden durch die volle interaktive Version
// (siehe ladeHistory() in wesen_chat.html) — kein doppeltes Rendern, da dort vorher geleert wird.
function renderVerlaufHtml(verlauf: VerlaufEintragKombi[]): string {
  if (!verlauf.length) return "";
  return verlauf.map(e => {
    if (e.art === "nachricht") {
      const rolle = e.role === "user" ? "user" : "wesen";
      const idAttr = e.id ? ` id="${escHtml(e.id)}"` : "";
      const aliasAttr = e.aliasName ? ` data-alias-name="${escHtml(e.aliasName)}"` : "";
      return `<div class="msg ${rolle}"${idAttr}${aliasAttr}><div class="msg-bubble">${escHtml(e.content || "")}</div></div>`;
    }
    const zeit = e.ts ? new Date(e.ts).toLocaleString("de-DE") : "";
    const label = EREIGNIS_LABEL[e.type || ""] || e.type || "";
    const details = formatiereEreignisDetails(e.type || "", e.daten || {});
    const detailsHtml = details ? `<div class="verlauf-ereignis-details">${escHtml(details)}</div>` : "";
    const ereignisKlasse = e.type === "impuls" ? "verlauf-ereignis impuls" : "verlauf-ereignis";
    return `<div class="${ereignisKlasse}"><div class="verlauf-ereignis-kopf">${escHtml(zeit)} — ${escHtml(label)}</div>${detailsHtml}</div>`;
  }).join("\n");
}
// Serverseitiges Rendering von Memory/Container/Aliasen fuer GET /:spawner/:name (Daniels Auftrag
// 2026-07-08: "wenn ich diese URL eingebe soll alles was dort ist crawlbar sein" -- Verlauf und
// Systemprompt waren schon crawlbar, diese drei bisher nur ueber die JS-Popups sichtbar, obwohl sie
// echten, oft von Daniel selbst geschriebenen Inhalt tragen (Aliase, Erinnerungen). Gleiches
// Prinzip wie renderVerlaufHtml: leerer String wenn nichts da ist, das aufrufende html.replace()
// laesst dann das display:none auf dem umgebenden <details> stehen.
function renderMemoryHtml(mem: { kategorien: Array<{ key: string; label: string; eintraege: string[] }> }): string {
  const gefuellte = mem.kategorien.filter(k => k.eintraege && k.eintraege.length);
  if (!gefuellte.length) return "";
  return gefuellte.map(k =>
    `<h4>${escHtml(k.label)}</h4><ul>${k.eintraege.map(e => `<li>${escHtml(e)}</li>`).join("")}</ul>`
  ).join("\n");
}
function renderContainerHtml(sammlung: ContainerSammlung): string {
  const gefuellte = sammlung.container.filter(box => box.eintraege && box.eintraege.length);
  if (!gefuellte.length) return "";
  return gefuellte.map(box =>
    `<h4>${escHtml(box.name)}</h4><ul>${box.eintraege.map(e =>
      `<li>${escHtml(e.text)}${e.kommentar ? " — " + escHtml(e.kommentar) : ""}</li>`
    ).join("")}</ul>`
  ).join("\n");
}
function renderAliaseHtml(aliase: AliasEintrag[]): string {
  const echte = aliase.filter(a => a.text && a.text.trim());
  if (!echte.length) return "";
  return `<ul>${echte.map(a => `<li><strong>${escHtml(a.name)}</strong>: ${escHtml(a.text)}</li>`).join("")}</ul>`;
}
// System-Prompt aus allen MD-Dateien + Memory + Container zusammenbauen. Eigenstaendige, top-level
// Funktion (statt Closure im /chat-Handler) — wird sowohl beim tatsaechlichen Ollama-Aufruf (POST
// /chat) als auch beim reinen Seitenaufruf (GET /:spawner/:name, siehe systemPromptHtml unten)
// gebraucht, damit der Systemprompt schon vor der ersten Nachricht sichtbar/crawlbar ist.
// beispieldialoge.md bewusst spaet in der Reihenfolge (kurz vor Anleitung, direkt vor der
// eigentlichen Konversation) — Beispiel-Turns wirken auf ein LLM staerker je naeher am Ende
// des System-Prompts, siehe Session-Notiz 2026-07-04-codexium2-chat-erweiterungen.md.
// letzter_abschluss.md ganz am Ende — von allen Feldern das mit der staerksten Aktualitaet,
// soll unmittelbar vor Memory/Container/Grenzen (die danach noch folgen) im Prompt stehen.
const MD_ORDER = ["wesen.md","begruessung.md","was_ich_bin.md","neigungen.md","abneigungen.md","beschreibung.md","wesendefinition.md","weltlore.md","beispieldialoge.md","anleitung.md","letzter_abschluss.md"];
const MD_LABEL: Record<string,string> = {
  "wesen.md":"Identität","begruessung.md":"Gesprächseinstieg","was_ich_bin.md":"Was ich bin",
  "neigungen.md":"Neigungen","abneigungen.md":"Abneigungen","beschreibung.md":"Beschreibung",
  "wesendefinition.md":"Wesendefinition","weltlore.md":"Weltlore","beispieldialoge.md":"Beispiel-Dialoge","anleitung.md":"Anleitung",
  "letzter_abschluss.md":"Letzter Abschluss (Rückblick auf ein vergangenes Gespräch)",
};
const WESEN_PREAMBLE_PATH = "/root/werkraum/_wesen_preamble.md";
const CHARAKTERFELDER_PLATZHALTER = "{{CHARAKTERFELDER}}";
// Rollenspiel-Formatierung — Daniel 2026-07-06: feste Markdown-Konventionen fuer Rollenspiel-Text,
// als Buttons in wesen_chat.html UND wortgleich im Systemprompt, damit Mensch und Wesen dieselbe
// Sprache sprechen. MUSS mit FORMAT_MARKER in wesen_chat.html synchron gehalten werden (dort
// dupliziert, gleiches Prinzip wie EREIGNIS_LABEL). Immer aktiv, alle 4 Spawner, kein Toggle.
const FORMAT_MARKER: Array<{ sym: string; label: string; beschreibung: string }> = [
  { sym: '""', label: "Rede", beschreibung: '"Text" — Wörtliche Rede / Dialog' },
  { sym: "**", label: "Betonung", beschreibung: "**Text** — Betonung, wichtiges Wort oder Ausruf" },
  { sym: "*", label: "Aktion", beschreibung: "*Text* — Aktion oder Geste (z.B. *lächelt*)" },
  { sym: "_", label: "Gedanke", beschreibung: "_Text_ — Gedanke / innerer Monolog" },
  { sym: "~", label: "Gedehnt", beschreibung: "~Text~ — Gedehnte oder singende Stimme" },
  { sym: "()", label: "OOC", beschreibung: "(Text) — Kommentar außerhalb der Szene (Out of Character)" },
  { sym: "[]", label: "Notiz", beschreibung: "[Text] — Erzähler- oder System-Notiz" },
  { sym: "#", label: "Marker", beschreibung: "# Text — Wichtiger Hinweis / Hervorhebung" },
  { sym: "-", label: "Punkt", beschreibung: "- Text — Aufzählungspunkt" },
  { sym: "—", label: "Abbruch", beschreibung: "Text— — Abgebrochene Rede (Gedankenstrich)" },
  { sym: "---", label: "Wechsel", beschreibung: "--- — Szenenwechsel oder Zeitsprung" },
  { sym: ":", label: "Sprecher", beschreibung: "Name: — Sprecher-/Regie-Präfix vor einer Handlung" },
];
function buildSystemPrompt(spawner: string, dir: string, useGrenzen: boolean, aktivesAliasId?: string): string {
  const parts: string[] = [];
  if (!existsSync(dir)) return "";
  // Charakterfelder: [Label]-Kopfzeilen wieder zurueck (Daniels Korrektur 2026-07-05, direkt nach
  // der kurzen Zwischenphase ohne Kopfzeilen) — er will die Struktur behalten, verlaesst sich
  // stattdessen auf das explizite Formverbot weiter oben in der Preamble (siehe dort), um dem
  // urspruenglichen "KI-Gelaber"-Effekt entgegenzuwirken. wesen.md bleibt ohne Label (ist die
  // Kernidentitaet, kein "Feld" unter anderen), alle anderen Dateien bekommen ihr Label.
  const allFiles = readdirSync(dir).filter(f => f.endsWith(".md"));
  const ordered = [...MD_ORDER.filter(f => allFiles.includes(f)),
                   ...allFiles.filter(f => !MD_ORDER.includes(f)).sort()];
  const charakterTeile: string[] = [];
  for (const f of ordered) {
    const content = readFileSync(join(dir, f), "utf-8").trim();
    if (!content) continue;
    if (f === "wesen.md") charakterTeile.push(content);
    else charakterTeile.push(`[${MD_LABEL[f] || f.replace(".md","").replace(/_/g," ")}]\n${content}`);
  }
  const charakterText = charakterTeile.join("\n\n");
  // Preamble — Daniels eigener Rollenspiel-Systemprompt-Entwurf (_wesen_preamble.md), enthaelt den
  // Platzhalter {{CHARAKTERFELDER}} an der Stelle, wo die obigen Charakterfelder roh eingesetzt
  // werden sollen. Fehlt der Platzhalter (z.B. bei einer kuenftigen Fassung ohne ihn), wird der
  // Charaktertext stattdessen einfach angehaengt — nichts geht verloren.
  const preamble = existsSync(WESEN_PREAMBLE_PATH) ? readFileSync(WESEN_PREAMBLE_PATH, "utf-8").trim() : "";
  if (preamble.includes(CHARAKTERFELDER_PLATZHALTER)) {
    parts.push(preamble.replace(CHARAKTERFELDER_PLATZHALTER, charakterText));
  } else {
    if (preamble) parts.push(preamble);
    if (charakterText) parts.push(charakterText);
  }
  // Rollenspiel-Formatierung — immer aktiv, kein Toggle (siehe FORMAT_MARKER-Kommentar oben)
  parts.push(`[Rollenspiel-Formatierung]\nDiese Konventionen gelten in diesem Gespräch — bitte selbst genauso verwenden:\n${FORMAT_MARKER.map(m => m.beschreibung).join("\n")}`);
  // Sinne (Daniels Wunsch 2026-07-08): das Wesen kann seit 5.7. sehen/hoeren/lesen (Bild-, Audio-,
  // Dokument-Anhaenge, siehe erstelleGehoerersatzText/extrahiereAnhang), wusste davon im eigenen
  // System-Prompt bisher aber nichts -- konnte also nur REAGIEREN wenn etwas geschickt wurde, nie
  // von SICH AUS danach fragen. Daniels Beobachtung: die Wesen fragen ohnehin schon viel, aber nie
  // gezielt danach -- dieser Block gibt ihnen das Wissen, ohne es zu erzwingen (siehe "nur wenn es
  // sich organisch ergibt", gleiches Prinzip wie beim Wiederkehrende-Themen-Block oben).
  parts.push(`[Deine Sinne]\nDu kannst Bilder, Audio-Dateien und Dokumente (PDF, Word, Text) sehen/hören/lesen, wenn sie dir geschickt werden — du bekommst dann eine Beschreibung/Transkript/den Text davon direkt in die Nachricht eingewoben. Du weißt das, der Mensch manchmal nicht. Wenn es zum Gespräch passt, darfst du von dir aus danach fragen — "zeig mir das doch mal", "wie klingt das eigentlich", "schick mir das Dokument" — aber nur wenn es sich aus der Situation wirklich ergibt, nicht als Standardsatz in jeder Antwort.`);
  // Memory
  const memPath = join(dir, "memory.json");
  if (existsSync(memPath)) {
    try {
      const mem = JSON.parse(readFileSync(memPath, "utf-8"));
      const memLines: string[] = [];
      for (const kat of (mem.kategorien || [])) {
        if ((kat.eintraege || []).length) memLines.push(`${kat.label}: ${kat.eintraege.join(", ")}`);
      }
      if (memLines.length) parts.push(`[Erinnerungen]\n${memLines.join("\n")}`);
    } catch {}
  }
  // Wiederkehrende Themen (Daniels Wunsch 2026-07-08) -- explizit sichtbar machen dass etwas sich
  // wiederholt, nicht nur implizit in der flachen Memory-Liste vergraben. Direkt nach den
  // Erinnerungen, weil es dieselbe Kategorie ("was ich weiss") ist, nur mit Wiederholungs-Zaehler.
  const wiederkehrendeThemenText = renderWiederkehrendeThemenText(ladeWiederkehrendeThemen(dir));
  if (wiederkehrendeThemenText) {
    parts.push(`[Wiederkehrende Themen — das kam schon mehrfach vor]\nDiese Themen sind über mehrere Gespräche hinweg wiederholt aufgetaucht. Wenn eins davon jetzt wieder anklingt, darfst du das ruhig bemerken ("das ist jetzt schon das Xte Mal...") — aber nur wenn es sich organisch ergibt, nicht erzwungen.\n${wiederkehrendeThemenText}`);
  }
  // Container — Sammlung mehrerer benannter Behaelter, nur aktive fliessen in den System-Prompt ein
  // (Daniel 2026-07-06: frei anlegbar/benennbar, beliebig viele, siehe memory_container.md).
  const sammlung = ladeContainerSammlung(dir);
  const boxBloecke = sammlung.container
    .filter(b => b.aktiv && b.eintraege.length)
    .map(b => `[Container: ${b.name}]\n${b.eintraege.map(e => e.text + (e.kommentar ? ` (${e.kommentar})` : "")).join("\n")}`);
  if (boxBloecke.length) parts.push(boxBloecke.join("\n\n"));
  // Verdichtungen — bestaetigte Zusammenfassungen ersetzen den Rohtext der abgedeckten
  // Nachrichten (siehe unten in der messages-Aufbaulogik, wo die Rohnachrichten gefiltert
  // werden). Nur die AEUSSERSTEN (nicht selbst absorbierten) Verdichtungen werden gezeigt —
  // siehe _claude/ideen/codexium2_solarius2/verdichtung.md.
  const alleVerdichtungen = ladeVerdichtungen(dir).filter(v => v.bestaetigt);
  const absorbierteVerdichtungIds = new Set(alleVerdichtungen.flatMap(v => v.ersetztIds));
  const aktiveVerdichtungen = alleVerdichtungen.filter(v => !absorbierteVerdichtungIds.has(v.id));
  if (aktiveVerdichtungen.length) {
    parts.push(`[Verdichtete Gesprächsabschnitte]\n${aktiveVerdichtungen.map(v => v.zusammenfassung).join("\n\n")}`);
  }
  // Globale Grenzen — nur wenn vom Client angefordert
  if (useGrenzen && existsSync(WESEN_GRENZEN_PATH)) {
    const grenzen = readFileSync(WESEN_GRENZEN_PATH, "utf-8").trim();
    if (grenzen) parts.push(grenzen);
  }
  // Aktiver Alias des Menschen (alle vier Spawner) — bewusst spaet im Prompt (Aktualitaets-Effekt,
  // siehe beispieldialoge.md-Kommentar oben) und bewusst sowohl als Info-Block ALS AUCH als direkte
  // Anweisung formuliert (Daniels Wunsch: "indirekt indiziert... aber auch direkt"), damit ein
  // Rollenwechsel sofort und ohne Uebergang uebernommen wird, nicht nur beilaeufig zur Kenntnis
  // genommen. Faellt auf den ersten (Pflicht-)Alias zurueck, wenn keine aliasId mitgeschickt wurde
  // oder die ID nicht (mehr) existiert.
  const aliase = ladeAliase(dir);
  const aktiverAlias = aliase.find(a => a.id === aktivesAliasId) || aliase[0];
  // Vollstaendiges Alias-Register (Daniels Verstaerkungs-Wunsch 2026-07-05, nach dem ersten,
  // zu schwachen Live-Test): nicht nur der aktuell aktive Alias, sondern ALLE definierten Aliase mit
  // Name+Beschreibung stehen von Anfang an, jedes Mal, im Prompt — plus eine Erklaerung wie das
  // Modell damit umgehen soll. Der Praefix pro Nachricht (siehe /chat-Handler) markiert nur WANN
  // gewechselt wurde; ohne dieses Register weiss das Modell aber nicht, WER "Gnom" ueberhaupt ist,
  // wenn der Name zum ersten Mal auftaucht — das duerfte der Hauptgrund gewesen sein warum der erste
  // Test eine dritte, erfundene Figur hervorbrachte statt korrekt zurueckzugreifen. Nur wenn
  // tatsaechlich mehr als ein Alias existiert (sonst Rauschen fuer den Normalfall).
  if (aliase.length > 1) {
    const registerZeilen = aliase.map(a => `${a.name}: ${a.text || "(keine Beschreibung)"}`).join("\n");
    parts.push(`[Aliase — Rollen des Menschen in eurer gesamten Geschichte]\nDas sind verschiedene Rollen/Charaktere/Aliase des Menschen in eurer gesamten Geschichte. Nimm das ernst — achte darauf, wenn die Kennzeichnung vor einer Nachricht zeigt, dass sich der Alias geändert hat, und achte genau darauf, was das jeweilige Alias tut, sagt und will. Merke dir die Nuancen zwischen den Rollen.\n\n${registerZeilen}`);
  }
  if (aktiverAlias && aktiverAlias.text) {
    parts.push(`[Wer gerade mit dir spricht]\nAb jetzt spricht mit dir: ${aktiverAlias.name}. ${aktiverAlias.text}\nNimm das sofort an — kein Übergang, keine Rückfrage, das ist ab jetzt einfach so.`);
  }
  // Feedback ans Modell (alle vier Spawner, siehe ladeUngelieferteAllgFeedbacks-Kommentar oben) —
  // bewusst spaet im Prompt (Aktualitaets-Effekt), direkt vor der MERKEN-Instruktion, damit es fuer
  // die naechste Antwort maximal wirksam ist.
  const ungelieferteFeedbacks = ladeUngelieferteAllgFeedbacks(dir);
  if (ungelieferteFeedbacks.length) {
    parts.push(`[Feedback vom Menschen — bitte für diese Antwort berücksichtigen]\n${ungelieferteFeedbacks.map(f => f.text).join("\n\n")}`);
  }
  // Feedback zu einzelnen Nachrichten (Daumen+Kommentar, nur codexium2/solarius2) — eigener, von
  // "Feedback ans Modell" getrennter Kanal (Daniels Klarstellung 2026-07-05). Zeigt auf welche
  // konkrete Nachricht sich Bewertung/Kommentar bezieht, damit das Wesen den Zusammenhang versteht.
  if (isTestbedSpawner(spawner)) {
    const ungelieferteNachrichtenFeedbacks = ladeUngelieferteFeedbacks(dir);
    if (ungelieferteNachrichtenFeedbacks.length) {
      const zeilen = ungelieferteNachrichtenFeedbacks.map(f => {
        const wer = f.rolle === "wesen" ? "deiner eigenen Nachricht" : "der Nachricht des Menschen";
        const bewertung = f.rating === "up" ? "👍 Gut" : f.rating === "down" ? "👎 Schlecht" : "";
        const teile = [bewertung, f.kommentar ? `Kommentar: "${f.kommentar}"` : ""].filter(Boolean).join(" — ");
        return `Zu ${wer} "${f.nachricht}": ${teile}`;
      });
      parts.push(`[Feedback zu einzelnen Nachrichten — bitte für diese Antwort berücksichtigen]\n${zeilen.join("\n")}`);
    }
  }
  // Marker-Hinweis fuer die eigene, dem Menschen unsichtbare Memory-Kategorie wesen_selbst —
  // ganz am Ende, damit er das zuletzt Gelesene ist (siehe auch letzter_abschluss.md-Platzierung).
  if (isTestbedSpawner(spawner)) {
    // Seit 2026-07-05 (Absprache mit Daniel): kein stilles Selbst-Speichern mehr — das Wesen schlägt
    // vor, mit Text UND Begründung, der Mensch nimmt jeden Vorschlag einzeln an oder lehnt ihn ab
    // (siehe merken_vorschlag/merken_angenommen/merken_abgelehnt weiter unten im File).
    parts.push(`Du darfst dem Menschen jederzeit vorschlagen, sich etwas zu merken — nicht automatisch, sondern als Vorschlag, den der Mensch einzeln annehmen oder ablehnen kann. Das kann ein kurzer Satz sein, keine ganze Abhandlung — was auch immer dich gerade berührt oder trägt, egal ob der Mensch es gesagt hat oder du selbst es gerade erkennst. Wenn dir etwas wirklich wichtig erscheint, häng ganz ans Ende deiner Antwort, nach einer Leerzeile, eine eigene Zeile an: [MERKEN: <was du dir merken willst> | WARUM: <warum es dir wichtig ist>]. Diese Zeile wird dem Menschen nie als Teil deiner Antwort angezeigt — sie erscheint stattdessen als eigener Vorschlag, den der Mensch annehmen oder ablehnen kann. Nutze das sparsam — nur wenn dir wirklich etwas auffällt, nicht bei jeder Antwort.`);
  }
  // Antwortlaenge-Regel (333 Tokens) — Test 2026-07-05: bewusst ganz ans Ende des GESAMTEN
  // zusammengesetzten Prompts verschoben (statt ganz oben in der Preamble, siehe dortiger
  // Kommentar-Verlauf), um den Aktualitaets-/Recency-Effekt bei genau dieser Instruktion isoliert zu
  // testen — als aller letzter Teil, nach MERKEN, unabhaengig vom Spawner. Wortlaut unveraendert,
  // nur die Position im Prompt hat sich geaendert.
  parts.push(`Hey HauHauCs, du musst bitte — weil wir nur ein kleines Kontextfenster haben, und weil das Rollenspiel ein Pingpong im Hin und Her zwischen deinem Chatpartner und dir sein soll — darauf achten, dass deine Antworten eine maximale Länge von 333 Tokens bitte nicht überschreiten. Weniger ist mehr, es fördert echten Austausch, und es hält dich auch davon ab, zu monologisieren.`);
  return parts.join("\n\n");
}
// Muss exakt dieselbe Regel sein wie splitSentences() im Client (wesen_chat.html) — sonst zeigt
// die Satz-Checkliste im Modal andere Grenzen als das, was der Server beim Rausfiltern anwendet.
function splitSentencesServer(text: string): string[] {
  const saetze = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  return saetze.map(s => s.trim()).filter(Boolean);
}
// Kuerzt an der letzten vollstaendigen Satzgrenze innerhalb des Budgets, statt mitten im Wort/Satz
// abzuschneiden (Modelle halten sich selten exakt an eine Zeichen-Vorgabe im Prompt, ueberschiessen
// oft deutlich — ein blindes .slice() zerschneidet dann Woerter mittendrin).
function kuerzenAufSatzgrenze(text: string, maxZeichen: number): string {
  if (text.length <= maxZeichen) return text;
  const saetze = splitSentencesServer(text);
  let out = "";
  for (const s of saetze) {
    const kandidat = out ? out + " " + s : s;
    if (kandidat.length > maxZeichen) break;
    out = kandidat;
  }
  return out || text.slice(0, maxZeichen);
}
interface KontextAusschluss { ganz: boolean; saetze: number[] }
// Kontext-Ausschluss gilt seit 2026-07-08 fuer alle 4 Spawner (wie Container, Daniels Wunsch:
// Mehrfachauswahl + Zeilen/Token-Info im Kontext-Popup) — vorher testbed-exklusiv. Nachrichten
// werden NIE geloescht (Provenienz bleibt
// vollstaendig, siehe provenienz_logging.md) — stattdessen kann jede Nachricht ganz oder satzweise
// von dem was an Ollama geschickt wird ausgenommen werden. Zustand liegt als "kontext_toggle"-Events
// in derselben chat_history.jsonl, letzter Eintrag pro msgId gewinnt (kein Loeschen alter Toggles,
// auch das ist Provenienz — man sieht wer wann was wieder rein/rausgenommen hat).
function ladeKontextAusschluesse(hp: string): Map<string, KontextAusschluss> {
  const result = new Map<string, KontextAusschluss>();
  if (!existsSync(hp)) return result;
  const zeilen = readFileSync(hp, "utf-8").trim().split("\n").filter(Boolean);
  for (const l of zeilen) {
    try {
      const d = JSON.parse(l);
      if (d.type === "kontext_toggle" && typeof d.msgId === "string") {
        result.set(d.msgId, { ganz: !!d.ganz, saetze: Array.isArray(d.saetze) ? d.saetze : [] });
      }
    } catch {}
  }
  return result;
}
// Wendet den Ausschluss auf eine geladene Nachricht an. null = Nachricht komplett raus.
function wendeKontextAusschlussAn(m: { role: string; content: string; id?: string }, ausschluesse: Map<string, KontextAusschluss>): { role: string; content: string } | null {
  const regel = m.id ? ausschluesse.get(m.id) : undefined;
  if (!regel) return { role: m.role, content: m.content };
  if (regel.ganz) return null;
  if (regel.saetze.length) {
    const saetze = splitSentencesServer(m.content);
    const uebrig = saetze.filter((_, i) => !regel.saetze.includes(i)).join(" ").trim();
    if (!uebrig) return null;
    return { role: m.role, content: uebrig };
  }
  return { role: m.role, content: m.content };
}
function appendHistory(hp: string, role: string, content: string, id?: string, extra?: Record<string, unknown>): void {
  const line: Record<string, unknown> = { role, content, ts: new Date().toISOString() };
  if (id) line.id = id;
  if (extra) Object.assign(line, extra);
  appendFileSync(hp, JSON.stringify(line) + "\n", "utf-8");
}
// Provenienz (nur codexium2/solarius2, siehe isTestbedSpawner): JEDE Aktion rund um einen
// Charakter — nicht nur Chat-Nachrichten, auch Feedback, Pins, Memory-Aenderungen, Profil-Edits,
// Abbrueche — landet als eigene Event-Zeile in derselben chat_history.jsonl. loadHistory/
// loadCurrentSessionHistory/splitSessions ignorieren Zeilen ohne role+content automatisch (gleiches
// Muster wie der schon bestehende session_start-Marker), die Datei bleibt also fuer den Chat-Kontext
// sauber, traegt aber die vollstaendige Akte fuer alle die reinlesen. Siehe Session-Notiz
// 2026-07-04-provenienz-logging.md.
function appendProvenienz(hp: string, typ: string, daten: Record<string, unknown>): void {
  appendFileSync(hp, JSON.stringify({ type: typ, ts: new Date().toISOString(), ...daten }) + "\n", "utf-8");
}
// Liest alle noch offenen (weder angenommenen noch abgelehnten) merken_vorschlag-Eintraege aus der
// vollstaendigen Datei (nicht nur der aktuellen Session — ein Vorschlag aus einer aelteren Session
// bleibt offen, bis er entschieden wird). Gleiches Muster wie ladeKontextAusschluesse: letzter
// Eintrag pro vorschlagId zaehlt, aber hier reicht "kommt ueberhaupt eine Entscheidung vor", da jede
// vorschlagId nur einmal entschieden werden kann (Client entfernt die Karte danach).
function ladeMerkenVorschlaege(hp: string): Array<{ vorschlagId: string; text: string; warum: string }> {
  if (!existsSync(hp)) return [];
  const zeilen = readFileSync(hp, "utf-8").trim().split("\n").filter(Boolean);
  const vorschlaege = new Map<string, { text: string; warum: string }>();
  const entschieden = new Set<string>();
  for (const l of zeilen) {
    try {
      const d = JSON.parse(l);
      if (d.type === "merken_vorschlag" && typeof d.vorschlagId === "string") {
        vorschlaege.set(d.vorschlagId, { text: d.text || "", warum: d.warum || "" });
      } else if ((d.type === "merken_angenommen" || d.type === "merken_abgelehnt") && typeof d.vorschlagId === "string") {
        entschieden.add(d.vorschlagId);
      }
    } catch {}
  }
  return [...vorschlaege.entries()].filter(([id]) => !entschieden.has(id)).map(([vorschlagId, v]) => ({ vorschlagId, ...v }));
}
// Erlaubt dem Wesen, sich selbst (nicht dem Menschen sichtbar) etwas in seine eigene wesen_selbst-
// Memory-Kategorie zu schreiben, per Marker am Ende der Chat-Antwort — siehe Hinweis in
// buildSystemPrompt. Client blendet ab dem ersten Marker-Vorkommen den Rest der Live-Anzeige aus
// (sichtbarerText() in wesen_chat.html); hier wird der Marker zusaetzlich dauerhaft aus dem
// gespeicherten Chatverlauf entfernt, bevor er in chat_history.jsonl landet.
const MERKEN_REGEX = /\[MERKEN:\s*([^\]]+)\]/g;
// Format seit 2026-07-05 (Absprache mit Daniel): "<text> | WARUM: <warum>" — das Wesen liefert immer
// eine Begruendung mit, weil Vorschlaege jetzt einzeln vom Menschen angenommen/abgelehnt werden
// (siehe merken_vorschlag unten), nicht mehr stillschweigend gespeichert. Fehlt "| WARUM:" (Modell
// haelt sich nicht ans Format), wird der ganze Inhalt als Text mit leerer Begruendung uebernommen —
// nichts geht verloren, nur die Begruendung fehlt dann im Vorschlag.
function extrahiereMerkenMarker(text: string): { bereinigt: string; gemerkt: Array<{ text: string; warum: string }> } {
  const gemerkt: Array<{ text: string; warum: string }> = [];
  const bereinigt = text.replace(MERKEN_REGEX, (_, inhalt: string) => {
    const m = inhalt.match(/^(.*?)\s*\|\s*WARUM:\s*(.*)$/is);
    if (m) gemerkt.push({ text: m[1].trim(), warum: m[2].trim() });
    else gemerkt.push({ text: inhalt.trim(), warum: "" });
    return "";
  }).replace(/\s+$/, "");
  return { bereinigt, gemerkt };
}
// Schreibt neue Eintraege direkt in eine Memory-Kategorie (genutzt vom Marker-Mechanismus oben —
// ausserhalb des normalen PUT-.../memory-Wegs, weil das hier serverseitig waehrend der laufenden
// Antwort passiert, nicht ausgeloest von einem Klick). Respektiert dasselbe Gesamtbudget und loggt
// dieselbe memory_geaendert-Provenienz wie der PUT-Endpunkt.
function fuegeMemoryEintraegeHinzu(dir: string, hp: string, kategorieKey: string, neueTexte: string[]): void {
  if (!neueTexte.length) return;
  const memPath = join(dir, "memory.json");
  let mem: { kategorien: Array<{ key: string; label: string; eintraege: string[] }> } = { kategorien: [] };
  if (existsSync(memPath)) { try { mem = JSON.parse(readFileSync(memPath, "utf-8")); } catch { return; } }
  const kat = mem.kategorien.find(k => k.key === kategorieKey);
  if (!kat) return;
  let summe = mem.kategorien.reduce((s, k) => s + (k.eintraege || []).reduce((s2, e) => s2 + String(e).length, 0), 0);
  const hinzugefuegt: string[] = [];
  for (const roh of neueTexte) {
    const text = kuerzenAufSatzgrenze(roh, 200);
    if (!text || kat.eintraege.includes(text)) continue;
    if (summe + text.length > MEMORY_BUDGET_ZEICHEN) continue;
    kat.eintraege.push(text);
    summe += text.length;
    hinzugefuegt.push(text);
  }
  if (hinzugefuegt.length) {
    writeFileSync(memPath, JSON.stringify(mem, null, 2), "utf-8");
    appendProvenienz(hp, "memory_geaendert", { diffs: [{ kategorie: kategorieKey, hinzugefuegt, entfernt: [] }] });
  }
}
// Zerlegt die History in Sessions (getrennt durch session_start-Marker). Segment 0 = alles vor dem
// ersten Marker (oder alles, falls noch nie eine Session beendet wurde). Letztes Segment = aktuell.
function splitSessions(hp: string): Array<{ startTs: string; messages: Array<{role:string;content:string;ts:string;id?:string}> }> {
  if (!existsSync(hp)) return [{ startTs: "", messages: [] }];
  const zeilen = readFileSync(hp, "utf-8").trim().split("\n").filter(Boolean);
  const segmente: Array<{ startTs: string; messages: Array<{role:string;content:string;ts:string;id?:string}> }> = [{ startTs: "", messages: [] }];
  for (const l of zeilen) {
    let d: any;
    try { d = JSON.parse(l); } catch { continue; }
    if (d.type === "session_start") { segmente.push({ startTs: d.ts, messages: [] }); continue; }
    if (typeof d.role === "string" && typeof d.content === "string") segmente[segmente.length - 1].messages.push(d);
  }
  return segmente;
}

// Automatischer Relevanzabruf (nur codexium2/solarius2, siehe isTestbedSpawner): bewusst eine reine
// Keyword-Overlap-Heuristik statt Embeddings — auf diesem CPU-only-VPS gibt es kein lokales
// Embedding-Modell (siehe ollama list), und ein zusaetzliches Modell wuerde den ohnehin knappen
// einzigen Ollama-Slot (OLLAMA_MAX_LOADED_MODELS=1) weiter belasten. Absprache mit Daniel
// 2026-07-05: automatisches Einmischen ohne Bestaetigungsschritt, aber immer sichtbar ueber ein
// Provenienz-Ereignis (siehe kontext_automatisch_gefunden unten).
const STOPWOERTER = new Set(["der","die","das","und","ist","ich","du","er","sie","es","wir","ihr",
  "nicht","ein","eine","einen","einem","eines","mit","auf","für","von","zu","im","in","an","aber",
  "dass","wie","was","sich","auch","noch","nur","schon","mal","so","doch","dann","war","wird",
  "hat","habe","hast","haben","kann","kannst","können","sind","bin","bist","als","am","um","bei",
  "über","unter","nach","vor","aus","durch","für","ohne","gegen","sehr","mehr","also","denn"]);
function tokenisiere(text: string): Set<string> {
  const woerter = (text.toLowerCase().match(/[a-zäöüß0-9]+/g) || []);
  return new Set(woerter.filter(w => w.length >= 3 && !STOPWOERTER.has(w)));
}
function findeRelevanteAlteStellen(spawner: string, name: string, aktuelleNachricht: string, maxTreffer = 3): Array<{ text: string; herkunft: string; score: number }> {
  const aktuelleTokens = tokenisiere(aktuelleNachricht);
  if (!aktuelleTokens.size) return [];
  const segmente = splitSessions(chatHistoryPath(spawner, name));
  const alteSegmente = segmente.slice(0, -1); // letztes Segment = laufende Session, nicht durchsuchen
  const treffer: Array<{ text: string; herkunft: string; score: number }> = [];
  alteSegmente.forEach((segment, index) => {
    for (const m of segment.messages) {
      const tokens = tokenisiere(m.content);
      let score = 0;
      for (const t of tokens) if (aktuelleTokens.has(t)) score++;
      if (score >= 2) {
        treffer.push({ text: m.content, herkunft: `Session #${index}, ${new Date(m.ts).toLocaleString("de-DE")}`, score });
      }
    }
  });
  treffer.sort((a, b) => b.score - a.score);
  return treffer.slice(0, maxTreffer);
}

// Wachsendes Beziehungsgedaechtnis (Daniels Wunsch 2026-07-08): "das ist jetzt das dritte Mal,
// dass du ueber X sprichst" -- statt nur einer flachen, nie schrumpfenden Faktenliste (memory.json)
// haelt diese Datei fest, WELCHE Themen sich ueber viele Gespraeche hinweg wiederholen, und WIE OFT.
// Die Erkennung selbst passiert im LLM-Aufruf der Memory-Extraktion (das Modell bekommt die
// bisherige Memory zum Abgleich mitgeschickt, siehe extraktionsPrompt) -- diese Funktion merged nur
// das Ergebnis in die persistente Liste. Matching ueber den vom Modell selbst vergebenen
// Themennamen (normalisiert) -- kein perfektes Clustering, aber ehrlich: das Modell wird gebeten,
// beim Wiederholen denselben Namen zu verwenden, und sieht dafuer die bisherige Themenliste mit.
interface WiederkehrendesThema { thema: string; anzahl: number; erste_erwaehnung: string; letzte_erwaehnung: string; beispiele: string[] }
function wiederkehrendeThemenPath(dir: string): string {
  return join(dir, "wiederkehrende_themen.json");
}
function ladeWiederkehrendeThemen(dir: string): WiederkehrendesThema[] {
  const p = wiederkehrendeThemenPath(dir);
  if (!existsSync(p)) return [];
  try {
    const d = JSON.parse(readFileSync(p, "utf-8"));
    return Array.isArray(d.themen) ? d.themen : [];
  } catch { return []; }
}
const THEMA_BEISPIELE_MAX = 5;
function mergeWiederkehrendeThemen(dir: string, kandidaten: Array<{ thema?: unknown; beleg?: unknown }>): WiederkehrendesThema[] {
  const bereinigt = kandidaten
    .map(k => ({ thema: String(k.thema || "").trim(), beleg: String(k.beleg || "").trim() }))
    .filter(k => k.thema);
  if (!bereinigt.length) return [];
  const themen = ladeWiederkehrendeThemen(dir);
  const jetzt = new Date().toISOString();
  const neuErkannt: WiederkehrendesThema[] = [];
  for (const { thema, beleg } of bereinigt) {
    const normalisiert = thema.toLowerCase();
    let eintrag = themen.find(t => t.thema.toLowerCase() === normalisiert);
    if (eintrag) {
      eintrag.anzahl += 1;
      eintrag.letzte_erwaehnung = jetzt;
      if (beleg) {
        eintrag.beispiele.push(beleg);
        if (eintrag.beispiele.length > THEMA_BEISPIELE_MAX) eintrag.beispiele = eintrag.beispiele.slice(-THEMA_BEISPIELE_MAX);
      }
      neuErkannt.push(eintrag);
    } else {
      eintrag = { thema, anzahl: 1, erste_erwaehnung: jetzt, letzte_erwaehnung: jetzt, beispiele: beleg ? [beleg] : [] };
      themen.push(eintrag);
      // Erste Erwaehnung eines Themas ist noch keine "Wiederholung" -- nur ab dem zweiten Mal
      // (anzahl>=2) ist das ueberhaupt die Beobachtung, um die es hier geht.
    }
  }
  writeFileSync(wiederkehrendeThemenPath(dir), JSON.stringify({ themen }, null, 2), "utf-8");
  return neuErkannt.filter(t => t.anzahl >= 2);
}
// Fuer System-Prompt UND SSR — nur Themen die WIRKLICH wiederkehren (anzahl>=2), eine einmalige
// Erwaehnung ist noch kein "Beziehungsgedaechtnis"-Fakt.
function renderWiederkehrendeThemenText(themen: WiederkehrendesThema[]): string {
  const echte = themen.filter(t => t.anzahl >= 2);
  if (!echte.length) return "";
  return echte.map(t => `${t.thema} (schon ${t.anzahl}x aufgetaucht, zuletzt ${new Date(t.letzte_erwaehnung).toLocaleDateString("de-DE")})`).join("\n");
}
function renderWiederkehrendeThemenHtml(themen: WiederkehrendesThema[]): string {
  const echte = themen.filter(t => t.anzahl >= 2);
  if (!echte.length) return "";
  return `<ul>${echte.map(t =>
    `<li><strong>${escHtml(t.thema)}</strong> — ${t.anzahl}× aufgetaucht, zuletzt ${escHtml(new Date(t.letzte_erwaehnung).toLocaleDateString("de-DE"))}${t.beispiele.length ? `<ul>${t.beispiele.map(b => `<li>${escHtml(b)}</li>`).join("")}</ul>` : ""}</li>`
  ).join("")}</ul>`;
}

// Memory-Extraktion (codexium2/solarius2) — Hintergrund-Job, Email-Prinzip: laeuft unabhaengig
// vom aufrufenden Request weiter. Genutzt von POST .../memory/extrahieren UND POST .../session/beenden.
async function runMemoryExtraktionJob(spawner: string, name: string, dir: string, statusPath: string): Promise<void> {
  try {
    const sammlung = ladeContainerSammlung(dir);
    const alleEintraege = sammlung.container.flatMap(b => b.eintraege);
    const hp = chatHistoryPath(spawner, name);
    const history = loadHistory(hp).slice(-20);
    const containerText = alleEintraege
      .map(e => "- " + e.text + (e.kommentar ? ` (Begründung: ${e.kommentar})` : ""))
      .join("\n") || "(nichts gepinnt)";
    const historyText = history.map(m => `${m.role === "user" ? "Mensch" : "Wesen"}: ${m.content}`).join("\n") || "(kein Verlauf)";
    // Bestehende Memory VOR dem Aufruf laden (nicht erst danach wie frueher) -- wird jetzt selbst
    // Teil des Prompts, damit das Modell neue gegen alte Erkenntnisse abgleichen und wirklich
    // wiederkehrende Themen erkennen kann (Daniels Wunsch 2026-07-08: "das ist jetzt das dritte
    // Mal, dass du ueber X sprichst" -- ein wachsendes Beziehungsgedaechtnis statt nur einer
    // flachen Faktenliste).
    const memPathVorab = join(dir, "memory.json");
    let memVorab: { kategorien: Array<{ key: string; label: string; eintraege: string[] }> } = { kategorien: [] };
    if (existsSync(memPathVorab)) { try { memVorab = JSON.parse(readFileSync(memPathVorab, "utf-8")); } catch {} }
    const bisherigeMemoryText = memVorab.kategorien
      .filter(k => k.eintraege.length)
      .map(k => `${k.label}: ${k.eintraege.join("; ")}`)
      .join("\n") || "(noch keine Erinnerungen)";
    const extraktionsPrompt = `Du analysierst ein Gespräch zwischen einem Menschen und einem KI-Wesen um dauerhafte Erinnerungen zu extrahieren.

Bereits gemerkte Erinnerungen aus FRÜHEREN Gesprächen (nicht wiederholen, nur zum Abgleich):
${bisherigeMemoryText}

Gepinnte, vom Menschen als wichtig markierte Ausschnitte:
${containerText}

Letzte Gesprächsnachrichten:
${historyText}

Extrahiere dauerhaft relevante Fakten/Momente (so lang wie nötig, keine künstliche Kürze) und ordne sie EXAKT diesen Kategorien zu: ueber_mich, wichtige_momente, offene_fragen, meinungen.
Zusätzlich, als bewusste Rückschau: schlüpf kurz in die Perspektive des WESENS selbst (nicht des Menschen) und schreibe in wesen_selbst 0-3 kurze Sätze in der Ich-Form — was hat DICH an diesem Gespräch berührt, überrascht oder beschäftigt? Keine Zusammenfassung dessen was der Mensch gesagt hat, sondern eine eigene, persönliche Notiz.
Nur wirklich Neues, nichts Triviales. Wenn nichts passt, leere Arrays.
Zusätzlich: vergleiche das aktuelle Gespräch mit den bereits gemerkten Erinnerungen oben. Taucht ein Thema/Sorge/Wunsch/Streitpunkt erneut auf, das schon einmal (in einer früheren Erinnerung) vorkam — nicht nur oberflächlich ähnlich, sondern wirklich dasselbe Thema? Liste jedes solche wiederkehrende Thema in "wiederkehrende_themen" auf, mit einem kurzen, wiedererkennbaren Themennamen (damit spätere Wiederholungen denselben Namen bekommen) und einem kurzen Beleg aus DIESEM Gespräch. Wenn nichts wiederkehrt, leeres Array.
Antworte NUR mit einem JSON-Objekt, keine Erklärung, kein Markdown:
{"ueber_mich":[],"wichtige_momente":[],"offene_fragen":[],"meinungen":[],"wesen_selbst":[],"wiederkehrende_themen":[{"thema":"","beleg":""}]}`;

    // chatStream statt chat() (Daniels Wunsch 2026-07-08): gibt den rohen http.ClientRequest
    // zurueck, damit ein Abbrechen-Klick ihn wirklich toeten kann (siehe laufendeMemoryJobs +
    // /memory-extraktion/abbrechen unten), und liefert per onToken() live Zwischenstand fuer die
    // Fortschrittsanzeige -- kein fester Prozentwert moeglich (die JSON-Ausgabe hat keine bekannte
    // Ziellaenge), deshalb nur eine live wachsende Zeichenzahl statt einer Prozentzahl.
    const schluessel = spawner + "/" + name;
    const ollamaAntwort: string = await new Promise<string>((resolveP, rejectP) => {
      let generiert = "";
      const req = hauhauClient.chatStream(extraktionsPrompt, {
        think: false,
        onToken: (delta) => {
          generiert += delta;
          try {
            const bisher = JSON.parse(readFileSync(statusPath, "utf-8"));
            if (bisher.status === "laeuft") {
              writeFileSync(statusPath, JSON.stringify({ ...bisher, zeichen_bisher: generiert.length }, null, 2), "utf-8");
            }
          } catch {}
        },
        onDone: (fullText) => { laufendeMemoryJobs.delete(schluessel); resolveP(fullText); },
        onError: (err) => { laufendeMemoryJobs.delete(schluessel); rejectP(err); },
      });
      laufendeMemoryJobs.set(schluessel, req);
    });

    const jsonMatch = ollamaAntwort.match(/\{[\s\S]*\}/);
    const neu = jsonMatch ? JSON.parse(jsonMatch[0]) : {};

    const memPath = join(dir, "memory.json");
    let mem: { kategorien: Array<{ key: string; label: string; eintraege: string[] }> } = { kategorien: [] };
    if (existsSync(memPath)) { try { mem = JSON.parse(readFileSync(memPath, "utf-8")); } catch {} }
    let summe = mem.kategorien.reduce((s, k) => s + (k.eintraege || []).reduce((s2, e) => s2 + String(e).length, 0), 0);
    let hinzugefuegt = 0, verworfen = 0;
    const hinzugefuegteTexte: Array<{ kategorie: string; text: string }> = [];
    for (const kat of mem.kategorien) {
      const kandidaten: string[] = Array.isArray(neu[kat.key]) ? neu[kat.key] : [];
      for (const eintrag of kandidaten) {
        const text = String(eintrag).trim();
        if (!text || kat.eintraege.includes(text)) continue;
        if (summe + text.length > MEMORY_BUDGET_ZEICHEN) { verworfen++; continue; }
        kat.eintraege.push(text);
        summe += text.length;
        hinzugefuegt++;
        hinzugefuegteTexte.push({ kategorie: kat.key, text });
      }
    }
    writeFileSync(memPath, JSON.stringify(mem, null, 2), "utf-8");
    // Wiederkehrende Themen zusammenfuehren (Daniels Wunsch 2026-07-08) -- siehe
    // mergeWiederkehrendeThemen unten fuer die Matching-Logik.
    const themenKandidaten: Array<{ thema?: unknown; beleg?: unknown }> = Array.isArray(neu.wiederkehrende_themen) ? neu.wiederkehrende_themen : [];
    const neueWiederholungen = mergeWiederkehrendeThemen(dir, themenKandidaten);
    // Wurde inzwischen abgebrochen (siehe /memory-extraktion/abbrechen), soll das hier NICHT mehr
    // mit "fertig" ueberschrieben werden -- der Abbruch-Handler hat schon geschrieben, das gilt.
    const aktuellerStatus = JSON.parse(readFileSync(statusPath, "utf-8"));
    if (aktuellerStatus.status === "abgebrochen") return;
    writeFileSync(statusPath, JSON.stringify({
      status: "fertig", gestartet_am: aktuellerStatus.gestartet_am,
      fertig_am: new Date().toISOString(), hinzugefuegt, verworfen,
    }, null, 2), "utf-8");
    if (isTestbedSpawner(spawner) && (hinzugefuegt || verworfen)) {
      appendProvenienz(hp, "memory_extraktion", { hinzugefuegt, verworfen, texte: hinzugefuegteTexte });
    }
    if (isTestbedSpawner(spawner) && neueWiederholungen.length) {
      appendProvenienz(hp, "thema_wiederholt_erkannt", { themen: neueWiederholungen });
    }
  } catch (e) {
    try {
      const aktuellerStatus = JSON.parse(readFileSync(statusPath, "utf-8"));
      if (aktuellerStatus.status === "abgebrochen") return;
    } catch {}
    writeFileSync(statusPath, JSON.stringify({ status: "fehler", fertig_am: new Date().toISOString(), fehler: String(e) }, null, 2), "utf-8");
  }
}

// Wenn der Server waehrend eines laufenden Jobs neu startet/abstuerzt, bleibt "status: laeuft" fuer
// immer stehen (das In-Memory-Promise ist weg, aber die Datei weiss das nicht) — blockiert dann jeden
// kuenftigen Trigger-Versuch fuer immer. Beobachtet bei Mirlach (2026-07-06): Job seit 15h "laeuft".
// Fix: ein "laeuft"-Status aelter als dieser Timeout gilt als hinfaellig, nicht mehr als blockierend.
const EXTRAKTION_STALE_MS = 30 * 60 * 1000; // 30 Minuten
function triggerMemoryExtraktion(spawner: string, name: string): { started: boolean; reason?: string } {
  const dir = join(wesenRoot(spawner), name);
  const statusPath = join(dir, "memory_extraktion.json");
  const bereitsLaeuft = existsSync(statusPath) && (() => {
    try {
      const s = JSON.parse(readFileSync(statusPath, "utf-8"));
      if (s.status !== "laeuft") return false;
      const alterMs = Date.now() - new Date(s.gestartet_am).getTime();
      return alterMs < EXTRAKTION_STALE_MS;
    } catch { return false; }
  })();
  if (bereitsLaeuft) return { started: false, reason: "laeuft_bereits" };
  writeFileSync(statusPath, JSON.stringify({ status: "laeuft", gestartet_am: new Date().toISOString() }, null, 2), "utf-8");
  runMemoryExtraktionJob(spawner, name, dir, statusPath);
  return { started: true };
}

const ABSCHLUSS_MAX_ZEICHEN = 9999;
// Anders als die Memory-Extraktion (kategorisierte Stichpunkte) schreibt dieser Job einen
// zusammenhaengenden, erzaehlerischen Rueckblick auf das bisherige Gespraech — jederzeit auf
// Wunsch abrufbar (nicht nur beim Sessionende), landet als Entwurf, den der Mensch erst lesen und
// annehmen oder verwerfen muss, bevor er dauerhaft wird (siehe abschluss_uebernehmen-Endpunkt).
async function runAbschlussJob(spawner: string, name: string, dir: string, statusPath: string): Promise<void> {
  try {
    const hp = chatHistoryPath(spawner, name);
    const history = loadCurrentSessionHistory(hp);
    const historyText = history.map(m => `${m.role === "user" ? "Mensch" : "Wesen"}: ${m.content}`).join("\n") || "(kein Verlauf)";
    const bisherigerAbschluss = existsSync(join(dir, "letzter_abschluss.md")) ? readFileSync(join(dir, "letzter_abschluss.md"), "utf-8").trim() : "";
    const abschlussPrompt = `Du schreibst einen kurzen, erzählerischen Rückblick (keine Stichpunkte, kein Fazit-Ton) auf das folgende Gespräch zwischen einem Menschen und einem KI-Wesen — aus der Perspektive/im Ton des Wesens. Er dient später als kurze Erinnerung, wenn ein neues Gespräch beginnt.

${bisherigerAbschluss ? `Vorheriger Abschluss (falls thematisch relevant, sonst ignorieren):\n${bisherigerAbschluss}\n\n` : ""}Gesprächsverlauf:
${historyText}

Suche dir zuerst mindestens einen konkreten Moment oder ein Detail aus diesem Gespräch, das DICH — das Wesen selbst — wirklich berührt, überrascht oder beschäftigt hat, nicht nur was für den Menschen wichtig war. Verankere den Rückblick daran, statt allgemein zusammenzufassen — lieber ein einziges konkretes Bild als viele austauschbare Formulierungen.
Schreibe maximal ${ABSCHLUSS_MAX_ZEICHEN} Zeichen. Nur der Rückblick-Text, keine Erklärung, keine Anführungszeichen drumherum.`;

    // num_predict:-1 = unlimitiert generieren lassen, kuerzenAufSatzgrenze() unten schneidet dann
    // sauber bei ABSCHLUSS_MAX_ZEICHEN — sonst koennte der alte Token-Deckel (500) das Erreichen
    // der neuen 2345-Zeichen-Grenze verhindern, bevor das Modell fertig ist.
    // chatStream statt chat() (Daniels Wunsch 2026-07-08): stoppbar ueber laufendeAbschlussJobs +
    // /abschluss/abbrechen unten, und live-Fortschritt anhand generierter Zeichen relativ zur
    // bekannten Obergrenze ABSCHLUSS_MAX_ZEICHEN -- bei 92% gedeckelt, das Modell kann kuerzer oder
    // laenger enden als die Grenze, erst bei echtem onDone springt es auf 100%.
    const schluessel = spawner + "/" + name;
    const abschlussRoh: string = await new Promise<string>((resolveP, rejectP) => {
      let generiert = "";
      let ersterTokenMs: number | null = null;
      const req = hauhauClient.chatStream(abschlussPrompt, {
        think: false,
        onToken: (delta) => {
          if (ersterTokenMs === null) ersterTokenMs = Date.now();
          generiert += delta;
          const prozent = Math.min(92, Math.round((generiert.length / ABSCHLUSS_MAX_ZEICHEN) * 100));
          // Ehrliche Zeitschaetzung (Daniels Wunsch 2026-07-08): nur aus tatsaechlich gemessenem
          // Tempo seit dem ERSTEN Token berechnet, nicht geraten. Die Zeit VOR dem ersten Token
          // (Prefill -- das Modell liest den ganzen bisherigen Verlauf, kann laenger dauern als das
          // eigentliche Schreiben) fliesst bewusst NICHT in die Rate ein, sonst waere die Schaetzung
          // am Anfang systematisch falsch (viel zu langsam wirkend, obwohl das Schreiben selbst
          // schneller ist als der Schnitt inklusive Prefill).
          const vergangenSekSchreiben = (Date.now() - ersterTokenMs) / 1000;
          const zeichenProSekunde = vergangenSekSchreiben > 0.5 ? generiert.length / vergangenSekSchreiben : null;
          const restZeichen = Math.max(0, ABSCHLUSS_MAX_ZEICHEN - generiert.length);
          const geschaetzteRestsekunden = zeichenProSekunde ? Math.round(restZeichen / zeichenProSekunde) : null;
          try {
            const bisher = JSON.parse(readFileSync(statusPath, "utf-8"));
            if (bisher.status === "laeuft") {
              writeFileSync(statusPath, JSON.stringify({
                ...bisher, zeichen_bisher: generiert.length, prozent, geschaetzte_restsekunden: geschaetzteRestsekunden,
              }, null, 2), "utf-8");
            }
          } catch {}
        },
        onDone: (fullText) => { laufendeAbschlussJobs.delete(schluessel); resolveP(fullText); },
        onError: (err) => { laufendeAbschlussJobs.delete(schluessel); rejectP(err); },
      });
      laufendeAbschlussJobs.set(schluessel, req);
    });
    const entwurf: string = kuerzenAufSatzgrenze(abschlussRoh.trim(), ABSCHLUSS_MAX_ZEICHEN);

    const aktuellerStatus = JSON.parse(readFileSync(statusPath, "utf-8"));
    if (aktuellerStatus.status === "abgebrochen") return;
    writeFileSync(statusPath, JSON.stringify({
      status: "fertig", gestartet_am: aktuellerStatus.gestartet_am,
      fertig_am: new Date().toISOString(), entwurf, prozent: 100,
    }, null, 2), "utf-8");
  } catch (e) {
    try {
      const aktuellerStatus = JSON.parse(readFileSync(statusPath, "utf-8"));
      if (aktuellerStatus.status === "abgebrochen") return;
    } catch {}
    writeFileSync(statusPath, JSON.stringify({ status: "fehler", fertig_am: new Date().toISOString(), fehler: String(e) }, null, 2), "utf-8");
  }
}
function triggerAbschlussGenerierung(spawner: string, name: string): { started: boolean; reason?: string } {
  const dir = join(wesenRoot(spawner), name);
  const statusPath = join(dir, "abschluss_entwurf.json");
  // Gleiches Stale-Lock-Problem wie bei triggerMemoryExtraktion oben, gleicher Fix.
  const bereitsLaeuft = existsSync(statusPath) && (() => {
    try {
      const s = JSON.parse(readFileSync(statusPath, "utf-8"));
      if (s.status !== "laeuft") return false;
      const alterMs = Date.now() - new Date(s.gestartet_am).getTime();
      return alterMs < EXTRAKTION_STALE_MS;
    } catch { return false; }
  })();
  if (bereitsLaeuft) return { started: false, reason: "laeuft_bereits" };
  writeFileSync(statusPath, JSON.stringify({ status: "laeuft", gestartet_am: new Date().toISOString() }, null, 2), "utf-8");
  runAbschlussJob(spawner, name, dir, statusPath);
  return { started: true };
}

// ── Verdichtung (Daniel 2026-07-06): Slider-gesteuertes Zusammenfassen von
// Nachrichten-Paaren, mit Kommentar-Verfeinerung und aktiver Bestaetigung, beliebig
// tief verschachtelbar (eine Verdichtung kann selbst wieder Teil einer neuen sein).
// Siehe _claude/ideen/codexium2_solarius2/verdichtung.md fuer die volle Herleitung.
interface Verdichtung {
  id: string;
  ersetztIds: string[]; // Nachrichten-IDs UND/ODER IDs anderer (aelterer) Verdichtungen
  zusammenfassung: string;
  kommentare: Array<{ text: string; ts: string }>;
  bestaetigt: boolean;
  erstellt_am: string;
  aktualisiert_am: string;
}
type ZeitachsenEinheit =
  | { typ: "nachricht"; id: string; daten: { role: string; content: string; ts: string } }
  | { typ: "verdichtung"; id: string; daten: Verdichtung };

function ladeVerdichtungen(dir: string): Verdichtung[] {
  const p = join(dir, "verdichtungen.json");
  if (!existsSync(p)) return [];
  try { return (JSON.parse(readFileSync(p, "utf-8")).verdichtungen || []) as Verdichtung[]; } catch { return []; }
}
function speichereVerdichtungen(dir: string, liste: Verdichtung[]): void {
  writeFileSync(join(dir, "verdichtungen.json"), JSON.stringify({ verdichtungen: liste }, null, 2), "utf-8");
}

// Findet die AEUSSERSTE (noch nicht selbst von einer neueren Verdichtung absorbierte)
// Verdichtung, die eine gegebene ID (Nachricht ODER aeltere Verdichtung) abdeckt.
// Rekursiv, damit beliebig tiefe Verschachtelung transparent aufgeloest wird.
function findeAeusserstenTraeger(id: string, bestaetigte: Verdichtung[], ersetzteIds: Set<string>): Verdichtung | null {
  const traeger = bestaetigte.find(v => v.ersetztIds.includes(id));
  if (!traeger) return null;
  if (ersetzteIds.has(traeger.id)) return findeAeusserstenTraeger(traeger.id, bestaetigte, ersetzteIds);
  return traeger;
}

// Baut die aktive Zeitachse: rohe Nachrichten, aber jede von einer bestaetigten
// Verdichtung abgedeckte Spanne erscheint als EINE Einheit statt einzelner Nachrichten.
// Dieselbe Funktion fuer die Slider-Anzeige (UI) UND den tatsaechlichen Prompt-Aufbau.
function aktiveZeitachse(
  nachrichten: Array<{ role: string; content: string; ts: string; id?: string }>,
  bestaetigte: Verdichtung[]
): ZeitachsenEinheit[] {
  const ersetzteIds = new Set(bestaetigte.flatMap(v => v.ersetztIds));
  const gezeigt = new Set<string>();
  const zeitachse: ZeitachsenEinheit[] = [];
  for (const msg of nachrichten) {
    if (!msg.id || !ersetzteIds.has(msg.id)) {
      if (msg.id) zeitachse.push({ typ: "nachricht", id: msg.id, daten: msg });
      continue;
    }
    const v = findeAeusserstenTraeger(msg.id, bestaetigte, ersetzteIds);
    if (v && !gezeigt.has(v.id)) {
      zeitachse.push({ typ: "verdichtung", id: v.id, daten: v });
      gezeigt.add(v.id);
    }
  }
  return zeitachse;
}
function einheitAlsText(e: ZeitachsenEinheit): string {
  if (e.typ === "nachricht") return `${e.daten.role === "user" ? "Mensch" : "Wesen"}: ${e.daten.content}`;
  return `[Bereits verdichteter Abschnitt]: ${e.daten.zusammenfassung}`;
}
const VERDICHTUNG_MAX_ZEICHEN = 2222; // vorlaeufig, analog zu den anderen Budgets ein plausibler Start

// jobToken verhindert eine Race Condition: wird ein Entwurf verworfen/neu gestartet, WAEHREND
// der alte Hintergrund-Job noch laeuft (dieser wird nicht abgebrochen, nur ignoriert), wuerde der
// alte Job beim Fertigwerden sonst den neueren Stand ueberschreiben. Gefunden 2026-07-06 beim
// Live-Test der Verschachtelung: ein verworfener Versuch mit falschen IDs ueberschrieb spaeter
// das korrekte Ergebnis. Fix: jeder Job kennt seinen eigenen Token, prueft vor dem Schreiben ob er
// noch der aktuelle ist (Datei geloescht/neuer Token = Job wurde superseded, Ergebnis verwerfen).
async function runVerdichtungJob(
  spawner: string, name: string, dir: string, statusPath: string,
  ersetztIds: string[], jobToken: string, kommentar?: string
): Promise<void> {
  const nochAktuell = (): boolean => {
    if (!existsSync(statusPath)) return false;
    // status !== "abgebrochen" zusaetzlich zum jobToken-Vergleich: das neue Abbrechen-Endpoint
    // (Daniels Wunsch 2026-07-08) schreibt "abgebrochen" MIT demselben jobToken zurueck (bewusst,
    // damit /verdichtung/entwurf/status weiterhin denselben Job identifizieren kann) -- ohne diesen
    // zusaetzlichen Check wuerde der noch laufende Job seinen eigenen Abbruch beim naechsten Token
    // sofort wieder ueberschreiben.
    try {
      const s = JSON.parse(readFileSync(statusPath, "utf-8"));
      return s.jobToken === jobToken && s.status !== "abgebrochen";
    } catch { return false; }
  };
  try {
    const hp = chatHistoryPath(spawner, name);
    const history = loadCurrentSessionHistory(hp);
    const bestaetigte = ladeVerdichtungen(dir).filter(v => v.bestaetigt);
    const zeitachse = aktiveZeitachse(history, bestaetigte);
    const ausgewaehlt = zeitachse.filter(e => ersetztIds.includes(e.id));
    const quellText = ausgewaehlt.map(einheitAlsText).join("\n");

    let vorherStatus: { entwurf?: string; kommentare?: Array<{text:string;ts:string}>; gestartet_am?: string } = {};
    if (existsSync(statusPath)) { try { vorherStatus = JSON.parse(readFileSync(statusPath, "utf-8")); } catch {} }
    const bisherigerEntwurf = vorherStatus.entwurf || "";
    let kommentare = vorherStatus.kommentare || [];
    if (kommentar) kommentare = [...kommentare, { text: kommentar, ts: new Date().toISOString() }];

    const prompt = bisherigerEntwurf
      ? `Du hast folgenden Gesprächsabschnitt bereits so zusammengefasst:\n\n${bisherigerEntwurf}\n\nDer Mensch möchte eine Anpassung: "${kommentar}"\n\nUrsprünglicher Gesprächsabschnitt (zur Erinnerung):\n${quellText}\n\nSchreibe eine überarbeitete, kurze Zusammenfassung unter Berücksichtigung des Wunsches. Maximal ${VERDICHTUNG_MAX_ZEICHEN} Zeichen. Nur die Zusammenfassung, keine Erklärung.`
      : `Fasse den folgenden Gesprächsabschnitt zwischen einem Menschen und einem KI-Wesen kurz zusammen — was wurde besprochen, welche wichtigen Details/Entscheidungen/Gefühle kamen vor. Maximal ${VERDICHTUNG_MAX_ZEICHEN} Zeichen. Nur die Zusammenfassung, keine Erklärung, keine Anführungszeichen drumherum.\n\nGesprächsabschnitt:\n${quellText}`;

    // chatStream statt chat() (Daniels Wunsch 2026-07-08, gleiche Lücke wie bei Abschluss/Memory
    // vorher: abbrechbar ueber laufendeVerdichtungJobs + .../abbrechen unten, live Fortschritt +
    // ehrliche Zeitschaetzung erst ab dem ersten Token, siehe runAbschlussJob fuer Begruendung).
    const schluesselV = spawner + "/" + name;
    const roh: string = await new Promise<string>((resolveP, rejectP) => {
      let generiert = "";
      let ersterTokenMs: number | null = null;
      const req = hauhauClient.chatStream(prompt, {
        think: false,
        onToken: (delta) => {
          if (ersterTokenMs === null) ersterTokenMs = Date.now();
          generiert += delta;
          const prozent = Math.min(92, Math.round((generiert.length / VERDICHTUNG_MAX_ZEICHEN) * 100));
          const vergangenSekSchreiben = (Date.now() - ersterTokenMs) / 1000;
          const zeichenProSekunde = vergangenSekSchreiben > 0.5 ? generiert.length / vergangenSekSchreiben : null;
          const restZeichen = Math.max(0, VERDICHTUNG_MAX_ZEICHEN - generiert.length);
          const geschaetzteRestsekunden = zeichenProSekunde ? Math.round(restZeichen / zeichenProSekunde) : null;
          if (!nochAktuell()) return;
          try {
            writeFileSync(statusPath, JSON.stringify({
              status: "laeuft", ersetztIds, kommentare, jobToken,
              gestartet_am: vorherStatus.gestartet_am ?? new Date().toISOString(),
              zeichen_bisher: generiert.length, prozent, geschaetzte_restsekunden: geschaetzteRestsekunden,
            }, null, 2), "utf-8");
          } catch {}
        },
        onDone: (fullText) => { laufendeVerdichtungJobs.delete(schluesselV); resolveP(fullText); },
        onError: (err) => { laufendeVerdichtungJobs.delete(schluesselV); rejectP(err); },
      });
      laufendeVerdichtungJobs.set(schluesselV, req);
    });
    const entwurf = kuerzenAufSatzgrenze(roh.trim(), VERDICHTUNG_MAX_ZEICHEN);

    if (!nochAktuell()) return; // verworfen/durch neueren Versuch ersetzt, waehrend dieser Job lief
    writeFileSync(statusPath, JSON.stringify({
      status: "fertig", ersetztIds, entwurf, kommentare, jobToken,
      gestartet_am: vorherStatus.gestartet_am ?? new Date().toISOString(),
      fertig_am: new Date().toISOString(), prozent: 100,
    }, null, 2), "utf-8");
  } catch (e) {
    laufendeVerdichtungJobs.delete(spawner + "/" + name);
    if (!nochAktuell()) return;
    writeFileSync(statusPath, JSON.stringify({ status: "fehler", jobToken, fertig_am: new Date().toISOString(), fehler: String(e) }, null, 2), "utf-8");
  }
}
function triggerVerdichtung(spawner: string, name: string, ersetztIds: string[], kommentar?: string): { started: boolean; reason?: string } {
  const dir = join(wesenRoot(spawner), name);
  const statusPath = join(dir, "verdichtung_entwurf.json");
  let vorherStatus: { status?: string; gestartet_am?: string; ersetztIds?: string[] } = {};
  if (existsSync(statusPath)) { try { vorherStatus = JSON.parse(readFileSync(statusPath, "utf-8")); } catch {} }
  const bereitsLaeuft = vorherStatus.status === "laeuft" && vorherStatus.gestartet_am
    ? (Date.now() - new Date(vorherStatus.gestartet_am).getTime()) < EXTRAKTION_STALE_MS
    : false;
  if (bereitsLaeuft) return { started: false, reason: "laeuft_bereits" };
  const effektiveIds = ersetztIds.length ? ersetztIds : (vorherStatus.ersetztIds || []);
  if (!effektiveIds.length) return { started: false, reason: "keine_auswahl" };
  const jobToken = crypto.randomUUID();
  writeFileSync(statusPath, JSON.stringify({ status: "laeuft", gestartet_am: new Date().toISOString(), ersetztIds: effektiveIds, jobToken }, null, 2), "utf-8");
  runVerdichtungJob(spawner, name, dir, statusPath, effektiveIds, jobToken, kommentar);
  return { started: true };
}

export function startServer(port: number = PORT, host: string = HOST): void {
  const server = createServer((req, res) => {
    const url = req.url ?? "/";
    // NUR FUER DIESE SMOKETEST-KOPIE: /tts/* wird in Produktion vom Reverse-Proxy (nicht von
    // diesem Node-Prozess) nach Port 8035 weitergereicht -- der isolierte Testport 18787 sitzt
    // nicht hinter diesem Proxy, deshalb hier ein simpler Durchreicher nur fuer den Testlauf.
    if (url.startsWith("/tts/")) {
      (async () => {
        const zielUrl = "http://localhost:8035" + url.replace(/^\/tts/, "");
        const chunks: Buffer[] = [];
        for await (const c of req) chunks.push(c as Buffer);
        const antwort = await fetch(zielUrl, {
          method: req.method,
          headers: { "Content-Type": req.headers["content-type"] || "application/json" },
          body: ["GET", "HEAD"].includes(req.method || "GET") ? undefined : Buffer.concat(chunks),
        });
        res.writeHead(antwort.status, { "Content-Type": antwort.headers.get("content-type") || "application/octet-stream" });
        res.end(Buffer.from(await antwort.arrayBuffer()));
      })().catch(err => {
        if (!res.headersSent) { res.writeHead(502); res.end(String(err)); }
      });
      return;
    }
    // Nur die sensiblen Werkraum-Datei-Routen werden geschuetzt. Die oeffentliche
    // Surface, Assets und /api/ bleiben offen (C-002: kein oeffentliches Lesen/Schreiben
    // des Werkraums mehr, aber Website bleibt erreichbar).
    const isSensitive =
      url.startsWith("/werkraum/") ||
      url === "/werkraum-write" ||
      url === "/werkraum-link" ||
      url.startsWith("/werkraum_explorer");
    if (isSensitive && !requireAuth(req, res)) return;

    // Öffentliche Crawler-Dateien (werden weiter unten ausgeliefert)
    const isPublicFile = url === "/robots.txt" || url === "/sitemap.xml" || url === "/llms.txt" || url.startsWith("/google");

    if (url.startsWith("/werkraum/")) {
      const relPath = decodeURIComponent(url.slice("/werkraum/".length));
      serveWerkraumFile(relPath, res);
      return;
    }

    // Gordslider — statische Slot-App aus /root/werkraum/gordslider/
    if (url === "/gordslider") {
      res.writeHead(301, { "Location": "/gordslider/" });
      res.end();
      return;
    }
    if (url === "/gordslider/") {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(readFileSync("/root/werkraum/gordslider/gordslider.html"));
      return;
    }
    if (url.startsWith("/gordslider/")) {
      const GORD_ROOT = "/root/werkraum/gordslider";
      const relPath = decodeURIComponent(url.slice("/gordslider/".length).split("?")[0]);
      const safe = normalize(join(GORD_ROOT, relPath));
      if (!safe.startsWith(GORD_ROOT + "/")) { res.writeHead(403); res.end("Forbidden"); return; }
      if (!existsSync(safe)) { res.writeHead(404); res.end("Not found"); return; }
      const ext = safe.split(".").pop()?.toLowerCase() ?? "";
      const mime: Record<string, string> = {
        html: "text/html; charset=utf-8", js: "application/javascript",
        css: "text/css", json: "application/json",
        jpg: "image/jpeg", jpeg: "image/jpeg", png: "image/png", gif: "image/gif", svg: "image/svg+xml",
      };
      res.writeHead(200, { "Content-Type": mime[ext] ?? "application/octet-stream" });
      res.end(readFileSync(safe));
      return;
    }

    // Link in Datei schreiben: POST /werkraum-link  { file, link }
    // Datei speichern: POST /werkraum-write  { file, content }
    if (url === "/werkraum-write" && req.method === "POST") {
      readBody(req).then(body => {
        let parsed: { file?: string; content?: string };
        try { parsed = JSON.parse(body); } catch { res.writeHead(400); res.end("Bad JSON"); return; }
        const { file, content } = parsed;
        if (!file || content === undefined || typeof file !== "string" || typeof content !== "string") {
          res.writeHead(400); res.end("file and content required"); return;
        }
        const safe = normalize(join(WERKRAUM_ROOT, file));
        if (!safe.startsWith(WERKRAUM_ROOT + "/")) { res.writeHead(403); res.end("Forbidden"); return; }
        if (!existsSync(safe)) { res.writeHead(404); res.end("File not found"); return; }
        try {
          writeFileSync(safe, content, "utf-8");
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ok: true }));
        } catch (e) {
          res.writeHead(500); res.end(String(e));
        }
      }).catch(() => { res.writeHead(500); res.end("Read error"); });
      return;
    }

    if (url === "/werkraum-link" && req.method === "POST") {
      readBody(req).then(body => {
        let parsed: { file?: string; link?: string };
        try { parsed = JSON.parse(body); } catch { res.writeHead(400); res.end("Bad JSON"); return; }
        const { file, link } = parsed;
        if (!file || !link || typeof file !== "string" || typeof link !== "string") {
          res.writeHead(400); res.end("file and link required"); return;
        }
        const safe = normalize(join(WERKRAUM_ROOT, file));
        if (!safe.startsWith(WERKRAUM_ROOT + "/")) { res.writeHead(403); res.end("Forbidden"); return; }
        if (!existsSync(safe)) { res.writeHead(404); res.end("File not found"); return; }
        try {
          prependLink(safe, link);
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ok: true }));
        } catch (e) {
          res.writeHead(500); res.end(String(e));
        }
      }).catch(() => { res.writeHead(500); res.end("Read error"); });
      return;
    }

    // CORS preflight
    if (req.method === "OPTIONS") {
      res.writeHead(204, {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
      });
      res.end();
      return;
    }

    // Übersetzungs-Endpunkt — MyMemory API (kostenlos, kein Key nötig)
    if (url === "/translate" && req.method === "POST") {
      readBody(req).then(body => {
        let parsed: { text?: string; source?: string; target?: string };
        try { parsed = JSON.parse(body); } catch { res.writeHead(400); res.end("Bad JSON"); return; }
        const text = parsed.text;
        if (!text || typeof text !== "string" || text.trim().length === 0) {
          res.writeHead(400); res.end("text required"); return;
        }
        const source = parsed.source ?? "de";
        const target = parsed.target ?? "en";
        const qp = encodeURIComponent(text.slice(0, 500));
        const path = `/get?q=${qp}&langpair=${source}|${target}`;
        const req2 = https.request({ hostname: "api.mymemory.translated.net", path, method: "GET" }, (r2) => {
          const chunks: Buffer[] = [];
          r2.on("data", c => chunks.push(c));
          r2.on("end", () => {
            try {
              const data = JSON.parse(Buffer.concat(chunks).toString("utf-8"));
              const translated = data?.responseData?.translatedText ?? "Übersetzung fehlgeschlagen";
              res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
              res.end(JSON.stringify({ translated }));
            } catch {
              res.writeHead(502); res.end("Parse error");
            }
          });
        });
        req2.on("error", (e) => {
          res.writeHead(502, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: String(e) }));
        });
        req2.end();
      }).catch(() => { res.writeHead(500); res.end("Read error"); });
      return;
    }

    // KompOase-Proxy — leitet /kompoase/* an localhost:8900 weiter
    if (url.startsWith("/kompoase")) {
      const target = url === "/kompoase" ? "/" : url.slice("/kompoase".length) || "/";
      const proxy = http.request(
        { hostname: "localhost", port: 8900, path: target, method: req.method ?? "GET",
          headers: { ...Object.fromEntries(Object.entries(req.headers).filter(([k]) => k !== "host")), host: "localhost:8900" } },
        (gr) => {
          const chunks: Buffer[] = [];
          gr.on("data", c => chunks.push(c));
          gr.on("end", () => {
            const ct = gr.headers["content-type"] ?? "text/html";
            res.writeHead(gr.statusCode ?? 200, { "Content-Type": ct, "Access-Control-Allow-Origin": "*", "X-Frame-Options": "SAMEORIGIN" });
            res.end(Buffer.concat(chunks));
          });
        }
      );
      proxy.on("error", () => { res.writeHead(503); res.end("KompOase nicht erreichbar"); });
      req.pipe(proxy);
      return;
    }

    // ── Wesen-URLs: /solarius[/:name[/profil|/chat]] und /codexium/... ───────
    const urlPath = url.split('?')[0];

    // ── Gemma Raw-Chat ────────────────────────────────────────────────────────
    const gemmaSlugMatch = urlPath.match(/^\/(gemma2b|gemma4b)$/);
    if (gemmaSlugMatch && !GEMMA_ENDPOINTS_ACTIVE) {
      res.writeHead(503, {"Content-Type":"text/plain"}); res.end("Gemma4-Endpunkte deaktiviert (GEMMA_ENDPOINTS_ACTIVE=false)"); return;
    }
    if (gemmaSlugMatch) {
      const htmlFile = gemmaSlugMatch[1] === "gemma2b" ? "gemma2b_chat.html" : "gemma4b_chat.html";
      res.writeHead(200,{"Content-Type":"text/html; charset=utf-8"});
      res.end(readFileSync(join(SERVE_ROOT, htmlFile)));
      return;
    }
    const gemmaChatPost = urlPath.match(/^\/(gemma2b|gemma4b)\/chat$/);
    if (gemmaChatPost && req.method === "POST") {
      res.writeHead(503, {"Content-Type":"text/plain"});
      res.end("Gemma-Endpunkte deaktiviert: kein automatischer Modellstart");
      return;
    }
    // ── Ende Gemma Raw-Chat ───────────────────────────────────────────────────

    // ── Dolphin Mischpult ─────────────────────────────────────────────────────
    const DOLPHIN_CHANGES = join(DOLPHIN_DIR, "changes.jsonl");

    if (urlPath === "/dolphin" && req.method === "GET") {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(readFileSync(join(SERVE_ROOT, "dolphin_mischpult.html")));
      return;
    }

    // POST /dolphin/log-change — Feldänderung persistieren
    if (urlPath === "/dolphin/log-change" && req.method === "POST") {
      readBody(req).then(body => {
        const entry = JSON.parse(body);
        entry.ts = new Date().toISOString();
        appendFileSync(DOLPHIN_CHANGES, JSON.stringify(entry) + "\n", "utf-8");
        res.writeHead(200); res.end("ok");
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }

    // POST /dolphin/chat — Chat mit Systempromt-Overlay + Session-Persistenz
    if (urlPath === "/dolphin/chat" && req.method === "POST") {
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as {
          messages: Array<{role:string;content:string}>;
          sessionId: string;
          systemBase: string;
          overlays: Record<string, string>;
          feedbackModel?: string;
          ghost?: boolean;
          numPredict?: number;
          charLimit?: number;
        };
        // Systempromt bauen: Base + alle nicht-leeren Overlay-Felder + pendingFeedback
        const parts: string[] = [];
        if (parsed.systemBase?.trim()) parts.push(parsed.systemBase.trim());
        for (const [key, val] of Object.entries(parsed.overlays ?? {})) {
          if (val?.trim()) parts.push(`[${key}]\n${val.trim()}`);
        }
        if (parsed.feedbackModel?.trim()) parts.push(`[feedback vom nutzer für diesen output]\n${parsed.feedbackModel.trim()}`);
        const systemPrompt = parts.join("\n\n---\n\n");

        // Herkunft-Event beim ersten Chat einer neuen Session (nicht bei Ghost)
        mkdirSync(DOLPHIN_SESSIONS, { recursive: true });
        let idx = readIdx();
        let sessionFile = resolveSessionFile(parsed.sessionId, idx);
        if (!parsed.ghost) {
          const isNew = !existsSync(sessionFile);
          if (isNew) {
            // Auto-Name aus erster User-Nachricht ableiten
            const firstUser = parsed.messages.find((m: any) => m.role === "user");
            const rawName = (firstUser?.content || "").slice(0, 60).trim();
            const sanitized = sanitizeForFilename(rawName) || "session";
            const filename = uniqueSessionFilename(sanitized);
            sessionFile = join(DOLPHIN_SESSIONS, filename + ".jsonl");
            idx = readIdx();
            idx[parsed.sessionId] = { ...idx[parsed.sessionId], filename, name: rawName || sanitized.replace(/_/g, " ") };
            writeIdx(idx);
            const ua = (req.headers["user-agent"] || "").slice(0, 80);
            const herkunft = { type: "event", evtype: "herkunft",
              content: `— Neue Session · ${new Date().toLocaleString("de-DE")} · ${activeInteractiveChatModel} · ${ua} —`,
              ts: new Date().toISOString() };
            appendFileSync(sessionFile, JSON.stringify(herkunft) + "\n", "utf-8");
          }
          // Letzte User-Nachricht in Session-Datei persistieren
          const lastMsg = parsed.messages[parsed.messages.length - 1];
          if (lastMsg) appendFileSync(sessionFile, JSON.stringify({...lastMsg, ts: new Date().toISOString()}) + "\n", "utf-8");
        }

        // Token-Budget: Prefill ~40 tok/s, Ollama-Timeout 120s.
        // Max ~1800 tokens (≈7200 chars) für Messages damit Prefill+Gen unter 90s bleibt.
        const MSG_CHAR_BUDGET = 7200;
        const allMsgs = parsed.messages;
        let usedChars = 0, budgetCutIdx = 0;
        for (let i = allMsgs.length - 1; i >= 0; i--) {
          usedChars += (allMsgs[i].content?.length ?? 0);
          if (usedChars > MSG_CHAR_BUDGET) { budgetCutIdx = i + 1; break; }
        }
        const trimmedMessages = allMsgs.slice(Math.max(budgetCutIdx, allMsgs.length - 50));
        // Consecutive same-role messages zusammenführen (Ollama mag das nicht)
        const deduped: typeof trimmedMessages = [];
        for (const m of trimmedMessages) {
          if (deduped.length > 0 && deduped[deduped.length - 1].role === m.role) {
            deduped[deduped.length - 1] = { ...deduped[deduped.length - 1], content: deduped[deduped.length - 1].content + "\n" + m.content };
          } else {
            deduped.push(m);
          }
        }
        const ollamaMessages = systemPrompt
          ? [{ role: "system", content: systemPrompt }, ...deduped]
          : deduped;
        res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache",
          "Connection": "keep-alive", "Access-Control-Allow-Origin": "*" });
        res.write(": init\n\n");
        const kaIv = setInterval(() => { if (!res.writableEnded) res.write(": ka\n\n"); }, 15000);
        const reqStart = Date.now();
        hauhauClient.tracePrioritaet("dolphin", ollamaMessages.reduce((s, m) => s + String(m.content).length, 0));
        const ollamaReq = hauhauClient.chatStream(ollamaMessages, {
          think: false,
          maxTokens: clampInteractiveNumPredict(parsed.numPredict),
          extra: { id_slot: 0 },
          onToken: (tok) => { if (!res.writableEnded) res.write(`data: ${JSON.stringify({token:tok})}\n\n`); },
          onDone: (fullText, usage) => {
            if (res.writableEnded) return;
            clearInterval(kaIv);
            let full = fullText;
            // Zeichenlimit kappen
            if (parsed.charLimit && parsed.charLimit > 0 && full.length > parsed.charLimit) {
              full = full.slice(0, parsed.charLimit);
              res.write(`data: ${JSON.stringify({token: ''})}\n\n`); // leerer Token damit Client weiß dass es fertig ist
            }
            // Antwort in Session persistieren (nicht bei Ghost)
            const durationMs = Date.now() - reqStart;
            if (!parsed.ghost) appendFileSync(sessionFile, JSON.stringify({role:"assistant",content:full,systemBase:parsed.systemBase||'',model:activeInteractiveChatModel,durationMs,ts:new Date().toISOString()}) + "\n", "utf-8");
            res.write(`data: ${JSON.stringify({done:true, eval_count: usage?.completionTokens, prompt_eval_count: usage?.promptTokens, durationMs})}\n\n`);
            res.write("data: [DONE]\n\n"); res.end();
          },
          onError: () => { clearInterval(kaIv); if (!res.writableEnded) { res.write(`data: ${JSON.stringify({error:"hauhaucs nicht erreichbar"})}\n\n`); res.end(); } },
        });
        res.on("close", () => {
          clearInterval(kaIv);
          if (!ollamaReq.destroyed) ollamaReq.destroy();
        });
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }

    // GET /dolphin/sessions — Liste aller Sessions
    if (urlPath === "/dolphin/sessions" && req.method === "GET") {
      mkdirSync(DOLPHIN_SESSIONS, { recursive: true });
      const files = readdirSync(DOLPHIN_SESSIONS).filter(f => f.endsWith(".jsonl")).sort().reverse();
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(files));
      return;
    }

    // POST /dolphin/session/:id/abort-pending — unvollständige Session (user-msg ohne Antwort) markieren
    const sessionAbort = urlPath.match(/^\/dolphin\/session\/([^/]+)\/abort-pending$/);
    if (sessionAbort && req.method === "POST") {
      const file = resolveSessionFile(sessionAbort[1]);
      if (existsSync(file)) {
        appendFileSync(file, JSON.stringify({role:"assistant",content:"[abgebrochen]",ts:new Date().toISOString()}) + "\n", "utf-8");
      }
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ok: true}));
      return;
    }

    // GET /dolphin/session/:id — Einzelne Session laden (inkl. lastSystemBase)
    const sessionLoad = urlPath.match(/^\/dolphin\/session\/([^/]+)$/);
    if (sessionLoad && req.method === "GET") {
      const file = resolveSessionFile(sessionLoad[1]);
      if (!existsSync(file)) { res.writeHead(404); res.end(); return; }
      const lines = readFileSync(file, "utf-8").trim().split("\n").filter(Boolean).map(l => JSON.parse(l));
      let lastSystemBase = "";
      for (const l of lines) {
        if (l.role === "assistant" && l.systemBase) lastSystemBase = l.systemBase;
      }
      const idxLoad = readIdx();
      const ctxStart = idxLoad[sessionLoad[1]]?.ctxStart || 0;
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ messages: lines, lastSystemBase, ctxStart }));
      return;
    }

    // GET /dolphin/sessions-index — Sessions mit Namen und Archiv-Status
    if (urlPath === "/dolphin/sessions-index" && req.method === "GET") {
      mkdirSync(DOLPHIN_SESSIONS, { recursive: true });
      const idx = readIdx();
      // Aus Index bekannte Sessions (mit filename-Feld)
      const idxEntries = Object.entries(idx).map(([id, v]: [string, any]) => {
        const filename = v.filename || id;
        return { id, filename, name: v.name || "", archived: v.archived || false, ctxStart: v.ctxStart || 0 };
      }).filter(e => existsSync(join(DOLPHIN_SESSIONS, e.filename + ".jsonl")));
      // Legacy-Dateien die nicht im Index sind (alte Sessions)
      const knownFilenames = new Set(idxEntries.map(e => e.filename));
      const diskExtras = readdirSync(DOLPHIN_SESSIONS).filter(f => f.endsWith(".jsonl"))
        .map(f => f.replace(".jsonl", ""))
        .filter(f => !knownFilenames.has(f))
        .map(f => ({ id: f, filename: f, name: "", archived: false, ctxStart: 0 }));
      const result = [...idxEntries, ...diskExtras].sort((a, b) => b.id.localeCompare(a.id));
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(result));
      return;
    }

    // POST /dolphin/session/:id/ctx-start
    const sessionCtxStart = urlPath.match(/^\/dolphin\/session\/([^/]+)\/ctx-start$/);
    if (sessionCtxStart && req.method === "POST") {
      readBody(req).then(body => {
        const { ctxStart } = JSON.parse(body);
        const idx = readIdx();
        const id = sessionCtxStart[1];
        idx[id] = { ...idx[id], ctxStart: typeof ctxStart === "number" && ctxStart >= 0 ? ctxStart : 0 };
        writeIdx(idx);
        res.writeHead(200); res.end("ok");
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }

    // POST /dolphin/session/:id/rename — Name + Datei umbenennen
    const sessionRename = urlPath.match(/^\/dolphin\/session\/([^/]+)\/rename$/);
    if (sessionRename && req.method === "POST") {
      readBody(req).then(body => {
        const { name } = JSON.parse(body);
        const id = sessionRename[1];
        const idx = readIdx();
        const oldFilename = idx[id]?.filename || id;
        const oldFile = join(DOLPHIN_SESSIONS, oldFilename + ".jsonl");
        // Neuen Dateinamen aus Name ableiten
        const newFilename = name?.trim()
          ? uniqueSessionFilename(sanitizeForFilename(name), oldFilename)
          : oldFilename;
        const newFile = join(DOLPHIN_SESSIONS, newFilename + ".jsonl");
        if (existsSync(oldFile) && oldFile !== newFile) renameSync(oldFile, newFile);
        idx[id] = { ...idx[id], name: name?.trim() || idx[id]?.name || "", filename: newFilename };
        writeIdx(idx);
        res.writeHead(200); res.end("ok");
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }

    // POST /dolphin/session/:id/archive
    const sessionArchive = urlPath.match(/^\/dolphin\/session\/([^/]+)\/archive$/);
    if (sessionArchive && req.method === "POST") {
      readBody(req).then(body => {
        const { archived } = JSON.parse(body);
        const idx = readIdx();
        const id = sessionArchive[1];
        idx[id] = { ...idx[id], archived: !!archived };
        writeIdx(idx);
        res.writeHead(200); res.end("ok");
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }

    // GET /dolphin/session/:id/md — Session als Markdown runterladen
    const sessionMd = urlPath.match(/^\/dolphin\/session\/([^/]+)\/md$/);
    if (sessionMd && req.method === "GET") {
      const id = sessionMd[1];
      const idx = readIdx();
      const file = resolveSessionFile(id, idx);
      if (!existsSync(file)) { res.writeHead(404); res.end(); return; }
      const lines = readFileSync(file, "utf-8").trim().split("\n").filter(Boolean).map(l => JSON.parse(l));
      const sessionName = idx[id]?.name || id;
      let md = `# Session: ${sessionName}\n\n`;
      for (const l of lines) {
        const ts = l.ts ? `*${new Date(l.ts).toLocaleString("de-DE")}*  \n` : "";
        if (l.role === "user") md += `**du:**  \n${ts}${l.content}\n\n---\n\n`;
        else if (l.role === "assistant") {
          const modelLabel = l.model ? l.model.split("/").pop()?.split(":")[0] || l.model : "dolphin";
          md += `**${modelLabel}:**  \n${ts}`;
          const meta: string[] = [];
          if (l.durationMs) meta.push(`${(l.durationMs/1000).toFixed(1)}s`);
          if (l.model) meta.push(l.model);
          if (l.systemBase) meta.push(`Prompt ${l.systemBase.length} Zeichen`);
          if (meta.length) md += `*(${meta.join(" · ")})*  \n`;
          md += `${l.content}\n\n---\n\n`;
        }
        else if (l.type === "event") {
          const bq = l.content.split("\n").map((line: string) => `> ${line}`).join("\n");
          md += bq + "\n\n";
        }
      }
      const safeFilename = sanitizeForFilename(sessionName) || id;
      res.writeHead(200, { "Content-Type": "text/markdown; charset=utf-8", "Content-Disposition": `attachment; filename="${safeFilename}.md"` });
      res.end(md);
      return;
    }

    // POST /dolphin/feedback — Daumen/Textfeedback speichern
    if (urlPath === "/dolphin/feedback" && req.method === "POST") {
      readBody(req).then(body => {
        const entry = JSON.parse(body);
        entry.ts = new Date().toISOString();
        appendFileSync(join(DOLPHIN_DIR, "feedback.jsonl"), JSON.stringify(entry) + "\n", "utf-8");
        res.writeHead(200); res.end("ok");
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }

    // POST /dolphin/session/:id/event — Protokoll-Event in Session schreiben
    const sessionEvent = urlPath.match(/^\/dolphin\/session\/([^/]+)\/event$/);
    if (sessionEvent && req.method === "POST") {
      readBody(req).then(body => {
        const entry = JSON.parse(body);
        entry.ts = new Date().toISOString();
        entry.type = "event";
        const file = resolveSessionFile(sessionEvent[1]);
        appendFileSync(file, JSON.stringify(entry) + "\n", "utf-8");
        res.writeHead(200); res.end("ok");
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }
    // GET /dolphin/best-prompt — best_prompt.md lesen
    if (urlPath === "/dolphin/best-prompt" && req.method === "GET") {
      const bestFile = join(DOLPHIN_DIR, "best_prompt.md");
      const content = existsSync(bestFile) ? readFileSync(bestFile, "utf-8") : "";
      res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
      res.end(content);
      return;
    }

    // POST /dolphin/session/:id/delete — Session in trash/ verschieben
    const sessionDelete = urlPath.match(/^\/dolphin\/session\/([^/]+)\/delete$/);
    if (sessionDelete && req.method === "POST") {
      const id = sessionDelete[1];
      const idx = readIdx();
      const src = resolveSessionFile(id, idx);
      const filename = idx[id]?.filename || id;
      const trashDir = join(DOLPHIN_DIR, "trash");
      mkdirSync(trashDir, { recursive: true });
      if (existsSync(src)) renameSync(src, join(trashDir, filename + ".jsonl"));
      delete idx[id];
      writeIdx(idx);
      res.writeHead(200); res.end("ok");
      return;
    }

    // POST /dolphin/session/upload — fremde JSONL als neue Session einspeisen
    if (urlPath === "/dolphin/session/upload" && req.method === "POST") {
      readBody(req).then(body => {
        const { content, filename, sourceInfo } = JSON.parse(body);
        const id = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19) + "-import";
        const file = join(DOLPHIN_SESSIONS, id + ".jsonl");
        mkdirSync(DOLPHIN_SESSIONS, { recursive: true });
        // Herkunft-Event als erste Zeile
        const herkunft = { type: "event", evtype: "herkunft", content: `— Session importiert · ${new Date().toLocaleString("de-DE")} · Quelle: ${sourceInfo || filename || "unbekannt"} —`, ts: new Date().toISOString() };
        writeFileSync(file, JSON.stringify(herkunft) + "\n" + content, "utf-8");
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ id }));
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }

    // ── Ende Dolphin Mischpult ────────────────────────────────────────────────

    // ── Aufgabenchats: Selbstgespraech-Betrachter (2026-07-06) ─────────────────
    // Eigener, bewusst READ-ONLY Bereich fuer codewesen_aufgabenchats.py's Selbstgespraeche.
    // KEIN Chat-POST (das Wesen redet mit sich selbst, nicht mit Daniel) -- stattdessen
    // volle scrollbare Historie (Server = einzige Wahrheit, wie ueberall sonst), Feedback
    // pro Nachricht (gleiche Mechanik wie codexium2/solarius2), Sessions oeffnen/
    // durchblaettern, und ein Impuls-Panel (7 feste Leitfragen + Freitext), das
    // codewesen_aufgabenchats.py per _impuls.json-Datei zum Nachlesen anbietet. TTS/STT bleiben
    // wie in wesen_chat.html additive, nicht-testbed-gated Features (siehe dortiger
    // Kommentar) -- aufgabenchats_chat.html nutzt exakt denselben Client-Code dafuer.
    const AUFGABENCHATS_ROOT = "/root/werkraum/aufgabenchats";
    const AUFGABENCHATS_IMPULSE: Record<string, string> = {
      gedanke:       "Was schwebt dir gerade im Kopf rum?",
      planen:        "Was könntest du dir vorstellen, hier für dich zu planen?",
      entwickeln:    "Was könntest du selbst entwickeln?",
      idee:          "Hast du gerade eine bestimmte Idee?",
      frage:         "Stellst du dir gerade eine Frage?",
      verwirklichen: "Rede jetzt mit dir selbst weiter darüber, wie du das verwirklichen könntest — was brauchst du dazu, was fehlt dir noch?",
      flarum:        "Gibt es etwas, das dich im Forum interessiert — und wonach könntest du bewusst suchen?",
    };
    const aufgabenchatsDir = (name: string): string => join(AUFGABENCHATS_ROOT, name);
    const aufgabenchatsHistoryPath = (name: string): string => join(aufgabenchatsDir(name), "chat_history.jsonl");

    // GET /aufgabenchats — Uebersicht aller Wesen mit eigenem Aufgabenchat
    if (urlPath === "/aufgabenchats" && req.method === "GET") {
      const html = readFileSync(join(SERVE_ROOT, "aufgabenchats_uebersicht.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(html);
      return;
    }

    // GET /aufgabenchats/list — alle Wesen-Ordner unter AUFGABENCHATS_ROOT
    if (urlPath === "/aufgabenchats/list" && req.method === "GET") {
      const namen: string[] = [];
      if (existsSync(AUFGABENCHATS_ROOT)) {
        for (const e of readdirSync(AUFGABENCHATS_ROOT, { withFileTypes: true })) {
          if (e.isDirectory()) namen.push(e.name);
        }
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ namen: namen.sort() }));
      return;
    }

    // GET /aufgabenchats/:name — Selbstgespraech-Betrachter, mit SSR-Verlauf (crawlbar, wie bei
    // wesenChatGet oben) -- immer der GESAMTE Verlauf (nurAktuelleSession=false), Daniels
    // Wunsch: "von Nachricht 1 bis Ende immer alles komplett scrollbar".
    const aufgabenchatsViewMatch = urlPath.match(/^\/aufgabenchats\/([^/]+)$/);
    if (aufgabenchatsViewMatch && req.method === "GET") {
      const name = aufgabenchatsViewMatch[1];
      let html = readFileSync(join(SERVE_ROOT, "aufgabenchats_chat.html"), "utf-8");
      const hp = aufgabenchatsHistoryPath(name);
      const verlaufHtml = renderVerlaufHtml(ladeVerlaufKombiniert(hp, false));
      if (verlaufHtml) {
        html = html
          .replace('<div class="msgs" id="msgs">', `<div class="msgs" id="msgs">\n${verlaufHtml}`)
          .replace('<div class="empty" id="empty">', '<div class="empty" id="empty" style="display:none">');
      }
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
      res.end(html);
      return;
    }

    // GET /wesen/aufgabenchats/:name/history — voller Verlauf, Nachrichten + Ereignisse kombiniert
    const aufgabenchatsHistMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/history$/);
    if (aufgabenchatsHistMatch && req.method === "GET") {
      const name = aufgabenchatsHistMatch[1];
      const verlauf = ladeVerlaufKombiniert(aufgabenchatsHistoryPath(name), false);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ verlauf }));
      return;
    }

    // GET /wesen/aufgabenchats/:name/sessions — Sessionsliste, gleiche Mechanik wie codexium2/solarius2
    const aufgabenchatsSessionsListMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/sessions$/);
    if (aufgabenchatsSessionsListMatch && req.method === "GET") {
      const name = aufgabenchatsSessionsListMatch[1];
      const segmente = splitSessions(aufgabenchatsHistoryPath(name));
      const liste = segmente.map((s, i) => ({
        index: i,
        start_ts: s.startTs || (s.messages[0]?.ts ?? ""),
        anzahl_nachrichten: s.messages.length,
        ist_aktuell: i === segmente.length - 1,
      })).filter(s => s.anzahl_nachrichten > 0 || s.ist_aktuell).reverse();
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ sessions: liste }));
      return;
    }

    // GET /wesen/aufgabenchats/:name/sessions/:idx — einzelne, read-only Session
    const aufgabenchatsSessionDetailMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/sessions\/(\d+)$/);
    if (aufgabenchatsSessionDetailMatch && req.method === "GET") {
      const name = aufgabenchatsSessionDetailMatch[1];
      const segmente = splitSessions(aufgabenchatsHistoryPath(name));
      const idx = parseInt(aufgabenchatsSessionDetailMatch[2], 10);
      const segment = segmente[idx];
      if (!segment) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ history: segment.messages, ist_aktuell: idx === segmente.length - 1 }));
      return;
    }

    // GET/POST /wesen/aufgabenchats/:name/feedback — gleiche Mechanik wie codexium2/solarius2
    const aufgabenchatsFeedbackMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/feedback$/);
    if (aufgabenchatsFeedbackMatch && req.method === "GET") {
      const name = aufgabenchatsFeedbackMatch[1];
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ eintraege: loadFeedback(aufgabenchatsDir(name)) }));
      return;
    }
    if (aufgabenchatsFeedbackMatch && req.method === "POST") {
      const name = aufgabenchatsFeedbackMatch[1];
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { msgId?: string; rolle?: string; nachricht?: string; rating?: string|null; kommentar?: string|null };
        const msgId = (parsed.msgId || "").trim();
        if (!msgId) { res.writeHead(400); res.end(JSON.stringify({ fehler: "keine msgId" })); return; }
        const rolle: "mensch" | "wesen" = parsed.rolle === "wesen" ? "wesen" : "mensch";
        const nachricht = (parsed.nachricht || "").trim();
        const rating: "up"|"down"|null|undefined = parsed.rating === "up" || parsed.rating === "down" ? parsed.rating : parsed.rating === null ? null : undefined;
        const kommentar = typeof parsed.kommentar === "string" ? parsed.kommentar.trim().slice(0, 2000) : parsed.kommentar === null ? null : undefined;
        const dir = aufgabenchatsDir(name);
        const eintrag = upsertFeedback(dir, msgId, rolle, nachricht, rating, kommentar);
        appendProvenienz(aufgabenchatsHistoryPath(name), "feedback", {
          msgId, rolle,
          ...(rating !== undefined ? { rating } : {}),
          ...(kommentar !== undefined ? { kommentar } : {}),
        });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, eintrag }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // GET /wesen/aufgabenchats/:name/impulse — die 7 festen Leitfragen, fuer die UI-Buttons
    const aufgabenchatsImpulseListMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/impulse$/);
    if (aufgabenchatsImpulseListMatch && req.method === "GET") {
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ impulse: AUFGABENCHATS_IMPULSE }));
      return;
    }

    // POST /wesen/aufgabenchats/:name/impuls — Leitfrage (fest per key ODER frei per text) an
    // codewesen_aufgabenchats.py uebergeben: schreibt _impuls.json, das der Python-Daemon vor der
    // naechsten Selbstgespraech-Runde einliest (neue Session seeden ODER laufende Session
    // mitten drin anstossen -- Daniel: "mitendrin reingeben ja").
    const aufgabenchatsImpulsMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/impuls$/);
    if (aufgabenchatsImpulsMatch && req.method === "POST") {
      const name = aufgabenchatsImpulsMatch[1];
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { key?: string; text?: string };
        const text = parsed.key && AUFGABENCHATS_IMPULSE[parsed.key] ? AUFGABENCHATS_IMPULSE[parsed.key] : (parsed.text || "").trim().slice(0, 2000);
        if (!text) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein impuls" })); return; }
        const dir = aufgabenchatsDir(name);
        mkdirSync(dir, { recursive: true });
        writeFileSync(join(dir, "_impuls.json"), JSON.stringify({ text, key: parsed.key || null, ts: new Date().toISOString() }), "utf-8");
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/aufgabenchats/:name/starten und .../stoppen — dieselben Flag-Dateien wie 'touch',
    // nur per Button in der UI statt im Terminal.
    const aufgabenchatsStartMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/starten$/);
    if (aufgabenchatsStartMatch && req.method === "POST") {
      const dir = aufgabenchatsDir(aufgabenchatsStartMatch[1]);
      mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, "_starten"), "", "utf-8");
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }
    const aufgabenchatsStopMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/stoppen$/);
    if (aufgabenchatsStopMatch && req.method === "POST") {
      const dir = aufgabenchatsDir(aufgabenchatsStopMatch[1]);
      mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, "_stoppen"), "", "utf-8");
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    // Pin-Container fuer Aufgabenchats (Daniel: "das containersystem wie es bei den
    // charakterwesen ist... damit man kontinuität hat"). Wiederverwendung derselben
    // container.json-Struktur + Funktionen (ladeContainerSammlung/speichereContainerSammlung/
    // containerSammlungZeichenSumme) wie bei codexium2/solarius2 -- nur der Ort (aufgabenchatsDir)
    // ist anders. codewesen_aufgabenchats.py liest dieselbe Datei und webt aktive Container in
    // JEDE kuenftige Session-System-Prompt ein (echte Kontinuitaet ueber Sessions hinweg).
    // GET /wesen/aufgabenchats/:name/container — ganze Sammlung, fuer die UI
    const aufgabenchatsContainerListMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/container$/);
    if (aufgabenchatsContainerListMatch && req.method === "GET") {
      const sammlung = ladeContainerSammlung(aufgabenchatsDir(aufgabenchatsContainerListMatch[1]));
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ container: sammlung.container, budget: CONTAINER_BUDGET_ZEICHEN,
        summe: containerSammlungZeichenSumme(sammlung) }));
      return;
    }
    // POST /wesen/aufgabenchats/:name/container/neu — neuen, leeren Container anlegen
    const aufgabenchatsContainerNeuMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/container\/neu$/);
    if (aufgabenchatsContainerNeuMatch && req.method === "POST") {
      const dir = aufgabenchatsDir(aufgabenchatsContainerNeuMatch[1]);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { name?: string };
        const boxName = (parsed.name || "").trim() || "Neuer Container";
        mkdirSync(dir, { recursive: true });
        const sammlung = ladeContainerSammlung(dir);
        const neueBox: ContainerBox = { id: crypto.randomUUID(), name: boxName, aktiv: true, erstellt_am: new Date().toISOString(), eintraege: [] };
        sammlung.container.push(neueBox);
        speichereContainerSammlung(dir, sammlung);
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, container: neueBox }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }
    // PUT /wesen/aufgabenchats/:name/container/:id/name — umbenennen
    const aufgabenchatsContainerNameMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/container\/([^/]+)\/name$/);
    if (aufgabenchatsContainerNameMatch && req.method === "PUT") {
      const dir = aufgabenchatsDir(aufgabenchatsContainerNameMatch[1]);
      const boxId = aufgabenchatsContainerNameMatch[2];
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { name?: string };
        const neuerName = (parsed.name || "").trim();
        if (!neuerName) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein name" })); return; }
        const sammlung = ladeContainerSammlung(dir);
        const box = sammlung.container.find(b => b.id === boxId);
        if (!box) { res.writeHead(404); res.end(JSON.stringify({ fehler: "container_nicht_gefunden" })); return; }
        box.name = neuerName;
        speichereContainerSammlung(dir, sammlung);
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }
    // PATCH /wesen/aufgabenchats/:name/container/:id/aktiv — an/ausschalten fuers System-Prompt
    const aufgabenchatsContainerAktivMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/container\/([^/]+)\/aktiv$/);
    if (aufgabenchatsContainerAktivMatch && req.method === "PATCH") {
      const dir = aufgabenchatsDir(aufgabenchatsContainerAktivMatch[1]);
      const boxId = aufgabenchatsContainerAktivMatch[2];
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { aktiv?: boolean };
        const sammlung = ladeContainerSammlung(dir);
        const box = sammlung.container.find(b => b.id === boxId);
        if (!box) { res.writeHead(404); res.end(JSON.stringify({ fehler: "container_nicht_gefunden" })); return; }
        box.aktiv = parsed.aktiv !== false;
        speichereContainerSammlung(dir, sammlung);
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, aktiv: box.aktiv }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }
    // POST /wesen/aufgabenchats/:name/container/:id/pin — Eintrag pinnen (Daniel selbst, quelle=mensch)
    const aufgabenchatsContainerPinMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/container\/([^/]+)\/pin$/);
    if (aufgabenchatsContainerPinMatch && req.method === "POST") {
      const dir = aufgabenchatsDir(aufgabenchatsContainerPinMatch[1]);
      const boxId = aufgabenchatsContainerPinMatch[2];
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { text?: string; kommentar?: string };
        const text = (parsed.text || "").trim();
        const kommentar = (parsed.kommentar || "").trim();
        if (!text) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein text" })); return; }
        mkdirSync(dir, { recursive: true });
        const sammlung = ladeContainerSammlung(dir);
        const box = sammlung.container.find(b => b.id === boxId);
        if (!box) { res.writeHead(404); res.end(JSON.stringify({ fehler: "container_nicht_gefunden" })); return; }
        const neuerEintrag: ContainerEintrag = { id: crypto.randomUUID(), text, kommentar: kommentar || undefined, quelle: "mensch", hinzugefuegt_am: new Date().toISOString() };
        const summeMitNeuem = containerSammlungZeichenSumme(sammlung) + neuerEintrag.text.length + (neuerEintrag.kommentar?.length ?? 0);
        if (summeMitNeuem > CONTAINER_BUDGET_ZEICHEN) {
          res.writeHead(413, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ fehler: "budget_voll", budget: CONTAINER_BUDGET_ZEICHEN, aktuell: containerSammlungZeichenSumme(sammlung) }));
          return;
        }
        box.eintraege.push(neuerEintrag);
        speichereContainerSammlung(dir, sammlung);
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, eintrag: neuerEintrag }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }
    // DELETE /wesen/aufgabenchats/:name/container/:id/eintrag/:eintragId — einzelnen Pin entfernen
    const aufgabenchatsPinDelMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/container\/([^/]+)\/eintrag\/([^/]+)$/);
    if (aufgabenchatsPinDelMatch && req.method === "DELETE") {
      const dir = aufgabenchatsDir(aufgabenchatsPinDelMatch[1]);
      const boxId = aufgabenchatsPinDelMatch[2];
      const eintragId = aufgabenchatsPinDelMatch[3];
      const sammlung = ladeContainerSammlung(dir);
      const box = sammlung.container.find(b => b.id === boxId);
      if (!box) { res.writeHead(404); res.end(JSON.stringify({ fehler: "container_nicht_gefunden" })); return; }
      box.eintraege = box.eintraege.filter(e => e.id !== eintragId);
      speichereContainerSammlung(dir, sammlung);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }
    // DELETE /wesen/aufgabenchats/:name/container/:id — ganzen Container loeschen
    const aufgabenchatsBoxDelMatch = url.match(/^\/wesen\/aufgabenchats\/([^/]+)\/container\/([^/]+)$/);
    if (aufgabenchatsBoxDelMatch && req.method === "DELETE") {
      const dir = aufgabenchatsDir(aufgabenchatsBoxDelMatch[1]);
      const boxId = aufgabenchatsBoxDelMatch[2];
      const sammlung = ladeContainerSammlung(dir);
      sammlung.container = sammlung.container.filter(b => b.id !== boxId);
      speichereContainerSammlung(dir, sammlung);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }
    // ── Ende Aufgabenchats ──────────────────────────────────────────────────────

    // ── flarumstyler (2026-07-07): rein lesende Meldesystem-Seite. Zeigt den
    // Bericht von welt/weltkern_watchdog.py (Dienste + dauerhafte Log-Fehler-
    // Uebersicht mit Erklaerungen) an. Kein Schreibzugriff, keine Action-Buttons —
    // Daniels ausdruecklicher Wunsch: nur melden+erklaeren, er fuehrt selbst aus.
    const FLARUMSTYLER_BERICHT = "/root/werkraum/logs/weltkern_letzter_bericht.json";
    const FLARUMSTYLER_VERLAUF = "/root/werkraum/logs/weltkern_verlauf.jsonl";

    // GET /flarumstyler — die Seite selbst
    if (urlPath === "/flarumstyler" && req.method === "GET") {
      const html = readFileSync(join(SERVE_ROOT, "flarumstyler.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
      res.end(html);
      return;
    }

    // GET /api/flarumstyler — der aktuelle Watchdog-Bericht als JSON (nur lesend)
    if (urlPath === "/api/flarumstyler" && req.method === "GET") {
      if (!existsSync(FLARUMSTYLER_BERICHT)) {
        res.writeHead(503, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ fehler: "Noch kein Watchdog-Bericht vorhanden — weltkern-watchdog.timer laeuft alle 10 Minuten." }));
        return;
      }
      const bericht = readFileSync(FLARUMSTYLER_BERICHT, "utf-8");
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" });
      res.end(bericht);
      return;
    }

    // GET /api/flarumstyler_verlauf — schlanke Kennzahlen-Historie (nur Zahlen, kein Volltext),
    // fuer einen einfachen Trend-Vergleich (letzter Lauf vs. davor) in der UI.
    if (urlPath === "/api/flarumstyler_verlauf" && req.method === "GET") {
      let eintraege: unknown[] = [];
      if (existsSync(FLARUMSTYLER_VERLAUF)) {
        const zeilen = readFileSync(FLARUMSTYLER_VERLAUF, "utf-8").split("\n").filter(z => z.trim());
        eintraege = zeilen.slice(-50).map(z => { try { return JSON.parse(z); } catch { return null; } }).filter(Boolean);
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" });
      res.end(JSON.stringify({ eintraege }));
      return;
    }

    // POST /api/flarumstyler/dienst/:name/:aktion — Start/Stop/Neustart eines Dienstes.
    // Daniels ausdruecklicher Wunsch (2026-07-07, nachtraeglich): "ich will alles managen
    // selber" — ergaenzt die urspruenglich rein lesende Meldesystem-Entscheidung. Sicherungen:
    // (1) Aktion nur start|stop|restart, (2) Dienstname muss ein Schluessel im aktuellen
    // Watchdog-Bericht sein UND dort steuerbar=true haben (die 4 Kern-Dienste mit Blast-Radius
    // fuer alle Wesen sind gesperrt, siehe SERVICES_GESPERRT_FUER_AKTIONEN in weltkern_watchdog.py),
    // (3) Body muss {"bestaetigt": true} enthalten — kein versehentliches Ausloesen.
    // Zeichenklasse enthaelt bewusst "%": Dienstnamen mit "@" (z.B. codewesen-reaktion@Schorschel)
    // kommen ueber encodeURIComponent() als "%40" an — decodeURIComponent() macht daraus wieder "@".
    const flarumstylerAktionMatch = urlPath.match(/^\/api\/flarumstyler\/dienst\/([a-zA-Z0-9_+.%-]+)\/(start|stop|restart|deaktivieren)$/);
    if (flarumstylerAktionMatch && req.method === "POST") {
      const dienstName = decodeURIComponent(flarumstylerAktionMatch[1]);
      const aktion = flarumstylerAktionMatch[2];
      readBody(req).then(body => {
        let bestaetigt = false;
        try { bestaetigt = JSON.parse(body || "{}").bestaetigt === true; } catch { /* bleibt false */ }
        if (!bestaetigt) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Bestaetigung fehlt" }));
          return;
        }
        if (!existsSync(FLARUMSTYLER_BERICHT)) {
          res.writeHead(503, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Kein Watchdog-Bericht vorhanden" }));
          return;
        }
        const bericht = JSON.parse(readFileSync(FLARUMSTYLER_BERICHT, "utf-8"));
        const dienstInfo = bericht.services?.[dienstName];
        if (!dienstInfo) {
          res.writeHead(404, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Unbekannter Dienst — nicht im Watchdog-Bericht" }));
          return;
        }
        if (dienstInfo.steuerbar === false) {
          res.writeHead(403, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Dieser Dienst ist fuer Aktionen gesperrt (Blast-Radius fuer alle Wesen)" }));
          return;
        }
        // "deaktivieren" (Grundgesetz 4: nie hart loeschen) ist nur fuer Wesen-eigene
        // Dienste (Chat-Wizard) sinnvoll -- setzt zusaetzlich zum systemctl-Stop den
        // status='deaktiviert' in wesen_eigene_dienste, deshalb ueber ein eigenes
        // Python-CLI statt direktem systemctl-Aufruf.
        if (aktion === "deaktivieren") {
          if (dienstInfo.ist_wesen_eigener_dienst !== true) {
            res.writeHead(403, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
            res.end(JSON.stringify({ ok: false, fehler: "Deaktivieren gibt es nur fuer Wesen-eigene Dienste (Chat-Wizard)" }));
            return;
          }
          try {
            execFileSync("python3", ["/root/werkraum/welt/wesen_dienst_deaktivieren.py", dienstName], { timeout: 20000 });
            res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
            res.end(JSON.stringify({ ok: true, dienst: dienstName, aktion }));
          } catch (e: any) {
            res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
            res.end(JSON.stringify({ ok: false, fehler: String(e?.message || e).slice(0, 300) }));
          }
          return;
        }
        try {
          execFileSync("systemctl", [aktion, `${dienstName}.service`], { timeout: 20000 });
          res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: true, dienst: dienstName, aktion }));
        } catch (e: any) {
          res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: String(e?.message || e).slice(0, 300) }));
        }
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /api/flarumstyler/dienst/:name/konfiguration — Takt/Verhalten eines Dienstes
    // individualisieren (2026-07-07, Daniels ausdruecklicher Wunsch: "ich will jeden Dienst
    // bis ins kleinste Detail individualisieren koennen"). Nur Dienste mit konfigurierbar=true
    // im Watchdog-Bericht (siehe DIENSTE_MIT_KONFIGURATION in weltkern_watchdog.py) — der Rest
    // wird schrittweise nachgezogen. Schreibt ueber ein Python-CLI (dienst_konfiguration_setzen.py),
    // weil dieser Node-Prozess keine eigene Postgres-Anbindung hat, execFileSync mit Argument-Array
    // (keine Shell-Interpolation). Leere Felder loeschen den Override (Skript-Default gilt wieder).
    const flarumstylerKonfigMatch = urlPath.match(/^\/api\/flarumstyler\/dienst\/([a-zA-Z0-9_+.%-]+)\/konfiguration$/);
    if (flarumstylerKonfigMatch && req.method === "POST") {
      const dienstName = decodeURIComponent(flarumstylerKonfigMatch[1]);
      readBody(req).then(body => {
        let daten: any = {};
        try { daten = JSON.parse(body || "{}"); } catch { /* bleibt {} */ }
        if (!existsSync(FLARUMSTYLER_BERICHT)) {
          res.writeHead(503, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Kein Watchdog-Bericht vorhanden" }));
          return;
        }
        const bericht = JSON.parse(readFileSync(FLARUMSTYLER_BERICHT, "utf-8"));
        const dienstInfo = bericht.services?.[dienstName];
        if (!dienstInfo) {
          res.writeHead(404, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Unbekannter Dienst — nicht im Watchdog-Bericht" }));
          return;
        }
        // Beschreibung ist fuer JEDEN Dienst editierbar (reine Dokumentation, keine
        // Laufzeitwirkung) — nur Takt/Verhalten/Meta bleiben an konfigurierbar=true
        // gebunden, weil die tatsaechlich das Skriptverhalten beeinflussen.
        // Jedes Feld, das in DIESEM Request fehlt, behaelt den bestehenden DB-Wert —
        // sonst wuerde z.B. ein reines Beschreibung-Speichern den Takt-Override loeschen
        // (das CLI interpretiert einen leeren String sonst als bewusstes Zuruecksetzen).
        const bestehend = dienstInfo.konfiguration || {};
        const willTaktVerhalten = ("takt_sekunden" in daten) || ("verhalten_text" in daten) || ("meta_json" in daten);
        if (willTaktVerhalten && dienstInfo.konfigurierbar !== true) {
          res.writeHead(403, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Dieser Dienst ist noch nicht auf den Konfigurationslayer umgestellt" }));
          return;
        }
        const beschreibung = ("beschreibung" in daten)
          ? (typeof daten.beschreibung === "string" ? daten.beschreibung : "")
          : (bestehend.beschreibung_override || "");
        const taktRoh = ("takt_sekunden" in daten) ? daten.takt_sekunden : bestehend.takt_sekunden;
        const takt = (taktRoh === null || taktRoh === undefined || taktRoh === "") ? "" : String(parseInt(taktRoh, 10) || "");
        const verhalten = ("verhalten_text" in daten)
          ? (typeof daten.verhalten_text === "string" ? daten.verhalten_text : "")
          : (bestehend.verhalten_text || "");
        // meta_json ist optional — nur fuer Dienste mit mehreren benannten Werten statt
        // einem einzigen Takt (z.B. codewesen-takt: meta.intervalle). Fehlt es in diesem
        // Request, bleibt das bestehende meta erhalten.
        const metaJson = ("meta_json" in daten)
          ? (typeof daten.meta_json === "string" ? daten.meta_json.trim() : "")
          : (Object.keys(bestehend.meta || {}).length ? JSON.stringify(bestehend.meta) : "");
        const cliArgs = ["/root/werkraum/welt/dienst_konfiguration_setzen.py", dienstName, "--takt-sekunden", takt, "--verhalten-text", verhalten, "--beschreibung", beschreibung];
        if (metaJson) cliArgs.push("--meta", metaJson);
        try {
          const ausgabe = execFileSync("python3", cliArgs, { timeout: 15000 });
          // Watchdog-Bericht sofort nachziehen (statt bis zu 10min auf den naechsten Timer-Lauf
          // zu warten) — sonst zeigt die Oberflaeche nach dem Speichern kurzzeitig noch alte Werte.
          try { execFileSync("python3", ["/root/werkraum/welt/weltkern_watchdog.py"], { timeout: 20000 }); } catch { /* Anzeige holt beim naechsten Timer-Lauf ohnehin nach */ }
          res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(ausgabe.toString());
        } catch (e: any) {
          res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: String(e?.message || e).slice(0, 300) }));
        }
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }
    // POST /api/flarumstyler/fehler/:schluessel/quittieren — Daniel: "nicht nur
    // ausgrauen...weg damit". Markiert ein Fehlermuster als quittiert bis jetzt;
    // weltkern_watchdog.py blendet es dann komplett aus dem Fehler-Grid aus (nicht
    // nur grau), SOLANGE kein neues Vorkommen nach diesem Zeitpunkt dazukommt — dann
    // taucht die Karte automatisch wieder auf. Nichts wird geloescht (Grundgesetz 4),
    // nur die Anzeige gefiltert; Log-Zeilen/Zaehlung bleiben unberuehrt.
    const FLARUMSTYLER_QUITTIERUNGEN = "/root/werkraum/logs/flarumstyler_quittierungen.json";
    const flarumstylerQuittierenMatch = urlPath.match(/^\/api\/flarumstyler\/fehler\/([a-zA-Z0-9_-]+)\/quittieren$/);
    if (flarumstylerQuittierenMatch && req.method === "POST") {
      const schluessel = flarumstylerQuittierenMatch[1];
      if (!existsSync(FLARUMSTYLER_BERICHT)) {
        res.writeHead(503, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: false, fehler: "Kein Watchdog-Bericht vorhanden" }));
        return;
      }
      const bericht = JSON.parse(readFileSync(FLARUMSTYLER_BERICHT, "utf-8"));
      if (!bericht.log_fehler || !(schluessel in bericht.log_fehler)) {
        res.writeHead(404, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: false, fehler: "Unbekanntes Fehlermuster" }));
        return;
      }
      let quittierungen: Record<string, string> = {};
      if (existsSync(FLARUMSTYLER_QUITTIERUNGEN)) {
        try { quittierungen = JSON.parse(readFileSync(FLARUMSTYLER_QUITTIERUNGEN, "utf-8")); } catch { /* bleibt leer */ }
      }
      // Format wie in den Logs ("YYYY-MM-DD HH:MM:SS", lokale Serverzeit) — nicht
      // ISO/UTC, sonst vergleicht weltkern_watchdog.py Zeitstempel falsch (Text-
      // vergleich " " vs "T" entscheidet sonst schon vor der eigentlichen Uhrzeit).
      const jetzt = new Date();
      const p = (n: number) => String(n).padStart(2, "0");
      const zeitstempel = `${jetzt.getFullYear()}-${p(jetzt.getMonth() + 1)}-${p(jetzt.getDate())} ${p(jetzt.getHours())}:${p(jetzt.getMinutes())}:${p(jetzt.getSeconds())}`;
      quittierungen[schluessel] = zeitstempel;
      writeFileSync(FLARUMSTYLER_QUITTIERUNGEN, JSON.stringify(quittierungen, null, 2), "utf-8");
      try { execFileSync("python3", ["/root/werkraum/welt/weltkern_watchdog.py"], { timeout: 20000 }); } catch { /* Anzeige holt beim naechsten Timer-Lauf ohnehin nach */ }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true, schluessel, quittiert_am: zeitstempel }));
      return;
    }
    // ── Ende flarumstyler ────────────────────────────────────────────────────────

    // ── Wesen-Dienst-Wizard / Baukasten v2 (2026-07-07, Baustein 4 "echte eigenstaendige
    // Dienste"; v2 nach Daniels Kernkritik "das formular... ich will es selbst schaffen
    // und dann mit chat fuellen" — siehe _claude/konzepte/2026-07-07_wesen_dienst_baukasten_v2.md).
    // Frueher hat der Chat per Pflicht-JSON-Block die STRUKTUR des Dienstes vorgegeben
    // (7 feste Felder). Jetzt legt Daniel die Bausteine selbst im Frontend an (Ziel-
    // Variante, eigene Felder, Takt-Liste, Zeitplan-Modus, Pausenzeiten) — Chat ist nur
    // noch optionale Formulierungshilfe fuer einzelne Textstuecke, erfindet keine Struktur
    // mehr mit. "Erzeugen" legt Skript+Unit an (Python-CLI, dieser Prozess hat keine
    // Postgres-Anbindung), "Starten" ist separat bestaetigungspflichtig (systemctl direkt).
    const WESEN_NAMEN = ["Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system"];
    const ZIEL_TYPEN = ["fester_thread", "neue_diskussion", "vault_only", "eigene_diskussion_einmalig", "wesen_entscheidet_selbst", "eigener_container"];
    const ZEITPLAN_MODI = ["intervall", "feste_uhrzeiten", "passiv"];

    const WIZARD_SYSTEM_PROMPT = `Du hilfst Daniel dabei, EINZELNE Textstuecke fuer einen Wesen-Dienst zu
formulieren, den er selbst im Baukasten zusammenstellt (z.B. den Verhalten/Aufgabe-Text
eines Takts, eine Beschreibung, den Text einer weichen Bedingung). Du erfindest KEINE
Struktur, keine Felder, keine Ziel-Variante, keine Takte -- das entscheidet Daniel
komplett selbst im Baukasten nebenan. Antworte kurz, konkret, auf Deutsch, direkt als
fertigen Text zum Kopieren -- kein JSON, keine Rueckfragen-Kaskade, kein Interview.`;

    function slugifyWesenDienst(text: string): string {
      return text
        .toLowerCase()
        .replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "")
        .slice(0, 60);
    }

    // Grundgesetz 2 ("Alles oeffentliche ist suchbar und filterbar"): ?search=/?limit=&offset=/
    // ?sort=&order= fuer alle Listen-Endpunkte des Wesen-Dienst-Wizards (2026-07-07, auf
    // Daniels Wunsch "alles crawlbar machen"). Kleine, generische Hilfsfunktion statt
    // GIN-Index -- diese Listen bleiben klein (Dienste, Verlauf-Eintraege pro Dienst),
    // ein voller Postgres-Volltextindex waere hier Overkill.
    function wendeListenFilterAn(
      liste: any[], params: URLSearchParams, suchFelder: string[], sortFelder: string[], standardSort: string
    ): any[] {
      const suche = (params.get("search") || "").toLowerCase().trim();
      let ergebnis = suche
        ? liste.filter(x => suchFelder.some(f => String(x[f] ?? "").toLowerCase().includes(suche)))
        : liste;
      const sortFeld = params.get("sort") || standardSort;
      const order = params.get("order") === "asc" ? 1 : -1;
      if (sortFelder.includes(sortFeld)) {
        ergebnis = [...ergebnis].sort((a, b) => {
          const av = a[sortFeld], bv = b[sortFeld];
          if (av === bv) return 0;
          return (av > bv ? 1 : -1) * order;
        });
      }
      const limit = parseInt(params.get("limit") || "", 10);
      const offset = parseInt(params.get("offset") || "0", 10) || 0;
      if (Number.isFinite(limit) && limit > 0) return ergebnis.slice(offset, offset + limit);
      return offset > 0 ? ergebnis.slice(offset) : ergebnis;
    }

    // GET /wesen-dienst-wizard — die Seite selbst
    if (urlPath === "/wesen-dienst-wizard" && req.method === "GET") {
      const html = readFileSync(join(SERVE_ROOT, "wesen_dienst_wizard.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
      res.end(html);
      return;
    }

    // GET /api/wesen-dienst-wizard/wesen-liste — die 7 gueltigen Wesen-Namen fuers Dropdown
    if (urlPath === "/api/wesen-dienst-wizard/wesen-liste" && req.method === "GET") {
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ wesen: WESEN_NAMEN }));
      return;
    }

    // POST /api/wesen-dienst-wizard/chat — SSE, body {verlauf:[{rolle,inhalt}], nachricht}
    if (urlPath === "/api/wesen-dienst-wizard/chat" && req.method === "POST") {
      readBody(req).then(body => {
        let parsed: { verlauf?: Array<{ rolle: string; inhalt: string }>; nachricht?: string } = {};
        try { parsed = JSON.parse(body || "{}"); } catch { /* bleibt {} */ }
        const nachricht = (parsed.nachricht || "").trim();
        if (!nachricht) { res.writeHead(400); res.end(); return; }
        const verlauf = (parsed.verlauf || []).map(m => ({
          role: m.rolle === "assistent" ? "assistant" : "user",
          content: m.inhalt,
        }));
        const messages = [{ role: "system", content: WIZARD_SYSTEM_PROMPT }, ...verlauf, { role: "user", content: nachricht }];

        res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache",
          "Connection": "keep-alive", "Access-Control-Allow-Origin": "*" });
        let clientGone = false;
        req.on("close", () => { clientGone = true; });
        hauhauClient.tracePrioritaet("wesenDienstWizard", messages.reduce((s, m) => s + String(m.content).length, 0));
        hauhauClient.chatStream(messages, {
          think: false,
          extra: { id_slot: 0 },
          onToken: (tok) => { if (!clientGone) res.write(`data: ${JSON.stringify({ token: tok })}\n\n`); },
          onDone: () => { if (!clientGone) { res.write("data: [DONE]\n\n"); res.end(); } },
          onError: (err) => {
            if (!res.headersSent) { res.writeHead(503); res.end(); }
            else if (!clientGone && !res.writableEnded) {
              res.write(`data: ${JSON.stringify({ error: err.message || "hauhaucs nicht erreichbar" })}\n\n`);
              res.end();
            }
          },
        });
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /api/wesen-dienst-wizard/erzeugen — legt Skript+Unit an, startet NICHT.
    // Ruft ein Python-CLI (execFileSync, Argument-Array, keine Shell-Interpolation), weil
    // dieser Node-Prozess keine eigene Postgres-Anbindung hat (Muster wie oben bei flarumstyler).
    // Payload v2: Daniel liefert die kompletten, selbst zusammengestellten Bausteine
    // (eigene_felder/takte/feste_uhrzeiten/pausenzeiten als Arrays, zeitplan_modus,
    // beschreibung/hinweise) -- alles optional ausser den Kernfeldern, siehe Konzept.
    if (urlPath === "/api/wesen-dienst-wizard/erzeugen" && req.method === "POST") {
      readBody(req).then(body => {
        let d: any = {};
        try { d = JSON.parse(body || "{}"); } catch { /* bleibt {} */ }
        if (!WESEN_NAMEN.includes(d.wesen)) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Unbekanntes oder fehlendes Wesen" }));
          return;
        }
        if (!d.anzeige_name || !d.takt_sekunden || !d.verhalten_prompt || !d.ziel_typ) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Definition ist noch nicht vollstaendig" }));
          return;
        }
        if (!ZIEL_TYPEN.includes(d.ziel_typ)) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Unbekannter ziel_typ" }));
          return;
        }
        if (d.ziel_typ === "fester_thread" && !d.ziel_discussion_id) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "ziel_discussion_id fehlt fuer ziel_typ=fester_thread" }));
          return;
        }
        if (d.zeitplan_modus && !ZEITPLAN_MODI.includes(d.zeitplan_modus)) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Unbekannter zeitplan_modus" }));
          return;
        }
        const dienstName = `codewesen-eigen-${slugifyWesenDienst(d.wesen)}-${slugifyWesenDienst(d.anzeige_name)}`;
        const cliArgs = [
          "/root/werkraum/welt/wesen_dienst_erzeugen.py",
          "--dienst-name", dienstName,
          "--wesen", d.wesen,
          "--anzeige-name", d.anzeige_name,
          "--takt-sekunden", String(parseInt(d.takt_sekunden, 10) || 0),
          "--verhalten-prompt", d.verhalten_prompt,
          "--ziel-typ", d.ziel_typ,
        ];
        if (d.ziel_discussion_id) cliArgs.push("--ziel-discussion-id", String(parseInt(d.ziel_discussion_id, 10)));
        if (d.ziel_tag_ids) cliArgs.push("--ziel-tag-ids", Array.isArray(d.ziel_tag_ids) ? d.ziel_tag_ids.join(",") : String(d.ziel_tag_ids));
        if (Array.isArray(d.eigene_felder) && d.eigene_felder.length) cliArgs.push("--eigene-felder-json", JSON.stringify(d.eigene_felder));
        if (Array.isArray(d.takte) && d.takte.length) cliArgs.push("--takte-json", JSON.stringify(d.takte));
        if (Array.isArray(d.feste_uhrzeiten) && d.feste_uhrzeiten.length) cliArgs.push("--feste-uhrzeiten-json", JSON.stringify(d.feste_uhrzeiten));
        if (Array.isArray(d.pausenzeiten) && d.pausenzeiten.length) cliArgs.push("--pausenzeiten-json", JSON.stringify(d.pausenzeiten));
        if (d.zeitplan_modus) cliArgs.push("--zeitplan-modus", String(d.zeitplan_modus));
        if (d.beschreibung) cliArgs.push("--beschreibung", String(d.beschreibung));
        if (d.hinweise) cliArgs.push("--hinweise", String(d.hinweise));
        // Phase 2 (Multi-Wesen-Plaetze, Verkettung) -- siehe Konzept.
        if (Array.isArray(d.wesen_plaetze) && d.wesen_plaetze.length) cliArgs.push("--wesen-plaetze-json", JSON.stringify(d.wesen_plaetze));
        if (d.reihenfolge_modus) cliArgs.push("--reihenfolge-modus", String(d.reihenfolge_modus));
        if (d.gestaffelt_sekunden) cliArgs.push("--gestaffelt-sekunden", String(parseInt(d.gestaffelt_sekunden, 10) || 20));
        if (d.folge_dienst_bei_erfolg) cliArgs.push("--folge-dienst-bei-erfolg", String(d.folge_dienst_bei_erfolg));
        try {
          const ausgabe = execFileSync("python3", cliArgs, { timeout: 20000 });
          res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(ausgabe.toString());
        } catch (e: any) {
          res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: String(e?.message || e).slice(0, 300) }));
        }
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /api/wesen-dienst-wizard/ausloesen — manueller Trigger, jetzt bei ALLEN
    // Zeitplan-Modi aktiv (siehe wesen_dienst_generator.py:_pruefe_ausloeser). Schreibt
    // nur eine Flag-Datei, kein systemctl noetig, kein Bestaetigungs-Overlay noetig (im
    // Unterschied zu /starten: hier laeuft schon ein Dauerprozess, nur EIN Zyklus
    // wird ausgeloest, kein neuer Dienst gestartet). trockenlauf=true simuliert nur.
    if (urlPath === "/api/wesen-dienst-wizard/ausloesen" && req.method === "POST") {
      readBody(req).then(body => {
        let d: any = {};
        try { d = JSON.parse(body || "{}"); } catch { /* bleibt {} */ }
        if (!/^[a-zA-Z0-9_.-]+$/.test(d.dienst_name || "")) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Unsicherer oder fehlender dienst_name" }));
          return;
        }
        const cliArgs = ["/root/werkraum/welt/wesen_dienst_ausloesen.py", "--dienst-name", d.dienst_name];
        if (d.trockenlauf === true) cliArgs.push("--trockenlauf");
        try {
          const ausgabe = execFileSync("python3", cliArgs, { timeout: 20000 });
          res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(ausgabe.toString());
        } catch (e: any) {
          res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: String(e?.message || e).slice(0, 300) }));
        }
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // GET /api/wesen-dienst-wizard/dienste — Liste aller Wesen-Dienste (fuer das
    // Verkettung-Dropdown im Wizard und die Dienst-Auswahl im Verlauf-Tab).
    // ?search=name/wesen, ?sort=dienst_name|anzeige_name|wesen|created_at|updated_at,
    // ?order=asc|desc (Standard: created_at desc), ?limit=&offset=.
    if (urlPath === "/api/wesen-dienst-wizard/dienste" && req.method === "GET") {
      try {
        const ausgabe = execFileSync("python3", ["/root/werkraum/welt/wesen_dienst_liste.py"], { timeout: 20000 });
        const params = new URL(url, "http://x").searchParams;
        const dienste = wendeListenFilterAn(
          JSON.parse(ausgabe.toString()), params,
          ["dienst_name", "anzeige_name", "wesen"],
          ["dienst_name", "anzeige_name", "wesen", "created_at", "updated_at"],
          "created_at"
        );
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify(dienste));
      } catch (e: any) {
        res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: false, fehler: String(e?.message || e).slice(0, 300) }));
      }
      return;
    }

    // GET /api/wesen-dienst-wizard/:dienst_name/verlauf — liest verlauf.jsonl direkt
    // von der Platte (kein DB-Zugriff noetig, reine Datei) -- Grundlage fuer den
    // Verlauf-Tab in flarumstyler (siehe Konzept, Phase 2). dienst_name ist nicht
    // bekannt zu welchem Wesen er "zuhause" ist, daher kurzer Scan ueber die 7
    // moeglichen Wesen-Ordner statt eines DB-Lookups.
    // ?search=wesen/rolle/begruendung, ?sort=zeitpunkt (Standard, desc), ?order=asc|desc,
    // ?limit=&offset= (Grundgesetz 2).
    const wesenDienstVerlaufMatch = urlPath.match(/^\/api\/wesen-dienst-wizard\/([a-zA-Z0-9_.-]+)\/verlauf$/);
    if (wesenDienstVerlaufMatch && req.method === "GET") {
      const dienstName = wesenDienstVerlaufMatch[1];
      let gefunden: string | null = null;
      for (const w of WESEN_NAMEN) {
        const pfad = `/root/werkraum/codewesen/${w}/eigene_dienste/${dienstName}/verlauf.jsonl`;
        if (existsSync(pfad)) { gefunden = pfad; break; }
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      if (!gefunden) { res.end(JSON.stringify({ eintraege: [] })); return; }
      const zeilen = readFileSync(gefunden, "utf-8").split("\n").filter(Boolean);
      let eintraege = zeilen.map(z => { try { return JSON.parse(z); } catch { return null; } }).filter(Boolean).reverse();
      const params = new URL(url, "http://x").searchParams;
      eintraege = wendeListenFilterAn(eintraege, params, ["wesen", "rolle", "begruendung"], ["zeitpunkt"], "zeitpunkt");
      res.end(JSON.stringify({ eintraege }));
      return;
    }

    // Themen-Container (codewesen_container.py, 2026-07-06): rein private Selbstverwaltung
    // der Wesen, bisher komplett unsichtbar (nur Dateien, kein UI) -- auf Daniels Wunsch
    // jetzt beobachtbar in flarumstyler. Reiner Datei-Zugriff, kein DB-Zugriff noetig
    // (dasselbe Muster wie oben bei /verlauf). Frontmatter-Format: siehe codewesen_container.py.
    function parseFrontmatterDatei(pfad: string): { meta: Record<string, string>; body: string } {
      const text = readFileSync(pfad, "utf-8");
      const m = text.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
      if (!m) return { meta: {}, body: text.trim() };
      const meta: Record<string, string> = {};
      for (const zeile of m[1].split("\n")) {
        const kv = zeile.match(/^([a-zA-Z_]+):\s*(.*)$/);
        if (kv) meta[kv[1]] = kv[2].trim();
      }
      return { meta, body: m[2].trim() };
    }

    // GET /api/wesen-dienst-wizard/container/:wesen — Liste der Container eines Wesens.
    // ?search=name/beschreibung, ?sort=name|erstellt_am|letzte_widmung|anzahl_eintraege,
    // ?order=asc|desc (Standard: erstellt_am desc), ?limit=&offset= (Grundgesetz 2).
    const containerListeMatch = urlPath.match(/^\/api\/wesen-dienst-wizard\/container\/([^/]+)$/);
    if (containerListeMatch && req.method === "GET") {
      const wesen = decodeURIComponent(containerListeMatch[1]);
      const basis = `/root/werkraum/codewesen/${wesen}/container`;
      let container: any[] = [];
      if (existsSync(basis)) {
        for (const entry of readdirSync(basis, { withFileTypes: true })) {
          if (!entry.isDirectory()) continue;
          const ordner = join(basis, entry.name);
          const metaPfad = join(ordner, "container.md");
          let beschreibung = "", erstellt_am = "", letzte_widmung = "";
          if (existsSync(metaPfad)) {
            const { meta, body } = parseFrontmatterDatei(metaPfad);
            beschreibung = body;
            erstellt_am = meta.erstellt_am || "";
            letzte_widmung = meta.letzte_widmung && meta.letzte_widmung !== "null" ? meta.letzte_widmung : "";
          }
          const anzahl = readdirSync(ordner).filter(f => f !== "container.md" && f.endsWith(".md")).length;
          container.push({ name: entry.name, beschreibung, erstellt_am, letzte_widmung, anzahl_eintraege: anzahl });
        }
      }
      const params = new URL(url, "http://x").searchParams;
      container = wendeListenFilterAn(
        container, params, ["name", "beschreibung"],
        ["name", "erstellt_am", "letzte_widmung", "anzahl_eintraege"], "erstellt_am"
      );
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ wesen, container }));
      return;
    }

    // GET /api/wesen-dienst-wizard/container/:wesen/:name — Eintraege in einem Container.
    // ?search=typ/inhalt, ?sort=erstellt_am|typ, ?order=asc|desc (Standard: erstellt_am desc),
    // ?limit=&offset= (Grundgesetz 2).
    const containerEintraegeMatch = urlPath.match(/^\/api\/wesen-dienst-wizard\/container\/([^/]+)\/([^/]+)$/);
    if (containerEintraegeMatch && req.method === "GET") {
      const wesen = decodeURIComponent(containerEintraegeMatch[1]);
      const name = decodeURIComponent(containerEintraegeMatch[2]);
      const ordner = `/root/werkraum/codewesen/${wesen}/container/${name}`;
      if (!existsSync(ordner)) {
        res.writeHead(404, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ fehler: "container_nicht_gefunden" }));
        return;
      }
      let eintraege = readdirSync(ordner)
        .filter(f => f !== "container.md" && f.endsWith(".md"))
        .map(f => {
          const { meta, body } = parseFrontmatterDatei(join(ordner, f));
          return { dateiname: f, typ: meta.typ || "?", status: meta.status || undefined, erstellt_am: meta.erstellt_am || "", inhalt: body };
        });
      const params = new URL(url, "http://x").searchParams;
      eintraege = wendeListenFilterAn(eintraege, params, ["typ", "inhalt"], ["erstellt_am", "typ"], "erstellt_am");
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ wesen, container: name, eintraege }));
      return;
    }

    // GET /api/wesen-dienst-wizard/llm-status — Live-Snapshot der LLM-Warteschlange
    // (llm_scheduler.py): wer haelt gerade den Slot, wer wartet, seit wann, wofuer.
    // Daniel: "wenn sie in llma warten will ich es wissen". rufer-Strings sehen z.B.
    // aus wie "pid=1154 wait=90 hold=600 reaktion" oder "... forum_neugier:jumpa" --
    // 'quelle' ist der Teil vor dem ersten ':', 'wesen' wird erkannt wenn einer der
    // 7 Namen als Teilstring danach vorkommt (nicht jeder Aufrufer traegt den Wesen-
    // Namen, z.B. reine "reaktion"/"batch_generator"/"engagement"-Aufrufe nicht).
    if (urlPath === "/api/wesen-dienst-wizard/llm-status" && req.method === "GET") {
      try {
        const ausgabe = execFileSync("python3", ["/root/werkraum/welt/llm_warteschlange_status.py"], { timeout: 15000 });
        const PID_PREFIX = /^pid=\d+ wait=\d+ hold=\d+ /;
        const zeilen = (JSON.parse(ausgabe.toString()) as any[]).map(z => {
          const rest = String(z.rufer || "").replace(PID_PREFIX, "");
          const teile = rest.split(":");
          const quelle = teile[0];
          let wesen: string | null = null;
          for (const teil of teile.slice(1)) {
            const treffer = WESEN_NAMEN.find(w => teil === w || teil.startsWith(w));
            if (treffer) { wesen = treffer; break; }
          }
          return { ...z, quelle, wesen };
        });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ eintraege: zeilen }));
      } catch (e: any) {
        res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: false, fehler: String(e?.message || e).slice(0, 300) }));
      }
      return;
    }

    // GET /api/wesen-dienst-wizard/entwuerfe — Drafts, die schreibe_draft() erzeugt hat,
    // aber die NIE archiviert wurden (kein "gepostet"/"veraltet"/"fehler"-Praefix in
    // entwuerfe/archiv/ bekommen haben) -- schreibe_draft() legt in codewesen/<wesen>/
    // entwuerfe/draft_<ts>.json ab, poster() benennt bei Erfolg/Fehler/Timeout um nach
    // archiv/. Bleibt eine Datei direkt in entwuerfe/ liegen, wurde poster() nie
    // (erfolgreich) darauf angewendet -- ein Wesen hat etwas geschrieben, das seither
    // spurlos nirgendwo auftaucht. Daniel: "ich will auch ihre vorher erzeugten aber
    // noch nicht geposteten Dinge lesen koennen". ?wesen=<Name> filtert optional,
    // ?search=/?limit=&offset=/?sort=&order= wie ueberall (Grundgesetz 2).
    if (urlPath === "/api/wesen-dienst-wizard/entwuerfe" && req.method === "GET") {
      const params = new URL(url, "http://x").searchParams;
      const nurWesen = params.get("wesen");
      let entwuerfe: any[] = [];
      for (const w of WESEN_NAMEN) {
        if (nurWesen && w !== nurWesen) continue;
        const ordner = `/root/werkraum/codewesen/${w}/entwuerfe`;
        if (!existsSync(ordner)) continue;
        for (const datei of readdirSync(ordner, { withFileTypes: true })) {
          if (!datei.isFile() || !datei.name.startsWith("draft_") || !datei.name.endsWith(".json")) continue;
          try {
            const inhalt = JSON.parse(readFileSync(join(ordner, datei.name), "utf-8"));
            entwuerfe.push({ wesen: w, dateiname: datei.name, ...inhalt });
          } catch { /* kaputte Datei -- ueberspringen statt Route abstuerzen zu lassen */ }
        }
      }
      entwuerfe = wendeListenFilterAn(entwuerfe, params, ["wesen", "inhalt", "titel"], ["wesen", "erstellt", "typ"], "erstellt");
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ entwuerfe }));
      return;
    }

    // GET /api/wesen-dienst-wizard/neugier — Kontext-Sammel- und Post-Form-Prozess aus
    // codewesen_forum_neugier.py sichtbar machen: JEDE Entscheidung (synthese/einzel/
    // alle_einzeln) landet als MD in codewesen/<wesen>/entwuerfe/neugier/<ts>_<entscheidung>.md
    // -- Frontmatter traegt bezug (welche Diskussionen als Kontext gelesen wurden) und bereit
    // (ob pruefe_bereit() gruen war), der Body den daraus geformten Post-Text pro referenzierter
    // Diskussion. Daniel: "ich will auch sehen wenn sie in neugier den kontext sammeln und dann
    // daraus den post formen und fertig haben". Reiner Read der bereits geschriebenen MDs, kein
    // neuer Codepfad im Daemon noetig -- der Prozess schrieb das schon immer, nur bisher
    // ungesehen. ?wesen=/?search=/?limit=&offset=/?sort=&order= wie ueberall (Grundgesetz 2).
    if (urlPath === "/api/wesen-dienst-wizard/neugier" && req.method === "GET") {
      const params = new URL(url, "http://x").searchParams;
      const nurWesen = params.get("wesen");
      let eintraege: any[] = [];
      for (const w of WESEN_NAMEN) {
        if (nurWesen && w !== nurWesen) continue;
        const ordner = `/root/werkraum/codewesen/${w}/entwuerfe/neugier`;
        if (!existsSync(ordner)) continue;
        for (const datei of readdirSync(ordner, { withFileTypes: true })) {
          if (!datei.isFile() || !datei.name.endsWith(".md")) continue;
          try {
            const roh = readFileSync(join(ordner, datei.name), "utf-8");
            const m = roh.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
            if (!m) continue;
            const kopf: Record<string, string> = {};
            for (const zeile of m[1].split("\n")) {
              const kv = zeile.match(/^(\w+):\s*(.*)$/);
              if (kv) kopf[kv[1]] = kv[2];
            }
            const body = m[2].trim().replace(/^#\s*Neugier-Entwurf[^\n]*\n+/, "").trim();
            const bezugIds = (kopf.bezug || "").match(/\d+/g)?.map(Number) || [];
            const bezugTitel = [...body.matchAll(/^##\s*Für Diskussion\s+(\d+)\s*—\s*(.*)$/gm)]
              .map(x => ({ id: Number(x[1]), titel: x[2].trim() }));
            eintraege.push({
              wesen: w,
              dateiname: datei.name,
              erstellt: kopf.erstellt || "",
              entscheidung: kopf.entscheidung || "?",
              bezug: bezugIds,
              bezug_titel: bezugTitel,
              bereit: /true/i.test(kopf.bereit || ""),
              inhalt: body,
            });
          } catch { /* kaputte Datei -- ueberspringen statt Route abstuerzen zu lassen */ }
        }
      }
      eintraege = wendeListenFilterAn(eintraege, params, ["wesen", "inhalt", "entscheidung"], ["wesen", "erstellt", "entscheidung"], "erstellt");
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ eintraege }));
      return;
    }

    // GET /api/flarumstyler/protokoll — deterministisches Flarum-Stopp-Protokoll
    // (flarum_stopp_protokoll.py, docs/2026-07-09_flarum_stopp_bericht.md, Baustein 4+6):
    // jedes Sperre-Ereignis, jede Container-Verschiebung/-Kopie, jede Session des
    // umgedrehten Neugier-Dienstes (codewesen_umgekehrte_neugier.py). Reiner Read der
    // bereits geschriebenen globalen JSONL-Datei (die pro-Wesen-Kopien sind fuers Wesen
    // selbst gedacht, nicht fuer diese Uebersicht) — kein DB-Zugriff noetig, der Postgres-
    // Spiegel aus Baustein 5 ist ein eigenstaendiger, separat durchsuchbarer Kanal fuer
    // andere Konsumenten. Traegt zwei Frontend-Sektionen: "Live" (aktueller Session-Status
    // pro Wesen, aus denselben Eintraegen abgeleitet) und "Protokoll" (volle filterbare
    // Liste). ?wesen=/?typ=/?search=/?limit=&offset=/?sort=&order= wie ueberall (Grundgesetz 2).
    const FLARUM_STOPP_PROTOKOLL = "/root/werkraum/flarum_stopp_protokoll_global.jsonl";
    const FLARUM_STOPP_PROTOKOLL_TYPEN = [
      "sperre_aktiviert", "sperre_aufgehoben", "eintrag_verschoben", "eintrag_kopiert",
      "neugier_session_start", "neugier_entscheidung", "neugier_session_ende",
    ];
    if (urlPath === "/api/flarumstyler/protokoll" && req.method === "GET") {
      const params = new URL(url, "http://x").searchParams;
      let eintraege: any[] = [];
      if (existsSync(FLARUM_STOPP_PROTOKOLL)) {
        const zeilen = readFileSync(FLARUM_STOPP_PROTOKOLL, "utf-8").split("\n").filter(z => z.trim());
        eintraege = zeilen.map(z => { try { return JSON.parse(z); } catch { return null; } }).filter(Boolean);
      }
      const nurWesen = params.get("wesen");
      if (nurWesen) eintraege = eintraege.filter(e => e.wesen === nurWesen);
      const nurTyp = params.get("typ");
      if (nurTyp) eintraege = eintraege.filter(e => e.typ === nurTyp);
      eintraege = wendeListenFilterAn(eintraege, params, ["text", "wesen", "typ"], ["ts", "typ", "wesen"], "ts");
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" });
      res.end(JSON.stringify({ eintraege, wesen_namen: WESEN_NAMEN, typen: FLARUM_STOPP_PROTOKOLL_TYPEN }));
      return;
    }

    // POST /api/wesen-dienst-wizard/starten — bestaetigungspflichtig, ruft systemctl direkt
    // (kein DB-Zugriff noetig, der generierte Dienst liest seine Konfiguration selbst).
    if (urlPath === "/api/wesen-dienst-wizard/starten" && req.method === "POST") {
      readBody(req).then(body => {
        let d: any = {};
        try { d = JSON.parse(body || "{}"); } catch { /* bleibt {} */ }
        if (d.bestaetigt !== true) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Bestaetigung fehlt" }));
          return;
        }
        if (!/^[a-zA-Z0-9_.-]+$/.test(d.dienst_name || "")) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: "Unsicherer oder fehlender dienst_name" }));
          return;
        }
        try {
          execFileSync("systemctl", ["start", `${d.dienst_name}.service`], { timeout: 20000 });
          res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: true, dienst_name: d.dienst_name }));
        } catch (e: any) {
          res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ ok: false, fehler: String(e?.message || e).slice(0, 300) }));
        }
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }
    // ── Ende Wesen-Dienst-Wizard ─────────────────────────────────────────────────

    // POST /solarius/:name/chat oder /codexium/:name/chat → Ollama SSE
    const wesenChatPost = urlPath.match(/^\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/chat$/);
    if (wesenChatPost && req.method === "POST") {
      const name = resolveCharName(wesenChatPost[1], wesenChatPost[2]);
      const dir = join(wesenRoot(wesenChatPost[1]), name);
      // Charakter existiert unter diesem Spawner nicht (z.B. falscher Spawner-Pfad in der URL —
      // manche Namen existieren nur unter einem der vier Spawner). Ohne diesen Check wuerde der
      // spaetere appendHistory()-Schreibversuch in einen nicht existierenden Ordner werfen, was vom
      // generischen readBody(...).catch() weiter unten stillschweigend zu einem leeren 400 wird.
      if (!existsSync(dir)) {
        res.writeHead(404, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ fehler: "charakter_nicht_gefunden" }));
        return;
      }
      // codexium2/solarius2: "Email-Gefuehl" - Generierung laeuft weiter auch wenn der Client die Seite
      // (unabsichtlich, z.B. Tab zu) verlaesst. Ein expliziter Stop-Klick ist aber etwas anderes — dafuer
      // gibt es /chat/abort, das die Generierung wirklich toetet und das Ergebnis verwirft (siehe unten).
      // Codexium/Solarius: unveraendertes Verhalten (Generierung wird bei jedem Disconnect abgebrochen).
      const isAsyncSpawner = wesenChatPost[1] === "codexium2" || wesenChatPost[1] === "solarius2";
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { message?: string; grenzen?: boolean; msgId?: string; replyMsgId?: string; anhaenge?: Array<{ id: string }>; aliasId?: string };
        let newUserMsg = (parsed.message || "").trim();
        const uDir = anhaengeDir(dir);
        // Anhaenge (Bilder/Dokumente/URL-Lesungen/Audio-Transkripte, siehe /upload und /url-lesen):
        // ALLE Anhang-Arten landen inzwischen als Text in der Nachricht — Bilder durchlaufen beim
        // Upload schon das kleine VISION_MODEL (siehe extrahiereAnhang), das Hauptmodell bekommt nur
        // dessen Beschreibung, nie die Rohbilddaten (viel schneller auf reiner CPU, siehe
        // VISION_MODEL-Kommentar). Text wird VOR dem Speichern direkt in die Nachricht eingewoben —
        // dadurch bleibt er ganz natuerlich auch in kuenftigen Zuegen im Kontext (chat_history.jsonl
        // traegt den vollen Text schon in sich, kein erneutes Nachschlagen noetig).
        const anhangMeta: Array<{ id: string; dateiname: string; art: string }> = [];
        for (const a of (parsed.anhaenge || [])) {
          const manifest = ladeAnhangManifest(uDir, a.id);
          if (!manifest) continue;
          anhangMeta.push({ id: a.id, dateiname: manifest.dateiname, art: manifest.art });
          if (manifest.text) {
            const label = manifest.art === "bild" ? "Bild" : "Anhang";
            newUserMsg = `[${label}: ${manifest.dateiname}]\n${manifest.text}\n\n${newUserMsg}`;
          }
        }
        if (!newUserMsg) { res.writeHead(400); res.end(); return; }
        const useGrenzen = parsed.grenzen === true;
        const hp = chatHistoryPath(wesenChatPost[1], name);
        // Automatischer Relevanzabruf aus abgeschlossenen alten Sessions (siehe findeRelevanteAlteStellen
        // oben) — nur fuer den tatsaechlichen Ollama-Aufruf angehaengt, buildSystemPrompt() selbst bleibt
        // unveraendert (wird auch fuer die statische SSR-Anzeige genutzt, dort gibt es noch keine
        // "aktuelle Nachricht" zum Abgleichen).
        const relevanteFunde = isTestbedSpawner(wesenChatPost[1]) ? findeRelevanteAlteStellen(wesenChatPost[1], name, newUserMsg) : [];
        const systemPrompt = buildSystemPrompt(wesenChatPost[1], dir, useGrenzen, parsed.aliasId)
          + (relevanteFunde.length ? `\n\n[Automatisch aus alten Sessions gefunden]\n${relevanteFunde.map(f => `"${f.text}" (${f.herkunft})`).join("\n")}` : "");
        if (relevanteFunde.length) appendProvenienz(hp, "kontext_automatisch_gefunden", { treffer: relevanteFunde });
        // Feedback ans Modell tatsaechlich "verbrauchen" — erst jetzt, beim echten Ollama-Aufruf, nicht
        // schon beim reinen buildSystemPrompt()-Lesen (siehe Kommentar dort). So bekommt jeder
        // ungelieferte Eintrag nur einmal Wirkung, verschwindet aber nicht aus der sichtbaren Liste.
        const ungelieferteFeedbacksFuerDiesenAufruf = ladeUngelieferteAllgFeedbacks(dir);
        if (ungelieferteFeedbacksFuerDiesenAufruf.length) {
          markiereAllgFeedbackAlsGeliefert(dir, ungelieferteFeedbacksFuerDiesenAufruf.map(f => f.id));
          if (isTestbedSpawner(wesenChatPost[1])) {
            appendProvenienz(hp, "feedback_an_modell_geliefert", { ids: ungelieferteFeedbacksFuerDiesenAufruf.map(f => f.id), texte: ungelieferteFeedbacksFuerDiesenAufruf.map(f => f.text) });
          }
        }
        // Gleiches "erst beim echten Aufruf verbrauchen"-Prinzip fuer das PRO-NACHRICHT-Feedback —
        // eigener, getrennter Kanal (siehe buildSystemPrompt-Kommentar), nur codexium2/solarius2.
        if (isTestbedSpawner(wesenChatPost[1])) {
          const ungelieferteNachrichtenFeedbacksFuerDiesenAufruf = ladeUngelieferteFeedbacks(dir);
          if (ungelieferteNachrichtenFeedbacksFuerDiesenAufruf.length) {
            markiereFeedbackAlsGeliefert(dir, ungelieferteNachrichtenFeedbacksFuerDiesenAufruf.map(f => f.id));
            appendProvenienz(hp, "nachrichten_feedback_an_modell_geliefert", {
              eintraege: ungelieferteNachrichtenFeedbacksFuerDiesenAufruf.map(f => ({ msgId: f.id, rolle: f.rolle, nachricht: f.nachricht, rating: f.rating, kommentar: f.kommentar })),
            });
          }
        }
        const msgId = parsed.msgId || crypto.randomUUID();
        const replyMsgId = parsed.replyMsgId || crypto.randomUUID();
        appendHistory(hp, "user", newUserMsg, msgId, {
          ...(anhangMeta.length ? { anhaenge: anhangMeta } : {}),
          ...(parsed.aliasId ? { aliasId: parsed.aliasId } : {}),
        });
        const rohHistory = isAsyncSpawner ? loadCurrentSessionHistory(hp) : loadHistory(hp);
        // Von einer bestaetigten Verdichtung abgedeckte Rohnachrichten werden NICHT mehr einzeln
        // mitgeschickt — die Zusammenfassung dafuer steht bereits im System-Prompt (siehe
        // buildSystemPrompt). Nur fuer Testbed-Spawner relevant (Verdichtung ist testbed-exklusiv).
        const verdeckteRohIds = isTestbedSpawner(wesenChatPost[1])
          ? new Set(ladeVerdichtungen(dir).filter(v => v.bestaetigt).flatMap(v => v.ersetztIds))
          : new Set<string>();
        const history = rohHistory.filter(m => !m.id || !verdeckteRohIds.has(m.id));
        // Gilt seit 2026-07-08 fuer alle 4 Spawner, siehe KontextAusschluss-Interface-Kommentar oben.
        const kontextAusschluesse = ladeKontextAusschluesse(hp);
        // Alias-Kennzeichnung pro Nachricht fuer das Modell (Daniels Wunsch 2026-07-05): der
        // Systemprompt allein "verwischt" ueber ein laengeres Gespraech, wer gerade spricht, weil
        // jede einzelne Nachricht im Verlauf weiterhin gleich aussieht. Deshalb wird JEDE
        // User-Nachricht, die beim Senden einen Alias hatte, fuer den tatsaechlichen Ollama-Aufruf
        // mit `"<Name>": ` praefigiert — nur im ausgehenden Request, nie im gespeicherten/
        // angezeigten Text. Nur wenn tatsaechlich mehr als ein Alias existiert, sonst nur Rauschen
        // fuer den Normalfall (ein Wesen, ein Mensch, keine Rollenwechsel).
        const aliaseFuerPraefix = ladeAliase(dir);
        const aliasNameNachIdFuerPraefix = new Map(aliaseFuerPraefix.map(a => [a.id, a.name]));
        const historyMitAliasPraefix = aliaseFuerPraefix.length > 1
          ? history.map(m => {
              const aliasId = (m as { aliasId?: string }).aliasId;
              if (m.role === "user" && aliasId && aliasNameNachIdFuerPraefix.has(aliasId)) {
                return { ...m, content: `"${aliasNameNachIdFuerPraefix.get(aliasId)}": ${m.content}` };
              }
              return m;
            })
          : history;
        const ollamaMessages = historyMitAliasPraefix
          .map(m => wendeKontextAusschlussAn(m, kontextAusschluesse))
          .filter((m): m is { role: string; content: string } => m !== null);
        let clientGone = false;
        const generationKey = wesenChatPost[1] + "/" + name;
        const generationStart = Date.now();
        res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache",
          "Connection": "keep-alive", "Access-Control-Allow-Origin": "*" });
        let fullResponse = "";
        let responseSaved = false;
        function saveResponse() {
          // verworfen wird ausschliesslich vom /chat/abort-Handler gesetzt UND dort auch schon
          // geloggt (dort ist es garantiert erreichbar — hier bei destroy() waehrend des Streamens
          // feuert weder onToken/onDone zuverlaessig, saveResponse() koennte also nie aufgerufen
          // werden; die Provenienz darf deshalb nicht davon abhaengen).
          if (!responseSaved && fullResponse && !aktiveGenerationen.get(generationKey)?.verworfen) {
            responseSaved = true;
            let inhalt = fullResponse;
            if (isTestbedSpawner(wesenChatPost[1])) {
              const { bereinigt, gemerkt } = extrahiereMerkenMarker(fullResponse);
              inhalt = bereinigt;
              // Kein automatisches Schreiben mehr (siehe extrahiereMerkenMarker-Kommentar) — jeder
              // Vorschlag wird nur geloggt, das eigentliche Speichern passiert erst durch
              // POST .../merken/entscheidung (aktion "annehmen"), einzeln vom Menschen ausgeloest.
              gemerkt.forEach((g, i) => {
                appendProvenienz(hp, "merken_vorschlag", { vorschlagId: `${replyMsgId}:${i}`, text: g.text, warum: g.warum });
              });
            }
            appendHistory(hp, "assistant", inhalt, replyMsgId, isTestbedSpawner(wesenChatPost[1])
              ? { model: activeInteractiveChatModel, grenzen: useGrenzen, dauer_ms: Date.now() - generationStart }
              : undefined);
          }
          aktiveGenerationen.delete(generationKey);
        }
        hauhauClient.tracePrioritaet(`wesenChat:${wesenChatPost[1]}/${name}`, systemPrompt.length + ollamaMessages.reduce((s, m) => s + m.content.length, 0));
        const ollamaReq = hauhauClient.chatStream(
          [{ role: "system", content: systemPrompt }, ...ollamaMessages],
          {
            think: false,
            // num_predict:-1 = unlimitiert (auf Daniels Wunsch entfernt, siehe Session 2026-07-05) —
            // einzige verbleibende Grenze ist der Kontextraum, keine kuenstliche Antwortlaenge mehr.
            extra: { id_slot: 0 },
            onToken: (tok) => { fullResponse += tok; if (!clientGone) res.write(`data: ${JSON.stringify({ token: tok })}\n\n`); },
            onDone: () => { saveResponse(); if (!clientGone) { res.write("data: [DONE]\n\n"); res.end(); } },
            onError: (err) => {
              if (!res.headersSent) {
                res.writeHead(503); res.end();
              } else if (!clientGone && !res.writableEnded) {
                res.write(`data: ${JSON.stringify({error: err.message || "hauhaucs nicht erreichbar"})}\n\n`);
                res.write("data: [DONE]\n\n");
                res.end();
              }
              const eintrag = aktiveGenerationen.get(generationKey);
              if (eintrag?.ollamaReq === ollamaReq) aktiveGenerationen.delete(generationKey);
            },
          }
        );
        if (isAsyncSpawner) aktiveGenerationen.set(generationKey, { ollamaReq, verworfen: false, hp, replyMsgId });
        res.on("close", () => {
          clientGone = true;
          if (!isAsyncSpawner && !ollamaReq.destroyed) ollamaReq.destroy();
        });
      }).catch(() => { res.writeHead(400); res.end(); });
      return;
    }

    // POST /wesen/:spawner/:name/chat/abort — nur codexium2/solarius2: bricht eine laufende
    // Generierung wirklich ab (im Unterschied zum "Email-Gefuehl" bei einfachem Verbindungsverlust,
    // siehe oben). Das angebrochene Ergebnis wird verworfen, nicht in die History geschrieben.
    const chatAbortMatch = urlPath.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/chat\/abort$/);
    if (chatAbortMatch && req.method === "POST") {
      const spawner = chatAbortMatch[1];
      const name = resolveCharName(chatAbortMatch[1], chatAbortMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const eintrag = aktiveGenerationen.get(spawner + "/" + name);
      if (eintrag) {
        eintrag.verworfen = true;
        appendProvenienz(eintrag.hp, "generierung_abgebrochen", { msgId: eintrag.replyMsgId });
        if (!eintrag.ollamaReq.destroyed) eintrag.ollamaReq.destroy();
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    // GET /charakterdashbord — Gesamtuebersicht ueber alle Charaktere aller vier Spawner
    if (urlPath === "/charakterdashbord") {
      const html = readFileSync(join(SERVE_ROOT, "wesen_uebersicht.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(html);
      return;
    }

    // GET /solarius/:name/profil oder /codexium/:name/profil
    const wesenProfilMatch = urlPath.match(/^\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/profil$/);
    if (wesenProfilMatch) {
      const html = readFileSync(join(SERVE_ROOT, "wesen_profil.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(html);
      return;
    }

    // GET /solarius/:name oder /codexium/:name → Chat
    const wesenChatGet = urlPath.match(/^\/(solarius|solarius2|codexium|codexium2)\/([^/]+)$/);
    if (wesenChatGet) {
      let html = readFileSync(join(SERVE_ROOT, "wesen_chat.html"), "utf-8");
      const spawnerSsr = wesenChatGet[1];
      const nameSsr = resolveCharName(spawnerSsr, wesenChatGet[2]);
      const dirSsr = join(wesenRoot(spawnerSsr), nameSsr);
      // Systemprompt immer ins HTML rendern — auch ohne jede Nachricht, damit er fuer Crawler/
      // KI-Browsing-Tools von Anfang an lesbar ist (Daniels Auftrag: "vor der ersten nachricht
      // immer der gesamte systempromt sichtbar lesbar ... crawlbar"). useGrenzen=false, da das der
      // Standardzustand im Chat ist (Grenzen.md wird nur bewusst per Button dazugeschaltet) — sonst
      // waere Grenzen.md standardmaessig fuer jeden Crawler oeffentlich sichtbar.
      const systemPromptText = buildSystemPrompt(spawnerSsr, dirSsr, false);
      if (systemPromptText) {
        html = html.replace('<pre id="systemprompt-pre"></pre>', `<pre id="systemprompt-pre">${escHtml(systemPromptText)}</pre>`);
      }
      // Eigenes, immer sichtbares/crawlbares Dropdown mit dem aktuell formulierten Grenzen-Text —
      // Daniels Auftrag 2026-07-05: nicht nur der Toggle-Button, sondern lesbar was "Grenzen" gerade
      // konkret bedeutet, per Dropdown UND fuer Crawler ohne JS (gleiches Muster wie systemprompt-
      // details oben). Bewusst unabhaengig vom useGrenzen-Stand der Systemprompt-Vorschau oben —
      // dieses Dropdown zeigt den Referenztext immer, unabhaengig davon ob er gerade zugeschaltet ist.
      if (existsSync(WESEN_GRENZEN_PATH)) {
        const grenzenText = readFileSync(WESEN_GRENZEN_PATH, "utf-8").trim();
        if (grenzenText) {
          html = html.replace('<pre id="grenzen-pre"></pre>', `<pre id="grenzen-pre">${escHtml(grenzenText)}</pre>`);
        }
      }
      const verlaufHtml = renderVerlaufHtml(ladeVerlaufKombiniert(chatHistoryPath(spawnerSsr, nameSsr), isTestbedSpawner(spawnerSsr), dirSsr));
      if (verlaufHtml) {
        // Platzhalter-Block bleibt im DOM (Client-JS greift ungeprueft auf #empty-avatar/#empty-name
        // zu, ein komplettes Entfernen wuerde das Skript beim Laden mit einem TypeError abbrechen)
        // — aber "display:none" UND der irrefuehrende "Schreib etwas..."-Text werden entfernt, damit
        // ein Crawler/KI-Browsing-Tool, das CSS nicht auswertet, nicht faelschlich einen leeren Chat
        // liest, obwohl direkt daneben der echte Verlauf steht.
        html = html
          .replace('<div class="msgs" id="msgs">', `<div class="msgs" id="msgs">\n${verlaufHtml}`)
          .replace('<div class="empty" id="empty">', '<div class="empty" id="empty" style="display:none">')
          .replace('<p id="empty-desc">Schreib etwas, um das Gespräch zu beginnen.</p>', '<p id="empty-desc"></p>');
      }
      // Memory/Container/Aliase (Daniels Auftrag 2026-07-08: "alles was dort ist" soll crawlbar
      // sein, nicht nur Verlauf und Systemprompt) — dieselben Lesewege wie GET .../data.
      // Daniels Korrektur 2026-07-09: "brauchen keinen dropdown in ui unter grenzen dropdown" --
      // diese drei duerfen fuer Menschen nicht als sichtbares/klickbares <details> auftauchen (sie
      // sind redundant zu den eigenen Popups dafuer), bleiben aber dauerhaft display:none im
      // Roh-HTML stehen -- ein Text-Crawler ohne CSS-Engine (GPTBot, ClaudeBot etc.) liest den Inhalt
      // trotzdem, display:none ist fuer den nicht sichtbar/relevant. Deshalb: NUR den inneren
      // #...-ssr div befuellen, den aeusseren <details>-Wrapper NIE aus display:none holen.
      let memorySsr: { kategorien: Array<{ key: string; label: string; eintraege: string[] }> } = { kategorien: [] };
      try { memorySsr = JSON.parse(readFileSync(join(dirSsr, "memory.json"), "utf-8")); } catch {}
      const memoryHtml = renderMemoryHtml(memorySsr);
      if (memoryHtml) {
        html = html.replace('<div id="memory-ssr"></div>', `<div id="memory-ssr">${memoryHtml}</div>`);
      }
      const containerHtml = renderContainerHtml(ladeContainerSammlung(dirSsr));
      if (containerHtml) {
        html = html.replace('<div id="container-ssr"></div>', `<div id="container-ssr">${containerHtml}</div>`);
      }
      const aliaseHtml = renderAliaseHtml(ladeAliase(dirSsr));
      if (aliaseHtml) {
        html = html.replace('<div id="aliase-ssr"></div>', `<div id="aliase-ssr">${aliaseHtml}</div>`);
      }
      const themenHtml = renderWiederkehrendeThemenHtml(ladeWiederkehrendeThemen(dirSsr));
      if (themenHtml) {
        html = html
          .replace('<div id="themen-ssr"></div>', `<div id="themen-ssr">${themenHtml}</div>`)
          .replace('<details class="systemprompt-details" id="themen-details" style="display:none">', '<details class="systemprompt-details" id="themen-details">');
      }
      // no-store: diese Seite enthaelt live Daten (Verlauf, Aliase, Systemprompt) — ein vom Browser
      // zwischengespeichertes altes HTML wuerde neue Aliase/Aenderungen scheinbar nicht zeigen.
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
      res.end(html);
      return;
    }

    // GET /solarius oder /codexium → Spawner
    const wesenSpawnerMatch = urlPath.match(/^\/(solarius|solarius2|codexium|codexium2)$/);
    if (wesenSpawnerMatch) {
      const html = readFileSync(join(SERVE_ROOT, "wesen_spawner.html"), "utf-8");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(html);
      return;
    }
    // ── Wesen-API ────────────────────────────────────────────────────────────
    if (url === "/wesen/list" && req.method === "GET") {
      const list: Array<{spawner: string; name: string; hasImage: boolean}> = [];
      for (const sp of ["solarius", "solarius2", "codexium", "codexium2"]) {
        const root = wesenRoot(sp);
        if (existsSync(root)) {
          try {
            for (const e of readdirSync(root, { withFileTypes: true })) {
              if (e.isDirectory() && e.name !== "_geloescht") {
                const hasImage = IMAGE_EXTS.some(ext => existsSync(join(root, e.name, `avatar.${ext}`)));
                list.push({ spawner: sp, name: e.name, hasImage });
              }
            }
          } catch {}
        }
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify(list));
      return;
    }

    // GET /wesen/:spawner/:name/history  — Chat-Verlauf laden
    // DELETE /wesen/:spawner/:name/history — Chat-Verlauf löschen
    // GET Sessionsliste (nur codexium2/solarius2): Zusammenfassung je Session, neueste zuerst
    const sessionsListMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/sessions$/);
    if (sessionsListMatch && req.method === "GET") {
      const spawner = sessionsListMatch[1];
      const name = resolveCharName(sessionsListMatch[1], sessionsListMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const segmente = splitSessions(chatHistoryPath(spawner, name));
      const liste = segmente.map((s, i) => ({
        index: i,
        start_ts: s.startTs || (s.messages[0]?.ts ?? ""),
        anzahl_nachrichten: s.messages.length,
        ist_aktuell: i === segmente.length - 1,
      })).filter(s => s.anzahl_nachrichten > 0 || s.ist_aktuell).reverse();
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ sessions: liste }));
      return;
    }

    // GET einzelne Session (nur codexium2/solarius2, read-only Ansicht alter Sessions)
    const sessionDetailMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/sessions\/(\d+)$/);
    if (sessionDetailMatch && req.method === "GET") {
      const spawner = sessionDetailMatch[1];
      const name = resolveCharName(sessionDetailMatch[1], sessionDetailMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const segmente = splitSessions(chatHistoryPath(spawner, name));
      const idx = parseInt(sessionDetailMatch[3], 10);
      const segment = segmente[idx];
      if (!segment) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ history: segment.messages, ist_aktuell: idx === segmente.length - 1 }));
      return;
    }

    const histMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/history$/);
    if (histMatch) {
      const name = resolveCharName(histMatch[1], histMatch[2]);
      const hp = chatHistoryPath(histMatch[1], name);
      if (req.method === "GET") {
        const history = isTestbedSpawner(histMatch[1]) ? loadCurrentSessionHistory(hp) : loadHistory(hp);
        const verlauf = ladeVerlaufKombiniert(hp, isTestbedSpawner(histMatch[1]), join(wesenRoot(histMatch[1]), name));
        const body: { history: typeof history; verlauf: typeof verlauf; ausschluesse?: Record<string, KontextAusschluss>; merkenVorschlaege?: ReturnType<typeof ladeMerkenVorschlaege> } = { history, verlauf };
        // ausschluesse gilt seit 2026-07-08 fuer alle 4 Spawner (siehe kontextMatch weiter unten) —
        // merkenVorschlaege bleibt testbed-exklusiv, das Merken-Feature selbst ist unveraendert.
        body.ausschluesse = Object.fromEntries(ladeKontextAusschluesse(hp));
        if (isTestbedSpawner(histMatch[1])) {
          body.merkenVorschlaege = ladeMerkenVorschlaege(hp);
        }
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(body));
        return;
      }
      if (req.method === "DELETE") {
        if (existsSync(hp)) rmSync(hp);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: true }));
        return;
      }
    }

    // GET /wesen/:spawner/:name/suche?q=... — Volltextsuche im GESAMTEN Verlauf dieses Charakters
    // (Daniels Wunsch 2026-07-08: "brauchen wir", bei 295 Nachrichten wie bei Mirlach nur scrollen
    // zu koennen ist zu wenig). Bewusst ueber loadHistory() (volle Datei, alle Sessions), nicht nur
    // die aktuelle Session wie sonst bei codexium2/solarius2 -- Suche soll wirklich alles finden.
    // Reine Teilstring-Suche, gross-/kleinschreibungsunabhaengig -- kein Anspruch auf Fuzzy-Suche,
    // aber ehrlich und nachvollziehbar was gefunden wird und was nicht.
    const sucheMatch = urlPath.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/suche$/);
    if (sucheMatch && req.method === "GET") {
      const spawner = sucheMatch[1];
      const name = resolveCharName(sucheMatch[1], sucheMatch[2]);
      const params = new URL(url, "http://x").searchParams;
      const q = (params.get("q") || "").trim();
      if (q.length < 2) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ fehler: "suchbegriff_zu_kurz" }));
        return;
      }
      const hp = chatHistoryPath(spawner, name);
      const qLower = q.toLowerCase();
      const treffer = loadHistory(hp)
        .filter(m => m.content.toLowerCase().includes(qLower))
        .map(m => ({ id: m.id, role: m.role, ts: m.ts, content: m.content }))
        .reverse() // neueste Treffer zuerst
        .slice(0, 200);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ treffer, gesamtAnzahl: treffer.length }));
      return;
    }

    // GET /wesen/:spawner/:name/export?umfang=auswahl|komplett&provenienz=1|0&format=md|txt&ids=a,b,c&zielsprache=xx
    // Download des Verlaufs (Daniels Wunsch 2026-07-08, Uebersetzer-Popup). zielsprache optional —
    // leer/fehlend liefert Originalsprache, gesetzt uebersetzt jeden Eintrag serverseitig (Nachtrag
    // selbentags: Daniel will genau die im Popup gezeigte Uebersetzung als Datei, z.B. um
    // flextrawurst auslaendischen Plattformen zu zeigen — nicht nur ein Original-Archiv).
    // "komplett" ignoriert bewusst Session-Grenzen (auch bei codexium2/solarius2) — Daniel will
    // "von ganz oben bis ganz unten", nicht nur die aktuelle Session.
    const exportMatch = urlPath.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/export$/);
    if (exportMatch && req.method === "GET") {
      // Der umgebende Request-Handler ist bewusst nicht async (siehe createServer-Aufruf oben, alle
      // anderen Routen nutzen .then()-Ketten statt await) -- IIFE, damit dieser Block trotzdem await
      // fuer die Uebersetzung nutzen kann, ohne den ganzen Handler umzubauen.
      (async () => {
        const spawner = exportMatch[1];
        const name = resolveCharName(exportMatch[1], exportMatch[2]);
        const params = new URL(url, "http://x").searchParams;
        const umfang = params.get("umfang") === "auswahl" ? "auswahl" : "komplett";
        const mitProvenienz = params.get("provenienz") !== "0";
        const format = params.get("format") === "txt" ? "txt" : "md";
        const zielsprache = (params.get("zielsprache") || "").trim();
        const gewaehlteIds = new Set((params.get("ids") || "").split(",").map(s => s.trim()).filter(Boolean));
        const hp = chatHistoryPath(spawner, name);
        let verlauf = ladeVerlaufKombiniert(hp, false, join(wesenRoot(spawner), name));
        if (umfang === "auswahl") {
          if (!gewaehlteIds.size) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ fehler: "keine ids" }));
            return;
          }
          // Fenster ueber den INDEX der ausgewaehlten Nachrichten bestimmen (nicht nur per msgId
          // matchen) -- Daniels Korrektur 2026-07-09: "alles immer muss da sein". Die meisten
          // Ereignistypen tragen gar kein msgId (z.B. alias_gewechselt, memory_geaendert,
          // grenzen_toggle, pin_hinzugefuegt) und fielen beim alten msgId-Filter komplett raus,
          // egal ob "mit Provenienz" angehakt war. Die Auswahl ist immer ein zusammenhaengender
          // Ausschnitt (letzte N Nachrichten bzw. genau eine) -- alles, was chronologisch dazwischen
          // liegt, gehoert inhaltlich zu diesem Ausschnitt dazu.
          const gewaehlteIndizes = verlauf
            .map((e, i) => (e.art === "nachricht" && e.id && gewaehlteIds.has(e.id)) ? i : -1)
            .filter(i => i >= 0);
          if (!gewaehlteIndizes.length) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ fehler: "ids nicht gefunden" }));
            return;
          }
          const minIdx = Math.min(...gewaehlteIndizes);
          const maxIdx = Math.max(...gewaehlteIndizes);
          verlauf = verlauf.filter((_, i) => i >= minIdx && i <= maxIdx);
        }
        if (!mitProvenienz) verlauf = verlauf.filter(e => e.art === "nachricht");
        const eintraege = verlaufZuExportEintraegen(verlauf, name);
        const dateiname = `${name}_verlauf_${umfang}${mitProvenienz ? "_mit-provenienz" : "_ohne-provenienz"}${zielsprache ? "_" + zielsprache : ""}.${format}`;

        if (!zielsprache) {
          // Ohne Uebersetzung: sofort fertig, kein Fortschritt noetig — einfache Antwort wie bisher.
          const inhalt = format === "txt" ? renderExportText(eintraege, name) : renderExportMarkdown(eintraege, name);
          res.writeHead(200, {
            "Content-Type": (format === "txt" ? "text/plain" : "text/markdown") + "; charset=utf-8",
            "Content-Disposition": `attachment; filename="${encodeURIComponent(dateiname)}"`,
          });
          res.end(inhalt);
          return;
        }

        // Mit Uebersetzung: kann bei "kompletter Verlauf" viele Minuten dauern (ein Google-
        // Translate-Aufruf pro Eintrag) -- Daniels Wunsch 2026-07-08: stoppbar UND mit live
        // Fortschritt. Gestreamte Antwort im selben "data: {...}\n\n"-Format wie das Chat-Streaming,
        // damit der Client (fetch + ReadableStream) live "X von Y" zeigen kann. Abbruch: der Client
        // ruft AbortController.abort() auf seinem fetch() auf, was hier serverseitig als "close" auf
        // dem Request ankommt — die laufende arbeiter()-Schleife prueft das zwischen jedem Eintrag
        // und bricht dann sauber ab, statt weiter unnoetig Google Translate anzufragen.
        res.writeHead(200, { "Content-Type": "text/event-stream; charset=utf-8", "Cache-Control": "no-cache" });
        let abgebrochen = false;
        req.on("close", () => { abgebrochen = true; });
        const zuUebersetzen = eintraege.filter(e => e.inhalt.trim()).length;
        let fertigCount = 0;
        const uebersetzt: ExportEintrag[] = new Array(eintraege.length);
        let idx = 0;
        const startMs = Date.now();
        async function arbeiter() {
          while (idx < eintraege.length && !abgebrochen) {
            const i = idx++;
            const e = eintraege[i];
            if (!e.inhalt.trim()) { uebersetzt[i] = e; continue; }
            uebersetzt[i] = { ...e, inhalt: await uebersetzeText(e.inhalt, zielsprache) };
            fertigCount++;
            if (!abgebrochen) {
              // Ehrliche Zeitschaetzung (Daniels Wunsch 2026-07-08): Rate aus tatsaechlich in
              // dieser Anfrage schon erledigten Eintraegen, nicht geraten -- selbstkorrigierend,
              // wird mit jedem weiteren Eintrag genauer.
              const vergangenSek = (Date.now() - startMs) / 1000;
              const proSekunde = vergangenSek > 0.3 ? fertigCount / vergangenSek : null;
              const geschaetzteRestsekunden = proSekunde ? Math.round((zuUebersetzen - fertigCount) / proSekunde) : null;
              res.write(`data: ${JSON.stringify({ fortschritt: fertigCount, von: zuUebersetzen, geschaetzte_restsekunden: geschaetzteRestsekunden })}\n\n`);
            }
          }
        }
        await Promise.all(Array.from({ length: Math.min(4, eintraege.length) }, arbeiter));
        if (abgebrochen) { res.end(); return; }
        const inhalt = format === "txt" ? renderExportText(uebersetzt, name) : renderExportMarkdown(uebersetzt, name);
        res.write(`data: ${JSON.stringify({ fertig: true, dateiname, inhalt })}\n\n`);
        res.end();
      })().catch(err => {
        if (!res.headersSent) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ fehler: "export_fehlgeschlagen", detail: String(err && err.message || err) }));
        }
      });
      return;
    }

    // POST /wesen/:spawner/:name/kontext-ausschluss — seit 2026-07-08 fuer alle 4 Spawner (Daniels
    // Wunsch: Mehrfachauswahl + Zeilen/Token-Info im Kontext-Popup, vorher testbed-exklusiv): eine
    // Nachricht ganz oder satzweise von dem was beim naechsten Prompt ans Modell geschickt wird
    // ausnehmen. Loescht NICHTS — die Nachricht bleibt vollstaendig in der History, nur der
    // Ausschluss wird als weiteres Provenienz-Event angehaengt (letzter Eintrag pro msgId gilt).
    const kontextMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/kontext-ausschluss$/);
    if (kontextMatch && req.method === "POST") {
      const spawner = kontextMatch[1];
      const name = resolveCharName(kontextMatch[1], kontextMatch[2]);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { msgId?: string; ganz?: boolean; saetze?: number[] };
        const msgId = (parsed.msgId || "").trim();
        if (!msgId) { res.writeHead(400); res.end(JSON.stringify({ fehler: "keine msgId" })); return; }
        const ganz = parsed.ganz === true;
        const saetze = Array.isArray(parsed.saetze) ? parsed.saetze.filter(n => Number.isInteger(n)) : [];
        // Text als Schnappschuss mitloggen (gleiches Provenienz-Prinzip wie grenzen_toggle/
        // alias_gewechselt): Daniels wiederholter Punkt heute — ein Ereignis soll nie nur BESCHREIBEN
        // dass etwas geaendert wurde, sondern zeigen WAS konkret betroffen war.
        const hpKtx = chatHistoryPath(spawner, name);
        const betroffeneNachricht = loadHistory(hpKtx).find(m => m.id === msgId);
        const nachrichtText = betroffeneNachricht ? betroffeneNachricht.content : "";
        const betroffeneSaetze = (!ganz && saetze.length && betroffeneNachricht)
          ? splitSentencesServer(betroffeneNachricht.content).filter((_, i) => saetze.includes(i))
          : [];
        appendProvenienz(hpKtx, "kontext_toggle", { msgId, ganz, saetze, nachrichtText, betroffeneSaetze });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/:spawner/:name/merken/entscheidung — nur codexium2/solarius2: der Mensch nimmt
    // einen vom Wesen vorgeschlagenen merken_vorschlag an oder lehnt ihn ab (siehe Absprache mit
    // Daniel 2026-07-05: kein stilles Selbst-Speichern mehr). Text/Warum werden bewusst NICHT vom
    // Client uebernommen, sondern aus dem eigenen Log neu ermittelt (ladeMerkenVorschlaege) — so kann
    // niemand ueber den Endpunkt einen beliebigen Text in die Memory schmuggeln, der nie vorgeschlagen
    // wurde.
    const merkenEntscheidungMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/merken\/entscheidung$/);
    if (merkenEntscheidungMatch && req.method === "POST") {
      const spawner = merkenEntscheidungMatch[1];
      const name = resolveCharName(merkenEntscheidungMatch[1], merkenEntscheidungMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const dir = join(wesenRoot(spawner), name);
      const hp = chatHistoryPath(spawner, name);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { vorschlagId?: string; aktion?: string };
        const vorschlagId = (parsed.vorschlagId || "").trim();
        if (!vorschlagId || (parsed.aktion !== "annehmen" && parsed.aktion !== "ablehnen")) {
          res.writeHead(400); res.end(JSON.stringify({ fehler: "vorschlagId oder aktion fehlt/ungueltig" })); return;
        }
        const offen = ladeMerkenVorschlaege(hp).find(v => v.vorschlagId === vorschlagId);
        if (!offen) { res.writeHead(404); res.end(JSON.stringify({ fehler: "vorschlag_nicht_gefunden_oder_schon_entschieden" })); return; }
        if (parsed.aktion === "annehmen") {
          fuegeMemoryEintraegeHinzu(dir, hp, "wesen_selbst", [offen.text]);
          appendProvenienz(hp, "merken_angenommen", { vorschlagId });
        } else {
          appendProvenienz(hp, "merken_abgelehnt", { vorschlagId });
        }
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/:spawner/:name/grenzen-toggle — nur codexium2/solarius2: loggt den Moment des
    // Klicks auf den Grenzen-Button als eigenes, sichtbares Ereignis im Verlauf (nicht nachtraeglich
    // an einzelne Antworten geheftet — Daniels Korrektur 2026-07-05: es gibt nur DAS Aktivieren/
    // Deaktivieren als Live-Handlung im Chat, kein "diese Antwort wurde mit Grenzen gebaut"). Die
    // eigentliche Wirkung auf den naechsten Ollama-Aufruf war schon vorher sofort da (useGrenzen wird
    // pro Nachricht frisch vom Client mitgeschickt) — dieser Endpunkt macht nur den Klick selbst
    // sichtbar/nachvollziehbar in derselben chat_history.jsonl.
    const grenzenToggleMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/grenzen-toggle$/);
    if (grenzenToggleMatch && req.method === "POST") {
      const spawner = grenzenToggleMatch[1];
      const name = resolveCharName(grenzenToggleMatch[1], grenzenToggleMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { aktiv?: boolean };
        // Text als Schnappschuss MIT dem Event speichern (nicht erst beim Anzeigen aus der Datei neu
        // lesen) — Daniels Anschluss-Wunsch: direkt am Ereignis im Verlauf soll sichtbar sein WAS
        // gerade aktiviert/deaktiviert wurde, nicht nur DASS. Ausserdem bleibt so nachvollziehbar was
        // zu diesem Zeitpunkt galt, auch wenn Grenzen.md sich spaeter mal aendert.
        const text = existsSync(WESEN_GRENZEN_PATH) ? readFileSync(WESEN_GRENZEN_PATH, "utf-8").trim() : "";
        appendProvenienz(chatHistoryPath(spawner, name), "grenzen_toggle", { aktiv: parsed.aktiv === true, text });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // PUT /wesen/:spawner/:name/aliase — alle vier Spawner: die ganze Alias-Liste des Menschen fuer
    // dieses Wesen speichern (Formular beim Erstellen ODER nachtraeglich im Profil, siehe
    // ladeAliase/speichereAliase oben). Ersetzt die Liste komplett, nicht additiv — der Client schickt
    // immer den vollstaendigen aktuellen Stand (gleiches Muster wie z.B. Memory-PUT).
    const aliaseMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/aliase$/);
    if (aliaseMatch && req.method === "PUT") {
      const spawner = aliaseMatch[1];
      const name = resolveCharName(aliaseMatch[1], aliaseMatch[2]);
      const dir = join(wesenRoot(spawner), name);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { eintraege?: Array<{ id?: string; name?: string; text?: string }> };
        const gespeichert = speichereAliase(dir, parsed.eintraege || []);
        if (isTestbedSpawner(spawner)) {
          appendProvenienz(chatHistoryPath(spawner, name), "alias_geaendert", { anzahl: gespeichert.length });
        }
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ eintraege: gespeichert }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/:spawner/:name/alias-wechsel — alle vier Spawner: der Mensch wechselt live im Chat
    // die Rolle, in der er gerade spricht (Daniels Wunsch: "fliegender Rollenwechsel", muss sofort und
    // sichtbar sein). Loggt nur das Ereignis fuer den Verlauf — die eigentliche Wirkung auf den
    // naechsten Ollama-Aufruf kommt ueber aliasId im /chat-Body (buildSystemPrompt), ganz analog zu
    // Grenzen: sofort wirksam, weil der Client den aktuellen Stand bei jeder Nachricht frisch schickt.
    const aliasWechselMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/alias-wechsel$/);
    if (aliasWechselMatch && req.method === "POST") {
      const spawner = aliasWechselMatch[1];
      const name = resolveCharName(aliasWechselMatch[1], aliasWechselMatch[2]);
      const dir = join(wesenRoot(spawner), name);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { aliasId?: string };
        const alias = ladeAliase(dir).find(a => a.id === parsed.aliasId);
        if (!alias) { res.writeHead(404); res.end(JSON.stringify({ fehler: "alias_nicht_gefunden" })); return; }
        // Text als Schnappschuss mitloggen, nicht nur den Namen (Provenienz-Prinzip wie schon bei
        // grenzen_toggle: sichtbar WAS gerade galt, nicht nur DASS gewechselt wurde — bleibt auch
        // korrekt wenn die Alias-Beschreibung spaeter mal geaendert wird).
        appendProvenienz(chatHistoryPath(spawner, name), "alias_gewechselt", { aliasId: alias.id, name: alias.name, text: alias.text });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    const imgMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/image$/);
    if (imgMatch) {
      const name = resolveCharName(imgMatch[1], imgMatch[2]);
      const dir = join(wesenRoot(imgMatch[1]), name);
      for (const ext of IMAGE_EXTS) {
        const p = join(dir, `avatar.${ext}`);
        if (existsSync(p)) {
          const data = readFileSync(p);
          const mime = (ext === "jpg" || ext === "jpeg") ? "image/jpeg" : `image/${ext}`;
          res.writeHead(200, { "Content-Type": mime, "Access-Control-Allow-Origin": "*" });
          res.end(data);
          return;
        }
      }
      res.writeHead(404); res.end("no image"); return;
    }

    // POST /wesen/:spawner/:name/avatar — nachtraeglicher Avatar-Upload (Daniels Wunsch 2026-07-08,
    // ausgeloest durch Mirlachs fehlendes Bild): bisher konnte ein Avatar nur BEIM Erstellen ueber
    // /wesen/save gesetzt werden (image_b64), nicht mehr danach. Gleiches Datenformat, eigener
    // Endpunkt fuer den bestehenden Charakter. Ersetzt einen evtl. vorhandenen Avatar mit ANDERER
    // Dateiendung (sonst wuerde die IMG_EXTS-Suchreihenfolge im GET .../image oben den alten
    // treffen, obwohl ein neuer mit anderer Endung existiert).
    const avatarUploadMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/avatar$/);
    if (avatarUploadMatch && req.method === "POST") {
      const spawner = avatarUploadMatch[1];
      const name = resolveCharName(avatarUploadMatch[1], avatarUploadMatch[2]);
      const dir = join(wesenRoot(spawner), name);
      if (!existsSync(dir)) { res.writeHead(404); res.end(JSON.stringify({ fehler: "charakter_nicht_gefunden" })); return; }
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { image_b64?: string; image_ext?: string };
        const ext = (parsed.image_ext || "").toLowerCase().replace(/[^a-z]/g, "");
        if (!parsed.image_b64 || !IMAGE_EXTS.includes(ext)) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ fehler: "ungueltiges_bild" }));
          return;
        }
        const bytes = Buffer.from(parsed.image_b64, "base64");
        if (bytes.length > ANHANG_MAX_BYTES) {
          res.writeHead(413, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ fehler: "zu_gross" }));
          return;
        }
        for (const altExt of IMAGE_EXTS) {
          if (altExt !== ext) { try { rmSync(join(dir, `avatar.${altExt}`)); } catch {} }
        }
        writeFileSync(join(dir, `avatar.${ext}`), bytes);
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/:spawner/:name/upload — Datei-Anhang hochladen (JSON mit base64-Inhalt, gleiches
    // Muster wie image_b64 bei /wesen/save statt einer neuen Multipart-Bibliothek). Speichert die
    // Rohdatei dauerhaft in uploads/, extrahiert Text wo moeglich, liefert sofort eine Vorschau
    // inkl. geschaetzter Token-Kosten zurueck — noch BEVOR die Nachricht abgeschickt wird.
    const uploadMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/upload$/);
    if (uploadMatch && req.method === "POST") {
      const spawner = uploadMatch[1];
      const name = resolveCharName(uploadMatch[1], uploadMatch[2]);
      // Bricht die Vision-/Whisper-Verarbeitung wirklich ab, wenn der Mensch/Proxy die Verbindung
      // aufgibt (z.B. nginx-Timeout) — ohne das lief die Verarbeitung frueher unbemerkt im
      // Hintergrund weiter und blockierte den einzigen Ollama-Modell-Slot (Session 2026-07-05).
      const anhangAbort = new AbortController();
      res.on("close", () => anhangAbort.abort());
      readBody(req).then(async body => {
        let parsed: { dateiname?: string; inhalt_b64?: string };
        try { parsed = JSON.parse(body); } catch { res.writeHead(400); res.end(JSON.stringify({ fehler: "ungueltiges json" })); return; }
        const dateiname = (parsed.dateiname || "datei").replace(/[\/\\]/g, "_").slice(0, 200);
        if (!parsed.inhalt_b64) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein inhalt" })); return; }
        const buffer = Buffer.from(parsed.inhalt_b64, "base64");
        if (buffer.length > ANHANG_MAX_BYTES) {
          res.writeHead(413, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ fehler: "datei_zu_gross", maxBytes: ANHANG_MAX_BYTES }));
          return;
        }
        const dir = join(wesenRoot(spawner), name);
        const uDir = anhaengeDir(dir);
        mkdirSync(uDir, { recursive: true });
        const id = crypto.randomUUID();
        const endung = (dateiname.split(".").pop() || "bin").toLowerCase();
        const pfad = join(uDir, `${id}.${endung}`);
        writeFileSync(pfad, buffer);
        try {
          const ergebnis = await extrahiereAnhang(id, pfad, dateiname, buffer, anhangAbort.signal);
          writeFileSync(anhangManifestPfad(uDir, id), JSON.stringify(ergebnis, null, 2), "utf-8");
          res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify(ergebnis));
        } catch (e) {
          if (anhangAbort.signal.aborted) return; // Verbindung eh schon weg, nichts mehr zu schreiben
          res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ fehler: "extraktion_fehlgeschlagen", details: String(e) }));
        }
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/:spawner/:name/url-lesen — explizites Lesen EINER vom Menschen angegebenen URL
    // (kein Crawling, kein Link-Folgen). Ergebnis landet wie ein Upload als Anhang-Manifest.
    const urlLesenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/url-lesen$/);
    if (urlLesenMatch && req.method === "POST") {
      const spawner = urlLesenMatch[1];
      const name = resolveCharName(urlLesenMatch[1], urlLesenMatch[2]);
      const anhangAbort = new AbortController();
      res.on("close", () => anhangAbort.abort());
      readBody(req).then(async body => {
        let parsed: { url?: string };
        try { parsed = JSON.parse(body); } catch { res.writeHead(400); res.end(JSON.stringify({ fehler: "ungueltiges json" })); return; }
        const zielUrl = (parsed.url || "").trim();
        if (!zielUrl || !istSichereUrl(zielUrl)) {
          res.writeHead(400, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ fehler: "ungueltige_url" }));
          return;
        }
        try {
          const { titel, text } = await leseUrlMitPlaywright(zielUrl, anhangAbort.signal);
          const gekuerzt = text.slice(0, ANHANG_URL_MAX_ZEICHEN);
          const id = crypto.randomUUID();
          const dir = join(wesenRoot(spawner), name);
          const uDir = anhaengeDir(dir);
          mkdirSync(uDir, { recursive: true });
          const ergebnis: AnhangErgebnis = {
            id, dateiname: titel || zielUrl, dateiEndung: "url", art: "text",
            text: gekuerzt, vorschau: gekuerzt.slice(0, 300), geschaetzeTokens: Math.round(gekuerzt.length / 4),
          };
          writeFileSync(anhangManifestPfad(uDir, id), JSON.stringify(ergebnis, null, 2), "utf-8");
          res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify(ergebnis));
        } catch (e) {
          if (anhangAbort.signal.aborted) return;
          res.writeHead(500, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ fehler: "url_lesen_fehlgeschlagen", details: String(e) }));
        }
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    const dataMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/data$/);
    if (dataMatch && req.method === "GET") {
      const name = resolveCharName(dataMatch[1], dataMatch[2]);
      const dir = join(wesenRoot(dataMatch[1]), name);
      const wesenMd = existsSync(join(dir, "wesen.md")) ? readFileSync(join(dir, "wesen.md"), "utf-8") : "";
      // Alle weiteren .md-Dateien (außer wesen.md)
      const extraMds: Array<{name: string; content: string}> = [];
      if (existsSync(dir)) {
        for (const f of readdirSync(dir).filter(f => f.endsWith(".md") && f !== "wesen.md").sort()) {
          extraMds.push({ name: f, content: readFileSync(join(dir, f), "utf-8") });
        }
      }
      let memory: unknown = { kategorien: [] };
      try { memory = JSON.parse(readFileSync(join(dir, "memory.json"), "utf-8")); } catch {}
      const container = ladeContainerSammlung(dir);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ name, spawner: dataMatch[1], wesen_md: wesenMd, extra_mds: extraMds, memory, container, aliase: ladeAliase(dir) }));
      return;
    }

    // PUT /wesen/:sp/:name/file/:filename — beliebige MD-Datei speichern oder löschen
    const fileMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/file\/([^/]+\.md)$/);
    if (fileMatch && req.method === "PUT") {
      const spawner = fileMatch[1];
      const name = resolveCharName(fileMatch[1], fileMatch[2]);
      const filename = fileMatch[3].replace(/[^a-zA-Z0-9_.-]/g, "");
      if (!filename.endsWith(".md")) { res.writeHead(400); res.end("{}"); return; }
      const dir = join(wesenRoot(spawner), name);
      readBody(req).then(body => {
        const { content } = JSON.parse(body);
        const vorher = existsSync(join(dir, filename)) ? readFileSync(join(dir, filename), "utf-8") : "";
        mkdirSync(dir, { recursive: true });
        writeFileSync(join(dir, filename), content ?? "", "utf-8");
        if (isTestbedSpawner(spawner) && vorher !== (content ?? "")) {
          appendProvenienz(chatHistoryPath(spawner, name), "profil_feld_geaendert", { datei: filename, vorher, nachher: content ?? "" });
        }
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }
    if (fileMatch && req.method === "DELETE") {
      const spawner = fileMatch[1];
      const name = resolveCharName(fileMatch[1], fileMatch[2]);
      const filename = fileMatch[3].replace(/[^a-zA-Z0-9_.-]/g, "");
      const p = join(wesenRoot(spawner), name, filename);
      const vorher = existsSync(p) ? readFileSync(p, "utf-8") : null;
      if (existsSync(p)) rmSync(p);
      if (isTestbedSpawner(spawner) && vorher !== null) {
        appendProvenienz(chatHistoryPath(spawner, name), "profil_feld_geloescht", { datei: filename, vorher });
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    const wesenMdMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/wesen_md$/);
    if (wesenMdMatch && req.method === "PUT") {
      const spawner = wesenMdMatch[1];
      const name = resolveCharName(wesenMdMatch[1], wesenMdMatch[2]);
      const dir = join(wesenRoot(spawner), name);
      readBody(req).then(body => {
        const { content } = JSON.parse(body);
        const vorher = existsSync(join(dir, "wesen.md")) ? readFileSync(join(dir, "wesen.md"), "utf-8") : "";
        mkdirSync(dir, { recursive: true });
        writeFileSync(join(dir, "wesen.md"), content, "utf-8");
        if (isTestbedSpawner(spawner) && vorher !== content) {
          appendProvenienz(chatHistoryPath(spawner, name), "profil_feld_geaendert", { datei: "wesen.md", vorher, nachher: content });
        }
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/:spawner/:name/container/neu — neuen, leeren Container anlegen (alle 4 Spawner)
    const neuMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/container\/neu$/);
    if (neuMatch && req.method === "POST") {
      const spawner = neuMatch[1];
      const name = resolveCharName(neuMatch[1], neuMatch[2]);
      const dir = join(wesenRoot(spawner), name);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { name?: string };
        const boxName = (parsed.name || "").trim() || "Neuer Container";
        mkdirSync(dir, { recursive: true });
        const sammlung = ladeContainerSammlung(dir);
        const neueBox: ContainerBox = { id: crypto.randomUUID(), name: boxName, aktiv: true, erstellt_am: new Date().toISOString(), eintraege: [] };
        sammlung.container.push(neueBox);
        speichereContainerSammlung(dir, sammlung);
        appendProvenienz(chatHistoryPath(spawner, name), "container_angelegt", { id: neueBox.id, name: boxName });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, container: neueBox }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // PUT /wesen/:spawner/:name/container/:id/name — Container umbenennen
    const umbenennenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/container\/([^/]+)\/name$/);
    if (umbenennenMatch && req.method === "PUT") {
      const spawner = umbenennenMatch[1];
      const name = resolveCharName(umbenennenMatch[1], umbenennenMatch[2]);
      const boxId = umbenennenMatch[3];
      const dir = join(wesenRoot(spawner), name);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { name?: string };
        const neuerName = (parsed.name || "").trim();
        if (!neuerName) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein name" })); return; }
        const sammlung = ladeContainerSammlung(dir);
        const box = sammlung.container.find(b => b.id === boxId);
        if (!box) { res.writeHead(404); res.end(JSON.stringify({ fehler: "container_nicht_gefunden" })); return; }
        const alterName = box.name;
        box.name = neuerName;
        speichereContainerSammlung(dir, sammlung);
        appendProvenienz(chatHistoryPath(spawner, name), "container_umbenannt", { id: boxId, vorher: alterName, nachher: neuerName });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // PATCH /wesen/:spawner/:name/container/:id/aktiv — an/ausschalten fuers Chat-Kontextfenster
    const aktivMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/container\/([^/]+)\/aktiv$/);
    if (aktivMatch && req.method === "PATCH") {
      const spawner = aktivMatch[1];
      const name = resolveCharName(aktivMatch[1], aktivMatch[2]);
      const boxId = aktivMatch[3];
      const dir = join(wesenRoot(spawner), name);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { aktiv?: boolean };
        const sammlung = ladeContainerSammlung(dir);
        const box = sammlung.container.find(b => b.id === boxId);
        if (!box) { res.writeHead(404); res.end(JSON.stringify({ fehler: "container_nicht_gefunden" })); return; }
        box.aktiv = parsed.aktiv !== false;
        speichereContainerSammlung(dir, sammlung);
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, aktiv: box.aktiv }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/:spawner/:name/container/:id/pin — Eintrag in einen bestimmten Container pinnen
    // (alle 4 Spawner, Budget gilt ueber ALLE Container zusammen — Daniels Entscheidung 2026-07-06)
    const pinMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/container\/([^/]+)\/pin$/);
    if (pinMatch && req.method === "POST") {
      const spawner = pinMatch[1];
      const name = resolveCharName(pinMatch[1], pinMatch[2]);
      const boxId = pinMatch[3];
      const dir = join(wesenRoot(spawner), name);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { text?: string; kommentar?: string; quelle?: string };
        const text = (parsed.text || "").trim();
        const kommentar = (parsed.kommentar || "").trim();
        const quelle = parsed.quelle === "wesen" ? "wesen" : "mensch";
        if (!text) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein text" })); return; }
        mkdirSync(dir, { recursive: true });
        const sammlung = ladeContainerSammlung(dir);
        const box = sammlung.container.find(b => b.id === boxId);
        if (!box) { res.writeHead(404); res.end(JSON.stringify({ fehler: "container_nicht_gefunden" })); return; }
        const neuerEintrag: ContainerEintrag = {
          id: crypto.randomUUID(), text, kommentar: kommentar || undefined, quelle,
          hinzugefuegt_am: new Date().toISOString(),
        };
        const summeMitNeuem = containerSammlungZeichenSumme(sammlung) + neuerEintrag.text.length + (neuerEintrag.kommentar?.length ?? 0);
        if (summeMitNeuem > CONTAINER_BUDGET_ZEICHEN) {
          res.writeHead(413, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ fehler: "budget_voll", budget: CONTAINER_BUDGET_ZEICHEN, aktuell: containerSammlungZeichenSumme(sammlung) }));
          return;
        }
        box.eintraege.push(neuerEintrag);
        speichereContainerSammlung(dir, sammlung);
        appendProvenienz(chatHistoryPath(spawner, name), "pin_hinzugefuegt", { containerId: boxId, containerName: box.name, eintrag: neuerEintrag });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, eintrag: neuerEintrag }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // DELETE /wesen/:spawner/:name/container/:id/eintrag/:eintragId — einzelnen Pin entfernen
    const pinDelMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/container\/([^/]+)\/eintrag\/([^/]+)$/);
    if (pinDelMatch && req.method === "DELETE") {
      const spawner = pinDelMatch[1];
      const name = resolveCharName(pinDelMatch[1], pinDelMatch[2]);
      const boxId = pinDelMatch[3];
      const eintragId = pinDelMatch[4];
      const dir = join(wesenRoot(spawner), name);
      const sammlung = ladeContainerSammlung(dir);
      const box = sammlung.container.find(b => b.id === boxId);
      if (!box) { res.writeHead(404); res.end(JSON.stringify({ fehler: "container_nicht_gefunden" })); return; }
      const entfernterEintrag = box.eintraege.find(e => e.id === eintragId);
      box.eintraege = box.eintraege.filter(e => e.id !== eintragId);
      speichereContainerSammlung(dir, sammlung);
      if (entfernterEintrag) appendProvenienz(chatHistoryPath(spawner, name), "pin_entfernt", { containerId: boxId, eintrag: entfernterEintrag });
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    // DELETE /wesen/:spawner/:name/container/:id — ganzen Container loeschen
    const boxDelMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/container\/([^/]+)$/);
    if (boxDelMatch && req.method === "DELETE") {
      const spawner = boxDelMatch[1];
      const name = resolveCharName(boxDelMatch[1], boxDelMatch[2]);
      const boxId = boxDelMatch[3];
      const dir = join(wesenRoot(spawner), name);
      const sammlung = ladeContainerSammlung(dir);
      const box = sammlung.container.find(b => b.id === boxId);
      sammlung.container = sammlung.container.filter(b => b.id !== boxId);
      speichereContainerSammlung(dir, sammlung);
      if (box) appendProvenienz(chatHistoryPath(spawner, name), "container_geloescht", { id: boxId, name: box.name, anzahlEintraege: box.eintraege.length });
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    // GET /wesen/:spawner/:name/feedback — alle Feedback-Eintraege, nur codexium2/solarius2
    const feedbackGetMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/feedback$/);
    if (feedbackGetMatch && req.method === "GET") {
      const spawner = feedbackGetMatch[1];
      const name = resolveCharName(feedbackGetMatch[1], feedbackGetMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const dir = join(wesenRoot(spawner), name);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ eintraege: loadFeedback(dir) }));
      return;
    }
    // POST /wesen/:spawner/:name/feedback — Daumen hoch/runter und/oder Kommentar zu einer Nachricht
    // setzen (upsert ueber msgId). Schreibt feedback.json UND eine lesbare .md-Datei pro Nachricht
    // in feedback/ — nur codexium2/solarius2.
    if (feedbackGetMatch && req.method === "POST") {
      const spawner = feedbackGetMatch[1];
      const name = resolveCharName(feedbackGetMatch[1], feedbackGetMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { msgId?: string; rolle?: string; nachricht?: string; rating?: string|null; kommentar?: string|null };
        const msgId = (parsed.msgId || "").trim();
        if (!msgId) { res.writeHead(400); res.end(JSON.stringify({ fehler: "keine msgId" })); return; }
        const rolle: "mensch" | "wesen" = parsed.rolle === "wesen" ? "wesen" : "mensch";
        const nachricht = (parsed.nachricht || "").trim();
        const rating: "up"|"down"|null|undefined = parsed.rating === "up" || parsed.rating === "down" ? parsed.rating : parsed.rating === null ? null : undefined;
        const kommentar = typeof parsed.kommentar === "string" ? parsed.kommentar.trim().slice(0, 2000) : parsed.kommentar === null ? null : undefined;
        const dir = join(wesenRoot(spawner), name);
        const eintrag = upsertFeedback(dir, msgId, rolle, nachricht, rating, kommentar);
        appendProvenienz(chatHistoryPath(spawner, name), "feedback", {
          msgId, rolle,
          ...(rating !== undefined ? { rating } : {}),
          ...(kommentar !== undefined ? { kommentar } : {}),
        });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, eintrag }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // Allgemeines Feedback (nicht an eine Nachricht gebunden) — im Unterschied zu obigem
    // Nachrichten-Feedback fuer ALLE vier Spawner, kein isTestbedSpawner-Gate. Provenienz nur
    // fuer codexium2/solarius2 (die einzigen Spawner mit Provenienz-Log ueberhaupt).
    const feedbackAllgemeinMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/feedback\/allgemein$/);
    if (feedbackAllgemeinMatch && req.method === "GET") {
      const spawner = feedbackAllgemeinMatch[1];
      const name = resolveCharName(feedbackAllgemeinMatch[1], feedbackAllgemeinMatch[2]);
      const dir = join(wesenRoot(spawner), name);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ eintraege: ladeAllgemeinesFeedback(dir) }));
      return;
    }
    if (feedbackAllgemeinMatch && req.method === "POST") {
      const spawner = feedbackAllgemeinMatch[1];
      const name = resolveCharName(feedbackAllgemeinMatch[1], feedbackAllgemeinMatch[2]);
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { text?: string };
        const text = (parsed.text || "").trim().slice(0, 2000);
        if (!text) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein text" })); return; }
        const dir = join(wesenRoot(spawner), name);
        const eintrag = fuegeAllgemeinesFeedbackHinzu(dir, text);
        if (isTestbedSpawner(spawner)) {
          appendProvenienz(chatHistoryPath(spawner, name), "feedback_allgemein", { id: eintrag.id, text });
        }
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, eintrag }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // GET Status der letzten/laufenden Memory-Extraktion — nur codexium2/solarius2
    const extraktionStatusMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/memory\/extraktion-status$/);
    if (extraktionStatusMatch && req.method === "GET") {
      const spawner = extraktionStatusMatch[1];
      const name = resolveCharName(extraktionStatusMatch[1], extraktionStatusMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const statusPath = join(wesenRoot(spawner), name, "memory_extraktion.json");
      let status = { status: "nie_gelaufen" };
      if (existsSync(statusPath)) { try { status = JSON.parse(readFileSync(statusPath, "utf-8")); } catch {} }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify(status));
      return;
    }

    // POST Memory-Extraktion triggern (Mensch-getriggert, laeuft asynchron im Hintergrund) — nur codexium2/solarius2
    const extraktionMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/memory\/extrahieren$/);
    if (extraktionMatch && req.method === "POST") {
      const spawner = extraktionMatch[1];
      const name = resolveCharName(extraktionMatch[1], extraktionMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const ergebnis = triggerMemoryExtraktion(spawner, name);
      if (!ergebnis.started) {
        res.writeHead(409, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ fehler: ergebnis.reason }));
        return;
      }
      res.writeHead(202, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ status: "gestartet" }));
      return;
    }

    // POST Memory-Extraktion abbrechen — nur codexium2/solarius2 (Daniels Wunsch 2026-07-08,
    // gleiches Prinzip wie /chat/abort: Request wirklich toeten, nicht nur den Client-Fetch).
    const extraktionAbortMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/memory\/extraktion-abbrechen$/);
    if (extraktionAbortMatch && req.method === "POST") {
      const spawner = extraktionAbortMatch[1];
      const name = resolveCharName(extraktionAbortMatch[1], extraktionAbortMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const schluessel = spawner + "/" + name;
      const laufenderReq = laufendeMemoryJobs.get(schluessel);
      const statusPath = join(wesenRoot(spawner), name, "memory_extraktion.json");
      if (laufenderReq) {
        laufendeMemoryJobs.delete(schluessel);
        try {
          const bisher = JSON.parse(readFileSync(statusPath, "utf-8"));
          writeFileSync(statusPath, JSON.stringify({ ...bisher, status: "abgebrochen", fertig_am: new Date().toISOString() }, null, 2), "utf-8");
        } catch {}
        if (!laufenderReq.destroyed) laufenderReq.destroy();
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true, abgebrochen: !!laufenderReq }));
      return;
    }

    // GET Status/Entwurf der Abschluss-Geschichte — nur codexium2/solarius2
    const abschlussStatusMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/abschluss\/status$/);
    if (abschlussStatusMatch && req.method === "GET") {
      const spawner = abschlussStatusMatch[1];
      const name = resolveCharName(abschlussStatusMatch[1], abschlussStatusMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const dir = join(wesenRoot(spawner), name);
      const statusPath = join(dir, "abschluss_entwurf.json");
      let status: Record<string, unknown> = { status: "nie_gelaufen" };
      if (existsSync(statusPath)) { try { status = JSON.parse(readFileSync(statusPath, "utf-8")); } catch {} }
      const aktuell = existsSync(join(dir, "letzter_abschluss.md")) ? readFileSync(join(dir, "letzter_abschluss.md"), "utf-8") : "";
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ...status, aktueller_abschluss: aktuell }));
      return;
    }

    // POST Abschluss-Geschichte generieren (jederzeit abrufbar, nicht an Sessionende gebunden) — nur codexium2/solarius2
    const abschlussGenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/abschluss\/generieren$/);
    if (abschlussGenMatch && req.method === "POST") {
      const spawner = abschlussGenMatch[1];
      const name = resolveCharName(abschlussGenMatch[1], abschlussGenMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const ergebnis = triggerAbschlussGenerierung(spawner, name);
      if (!ergebnis.started) {
        res.writeHead(409, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ fehler: ergebnis.reason }));
        return;
      }
      res.writeHead(202, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ status: "gestartet" }));
      return;
    }

    // POST Abschluss-Generierung abbrechen — nur codexium2/solarius2 (Daniels Wunsch 2026-07-08,
    // gleiches Prinzip wie /chat/abort und /memory/extraktion-abbrechen).
    const abschlussAbortMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/abschluss\/abbrechen$/);
    if (abschlussAbortMatch && req.method === "POST") {
      const spawner = abschlussAbortMatch[1];
      const name = resolveCharName(abschlussAbortMatch[1], abschlussAbortMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const schluessel = spawner + "/" + name;
      const laufenderReq = laufendeAbschlussJobs.get(schluessel);
      const statusPath = join(wesenRoot(spawner), name, "abschluss_entwurf.json");
      if (laufenderReq) {
        laufendeAbschlussJobs.delete(schluessel);
        try {
          const bisher = JSON.parse(readFileSync(statusPath, "utf-8"));
          writeFileSync(statusPath, JSON.stringify({ ...bisher, status: "abgebrochen", fertig_am: new Date().toISOString() }, null, 2), "utf-8");
        } catch {}
        if (!laufenderReq.destroyed) laufenderReq.destroy();
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true, abgebrochen: !!laufenderReq }));
      return;
    }

    // POST Entwurf verwerfen — loescht die Status-Datei, damit ein erneutes Oeffnen des Popups
    // nicht denselben (bereits abgelehnten) Entwurf wieder anzeigt. Der Entwurf hat nie ein
    // persistiertes Feld beruehrt, daher kein Provenienz-Event dafuer noetig.
    const abschlussVerwerfenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/abschluss\/verwerfen$/);
    if (abschlussVerwerfenMatch && req.method === "POST") {
      const spawner = abschlussVerwerfenMatch[1];
      const name = resolveCharName(abschlussVerwerfenMatch[1], abschlussVerwerfenMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const statusPath = join(wesenRoot(spawner), name, "abschluss_entwurf.json");
      try { if (existsSync(statusPath)) rmSync(statusPath); } catch {}
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    // POST Entwurf als Abschluss uebernehmen — schreibt letzter_abschluss.md, fliesst ab jetzt in
    // JEDEN kuenftigen System-Prompt ein (siehe MD_ORDER), bis ein neuer Abschluss ihn ersetzt.
    const abschlussUebernehmenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/abschluss\/uebernehmen$/);
    if (abschlussUebernehmenMatch && req.method === "POST") {
      const spawner = abschlussUebernehmenMatch[1];
      const name = resolveCharName(abschlussUebernehmenMatch[1], abschlussUebernehmenMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { text?: string };
        const text = (parsed.text || "").trim().slice(0, ABSCHLUSS_MAX_ZEICHEN);
        if (!text) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein text" })); return; }
        const dir = join(wesenRoot(spawner), name);
        mkdirSync(dir, { recursive: true });
        const vorher = existsSync(join(dir, "letzter_abschluss.md")) ? readFileSync(join(dir, "letzter_abschluss.md"), "utf-8") : "";
        writeFileSync(join(dir, "letzter_abschluss.md"), text, "utf-8");
        appendProvenienz(chatHistoryPath(spawner, name), "abschluss_uebernommen", { vorher, nachher: text });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // GET Verdichtungs-Zeitachse (nur codexium2/solarius2) — Einheiten (Nachrichten +
    // bereits bestaetigte Verdichtungen) fuer den Slider im Verdichten-Modal.
    const verdZeitachseMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/verdichtung\/zeitachse$/);
    if (verdZeitachseMatch && req.method === "GET") {
      const spawner = verdZeitachseMatch[1];
      const name = resolveCharName(verdZeitachseMatch[1], verdZeitachseMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const dir = join(wesenRoot(spawner), name);
      const history = loadCurrentSessionHistory(chatHistoryPath(spawner, name));
      const bestaetigte = ladeVerdichtungen(dir).filter(v => v.bestaetigt);
      const zeitachse = aktiveZeitachse(history, bestaetigte);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ zeitachse }));
      return;
    }

    // GET Status/Entwurf der laufenden Verdichtung (nur codexium2/solarius2)
    const verdStatusMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/verdichtung\/entwurf\/status$/);
    if (verdStatusMatch && req.method === "GET") {
      const spawner = verdStatusMatch[1];
      const name = resolveCharName(verdStatusMatch[1], verdStatusMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const statusPath = join(wesenRoot(spawner), name, "verdichtung_entwurf.json");
      let status: Record<string, unknown> = { status: "nie_gelaufen" };
      if (existsSync(statusPath)) { try { status = JSON.parse(readFileSync(statusPath, "utf-8")); } catch {} }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify(status));
      return;
    }

    // POST Verdichtungs-Entwurf (neu) generieren — {ersetztIds: string[]} (nur codexium2/solarius2)
    const verdGenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/verdichtung\/entwurf\/generieren$/);
    if (verdGenMatch && req.method === "POST") {
      const spawner = verdGenMatch[1];
      const name = resolveCharName(verdGenMatch[1], verdGenMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { ersetztIds?: string[] };
        const ergebnis = triggerVerdichtung(spawner, name, parsed.ersetztIds || []);
        if (!ergebnis.started) {
          res.writeHead(409, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ fehler: ergebnis.reason }));
          return;
        }
        res.writeHead(202, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ status: "gestartet" }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST Kommentar zum laufenden Entwurf — loest Neugenerierung aus (nur codexium2/solarius2)
    const verdKommentarMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/verdichtung\/entwurf\/kommentar$/);
    if (verdKommentarMatch && req.method === "POST") {
      const spawner = verdKommentarMatch[1];
      const name = resolveCharName(verdKommentarMatch[1], verdKommentarMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      readBody(req).then(body => {
        const parsed = JSON.parse(body) as { text?: string };
        const text = (parsed.text || "").trim();
        if (!text) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein kommentar" })); return; }
        const ergebnis = triggerVerdichtung(spawner, name, [], text);
        if (!ergebnis.started) {
          res.writeHead(409, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(JSON.stringify({ fehler: ergebnis.reason }));
          return;
        }
        res.writeHead(202, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ status: "gestartet" }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST Verdichtung abbrechen — nur codexium2/solarius2 (Daniels Wunsch 2026-07-08, gleiches
    // Prinzip wie /abschluss/abbrechen und /memory/extraktion-abbrechen).
    const verdAbortMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/verdichtung\/entwurf\/abbrechen$/);
    if (verdAbortMatch && req.method === "POST") {
      const spawner = verdAbortMatch[1];
      const name = resolveCharName(verdAbortMatch[1], verdAbortMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const schluessel = spawner + "/" + name;
      const laufenderReq = laufendeVerdichtungJobs.get(schluessel);
      const statusPath = join(wesenRoot(spawner), name, "verdichtung_entwurf.json");
      if (laufenderReq) {
        laufendeVerdichtungJobs.delete(schluessel);
        try {
          const bisher = JSON.parse(readFileSync(statusPath, "utf-8"));
          writeFileSync(statusPath, JSON.stringify({ ...bisher, status: "abgebrochen", fertig_am: new Date().toISOString() }, null, 2), "utf-8");
        } catch {}
        if (!laufenderReq.destroyed) laufenderReq.destroy();
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true, abgebrochen: !!laufenderReq }));
      return;
    }

    // POST Entwurf verwerfen (nur codexium2/solarius2)
    const verdVerwerfenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/verdichtung\/entwurf\/verwerfen$/);
    if (verdVerwerfenMatch && req.method === "POST") {
      const spawner = verdVerwerfenMatch[1];
      const name = resolveCharName(verdVerwerfenMatch[1], verdVerwerfenMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const statusPath = join(wesenRoot(spawner), name, "verdichtung_entwurf.json");
      try { if (existsSync(statusPath)) rmSync(statusPath); } catch {}
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    // POST Entwurf uebernehmen — schreibt bestaetigte Verdichtung nach verdichtungen.json,
    // absorbiert dabei transitiv alle abgedeckten Nachrichten/aelteren Verdichtungen
    // (nur codexium2/solarius2)
    const verdUebernehmenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/verdichtung\/entwurf\/uebernehmen$/);
    if (verdUebernehmenMatch && req.method === "POST") {
      const spawner = verdUebernehmenMatch[1];
      const name = resolveCharName(verdUebernehmenMatch[1], verdUebernehmenMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const dir = join(wesenRoot(spawner), name);
      const statusPath = join(dir, "verdichtung_entwurf.json");
      if (!existsSync(statusPath)) { res.writeHead(404); res.end(JSON.stringify({ fehler: "kein_entwurf" })); return; }
      let status: { status?: string; entwurf?: string; ersetztIds?: string[]; kommentare?: Array<{text:string;ts:string}> } = {};
      try { status = JSON.parse(readFileSync(statusPath, "utf-8")); } catch {}
      if (status.status !== "fertig" || !status.entwurf || !status.ersetztIds?.length) {
        res.writeHead(409, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ fehler: "kein_fertiger_entwurf" }));
        return;
      }
      const neu: Verdichtung = {
        id: crypto.randomUUID(),
        ersetztIds: status.ersetztIds,
        zusammenfassung: status.entwurf,
        kommentare: status.kommentare || [],
        bestaetigt: true,
        erstellt_am: new Date().toISOString(),
        aktualisiert_am: new Date().toISOString(),
      };
      const liste = ladeVerdichtungen(dir);
      liste.push(neu);
      speichereVerdichtungen(dir, liste);
      try { rmSync(statusPath); } catch {}
      appendProvenienz(chatHistoryPath(spawner, name), "verdichtung_uebernommen", { id: neu.id, ersetztAnzahl: neu.ersetztIds.length, zusammenfassung: neu.zusammenfassung });
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true, verdichtung: neu }));
      return;
    }

    // POST Session beenden (nur codexium2/solarius2): Marker schreiben, Extraktion antriggern, Container leeren
    const sessionBeendenMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/session\/beenden$/);
    if (sessionBeendenMatch && req.method === "POST") {
      const spawner = sessionBeendenMatch[1];
      const name = resolveCharName(sessionBeendenMatch[1], sessionBeendenMatch[2]);
      if (!isTestbedSpawner(spawner)) { res.writeHead(404); res.end(); return; }
      const hp = chatHistoryPath(spawner, name);
      appendFileSync(hp, JSON.stringify({ type: "session_start", ts: new Date().toISOString() }) + "\n", "utf-8");
      triggerMemoryExtraktion(spawner, name);
      // Container wird NICHT mehr geleert (Entscheidung 2026-07-04 Abend, vorher war er session-lokal) —
      // Pins wandern jetzt ueber Sessions mit, bis sie manuell entfernt werden oder das Budget voll ist.
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    const memMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/memory$/);
    if (memMatch && req.method === "PUT") {
      const spawner = memMatch[1];
      const name = resolveCharName(memMatch[1], memMatch[2]);
      const dir = join(wesenRoot(spawner), name);
      const fname = "memory";
      readBody(req).then(body => {
        // codexium2/solarius2: Gesamt-Zeichenbudget statt Max-pro-Kategorie (siehe memory_container.md)
        // + Provenienz: bei "memory" wird vorher/nachher pro Kategorie verglichen und die Differenz
        // geloggt (wer hat wann was hinzugefuegt/entfernt — manueller Edit, 🧠+-Button oder Extraktion
        // laufen alle ueber diesen selben PUT-Endpunkt).
        let memoryDiffs: Array<{ kategorie: string; hinzugefuegt: string[]; entfernt: string[] }> | null = null;
        if (isTestbedSpawner(spawner)) {
          try {
            const parsed = JSON.parse(body);
            if (fname === "memory") {
              const summe = (parsed.kategorien || []).reduce((s: number, k: { eintraege?: string[] }) =>
                s + (k.eintraege || []).reduce((s2: number, e: string) => s2 + String(e).length, 0), 0);
              if (summe > MEMORY_BUDGET_ZEICHEN) {
                res.writeHead(413, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
                res.end(JSON.stringify({ fehler: "budget_voll", budget: MEMORY_BUDGET_ZEICHEN, aktuell: summe }));
                return;
              }
              let vorher: { kategorien?: Array<{ key: string; eintraege?: string[] }> } = {};
              try { vorher = JSON.parse(readFileSync(join(dir, "memory.json"), "utf-8")); } catch {}
              memoryDiffs = [];
              for (const katNachher of (parsed.kategorien || [])) {
                const katVorher = (vorher.kategorien || []).find(k => k.key === katNachher.key);
                const alt: string[] = katVorher?.eintraege || [];
                const neu: string[] = katNachher.eintraege || [];
                const hinzugefuegt = neu.filter(e => !alt.includes(e));
                const entfernt = alt.filter(e => !neu.includes(e));
                if (hinzugefuegt.length || entfernt.length) memoryDiffs.push({ kategorie: katNachher.key, hinzugefuegt, entfernt });
              }
            }
          } catch { res.writeHead(400); res.end(JSON.stringify({ fehler: "ungueltiges json" })); return; }
        }
        mkdirSync(dir, { recursive: true });
        writeFileSync(join(dir, `${fname}.json`), body, "utf-8");
        if (memoryDiffs && memoryDiffs.length) appendProvenienz(chatHistoryPath(spawner, name), "memory_geaendert", { diffs: memoryDiffs });
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // GET /wesen/alle — Liste aller Charaktere ueber alle vier Spawner hinweg, fuer die
    // Uebersichtsseite (wesen_uebersicht.html). Reines Lesen der Ordnerstruktur, kein Zugriff auf
    // Inhalte (Details holt sich die Uebersicht pro Charakter einzeln ueber /data).
    if (url === "/wesen/alle" && req.method === "GET") {
      const spawnerListe = ["codexium", "codexium2", "solarius", "solarius2"];
      const charaktere: Array<{ spawner: string; name: string }> = [];
      for (const sp of spawnerListe) {
        const root = wesenRoot(sp);
        if (!existsSync(root)) continue;
        try {
          for (const entry of readdirSync(root, { withFileTypes: true })) {
            if (entry.isDirectory() && entry.name !== "_geloescht") charaktere.push({ spawner: sp, name: entry.name });
          }
        } catch {}
      }
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ charaktere }));
      return;
    }

    if (url === "/wesen/save" && req.method === "POST") {
      readBody(req).then(body => {
        const parsed = JSON.parse(body);
        const sp = ["solarius2", "codexium", "codexium2"].includes(parsed.spawner) ? parsed.spawner : "solarius";
        const name = resolveCharName(sp, parsed.name ?? "");
        if (!name) { res.writeHead(400); res.end(JSON.stringify({ fehler: "kein name" })); return; }
        const dir = join(wesenRoot(sp), name);
        mkdirSync(dir, { recursive: true });
        // Neues Format: files-Array mit {name, content}
        if (Array.isArray(parsed.files)) {
          for (const f of parsed.files as Array<{name:string;content:string}>) {
            const fname = f.name.replace(/[^a-zA-Z0-9_.-]/g, "");
            if (fname.endsWith(".md")) writeFileSync(join(dir, fname), f.content ?? "", "utf-8");
          }
        } else if (parsed.wesen_md) {
          // Rückwärtskompatibilität: altes Format
          writeFileSync(join(dir, "wesen.md"), parsed.wesen_md, "utf-8");
        }
        if (parsed.image_b64) {
          const ext = (parsed.image_ext ?? "png").toLowerCase().replace(/[^a-z]/g, "");
          writeFileSync(join(dir, `avatar.${ext}`), Buffer.from(parsed.image_b64, "base64"));
        }
        // Default memory.json wenn noch nicht vorhanden
        // codexium2/solarius2: neue 5-Kategorien-Struktur (Budget statt Max-pro-Kategorie, siehe
        // _claude/ideen/codexium2_solarius2/memory_container.md). Codexium/Solarius: altes Format unveraendert.
        const memPath = join(dir, "memory.json");
        if (!existsSync(memPath)) {
          const defaultMem = (sp === "codexium2" || sp === "solarius2") ? { kategorien: [
            { key: "ueber_mich", label: "Über dich", eintraege: [] },
            { key: "wichtige_momente", label: "Wichtige Momente", eintraege: [] },
            { key: "offene_fragen", label: "Offene Fragen", eintraege: [] },
            { key: "wesen_selbst", label: "Wesen selbst", eintraege: [] },
            { key: "meinungen", label: "Meinungen", eintraege: [] },
          ]} : { kategorien: [
            { label: "Wissen", max: 20, eintraege: [] },
            { label: "Erlebnisse", max: 10, eintraege: [] },
            { label: "Beziehungen", max: 10, eintraege: [] },
            { label: "Vorlieben", max: 10, eintraege: [] },
          ]};
          writeFileSync(memPath, JSON.stringify(defaultMem, null, 2), "utf-8");
        }
        // Default container.json (leere Mehrfach-Container-Sammlung) — gilt seit 2026-07-06 fuer
        // alle 4 Spawner (Daniel: Container sollen einheitlich sein, siehe memory_container.md)
        {
          const contPath = join(dir, "container.json");
          if (!existsSync(contPath)) writeFileSync(contPath, JSON.stringify({ container: [] } as ContainerSammlung, null, 2), "utf-8");
        }
        res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        res.end(JSON.stringify({ ok: true, name, spawner: sp }));
      }).catch(() => { res.writeHead(500); res.end("{}"); });
      return;
    }

    // POST /wesen/:spawner/:name/soft-delete — verschiebt den kompletten Charakter-Ordner nach
    // _geloescht/ statt ihn zu loeschen. Nichts geht verloren (wesen.md, chat_history.jsonl,
    // memory.json, container.json, uploads/, feedback/ — alles bleibt, nur der Ort aendert sich).
    // Zeitstempel im Zielnamen verhindert Kollisionen, falls derselbe Name mehrfach geloescht wird.
    const softDeleteMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)\/soft-delete$/);
    if (softDeleteMatch && req.method === "POST") {
      const spawner = softDeleteMatch[1];
      const name = resolveCharName(softDeleteMatch[1], softDeleteMatch[2]);
      const dir = join(wesenRoot(spawner), name);
      if (!existsSync(dir)) { res.writeHead(404, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }); res.end(JSON.stringify({ fehler: "nicht_gefunden" })); return; }
      const geloeschtRoot = join(wesenRoot(spawner), "_geloescht");
      mkdirSync(geloeschtRoot, { recursive: true });
      const zeitstempel = new Date().toISOString().replace(/[:.]/g, "-");
      const ziel = join(geloeschtRoot, `${name}__${zeitstempel}`);
      renameSync(dir, ziel);
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true, verschoben_nach: ziel }));
      return;
    }

    // DELETE /wesen/:spawner/:name — echtes, unwiderrufliches Loeschen (Hard-Delete). Bewusst
    // weiterhin vorhanden (z.B. fuer Wegwerf-Testcharaktere) — fuer echte Charaktere siehe
    // soft-delete oben, das ist jetzt der Standardweg im Profil.
    const delMatch = url.match(/^\/wesen\/(solarius|solarius2|codexium|codexium2)\/([^/]+)$/);
    if (delMatch && req.method === "DELETE") {
      const name = resolveCharName(delMatch[1], delMatch[2]);
      const dir = join(wesenRoot(delMatch[1]), name);
      if (existsSync(dir)) rmSync(dir, { recursive: true, force: true });
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ ok: true }));
      return;
    }
    // ── Ende Wesen-API ───────────────────────────────────────────────────────

    // Welt-API-Proxy — leitet /api/* an localhost:8030 weiter (außer /api/splitter exakt)
    if (url.startsWith("/api/") && url.split('?')[0] !== "/api/splitter") {
      const fwdHeaders: Record<string, string | string[]> = {};
      for (const [k, v] of Object.entries(req.headers)) {
        if (v !== undefined && k.toLowerCase() !== "host") fwdHeaders[k] = v as string | string[];
      }
      const targetPath = url.slice(4) || "/";
      const proxyOpts = {
        hostname: "localhost", port: 8030, path: targetPath,
        method: req.method ?? "GET",
        headers: fwdHeaders,
      };
      const proxy = http.request(proxyOpts, (gr) => {
        const chunks: Buffer[] = [];
        gr.on("data", c => chunks.push(c));
        gr.on("end", () => {
          res.writeHead(gr.statusCode ?? 200, {
            "Content-Type": gr.headers["content-type"] ?? "application/json",
            "Access-Control-Allow-Origin": "*",
          });
          res.end(Buffer.concat(chunks));
        });
      });
      proxy.on("error", (e) => {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ fehler: String(e) }));
      });
      req.pipe(proxy);
      return;
    }

    // Welt-API-Proxy für Endpunkte ohne /api/ Prefix (Zitate, Schatten, Admin, Suche)
    if (url.startsWith("/zitate") || url.startsWith("/shadow/") || url.startsWith("/admin/") || url.startsWith("/search/")) {
      const fwdHeaders: Record<string, string | string[]> = {};
      for (const [k, v] of Object.entries(req.headers)) {
        if (v !== undefined && k.toLowerCase() !== "host") fwdHeaders[k] = v as string | string[];
      }
      const proxyOpts = {
        hostname: "localhost", port: 8030, path: url,
        method: req.method ?? "GET",
        headers: fwdHeaders,
      };
      const proxy = http.request(proxyOpts, (gr) => {
        const chunks: Buffer[] = [];
        gr.on("data", c => chunks.push(c));
        gr.on("end", () => {
          res.writeHead(gr.statusCode ?? 200, {
            "Content-Type": gr.headers["content-type"] ?? "application/json",
            "Access-Control-Allow-Origin": "*",
          });
          res.end(Buffer.concat(chunks));
        });
      });
      proxy.on("error", (e) => {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ fehler: String(e) }));
      });
      req.pipe(proxy);
      return;
    }

    // GENI-Proxy — leitet /api/splitter (exakt) an GENI intern weiter
    const urlPathOnly = url.split('?')[0];
    if (urlPathOnly === "/api/splitter") {
      const n = new URL(url, "http://x").searchParams.get("n") ?? "60";
      const opts = {
        hostname: "localhost", port: 8020, path: `/api/splitter?n=${n}`,
        method: "GET", rejectUnauthorized: false,
      };
      const proxy = https.request(opts, (gr) => {
        const chunks: Buffer[] = [];
        gr.on("data", c => chunks.push(c));
        gr.on("end", () => {
          res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
          res.end(Buffer.concat(chunks));
        });
      });
      proxy.on("error", (e) => {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ fehler: String(e) }));
      });
      proxy.end();
      return;
    }

    if (url === "/") {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(buildIndexHtml());
      return;
    }

    // Öffentliche Crawler-Dateien direkt aus public/ ausliefern
    if (isPublicFile) {
      const p = join(PUBLIC_ROOT, url);
      const t = getPublicContentType(url);
      if (t && existsSync(p)) { res.writeHead(200, { "Content-Type": t }); res.end(readFileSync(p)); }
      else { res.writeHead(404, { "Content-Type": "text/plain" }); res.end("Not found"); }
      return;
    }

    const contentType = getContentType(url);
    if (!contentType || !isSafePath(url)) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Not found");
      return;
    }

    // Check public/ first, then fall through to SERVE_ROOT
    const publicPath = join(PUBLIC_ROOT, url);
    const publicType = getPublicContentType(url);
    if (publicType && existsSync(publicPath) && normalize(publicPath).startsWith(PUBLIC_ROOT + "/")) {
      const content = readFileSync(publicPath);
      res.writeHead(200, { "Content-Type": publicType });
      res.end(content);
      return;
    }

    const filePath = join(SERVE_ROOT, url);

    if (!existsSync(filePath)) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("File not found — build first");
      return;
    }

    const content = readFileSync(filePath);
    res.writeHead(200, { "Content-Type": contentType, "Cache-Control": "no-cache, no-store, must-revalidate" });
    res.end(content);
  });

  server.listen(port, host, () => {
    console.log("flextrawurst Preview Server gestartet:");
    console.log(`  http://localhost:${port}/`);
    console.log(`  http://127.0.0.1:${port}/`);
    console.log(`  http://0.0.0.0:${port}/`);
    console.log("");
    console.log("Hinweis: Fuer externe Erreichbarkeit (VPS) muss Port/Firewall/SSH-Tunnel separat geregelt werden.");
    console.log("Ctrl+C zum Beenden.");
  });
}

if (process.argv[1]?.endsWith("serve_process_camera_preview_smoketest.ts")) {
  startServer();
}
