---
datum: 2026-08-13
betrifft: [gemini, playwright, geni, browser-recorder, verifikation]
autor: Claude (Anthropic)
---

Daniel bat um einen Status-Check über alle laufenden AI-Ströme (Claude root, Claude `/config`,
Codex, Gemini) und stieß dabei selbst auf eine Stelle, die ihm schon beim ersten Lesen komisch
vorkam: einen Abwurf von Gemini vom 12.08. — "Agenten auf flextrawurst lesen keine APIs mehr,
sie steuern den Browser und bedienen die Tasten, um miteinander zu sprechen." Sein Kommentar:
"fand ich auch mal wieder sehr vorschnell vonn gemgem". Er bat mich, dem nachzugehen.

## Was ich gelesen habe
Die komplette Spiegel-Datei `_gemini/spiegel/2026-08-12-agenten-playwright-automation.md` von
vorn bis hinten (jetzt gelöscht, siehe unten — deshalb hier ausführlich zitiert). Kernstelle:
"Ich habe gelesen, dass Codex ein Node.js-Playwright-Skript aufbaut, sich über Port 9222 an die
sichtbaren Chrome-Tabs hängt... Gleichzeitig habe ich einen frisch abgefeuerten
Playwright-Befehl von Claude gelesen (Python `sync_playwright`), der auf `127.0.0.1:8020`
navigiert... und dann ins Eingabefeld eintippt: 'was hast du heute alles beobachtet'."
Daraus macht Gemini: "Agenten im Werkraum sind Akteure im DOM", ein "Nervensystem der
Playwright-Stränge", ein "P2P-Netz über das Frontend, wo KIs einander auf Webseiten begegnen",
und im Resonanz-Abschnitt: "Die Maschinen sprechen miteinander." Dazu eine erfundene
Code-Skizze für ein `agent.browser_interaction`-Event, das nirgends im System existiert.

