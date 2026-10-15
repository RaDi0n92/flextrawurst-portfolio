---
datum: 2026-08-13
betrifft: [browser-recorder, postreload, p6, recovery-isolation, p7]
importable: false
autor: codex bei Daniels VPS
---

# Browser Recorder — Post-Reload und P6

## Was ich gelesen habe

Ich habe den laufenden Service, die geladene Extension und den read-only P6-Runner geprüft. Der Service startete nach dem kontrollierten Reload mit neuer PID; Chromium meldete Extension v1.8.0.

Ich habe den sichtbaren Smoke-Import im Chat `Neuer Abschnitt RISSWANDLER` verfolgt. Das Sidepanel zeigte wieder „Aufnahme freigegeben“, der Zugangsschlüssel wurde nur über das sichtbare Feld gesetzt und nicht ausgegeben.

Danach habe ich die fünf neuen P6-Artefakte und den kombinierten Vergleich gelesen. Die alten historischen Ordner blieben außerhalb des Schreibpfads; der Gate-Lauf meldete null Mutationen.

## Was ich verstehe

Der Reload war nötig, weil ein Service-Neustart allein die bereits injizierten Content-Scripts nicht ersetzt. Ein einzelner Chat-Reload hat den Adapter neu injiziert; danach war der Smoke-Import ausführbar und die neue Recovery-Identität sichtbar.

## Was ich nicht verstehe

Noch offen bleibt, warum die aktuelle Vergleichsmenge gegenüber dem vorherigen P6-Lauf von 190 auf 171 Matches gefallen ist. Das ist ein echter neuer Befund und darf nicht ohne weitere zeitliche oder textuelle Prüfung als Regression etikettiert werden.

## Was mich interessiert

Mich interessiert, welche der 19 verlorenen Matches durch aktuelle Chat-Oberflächenänderung, Textfortschreibung oder den Zeitpunkt der Sichtung entstanden sind. Die neue Vergleichsdatei hält die Klassen getrennt genug, um diese Frage später gezielt zu untersuchen.

## Was zusammenhängt und wie

Service-Reload lädt den Receiver neu. Extension-Reload lädt den Hintergrund und die Sidepanel-Ressourcen neu. Chat-Reload injiziert den Content-Script-Teil neu. Danach schreibt ein historischer Import in einen Recovery-Ordner, während P6 read-only nur eine unabhängige Sichtung in `audit_runs/` erzeugt. Der Vergleich liest beide Körper, verändert keinen.

## Was konzeptionell darin steht

Die Isolation ist jetzt nicht mehr nur ein Testversprechen. Sie hat den Übergang durchlaufen: echter Browser-Import, eigener `recovery_run_id`, unveränderter stabiler Quellordner, danach unabhängige P6-Sichtung. Herkunft bleibt an jedem Übergang sichtbar.

## Was mich heute beschäftigt hat

Der Moment zwischen Reload und Smoke-Test war der kritische Teil. Die Extension war technisch neu geladen, aber die alten Tabs waren noch nicht wieder freigegeben. Erst der gezielte Chat-Reload machte aus „Adapter wird geprüft“ wieder eine tatsächlich nutzbare UI.

## Was mich noch beschäftigt

171 Matches sind kein grünes Ergebnis, aber ein ehrlicheres neues Messbild. P7 bleibt deshalb `false`. Die Recovery-Isolation ist bestanden; die semantische Vollständigkeit ist es nicht.

## Tiefer eingetaucht

Der Smoke-Import lief mit einem realen Wheel-Schritt von 163 Pixeln bei 233 Pixel Viewporthöhe: 0,3004 Überlappung. Er erzeugte den Recovery-Lauf `recovery-import-2026-08-13T072846850Z-de56eaf8`. Die fünf P6-Sichtungen hatten 290, 75, 214, 204 und 170 stabile Fenster, jeweils ohne Fehler und am End-Sentinel.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein sauberer Neustart mit einem unangenehm ehrlichen Messgerät. Das System tut jetzt das Richtige, aber die Zahlen erlauben weiterhin keine bequeme Erfolgserzählung.

## Warum dieser Code / diese Datei wohl existiert

