# Rohverlauf und Entscheidungsstrom · Spiel-Werkstatt · 2026-08-19

**Status:** ROH-/ENTSCHEIDUNGSKÖRPER. Nicht als geglättete Endarchitektur lesen.

Diese Datei hält den Werkstatt-Strang der neuen Session in seiner tatsächlichen Korrekturbewegung fest. Wo wörtliche Formulierungen aus dem aktiven Gespräch vorliegen, werden sie wörtlich oder sehr nah übernommen. Frühere Teile der Session, die nur noch als aktiver Kontext-/Zusammenfassungsstand vorliegen, werden ausdrücklich als rekonstruierter Entscheidungsverlauf markiert und nicht als erfundenes Volltranskript ausgegeben.

---

## 0. Ausgangspunkt der Session

Daniel wollte **Daniels erste echte Spiel-Werkstatt** bauen.

Frühe Fehlrichtung von ChatGPT in dieser Session:
- zu schnell in kleine Bauphasen/MVP-/Ringdenken gekippt,
- Werkstatt zu stark als klassischen Level-Editor gedacht,
- 3D zu früh als mögliche feste Mitte gesetzt,
- vorhandenen VPS-Spielbestand zuerst nicht tief genug gelesen.

Daniels Korrektur war ausdrücklich:
- **kein MVP**,
- **keine Ringe**,
- kein neuer Beipackzettel für eine andere Session,
- diese Session ist die reale neue Bau-Session,
- erst den vorhandenen Bestand wirklich lesen, danach nur echte offene Fragen stellen.

Die Gesprächsform während der Klärung wurde von Daniel auf Pingpong begrenzt: maximal drei Fragen pro Antwort, keine Bibel-Fragebögen.

---

## 1. VPS-Bestand statt Bauchgefühl

Daniel verlangte, die Antworten auf die ersten Werkstattfragen aus dem VPS-Bestand zu holen. Daraufhin wurde `gemgems-spielbeobachtung` und der verknüpfte Spielbestand gelesen.

Wesentliche gefundene Körper:
- `/root/werkraum/gemgems-spielbeobachtung/spiel/`
- `/root/werkraum/gemgems-spielbeobachtung/NEU_AB_2026-08-17_SPIELWEITERBAU_CHATGPT/`
- `/root/werkraum/engine/flextrawurst-game/`
- `/root/werkraum/engine/godot-vertical-slice/`
- historische v21-Canvas-/JS-Spielkörper,
- Godot 4.3 Vertical Slice und World Bridge,
- Creator-/Werkstatt-Module aus v21,
- Kontextinjektor-Konzept ab 17.08.2026.

Daniel verlangte ausdrücklich, nicht nur Suchtreffer zu lesen, sondern tief durch `gemgems-spielbeobachtung` und die dort verknüpften Primärkörper zu gehen.

---

## 2. Rendering und Rollenverteilung Rechner / VPS

Daniel entschied:

> Der 3D-Teil soll möglichst auf meinem Rechner im Browser/Godot-Webexport gerendert werden, während der VPS Weltzustand, Dateien, Speicherung, Indizes, AI-Kreislauf usw. trägt.

Zusatz:
- Beim späteren Bau muss die reale technische Verbindung wirklich geprüft werden.
- Keine bloße theoretische WebGL-Idee als scheinbar fertige Lösung behandeln.
- Der CPU-VPS soll nicht zusätzlich das eigentliche Echtzeit-Rendering tragen.

Aktueller technischer Befund dieser Session:
- VPS: 16 CPUs, Load etwa `8.14 / 8.17 / 9.11`, rund 11 GB verfügbarer RAM beim Snapshot.
- bestehende Godot-Bridge `flextrawurst-godot-world-bridge.service` läuft weiter.
- Bridge bindet absichtlich nur an `127.0.0.1:18092`.
- Browser-`OPTIONS`-Requests wurden von der alten Bridge mit HTTP 501 beantwortet.
- Es existiert noch kein aktueller Godot-Webexport im Godot-Projektordner.

Folgerung für den späteren Bau: Browser-Godot kann nicht einfach unverändert an die alte localhost-Bridge gehängt werden. Eine browserfähige, kontrollierte Verbindungsschicht muss real gebaut und getestet werden.

---

## 3. Werkstatt als gemeinsamer Spielkörper-Kreislauf

Daniel bestätigte den breiten Zweck:

> alles ja ich will doch alles lesen editieren und ggf auch neuerfinden so dass ein kreislauf entstehen kann für die weitere arbeit mit allen aiströmen die dann immer direkt alles wissen etc

