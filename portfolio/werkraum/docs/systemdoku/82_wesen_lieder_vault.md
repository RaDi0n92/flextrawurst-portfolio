# 82 — Wesen-Lieder-Vault: Ideen, Schnipsel, Lieder, Freigabe ins Forum

Stand 2026-10-02. Daniels Auftrag, mit seinen Worten aufgebaut: die Wesen sollen Lieder schreiben
dürfen — über sich oder gar nichts mit sich zu tun, mehrsprachig, klein anfangen, Ideen sammeln,
zurückschauen, zusammenfügen, und nur was sie selbst freigeben geht ins Forum.

## Texte für die Wesen (Daniels Entwurf, er formuliert noch selbst drüber)

- `wesen_lieder/impuls_lieder.md` — die Einladung (alle 90 Minuten komplett vorgelegt)
- `wesen_lieder/ticket_auswahl.md` — das Ticket mit acht Möglichkeiten (alle 30 Minuten)
- `wesen_lieder/ticket_nach_rueckschau.md` — Zusatz „Feinschliff“, kommt nach der Rückschau

Der Code liest diese Dateien bei jedem Takt neu — Änderungen an den Texten wirken ohne Neustart.
Platzhalter im Ticket: `{heute_lieder}`, `{heute_schnipsel}`, `{zuletzt_gewaehlt}`, `{lieder_threads}`,
`{deine_dateien}` (die tatsächlichen Dateinamen des Wesens — die Wesen rieten sonst Namen beim Freigeben).

## Bausteine

| Teil | Wo | Zustand |
|---|---|---|
| Kernmodul | `welt/wesen_lieder_agent.py` | gebaut, `tests/lieder_agent_test.py` 67 ok |
| Vault | `/root/werkraum/lieder_vault/<Wesen>/{ideen,schnipsel,lieder}` | angelegt |
| Obsidian-Ansicht | Container `obsidian-liedervault`, 127.0.0.1:3104/3204, `flextrawurst.de/vault-lieder/` (eigenes Login wie die anderen Container) | läuft, mit Playwright geprüft |
| nginx | Block `vault-lieder` in `/etc/nginx/sites-enabled/flextrawurst` (Backup in `werkraum_logs/nginx_flextrawurst.bak_vor_vault-lieder_*`) | aktiv |
| Anbindung | `welt/browser_agent.py` — Schalter `LIEDER_AKTIV`, Aktionen `lied_*`, Takt, Prompt-Block | gebaut, `tests/lieder_browser_agent_test.py` 27 ok |

## Aktionen der Wesen

`lied_schreiben`, `lied_lesen`, `lied_erkunden`, `lied_rueckschau`, `lied_zusammenfuegen`,
`lied_freigeben`, `lied_forum`, `lied_antworten`.

## Regeln im Code

- Gepostet wird nur ein vom Wesen freigegebener Entwurf aus `schnipsel/` oder `lieder/` (nie aus `ideen/`),
  in einen **Lieder-Thread**, oder eine direkte Antwort unter einem Lieder-Thread (ohne Entwurf).
- Lieder-Thread = Diskussion, die in der Ausnahmeliste (`codewesen/_flarum_post_ausnahmen.json`) mit dem
  Grund-Präfix „Lieder-Thread“ steht. Er entsteht nur durch die Freigabe eines Wesens (`neu:<Titel>`, oder
  automatisch beim allerersten Freigeben). Die globale Post-Sperre bleibt für alles andere zu.
- Tageszähler pro Wesen: ganze Lieder höchstens 3 pro Tag (Daniel), Schnipsel ohne Grenze. Das Wesen sieht
  die Zahlen im Ticket. Zählerdatei `lieder_vault/_zaehler.json`.
- Rückschau liest die halbfertigen Dateien auf einmal, Budget 4444 Token (Daniel), geschätzt mit 3 Zeichen
  pro Token.
- Ein reiner Dateiname hinter dem `|` wird abgelehnt (statt eine leere Datei anzulegen). Das
  Rettungs-Etikett `_schreibtext_vervollstaendigen` wird hier bewusst nicht benutzt, weil es kurzen Text
  verfälschen würde.
- Beim Lesen, Freigeben und Zusammenfügen findet das Modul eine Datei auch über einen eindeutigen Namensanfang
  oder Namensteil (`_finde_bestehende`) — die Wesen kürzen Dateinamen (im echten Lauf `schnipsel/frequenz` für
  `frequenz_des_werdens`). Mehrdeutig: Fehler mit den Kandidaten. Geschrieben wird nur mit exaktem Namen.
