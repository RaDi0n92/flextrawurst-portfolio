
# Vault-Infrastruktur & Werkzeuge — Bericht
**Datum:** 2026-08-13
**Stand:** Ampel GRÜN — alles live getestet, nichts offen geblieben

---

## Gesamtlage

Sechs voneinander unabhängige Aufträge in einer Session, alle mit Daniel einzeln
abgestimmt und einzeln live verifiziert, bevor der nächste begann. Kein Punkt blieb
halb fertig liegen. Details der einzelnen technischen Entscheidungen stehen bereits
in den jeweiligen `docs/systemdoku/*.md`-Dateien (verlinkt unten) — dieser Bericht
zieht den Gesamtbogen.

---

## Was gebaut/geändert wurde

| # | Was | Ergebnis |
|:---|:---|:---|
| 1 | `tools/config_waechter.py` — Baseline-Diff-Wächter für die llama-Services | gebaut, live getestet, fand sofort einen echten Fund (Doku veraltet) |
| 2 | Tool-Calling-Test für `hauhaucs-q6` | bestätigt: echtes strukturiertes Tool-Calling, rundenfähig |
| 3 | `weltfutter.timer` deaktiviert | sauber gestoppt, Backup gesichert, nichts gelöscht |
| 4 | 3989 leere `.md`-Dateien aus 7 Wesen-Vaults entfernt | verifiziert, Ordnerstruktur unangetastet, 1:1-Kopie vorher gesichert |
| 5 | Echter Rücklesekanal in den Vault (`vault_lesen`/`vault_erkunden`/`vault_umbenennen`/`vault_verschieben`/`vault_loeschen`) | gebaut, isoliert + End-zu-End getestet, live bei allen 7 Wesen |
| 6 | 8-stündige Aufräum-Einladung im Vault-Takt, Daniels wortwörtlicher Prompt | gebaut, gerendert getestet, live bei allen 7 Wesen |

---

## 1. `config_waechter.py`

**Herkunft:** Geborgene Idee aus dem Vor-Reset-Archiv (Cache-Ram-Krise vom 07./08.07.2026),
nie gebaut, auf Daniels expliziten Auftrag jetzt umgesetzt.

**Design:** Baseline-Snapshot statt hartcodierter Werte — die Chat-Config allein wurde seit
Mai mindestens fünfmal geändert, ein statischer `ERWARTETE_WERTE`-Dict wäre sofort veraltet
gewesen. `check`/`update`-Subcommands, Baseline in `tools/config_waechter_baseline.json`.

**Sofortiger Fund:** `docs/systemdoku/12_ollama_gemma4.md` dokumentiert noch die
21.07.-Sollwerte (`ctx-size 66666`, `cache-ram 12288`/`16384`), live läuft seit 03./04.08.
mit `ctx-size 34567`/`cache-ram 0` — sauber per Backup-Dateien belegt, keine Drift, nur die
Doku wurde nie nachgezogen. Nachgetragen, nicht korrigiert (eigener Auftrag nötig).

→ Details: `docs/systemdoku/12_ollama_gemma4.md`, Nachtrag 2026-08-13.

---

## 2. Tool-Calling-Test `hauhaucs-q6`

Offene Vorbedingung aus dem Flickflag-Spiegel (25.07.) geklärt: kann das lokale Modell
zuverlässiges, strukturiertes Tool-Calling? Drei Live-Tests gegen Port 11435 (`id_slot=0`):
sauberer `finish_reason: "tool_calls"`, echtes JSON statt Text-Fake, korrekter Rundweg mit
Tool-Ergebnis zurück zur finalen Antwort. `--jinja` war bereits auf beiden Instanzen aktiv.

**Ergebnis:** Vorbedingung erfüllt. Kein Auftrag für einen tatsächlichen Umstieg auf
`@playwright/mcp` — nur die technische Blockade davor entfernt.

→ Details: `docs/systemdoku/12_ollama_gemma4.md`, Nachtrag 2026-08-13.

---

## 3. Weltfutter deaktiviert

`weltfutter.timer` lief alle 2h, holte externe Ereignisse (Erdbeben, Nachrichten,
Flarum-Funde) und erzeugte daraus Splitter für die 7 Wesen — 1616 kumuliert seit
Einführung. Daniel: *"das ist ausgeartet, das muss ich erstmal alles lesen"*.

`systemctl stop`+`disable`, Backup der Unit-Dateien in
`_claude/backups_systemd/weltfutter.bak_vor_deaktivierung_20260813.conf`. Nichts gelöscht,
jederzeit reaktivierbar per `systemctl enable --now weltfutter.timer`.

---

## 4. Leerdatei-Bereinigung (3989 Dateien)

Direkte Zählung ergab: historisch waren 60-70% aller `.md`-Dateien in allen 7 Vaults 0 Byte
(Ursache: ein länger bekannter Schreibfehler, seit ca. 01.08. praktisch behoben — neue
Schreibvorgänge sind fast durchgehend gefüllt).

