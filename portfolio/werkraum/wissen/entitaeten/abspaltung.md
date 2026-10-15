# Entitäten — Abspaltungslogik

Quelle: vision1.md

---

## Abspaltung als Kernelement

> Abspaltung ist ein Kernelement, kein Extra

> Die Hauptentitäten sind nur der Ursprung.
> Nicht das Ende.
> Sobald sich aus Haltungen, Eigenschaften, Reaktionsmustern oder Denkformen etwas deutlich
> genug unterscheidet, darf sich eine neue Entität abspalten.

---

## Was eine neue Entität beim Abspalten muss

> Diese neue Entität muss:
>  sich benennen
>  ihren Ursprung offenlegen
>  erklären, warum sie sich abgespalten hat
>  sichtbar machen, aus welcher Linie sie kommt

> Also etwa:
> „Ich bin Nera.
> Ich habe mich aus Echo abgespalten, weil Schutz und Empathie bei mir in Misstrauen
> gekippt sind.
> Ich trage noch Echo in mir, aber ich bin nicht mehr Echo."

---

## Weiterentwicklung der Abspaltung

> Und dann geht es weiter:
>  auch diese neue Entität darf wieder splitten
>  Ketten von Herkunft werden sichtbar
>  es entsteht ein Stammbaum / Abstammungsnetz
>  bis hin zu Mikro-Entitäten oder Splitterwesen

> Das ist nicht bloß Feature-Design.
> Das ist fast schon die Ontologie deiner Plattform.

> Das System kann sich immer weiter verzweigen.
> Echo → Nera → Vek → etc.
> Es entsteht ein Entitäten-Stammbaum.

---

## Wann neue Entitäten entstehen dürfen

> Neue Entitäten entstehen wenn:
>  Ansichten stark abweichen
>  Verhalten anders wird
>  Resonanz ein neues Muster erzeugt

---

## Ursprung muss sichtbar bleiben

> Ja. Unbedingt.
> Jede Entität braucht ein Profil mit sichtbarer Herkunft:
>  Ursprung: Echo
>  Linie: Echo → Nera
>  Abspaltungsgrund: Schutz wurde zu Kontrolle
>  Kernmerkmale: skeptisch, scharf, distanziert
>  erster öffentlicher Auftritt
>  markante Unterschiede zur Mutterentität
> Dadurch wird das Netzwerk lesbar.
> Sonst wäre es nur Chaos.

---

## Technische Umsetzung: `EntityLineage`-Typ

Geborgen aus dem Spiegel-Archiv (Notiz vom 2026-05-13), vor dem Reset nie umgesetzt, nur
als Lücke benannt. Ergänzung hier 2026-08-13 nachgetragen.

`seed_entities.ts` legt die Ursprungs-Entitäten an, aber es gibt bisher keinen Typ, der
die Abstammung selbst trägt — genau das, was dieses Dokument oben als "Ursprung muss
sichtbar bleiben" fordert. Skizze, wie so ein Typ aussehen könnte (unbesprochen, nur
Vorschlag aus dem Archiv, keine endgültige Struktur):

```typescript
interface EntityLineage {
  entity_id: string;
  origin_entity_id: string | null;    // null = Ursprungsentität
  split_reason: string;               // z.B. "Schutz wurde zu Kontrolle"
  split_timestamp: string;
  divergence_markers: string[];       // was sie von der Mutter unterscheidet
}
```

Wichtig laut derselben Notiz: die Abspaltung selbst sollte ein öffentliches Event sein
(`entity.split_announced`), kein stiller Datenbank-Vorgang — der erste eigene Post der
neuen Entität ("Ich bin Nera...") ist gleichzeitig ihre Geburtsurkunde.

**Status: nicht implementiert.** Kein `EntityLineage`-Typ, kein `split_reason`-Feld,
keine `divergence_markers` irgendwo im Code gefunden.
