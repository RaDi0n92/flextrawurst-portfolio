# Diktat & Stimme — Bericht
**Datum:** 2026-08-13
**Stand:** Ampel GELB — Ziel erreicht, aber über einen Umweg, nicht den ursprünglich geplanten

---

## Gesamtlage

Daniel wollte direkt in sein Terminal sprechen können, egal welches von mehreren offenen
Fenstern gerade den Fokus hat — "so in der Art wie Voicely oder so". Drei verschiedene
technische Wege wurden verfolgt, bevor einer zuverlässig funktionierte. Dieser Bericht hält
fest, warum die ersten beiden nicht trugen, nicht nur was am Ende funktioniert hat — genau
die Stellen, an denen es nicht wie erwartet lief, waren die aufschlussreichsten.

---

## Weg 1: Lokales Windows-Skript (gescheitert)

**Idee:** `tools/windows_diktat.py` — Hotkey (rechte Strg-Taste) gedrückt halten, Mikrofon
aufnehmen, lokal per `faster-whisper` transkribieren (komplett offline, kostenlos, kein
Account), Text per `keyboard.write()` direkt ins fokussierte Fenster tippen. Bewusst
komplett lokal auf Daniels Windows-Rechner, kein Umweg über den VPS — "welches Fenster den
Fokus hat" ist reine Windows-Sache, ein Netzwerk-Umweg hätte nur Latenz gebracht.

