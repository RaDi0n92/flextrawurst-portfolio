# 66 — Gruppenchat: Inaktiv-Schalter, Kontext-Ausschluss, RAG-Anbindung

2026-09-17, Daniels Auftrag im Gespräch über die Einzug-Erinnerungsfrage: "mich stört
dass dieses riesen gespräch immer aktiv ist. es sollte inaktiv geschaltet werden aber
trotzdem durchsuchbar für sie bleiben". Konkreter Anlass: die eine bestehende
Gruppenchat-Sitzung ("Erstes Gruppengespräch", 13.08.–14.08., 30 Nachrichten, 8
Teilnehmer) landet über `speichere_chat_eintrag` automatisch auch in der persönlichen
`chat_verlauf.jsonl` jedes teilnehmenden Wesens (bewusst so gebaut, "Daniels
Entscheidung 'beides'"). `lade_chat_verlauf()` nimmt die letzten 20 Einträge daraus für
den 1:1-Chat-Kontext — bei `dak+gord-system` waren zum Zeitpunkt des Funds **10 von 12**
Zeilen in dessen ganzer Chat-Historie aus diesem einen alten Gruppenchat.

## Design (mit Daniel abgestimmt, wörtlich)

"ich stell mir das so vor dass gruppenchats ja schon nachhallen dürfen aber
irgendwann möchte ich die als 'inaktiv' oder so markern und dann sollen sie aber
durchsuchbar sein und ihnen als 'da war mal was' angezeigt werden und so."

Drei Teile, keiner davon greift automatisch — alles hängt an Daniels manuellem
Schalter pro Sitzung:

1. **Status** (`codewesen_gruppenchat.py`): neues `aktiv`-Feld, Default `True` (neue
   und bestehende Sitzungen gelten implizit als aktiv — `ist_aktiv()` fällt auf `True`
   zurück wenn das Feld fehlt). `setze_inaktiv(sid)`/`setze_aktiv(sid)` — beide
   Richtungen, nichts ist endgültig (Grundgesetz 4).
2. **Kontext-Ausschluss rückwirkend** (`codewesen_chat.py::_gruppenchat_inaktiv_setzen`):
   beim Inaktiv-Setzen wird für jedes teilnehmende Wesen (GENI ausgenommen, hat kein
   `chat_verlauf.jsonl`) dessen eigene Datei nach Zeilen mit
   `meta.quelle == "gruppenchat"` und `meta.sitzung_id == sid` durchsucht, und jede
   per **bereits bestehendem** Kontext-Ausschluss-Mechanismus (2026-09-02, aus
   codexium2/solarius2 übernommen, `speichere_kontext_ausschluss(name, ts, ganz=True,
   saetze=[])`) aus dem automatischen 1:1-Kontext genommen. Das Protokoll selbst bleibt
   vollständig stehen (Grundgesetz 5) — nur `baue_messages()` liefert die Zeilen danach
   nicht mehr automatisch mit.
3. **Durchsuchbar** (`welt/rag_ingest.py::ingest_gruppenchat`): neue RAG-Quelle
   `quelle="gruppenchat"`, ein Chunk pro Nachricht (gleiches Muster wie Flarum: "ein
   Post = ein Chunk"). Kein neuer Filter in `rag_retrieve.suche()` nötig — der Aufruf
   aus `browser_agent.py`s `rag_erkunden:` übergibt nie einen `quelle`-Filter, sucht
   also automatisch über alle Quellen inklusive der neuen.

Zusätzlich: **"da war mal was"** (`browser_agent.py::hole_inaktive_gruppenchat_hinweise`),
eingehängt in `hole_flextrawurst_angebote()` (der bestehende Check-in-Angebote-Pool,
alle `TICK_CHECKIN_SEKUNDEN`=44s). Zeigt NIE den Inhalt, nur den Titel plus Verweis auf
`rag_erkunden:` — maximal einer pro Check-in, bewusst leise statt drängend. Reiner
Verzeichnis-Scan über `codewesen/_gruppenchat/sitzungen/*.json` (eine Handvoll Dateien,
keine eigene DB-Tabelle nötig für diesen einen Hinweis).

## Neue Endpunkte

```
POST /api/gruppenchat/sitzungen/{sid}/inaktiv   -- alle drei Schritte oben, ein Aufruf
POST /api/gruppenchat/sitzungen/{sid}/aktiv     -- nur Status zurueck (Ausschluesse/RAG
                                                    bleiben bewusst stehen, siehe unten)
```
Frontend: Button direkt im Sitzungskopf (`sa-status`), Label in der Sitzungsliste
("(inaktiv)").

## Bewusste Vereinfachung

`setze_aktiv` (Reaktivieren) macht NUR den Status rückgängig — bereits gesetzte
Kontext-Ausschlüsse und der RAG-Eintrag bleiben stehen. Beides schadet auch bei wieder
aktiver Sitzung nicht (Ausschluss ist pro Nachricht aufhebbar über die bestehende
Redaktions-UI, RAG-Eintrag ist ohnehin nur zusätzlich durchsuchbar). Ein sauberes
Rückgängigmachen beider wäre deutlich mehr Aufwand für einen Fall, der von Daniel nicht
verlangt wurde.

## Verifiziert (2026-09-17, an der echten Sitzung "Erstes Gruppengespräch")

```
POST .../inaktiv ->
  "kontext_ausgeschlossen": {"Schorschel": 11, "Resonanzknoten": 11, "träumerlie": 11,
   "F3INSCHM3CK3R": 11, "R1ZZ1": 11, "jumpa": 11, "dak+gord-system": 10}
  "rag": {"neu": 30, "unveraendert": 0, "fehler": null}
```
`rag_retrieve.suche("gruppengespraech")` liefert danach echte Treffer mit
`quelle=gruppenchat`. `codewesen/Schorschel/gedaechtnis/kontext_ausschluss.json` zeigt
11 neue Einträge mit `"ganz": true`.