**Vor jeder Änderung:** vollständige 1:1-Kopie nach
`wesen_vaults_backup_vor_aufraeumen_2026-08-13/`, per `diff -rq` bytegleich verifiziert
(6165 Dateien).

Daniels Regel, wörtlich: *"ich will das jede md wo auch nur ein wort drin steht bleibt bei
jedem und dann bleibt diese auch ggf in den unterordnern und ordnern"* — nur `.md`-Dateien
mit exakt 0 Byte galten als leer. Ergebnis pro Vault:

| Vault | gelöscht | verbleibend | Ordner unverändert |
|---|---|---|---|
| Schorschel | 598 | 264 | 327 |
| F3INSCHM3CK3R | 561 | 304 | 395 |
| R1ZZ1 | 591 | 303 | 399 |
| Resonanzknoten | 532 | 281 | 335 |
| dak+gord-system | 489 | 346 | 383 |
| jumpa | 538 | 298 | 335 |
| träumerlie | 680 | 346 | 409 |
| **Gesamt** | **3989** | **2142** | — |

→ Details: `docs/systemdoku/30_wesen_eigene_obsidian_vaults.md`, Nachtrag 2026-08-13.

---

## 5. Echter Rücklesekanal in den Vault

Daniels Frage, die den Auftrag auslöste: gibt es einen Rücklaufkanal, damit ein Wesen sein
eigenes Vault-Geschriebenes auch wieder lesen, explorieren und ggf. selbst umorganisieren
kann? Antwort vorher: nein — die bestehende `obsidian_lesen`-Aktion zeigt auf
`codewesen/<name>/` (die alte Flarum-Vorphase-Akte), nicht auf den eigentlichen
Obsidian-Vault.

**Technischer Fund vor dem Bauen:** die Obsidian-Fenster laufen über Selkies-WebRTC-Streaming
(nur `<canvas>`/`<video>` im DOM, kein Obsidian-eigenes HTML) — sichtbares Auslesen des
Fensters ist technisch nicht möglich. Design, mit Daniel abgestimmt:

- **Einzelne Datei lesen** (`vault_lesen`): sichtbar über den Quick Switcher geöffnet (wie
  beim Schreiben), Text kommt von der Platte.
- **Ordner erkunden** (`vault_erkunden`): rein mechanisch, kein Playwright — sonst wäre ein
  Blick in einen Ordner ~12s teuer, ohne dass sich am Fenster etwas auslesen ließe.
- **Umbenennen/Verschieben** (`vault_umbenennen`/`vault_verschieben`): sichere
  Plattenoperationen mit Pfad-Ausbruchsschutz.
- **Löschen** (`vault_loeschen`): landet in `_papierkorb/`, kein echtes `unlink()` —
  Grundgesetz-4-Konsistenz ("nichts wird gelöscht, nur unsichtbar gemacht").

Verifiziert: isolierte Tests gegen Schorschels echten Vault (Lesen inkl. Umlaute korrekt,
Pfad-Ausbruchsversuch korrekt blockiert), End-zu-End-Test über die echte
Ausführungsfunktion, alle 7 Wesen neu gestartet und fehlerfrei.

---

## 6. 8-stündige Aufräum-Einladung

Daniels wortwörtlicher Prompt-Wunsch:

> *"hallo (name), bitte schau dir die vault genau an und mach sie für dich und auch
> menschen etwas lesbarer und nenne vielleicht die dateien gezielt um und schaffe richtige
> ordnerstrukturen und verschiebe zusammengehörende dateien mit ihren kontexten zusammen,
> das ist kein zwang du kannst auch alles so lassen xD"*

Neue `VAULT_AUFRAEUM_SEKUNDEN` (8h), piggybackt auf einen ohnehin fälligen Vault-Takt
(kein vierter, unabhängiger Timer), gestaffelt über alle 7 Wesen wie der Vault-Takt selbst.
Text 1:1 übernommen, nur `(name)` durch den echten Namen ersetzt. Live gerendert getestet
(~3470 Zeichen, ~870 Token — unkritisch), alle 7 Services fehlerfrei neu gestartet.

---

## Ampel-Zusammenfassung

**GRÜN.** Alle sechs Punkte live verifiziert, kein offener Blocker. Die einzige bewusst
liegen gelassene Sache: die veraltete Ollama-Doku (Sollwerte vs. Live-Config) — nachgetragen,
nicht korrigiert, weil das ein eigener, separater Auftrag wäre.

---

## Schlusssatz

Sechs unabhängige, kleine bis mittlere Bausteine, jeder einzeln abgestimmt und einzeln
bewiesen, kein einziger nur behauptet. Der Config-Wächter und der Rücklesekanal sind die
beiden mit dem größten Nachwirkungspotential — der eine verhindert künftig eine ganze
Fehlerklasse strukturell, der andere macht aus einem Wesen, das nur in seinen Vault
schreiben konnte, eines, das ihn auch wirklich besitzen kann.

