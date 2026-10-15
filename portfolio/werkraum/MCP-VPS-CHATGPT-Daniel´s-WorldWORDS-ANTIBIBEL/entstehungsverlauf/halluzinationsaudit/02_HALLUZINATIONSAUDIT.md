# Halluzinationsaudit der Metamonster-Wortsuche

Erstellt UTC: `2026-07-26T09:53:35.210796+00:00`

## Ergebnis in einem Satz

Die Dateimessungen waren überwiegend real, aber mehrere sprachliche Schlussfolgerungen waren zu stark: Dateizahl wurde mit Quellenzahl verwechselt, Userrollen-Datensätze mit Daniels eigener Formulierung, gespeicherte Attribution mit Urheberschaft und konsolidierte Systemtexte mit Geburtssituationen.

## Konservativer Userrollen-Korpus

- Userrollen-Textdatensätze insgesamt: `2440`
- `AUTOMATISCH_ODER_SYSTEMISCH`: `347`
- `USERROLLE_MIT_EINGEFUEGTEM_ODER_UNKLAREM_MATERIAL`: `197`
- `WAHRSCHEINLICH_AKTUELLE_MENSCHLICHE_EINGABE`: `1896`

### Nach Provider

- **claude:** `AUTOMATISCH_ODER_SYSTEMISCH=347`, `USERROLLE_MIT_EINGEFUEGTEM_ODER_UNKLAREM_MATERIAL=132`, `WAHRSCHEINLICH_AKTUELLE_MENSCHLICHE_EINGABE=1190`
- **codex:** `USERROLLE_MIT_EINGEFUEGTEM_ODER_UNKLAREM_MATERIAL=65`, `WAHRSCHEINLICH_AKTUELLE_MENSCHLICHE_EINGABE=706`

> Auch die Klasse `WAHRSCHEINLICH_AKTUELLE_MENSCHLICHE_EINGABE` beweist nur, dass Daniel den Text wahrscheinlich aktuell übermittelt hat. Sie beweist nicht, dass jedes enthaltene Wort von ihm erfunden wurde.

## Korrigierte Hauptpunkte

### Der VPS sei ein 3,8-GB-Sprachbiotop.

- **Status:** `VERWORFEN`
- **Befund:** 3,8 GB war keine gültige Beschreibung des VPS. Aktuell gemessen: Root-Dateisystem 997.388.681.216 Byte Gesamtgröße, 510.450.950.144 Byte belegt.
- **Folge:** Nur noch als dokumentierter Assistenzfehler zitieren.

### Der VPS sei ungefähr 500 GB groß.

- **Status:** `HERABGESTUFT_ZU_PRAEZISE`
- **Befund:** Ungefähr 500 GB beschreibt die belegte Datenmenge brauchbar. Die Gesamtkapazität liegt bei knapp 1 TB.
- **Folge:** Formulieren: rund 510 GB belegt auf einem knapp 1-TB-Dateisystem.

### 20.258 Dateien und rund 630 MB wurden gelesen.

- **Status:** `BESTAETIGT_MIT_SCOPE`
- **Befund:** Stimmt für den Werkraumscanner mit Dateityp-, Größen- und Ausschlussfiltern. Kein Vollscan aller Dateien.
- **Folge:** Immer Scannerfilter und Ausschlüsse nennen.

### 4.359.693 Außenraum-Textdateien wurden gelesen.

- **Status:** `BESTAETIGT_MIT_SCOPE_ABER_IRREFUEHREND_OHNE_KONTEXT`
- **Befund:** Technisch stimmt der gefilterte Zähler. 4.296.955 davon stammen allein aus /root/zensi und sind stark durch generierte/gespiegelte Massenkörper geprägt.
- **Folge:** Nicht als Millionen unabhängiger Sprachquellen darstellen.

### Null Lesefehler.

