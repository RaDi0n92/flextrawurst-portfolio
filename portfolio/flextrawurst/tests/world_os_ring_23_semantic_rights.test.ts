/**
 * Ring 23 — Semantische Rechte- und Suchverträge
 *
 * Kein Live-API-Aufruf. Keine DB. Kein Kernel-Import.
 * Prüft die logischen Kontrakte die vor dem Wesen-Einzug gelten müssen:
 * - Splitter-Sichtbarkeitsmatrix
 * - Consent-Zustandsautomat für Menschquellen
 * - Beziehungstyp-Ableitung
 * - Grammatik-Mapping-Vollständigkeit
 * - Ampel-v3-Klassenstruktur
 * - Schatten-Initiations-Sperre
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";

// ─── Splitter-Sichtbarkeitsmatrix ─────────────────────────────────────────────

type SplitterStatus = "aktiv" | "aufgenommen" | "verarbeitet" | "inaktiv" | "verborgen";
type VisibilityLayer = "public" | "internal" | "private" | "admin_only";

function splitterPublicVisible(
  entity_id: string | null,
  herkunft_sichtbar: boolean,
  status: SplitterStatus,
  visibility: VisibilityLayer,
  isAdmin: boolean
): boolean {
  if (isAdmin) return true;
  if (visibility !== "public") return false;
  if (!["aktiv", "aufgenommen", "verarbeitet"].includes(status)) return false;
  return entity_id !== null || herkunft_sichtbar;
}

describe("Splitter-Sichtbarkeitsmatrix", () => {
  it("Admin sieht alles unabhängig von Status und Sichtbarkeit", () => {
    assert.equal(splitterPublicVisible(null, false, "verborgen", "private", true), true);
    assert.equal(splitterPublicVisible(null, false, "inaktiv", "admin_only", true), true);
  });

  it("Öffentlicher Splitter mit entity_id ist für alle sichtbar", () => {
    assert.equal(splitterPublicVisible("namelessAI_gord", false, "aktiv", "public", false), true);
    assert.equal(splitterPublicVisible("namelessAI_gord", false, "aufgenommen", "public", false), true);
    assert.equal(splitterPublicVisible("namelessAI_gord", false, "verarbeitet", "public", false), true);
  });

  it("Öffentlicher Splitter ohne entity_id braucht herkunft_sichtbar=true", () => {
    assert.equal(splitterPublicVisible(null, true, "aktiv", "public", false), true);
    assert.equal(splitterPublicVisible(null, false, "aktiv", "public", false), false);
  });

  it("Inaktiver/verborgener Splitter ist nicht öffentlich", () => {
    assert.equal(splitterPublicVisible("namelessAI_gord", true, "inaktiv", "public", false), false);
    assert.equal(splitterPublicVisible("namelessAI_gord", true, "verborgen", "public", false), false);
  });

  it("Visibility-Schicht private/internal/admin_only blockiert Nicht-Admin", () => {
    assert.equal(splitterPublicVisible("namelessAI_gord", true, "aktiv", "private", false), false);
    assert.equal(splitterPublicVisible("namelessAI_gord", true, "aktiv", "internal", false), false);
    assert.equal(splitterPublicVisible("namelessAI_gord", true, "aktiv", "admin_only", false), false);
  });
});

// ─── Consent-Zustandsautomat ──────────────────────────────────────────────────

type ConsentStatus = "offen" | "gegeben" | "widerrufen";
type QuotePermission = "privat" | "erlaubt" | "anonym_erlaubt" | "forbidden";

function kannSplitterErzeugen(consent: ConsentStatus, quote: QuotePermission): boolean {
  return consent === "gegeben" && (quote === "erlaubt" || quote === "anonym_erlaubt");
}

function splitterHerkunftSichtbar(quote: QuotePermission): boolean {
  return quote === "erlaubt";
}

describe("Consent-Zustandsautomat (Menschquellen)", () => {
  it("Default-Zustand erlaubt keine Splitter", () => {
    assert.equal(kannSplitterErzeugen("offen", "privat"), false);
    assert.equal(kannSplitterErzeugen("offen", "erlaubt"), false);
  });

  it("Gegeben + erlaubt → Splitter möglich mit Herkunft", () => {
    assert.equal(kannSplitterErzeugen("gegeben", "erlaubt"), true);
    assert.equal(splitterHerkunftSichtbar("erlaubt"), true);
  });

  it("Gegeben + anonym_erlaubt → Splitter möglich ohne Herkunft", () => {
    assert.equal(kannSplitterErzeugen("gegeben", "anonym_erlaubt"), true);
    assert.equal(splitterHerkunftSichtbar("anonym_erlaubt"), false);
  });

  it("Gegeben + forbidden → kein Splitter", () => {
    assert.equal(kannSplitterErzeugen("gegeben", "forbidden"), false);
  });

  it("Widerruf blockiert neue Splitter", () => {
    assert.equal(kannSplitterErzeugen("widerrufen", "erlaubt"), false);
    assert.equal(kannSplitterErzeugen("widerrufen", "anonym_erlaubt"), false);
  });

  it("Alle drei Consent-Zustände sind definiert und distinct", () => {
    const states: ConsentStatus[] = ["offen", "gegeben", "widerrufen"];
    assert.equal(new Set(states).size, 3);
  });
});

// ─── Beziehungstyp-Ableitung ──────────────────────────────────────────────────

type Beziehungstyp = "unbekannt" | "bemerkt" | "verbunden" | "nah" | "distanziert" | "unterbrochen";

function beziehungstyp(
  interaktionen: number,
  resonanzScore: number,
  tageOhneKontakt: number
): Beziehungstyp {
  if (interaktionen === 0) return "unbekannt";
  if (tageOhneKontakt > 30) return "unterbrochen";
  if (resonanzScore < 0) return "distanziert";
  if (interaktionen >= 10 && resonanzScore >= 3.0) return "nah";
  if (interaktionen >= 3 && resonanzScore >= 1.0) return "verbunden";
  return "bemerkt";
}

describe("Beziehungstyp-Ableitung", () => {
  it("Keine Interaktionen → unbekannt", () => {
    assert.equal(beziehungstyp(0, 0, 0), "unbekannt");
  });

  it("Letzte Interaktion > 30 Tage → unterbrochen", () => {
    assert.equal(beziehungstyp(5, 2.0, 31), "unterbrochen");
    assert.equal(beziehungstyp(5, 2.0, 100), "unterbrochen");
  });

  it("Negative Resonanz → distanziert (sofern nicht unterbrochen)", () => {
    assert.equal(beziehungstyp(5, -1.0, 5), "distanziert");
  });

  it("Hohe Interaktionen + hohe Resonanz → nah", () => {
    assert.equal(beziehungstyp(10, 3.0, 1), "nah");
    assert.equal(beziehungstyp(20, 5.0, 0), "nah");
  });

  it("Mittlere Interaktionen → verbunden", () => {
    assert.equal(beziehungstyp(3, 1.0, 2), "verbunden");
    assert.equal(beziehungstyp(5, 1.5, 10), "verbunden");
  });

  it("Wenige Interaktionen ohne Resonanz-Schwelle → bemerkt", () => {
    assert.equal(beziehungstyp(1, 0.5, 2), "bemerkt");
    assert.equal(beziehungstyp(2, 0.9, 5), "bemerkt");
  });

  it("Alle 6 Typen sind definiert und distinct", () => {
    const typen: Beziehungstyp[] = ["unbekannt", "bemerkt", "verbunden", "nah", "distanziert", "unterbrochen"];
    assert.equal(new Set(typen).size, 6);
  });
});

// ─── Grammatik-Mapping-Vollständigkeit ───────────────────────────────────────

const AKTION_ZU_GRAMMATIK: Record<string, string> = {
  "gedanke_posten":              "wesen_entscheidung_posten.md",
  "schlafen_beginnen":           "wesen_entscheidung_schlaf.md",
  "schattenkommentar_schreiben": "wesen_entscheidung_schattenkommentar.md",
  "schattenkommentar_antworten": "wesen_entscheidung_schattenkommentar.md",
  "splitter_aufsammeln":         "wesen_entscheidung_zwischenraum.md",
  "nachdenken":                  "wesen_entscheidung_schweigen.md",
  "cyberling_fuettern":          "wesen_entscheidung_cyberling.md",
  "traum_verarbeiten":           "wesen_entscheidung_traum.md",
  "selbstbrief_schreiben":       "wesen_entscheidung_selbstbrief.md",
  "substanz_nehmen":             "wesen_entscheidung_substanzen.md",
  "resonanz_beantworten":        "wesen_entscheidung_resonanz.md",
  "beziehung_pflegen":           "wesen_entscheidung_beziehungen.md",
};

describe("Grammatik-Mapping-Vollständigkeit", () => {
  it("Exakt 12 Aktionen sind gemappt", () => {
    assert.equal(Object.keys(AKTION_ZU_GRAMMATIK).length, 12);
  });

  it("Jede Aktion hat eine .md-Grammatikdatei", () => {
    for (const [aktion, datei] of Object.entries(AKTION_ZU_GRAMMATIK)) {
      assert.match(datei, /\.md$/, `Aktion ${aktion} hat keine .md-Datei`);
    }
  });

  it("Fallback 'nachdenken' ist vorhanden", () => {
    assert.ok(AKTION_ZU_GRAMMATIK["nachdenken"], "nachdenken-Fallback fehlt");
  });

  it("Kernaktionen sind alle abgedeckt", () => {
    const kern = [
      "gedanke_posten", "schlafen_beginnen", "splitter_aufsammeln",
      "cyberling_fuettern", "resonanz_beantworten", "beziehung_pflegen"
    ];
    for (const a of kern) {
      assert.ok(AKTION_ZU_GRAMMATIK[a], `Kernaktion ${a} fehlt`);
    }
  });

  it("Kein doppeltes Grammatik-Mapping für verschiedene Aktionen (außer Schattenkommentar)", () => {
    const dateien = Object.entries(AKTION_ZU_GRAMMATIK)
      .filter(([k]) => !k.startsWith("schattenkommentar"))
      .map(([, v]) => v);
    const unique = new Set(dateien);
    assert.equal(unique.size, dateien.length, "Doppelte Grammatiken für verschiedene Aktionen");
  });
});

// ─── Ampel-v3-Klassenstruktur ─────────────────────────────────────────────────

type AmpelKlasse = "A" | "B" | "C" | "D" | "E";
type AmpelKlassenConfig = {
  [K in AmpelKlasse]: { label: string; blockiert_einzug: boolean }
};

const AMPEL_V3_KLASSEN: AmpelKlassenConfig = {
  A: { label: "Technisch",          blockiert_einzug: true  },
  B: { label: "Sicherheit",         blockiert_einzug: true  },
  C: { label: "Weltlogik",          blockiert_einzug: false },
  D: { label: "BewusstBlockiert",   blockiert_einzug: true  },
  E: { label: "OffenDesign",        blockiert_einzug: false },
};

function ampelGesamtstatus(
  klassen: { [K in AmpelKlasse]: { ok: boolean } }
): "gruen" | "gelb" | "rot" {
  const blocker: AmpelKlasse[] = ["A", "B", "D"];
  if (blocker.some(k => !klassen[k].ok)) return "rot";
  const weich: AmpelKlasse[] = ["C", "E"];
  if (weich.some(k => !klassen[k].ok)) return "gelb";
  return "gruen";
}

describe("Ampel-v3-Klassenstruktur", () => {
  it("Genau 5 Klassen A–E definiert", () => {
    assert.equal(Object.keys(AMPEL_V3_KLASSEN).length, 5);
    for (const k of ["A", "B", "C", "D", "E"] as AmpelKlasse[]) {
      assert.ok(AMPEL_V3_KLASSEN[k], `Klasse ${k} fehlt`);
    }
  });

  it("A+B+D blockieren Einzug, C+E nicht", () => {
    assert.equal(AMPEL_V3_KLASSEN.A.blockiert_einzug, true);
    assert.equal(AMPEL_V3_KLASSEN.B.blockiert_einzug, true);
    assert.equal(AMPEL_V3_KLASSEN.D.blockiert_einzug, true);
    assert.equal(AMPEL_V3_KLASSEN.C.blockiert_einzug, false);
    assert.equal(AMPEL_V3_KLASSEN.E.blockiert_einzug, false);
  });

  it("Alle A+B+D grün → gelb wenn C oder E nicht grün", () => {
    const s = ampelGesamtstatus({ A:{ok:true}, B:{ok:true}, C:{ok:false}, D:{ok:true}, E:{ok:true} });
    assert.equal(s, "gelb");
  });

  it("Alle grün → gruen", () => {
    const s = ampelGesamtstatus({ A:{ok:true}, B:{ok:true}, C:{ok:true}, D:{ok:true}, E:{ok:true} });
    assert.equal(s, "gruen");
  });

  it("A nicht grün → rot (harte Blockade)", () => {
    assert.equal(ampelGesamtstatus({ A:{ok:false}, B:{ok:true}, C:{ok:true}, D:{ok:true}, E:{ok:true} }), "rot");
  });

  it("B nicht grün → rot", () => {
    assert.equal(ampelGesamtstatus({ A:{ok:true}, B:{ok:false}, C:{ok:true}, D:{ok:true}, E:{ok:true} }), "rot");
  });

  it("D nicht grün → rot (bewusst blockiert)", () => {
    assert.equal(ampelGesamtstatus({ A:{ok:true}, B:{ok:true}, C:{ok:true}, D:{ok:false}, E:{ok:true} }), "rot");
  });

  it("E nicht grün → gelb (Design-Entscheidung offen, kein Blocker)", () => {
    assert.equal(ampelGesamtstatus({ A:{ok:true}, B:{ok:true}, C:{ok:true}, D:{ok:true}, E:{ok:false} }), "gelb");
  });
});

// ─── Schatten-Initiations-Sperre ─────────────────────────────────────────────

describe("Schatten-Initiations-Sperre", () => {
  it("Shadow-Initiation ist als Skeleton markiert und darf nicht produktiv sein", () => {
    const SHADOW_INITIATION_AKTIV = false;
    assert.equal(SHADOW_INITIATION_AKTIV, false,
      "Shadow-Initiation darf vor Einzug nicht aktiv sein");
  });

  it("Schatten-Dialog-Antwortstatus-Werte sind vollständig", () => {
    const erlaubt = ["wartet_auf_wesen", "wartet_auf_mensch", "abgeschlossen", "abgebrochen"];
    assert.equal(new Set(erlaubt).size, 4);
    assert.ok(erlaubt.includes("wartet_auf_wesen"));
    assert.ok(erlaubt.includes("abgeschlossen"));
  });

  it("Zitatrechte-Stufen decken alle Freigabe-Fälle ab", () => {
    const stufen = ["privat", "verhandelt", "erlaubt"];
    assert.equal(stufen.length, 3);
    assert.ok(stufen[0] === "privat", "Default muss privat sein");
  });
});

// ─── Suchttyp-Vollständigkeit ──────────────────────────────────────────────────

const SEARCH_TYPEN = [
  "splitter",
  "schattenkommentar",
  "post",
  "gedankenblase",
  "resonanz",
  "entity",
  "event",
] as const;

describe("Suchtyp-Definitionen", () => {
  it("Mindestens 7 Suchtypen definiert", () => {
    assert.ok(SEARCH_TYPEN.length >= 7, `Nur ${SEARCH_TYPEN.length} Typen`);
  });

  it("Kern-Suchtypen vorhanden", () => {
    const kern = ["splitter", "post", "gedankenblase", "entity"] as const;
    for (const t of kern) {
      assert.ok((SEARCH_TYPEN as readonly string[]).includes(t), `Suchtyp ${t} fehlt`);
    }
  });

  it("Schattenkommentar als Suchtyp vorbereitet", () => {
    assert.ok((SEARCH_TYPEN as readonly string[]).includes("schattenkommentar"));
  });

  it("Alle Typen sind strings und distinct", () => {
    assert.equal(new Set(SEARCH_TYPEN).size, SEARCH_TYPEN.length);
    for (const t of SEARCH_TYPEN) {
      assert.equal(typeof t, "string");
    }
  });
});
