// Zentraler Client fuer hauhaucs (llama-server, Port 11435, OpenAI-Format).
// TS-Pendant zu /root/werkraum/hauhau_client.py -- ersetzt direkte Ollama-Aufrufe
// (Port 11434) in serve_process_camera_preview.ts.
//
// Nutzt Node's rohes http-Modul (nicht fetch), damit chatStream() denselben
// http.ClientRequest zurueckgibt, den der Aufrufer schon kennt -- fuer
// Abbruch-Tracking (aktiveGenerationen-Map, req.destroy()) muss der Request-
// Handle erhalten bleiben, genau wie beim bisherigen Ollama-Aufruf.

import * as http from "node:http";
import * as fs from "node:fs";

// Zwei getrennte llama-server-Instanzen seit 2026-07-06 (dieselbe GGUF-Datei,
// per mmap geteilter Speicher — live getestet, ~1GB Mehrkosten statt ~30GB):
// Chat-Instanz exklusiv fuer Live-Chat (id_slot=0), Hintergrund-Instanz fuer
// alles andere. Siehe docs/systemdoku/12_ollama_gemma4.md.
const LLAMA_HOST = "localhost";
const LLAMA_PORT_CHAT = 11435;
const LLAMA_PORT_HINTERGRUND = 11436;
const LLAMA_PATH = "/v1/chat/completions";
const MODEL = "hauhaucs-q6";

// Leichtgewichtiges Trace-Log fuer Slot-0-Anfragen (Chat-Prioritaet) — siehe hauhau_client.py fuer
// die volle Begruendung (zwei nicht zurueckverfolgbare Haenger am 2026-07-06).
const CHAT_PRIORITAET_TRACE = "/root/werkraum/_shared/chat_prioritaet_trace.jsonl";
export function tracePrioritaet(quelle: string, zeichen: number): void {
  try {
    fs.appendFileSync(CHAT_PRIORITAET_TRACE, JSON.stringify({
      ts: new Date().toISOString(), quelle, zeichen, pid: process.pid,
    }) + "\n", "utf-8");
  } catch { /* Trace-Log darf den Chat nie blockieren */ }
}

export type HauhauMessage = { role: string; content: unknown };

export type HauhauChatOptions = {
  system?: string;
  images?: string[]; // rohe Base64-Strings (jpeg), werden als image_url Content-Parts angehaengt
  think?: boolean;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  topK?: number;
  minP?: number;
  presencePenalty?: number;
  dryMultiplier?: number;
  repeatPenalty?: number;
  extra?: Record<string, unknown>;
};

function normalizeMessages(
  messagesOrPrompt: HauhauMessage[] | string,
  opts: HauhauChatOptions
): HauhauMessage[] {
  let messages: HauhauMessage[];
  if (typeof messagesOrPrompt === "string") {
    messages = [];
    if (opts.system) messages.push({ role: "system", content: opts.system });
    messages.push({ role: "user", content: messagesOrPrompt });
  } else {
    messages = opts.system
      ? [{ role: "system", content: opts.system }, ...messagesOrPrompt]
      : [...messagesOrPrompt];
  }

  if (opts.images && opts.images.length > 0) {
    const letzte = { ...messages[messages.length - 1] } as HauhauMessage;
    const text = typeof letzte.content === "string" ? letzte.content : "";
    const content: Array<Record<string, unknown>> = text ? [{ type: "text", text }] : [];
    for (const b64 of opts.images) {
      content.push({ type: "image_url", image_url: { url: `data:image/jpeg;base64,${b64}` } });
    }
    letzte.content = content;
    messages = [...messages.slice(0, -1), letzte];
  }

  return messages;
}

// Hintergrund-Instanz hat seit --parallel 1 genau einen echten Slot.
function defaultIdSlot(): number {
  return 0;
}

/** `extra.id_slot === 0` explizit gesetzt => Live-Chat => eigene Chat-Instanz,
 * sonst Hintergrund-Instanz. */
function zielPort(opts: HauhauChatOptions): number {
  return opts.extra?.id_slot === 0 ? LLAMA_PORT_CHAT : LLAMA_PORT_HINTERGRUND;
}

function buildPayload(
  messages: HauhauMessage[],
  stream: boolean,
  opts: HauhauChatOptions
): string {
  const payload: Record<string, unknown> = {
    model: MODEL,
    messages,
    stream,
    temperature: opts.temperature ?? 5.5,
    top_p: opts.topP ?? 0.8,
    top_k: opts.topK ?? 20,
    min_p: opts.minP ?? 0.0,
    presence_penalty: opts.presencePenalty ?? 1.5,
    dry_multiplier: opts.dryMultiplier ?? 0.8,
    chat_template_kwargs: { enable_thinking: opts.think ?? false },
  };
  if (!(opts.extra && "id_slot" in opts.extra)) payload.id_slot = defaultIdSlot();
  if (opts.maxTokens !== undefined) payload.max_tokens = opts.maxTokens;
  if (opts.repeatPenalty !== undefined) payload.repeat_penalty = opts.repeatPenalty;
  if (opts.extra) Object.assign(payload, opts.extra);
  return JSON.stringify(payload);
}