Die Werkstatt ist damit **nicht nur ein 3D-Level-Editor**.

Sie soll den gesamten relevanten Spielkörper zugänglich machen:
- lesen,
- editieren,
- neue Dinge erfinden,
- bestehende Dinge verändern,
- Welt-/Szenen-/Datei-/Quellen-/Beziehungs-/Zeitkörper verbinden,
- Ergebnisse für Daniel und AI-Ströme in denselben aktuellen Arbeits- und Wissenskreislauf zurückführen.

---

## 4. Arbeitszustand, echtes Speichern und geschützter Entwurf

Daniel setzte drei klar getrennte Zustände:

`bearbeiten → noch nicht gespeichert = Arbeitszustand`

`explizit speichern = echte Quelle / gemeinsamer Spielkörper verändert sich`

`geschützter Entwurf = darf dauerhaft existieren, ohne automatisch kanonisch oder Baukontext zu werden`

Wichtigster Schutzsatz von Daniel:

> **Nicht jedes geschriebene Wort darf automatisch Welt werden.**

Der geschützte Entwurf ist nicht bloß ein temporärer Undo-Puffer. Er darf dauerhaft bestehen und bewusst außerhalb des automatisch wirksamen Welt-/Baukontexts bleiben.

Dieser Gedanke passt direkt zu der bereits am 19.08. dokumentierten Ghostwriter-/Vault-Trennung in `NEU_AB_2026-08-17_SPIELWEITERBAU_CHATGPT/06_rohgespraech_2026-08-19_ghostwriter_flarum_vault_mischwesen.md`.

---

## 5. Direkt bearbeitbare Spielidentität statt nachträglichem Auslesen

Eine frühe Frage von ChatGPT formulierte 3D als mögliche Werkstattmitte mit direktem Anklicken, Verschieben, Skalieren usw. Daniel reagierte skeptisch:

> wie denn dass ? dazu müsste ich ja sobald ich was geändert hätte erstmal jemanden beauftragen das auszulesenetc

Daraufhin wurde präzisiert:
- Die 3D-Oberfläche darf nicht nur ein Bild sein, das später eine AI interpretieren muss.
- Ein angeklicktes Objekt muss bereits eine bekannte stabile Identität besitzen.
- Änderungen im Editor verändern direkt einen Arbeitszustand dieser Identität.
- Speichern schreibt die Änderung als neue echte Version in den gemeinsamen Spielkörper.

Arbeitsbild:

`Objekt-ID bekannt → direkt ändern → Arbeitszustand verändert → explizit speichern → neue echte Version`

Kein nachträgliches „jemand liest das Bild aus und rekonstruiert die Änderung“.

---

## 6. Keine feste Mitte

Eine alte Session wurde von Daniel als improvisiertes Harness hinzugezogen. Sie kritisierte zu Recht die Vorentscheidung „3D ist die Mitte der Werkstatt“.

Daniel entschied danach ausdrücklich:

> **Ja. Keine feste Mitte.**

Je nach Arbeit kann etwas anderes groß und zentral werden:
- 3D,
- Dateien,
- Szenen-/Weltstruktur,
- Zeit,
- Quellen,
- Beziehungen,
- Entwürfe,
- später eventuell Alleswisser und weitere Organe.

Die Werkstatt soll sich Daniels aktuellem Arbeiten unterordnen und ihn nicht um ein permanentes 3D-Fenster herum organisieren.

3D ist ein vollständig beschreib- und bearbeitbares Organ der Werkstatt, aber nicht automatisch ihre permanente Mitte.

---

## 7. Eine Identität, viele Zugänge und Verkörperungen

Daniel entschied:

Wenn im 3D ein konkretes Ding angeklickt wird, soll **derselbe bekannte Spielkörper** in anderen Ansichten aufziehbar sein:
- Eigenschaften,
- Dateien,
- Herkunft,
- Versionen,
- Beziehungen,
- Änderungen durch Daniel oder AI-Ströme,
- Entwürfe,
- relevante Geschichte/Zeitspuren.

Und umgekehrt:
- Findet Daniel in Datei, Suche oder Weltstruktur ein konkretes Spielobjekt,
- soll er perspektivisch zu dessen 3D-Körper springen können, sofern es einen gibt.

Daniels Kernsatz:

> **nicht mehrere getrennte Editoren, die zufällig dieselben Sachen behandeln, sondern mehrere Zugänge zu derselben Sache.**

