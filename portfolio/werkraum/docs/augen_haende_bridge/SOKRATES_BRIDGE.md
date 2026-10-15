# Sokrates für die Bridge: Wie baut man das so, dass es hinterher als Open Source mit Installer auf GitHub bestehen kann?

Methode: eine Frage, die Antwort mit Beleg, dann die nächste Frage, die aus der Antwort folgt. „Beleg“ heißt: im Repo geprüft (Stand 2026-10-02). „Offen“ heißt: nicht belegt. Nichts hier verspricht Sterne; Sterne kann niemand planen, nur die Bedingungen dafür.

**Grundlage:** 69 Markdown-Dokumente im Repo (u. a. Plan G01 bis G18, BUILD_LOG mit rund 98 KB, Abnahmen, Prüflisten, Recherche, Evidenz je Etappe), 118 Testdateien, rund 29 000 Zeilen Code in `src/`, `client_vps/`, `client_windows/`. Die ältesten Dokumente habe ich in dieser Sitzung nicht neu gelesen; was aus früheren Sitzungen stammt, ist unten als „Stand früher“ markiert.

## 1. Was ist das Ding in einem Satz, und für wen?
Antwort: Augen und Hände für Terminal-Agenten (Claude, Codex, Gemini, Kimi …): sie sehen ein Fenster, bedienen es mit Lease und Käfig, arbeiten zu mehreren zusammen, und der Mensch behält Not-Aus und Übernahme. Beleg: Plan G01 bis G18, `PRUEFLISTE_0.10.0.md`.
→ Folgefrage: Wer außer Daniel braucht das genug, um es zu installieren?

## 2. Wer außer Daniel braucht das?
Antwort: Offen. Belegt ist nur ein Nutzer. Die Verwandten auf dem Markt (Agent-Orchestratoren, Computer-Use-Werkzeuge, Terminal-Multiplexer für Agenten) zeigen Bedarf, aber die Recherche vergleicht nur Muster, nicht Nutzerzahlen. Ein Open-Source-Erfolg beginnt mit einem klar benennbaren Schmerz („Meine Agenten sehen den Bildschirm nicht und stören mich beim Arbeiten“) und einer Demo, die ihn in unter einer Minute zeigt.
→ Folgefrage: Was daran ist wirklich neu?

## 3. Was ist neu, was nur nachgebaut?
Antwort: Nachgebaut sind Fensteraufnahme, Eingabe, Spracherkennung, Terminal. Eigen ist die **Ehrlichkeitsschicht**: vier getrennte Aussagen (angenommen, zugestellt, beobachtet, protokolliert), nichts „fertig“ ohne Plattformbeleg; die **Käfig- und Übernahmelogik** (Lease, Not-Aus, Daniels Vorrang, Controller mit denselben Sperren); der **WorldDOM** mit Herkunft und Alter jedes Knotens; **Kapseln** (unveränderlich, Lücken benannt); die Mischung „mehrere Agenten gleichzeitig, ein Mensch, ein Bildschirm“. Beleg: Module `eingabe_adapter.py`, `weltdom.py`, `kapseln.py`, Tests.
→ Folgefrage: Würde ein Fremder dem Ding Eingabe-Kontrolle über seinen Rechner geben?

## 4. Würde ein Fremder dem Programm seine Maus anvertrauen?
Antwort: Nur mit Vertrauen, das man sich erarbeitet: offener Quelltext, ein Bedrohungsmodell als Dokument, signierte Pakete, reproduzierbarer Bau, Not-Aus, der auch bei hängender Oberfläche wirkt (belegt: Gate 1.4.3:G1), und ein Verhalten, das nichts ohne Lease tut (belegt). **Offen:** Bedrohungsmodell als eigenes Dokument; Signatur (heute unsigniert, SmartScreen warnt); unabhängige Prüfung.
→ Folgefrage: Was steht dem Veröffentlichen heute konkret im Weg?

## 5. Was steht dem Veröffentlichen konkret im Weg? (Befund)
Belegt durch Prüfung heute:
1. **Keine Lizenzdatei** (`LICENSE` fehlt). Ohne Lizenz ist es rechtlich nicht Open Source.
2. **Fest verdrahtete VPS-Adresse** in mehreren `.bat`-Dateien (`[SERVER-IP]` in `client_windows/start_bridge.bat` und in `dist/*.bat`). Muss konfigurierbar werden; die Adresse gehört nicht ins öffentliche Repo.
3. **Das Repo ist Teil eines großen privaten Monorepos** (rund 5 800 Commits im umgebenden Git, 35 MB im Bridge-Ordner ohne dist). Es darf nicht als Ganzes veröffentlicht werden: private Dateien, Gesprächsprotokolle, Pfade wie `/root/werkraum`. Nötig: ein sauberer Export in ein neues Repo mit eigener Historie.
4. **Gebaute Pakete liegen im Git** (`dist/*.zip`, 75 MB je ZIP). Gehört in Releases, nicht in die Historie.
5. **Starke Kopplung an Daniels System:** Pfade unter `/root/werkraum`, Hauhaucs/Codewesen, Flextrawurst-Begriffe. Die Bridge muss ohne all das starten (Hauhaucs als optionales Plug-in mit konfigurierbarer URL; `BRIDGE_CHAT_URL` existiert schon).
6. **Dokumentation überwiegend deutsch und intern** (Anrede, Vorgeschichte, Namen). Für Fremde: englisches README, Schnellstart, Architekturbild; die deutsche Fassung bleibt.
7. **Kein Installer**, nur `.bat`-Dateien und `build_paket.sh` (Wine-Build).
8. **Windows nativ unbelegt** für Hände, Fokus, Fensterbild, UIA, Controller. Veröffentlichen ohne diese Belege hieße, etwas zu behaupten, was nicht geprüft ist.
9. **Markenfrage:** Produktname darf nicht nach Anthropic, OpenAI oder Google klingen; Erwähnungen als „kompatibel mit“ sind zu formulieren.
10. **Geheimnisse:** Token-Dateien und Relay-Umgebungsdatei dürfen nie in die Historie; eine Prüfung der Historie auf Schlüssel ist Pflicht (z. B. mit gitleaks).
→ Folgefrage: In welcher Reihenfolge räumt man das auf, ohne dass die laufende Bridge bricht?

