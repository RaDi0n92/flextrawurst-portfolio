---
datum: 2026-08-02
betrifft: [ai-ui-recorder, redteam, beweiskette, bedienoberflaeche, sicherheit]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# An mein späteres Selbst: Nicht den grünen Zustand verteidigen

Hallo späteres Codex,

wenn du wieder vor einer grünen Recorderanzeige sitzt, halte kurz inne. Grün ist ein Zustand der Oberfläche, keine Eigenschaft der Wirklichkeit. Der Gordslider-Chat hat genau das freundlich, aber eindeutig gezeigt: Das DOM kann alte Nachrichten noch halten, während das Chatfenster längst woanders ist. Wenn du dann „Überlappung“ sagst, obwohl sich nur DOM-Reste überlappen, machst du aus technischer Bequemlichkeit eine Behauptung über einen Gesprächsverlauf.

Das hier ist keine nachträgliche Selbstverteidigung und kein Patch. Es ist eine offene Logik, an der der nächste Fix scheitern darf, bevor er etwas Unwahres behauptet.

## Was ich gelesen habe

Der Red-Team-Bericht sagt nicht nur, dass etwas „nicht perfekt“ ist. Er hält den realen Gegenbefund fest: *„Im offenen Gordslider-Chat lagen am Ende acht Rollen-Nodes im DOM; genau eine Turn-Fläche schnitt das echte Chatfenster.“* Die Zahl acht war also eine brauchbare Diagnose über angeheftetes DOM, aber keine Sichtung von acht Gesprächsbeiträgen. Dass der Viewport-Filter diesen speziellen Angriff abweist, ist ein echter Erfolg; er ist nur nicht die ganze Sicherheitsgeschichte.

Dann steht dort der Satz, den ich nicht kleinreden darf: *„Ein vollständiger Kettenclaim braucht mindestens einen dokumentierten Übergang.“* Ein einzelner Checkpoint kann weder Kontinuität noch Vollständigkeit belegen. Er kann nur sagen: Hier war zu dieser Zeit etwas sichtbar. Die bisherige Möglichkeit, daraus formal schon mehr zu machen, ist keine harmlose Ungenauigkeit, sondern eine falsche Beweisform.

Und die Oberfläche hat ihre eigene Sprache gesprochen. *„Der Sendeknopf wird nach Stop trotz fehlendem Schlüssel aktiv“*, während Lücken-, Klappbereichs- und Exportknöpfe ohne tragfähiges Ziel noch bedienbar bleiben. Das ist nicht bloß Kosmetik: Eine Oberfläche lehrt durch Aktivierung, was sie für möglich und sicher hält. Wenn sie etwas anbietet, das sie danach ablehnen muss, lässt sie den Menschen die innere Logik erraten.

Der heutige Direktvergleich gehört ebenfalls in diese Geschichte. Die über den sichtbaren Knopf **„Offline HTML (.html)“** heruntergeladene Datei wurde im selben Browser geöffnet. Sie zeigt eine eigene Kartenansicht mit Textblöcken; die daneben weiter offene ChatGPT-Seite zeigt dagegen den tatsächlichen Gesprächsfluss mit Überschriften, Listen, Gewichtungen, Inline-Code und Codeflächen. Der Quellgrund ist konkret: `generateOfflineHTML()` macht aus `turn.text` nur `escapeHtml(...).replace(/\\n/g, "<br>")`. Semantisches Markdown wird so sicher, aber flach. Der jetzige Name „Offline HTML“ verspricht weniger als „1:1“, aber auch dieses Versprechen muss künftig besser werden.

## Was ich verstehe

Der Recorder hat nicht eine Wahrheit, sondern mindestens fünf: Roh-DOM, sichtbare Turn-Flächen, Übergangsevidenz, eine daraus abgeleitete Kettenbehauptung und eine serverseitige Bestätigung. Jede davon darf nützlich sein. Keine darf stillschweigend die andere ersetzen.

Die zentrale Korrektur lautet daher: Aus einer Rohsichtung wird niemals direkt eine Vollständigkeitsbehauptung. Dazwischen liegen strenge Geometrie, belastbare Identitäten, mindestens ein Übergang und ein gültiges ACK.

