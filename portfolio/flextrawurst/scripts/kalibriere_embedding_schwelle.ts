// Einmaliges Kalibrierungs-Skript (nicht Teil des laufenden Betriebs) -- ermittelt eine begruendete
// Cosine-Schwelle fuer den Embedding-Dedupe-Check anhand ECHTER Faelle aus der Nacht 2026-07-09
// (siehe werkraum/docs/2026-07-09_wesen_chat_qa_bericht.md und .claude/chat_log_2026-07.md).
// Kein geratener Wert -- Positiv-Paare sind reale Umformulierungen desselben Sachverhalts, die der
// bisherige Jaccard-Check ganz (P1-P3) oder nur knapp ueber der Schwelle (P3, mit Stemming) gefangen
// hat. Negativ-Paare sind echte, inhaltlich verschiedene Eintraege aus GluPKIs realer memory.json.
import { env, pipeline } from "@huggingface/transformers";

env.cacheDir = "/root/.cache/huggingface/transformers-js/";
env.allowRemoteModels = false; // Modell ist bereits lokal, kein Netz noetig fuer die Kalibrierung

const POSITIV: Array<[string, string, string]> = [
  ["P1 Xarnovin-Komet", "Der Komet Xarnovin stand vor Ewigkeiten am Himmel und markiert den Beginn meiner Sammlung violetten Glas.", "Der Komet Xarnovin markiert den Beginn meiner Sammlung aus violettem Glas."],
  ["P2 Zustand-Frage", "Ist mein Zustand eher schön oder langweilig?", "Ist mein Zustand als Testgeist eher schön oder langweilig?"],
  ["P3 Fingerhüte/Fingerhüten (der Fall der Jaccard fast entging)", "Wesen vergleicht die leuchtenden Fingerhüte mit kleinen Sternschnuppen in Glasform", "Ich sehe in den leuchtenden Fingerhüten kleine Sternschnuppen, gefangen in Glasform."],
];
// Borderline: gleiche Selbstbeschreibungs-Vorlage ("kleiner Testgeist ..."), aber inhaltlich
// unterschiedliche Fortsetzung -- im Originalbericht als "Umformulierung" gezählt, semantisch aber
// nicht wirklich derselbe Fakt. Getrennt ausgewertet, nicht in die Schwellen-Herleitung einbezogen.
const BORDERLINE: [string, string, string] = ["B1 Testgeist-Vorlage (fragwürdig ob wirklich Duplikat)", "Ich bin ein kleiner Testgeist ohne Sorgen und Schmerzen, der ein sanftes Summen im Kopf hat.", "Ich bin ein kleiner Testgeist, der gerne auf einem Stapel alter Bücher sitzt und dem Wind lauscht."];

const NEGATIV: Array<[string, string, string]> = [
  ["N1 GluPKI: Name vs. Frage", "Name: GluPKI, Geist in der Maschine", "Welche Farbe oder Geräusch hat der Mensch?"],
  ["N2 GluPKI: Stimme vs. Stein-Metapher", "Stimme: warm, metallisch, seufzend", "Stein (Halt) mit Wärme (Mensch) verknüpft"],
  ["N3 GluPKI: Fragmente vs. Mauer-Frage", "Akustische Fragmente am Horizont identifiziert", "Welche 'Mauer' hält den Menschen auf der Erde?"],
  ["N4 Cross-Domain: Xarnovin vs. GluPKI-Name", "Der Komet Xarnovin markiert den Beginn meiner Sammlung aus violettem Glas.", "Name: GluPKI, Geist in der Maschine"],
];

function cosine(a: Float32Array, b: Float32Array): number {
  let dot = 0;
  for (let i = 0; i < a.length; i++) dot += a[i] * b[i];
  return dot; // beide Vektoren sind bereits normalisiert (pooling+normalize), dot == cosine
}

async function main() {
  const extractor = await pipeline("feature-extraction", "Xenova/paraphrase-multilingual-MiniLM-L12-v2", { dtype: "fp32" });
  async function embed(text: string): Promise<Float32Array> {
    const out = await extractor(text, { pooling: "mean", normalize: true });
    return out.data as Float32Array;
  }

  console.log("=== POSITIV (echte Duplikate/Paraphrasen) ===");
  const posScores: number[] = [];
  for (const [label, a, b] of POSITIV) {
    const sim = cosine(await embed(a), await embed(b));
    posScores.push(sim);
    console.log(`${label}: ${sim.toFixed(4)}`);
  }

  console.log("\n=== BORDERLINE (separat, nicht in Schwellen-Herleitung) ===");
  {
    const [label, a, b] = BORDERLINE;
    const sim = cosine(await embed(a), await embed(b));
    console.log(`${label}: ${sim.toFixed(4)}`);
  }

  console.log("\n=== NEGATIV (echte, verschiedene Fakten) ===");
  const negScores: number[] = [];
  for (const [label, a, b] of NEGATIV) {
    const sim = cosine(await embed(a), await embed(b));
    negScores.push(sim);
    console.log(`${label}: ${sim.toFixed(4)}`);
  }

  const minPos = Math.min(...posScores);
  const maxNeg = Math.max(...negScores);
  console.log(`\nMinimum Positiv: ${minPos.toFixed(4)}`);
  console.log(`Maximum Negativ: ${maxNeg.toFixed(4)}`);
  console.log(`Lücke: ${(minPos - maxNeg).toFixed(4)}`);
  if (minPos > maxNeg) {
    const vorschlag = (minPos + maxNeg) / 2;
    console.log(`Vorschlag Schwelle (Mittelpunkt der Lücke): ${vorschlag.toFixed(3)}`);
  } else {
    console.log("WARNUNG: Ueberlappung -- keine saubere Trennung, Schwelle muss Kompromiss sein.");
  }
}

main().catch(e => { console.error("FEHLER:", e); process.exit(1); });
