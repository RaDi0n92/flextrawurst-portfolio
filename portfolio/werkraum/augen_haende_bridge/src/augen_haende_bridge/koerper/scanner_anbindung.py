"""Verbindet den Scanner-Knopf eines TerminalFensters mit dem Fensterscanner und dem read-only Binding (R015, R120).

Benutzt unverändert: `windows_capture.py` (Frame-Zeuge), `windows_scanner.py` (Inventar, Generation),
`read_only_binding.py` (G09: Binding nur für genau diese Generation und diesen Frame, Rücklese fail-closed) und die
`SCANNER_PROOF_SEQUENCE` der Harness. Ablauf je Knopfdruck:

    SCAN_REQUESTED → FRAME_CAPTURED → INVENTORY_READ → TARGET_SELECTED (Daniels Auswahl im Menü)
    → IDENTITY_VERIFIED → BINDING_CREATED → BINDING_READ_BACK

„Die Scanner-Bedienung öffnet die Auswahl, sie bindet nicht heimlich.“ Ohne Auswahl bleibt das Ziel, wie es war.
`PRE_ACTION_RESCAN` und `TARGET_STATE_OBSERVED` gehören zu Aktionen; der erste Körper führt keine aus.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from augen_haende_bridge.contracts import TargetScanItem
from augen_haende_bridge.harness import HarnessGraph, HarnessNode, HarnessRun, NodeKind
from augen_haende_bridge.read_only_binding import (
    BindingError,
    ReadOnlyTargetBinding,
    create_read_only_binding,
    read_back_binding,
)
from augen_haende_bridge.windows_capture import CapturedFrame, WindowsScreenCapture
from augen_haende_bridge.windows_scanner import TargetScanSnapshot, WindowsWindowScanner

from . import menue
from .terminal_fenster import TerminalFenster

ScannerCallback = Callable[[int, int], None]


@dataclass(frozen=True)
class Bindung:
    """Was nach einer gelungenen Rücklese an den Besitzer geht."""

    binding: ReadOnlyTargetBinding
    item: TargetScanItem
    frame: CapturedFrame
    snapshot: TargetScanSnapshot


def snapshot_zu_eintraegen(snapshot: TargetScanSnapshot) -> list[menue.Eintrag]:
    """Popup-Menü-Einträge aus einem Scan-Ergebnis: Befehls-Id 1..n in Scan-Reihenfolge (0 bleibt „Abbruch“)."""
    return [(index, item.label, 0) for index, item in enumerate(snapshot.items, start=1)]


def eintrag_zu_ziel(snapshot: TargetScanSnapshot, befehl_id: int) -> tuple[str, str] | None:
    """(target_id, label) der gewählten Befehls-Id, oder None bei Abbruch (0) oder ungültiger Id."""
    if befehl_id <= 0 or befehl_id > len(snapshot.items):
        return None
    item = snapshot.items[befehl_id - 1]
    return item.target_id, item.label


def neuer_scanner_lauf() -> HarnessRun:
    graph = HarnessGraph(id="fensterscanner", start_node_id="scan",
                         nodes={"scan": HarnessNode("scan", NodeKind.OBSERVATION, "Fensterscanner")}, edges=())
    lauf = HarnessRun(id=f"scan-{uuid.uuid4().hex[:12]}", graph=graph)
    lauf.start()
    return lauf


def mache_scanner_callback(terminal: TerminalFenster, *, scanner: WindowsWindowScanner,
                           capture: WindowsScreenCapture, agent_id: str = "agent",
                           menue_anzeigen: Callable[..., int] = menue.zeige_menue,
                           gebunden: Callable[[Bindung], None] = lambda bindung: None,
                           geloest: Callable[[], None] = lambda: None,
                           lauf_beendet: Callable[[HarnessRun], None] = lambda lauf: None) -> ScannerCallback:
    """Baut den `scanner_gewuenscht`-Callback eines TerminalFensters."""

    def bei_scanner_knopf(x: int, y: int) -> None:
        lauf = neuer_scanner_lauf()
        try:
            lauf.attest("SCAN_REQUESTED", detail=f"terminal={terminal.name}")
            try:
                frame = capture.capture()
            except Exception as fehler:  # kein Bild heißt kein Scan; sichtbar statt still
                terminal.setze_ziel(f"Scanner: keine Aufnahme ({fehler})", terminal.ziel_gebunden)
                return
            lauf.attest("FRAME_CAPTURED", detail=f"{frame.frame_ref} {frame.width}x{frame.height}")
            try:
                snapshot = scanner.scan(frame_ref=frame.frame_ref, frame_hash=frame.frame_hash,
                                        captured_at_ms=frame.captured_at_ms)
            except Exception as fehler:
                terminal.setze_ziel(f"Scanner: kein Inventar ({fehler})", terminal.ziel_gebunden)
                return
            lauf.attest("INVENTORY_READ", detail=f"{snapshot.scan_id} ziele={len(snapshot.items)}")
            eintraege = snapshot_zu_eintraegen(snapshot)
            loesen_id = len(eintraege) + 1
            if terminal.ziel_gebunden:  # eine Bindung lässt sich wieder lösen (R015): zurück zu „Ziel: Desktop (ungebunden)“
                eintraege = [*eintraege, None, (loesen_id, "Bindung lösen (zurück zu ungebunden)", 0)]
            wahl = menue_anzeigen(terminal.hwnd, eintraege, x, y)
            if wahl == loesen_id and terminal.ziel_gebunden:
                lauf.attest("TARGET_UNBOUND", detail=terminal.ziel_text)
                terminal.setze_ziel("Ziel: Desktop (ungebunden)", False)
                geloest()
                return
            ziel = eintrag_zu_ziel(snapshot, wahl)
            if ziel is None:
                return  # Abbruch: nichts wird gebunden, das bisherige Ziel bleibt
            target_id, label = ziel
            lauf.attest("TARGET_SELECTED", detail=target_id)
            try:
                binding = create_read_only_binding(snapshot, binding_id=f"binding-{uuid.uuid4().hex[:12]}",
                                                   agent_id=agent_id, target_id=target_id)
            except BindingError as fehler:
                terminal.setze_ziel(f"Ziel: {label} — nicht bindbar ({fehler})", False)
                return
            lauf.attest("IDENTITY_VERIFIED", detail=binding.target_generation)
            lauf.attest("BINDING_CREATED", detail=binding.binding_id)
            rueck = read_back_binding(binding, snapshot)
            if not rueck.valid:
                terminal.setze_ziel(f"Ziel: {label} — Rücklese {rueck.reason}", False)
                return
            lauf.attest("BINDING_READ_BACK", detail=rueck.reason)
            item = next(i for i in snapshot.items if i.target_id == binding.target_id)
            terminal.setze_ziel(f"Ziel: {label}", True)
            gebunden(Bindung(binding, item, frame, snapshot))
        finally:
            lauf_beendet(lauf)

    return bei_scanner_knopf