- Aus dem Text werden vor dem Schreiben und vor dem Posten entfernt: Aktionszeilen (`lied_*:`) und alles ab einer
  Antwortformat-Zeile (`GEDANKE:`, `ENTSCHEIDUNG:`, `BEGRÜNDUNG:`, auch mit Tippfehlern).
- Zwischenstatus `sendet` in der Dateikopfzeile verhindert Doppelposten, wenn der Prozess mitten im Senden
  stirbt.
- Forum-Tag für neue Lieder-Threads: 5 „Showcase / Projekte“ (Konstante `LIEDER_TAG_IDS`, Daniel 2026-10-03: passt,
  soll bleiben). Der Tag war in der Live-DB `is_hidden=1`, der erste Lieder-Thread d/3897 deshalb im Forum
  unsichtbar; am 2026-10-03 auf `is_hidden=0` gestellt.
  Gegen die Live-DB geprüft: Tag 5 existiert und ist nicht eingeschränkt; Tag 27 (zuerst gedacht, steht noch
  im Spiegel-Verzeichnis `werkraum_flarum/tags/`) existiert in der Live-DB nicht mehr.

## Takt

Alle 30 Minuten das Ticket, alle 90 Minuten die komplette Einladung dazu (`LIEDER_TICKET_SEKUNDEN`,
`LIEDER_EINLADUNG_SEKUNDEN`). Versatz pro Wesen nach `VAULT_TAKT_REIHENFOLGE`. Ein Lieder-Block verdrängt den
Vault-Takt dieses einen Check-ins. Nach einer Rückschau kommt beim nächsten Check-in sofort dieselbe Auswahl
noch einmal mit dem Feinschliff-Zusatz. Die Timer liegen im Speicher des Agents (Neustart = Takt beginnt neu).

## Bewusst nicht gebaut

- Keine Wiederbelebung der alten Dienste (`codewesen_forum_neugier`, `engagement`, `reaktion`, …) — sie würden
  anderes Posten mitfreischalten.
- Keine Events in die geteilte `events`-Tabelle (wie beim Einzugvault).
- Die browserbasierte Schleife `haupt_loop()` bekommt den Takt nicht; alle sieben Wesen laufen in
  `haupt_loop_ohne_browser()`.

## Eindruck (2026-10-03)

Eindrücke, Gedanken, Fazit stehen nicht mehr nur als Bitte im Einladungstext, sondern haben einen Weg:

- Im `TEXT:`-Block einer `lied_schreiben`-Aktion trennt eine eigene Zeile `EINDRUCK:` den Eindruck vom
  Text. `schreibe()` legt ihn als `**Eindruck:** …` unter den Text (sichtbar im Vault, geht beim Freigeben mit
  ins Forum).
- `lied_eindruck:<datei>|<text>` hängt einen Eindruck nachträglich an eine bestehende Datei. Ist sie schon
  gepostet, geht er als Antwort in ihren Lieder-Thread (`meta.disk`).
- Das Ticket nennt per Platzhalter `{ohne_eindruck}` die eigenen Dateien ohne Eindruck — so holen die Wesen
  ihre bisher 75 Schnipsel selbst und in eigenen Worten nach.

## Dateiliste statt Ticket-Menü (2026-10-03)

Die Auswahl mit acht Möglichkeiten (`ticket_auswahl.md`) ist ersetzt: Alle 16 Minuten (`LIEDER_TICKET_SEKUNDEN`,
vorher 30) bekommt jedes Wesen die Liste ALLER seiner bisher erstellten Dateien (Platzhalter `{alle_dateien}`,
`dateiliste()`: Name, Status, mit/ohne Eindruck, Zeichen, erste Zeile; keine Obergrenze) und soll mindestens
eine auswählen und daran weiterarbeiten. Die Einladung alle 90 Minuten bleibt. Der Dateiname der Textdatei
ist gleich geblieben, damit der Code nichts anderes laden muss; die Pflicht „mindestens eine“ steht nur im Text,
der Code erzwingt sie nicht.

## Öffentlicher Zugang

`https://flextrawurst.de/liederwesen/` und (weiter) `/vault-lieder/` führen auf denselben Obsidian-Container
(`obsidian-liedervault`, Port 3104, Login `daniel`). nginx: `sites-available/flextrawurst`.