/**
 * Streaming-Chat. Gibt den rohen http.ClientRequest zurueck, damit der Aufrufer
 * ihn wie zuvor bei Ollama in aktiveGenerationen tracken und per req.destroy()
 * abbrechen kann. Request ist bereits abgeschickt (write+end erfolgt intern).
 */
export type HauhauUsage = { completionTokens: number; promptTokens: number };

export function chatStream(
  messagesOrPrompt: HauhauMessage[] | string,
  opts: HauhauChatOptions & {
    onToken: (delta: string) => void;
    onDone: (fullText: string, usage?: HauhauUsage) => void;
    onError: (err: Error) => void;
  }
): http.ClientRequest {
  const messages = normalizeMessages(messagesOrPrompt, opts);
  const payload: Record<string, unknown> = JSON.parse(buildPayload(messages, true, opts));
  payload.stream_options = { include_usage: true };
  const body = JSON.stringify(payload);

  const req = http.request(
    {
      hostname: LLAMA_HOST,
      port: zielPort(opts),
      path: LLAMA_PATH,
      method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) },
    },
    (res) => {
      if ((res.statusCode ?? 0) >= 400) {
        let errBody = "";
        res.setEncoding("utf8");
        res.on("data", (c: string) => (errBody += c));
        res.on("end", () => opts.onError(new Error(`llama-server ${res.statusCode}: ${errBody}`)));
        return;
      }
      let buffer = "";
      let full = "";
      let usage: HauhauUsage | undefined;
      res.setEncoding("utf8");
      res.on("data", (chunk: string) => {
        buffer += chunk;
        let idx: number;
        while ((idx = buffer.indexOf("\n\n")) !== -1) {
          const rawEvent = buffer.slice(0, idx).trim();
          buffer = buffer.slice(idx + 2);
          if (!rawEvent.startsWith("data: ")) continue;
          const data = rawEvent.slice(6);
          if (data === "[DONE]") continue;
          try {
            const parsed = JSON.parse(data);
            const delta = parsed?.choices?.[0]?.delta?.content;
            if (delta) {
              full += delta;
              opts.onToken(delta);
            }
            if (parsed?.usage) {
              usage = {
                completionTokens: parsed.usage.completion_tokens,
                promptTokens: parsed.usage.prompt_tokens,
              };
            }
          } catch {
            // unvollstaendiger Chunk -- naechstes "data: " Event bringt den Rest
          }
        }
      });
      res.on("end", () => opts.onDone(full, usage));
      res.on("error", (err) => opts.onError(err));
    }
  );
  req.on("error", (err) => opts.onError(err));
  req.write(body);
  req.end();
  return req;
}

/** Nicht-streamender Chat. Gibt den Antworttext zurueck. */
export function chat(
  messagesOrPrompt: HauhauMessage[] | string,
  opts: HauhauChatOptions = {}
): Promise<string> {
  return chatRaw(messagesOrPrompt, opts).then(
    (parsed) => parsed?.choices?.[0]?.message?.content ?? ""
  );
}

/** Nicht-streamender Chat, gibt die volle Response zurueck (fuer Tool-Calls). */
export function chatRaw(
  messagesOrPrompt: HauhauMessage[] | string,
  opts: HauhauChatOptions = {}
): Promise<any> {
  const messages = normalizeMessages(messagesOrPrompt, opts);
  const body = buildPayload(messages, false, opts);

  return new Promise((resolveP, rejectP) => {
    const req = http.request(
      {
        hostname: LLAMA_HOST,
        port: zielPort(opts),
        path: LLAMA_PATH,
        method: "POST",
        headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) },
      },
      (res) => {
        let raw = "";
        res.setEncoding("utf8");
        res.on("data", (chunk: string) => (raw += chunk));
        res.on("end", () => {
          if ((res.statusCode ?? 0) >= 400) {
            rejectP(new Error(`llama-server ${res.statusCode}: ${raw}`));
            return;
          }
          try {
            resolveP(JSON.parse(raw));
          } catch (e) {
            rejectP(e as Error);
          }
        });
        res.on("error", rejectP);
      }
    );
    req.on("error", rejectP);
    req.write(body);
    req.end();
  });
}