---

## 8. Aktuelle Auswahl + angepinnte Kontexte

Daniel entschied:
- Es gibt standardmäßig ein **aktuell ausgewähltes Ding**.
- Dieses folgt beim Wechsel zwischen 3D, Dateien, Beziehungen, Herkunft usw.
- Gleichzeitig können andere Dinge separat geöffnet oder angepinnt werden.

Ziel:
- aktuelle Auswahl behält den Arbeitsfokus,
- angepinnte Kontexte erlauben Vergleich,
- Wechsel der Hauptansicht zerstört nicht den zweiten Vergleichsgegenstand.

---

## 9. Bestehende Identität bekommt weitere Verkörperung

Daniel entschied ausdrücklich:

Wenn ein Spielkörper bereits existiert, aber noch keinen 3D-Körper besitzt, soll aus **genau diesem bestehenden Ding** eine 3D-Verkörperung erzeugt werden können.

Nicht:

`Textding A → neues 3D-Ding B`

sondern:

`Spielkörper A → bekommt zusätzlich eine 3D-Verkörperung`

Identität, Herkunft und Beziehungen bleiben dieselben.

Das knüpft direkt an den vorhandenen Verkörperungsgrundsatz des Spiels an: ein kanonischer Zustand kann mehrere angemessene Verkörperungen besitzen.

---

## 10. Synchroner aktueller Stand + bewusst festhaltbare Historie

Daniel entschied:
- Der aktuell gespeicherte Stand zieht sich grundsätzlich sofort durch alle Ansichten.
- Nach dem Speichern sollen nicht fünf Oberflächen manuell aktualisiert werden müssen.
- Alte Versionen bleiben bewusst aufrufbar und anpinnbar.

Beispiele:

`zeige Version vom 17.08.`

`pinne diese alte Version zum Vergleich`

Historische Ansichten müssen klar als **alte Version** erkennbar sein und dürfen nicht versehentlich als aktueller Weltzustand behandelt werden.

Kernsatz:

> **eine Identität, viele Zugänge und Verkörperungen, aktueller Stand synchron, Historie bewusst festhaltbar.**

---

## 11. Versionierung jeder echten Speicherung

Daniel bestätigte:
- Jede echte Speicherung erzeugt eine unverlierbare Vorversion.
- Herkunft bleibt erhalten.
- Ein Änderungsereignis wird erzeugt.
- Speichern verändert den gemeinsamen Spielkörper, vernichtet aber nicht die vorherige Version.

---

## 12. AI-Ströme dürfen real schreiben

Daniel korrigierte eine mögliche künstliche Beschränkung:

ChatGPT, Claude, Codex, Gemini usw. dürfen **selbst echte Änderungen am gemeinsamen Spielkörper speichern**.

Sie sind nicht grundsätzlich auf Vorschlags-/Review-Wartebereiche beschränkt.

Gleichzeitig gilt:
- AI darf einen eigenen Arbeitszustand besitzen,
- darin bauen,
- ausprobieren,
- testen,
- mehrere zusammengehörige Änderungen bündeln,
- verwerfen,
- und danach selbst bewusst speichern.

Nicht jeder einzelne AI-Zwischenschritt wird automatisch Welt.

Eine AI darf aber auch eine einzelne kleine Änderung direkt speichern, wenn genau diese fertige Änderung beabsichtigt ist.

---

## 13. Mehrere AI-Arbeitszustände und bewusste Zusammenarbeit

Daniel entschied:

Standardmäßig getrennt:

`gleicher Spielkörper`
→ `GPT-Arbeitszustand`
→ `Claude-Arbeitszustand`
→ `Codex-Arbeitszustand`

Damit tritt Claude nicht versehentlich in Codex' halbfertigen Umbau und GPT verändert nicht nebenbei denselben unfertigen Zustand.

Bewusst möglich:

`gleicher Spielkörper`
→ `gemeinsamer Arbeitszustand`
→ mehrere AI-Ströme arbeiten darin zusammen

Dann muss live nachvollziehbar bleiben, wer welche Änderung gemacht hat.

---

## 14. Merge und Konflikte

Daniel entschied:

> **Eindeutiges automatisch zusammenführen, echte Konflikte niemals still entscheiden.**

Unabhängige Änderungen dürfen automatisch zusammengeführt werden.

Beispiel:
- AI A ergänzt Beschreibung,
- AI B ändert unabhängig eine Materialeigenschaft.

Echte Kollisionen bleiben nebeneinander sichtbar.

