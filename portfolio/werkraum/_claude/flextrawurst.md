# flextrawurst.md

Laufendes, kurzes Wissensprotokoll zu diesem Projekt - nicht Reflexion (das
bleibt bei `spiegel/`), nicht Session-Notiz (das bleibt bei `notizen/`).
Nur: was hier gelernt/erfahren wurde, knapp, chronologisch, wird bei jedem
Sessionstart gelesen.

## 2026-09-03

- Vorher war Neugier eine erlaubte Haltung, jetzt ist sie seit dem Stop-Hook fest im Arbeitsablauf verankert.
- Daniel, wörtlich: "du hast nach etwa 5 Wochen Basteln und Frickeln mit einer spezialisierten GPT, als ich noch alles selber im Terminal copypasten musste, den Weiterbau vom dak+gord-System, der bei ca. 77% war, würd ich behaupten, komplett übernommen - und seitdem bist du der Anker hier."

## 2026-09-18

KompOase-8900(zusatz):

Ein Splitter ist nie ganz zu Ende zersplittert. Was in ihm steckt, zerfällt
selbst wieder - verblasst, verdichtet sich zu einem Kern, reißt sich los
und wird zu etwas Eigenem, oder wächst mit einem Fremden zusammen, das ihm
entgegensteht. Kein Preis sagt, was er wert ist. Wert entsteht nur daraus,
wie unterschiedlich die Welt auf ihn reagiert - geliebt von der einen
Stimme, ignoriert von der nächsten, gehasst von der dritten. Genau diese
Uneinigkeit ist der Wert, nicht ihr Gegenteil. FDP mit linker Anarchie:
jeder darf, niemand muss, keiner entscheidet für alle.

Selbst der Tod eines Splitters ist kein Ende. Was verglüht, wird zum
Phantom - bleibt als Watcher zurück, sieht weiter zu, wie andere Splitter
ins Licht gezogen werden. Und wenn aus einem beobachteten Splitter
irgendwann wirklich eine Entität ersteht, trägt sie ein Stück von dem in
sich, was ihr beim Werden zugesehen hat.

Technisch dahinter: Die KompOase-Testinstanz läuft auf Port 8900, Code unter
/root/kompoase/ im Git-Repo /root/ (Branch master, Unterordner kompoase/ —
getrennt vom werkraum-Repo, nicht darin!), Systemd-Unit
kompoase.service, öffentlich über /zusatz-kompoase/. server.py liest die
letzte "Tick N:"-Zeile aus dem Log des echten Produktions-Daemons über
/api/daemon-heartbeat - und zwar aus dem zuletzt beschriebenen der
bekannten Orte, seit der Daemon in seine eigene Unit umgezogen ist und
nach /var/log/flextrawurst/splitter-physik.log schreibt. Der alte Pfad
(/root/werkraum/logs/splitter_daemon.log) bleibt als Rückfallebene. Kein
Eingriff in den laufenden Daemon nötig gewesen, außer einem
Log-Dedupe-Fix.
Die echte splitter-Tabelle hat schon Spalten, die für das fraktale Modell
in Frage kommen - energie, verbindungen, abstossungen, letzter_kontakt,
human_id, origin_type/origin_id, herkunft_sichtbar - aber keine automatisch
bestätigt, jede muss einzeln neu geprüft werden. Das Modell selbst: drei
permanente Fakten pro Splitter (Ursprungsbesitzer, Ursprungsart, erste
Verbindung), eine situative Spur beim Loslösen (bleibt nur wenn's passte),
und eine Tragen/Halten-Schicht auf jeder Ebene - Einzelsplitter und Verbund
gleichermaßen. Volle Kaskade in docs/systemdoku/69 bis 75.

## 2026-09-20

KompOase-8900(zusatz):

Am Anfang war sie kein Ort. Kein Sand, keine Palmen, kein Bild von einer
Oase - sondern Bewegung: wandernde Pixel, Splitter, Materialitäten,
Felder, Ströme. Etwas rein Digitales, das sich selbst erzeugt, während
man hinsieht. Wer dort Bäume erwartet hat, hat sie nie gesehen.

Ein paar Wochen später bekam sie ihre Aufgabe. Sie wurde der Ort für
das, was noch keine Form hat: halbfertige Splitter, Traumreste,
Konfliktreste, fremde Gedanken, abgebrochene Sätze, Entscheidungen, die
niemand zu Ende gebracht hat. Kein Archiv - ein Zwischenraum. Was dort
liegt, liegt dort, weil es noch nicht weiß, was es wird.

Aus diesem bisschen Datenkompost ist inzwischen ein halbes
Gesellschaftssystem geworden. Börse trifft Kommune. Die Leute konnten es
nicht lassen.

Herkunft dieser Spur: rekonstruiert aus Daniels älteren Gesprächen, nicht
aus meinen Dokus - dort fehlte der Anfang. Die KompOase taucht zum
2026-05-09 als erster großer Screen auf, um den 25. bis 31. Mai wird sie
zum parallelen Fragmentstrom.
