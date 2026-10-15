# Native Windows-Programm

`/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py` ist der
native Programmeinstieg fuer das echte Windows-Overlay. Es ist kein Browser-
Frontend und kein Webserver.

Der aktuelle erste Ziegelstein ist absichtlich `observe-only`: Das Programm
oeffnet ein rahmenloses, immer sichtbares Overlay, liest die
`TargetRegistry` und zeigt Provenienz sowie real verfuegbare Original-Terminals.
Eingabe bleibt bis zu den spaeteren Capability-/Lease-/Not-Aus-Gates gesperrt.

Auf Windows bauen (Python 3.13 und Internetzugang fuer die feste Build-Abhaengigkeit):

```bat
client_windows\build_exe.bat
```

Das Ergebnis ist ein vollstaendiges `--onedir`-Bundle und liegt danach unter:

`/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge/AugenUndHaendeBridge.exe`

Ein reproduzierbares PE32+-Bundle liegt aktuell bereits an diesem Pfad. Es
wurde am 2026-09-20 in einem isolierten Wine-Prefix mit vollstaendigem
Windows-Python 3.13.5, PyInstaller 6.14.2 und `websockets` 16.1.1 gebaut.
Die aktuelle EXE hat SHA256
`68f55707dedf08ace0cf9de515015df25918996c88fbb236d842a7bad0e0418d`.
Der komplette `_internal`-Ordner gehoert zur Lieferung und darf nicht von der
`.exe` getrennt werden.

Für die Übergabe ist deshalb auch ein vollständiges Archiv vorhanden:

`/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G07-win64.zip`

Archiv-SHA256:
`291d682c905dbcd7352f1ae141eb9c82044de6e9843ade87b5bb8424c2fee34e`.
Archiv entpacken und anschließend die EXE innerhalb des entpackten
`AugenUndHaendeBridge/`-Ordners starten.

Der Bundle-Smoke unter Wine hat das echte Programmfenster gestartet. Das ist
ein Paket-/Startbeleg, aber noch keine native Abnahme auf Daniels echtem
Windows. Die native Win32-Fenster-, DPI-, Capture- und Eingabeprüfung bleibt
offen. Der Windows-Build auf echtem Windows bleibt mit demselben
versionierten Quellpfad reproduzierbar.

## VPS-Hand-off über SSH

Die EXE allein verbindet sich nicht mit dem VPS. Auf dem VPS muss zuerst der
aktuelle Relay aus
`/root/werkraum/augen_haende_bridge/client_vps/bridge_server.py` mit den
beiden Token-Umgebungsvariablen laufen. Auf Windows startet dann
`/root/werkraum/augen_haende_bridge/client_windows/start_with_ssh_tunnel.ps1`
einen SSH-LocalForward und anschließend die EXE:

```powershell
$env:BRIDGE_DESKTOP_TOKEN = '<das gleiche kurzlebige Desktop-Token wie auf dem VPS>'
& .\start_with_ssh_tunnel.ps1 -VpsHost '<VPS-DNS-oder-IP>' -VpsUser 'root'
```

Voraussetzung ist ein funktionierender OpenSSH-Schlüsselzugang mit geprüfter
`known_hosts`-Zeile. Das Skript setzt **nicht**
`StrictHostKeyChecking=no`, veröffentlicht keinen Port und beendet beim Ende
der EXE ausschließlich seinen eigenen SSH-Prozess.

Der Transport ist in der EXE vorhanden, aber opt-in. Der Launcher setzt lokal:

```text
BRIDGE_URL=ws://127.0.0.1:19880
BRIDGE_TOKEN=<kurzlebiges-operator-token>
```

Fehlt eine Variable, bleibt die EXE offline und verbindet sich nicht heimlich.
Beide Seiten bleiben loopback-only; SSH ist nur der verschlüsselte Transport
dazwischen.

## Nativer read-only Acceptance-Witness

Für den ersten echten Windows-Beleg gibt es zusätzlich
`/root/werkraum/augen_haende_bridge/client_windows/native_acceptance_witness.ps1`.
Er verwendet den vorhandenen Launcher, setzt nur den expliziten
`BRIDGE_NATIVE_SCAN_ON_START=1`-Testschalter und liest anschließend den
Fenstertitel/HWND/Rechteck der eigenen EXE über `user32.dll`. Danach schreibt
er einen Bildschirm-Screenshot und eine JSON-Evidence in den angegebenen
Evidence-Ordner. Er führt keine Maus-, Tastatur- oder Terminalaktion aus.

```powershell
$env:BRIDGE_DESKTOP_TOKEN = '<das gleiche kurzlebige Desktop-Token wie auf dem VPS>'
& .\native_acceptance_witness.ps1 -VpsHost '<VPS-DNS-oder-IP>' -VpsUser 'root'
```

Ein erfolgreicher Witness-Lauf belegt zunächst nativen Start, Scanmarker und
sichtbare Rücklese. Er behauptet noch nicht die spätere Zielauswahl oder
Binding-Rücklese. Der vollständige Bericht liegt unter
`/root/werkraum/augen_haende_bridge/tests/evidence/G10_NATIVE_ACCEPTANCE_WITNESS_EVIDENCE.md`.

Für den manuellen Zielauswahl-Beleg kann der Witness nach dem Scan auf deinen
Klick warten:

```powershell
& .\native_acceptance_witness.ps1 -VpsHost '<VPS-DNS-oder-IP>' -VpsUser 'root' -WaitForManualBinding
```

Nach dem Scan klickst du im Zielrail selbst einen nativen Scan-Eintrag an. Das
Skript liest nur den anschließenden `binding-readback`-Fenstermarker und nimmt
Screenshot/JSON auf; es führt den Klick nicht selbst aus.

Für die Übergabe von EXE und Witness gibt es das aktuelle G12-Archiv:

`/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G12-win64-handoff.zip`

Die autoritative SHA256-Prüfsumme steht außerhalb dieses Archivs in
`/root/werkraum/augen_haende_bridge/tests/evidence/G12_MANUAL_BINDING_WITNESS_EVIDENCE.md`;
die README enthält absichtlich keine Selbstreferenz auf ihren eigenen
Archivhash.

Beim Entpacken muss der komplette Ordner `AugenUndHaendeBridge/` erhalten
bleiben; die `.exe` darf nicht vom `_internal`-Ordner getrennt werden.
Der Launcher erkennt sowohl die Quellbaum-Struktur als auch die Struktur des
entpackten Handoff-Archivs automatisch.

Nach dem Windows-Lauf können JSON und PNG read-only gegen den Witness-Vertrag
geprüft werden:

```text
PYTHONPATH=. python3 tests/validate_native_binding_evidence.py --json <evidence.json> --screenshot <evidence.png>
```

`PASS` bedeutet nur, dass die gelieferten Artefakte konsistent sind; der
Validator ersetzt weder den echten Windows-Lauf noch Daniels Klick.

Das aktuelle G11-Bundle enthält zusätzlich die Scan→observe-only-Binding-
Verdrahtung. Die EXE hat SHA256
`265c9fa3713df411864d3dc7d04b8f6f97d34b947e8a7a3db7d1c3a9caf855cd`.