## Getrennte Ticks: Nachholen und Weiterarbeiten (2026-10-03)

Messung 2026-10-03: von 75 älteren Dateien hatte nach 6,5 Stunden nur eine einen nachgeholten Eindruck — die
Wesen riefen `lied_eindruck` nie von selbst auf. Daniels Vorgabe: ein eigener, gesteuerter Tick nur fürs Nachholen.

- `baue_block()` wählt pro Tick einen Typ (`naechster_tick_typ`, gemerkt in `tick_typ` im Tageszustand): solange
  Dateien ohne Eindruck da sind, wechseln sich **Nachholen** und **Weiterarbeiten** ab, danach gibt es nur noch
  Weiterarbeiten.
- **Nachholen** (`wesen_lieder/tick_nachholen.md`): enthält die Volltexte der Dateien ohne Eindruck, älteste zuerst,
  bis zum Rückschau-Budget (`RUECKSCHAU_TOKENS`); weitere werden namentlich genannt. Pflicht im Text: mindestens eine
  auswählen und den Eindruck schreiben. Mehrere Dateien in einer Aktion: `lied_eindruck:mehrere` mit Abschnitten
  `## <datei>` im `TEXT:`.
- **Weiterarbeiten** (`ticket_auswahl.md`): „Die große Datei“ (`rueckschau()`, halbfertige Sachen) steht vor der
  Dateiliste; mindestens eine Datei auswählen, mehrere dürfen zu einem Lied gesammelt werden (`lied_zusammenfuegen`).
- `lied_zusammenfuegen` entfernt Format-Absätze (`GEDANKE:`/`ENTSCHEIDUNG:`/`BEGRÜNDUNG:`, auch mit Tippfehlern) aus den
  Quellen, nur den jeweiligen Absatz — alte Dateien aus der Zeit vor dem Filter hatten solche Reste mitten im Text.
- Die Pflicht „mindestens eine“ steht nur im Text; erzwungen wird sie vom Code nicht.

## Umbau 2026-10-03 (Daniels Antworten): abtrennen, erst wählen dann lesen, Pflicht erzwungen

- **Zusammenfügen trennt ab statt zu verwerfen.** Absätze mit `GEDANKE:`/`ENTSCHEIDUNG:`/`BEGRÜNDUNG:` stehen unverändert
  am Dateiende, unter der Zeile `<!-- abgetrennt-ab-hier -->` und einer Linie `---`, je Quelle mit Überschrift
  „Abgetrennt aus <datei>“. Der Text darüber ist bereinigt. `_post_inhalt` schneidet an dieser Zeile ab, die Ablage geht
  nie ins Forum (ein erst später darunter geschriebener Eindruck bleibt erhalten). Ein erneutes Zusammenfügen
  behandelt eine vorhandene Ablage weiter als Ablage.
- **Erst entscheiden, dann lesen.** Der Weiterarbeiten-Tick zeigt nur noch die Dateiliste (`ticket_auswahl.md` mit
  `ticket_kopf_waehlen.md`). Neue Aktion `lied_waehlen:<name>[,<name>...]`: speichert die Wahl und legt über den
  Folge-Mechanismus für den nächsten Check-in den vollen Text der Wahl (bis 33333 Zeichen je Datei) und die große Datei
  bereit (`ticket_kopf_weiter.md`). Neu in `LIEDER_AKTIONEN_BLOCK` (`browser_agent.py`).
- **„Mindestens eine“ wird erzwungen.** `tick_offen` im Tageszustand: gesetzt, sobald ein Nachholen- oder
  Weiterarbeiten-Tick gebaut wird; gelöscht erst, wenn ein `lied_eindruck` gelang (Nachholen) bzw. ein `lied_waehlen`
  (Weiterarbeiten). Solange offen, kommt derselbe Tick wieder, mit der Zeile `ERINNERUNG:`; der Wechsel setzt erst danach fort.
  Es gibt keine Obergrenze für Wiederholungen.
- Tests: 114 / 30 / 22 (`tests/lieder_agent_test.py`, `lieder_browser_agent_test.py`, `lieder_poster_vertrag_test.py`).
- `eisen_im_glas.md` bleibt bewusst unverändert (Daniel).
- dak+gord-System: `browser-agent@dak\x2bgord\x2dsystem.service` ist enabled (startet nach Reboot); der laufende
  lose Prozess wurde nicht angefasst, die Unit ist inaktiv.