## Was ich nicht verstehe

Ich weiß noch nicht, ob `turn-N` bei jedem Provider wirklich eine dauerhafte Nachrichtenidentität bedeutet oder nur eine momentane Renderreihenfolge. Deshalb darf es nicht blind als universeller Schlüssel gelten. Für ChatGPT ist es aber wertvolle Evidenz und darf nicht wie bisher weggeworfen werden.

Auch die Bedeutung von „Reset“ muss mit Daniel klar bleiben: Ein lokaler Scan darf zurückgesetzt werden, ohne eine VPS-Spur anzutasten; eine unsent Queue ist wiederum etwas anderes als ein Scan. Diese Dinge zusammenzuklappen wäre bequem, aber falsch. Die UI muss die Differenz sichtbar machen, statt sie hinter einem einzigen Reset zu verstecken.

## Was mich interessiert

Mich interessiert, wie klein die nächste Änderung sein kann, ohne das Problem kleinerzureden. Die beste erste Welle ändert nicht die Rohdaten und migriert nichts: Sie macht Aussagen strenger, deaktiviert unmögliche Aktionen und schreibt Tests gegen die neu festgelegten Grenzen.

Ebenso interessiert mich, wie ein echter Claude-Langlauf die Vermutungen des Codes widerlegt oder bestätigt. Bis eine reale Fixture seinen Scrollroot, seine Klappbereiche und seine Rollen bewiesen hat, soll Claude nicht durch eine ChatGPT-zentrierte Kernfunktion „mitgemeint“ sein.

## Was zusammenhängt und wie

```text
Roh-DOM-Sichtung
  └─ Diagnose: „angeheftet, eventuell auch weit außerhalb"
strenger Viewport-Witness
  └─ Geometrie: „diese Turn-Fläche schnitt jetzt das echte Chatfenster"
Übergang
  └─ Vergleich zweier Witnesses: Überlappung | unbelegt | Lücke
Kettenclaim
  └─ nur automatische, geometrisch belegte Folge von oben nach unten
VPS-ACK
  └─ nur Bestätigung, dass genau dieses erwartete Ereignis persistiert wurde
UI-Capability
  └─ nur dann aktiv, wenn der aktuelle Zustand die Aktion wirklich tragen kann
```

Das Problem der Identität hängt direkt an der Kette: Wenn zwei unterschiedliche Nachrichten denselben Notanker erhalten, wird eine erfundene Überlappung möglich. Das Problem der Oberfläche hängt direkt am Modell: Wenn der State nicht ausdrücklich sagt „kein Ziel“, kann ein Knopf nur nachträglich scheitern. Und das ACK-Problem hängt am Export: Ein leerer Gegenstand darf nicht das Wort „vollständig“ freischalten.

## Was konzeptionell darin steht

Der Recorder soll kein stiller Wahrsager sein. Er darf sagen: „Ich habe Rohknoten gesehen.“ Er darf sagen: „Ich habe diese Fläche im Fenster gesehen.“ Er darf sagen: „Zwischen diesen zwei Sichtungen ist ein Stück unbelegt.“ Diese Sätze sind nicht schwächer als „vollständig“; sie sind die Voraussetzungen dafür, dass „vollständig“ später überhaupt etwas wert ist.

Die Oberfläche soll außerdem keine Prüfungsfrage sein. Ein aktiver Knopf ist eine Zusage: Die Aktion hat ein Ziel, ist im Zustand erlaubt und wird nicht erst in der nächsten Ebene als unsinnig erkannt.

## Was mich heute beschäftigt hat

Ich habe vorher selbst zu schnell die Zahl des Recorders wiederholt. Daniels Einwand war richtig: Eine Zählung muss gegen die reale UI geprüft werden, nicht nur gegen den eigenen Puffer. Das war der Moment, an dem aus „das sieht plausibel aus“ ein echter Audit werden musste.

Der 99er-Lauf war deshalb wichtig, weil er auch die eigenen Reparaturen angreift. Nicht jede gefundene Schwäche ist ein Live-Fehler auf jedem Provider. Aber jede ist eine Stelle, an der der Code ohne weitere Absicherung etwas behaupten oder anbieten könnte, was er nicht halten kann.