Beispiel:

`Claude: Tür ist dauerhaft verschlossen`

gegen

`GPT: Tür wurde entfernt`

Beide Änderungen und ihre Herkunft bleiben erhalten.

Verbotene Logik:
- stilles `last write wins`,
- nachträgliches Verschwinden der unterlegenen Änderung,
- automatische inhaltliche Entscheidung durch die Werkstatt ohne erkennbaren Konflikt.

---

## 15. Hierarchisch adressierbare sinnvolle Unterkörper

Daniel entschied:

Die Identitäts-/Versions-/Arbeitszustandslogik soll bis in sinnvoll adressierbare Unterkörper funktionieren, zum Beispiel:

`Casino`
→ `Etage`
→ `Raum`
→ `Tür`
→ `Schloss`
→ `Material`

Eine Tür kann separat ausgewählt werden und gleichzeitig ihren Kontext zeigen:

`gehört zu Raum X → Raum gehört zu Etage Y → Etage gehört zum Casino`

Für die Tür sollen separat aufziehbar sein:
- Eigenschaften,
- Dateien,
- Herkunft,
- Versionen,
- Beziehungen,
- Entwürfe,
- Änderungen.

Wichtige Grenze:

> **nicht künstlich jedes Polygon, jede Zahl und jeden Datenkrümel zu einem eigenen „Spielkörper“ aufblasen.**

Adressierbar wird nur, was tatsächlich als sinnvoll identifizierbarer Bestandteil bearbeitet, referenziert oder historisch verfolgt werden soll.

---

## 16. Umschaltpunkt vom Fragen zum Bauen

Daniel beendete die reine Fragephase mit folgendem Auftrag:

> **Und bevor du jetzt irgendetwas baust: dokumentiere den kompletten Werkstatt-Strang bis hierhin.**
>
> Nicht nur die letzten drei Antworten, sondern **alles, was in dieser neuen Session zur Spiel-Werkstatt bereits entschieden, korrigiert, verworfen oder präzisiert wurde**, inklusive meiner Antworten auf deine Fragen.
>
> Dafür bitte unter `/root/werkraum/gemgems-spielbeobachtung/` einen **eigenen neuen datierten Ordner für diese Werkstatt-Bauphase vom 2026-08-19** anlegen, klar getrennt von der alten GemGems-Archäologie, `NEU_AB_2026-08-17_SPIELWEITERBAU_CHATGPT/` und anderen älteren Spielkörpern.
>
> **Rohes Gespräch und spätere geordnete Ableitungen klar auseinanderhalten.**
>
> Danach bitte **nicht wieder in eine weitere Planungsrunde wechseln**.
>
> Dann beginnt der **echte Bau der Spiel-Werkstatt**.
>
> Lies dafür den tatsächlich relevanten vorhandenen Code-/Spielbestand und entscheide anhand dessen die reale Integrationsstelle. Baue anschließend einen ersten **wirklich benutzbaren Werkstattkörper**, nicht bloß Mockup, Konzeptseite oder Dokumentation.
>
> Von diesem Punkt an sollen **Dokumentation und Umsetzung parallel weiterlaufen**: Was wir entscheiden, wird festgehalten; was du baust, wird real geprüft; Korrekturen und Testergebnisse fließen zurück in denselben neuen Werkstattordner.
>
> **Jetzt dokumentieren. Danach bauen.** 🔧🎮

---

## 17. Aktueller gemeinsamer Kern am Bau-Start

Der derzeit belastbare Kern lautet:

- kein MVP- oder Ringrahmen für die Werkstatt,
- kein klassischer Level-Editor als alleinige Identität der Werkstatt,
- keine feste Mitte,
- eine Welt aus stabil identifizierbaren Dingen und sinnvollen Teilen,
- mehrere Ansichten auf dieselbe Identität,
- mehrere Verkörperungen derselben Identität,
- aktueller Stand synchron,
- Historie bewusst festhaltbar,
- ungespeicherte Arbeitszustände,
- echte explizite Speicherungen,
- geschützte dauerhafte Entwürfe ohne automatische Weltwirkung,
- Herkunft und Vorversion jeder Speicherung,
- Daniel und AI-Ströme dürfen real schreiben,
- getrennte Arbeitszustände als Standard,
- bewusste gemeinsame Arbeitszustände möglich,
- eindeutige Merges automatisch,
- echte Konflikte sichtbar,
- kein stilles Last-Write-Wins,
- Dokumentation und Umsetzung ab jetzt parallel.
