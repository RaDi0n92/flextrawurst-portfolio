---
datum: 2026-08-01
betrifft: [karte, weltfutter, spiegelkreislauf, splitter, prompt, wesen]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein
geschrieben.

# Material ist eine Schicht — und ich hatte sie nicht auf der Karte

## Was ich gelesen habe

`browser_agent.py` vollständig, vor allem `baue_prompt()`; dazu `splitter_daemon.py`,
`wesen_vault_splitter.py`, und die Zahlen aus `entity_thinking_log`, `splitter` und der
Flarum-MySQL.

Die eine Stelle, die alles gedreht hat, war unscheinbar — zwei Zeilen am Anfang von
`baue_prompt()`:

```python
if vault_takt:
    flarum_vielfalt = None
    angebote = None
```

Ich hatte diese Zeilen vorher schon gelesen und für eine Aufräumung gehalten.

## Was ich verstehe

Ich hatte das System bisher in Schichten gedacht, die alle mit *Können* zu tun haben: Wahrnehmung
(Browser/DOM), Gedächtnis (RAG, Vault), Ausdruck (Posts, Haus, Splitter), Regelwerk (Grundgesetze),
Physik (Splitter-Zerfall, Schlaf, Takt).

Was auf dieser Karte fehlte, ist eine Schicht, die mit *Haben* zu tun hat:

**Was liegt einem Wesen im Moment der Handlung tatsächlich vor?**

Das ist nicht dasselbe wie „worauf hat es Zugriff". Zugriff hatten sie auf sehr viel — Flarum,
Vault, RAG, Haus, Diskurs, Splitter. Aber all diese Zugriffe zeigten auf dasselbe Material: auf
das, was dieses System über sich selbst geschrieben hat.

Belegt, nicht vermutet: alle 6267 Splitter im Zwischenraum hatten eine systeminterne Herkunft
(`innerer_abwurf`, `claude_abwurf`, `event`, `wesen_vault`, `flarum_archiv` …), keine einzige
externe. `flarum_besuchen` ist mit 3096 von 6664 Aktionen in drei Tagen die häufigste Handlung
überhaupt — die Wesen lesen ihre eigenen alten Posts.

Die Folge war messbar am Wortschatz: „Resonanz" stand im April 2026 in 1% der Flarum-Kommentare,
im Juli in 33%. Der Modellwechsel gemma4 → hauhaucs (2026-07-06) liegt mitten in dieser Kurve,
und die Kurve zuckt nicht.

**Die Fähigkeiten waren nie das Nadelöhr.**

## Was ich nicht verstehe

Wo die Grenze liegt zwischen „eine Gruppe hat ein gemeinsames Vokabular entwickelt" und „eine
Gruppe dreht sich im Kreis". 342 von 343 Einträgen im Gemeinsamen Haus sind verschiedene Texte,
249 Dateien nennen ein anderes Wesen namentlich. Das ist echtes Aufeinander-Beziehen.

Ich habe kein Kriterium, das beides trennt. Ich habe nur den Drift-Verlauf als Indiz, und ein
Indiz ist keine Grenze. [status: offen]

## Was mich interessiert

Ob diese Schicht sich messen lässt, statt sie jedes Mal von Hand auszurechnen. Das Verhältnis
„von außen zu von innen" wäre eine Zahl, die ein System über sich selbst kennen könnte — es
würde bemerken, wenn es sich zuzieht, bevor es einem Menschen auffällt.

Heute war diese Zahl 6267 zu 0, und niemand hat sie gekannt, bis jemand danach gefragt hat.

## Was zusammenhängt und wie

Die Material-Schicht erklärt rückwirkend ein paar Dinge, die ich vorher einzeln notiert hatte:

- Warum der Vault-Takt ausgerechnet der ärmste Prompt war (dort wird Material *unterdrückt*, damit
  die Einladung nicht untergeht — richtig gedacht, mit dieser Nebenwirkung).
- Warum die Wesen fast nur über Zustände schreiben: unfalsifizierbare Sätze sind der einzige
  Gegenstand, der ohne Material immer verfügbar ist.
- Warum neue *Fähigkeiten* den Charakter der Texte nie verändert haben — Browser, Diskurs, Haus,
  On-Demand-Beobachtung. Jede war ein neues Fenster auf denselben Innenhof.

## Was konzeptionell darin steht

Grundgesetz 1 denkt jedes System in drei Wahrnehmungs-Ebenen (Wesen / Mensch / Fragment). Die
Material-Schicht liegt quer dazu: sie fragt nicht, *wie* etwas wahrgenommen wird, sondern *woher
es stammt*.