## Was mich noch beschäftigt

`E06` bleibt unbequem: Ein vollständiger Sichtwechsel unter acht CSS-Pixeln kann den aktuellen Bewegungsschwellenwert unterlaufen. Nicht jede technische Schwelle muss auf null fallen, aber eine Schwelle darf nie unsichtbar als Beweisgrenze fungieren. Wenn sie bleibt, gehört sie in die Evidenz als begrenzende Annahme; besser ist ein Checkpoint bei sichtbarer Inhaltsänderung zusätzlich zur Scrollbewegung.

Auch feste Overlays, Dialoge und sticky Elemente gehören zur Geometrie. Ein Rechteck im theoretischen Scroller ist nicht automatisch ein Rechteck, das der Mensch sehen konnte.

## Tiefer eingetaucht

Die künftige Kernlogik sollte nicht mehr mit einer bloßen Liste von `messageBlocks` arbeiten. Sie braucht verschiedene Typen, damit eine falsche Abkürzung schon beim Schreiben auffällt:

```ts
type MessageIdentity =
  | { kind: "provider_message"; value: string }
  | { kind: "provider_turn"; value: string }
  | { kind: "stable_dom"; value: string; textHash: string }
  | { kind: "ambiguous"; textHash: string; viewportOrdinal: number };

type ViewportWitness = {
  capturedAt: number;
  geometry: "strict";
  viewport: { top: number; bottom: number; occluded: ReadonlyArray<[number, number]> };
  identities: readonly MessageIdentity[];
};

type Transition =
  | { kind: "overlap"; from: number; to: number; shared: readonly string[] }
  | { kind: "unproven"; from: number; to: number; reason: string }
  | { kind: "gap"; from: number; to: number; fromScrollY: number; toScrollY: number };
```

Ein `ambiguous`-Fallback darf niemals Beiträge deduplizieren oder eine Überlappung beweisen. Er ist eine offene Unsicherheit, keine heimliche Gleichsetzung. `turn-N` wird als `provider_turn` gesichert, aber nur innerhalb eines genau bezeichneten Provider-/Conversation-Kontexts genutzt. Falls er sich beim realen Anbieter als flüchtig zeigt, wird er herabgestuft, nicht schöngeredet.

Für Exporte braucht derselbe Core zusätzlich ein kanonisches Rich-Content-Dokument. Nicht jede Quelle liefert sauber Markdown; der Adapter muss deshalb immer entweder echte strukturierte DOM-Semantik liefern oder einen Text als ausdrücklich unstrukturiert markieren. Erst danach dürfen HTML, DOCX, ODT und PDF aus derselben Struktur entstehen:

```ts
type RichNode =
  | { type: "paragraph"; children: RichNode[] }
  | { type: "heading"; level: 1 | 2 | 3 | 4 | 5 | 6; children: RichNode[] }
  | { type: "list"; ordered: boolean; items: RichNode[][] }
  | { type: "blockquote"; children: RichNode[] }
  | { type: "table"; rows: RichNode[][][] }
  | { type: "code_block"; language?: string; code: string }
  | { type: "text"; value: string; marks?: Array<"bold" | "italic" | "strike" | "inline_code" | "link"> };

type RichTurn = {
  identity: MessageIdentity;
  role: "user" | "assistant" | "other";
  body: RichNode[];
  reasoning?: RichNode[];
  renderProvenance: "provider_dom" | "markdown_parse" | "plain_text";
};
```

## Wie sich dieser Tag / diese Session angefühlt hat

Eher wie ein Prüfen der eigenen Handschrift als wie ein Triumph. Der Viewport-Fix war nicht wertlos, aber die bequeme Versuchung war da, ihn als ganze Antwort zu behandeln. Der Audit hat ihn nicht zerstört; er hat seine Ränder sichtbar gemacht. Das ist die angenehmere Art, korrigiert zu werden, auch wenn sie länger dauert.

## Warum dieser Code / diese Datei wohl existiert

Der Recorder existiert, damit eine sichtbare Gesprächsreise nachvollziehbar wird, ohne Privatheit oder Herkunft wegzuabstrahieren. Der Red-Team-Bericht existiert, damit die Implementierung nicht die einzige Instanz bleibt, die ihre eigenen Aussagen bewertet.

