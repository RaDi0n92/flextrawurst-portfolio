# Aktiver Arbeitskörper

## Wozu dieser Baum dient

Der Ordnerbaum ist ein minimaler Obsidian-Vault mit realen Dateien als Gewebe. Der Planer, seine Objekt-IDs, Kanten, Ereignisse und Spuren sind die Nervenbahnen dazu. Kein Bereich darf eine zweite Wahrheit führen.

| Bereich | Organfunktion | Darf liefern |
|---|---|---|
| `00_Start` | Orientierung und Arbeitsvertrag | Einstieg, aktueller Baupfad, Begriffe |
| `01_Material` | Eingang/Gedächtnis | Originale, Quellen, Dateien, Herkunft |
| `02_Ideen` | Denken ohne falsche Tatsachen | Rohideen, Fragen, Varianten, klar als Entwurf |
| `03_Abläufe` | Nervenbahnen | Schritte, Zustände, Bedingungen, Ein-/Ausgänge, Stopps, Belege |
| `03_Gemeinsame_Arbeit` | gemeinsames Gedächtnis | Prüfungen, Entscheidungen, Agenten-/Menschenbeiträge, offene Übergaben |
| `04_Automationen` | kontrollierte Reflexe | explizite Trigger, Rechte, Eingaben, Runs, Logs, Fehlerwege |
| `05_Übergaben` | Schnittstellen | lesbare Übergaben mit realem Stand, Grenzen und nächsten Handlungen |
| `06_Redteam-Umbau` | Immunsystem | Gegenbeweise, Akzeptanztests, bekannte Risiken, bestätigte Fixes |

## Eine Arbeitszelle

Jede konkrete Arbeit wird als zusammenhängende Zelle behandelt:

`Gegenstand → Nutzerhandlung → Ergebnis/Beleg → Ereignis/Spur → nächste Verbindung`

- **Gegenstand:** reale Datei, Objekt-ID, Kante oder Feedback-ID.
- **Nutzerhandlung:** was ein Mensch/Agent tatsächlich tun soll.
- **Ergebnis/Beleg:** sichtbares Resultat, API-Antwort, Test und bei Speicherung Reload.
- **Ereignis/Spur:** wer, warum, wann, mit welcher Grenze.
- **Nächste Verbindung:** die aus Sokrates + 3× Redteam abgeleitete konkrete Folgefrage.

## Fester Bearbeitungszustand für selbst erzeugtes Feedback

`offen → live nachvollzogen → Fix gebaut → Playwright geprüft → Reload geprüft → 3× Redteam → Folgefeedback gespeichert → erledigt`

Keinen Pfeil überspringen. Ein UI-Klick ohne echte Speicherung ist kein Ergebnis. Eine Datei ohne Rückbindung an Objekt/Ereignis ist noch keine Nervenzelle; die fehlende Verbindung wird als offenes Feedback notiert.

## Erkunden und weiterbauen

- **Bauauftrag und alle Regeln:** `00_Start/00_MEIN_GESAMTKONSTRUKT_PLANER_BAUAUFTRAG.md`
- **Real geplanter Ablauf:** `03_Abläufe/01_Gesamtplan_Durchfuehrung.md`
- **Gemeinsame Entscheidungen, Prüfungen und Grenzen:** `03_Gemeinsame_Arbeit/PROTOKOLL.md`
- **17 Replica-Zwecke, Erweiterungen und Nutzerlücken:** `03_Gemeinsame_Arbeit/01_REPLICA_RECHERCHE_ERWEITERUNGEN_UND_NUTZERWUENSCHE.md`
- **Was im Cloud-Browser tatsächlich gegengeprüft wurde:** `03_Gemeinsame_Arbeit/02_CLOUDBROWSER_GEGENPROBE_REPLICAS_2026-08-22.md`
- **Was nur gesichert, was offen und was widerlegt ist:** `06_Redteam-Umbau/STATUS.md`

Jeder kann diese Dateien über **Start hier** oder **Ordner & Dateien** auf der URL öffnen. Weiterbauen heißt: betroffenes Material öffnen, Änderung klein und nachvollziehbar machen, dann dieselbe Arbeitszelle samt Beleg und Folgefrage ergänzen.

## Der aktuelle Baupfad

1. Den gemeinsamen Arbeitskörper und seine Spuren konsistent an den bestehenden Planerbestand anbinden.
2. Den nächstbesten offenen Feedbackpunkt nur nach diesem Zustandsmodell bearbeiten.
3. Pro betroffener Replica ihre eigene Kernhandlung, Datenrechte und ihr Resultat prüfen — keine bloße Ansicht.

## Nicht behaupten

- Dass ein Dokument automatisch bereits ein Planerobjekt oder eine Kante ist.
- Dass sichtbare UI-Reaktion schon Persistenz, Ausführung oder eine Replica-Kernhandlung beweist.
- Dass Altbestand (`07_AI-Spuren`) bereits sauber in `03_Gemeinsame_Arbeit` überführt wurde.
