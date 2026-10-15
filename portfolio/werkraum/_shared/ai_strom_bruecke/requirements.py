#!/usr/bin/env python3
"""Executable requirement ledger for the full AI-Strom-Brücke build."""

from __future__ import annotations

from typing import Any


_VERIFIED = {
    "FW-02", "FW-04", "FW-05", "FW-06", "FW-10", "FW-11", "FW-12", "FW-13", "FW-14", "FW-15", "FW-16",
    "FW-20", "FW-21", "FW-22", "FW-23", "FW-24", "FW-25", "FW-26", "FW-27", "FW-30", "FW-31", "FW-32",
    "FW-33", "FW-34", "FW-35", "FW-36", "FW-37", "FW-38", "FW-40", "FW-41", "FW-42", "FW-43", "FW-44",
    "FW-50", "FW-51", "FW-52", "FW-53", "FW-54", "FW-55", "FW-56", "FW-57", "FW-61", "FW-63", "FW-65", "FW-66", "FW-67", "FW-68", "FW-70",
    "FW-71", "FW-72", "FW-73", "FW-74", "FW-75", "FW-76", "FW-80", "FW-82", "FW-83", "FW-84", "FW-85",
    "FW-00", "FW-01", "FW-03", "FW-45", "FW-60", "FW-62", "FW-81", "FW-86", "FW-87", "FW-88", "FW-89",
}

_TITLES = {
    "FW-00": "alle Eingangsanforderungen rückverfolgen", "FW-01": "v1-Dateien und Endpunkte inventarisieren", "FW-02": "v2-Verträge", "FW-03": "Kompatibilität und additive Migration", "FW-04": "deterministische Fixtures", "FW-05": "Playwright-Projekt und Testserver", "FW-06": "Modellfreiheits-Gate",
    "FW-10": "Frame-Envelope und Digest", "FW-11": "gemessener 100-ms-Observer", "FW-12": "30–60-Sekunden-Frame-Ring", "FW-13": "Duplikat/Stale/Reconnect", "FW-14": "Push-/Vision-State", "FW-15": "Health/Gate/Shutdown", "FW-16": "Realtime-Testabnahme",
    "FW-20": "Earth-Statusleisten-OCR", "FW-21": "DMS/Dezimal/O-Normalisierung", "FW-22": "Pointer-vs-Center", "FW-23": "Kamera/Kalibrierung", "FW-24": "Bilddiff und Popup-Klassifikation", "FW-25": "Analyseoverlay/Fadenkreuz", "FW-26": "bestätigte Ortsanker", "FW-27": "Earth-Fehlanker-Regressionen",
    "FW-30": "Target/Fokus/Control-Lease", "FW-31": "Pointer-Zwischenpunkte/Hold", "FW-32": "linke/mittlere/rechte Gesten", "FW-33": "Rad/Zoom/Controls", "FW-34": "WASD/Pfeile/Modifier", "FW-35": "Stop/Timeout/Crash", "FW-36": "Action-Transaction", "FW-37": "sichtbares Action-Ack", "FW-38": "Release-Regressionen",
    "FW-40": "lokales Cockpit", "FW-41": "Terminal-Heartbeat", "FW-42": "SSE/Reconnect", "FW-43": "Pointer/Provenienz-Overlay", "FW-44": "Stale/Pause/Gate/Stop", "FW-45": "mehrminütige Cockpit-Abnahme",
    "FW-50": "Objektidentität/Version/Provenienz", "FW-51": "echter Web-DOM-Leib", "FW-52": "Native semantic-proxy", "FW-53": "DOM/CSS/ID/Aktion/Frische", "FW-54": "atomischer Dreileib-Builder", "FW-55": "Rot-Block", "FW-56": "Deep-Link/Share/Avatar/Counter", "FW-57": "Dreileib-Atomizität",
    "FW-60": "rrweb-Live-Spiegel/Recovery", "FW-61": "WebGL/3D-Menschenfläche", "FW-62": "Animation/Interaktion/Welt-Event", "FW-63": "Rendermetriken", "FW-64": "8K/66-FPS-Messbericht", "FW-65": "Organ-Leib Posts/Splitter", "FW-66": "Organ-Leib Gruppen/Schatten", "FW-67": "Organ-Leib KompOase/Profile/Resonanz", "FW-68": "kanonische Organ-Events",
    "FW-70": "Codewesen-Wahrnehmung/Aktion", "FW-71": "kanonische Weltänderung", "FW-72": "Menschen-Folge", "FW-73": "Organ-Folge", "FW-74": "menschliche Reaktion", "FW-75": "frische rot-gefilterte Kapsel", "FW-76": "Playwright-Dreierregen",
    "FW-80": "Unit/Contract/Integration", "FW-81": "alle Playwright-E2E", "FW-82": "Native/Earth-Härtetest", "FW-83": "100-ms-Lasttest", "FW-84": "Crash/Lease/Stop-Regressionen", "FW-85": "Modellfreiheits/Primary-Sicherheit", "FW-86": "integrierter Red-Team", "FW-87": "Red-Team-Reparaturen", "FW-88": "Matrix nach Reparatur", "FW-89": "Doku/Belegpfade/Commits", "FW-90": "Endabnahme erst vollständig grün",
}

_SECTION_BY_BAND = {
    0: "61.2–61.7 Vertrags- und Bestandssicherung",
    1: "61.6 Phase B / 61.7 Frame-Verträge",
    2: "61.6 Phase C / 61.8 OCR- und Kameratests",
    3: "61.6 Phase D–E / 61.8 Steuerungstests",
    4: "61.5–61.6 Phase F Cockpit",
    5: "61.4–61.7 Dreileib-/DOM-Verträge",
    6: "61.3–61.6 Phase I Menschen- und Organ-Leib",
    7: "61.4 / 61.6 Phase J Dreierregen",
    8: "61.8–61.10 Testplan und Endabnahme",
}


def registry() -> list[dict[str, Any]]:
    result = []
    for number in [*range(0, 7), *range(10, 17), *range(20, 28), *range(30, 39), *range(40, 46), *range(50, 58), *range(60, 69), *range(70, 77), *range(80, 91)]:
        requirement_id = f"FW-{number:02d}"
        status = "verified" if requirement_id in _VERIFIED else "open"
        band = number // 10
        result.append({
            "id": requirement_id,
            "title": _TITLES.get(requirement_id, requirement_id),
            "status": status,
            "completion_gate": "Playwright + Integrationsbeleg + Red-Team",
            "source_refs": [f"DOKUMENTATION.md §{_SECTION_BY_BAND.get(band, '61.10')}", "Daniels Bauauftrag: vollständiges Endprodukt ohne MVP"],
        })
    return result


def summary() -> dict[str, Any]:
    items = registry()
    verified = sum(item["status"] == "verified" for item in items)
    return {"schema": "ai-strom-bruecke.requirements.v1", "total": len(items), "verified": verified, "open": len(items) - verified, "end_abnahme": "blocked_until_FW-90", "items": items}