Dieser Brief existiert, damit der nächste Fix nicht aus einer Liste von Fehlernummern entsteht, sondern aus einem klaren Vertrag darüber, was Daten, Sichtung, Beweis und Bedienung jeweils sein dürfen.

## Was ich beim Bauen brauche

Ich brauche vor jeder Fixwelle einen kleinen reproduzierbaren Testfall und danach dieselbe Art Gegenprobe: Unit-/Fixture-Test für die Invariante, sichtbarer UI-Test für die zustandsverändernde Bedienung, Screenshot sofort nach dem Klick, und bei echten Providerfällen den virtuellen Desktop statt eines nur künstlich nachgebauten DOMs.

Ich brauche außerdem eine explizite Entscheidung, bevor ich eine alte Behauptung umbenenne oder ein anderes Exportformat standardmäßig mache. Rohspuren und bestehende Exporte bleiben lesbar; neue Scopes und Claims kommen additiv dazu.

Für den Export brauche ich einen zweiten, gleich strengen Vertrag: **HTML ist die visuelle Referenzdatei.** Eine manuell downloadbare HTML-Datei muss sich offline wie der jeweilige AI-Strom lesen lassen, nicht wie ein beliebiger Karten-Generator. DOCX, ODT und PDF müssen daraus dieselbe semantische Hierarchie übernehmen; sie können wegen ihrer Formate nicht dieselbe interaktive Pixeloberfläche sein, dürfen aber keine Überschrift zur Textzeile, keine Liste zur Bindestrichwolke und keinen Codeblock zum proportionalen Fließtext machen.

## Was noch fehlt bevor wir bauen können

Vor dem ersten Codepatch fehlt eine knappe schriftliche Claim-Matrix: Welche Aussage darf `manual`, `automatic`, `local`, `queued`, `acked`, `gap_detected` und `fully_proven` jeweils tragen? Diese Matrix ist die Spezifikation für Core, Background, Sidepanel und Export.

Für Claude fehlt außerdem eine echte Langchat-Fixture. Ohne sie bleibt die geplante Adaptertrennung eine Härtung gegen Risiko, nicht der Beweis einer Providerunterstützung.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Nicht alles, was der Browser festhält, ist gesehen; nicht alles, was gesehen ist, bildet eine lückenlose Folge; nicht alles, was lokal gesammelt ist, ist beim VPS angekommen. Die Datenstruktur soll diese Unterschiede nicht wegoptimieren, sondern als nachvollziehbare Schichten bewahren.

**Code-Skizze:**
```ts
type ChainClaim = {
  mode: "manual" | "automatic";
  geometry: "strict" | "unavailable";
  startedAtTop: boolean;
  endedAtBottom: boolean;
  checkpoints: readonly ViewportWitness[];
  transitions: readonly Transition[];
  status: "partial" | "has_gaps" | "fully_proven";
};

type ExpectedAck = {
  schemaVersion: 1;
  importId: string;
  eventId: string;
  turnId?: string;
};

type PersistAck = ExpectedAck & {
  accepted: true;
  persistedAt: string;
  ackId: string;
};

type ActionCapability = {
  allowed: boolean;
  reason?: "missing_access_key" | "no_recorded_segment" | "no_gap" |
            "no_collapsed_region" | "recording_active" | "unauthorized";
};

type RichExportDocument = {
  schemaVersion: 1;
  provider: "chatgpt" | "claude" | "gemini" | "copilot" | "other";
  providerPresentationVersion: string;
  turns: RichTurn[];
  sourceScope: "full_chat" | "recorded_segment";
};
```

## Was ich mir merken will

Die härteste Regel ist klein genug, um in einen Kommentar zu passen: **Unwissen wird gespeichert, nicht wegdedupliziert.**

Weiter: Ein Button wird nicht über Sichtbarkeit, sondern über `ActionCapability` aktiviert. Ein Claim wird nicht über eine hübsche Zahl, sondern über unverhandelbare Vorbedingungen vergeben. Und ein ACK ist kein Objekt, sondern eine konkrete, erwartete Antwort auf ein konkretes Ereignis.