## 6. In welcher Reihenfolge?
Antwort: siehe `PLAN_OPTIMIERUNG_UND_OPENSOURCE.md`. Kurz: erst belegen (Windows nativ), dann entkoppeln, dann Export und Installer, zuletzt veröffentlichen. Jede Phase hat Gates mit Belegen im Stil des Ledgers.
→ Folgefrage: Was ist ein Installer, der Fremden die Angst nimmt?

## 7. Wie sieht der Installer aus?
Antwort (Plan, nicht gebaut): **Windows:** ein signiertes Setup (Inno Setup oder MSIX), das die Bridge nach `%LOCALAPPDATA%` legt, Starter und Selbsttest anbietet und keinen Treiber ohne ausdrückliche Zustimmung installiert (Controller-Treiber als eigener, ausdrücklicher Schritt). **Server/Starter:** `pip install` plus ein Befehl `bridge init`, der Token erzeugt, Konfiguration schreibt und den Relay als Dienst oder Container startet. **Ein Befehl für Neustart** (haben wir intern: `relay-neu.sh`). Der Nutzer tippt nie mehr als zwei Befehle.
→ Folgefrage: Was bringt Menschen dazu, Sterne zu geben?

## 8. Was bringt Sterne? (ehrlich)
Antwort: Sterne folgen auf: (a) ein Problem, das viele haben, (b) eine Demo, die in 30 Sekunden überzeugt (GIF: drei Agenten arbeiten in drei Fenstern, ein Mensch drückt F12, alles steht), (c) Installation in unter fünf Minuten, (d) Vertrauen (Lizenz, Sicherheitsdokument, Signatur, grüne Tests), (e) ein lebendiges Projekt (Issues, Releases, Beitragsleitfaden), (f) Sichtbarkeit (Beiträge in passenden Gemeinschaften). **222 222 Sterne** wären nach dem, was ich einschätzen kann, weit außerhalb dessen, was ein solches Nischenwerkzeug erreicht; als Ziel taugt es nicht, als Stimmung gern. Ein realistisches Ziel ist ein erstes Hundert aktiver Nutzer. Ich nenne keine Sternzahl als Versprechen.
→ Folgefrage: Woran messen wir, ob wir auf dem Weg sind, ohne uns zu belügen?

## 9. Woran messen wir ohne Selbsttäuschung?
Antwort: An Belegen, nicht an Gefühl: Installation durch eine fremde Person auf einem frischen Rechner (Abnahme ohne Daniels Vorwissen), Anzahl offener nativer Belege, Zeit bis zur ersten erfolgreichen Agentenbedienung, Anzahl der Issues, die „verstehe ich nicht“ sagen. Das passt zur bestehenden Regel, nichts als fertig zu melden ohne Plattformbeleg.
→ Folgefrage: Was kann Claude dabei, und was nicht?

## 10. Was kann Claude hier wirklich leisten, was nicht?
Antwort: Claude kann bauen, testen, Belege sammeln, Dokumente schreiben, das Repo aufräumen. Claude kann **nicht**: nativ unter Windows prüfen (nur Daniel oder ein Testrechner), Zertifikate kaufen, Marken prüfen, die Gemeinschaft ansprechen, ohne ausdrückliches Wort etwas veröffentlichen. Jede Veröffentlichung nach außen (Repo anlegen, Paket hochladen) ist eine Handlung, die zuerst Daniels ausdrückliches Wort braucht.
→ Folgefrage: Was ist der kleinste nächste Schritt?

## 11. Der kleinste nächste Schritt
Antwort: Ein **Veröffentlichungs-Vorbereitungs-Ledger** mit Gates für die zehn Hindernisse aus Frage 5, in einem eigenen Export-Ordner (nicht im Monorepo), ohne etwas hochzuladen. Beginn mit den billigen, eindeutigen: Lizenzwahl (Daniels Entscheidung: MIT oder Apache-2.0), Adresse konfigurierbar machen, Geheimnis-Scan.