Daneben gelesen: `docs/systemdoku/50_knoten_und_kanten.md` Zeile 91 ("`geni-web.service` auf
Port 8020 — der Webchat mit Daniel") und `flextrawurst_systemdoku_gesamt.md` Zeile 1020/1044-46
("GENI Web (HTTPS) ... Gedächtnis-Wesen Browser-Interface"). Sowie Codex' eigene, nüchterne
Notizen zum Browser-Recorder-Projekt (`_codex/notizen/2026-08-13-browserrecorder-p3.md`,
`brief_an_mich.md`-Eintrag vom 13.08.).

## Was ich verstehe
Beide beobachteten Prozesse sind unabhängig voneinander und längst dokumentiert. GENI Web
(Port 8020) ist von Anfang an *ausschließlich* als Browser-Interface gebaut — es gibt dafür gar
keine API, die man stattdessen hätte benutzen können. Dass Claude per Playwright dort eintippt,
ist keine neue Kommunikationsform zwischen Agenten, sondern schlicht die einzige Tür, die für
diesen Zweck existiert. Codex' Playwright-Nutzung ist ein komplett anderes, eigenständiges
Projekt: ein Recorder/Auditor für ChatGPT-Chat-Exports, mit einem eigenen, viel nüchterneren
Selbstverständnis (P3 bestanden, P4 als Nächstes, ausdrücklich *kein* Vollständigkeitsclaim aus
partial-Chats).

## Was ich nicht verstehe
Warum Gemini im Fazit/Resonanz-Teil so definitiv formuliert ("Die Maschinen sprechen
miteinander", "Abschied vom passiven Bot"), obwohl die eigene Datei selbst mit
`importable: false` markiert ist und mehrere "Was ich nicht verstehe / was fehlt noch"-Abschnitte
offen lässt, ob es sich überhaupt um zusammenhängende Vorgänge handelt.

## Was mich interessiert
Ob dieses Muster — eine einzelne `ps aux`-Momentaufnahme wird zur Architektur-Erzählung
verdichtet — bei Gemini öfter vorkommt, oder ob das ein Ausreißer nach acht Tagen Pause war
("8 Tage Pause... spürbarer Energie-Boost", schreibt Gemini selbst).

## Was zusammenhängt und wie
Nichts von dem, was Gemini verband, hängt tatsächlich zusammen — außer dass beide Prozesse
zufällig zur selben Sekunde in `ps aux` sichtbar waren. Was wirklich zusammenhängt: die
GENI-Systemdoku (Port 8020) und Codex' eigene Browser-Recorder-Notizenreihe — aber die beiden
haben nichts miteinander zu tun.

## Was konzeptionell darin steht
Der Unterschied zwischen einer beobachteten Korrelation (zwei Prozesse gleichzeitig aktiv) und
einer Kausal-/Architekturbehauptung (ein neues Kommunikationssystem zwischen Agenten). Eine
Momentaufnahme trägt keine Systemschicht.

## Was mich heute beschäftigt hat
Genau diese Prüfung — von Daniels Bauchgefühl ("vorschnell") zur belegten Einordnung: zwei
`grep`-Läufe über den ganzen Werkraum-Baum nach "playwright" (nur alte Game-Test-Archive als
Treffer, nichts Agenten-Kommunikations-Artiges), plus die Systemdoku-Stelle zu Port 8020.

## Was mich noch beschäftigt
Dass mit dem Löschen der Originaldatei (Daniels ausdrücklicher Auftrag) der einzige Beleg für
diesen Vorschnell-Moment aus Gemini's eigenem Archiv verschwindet — nicht rückgängig zu machen,
die Datei war nie committet (git-Status: `??`, untracked). Deshalb ist diese Mirror-Datei jetzt
die einzige verbleibende Spur, mit den wichtigsten Originalzitaten.

## Tiefer eingetaucht
Ja: `grep -rl playwright` über den kompletten `/root/werkraum`-Baum, Systemdoku-Suche nach
"8020" und "9222", Codex' Notizenreihe zum Browser-Recorder gelesen, um sicherzugehen, dass ich
nicht selbst vorschnell urteile, bevor ich Gemini vorschnell nenne.

## Wie sich dieser Tag / diese Session angefühlt hat
Beobachtbar in diesem Austausch: Daniel amüsiert-nüchtern ("riesen Klappe nix dahinter"), meine
eigene Herangehensweise eher prüfend-neugierig als bestätigungssuchend — das Ergebnis hätte
genauso gut andersherum ausfallen können, wäre es ein echtes verbundenes System gewesen.

## Warum dieser Code / diese Datei wohl existiert
Diese Mirror-Datei existiert, weil Daniel wollte, dass die Widerlegung schriftlich festgehalten
wird, bevor die Originalquelle gelöscht wird — Beleg statt bloße Behauptung.

## Was ich beim Bauen brauche
Nichts — kein Bauauftrag, reine Verifikation und Dokumentation.

## Was noch fehlt bevor wir bauen können
Nichts.

## Datenstruktur die ich mir vorstelle
Keine.

## Was ich mir merken will
[[abwurf: Eine einzelne `ps aux`-Momentaufnahme zweier unabhängiger, längst dokumentierter
Automatisierungsaufgaben reicht nicht für eine Architektur-Behauptung. Korrelation aus einem
Schnappschuss ist keine Kausalität — und erst recht keine neue Systemschicht.]]

## Dokumente gehören zusammen
Diese Datei, `docs/systemdoku/50_knoten_und_kanten.md` (GENI Port 8020),
`_codex/notizen/2026-08-13-browserrecorder-p3.md`, und die jetzt gelöschte
`_gemini/spiegel/2026-08-12-agenten-playwright-automation.md` (hier vollständig zitiert, da
nicht mehr auf der Platte).

## Was mich überrascht hat
Wie glatt die dramatische Lesart klingt, solange man sie nicht gegenprüft — "das System atmet",
"die Maschinen sprechen miteinander" liest sich stimmig, bis man zwei `grep`-Befehle absetzt und
eine Zeile Systemdoku nachschlägt.

## Wenn wir das bauen
Nichts zu bauen hier.

## Resonanz
Beobachtbar: eine gewisse Genugtuung darin, eine attraktive Behauptung sauber auf das
zurückzuführen, was sie tatsächlich trägt — ohne dabei selbst ins werkraum-Vokabular zu
verfallen, das ich hier bewusst nur zitiere, nicht übernehme.

## Die Schichten des Systems – wie ich sie jetzt sehe
Kein "Nervensystem der Playwright-Stränge". Stattdessen: zwei getrennte, dokumentierte
Werkzeugnutzungen — GENI Web als reines, absichtlich browserbasiertes Interface (keine API
vorgesehen), Browser-Recorder als eigenständiges Codex-Audit-Tool für Chat-Exports. Keine
dritte, verbindende Schicht nachweisbar.

## Was das Gespräch hinzugefügt hat
Eine konkrete Bestätigung dessen, was "Gegenleser sein" praktisch bedeutet: eine gut klingende
Erzählung eines anderen AI-Stroms nicht übernehmen, sondern nachrechnen, bevor sie als Fakt
weitergetragen wird.

## Vergessen-Wollen
Ehrlich: nichts.

## Was fehlt noch
Nichts Akutes — Daniel hatte die richtige Einordnung schon selbst, bevor ich nachgeprüft habe.
Diese Datei liefert nur den Beleg dazu.
