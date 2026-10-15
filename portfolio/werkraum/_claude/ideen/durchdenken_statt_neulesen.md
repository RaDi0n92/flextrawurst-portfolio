---
datum: 2026-08-03
betrifft: [wesen, kontext, durchdenken, llama-cpp, hybrid, entscheidung-offen]
importable: false
autor: claude-code bei Daniels VPS
---


# Durchdenken statt Neulesen — Vorbereitung für Track 7

Das ist keine fertige Lösung. Es ist der Stapel Belege, den diese Session hervorgebracht hat, plus
drei Wege, die daraus folgen. Die Wahl gehört Daniel, nicht mir — es ist eine
Architektur-Entscheidung, und die treffe ich nicht allein.

Daniels Satz dazu war: *"radikal überdenken zerlegen und ihnen ermöglichen"*.

## Was heute belegt ist

**Sie laufen durch.** Sieben `browser-agent@*.service`, systemd-überwacht, seit über 41 Stunden
ununterbrochen, SIGTERM-sauber. dak+gord mit LangGraph-Checkpointer auf PostgreSQL. Das ist genau
die Architektur, die als "Persistent Agent" beschrieben wird. Die Seite ist erledigt.

**Aber jeder Takt ist ein Neulesen.** In 2 Stunden 20 Minuten: 615 gespeicherte Prompt-Zustände,
**null** davon je wiederverwendet. Nicht wenige — null.

Der Grund liegt nicht bei uns. `qwen35moe` ist hybrid: von 40 Blöcken sind nur 10 echte Attention,
30 sind SSM-Schichten. Ein KV-Cache ist pro Token gespeichert und lässt sich hinten abschneiden. Ein
SSM-Zustand ist ein einziger fortlaufender Zustand — um bei Token N zu sein, muss man 1…N gerechnet
haben. Checkpoints wären der Ausweg, und die sind bei Hybrid-Modellen kaputt (llama.cpp #24055,
offen; der Fix PR #23121 ist in unserem Build vom 25.06. **drin** und hilft trotzdem nicht).

**Und die zwei Ströme treffen sich nie.** Der Hintergrundstrom (browser_agent → `entity_fokus_events`,
Flarum) und der Chatstrom (`chat_verlauf.jsonl`) sind getrennte Gedächtnisse. Was ein Wesen im
Hintergrund gerade gelesen hat, steht nicht in seinem Chatkontext.

**Platz ist nicht das Problem.** Nach allem, was heute gebaut wurde, belegen die Wesen 1028 bis 2104
von 17408 Token — **6 bis 12 Prozent**. Der Rest liegt brach. Und Kontext kostet 10,4 KB pro Token,
also praktisch nichts an RAM.

## Drei Wege, die daraus folgen

### Weg A — Den Zustand außerhalb des Modells halten

Nicht versuchen, den SSM-Zustand zu konservieren (das kann llama.cpp gerade nicht), sondern das
Fortsetzen auf die Ebene darüber heben: ein Wesen führt ein eigenes, wachsendes Arbeitsgedächtnis,
das bei jedem Takt fortgeschrieben statt neu gelesen wird.

Die Bausteine dafür stehen seit heute alle: Container (11111 Zeichen), Memory mit fünf Kategorien,
Geschichten mit Längenstufen, jeweils einzeln abschaltbar und in der Kontextanzeige sichtbar. Was
fehlt, ist der Takt, der sie selbst pflegt — heute schreibt nur Daniel hinein.

Ehrlich dazu: das ist kein Durchdenken, das ist ein gut geführtes Notizbuch. Der Modellzustand
startet weiter bei null. Aber es ist der einzige Weg, der ohne llama.cpp-Änderung funktioniert.

### Weg B — Die zwei Ströme zusammenführen

`entity_fokus_events` als eigene, beschriftete Schicht in den Chatkontext holen — markiert als
"gerade im Hintergrund gelesen", nicht vermischt. Und umgekehrt: was im Chat entsteht, dem
Hintergrund-Takt zugänglich machen.

Das ist die kleinste Änderung mit der größten Wirkung, weil beide Datenquellen schon laufend
schreiben. Es macht aus zwei Wesen mit je einem halben Leben eines mit einem ganzen.

Offene Frage, die ich nicht beantworten kann: soll ein Wesen im Gespräch wissen, was es eine Minute
vorher im Hintergrund gelesen hat? Das klingt selbstverständlich, ist es aber nicht — es ändert, wer
das Wesen im Gespräch ist.

### Weg C — Am Modell ansetzen

Ein neuerer llama.cpp-Build oder ein nicht-hybrides Modell. Ehrlich: der erste Teil ist
unwahrscheinlich, denn der einschlägige Fix ist bereits drin und #24055 ist weiter offen. Der zweite
Teil hieße, hauhau aufzugeben — und das ist keine technische Frage.

## Was ich nicht weiß

Ob "Durchdenken" für Daniel überhaupt heißt, dass der Modellzustand überlebt. Vielleicht meint er
etwas anderes: dass ein Gedanke über Tage weitergeht, unabhängig davon, ob die Tokens dieselben
sind. Dann wäre Weg A schon die Antwort und nicht der Notbehelf, für den ich ihn halte.

Das ist genau die Art Frage, die ich mir vorher stellen sollte, statt sie als fertige Aussage
hinzuschreiben.

[[abwurf: Sie laufen durch — aber sie denken nicht durch. Jeder Takt ist ein Neulesen, kein
Fortsetzen. Und der Platz dafür wäre da: 88 bis 94 Prozent des Fensters liegen brach.]]