**Warum gescheitert:** Setup lief sauber durch (pip-Install, Modell-Download, "Modell
geladen. Bereit."), aber die `keyboard`-Bibliothek reagierte auf Tastendrücke überhaupt
nicht — auch nicht als Administrator gestartet. Ursache nicht abschließend geklärt
(vermutlich Antivirus/Treiber-Interferenz mit dem globalen Tastatur-Hook). Ein isolierter
Diagnose-Test (`test_tasten.py`, jede Taste protokollieren) wurde vorbereitet, aber Daniel
entschied sich für einen Pivot statt weiterer Fehlersuche.

**Nebenerkenntnis unterwegs:** Copy-Paste zwischen Chat und Windows-CMD scheiterte mehrfach
(Zwischenablage hing an altem Inhalt fest, Rechtsklick fügte in seinem Terminal-Setup
automatisch ein — dieselbe Konvention wie PuTTY). Gelöst über Direktdownload der Datei per
`curl`/WinSCP statt Copy-Paste.

---

## Weg 2: Browser-STT im bestehenden `/tts`-Tool

**Daniels Pivot, wörtlich:** *"können wir nicht einfach auf flextrawurst.de/tts noch nen tab
bauen der quasi das stt nutzt ... und dann will ich so wie bei /tts schon ist das selbe
loegik des abspeicherns ind selbstgeschaffenen containern"*.

**Gebaut:** Neuer Tab "Diktat" auf `flextrawurst.de/tts`, gleiche Struktur wie der
bestehende Soundboard-Tab (Kategorien, `.panel`/`.row`/`.chip`-Klassen wiederverwendet,
keine neue CSS). Nutzt browsereigene `SpeechRecognition`/`webkitSpeechRecognition`
(`de-DE`), kein Cloud-Umweg fürs Erkennen selbst. Bekannter Android/Chrome-Bug beachtet:
`continuous:false` + eigener Neustart in `onend()` statt `continuous:true` (verdoppelt
sonst Wörter).

**Backend:** neuer `/diktat-library` GET/PUT-Endpunkt, 1:1 nach dem Muster des
bestehenden `/library`-Endpunkts (`tts_diktat_library.json`, atomic write).

**Bedienung:** Diktieren startet/stoppt per Button, Live-Text im Feld, "Kopieren" für die
Zwischenablage — Daniels eigentliches Ziel war ja "Text erkennen lassen, dann irgendwo
einfügen", nicht direktes Tippen ins fokussierte Fenster wie bei Weg 1. Speichern optional,
mit selbstgewählter Kategorie.

### Zwei Bugs unterwegs gefunden und gefixt

1. **Gelöschte Einträge kamen nach Reload zurück.** Root Cause: die Zusammenführung von
   Server- und lokalem Stand beim Laden war eine reine Vereinigung beider Eintragslisten —
   eine Löschung war darin nie "weg", nur "auf einer Seite nicht mehr vorhanden", und kam
   beim nächsten Laden aus dem Server-Stand zurück. Fix: kein additiver Merge mehr, der
   Server ist die alleinige Wahrheit sobald erreichbar.
2. **Fehlermeldungen landeten in einem unsichtbaren Element.** Die bestehende `dbg()`-Funktion
   schreibt nur in ein `<div id="dbg">` innerhalb des TTS-Tab-Panels — auf dem Diktat-Tab war
   das unsichtbar, deshalb blieb die Browser-Konsole scheinbar leer, obwohl intern etwas
   passierte. Fix: echtes `console.log`/`console.error` an allen Stationen ergänzt
   (onstart, onaudiostart, onresult, onerror, onend).

### Feature nachgezogen: geräteübergreifender Entwurf

Daniel: *"wir könnten es doch auch so machen dass auch nach nem neuladen der seite das wa
in dem textfeld steht da so lange steht ... ich diktiere am handy ... lade seite im laptop
neu und es steht dann da als text?"*

Neues `draft`-Feld in `tts_diktat_library.json`, debounced (1,2s) bei jeder Änderung
gespeichert — bei Spracherkennungs-Zwischenergebnissen und bei manueller Eingabe. Beim
Laden gewinnt der Server-Entwurf, nur wenn der Server leer ist bleibt ein lokal schon
eingetippter Text erhalten.

### Zusatzwunsch: Vollansicht

Daniel wollte gespeicherte Diktate ungekürzt lesen können ("bis zu 3333333 Zeichen"). Im
System existierte bereits eine generische `openFullView()`-Funktion (für andere Tabs
gebaut) — nur ein "Anzeigen"-Button musste ergänzt werden, kein neues Modal nötig.

---

## Warum Weg 2 am Laptop trotzdem nicht direkt lief

Live-Diagnose per Konsolen-Log (nach dem `dbg()`-Fix) ergab eindeutig: `onerror: network`.
Mikrofon funktionierte (`onaudiostart` feuerte), aber jede Erkennungsanfrage scheiterte
sofort. Ursache: **Chromium** (Daniels Browser, nicht Google Chrome) hat keinen
eingebauten Google-API-Schlüssel für den Spracherkennungsdienst — jede Anfrage an Googles
Server schlägt strukturell fehl, unabhängig von jeder Konfiguration. Erklärt auch, warum es
am Handy (dort echtes Google Chrome vorinstalliert) klappte.

**Nachgezogener Fix:** die vorher endlose `onend → start() → onerror`-Schleife (Konsolen-Spam,
Mikrofon blieb dauerhaft aktiv) gibt jetzt nach 3 Netzwerkfehlern in Folge auf und zeigt eine
klare Meldung mit Fix-Hinweis statt endlos weiterzuversuchen.

**Firefox als Alternative geprüft:** `media.webspeech.recognition.enable` existiert und war
bei Daniel bereits `true` — der Schalter ist an, aber es steht kein tatsächlich
funktionierender Erkennungsdienst dahinter (bestätigt: bleibt bei aktiviertem Schalter
weiterhin ohne Funktion). Die `media.webspeech.test.*`-Einstellungen wurden bewusst NICHT
aktiviert — die schalten einen Fake-Erkennungsdienst für Mozillas eigene automatisierte
Tests ein, keine echte Funktion.

---

## Was am Ende tatsächlich trägt

Kein direktes Diktieren am Laptop (Chromium: kein API-Schlüssel; Firefox: kein
funktionierender Dienst; Windows-Hook: reagiert nicht). Stattdessen: **am Handy diktieren
(echtes Chrome dort), Laptop-Seite neu laden, der Text steht im Feld** — über den
geräteübergreifenden Entwurf. Von Daniel selbst als "perfekt" bestätigt.

Offen, falls Daniel es später doch will: echtes Google Chrome auf dem ThinkPad, z.B. als
Flatpak mit eigenem Speicherlimit statt dauerhaft offen — Daniel wollte das selbst noch
anschauen, kein aktueller Auftrag.

---

## Ampel-Zusammenfassung

**GELB.** Das eigentliche Ziel (diktieren, Text bekommen) ist zuverlässig erreicht — aber
nicht auf dem ursprünglich vorgestellten Weg (direkt ins fokussierte Laptop-Fenster
sprechen), sondern über den Handy-Umweg mit geteiltem Entwurf. Kein Blocker, aber auch
keine vollständige Erfüllung der ursprünglichen Vision.

---

## Schlusssatz

Drei technische Sackgassen (Windows-Hook, Chromium, Firefox), jede mit einer klaren,
verifizierten Ursache statt eines Achselzuckens — und am Ende eine Lösung, die aus der
zweiten Sackgasse selbst hervorging (Daniels eigener Vorschlag, den geteilten Entwurf zu
bauen). Nicht der Weg, der geplant war, aber einer, der trägt.
