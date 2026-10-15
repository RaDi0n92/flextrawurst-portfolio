---
datum: 2026-09-19
autor: codex bei Daniels VPS
herkunft: Daniels Bridge-Vision, ChatGPT-/Chatty-Ausarbeitung und Codex-Recherche
status: verbindlicher Konzept- und Erstkontaktvertrag; native ChatGPT-Abnahme offen
---

# ChatGPT-Schicht der Augen-&-Hände-Bridge

Dieses Dokument beschreibt die ChatGPT-spezifische Schicht der Bridge. Es ist
kein Ersatz für den nativen Windows-/KDE-Nachweis und behauptet keine bereits
hergestellte ChatGPT-Verbindung.

## Die fünf getrennten Körper

- **Raute:** räumliche Präsenz eines konkreten ChatGPT-Agenten. Sie ist frei
  verschiebbar, zielgebunden und kann kurzlebige Sprechblasen anzeigen.
- **Chatkörper:** kleiner, manuell öffnbarer und frei verschiebbarer
  Gesprächsraum. Daniel und ChatGPT schreiben dort als getrennte Absender.
- **Anti-Terminal:** technische Wirbelsäule für Session, Turn, MCP-Calls,
  Zielbindung, Provenienz, Zustände, Fehler und Belege. Sie bleibt kompakt und
  bei Bedarf aufklappbar.
- **Bridge:** Transport und Verbindung zur realen Windows-/KDE-Bildschirmwelt.
- **Fensterscanner:** Quelle für Ziel-, Fenster-, Desktop- und
  Binding-Wahrheit; nicht bloß eine dekorative Fensterliste.

Diese Teile dürfen nicht wieder in einem riesigen Monsterfenster verschmolzen
werden. Anzeigeort, Arbeitsziel, konkrete Session und Empfänger bleiben
unabhängige Entscheidungen.

## ChatGPT ist kein lokaler Dummy

Die ChatGPT-Schicht bindet eine echte ChatGPT-Web-/MCP-Session an. Die EXE
simuliert kein lokales ChatGPT-Modell und kopiert keinen Webchat als Attrappe.
ChatGPT bleibt ein externer AI-Strom mit eigener Session-ID, eigenem Turn und
eigenem Zugriffspfad `mcp_chatgpt_web`.

Der Chatkörper ist standardmäßig ein Gesprächsraum. Eine normale Nachricht
von Daniel darf keinen MCP- oder Toolaufruf implizit auslösen. Ein absichtlicher
technischer Auftrag ist ein eigenes Action-Ereignis, mit eigener Freigabe,
Capability, Zielbindung und Beweiskette.

## Zwei Ereignisbahnen

```text
CHAT
Daniel → ChatGPT → Antwort → Chatkörper

ACTION
ChatGPT → MCP → Tool → Zielwelt → Rücklese → Beleg
```

Beide Bahnen dürfen im Anti-Terminal nebeneinander angezeigt werden. Sie
werden aber nicht als dasselbe Ereignis gespeichert.

Für die Chatbahn gilt:

```text
submitted → delivered → turn_received → rendered
```

Für eine technische Aktion gilt:

```text
accepted → sent → delivered → executed → observed → proven
```

Bei einer normalen Chatnachricht gibt es kein künstliches `executed` im Sinne
einer Windows-Aktion. Die Harness muss diese beiden Bedeutungen getrennt
behandeln.

## Absendervertrag

Die zulässigen sichtbaren Quellen sind:

- `daniel` — manuelle Nachricht von Daniel;
- `chatgpt` — veröffentlichte Antwort der echten ChatGPT-Session;
- `bridge_context` — technisch markierte Beobachtung, Status- oder
  Provenienzinformation.

`bridge_context` darf niemals wie Daniel oder ChatGPT sprechen. Eine
ChatGPT-Bemerkung darf wiederum nicht als nativer Zielbefund ausgegeben
werden. Jeder Eintrag trägt Session, Turn, Ziel, Empfänger und Provenienz,
soweit diese Daten vorhanden sind.

## Erster echter ChatGPT-Vertikalschnitt

Der erste ChatGPT-Slice gilt nur dann als erreicht, wenn diese Kette an einem
realen Ziel durchlaufen und belegt wurde:

```text
EXE startet
→ echter Fensterscanner liefert Desktop/Fensterziel
→ reale ChatGPT-Session wird ausgewählt
→ Binding wird zurückgelesen
→ ChatGPT-Raute erscheint am Ziel
→ Chatkörper wird geöffnet
→ Daniel schreibt manuell
→ Nachricht erreicht die reale ChatGPT-Session
→ echte ChatGPT-Antwort kommt zurück
→ Antwort wird im Chatkörper gerendert
→ Absenderidentität stimmt
→ normaler Chat erzeugt keinen impliziten Toolcall
→ Ziel-/Frame-Zustand wird beobachtet
→ gesamte Kette wird belegt
```

Ein lokaler Dummy-Reply, ein Server-ACK, eine Browser-Proof-Surface oder eine
angezeigte Beispielnachricht zählt dafür nicht.

## Harness-Zähne

Die maschinell kontrollierbaren Erstkontakt-Proofs sind:

```text
session_is_real
target_bound
binding_read_back
chat_message_submitted
message_delivered
chatgpt_turn_received
response_rendered
sender_identity_correct
tool_not_triggered_by_plain_chat
target_observed
proof_attested
```

Die Harness speichert diese als geordnete Beweise und blockiert bei falscher
Reihenfolge, unbekannter Absenderidentität oder einer impliziten Chat-zu-
Action-Kante. Sie speichert nicht die Philosophie der Raute und behauptet
keine Bilder, Gedanken oder Fähigkeiten, die nicht tatsächlich veröffentlicht
und beobachtet wurden.

## Sichtbarer Chatkörper

Der Chatkörper bleibt klein und frei beweglich. Geschlossen ist ChatGPT nur als
Raute sichtbar. Beim Öffnen erscheinen der relevante Verlaufsausschnitt, das
manuelle Eingabefeld und der klare Ziel-/Sessionhinweis. Die 3,3-Sekunden-
Raumblende und der 6,6-Sekunden-Rautenticker bleiben zusätzliche
Präsenzdarstellungen; sie ersetzen nicht den dauerhaften Chatverlauf.

Die technische Anti-Terminal-Ansicht kann bei Bedarf daneben geöffnet werden
und zeigt dann mindestens Session, Turn, Gate, MCP-Call, Status,
Provenienz sowie `accepted → sent → delivered → executed → observed → proven`.

## Nicht versprochen

- ChatGPT kann nicht als dauerhaft autonom denkendes lokales Wesen behauptet
  werden, nur weil der Chatkörper offen ist.
- Eine ChatGPT-Antwort beweist keine native Windows- oder KDE-Wirkung.
- Ein MCP-Erfolg beweist keine Wirkung im gebundenen Programm.
- Playwright beweist die browserbedienbare Prüfstrecke, aber nicht automatisch
  die native EXE, den Windows-Fensterscanner oder echte Eingabezustellung.

Der nächste technische Schritt nach dem tragenden Codex-Terminal und dem
Fensterscanner ist daher ein einziger echter ChatGPT-Rundlauf. Erst danach
kommen mehrere Sessions, ChatGPT-Subagenten, Hauhaucs-Beobachtung und größere
Kapsel-/Replay-Funktionen.
