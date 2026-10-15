---
datum: 2026-09-20
autor: codex bei Daniels VPS
herkunft: Fensterscanner-Vertrag aus V3-Baustartprüfung und Windows-Zielanforderung
status: V3.4 Win32-Adapter implementiert; native Windows-Abnahme offen
---

# V3.4 — Windows-Fensterscanner-Kern

## Ergebnis

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/windows_scanner.py`
implementiert den read-only Inventarkern für Windows. Der Scanner erzeugt pro
Scan:

- das vollständige Windows-Desktop-Ziel als `default_target_id`;
- sichtbare Top-Level-Fenster in EnumWindows-Reihenfolge;
- Handle, Generation, Titel, Klasse, Rechteck, Z-Order, Prozess-ID und —
  soweit Windows erlaubt — Prozesspfad;
- ein Capability-Profil, das zunächst nur `inventory` behauptet;
- die vom Aufrufer gelieferte visuelle Frame-Referenz und den Frame-Hash.

Pixel-Capture, Overlay, UI-Automation, Binding und Input sind absichtlich nicht
in diesem Baustein versteckt.

## Identität

`windows:window:<hwnd>` ist die auswählbare Ziel-ID. Die Generation wird in
der Scannerinstanz erhöht, wenn sich Prozess-ID oder Fensterklasse für denselben
Handle ändern. Titel- oder Geometrieänderungen erhalten damit dieselbe
Identität; ein Handle-Reuse mit anderem Prozess wird nicht still als dasselbe
Ziel behandelt.

Das ist eine In-Memory-Generation, noch keine über Neustarts persistierte
Windows-Prozessstartzeit. Diese stärkere Identität bleibt offen und braucht
native Tests auf Daniels Windows.

## Prüfstatus

Die Fake-API-Tests unter
`/root/werkraum/augen_haende_bridge/tests/test_windows_scanner.py` prüfen
Default-Desktop, Fensterinventar, Generationen und fehlenden Frame-Zeugen.
Der Linux-VPS kann den Win32-Adapter nicht nativ ausführen. Der Teststatus ist
deshalb Core-/Adaptervertrag, kein Windows-Native-PASS.