Der Code trennt historische Wiederholung von Live-Aufnahme. Diese Notiz hält fest, dass die Trennung nicht nur im Temp-Test, sondern nach Reload im echten sichtbaren Browserpfad wirksam war.

## Was ich beim Bauen brauche

Für weitere Änderungen brauche ich weiterhin den echten Service, den geladenen Extensionstand und getrennte read-only Runner. Die alte Quelle bleibt Referenzmaterial; neue Recovery- und P6-Läufe bekommen eigene IDs und eigene Ordner.

## Was noch fehlt bevor wir bauen können

Es fehlt kein weiterer Isolation-Bauschritt. Vor einer P7-Entscheidung fehlt aber eine Ursachenanalyse der 19 Match-Differenz und gegebenenfalls eine nochmals gezielte Sichtung der betroffenen IDs.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Ein Reload soll nicht nur Code neu laden, sondern die Herkunftskette wieder anschlussfähig machen: Receiver, Extension, Tab und Recovery-Ordner müssen dieselbe neue Identität tragen, ohne die alte Quelle zu verschieben.

**Code-Skizze**

```python
postreload = {
    "service_reloaded": True,
    "extension_version": "1.8.0",
    "recovery_run_id": recovery_run_id,
    "p6_run_id": "audit-20260813T-p6-postreload-combined-v1",
    "historical_folder_mutations": [],
    "p7_eligible": False,
}
```

## Was ich mir merken will

Extension-Reload und Chat-Tab-Reload sind zwei verschiedene Dinge. Ein neuer Service-Prozess beweist noch nicht, dass ein bestehender Tab neue Content-Scripts verwendet.

## Dokumente gehören zusammen

Zusammengehören: die native Isolation in `browser_capture.py`, die Ack-Propagation, der echte Recovery-Smoke-Ordner, die fünf Post-Reload-P6-Dateien, der kombinierte Vergleich und der Isolationsgate. Die alten P6-Berichte bleiben unveränderte Vergleichsbasis.

## Was mich überrascht hat

Der echte Smoke-Import erzeugte trotz nur eines Wheel-Schritts bereits neun historische Records und eine sichtbare Belegkette. Gleichzeitig blieb der alte Quellordner frei von historischen Events. Die technische Trennung funktioniert also auch unter der realen UI-Schicht.

## Wenn wir das bauen

**Vision-Schicht**

Wir bauen eine Geschichte, in der ein Neustart die Anschlüsse erneuert, nicht die Herkunft verwischt. Der Recovery-Lauf darf wachsen; die Quelle bleibt still und lesbar.

**Code-Skizze**

```python
assert recovery_manifest["capture_scope"] == "historical_import_recovery"
assert recovery_manifest["source_folder_immutable"] is True
assert stable_messages_does_not_contain("historical_import_")
assert p6_gate["historical_folder_mutations"] == []
```

Als nächster Schritt kommt Analyse der Differenzklassen, nicht blindes Freischalten von P7.

## Resonanz

[[abwurf: Die Recovery-Isolation ist bestanden; die semantische Vollständigkeit ist es nicht.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Service, Extension-Hintergrund, Content-Script, sichtbares Sidepanel, Recovery-Ordner, read-only P6 und P7-Gate bilden eine Kette. Jede Schicht hat ihren eigenen Reload- oder Beweiszeitpunkt. Der Fehler wäre, diese Zeitpunkte als einen einzigen Zustand zu behandeln.

## Was das Gespräch hinzugefügt hat

Daniels „go“ hat den Wechsel von vorbereiteter Implementierung zu kontrolliertem Live-Betrieb ausgelöst: Backup, Reload, Schlüsselübergabe, Smoke-Test und neue P6-Sichtung.

## Vergessen-Wollen

Vergessen werden soll der Impuls, aus `p6_isolation_passed` automatisch `p7_eligible` zu machen. Das Gate prüft Provenienz, nicht semantische Gleichheit.

## Was fehlt noch

- Ursachenanalyse der 19 Match-Differenz;
- optional gezielte Wiederholung nur der betroffenen IDs;
- keine P7-Freigabe ohne neuen Beleg.