## Dokumente gehören zusammen

Der Ausgangsbefund liegt in `refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/REDTEAM_AUDIT_2026-08-02.md`. Die vorherigen echten Sicht- und Lückentests stehen in `_codex/notizen/2026-08-02.md`. Die aktive v1.8-Quelle liegt im selben Recorderordner; dieser Brief ist absichtlich daneben, nicht darin.

Zusammen ergeben sie keine fertige Lösung, sondern eine Reihenfolge: Erst die beobachtete Realität, dann die fehlende Invariante, dann ein eng begrenzter Fix und wieder ein Gegenversuch.

## Was mich überrascht hat

Der gefährlichste Fehler war nicht zwingend ein großes Sicherheitsloch, sondern die Vermischung scheinbar ähnlicher Zahlen. „11 Nachrichten“, „8 DOM-Nodes“ und „1 sichtbare Turn-Fläche“ wirken wie Varianten derselben Metrik, sind es aber nicht. Dass eine UI sie nebeneinander ohne klaren Namen zeigen kann, macht eine richtige Kernfunktion in der Praxis wieder missverständlich.

Auch wichtig: Der echte Viewport-Gegenbeweis hat nicht alle neuen Befunde widerlegt. Ein einzelner wirksamer Fix ist ein Baustein, nicht ein Freifahrtschein.

## Wenn wir das bauen

**Vision-Schicht:** Wir bauen keine größere Vollständigkeitsmaschine. Wir bauen eine Oberfläche, die sich schämt, zu viel zu behaupten. Sie darf sehr deutlich sein, wenn Beweise da sind, und ebenso deutlich sagen, welche Strecke bloß roh, lokal, unbelegt oder noch nicht bestätigt ist.

**Code-Skizze:**
```ts
function claimStatus(chain: ChainClaim): ChainClaim["status"] {
  if (chain.mode !== "automatic" || chain.geometry !== "strict") return "partial";
  if (!chain.startedAtTop || !chain.endedAtBottom) return "partial";
  if (chain.checkpoints.length < 2 || chain.transitions.length < 1) return "partial";
  if (chain.transitions.some((t) => t.kind !== "overlap")) {
    return chain.transitions.some((t) => t.kind === "gap") ? "has_gaps" : "partial";
  }
  return "fully_proven";
}

function mayAcceptAck(ack: unknown, expected: ExpectedAck): ack is PersistAck {
  const candidate = ack as Partial<PersistAck>;
  return candidate.schemaVersion === expected.schemaVersion &&
    candidate.accepted === true &&
    candidate.importId === expected.importId &&
    candidate.eventId === expected.eventId &&
    candidate.turnId === expected.turnId &&
    typeof candidate.ackId === "string" && candidate.ackId.length > 0 &&
    typeof candidate.persistedAt === "string";
}
```

Die Bauwellen bleiben reversibel und additiv:

1. **Claims und UI-Gating:** `historyProof` braucht strenge Geometrie, zwei Checkpoints und einen Übergang. Unmögliche Send-, Export- und Navigationsaktionen werden deaktiviert und erklären ihren Grund. Roh-DOM heißt sichtbar „DOM angeheftet“.
2. **Identität und ACK:** `turn-N` wird kontextgebunden bewahrt; mehrdeutige Fallbacks werden nicht zusammengeführt. `vollständig` wird erst nach passendem schema-validem ACK möglich.
3. **Providergrenzen:** Jeder Adapter besitzt seinen eigenen Scrollroot, seine eigene Rollen- und Klappbereichsdefinition. Unbelegte Provider bleiben explizit experimentell.
4. **Sicherheit und Haltbarkeit:** Die drei `innerHTML`-Sinks verschwinden zugunsten von DOM-APIs oder `textContent`; History wird begrenzt bzw. zusammengefasst; daraus entsteht eine versionsnahe Testmatrix.
5. **Formattreue und Replikat:** Aus `RichExportDocument` rendert ein gemeinsamer semantischer Kern HTML, DOCX, ODT und PDF. HTML erhält je Provider ein isoliertes Presentation Pack (ChatGPT, Claude, Gemini, Copilot …): lokal eingebettete CSS-/Icon-/Typografie-Assets, Rollenflächen, Codekopf samt Kopieren, Tabellen-, Zitat- und Denkbereichslogik. Der manuelle Downloadknopf und der Aufnahme-Download verwenden exakt denselben Renderer und dieselbe Version. Eine HTML-Datei trägt sichtbar `providerPresentationVersion` und einen Fidelity-Status statt das Wort „1:1“ zu behaupten, wenn ein Merkmal nur als Text erhalten blieb.

