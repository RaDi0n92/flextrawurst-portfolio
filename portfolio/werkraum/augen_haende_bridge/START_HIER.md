# START HIER — Augen & Hände Bridge

Dieser Ordner ist der kanonische gemeinsame Arbeitsort für die Bridge. Wenn
Codex, Claude, Gemini oder ein Mensch weiterarbeiten, beginnen sie hier — nicht
in einer separaten Provider-Kopie.

## Zuerst: die Quelle

Die Quelle für den Körper der Bridge ist Daniels ausdrücklicher Wortlaut. Wo er sich später
korrigiert oder feinjustiert hat, gilt die spätere Fassung. Kein Code und kein Plan steht
darüber.

Maßgeblich ist `bridge_docs/ANFORDERUNGEN.md`: jede Anforderung mit Stand. Dort gilt: spätere
ausdrückliche Korrektur vor früherem Entwurf. Den Rahmen gibt `bridge_docs/PLAN.md`.

Nur zur Orientierung: `/root/werkraum_bilder/refferenzen/h a bridge.jpg`, Daniels frühe
Skizze. Sie liegt quer und wird zum Lesen um 90° gedreht. Sie zeigt die räumliche
Anordnung, ist aber älter als die Feinjustierung: ihre Beschriftungspfeile sind Erklärung,
keine Bauteile, und sie zeigt drei Terminals, wo der erste Körper eines hat. Bei
Widerspruch gilt das Dokumentierte.

Der erste Körper, den Daniel haben will, ist klein. Seine Worte (2026-09-20): „das 1zu1
terminal. fensterscanner. und … seine raute. dazu kamera mikrophon. stop fertig".

Daraus folgt für jeden Strom, der hier baut:

1. Daniels dokumentierter Wortlaut steht über vorhandenem Code. Widerspricht Code ihm, ist
   er Altlast — entfernen oder quarantänisieren, nicht als Fundament weiterbauen.
2. Bevor Transport, Evidence oder Tests auf den Körper gesetzt werden: den Körper starten
   und gegen `ANFORDERUNGEN.md` halten, nicht nur gegen die Tests. „Technisch grün"
   ersetzt nicht „das hat Daniel festgelegt".
3. Kein Bauteil, das dort nicht verlangt wird. Und keins, das verlangt wird, als Attrappe:
   ein Schalter, hinter dem keine Aufnahme hängt, ist keine Kamera.
4. Rauten erscheinen nur für Agenten, die es wirklich gibt und die gebunden sind.

Herkunft: Daniels Vorgaben (Anforderungsregister, Baustartprüfung). Formulierung der vier
Regeln: Claude, 2026-09-20 — Daniel hat den Text nicht abgenommen.

## Pflichtlektüre

1. Diese Datei und `/root/werkraum/augen_haende_bridge/README.md`
2. `/root/werkraum/augen_haende_bridge/bridge_docs/PLAN.md`
3. `/root/werkraum/augen_haende_bridge/bridge_docs/ANFORDERUNGEN.md`
4. `/root/werkraum/augen_haende_bridge/bridge_docs/TECHNIK.md`
5. `/root/werkraum/augen_haende_bridge/bridge_docs/2026-09-20_BRUECKE_BAUPROTOKOLL_FOKUS_UND_WIEDERAUFNAHME.md`
   (läuft aus, sobald der Skill entschlackt ist)
6. `/root/werkraum/augen_haende_bridge/skills/augen-haende-greenfield-builder/SKILL.md`
7. `/root/werkraum/augen_haende_bridge/skills/augen-und-haende-bridge/SKILL.md`
8. `/root/werkraum/augen_haende_bridge/BUILD_LOG.md`
9. den relevanten Code unter `/root/werkraum/augen_haende_bridge/src/`
   und die aktuelle Evidence unter
   `/root/werkraum/augen_haende_bridge/tests/evidence/`

## Aktive Grundsätze

- Der alte Gemini-Prototyp und die alte EXE sind keine aktive Referenz.
- Der nächste Pfad beginnt bei G01 und führt erst über G02 zur echten EXE.
- Kein UI- oder ChatGPT-Ausbau vor dem dafür erforderlichen nativen Fundament.
- Skill vor dem Schritt, Dokus/Git/Code/Evidence lesen, ein kleiner Stein,
  Beweis, Skill danach, Protokoll fortschreiben.
- Jeder Zyklus braucht einen `FocusContract`.
- Playwright ist äußerer Zeuge für Browserpfade; native Windows-/KDE-Belege
  bleiben für native Fähigkeiten erforderlich.
- Claude und Gemini benutzen denselben Code, dieselbe Harness und dieselben
  Dokus hier im Workspace. Keine konkurrierenden Provider-Kopien anlegen.
- Körper-Tor: `tests/pruefe_koerper.py` vor jeder Etappe am Windows-Körper und vor jedem
  Fertigmelden. Exit 1, solange beanstandeter Altbestand im Körper steht.

## Kanonische Schichten

- Skill-Verweise: `/root/werkraum/augen_haende_bridge/skills/`
- Harness/Runtime: `/root/werkraum/augen_haende_bridge/src/`
- Tests: `/root/werkraum/augen_haende_bridge/tests/`
- Bauzustand: `/root/werkraum/augen_haende_bridge/BUILD_LOG.md`
- Bridge-Doku: `/root/werkraum/augen_haende_bridge/bridge_docs/`
- Übergabe-Vault: `/root/werkraum/übergabekapseln/augen_haende_bridge/`

Die Übergabekapsel ist für Lesen, Verpacken und Weitergeben. Dieser Ordner ist
für die tatsächliche gemeinsame Arbeit.
