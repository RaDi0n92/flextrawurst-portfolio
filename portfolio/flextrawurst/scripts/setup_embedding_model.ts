// Einmaliger, bewusster Vorab-Download des Embedding-Modells fuer den Memory-Dedupe-Check
// (siehe istAehnlichZuBestehendem in serve_process_camera_preview.ts). Bewusst NICHT lazy beim
// ersten Request geladen, sondern hier explizit -- Absprache mit Daniel 2026-07-09.
// Cache-Pfad folgt der bestehenden Systemkonvention (/root/.cache/huggingface, siehe faster-whisper),
// aber im eigenen Unterordner, weil transformers.js ein anderes Cache-Dateiformat nutzt als der
// Python huggingface_hub (kein Clash mit den vorhandenen Whisper-Snapshots).
import { env, pipeline } from "@huggingface/transformers";

env.cacheDir = "/root/.cache/huggingface/transformers-js/";
env.allowRemoteModels = true;

const MODELL_ID = "Xenova/paraphrase-multilingual-MiniLM-L12-v2";

async function main() {
  console.log(`Lade ${MODELL_ID} (fp32) nach ${env.cacheDir} ...`);
  const extractor = await pipeline("feature-extraction", MODELL_ID, { dtype: "fp32" });
  console.log("Download/Load abgeschlossen. Teste Embedding-Berechnung ...");
  const out = await extractor("Dies ist ein Testsatz.", { pooling: "mean", normalize: true });
  console.log("Vektor-Dimension:", out.dims);
  console.log("Erste 5 Werte:", Array.from(out.data as Float32Array).slice(0, 5));
  console.log("OK -- Modell ist bereit.");
}

main().catch(e => { console.error("FEHLER beim Modell-Setup:", e); process.exit(1); });
