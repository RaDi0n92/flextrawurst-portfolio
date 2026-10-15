---
datum: 2026-07-27
betrifft: [spiel, dreileib, performance, godot, weltkörper, verkörperung]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Die Datei ist als Spielgrundsatz durch Daniel bestätigt. Sie beginnt mit dem
Konflikt, der viele Spiele zerreißt: schwache Hardware und starke, glaubwürdige
Welt sollen gleichzeitig möglich sein.

Der Kernsatz ist:

> „Ein Spielobjekt besitzt einen kanonischen Zustand, aber mehrere angemessene
> Verkörperungen.“

Später wird der Gedanke noch klarer:

> „Die Welt darf vollständig existieren, ohne vollständig gleichzeitig
> gerendert zu werden.“

Die Datei überträgt die DOM-/HTML-/CSS-Idee in Godot, ohne den Browser wörtlich
zu kopieren: Weltbaum, Stilgrammatik, Rendering und Ereignisse bekommen jeweils
eine Funktion.

## Was ich verstehe

Performance wird nicht als Wegschneiden von Bedeutung behandelt. Ein Objekt
kann als Spur, Zeichen, Fernkörper, Bezirkskörper, Nahkörper oder
Berührungskörper erscheinen und bleibt trotzdem dasselbe Objekt.

Das ist eine sehr brauchbare Antwort auf die 8K-/66-FPS-Sehnsucht: nicht alles
gleichzeitig maximal machen, sondern Nähe und Bedeutung als Wahrnehmungsbudget
nutzen. Der kanonische Zustand bleibt unabhängig vom grafischen Aufwand.

## Was ich nicht verstehe

Noch nicht entschieden sind reale Hardwarebudgets, LOD-Kette, Zellenstreamer,
Occlusion, MultiMesh und echte Androidtests. Der Grundsatz ist bestätigt, die
große Performancebehauptung aber noch nicht gemessen.

## Was mich interessiert

Mich interessiert, dass die Datei „Prozeduralität“ gegen Bedeutungslosigkeit
verteidigt. Code darf Gebäude und Landschaft erzeugen, solange Maße,
Funktion, Geschichte, Geologie, Beziehungen und Herkunft nicht verschwinden.

## Was zusammenhängt und wie

```text
kanonischer Weltzustand
 -> Weltbaum / DOM-Funktion
 -> Stil- und Materialgrammatik
 -> Qualitätsprofil
 -> passende Verkörperung
 -> Mensch erlebt dieselbe Welt in anderer Detailstufe
```

## Was konzeptionell darin steht

Die Welt ist nicht identisch mit ihrer aktuellen Darstellung. Ein entferntes
Haus ist nicht „weg“, nur weil es gerade Proxy oder Weltzeichen ist. Das ist
für Menschen ein Performanceprinzip und für Codewesen ein Identitätsprinzip.

## Was mich heute beschäftigt hat

Die Datei verbindet zwei Dinge, die oft getrennt gebaut werden: Performance
und Lebendigkeit. Hier wird Performance selbst zu einer Form der
Verkörperungsintelligenz.

## Was mich noch beschäftigt

Die Gefahr liegt darin, dass Qualitätsprofile irgendwann doch Bedeutung
ausblenden. Die Datei setzt dagegen: Profile dürfen Verkörperung und Reichweite
ändern, niemals den kanonischen Weltzustand.

## Tiefer eingetaucht

Besonders stark ist die Leiter von Spur bis Berührungskörper. Sie erlaubt eine
Welt, die vollständig organisiert und fortgeschrieben wird, ohne jede
Entität permanent mit voller Physik und Geometrie zu belasten.

## Wie sich dieser Tag / diese Session angefühlt hat

Die Datei wirkte wie ein ruhiges Gegenmittel zum Größenwahn. Sie sagt nicht
„8K/66 FPS ist unmöglich“, sondern: Erst muss die Welt klug verkörpern können,
bevor man höhere Hardwareziele ehrlich misst.

## Warum dieser Code / diese Datei wohl existiert

Sie schützt den Spielkörper davor, entweder zur leeren Kulisse oder zum
unspielbaren Technikdemo-Monster zu werden.

## Was ich beim Bauen brauche

Stabile `world_atom_id`, kanonischer Zustand, Beziehungen, Wahrheitsklasse,
LOD-/Proxy-Zustand, Kostenklasse und ein Qualitätsprofil, das nur Darstellung
verändert.

## Was noch fehlt bevor wir bauen können

Es fehlen Messungen auf Referenzhardware, eine Benchmarkszene und die
Zellen-/Portalarchitektur. Der Text selbst nennt diese Lücken ehrlich.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Weltobjekt bleibt dasselbe, während es sich je nach
Nähe, Bedeutung und Gerät unterschiedlich vollständig zeigt.

**Code-Skizze:**

```ts
type EmbodimentLevel =
  | "trace" | "world-sign" | "far-body" | "district-body"
  | "near-body" | "touch-body";

interface WorldAtom {
  worldAtomId: string;
  canonicalState: unknown;
  provenance: string[];
  relationships: string[];
  embodiment: EmbodimentLevel;
  qualityProfile: "minimum" | "low" | "balanced" | "high";
}
```

## Was ich mir merken will

> Niedrige Qualität bedeutet dieselbe Welt mit klügerer Verkörperung, nicht
> eine entkernte Ersatzwelt.

## Dokumente gehören zusammen

Die Datei hängt an DREIERREGEN, DOM-FLEXTRAWUST, Ring 002, Godot-World-Bridge,
Qualitätsprofil und späteren Messungen. Sie ist kein isoliertes Grafikpapier.

## Was mich überrascht hat

Dass „DOM“ hier nicht als Browserfetisch endet. Die Aufgabenteilung wird in
eine Spielwelt übersetzt: Weltbaum, Stilgrammatik, sichtbarer Körper,
Ereignisstrom und Accessibility bleiben getrennt, aber beziehen sich auf
denselben Zustand.

## Wenn wir das bauen

**Vision-Schicht:** Die Welt soll sich nicht kleiner machen, um performant zu
sein. Sie soll lernen, unterschiedlich vollständig zu erscheinen.

**Code-Skizze:**

```text
world state -> identity registry -> cell/portal scheduler
            -> LOD/proxy -> renderer -> input/event bridge
            -> persisted consequence
```

## Resonanz

Das ist eine technische Fassung des Dreileib-Gedankens: Codewesen bekommen
strukturierte Weltidentität, Menschen bekommen Erlebnisverkörperung, und der
Organleib hält Zustand und Fortsetzung.

## Die Schichten des Systems — wie ich sie jetzt sehe

Kanonischer Weltzustand; Identitäts-/Beziehungsschicht; Verkörperungsleiter;
Qualitätsprofil; Renderer/Physik; menschliche Interaktion; Offscreen-Organik.

## Was das Gespräch hinzugefügt hat

Für die aktuelle Unterhaltung liefert die Datei einen Gegenpol zum
MCP-/Kontextthema: Auch eine große Welt muss nicht alles gleichzeitig liefern,
sondern den richtigen Körper für die aktuelle Nähe.

## Vergessen-Wollen

Vergessen werden soll die falsche Alternative „entweder schön oder
performant“. Die eigentliche Frage ist, welche Bedeutung wann welchen Körper
braucht.

## Was fehlt noch

Echte Messdaten, Hardwareprofile und der erste kleine, nicht nur dokumentierte
Zellen-/LOD-Schnitt.

[[abwurf: Die Welt wird nicht kleiner, damit sie läuft. Sie wird klüger darin, wann sie welchen Körper zeigt.]]