- **Status:** `BESTAETIGT_NUR_TECHNISCH`
- **Befund:** Die Scanner meldeten null Exceptions. Das beweist weder korrekte Sprecherzuordnung noch semantische Vollständigkeit.
- **Folge:** Nur als null Scanner-Ausnahmen bezeichnen.

### 2.884 direkte Nachrichten von Daniel aus Claude, Codex und Zensi.

- **Status:** `VERWORFEN`
- **Befund:** Zensi war nie direkt im Einsatz. Außerdem enthielt der Korpus automatische und eingefügte Datensätze.
- **Folge:** Frühere Zahl vollständig außer Kraft setzen.

### 2.440 direkte Nachrichten von Daniel aus Claude und Codex.

- **Status:** `HERABGESTUFT`
- **Befund:** Es sind 2.440 deduplizierte Userrollen-Textdatensätze im alten Heuristiklauf. Darunter automatische Taskmeldungen, Kompaktzusammenfassungen und eingefügtes Material.
- **Folge:** Nur konservativ klassifizierten Korpus verwenden.

### Dutzende Claude-Code-Sitzungen mit mehreren Dateien über 20 MB.

- **Status:** `VERWORFEN`
- **Befund:** Aktuelle Messung: genau eine Claude-Datei und eine Codex-Datei sind größer als 20 MiB. Dutzende Sitzungen existieren, aber nicht mehrere Dutzend Großdateien.
- **Folge:** Aussage nicht weiterverwenden.

### Frühe AI-Gesprächssammlung etwa 3,3 MB.

- **Status:** `BESTAETIGT`
- **Befund:** 87 Dateien mit zusammen 3.239.445 Byte.
- **Folge:** Als ungefähr 3,24 MB beziehungsweise 3,09 MiB angeben.

### Ein 250-Seiten-Kimi-Körper.

- **Status:** `UNKLAR`
- **Befund:** Die Zeichenfolge 250seiter steht im Dateinamen. Seiten wurden nicht unabhängig nachgezählt.
- **Folge:** Nur sagen: Datei trägt 250 Seiten im Namen.

### Sieben frühe Flextrawurst-Visionen.

- **Status:** `BESTAETIGT_MIT_SCOPE`
- **Befund:** Eine explizite Reihe V1 bis V7 existiert. Daneben gibt es weitere relevante Visionstexte und zusätzliche V1-benannte Dateien.
- **Folge:** Als V1-bis-V7-Reihe bezeichnen, nicht als gesamten Visionbestand.

### Zensi-Userfelder seien direkte Daniel-Nachrichten.

- **Status:** `VERWORFEN`
- **Befund:** Daniel stellte ausdrücklich klar, dass Zensi nie direkt eingesetzt wurde.
- **Folge:** Zensi nur als importierte, gespiegelte, generierte oder ungeklärte Schicht behandeln.

### Datenbankangabe Angelegt von X beweise, dass Wesen X den Namen erfand.

- **Status:** `HERABGESTUFT`
- **Befund:** Das Feld belegt nur eine gespeicherte Attribution im System. Es beweist weder reale autonome Handlung noch sprachliche Ersturheberschaft.
- **Folge:** Existenz und gespeicherte Attribution getrennt berichten.

### Grellader, Stillgift, Gesternöl und andere seien Daniels Wörter.

- **Status:** `UNKLAR`
- **Befund:** Ihre Existenz im Katalog ist bestätigt. Daniels alleinige Urheberschaft ist ohne älteren Ursprungskörper nicht belegt.
- **Folge:** Als Weltwörter mit ungeklärter Urheberschaft führen.

### Metamonster sei ein aktuelles Daniel-Fundstück.

- **Status:** `BESTAETIGT`
- **Befund:** Daniel bezeichnete sich im aktuellen Auftrag selbst als Metamonster.
- **Folge:** Direkte Fundstelle erhalten; Bedeutung noch nicht überdehnen.

### Wortlike sei eine bewusste Daniel-Wortschöpfung.