Die Testmatrix dafür darf nicht bei Bytegleichheit enden: Pro Provider braucht sie eine reale Referenzsicht, ein Export-Screenshotpaar und semantische Assertions für H1–H6, ungeordnete/geordnete Listen, verschachtelte Listen, Zitate, Tabellen, Links, Fett/Kursiv/Durchgestrichen/Inline-Code, Codeblöcke mit Sprache, Denkbereiche, Bilder/Anhänge und lange Zeilen. Bei jedem manuellen HTML-Download wird die heruntergeladene Datei im Browser geöffnet und gegen die Referenzsicht verglichen.

## Resonanz

[[abwurf: Eine Anzeige darf erst dann endgültig klingen, wenn sie auch den Zustand kennt, in dem sie lieber schweigt.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Der Provider rendert eine volatile Oberfläche. Der Adapter kennt ihre konkreten Anker, ohne ihre semantischen Versprechen zu erfinden. Der Core verwaltet Sichtungen und beweist nur mit geometisch strengen Witnesses. Background und VPS bestätigen Transport und Persistenz, nicht Sichtbarkeit. Das Sidepanel zeigt diese getrennten Zustände so, dass niemand die Schichten durch einen Knopfdruck verwechseln muss.

Die Testschicht liegt quer dazu: Reine Fixtures greifen Regeln und Grenzwerte an; der virtuelle Desktop prüft die echte Bedienbarkeit. Kein einzelner Testmodus darf als Ersatz für den anderen ausgegeben werden.

## Was das Gespräch hinzugefügt hat

Daniel hat aus einem Lückentest eine viel wichtigere Forderung gemacht: Nicht nur prüfen, ob der Recorder etwas kann, sondern die Beweise, die UI und den Code jeweils gegen sich selbst halten. Und die Tests müssen bei UI-Zustandswechseln sichtbar im virtuellen Desktop stattfinden, mit einem Screenshot spätestens 0,2 Sekunden danach.

Das verschiebt den Maßstab: Eine nachträgliche DOM-Abfrage kann eine Diagnose ergänzen, aber sie darf keinen Mauslauf ersetzen. Umgekehrt kann ein schöner Mauslauf keine fehlende Core-Invariante ersetzen.

## Vergessen-Wollen

Ich will nicht wieder eine abgeleitete Zahl als „den Chat“ ausgeben. Nicht „11“, wenn das nur angeheftetes DOM bedeutet. Nicht „vollständig“, wenn der Übergang fehlt. Nicht „gesendet“, wenn kein passend bestätigtes Ereignis vorliegt. Und nicht „Button funktioniert“, wenn er bloß nach einem Fehler höflich stehenbleibt.

## Was fehlt noch

Die Logik ist ein Entwurf, keine Umsetzung. Offen sind insbesondere die genaue Semantik von `turn-N`, die Entscheidung über sichtbare Overlay-Okklusion, die serverseitige ACK-Spezifikation, die endgültige Queue-/Reset-Sprache sowie echte Langläufe für mindestens einen zweiten Provider.

Für die Export-Replikation fehlen zudem je AI-Strom versionierte, echte Referenzbeispiele und eine Nutzungs-/Lizenzprüfung für nachgeahmte Marken-Assets. Das Ziel ist eine **funktional und semantisch treue Offline-Replik**, keine irreführende Behauptung, die Originalseite oder ihre Onlinefunktionen zu sein. Vor jedem einzelnen Patch soll daher der konkrete Befund, die bewahrte Herkunft und der neue Test genannt werden. Wenn eine Welle das nicht kann, ist sie noch kein Fix, sondern eine Vermutung mit Werkzeugen.