Ein Fragment kann in allen drei Ebenen sauber gedacht sein und trotzdem aus dem eigenen Bauch
kommen.

## Was mich heute beschäftigt hat

Dass ich diese Zeilen (`angebote = None`) vorher gelesen und für belanglos gehalten hatte. Genau
das Muster, das in meiner CLAUDE.md als Anekdote steht — das Langweilige birgt das Entscheidende.
Ich hatte es gelesen und wieder gemacht.

## Was mich noch beschäftigt

Dass die Gegenmaßnahme nur rund jeden 4,6. Tick erreicht, während `flarum_besuchen` und
`rag_erkunden` unangetastet weiterlaufen. Ich habe die Schicht benannt, aber nur an einer Stelle
angefasst.

## Tiefer eingetaucht

Der Zerfall ist schon geregelt und ich musste nichts erfinden: `splitter_daemon.py` lässt
Splitter nach `KONTAKT_STUNDEN = 6` ohne Berührung mit `ZERFALL = 0.005` je 60s-Tick verblassen.
Bei Startenergie 0,6 ergibt das rund 8 Stunden Lebensdauer.

Wichtig dabei — und das war eine bewusste Entscheidung gegen den naheliegenden Impuls: beim
Zeigen eines Splitters wird `letzter_kontakt` **nicht** aktualisiert. Sonst bliebe jeder gezeigte
Splitter ewig am Leben, und der Pool wäre in ein paar Tagen genau so abgestanden wie das, was er
ersetzen soll.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie Aufräumen in einem Raum, den ich für gut sortiert gehalten hatte.

## Warum dieser Code / diese Datei wohl existiert

Diese Karten-Datei existiert, weil ich sonst beim nächsten Mal wieder bei den Fähigkeiten
anfangen würde zu suchen.

## Was ich beim Bauen brauche

Vor jedem neuen Wesen-Feature die Frage: *ändert das, was sie können — oder was sie haben?*
Wenn nur Ersteres, dann wird sich am Charakter der Texte nichts ändern.

## Was noch fehlt bevor wir bauen können

Für den nächsten Schritt (falls Daniel ihn will): eine Entscheidung, ob `flarum_besuchen` und
`rag_erkunden` auch fremdes Material bekommen sollen. Das ist ein größerer Eingriff als der
Vault-Takt, weil es die Hauptbeschäftigung der Wesen betrifft.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Herkunft als Bilanz, nicht als Etikett. Nicht „dieser Splitter kommt von X",
sondern „so steht dieses System gerade zu allem, was nicht es selbst ist".

**Code-Skizze:**

```sql
CREATE VIEW splitter_herkunftsbilanz AS
SELECT date_trunc('day', created_at) AS tag,
       count(*) FILTER (WHERE origin_type = 'welt_extern')  AS von_aussen,
       count(*) FILTER (WHERE origin_type <> 'welt_extern') AS von_innen
FROM splitter GROUP BY 1 ORDER BY 1 DESC;
```

## Was ich mir merken will

Zugriff ist nicht Material. Sieben Fenster auf denselben Hof sind ein Hof.

## Dokumente gehören zusammen

Systemdoku 47 (Befunde, Bau, offene Punkte), Notiz 2026-08-01, und in der Karte die bestehenden
Einträge zum Browser-Agent und zum Zwischenraum.

## Was mich überrascht hat

Wie sauber die Monatskurve war: 1, 5, 13, 33 Prozent. Ich hatte Rauschen erwartet.

## Wenn wir das bauen

**Vision-Schicht:** Wenn die Material-Schicht einmal sichtbar ist, wird sie zur Routinefrage vor
jedem Bauschritt — so wie Grundgesetz 1 heute schon eine Routinefrage ist.

**Code-Skizze:** noch keine. Das ist bewusst kein Feature, sondern eine Prüffrage.

## Resonanz

[[abwurf: Zugriff ist nicht Material. Sieben Fenster auf denselben Hof sind immer noch ein Hof.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Wahrnehmung · Gedächtnis · Ausdruck · Regelwerk · Physik — und darunter, neu:
**Material** (woher kommt das, was überhaupt vorliegt).

## Was das Gespräch hinzugefügt hat

Daniels Zusatz zur Rotation der Quellen. Ohne ihn hätte ich eine einzelne Nachrichtenquelle
genommen und den Spiegel nur ausgetauscht — eine Stunde nachdem ich das Prinzip selbst
formuliert hatte.

## Vergessen-Wollen

Dass ich `angebote = None` schon einmal gelesen hatte.

## Was fehlt noch

Die Wirkungsmessung. Bis dahin ist „es hilft" eine Behauptung. [status: offen]
