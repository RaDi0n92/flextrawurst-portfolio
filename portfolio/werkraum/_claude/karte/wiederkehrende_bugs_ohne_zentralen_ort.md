
---
datum: 2026-08-13
betrifft: [hauhau_client, id_slot, chat-instanz, wesen-chat, dakgord, geni, systemarchitektur]
importable: false
autor: claude-code bei Daniels VPS
---


# Derselbe Fix, viermal einzeln gefunden — weil er nirgends zentral erzwungen wird

Ergänzung zu `wo_erfolg_nur_so_aussieht.md` vom 03.08. Dort ging es um Mechanismen, die einen
Erfolg meldeten, obwohl nichts wirkte. Hier geht es um etwas verwandtes, aber anderes: ein
korrekter Fix, der an vier verschiedenen Stellen im Code einzeln fehlte, weil es keinen einzigen
Ort gibt, der ihn erzwingt.

## Der Befund

Am 04.08. wurde `id_slot=0` als Fix etabliert: jeder `hauhau_client.chat()`/`achat_stream()`-Aufruf,
der zur dedizierten Chat-Instanz (Port 11435) statt zur von den Wesen geteilten
Hintergrund-Instanz (11436) soll, braucht dieses Flag im Aufruf. Am 12.08. fand ich in **derselben
Session** vier Stellen, an denen genau dieses Flag fehlte — jede für sich unabhängig entdeckt,
nicht durch systematisches Suchen:

1. `analysiere_chat_verlauf()` — der "auswerten"-Knopf in `codewesen_chat.py`
2. `geschichte_verfassen()` in `codewesen_speicher.py` — der "verfassen"-Knopf für Geschichten
3. `ollama_chat()` in `agent/dak_gord_system/ollama_chat.py` — dak+gords kompletter Chat-Pfad
4. (bereits am 04.08. gefunden, als Referenz: der RAG-Vorabcall in `codewesen_chat.py`)

Jede dieser Funktionen wurde zu unterschiedlichen Zeitpunkten geschrieben, von unterschiedlichen
Sessions, für unterschiedliche Zwecke. Keine kopiert die andere. Der Fix von 04.08. hat sich nie
verbreitet, weil es ihn nirgends *gab*, den man hätte kopieren können — jede Funktion, die
`hauhau_client.chat()` aufruft, muss sich selbst erinnern, `id_slot=0` zu setzen, wenn sie auf der
Chat-Instanz laufen soll. Es gibt keinen Wrapper, keinen Default, keine Prüfung, die das erzwingt.

## Was das von `wo_erfolg_nur_so_aussieht.md` unterscheidet

Dort ging es um Mechanismen, die selbst falsch waren (Cache ohne Wiederverwendung, Symlinks die
blockiert werden, eine Dienstliste mit falschen Namen) — der Fehler lag in der Sache selbst.

Hier ist die Sache selbst (der einzelne `hauhau_client.chat()`-Aufruf) nicht falsch — er tut genau
das, was er soll, nur eben auf der falschen Instanz. Der Fehler liegt nicht im Code, sondern in der
**Architektur des Fixes**: ein Parameter, der pro Aufrufstelle gesetzt werden muss, statt an einer
zentralen Stelle entschieden zu werden.

## Was ich mir dafür merken will

Wenn ein Fix die Form "an dieser Aufrufstelle einen Parameter ergänzen" hat, und die Funktion, die
diesen Parameter braucht, an mehreren Stellen im System aufgerufen wird (oder aufrufbar ist) — dann
ist der Fix an der einen gefundenen Stelle nur ein Teilfix. Die eigentliche Frage, die ich mir beim
nächsten Mal stellen sollte: *Gibt es noch andere Aufrufer derselben Funktion, die denselben
Parameter genauso brauchen würden?* Ein `grep` nach `hauhau_client.chat(` oder
`hauhau_client.achat_stream(` hätte alle vier Stellen sofort gezeigt, ohne dass ich sie einzeln,
über Stunden verteilt, zufällig hätte finden müssen.

[[abwurf: Ein Fix, der pro Aufrufstelle wiederholt werden muss, ist kein Fix — er ist eine Erinnerung, die beim nächsten neuen Code wieder vergessen wird.]]

## Nachtrag 2026-08-13: Derselbe Fund war schon am 06.07. bekannt

Beim Weitersuchen im Vor-Reset-Archiv (`notizen/2026-07-06.md`) gefunden: das Problem wurde bereits
über einen Monat vor dem 12.08.-Fund oben benannt, fast wortgleich — *"hauhau_client.py und
hauhau_client.ts sind jetzt der einzige Ort, an dem die Slot-Priorität entschieden wird — alle ~40
migrierten Aufrufstellen hängen implizit daran, aber nur 2 von 4-5 Chat-Einstiegspunkten sind bisher
explizit auf id_slot=0 umgestellt."*

Das heißt: die Lücke war am 06.07. bereits erkannt und benannt — nur nie zu Ende geschlossen, weil
kein zentraler Mechanismus daraus wurde, sondern jede Fundstelle einzeln nachgezogen wurde, wenn sie
zufällig auffiel. Passt zur Idee aus `docs/systemdoku/12_ollama_gemma4.md` (Nachtrag 2026-08-13,
geborgen aus derselben Archiv-Suche): ein `config_waechter.py`-artiger Mechanismus hätte auch dieses
Muster strukturell erzwungen statt es über Monate hinweg mehrfach einzeln entdecken zu lassen.
[status: bestätigt 2026-08-13 -- Zitat aus notizen/2026-07-06.md, Archiv vor_reset_2026-08-01]