- **Status:** `UNKLAR`
- **Befund:** Wortlike steht in Daniels aktueller typo-reicher Nachricht. Bewusste Setzung, Tippfehler oder spontaner Fehlerkeim ist nicht geklärt.
- **Folge:** Nur als Rohfund/Fehlerkeim führen.

### Livesupport sei direkt von Daniel verwendet worden.

- **Status:** `BESTAETIGT`
- **Befund:** Im frühen GPT-5-Dialog sagt Daniel selbst, es gehe um eine Art livesupport. Das Wort ist jedoch allgemeinsprachlich und nicht automatisch Daniels Neuschöpfung.
- **Folge:** Direkte Verwendung von Urheberschaft unterscheiden.

### Ideenmonstrum und organisch wachsendes Ideenkonstrukt seien Daniels frühe Formulierungen.

- **Status:** `BESTAETIGT`
- **Befund:** Beide stehen direkt in Daniels Eingabe am Beginn des V1-Dialogs.
- **Folge:** Als starke Daniel-Sprachspur aufnehmen.

### Bildhauen sei Daniels Begriff.

- **Status:** `BESTAETIGT_STARK`
- **Befund:** Daniel schreibt explizites bildhauen; Kimi antwortet danach Das Bildhauen, wie du es nennst.
- **Folge:** Als starke Daniel-Prägung führen.

### Stundenverlaufssystemwesen und Formfadenprompts seien Daniels Formulierungen.

- **Status:** `BESTAETIGT_STARK`
- **Befund:** Daniel verwendet beide direkt in seinem frühen Kimi-Dialog.
- **Folge:** Als starke Daniel-Spur führen; genaue Schreibvarianten erhalten.

### Robotermodus sei allein von Daniel erfunden.

- **Status:** `HERABGESTUFT_ZU_GEMEINSAMER_ENTSTEHUNG`
- **Befund:** Die AI sprach zuvor vom Maschinenmodus. Daniel setzte danach konkret Wenn eher so... robotermodus wurde ausgelöst; die AI übernahm und systematisierte es.
- **Folge:** Gemeinsame Entstehung, konkrete Schlüsselformulierung durch Daniel.

### Punktbühne sei sicher Daniels Wort.

- **Status:** `UNKLAR`
- **Befund:** Punktbühne steht im konsolidierten Formfadenprompt, aber im bisher gelesenen früheren Dialog wurde die Geburt nicht gefunden.
- **Folge:** Keine Urheberschaft behaupten.

### Forschungssnack sei sicher Daniels Wort.

- **Status:** `UNKLAR_GEMEINSAM_MOEGLICH`
- **Befund:** Der Begriff ist im gemeinsam gewachsenen Stundenkörper häufig. Die früheste Sprecherstelle wurde noch nicht sicher identifiziert.
- **Folge:** Gemeinsam/unklar bis Ursprung gelesen ist.

### NULLSTUNDEN sei sicher Daniels Wort.

- **Status:** `UNKLAR`
- **Befund:** Der Begriff ist als Dateiname und späterer Systemkörper belegt. Der Dateiname allein beweist die Geburt nicht.
- **Folge:** Ursprung offenlassen.

### ChatGPT.com sei vollständig nach allen jemals vorhandenen Sessions durchsucht worden.

- **Status:** `NICHT_BEHAUPTBAR`
- **Befund:** Erreichbare Bibliotheks-/Gesprächsdateien und VPS-Exporte wurden durchsucht. Eine vollständige Kontoweitsuche ist technisch nicht belegt.
- **Folge:** Reichweite immer ausdrücklich begrenzen.

## Navigation

- [[entstehungsverlauf/halluzinationsaudit/00_AUDITREGELN|Auditregeln]]
- [[entstehungsverlauf/halluzinationsaudit/05_WORT_HERKUNFTSAUDIT|Wort-Herkunftsaudit]]
- [[entstehungsverlauf/halluzinationsaudit/07_QUELLEN_MIT_AI_HALLUZINATIONEN|Alte Quellen mit AI-Halluzinationen]]
- [[HOME|Vault Home]]
