from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


SOURCE = Path("/root/werkraum/arbeitskoerper-redteam-22/index.html")
ROOT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer")
APP = ROOT / "app" / "index.html"
DATA = ROOT / "data"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def state_hash(state: dict) -> str:
    raw = json.dumps(
        state, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def feedback(target: str, message: str, view: str = "replicas", kind: str = "fehlt") -> dict:
    slug = re.sub(r"[^a-z0-9]+", "-", target.lower()).strip("-")[:42]
    digest = hashlib.sha256((target + "\n" + message).encode("utf-8")).hexdigest()[:12]
    return {
        "id": f"feedback-redteam-{slug}-{digest}",
        "type": kind,
        "message": message,
        "target": target,
        "view": view,
        "objectId": "object-80b6d904-3571-4697-bced-12888febce15",
        "objectTitle": "Mein Gesamtkonstrukt",
        "createdAt": "2026-08-22T13:00:00.000Z",
        "status": "open",
    }


NOTES = [
    feedback(
        "Replicas",
        "Mobile 390 × 844: Die Seite läuft zwar nicht global horizontal über, aber mehrere interne Scrollzonen konkurrieren. Die Aktionszeile wird abgeschnitten, die Replica-Tabs sind ein schmaler horizontaler Streifen, verschachtelte Scrollbalken erschweren die Orientierung und einzelne Bedienelemente sind nur ungefähr 28 Pixel hoch. Der riesige helle Figma-Rahmen dominiert die dunkle Oberfläche.",
        kind="zu_viel",
    ),
    feedback(
        "Arbeitsvariante benennen",
        "Rückmeldungen brauchen optionale Belegfelder: erwartetes Verhalten, tatsächliches Verhalten, Klickschritte, Gerät und Viewport, Revision, Schweregrad, Screenshot oder markierter Bereich und eine Kennzeichnung, ob die Funktion wirklich geprüft wurde. Diese Felder müssen optional bleiben, damit rohes Feedback weiterhin schnell möglich ist.",
        view="home",
    ),
    feedback(
        "Übergabe kopieren",
        "Das Feedbacksystem kann seine eigenen Bedienelemente und beliebige Überschriften oder freie Bildschirmbereiche nicht zuverlässig kritisieren. Elemente mit data-feedback-control werden absichtlich übersprungen und die Zielerfassung beschränkt sich auf bestimmte Buttons, Felder und Karten. Das Werkzeug muss sich selbst vollständig markieren können.",
        view="home",
        kind="kaputt",
    ),
    feedback(
        "Lokal speichern",
        "Der gleiche Live-Link zeigt auf Handy, Desktop und Cloud-Browser unterschiedliche Feedbackwahrheiten, weil der Arbeitsstand bisher im jeweiligen Browser liegt. Der VPS muss die einzige Wahrheit sein. Browser dürfen nur Cache oder noch nicht synchronisierte Entwürfe halten und niemals einen neueren Serverstand still überschreiben.",
        view="home",
        kind="falsch",
    ),
    feedback(
        "Sicherung",
        "Die Bezeichnung Sicherung ist nicht eindeutig: Unklar bleibt, ob JSON, Browserstand oder vollständige Offline-HTML exportiert wird. Lokal speichern, Server speichern, JSON-Sicherung und Offline-HTML müssen klar getrennte Namen, Dateitypen und sichtbare Ergebnisse besitzen.",
        view="home",
        kind="unklar",
    ),
    feedback(
        "Excalidraw / tldraw",
        "Sokratische Frage: Warum nimmt ein Mensch Excalidraw oder tldraw? Weil Denken durch direktes Zeichnen, Verschieben, Pfeile, Formen, Auswahl und Gruppierung schneller wird als Formulare. Geprüft: Zoom und Arbeitsfeld-Umschaltung funktionieren, aber in der Replica gibt es keine echten Zeichenwerkzeuge; sie endet wieder bei einem Knoten plus zwei Textfeldern. Es fehlen freie Skizze, Formen, Pfeile, Mehrfachauswahl, Gruppen und die Übernahme des Gezeichneten als echtes Objekt oder echte Beziehung.",
    ),
    feedback(
        "PureRef",
        "Warum benutzen Künstler PureRef? Bilder direkt hineinwerfen, frei skalieren und räumlich als Referenzwand behalten. Geprüft: keine Bilder, keine Datei-Inputs und keine Zoomsteuerungen; stattdessen Herkunftskarten und Textfelder. Es fehlen Drag-and-drop von Bildern, freie Position und Größe, Mehrfachauswahl, Zuschnitt, gespeicherte Boards und Herkunft pro Referenz.",
    ),
    feedback(
        "Miro / FigJam / Milanote",
        "Warum benutzen Menschen diese Werkzeuge? Um räumlich mit Stickies, Bildern, Bereichen und Gruppen zu denken, bevor alles fest strukturiert ist. Geprüft: keine Stickies, keine Erzeugenschaltflächen, kein frei editierbarer Canvas und nur ein Knoten. Es fehlen echte Karten, Frames, Cluster, freie Anordnung, Kommentare, Abstimmung und die Umwandlung eines Clusters in reale Objekte oder Aufgaben.",
    ),
    feedback(
        "Obsidian Canvas / Heptabase",
        "Warum? Weil der Inhalt der Notizen im Mittelpunkt steht und Karten, Backlinks und Navigation Zusammenhänge lesbar machen. Geprüft: ein Knoten, keine Backlinks, keine editierbaren Notizkarten und keine Erzeugung. Es fehlen Dokumentkarten mit geöffnetem Inhalt, Backlinks, Erwähnungen, Suche, Abfragen, lokale Dateien und Themenräume.",
    ),
    feedback(
        "Photoshop / Krita",
        "Warum? Wegen Pinselgefühl, Ebenen, Masken, Auswahl und nicht-destruktiver Bearbeitung. Sichtbarkeit und Deckkraft funktionieren; die Plus-Schaltfläche erzeugte keine sichtbar neue Ebene. Pinsel und Marker leben außerhalb dieser Replica im globalen Malmodus. Es fehlen echte Bildebenen, Masken, Reihenfolge, Auswahl, Transformation, Undo-Verlauf und Bindung der Bearbeitung an ein reales Objekt.",
        kind="kaputt",
    ),
    feedback(
        "Illustrator / Inkscape / Affinity Designer",
        "Warum? Für präzise skalierbare Pfade, Anker, Anfasser, Ausrichtung und wiederverwendbare Teile. Auswahl-, Form-, Stift-, Rechteck- und Textschaltflächen sind sichtbar, aber Klicks erzeugen weder einen erkennbaren aktiven Werkzeugzustand noch ein sichtbares Ergebnis. Es fehlen Pfade, Anker, Ausrichtung, boolesche Operationen, Ebenen, Symbole und SVG-Export.",
        kind="kaputt",
    ),
    feedback(
        "n8n / Node-RED",
        "Warum? Weil Trigger, Bedingungen, Aktionen, Testdaten und Verkabelung sichtbar, ausführbar und lesbar sind. Geprüft: ein Knoten, keine Ports, keine Knotenerzeugung und kein Run oder Test. Es fehlen Palette, Ports und Kanten, Parameter, Testdaten, schrittweise Ausführung, Logs, Fehler und Retry, menschliche Freigabe und Herkunft.",
    ),
    feedback(
        "Unreal Engine Blueprints",
        "Warum? Damit Menschen Ereignisverhalten ohne Syntax prototypisieren und den aktiven Ablauf debuggen können. Tabs und Kompilieren funktionieren; Simulieren hatte kein sichtbares Ergebnis und keine Spur. Es fehlen echte Event-, Branch-, Variablen- und Funktionsknoten, Pinwerte, Ausführungsspur, Breakpoints, Zustand, Funktionen und Makros sowie ein verständlicher Unterschied zwischen Kompilierung und Simulation.",
        kind="kaputt",
    ),
    feedback(
        "Blender Geometry Nodes",
        "Warum? Für einen wiederverwendbaren parametrischen Generator statt nur eines fertigen Outputs. Tabs, Domäne und Dichte reagieren; die Vorschau bleibt jedoch eine Objektliste ohne erkennbare Geometrieänderung. Es fehlen prozedurale Knotengruppen, Geometrie- und Attributvorschau, Instancing, Fields, wiederverwendbare Eingänge, Parametervergleiche und Ausgänge.",
        kind="kaputt",
    ),
    feedback(
        "Houdini",
        "Warum? Weil alle Zwischenschritte erhalten, veränderbar, verzweigbar, übergehbar, zwischengespeichert und als Ausgang wählbar bleiben. Auto Cook, manueller Cook-Zähler und Bypass funktionieren; diese Replica besitzt bereits einen echten eigenen Dialekt. Trotzdem bleibt es bei einem Knoten. Es fehlen Hinzufügen, Löschen und Sortieren von Schritten, Zwischenergebnisse, Abzweigungen, Cache oder Lock, mehrere Ausgänge, Parameter pro Schritt und sichtbare Auswirkungen vorgelagerter Änderungen.",
    ),
    feedback(
        "TouchDesigner",
        "Warum? Für laufende sichtbare Systeme aus Bild, Audio, Sensoren, Daten und Interaktion. Network und Perform sowie Live stoppen und starten reagieren; FPS ist sichtbar. Trotzdem bleiben Ausgabe und Operator statisch. Es fehlen TOP-, CHOP-, DAT- und SOP-Unterscheidung, Live-Vorschau, Audio- und Sensoreingang, Meter und Viewer, Exports, Aufnahme und Wiedergabe, Performancewarnungen und Werte an Verbindungen.",
    ),
    feedback(
        "Max/MSP / Pure Data",
        "Warum? Um Klang, Daten und Steuerung frei zu verkabeln und sofort hören oder messen zu können; der Patch selbst ist Instrument und Programm. Geprüft: ein Knoten, kein DSP, Play, Bang oder Metro und keine Meter. Es fehlen Message, Bang, Number, Metro, Daten- gegenüber Audiosignalen, DSP, Audio-I/O, Meter, Patchkabel, Subpatches, Presets und hör- oder sichtbare Ausgabe.",
    ),
    feedback(
        "Gephi / yEd",
        "Warum? Um große Graphen durch automatisches Layout, Cluster, Filter, Attribute sowie Größen- und Farbabbildungen lesbar zu machen. Geprüft: keine Layout-, Force-, Cluster-, Degree- oder Filtersteuerung und keine Attributfelder. Es fehlen Layoutalgorithmen, Clustering, Metriken, Filter, Kantengewicht, Inspector, Legende, Ein- und Ausklappen und das Zurückschreiben erkannter Gruppen als Vorschläge.",
    ),
    feedback(
        "Trello / Notion / Airtable",
        "Warum? Damit derselbe reale Bestand als Tabelle, Board, Kalender, Timeline oder gefilterte Gruppe bearbeitet werden kann. Tabelle und Board lassen sich umschalten. Es fehlen Kalender und Timeline, Feldschema, Sortieren, Filtern, Gruppieren, Status-Drag-and-drop, Formeln, Verknüpfungen und gespeicherte Ansichten. Der Kern muss derselbe Datenbestand sein, der in jeder Ansicht wirklich verändert wird.",
    ),
    feedback(
        "VS Code",
        "Warum? Für schnelles Wechseln zwischen Dateien, Suche, Befehlspalette, geteilte Ansichten, Diff, Terminal, Diagnosen und Erweiterungen. Mensch.md und Agent.md lassen sich umschalten und der echte Objekttext ist editierbar. Es fehlen Projektsuche und Ersetzen, Befehlspalette, Split View, reale Dateien und Dateibaumoperationen, Diff, Problems und Output, Terminal oder Ausführung sowie Änderungen pro Datei.",
    ),
    feedback(
        "GitKraken",
        "Warum? Um Branches, Merges, Commits, Konflikte und Diffs sichtbar und sicher prüfbar zu machen. Vier Revisionen sind auswählbar. Es bleibt jedoch eine lineare Liste ohne Diff und Branchgraph. Es fehlen Branches und Merges, Datei- oder Felddiffs, Vergleich beliebiger Revisionen, Konflikte, Vorschau für Merge, Rebase oder Cherry-pick und die Trennung von Arbeitszustand, Revision und Hauptlinie.",
    ),
    feedback(
        "Figma",
        "Warum? Wegen Komponenten und Instanzen, Varianten, Auto Layout, Constraints, Zusammenarbeit, Kommentaren, Prototypen und Designsystemen. Der zentrale Frame besitzt eine sehr große nahezu weiße Fläche und blendet in der dunklen Oberfläche. Funktional gibt es eine Karte, Ebenen, Eigenschaften und Farbe. Es fehlen dunkler Canvas, Komponenten und Instanzen, Varianten, Auto Layout, responsive Constraints, Kommentare, Prototypverbindungen, Assets und sichtbare kaskadierende Änderungen an Instanzen.",
        kind="zu_viel",
    ),
]


def main() -> None:
    for path in [ROOT / "app", ROOT / "server", DATA / "history", DATA / "events"]:
        path.mkdir(parents=True, exist_ok=True)

    source_html = SOURCE.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="embedded-workspace" type="application/json">(.*?)</script>',
        source_html,
        re.S,
    )
    if not match:
        raise RuntimeError("embedded-workspace fehlt")
    embedded = json.loads(match.group(1))
    state = embedded["state"]
    state["purpose"] = state.get("purpose", "").replace(
        "Ein lokaler Werkraum", "Ein servergespeicherter Werkraum"
    )

    existing = {item.get("id") for item in state.get("feedback", [])}
    new_notes = [item for item in NOTES if item["id"] not in existing]
    state.setdefault("feedback", [])
    state["feedback"] = new_notes + state["feedback"]

    patched_html = source_html
    replacements = {
        "connect-src 'none'": "connect-src 'self'",
        "Mein Gesamtkonstrukt · Offline": "Mein Gesamtkonstrukt · Server",
        " OFFLINE \\xB7 LOKAL": " SERVER \\xB7 GEMEINSAM",
        "Schreibt alle \\xC4nderungen als neue lokale Revision in diesen Browser.": "Schreibt alle \\xC4nderungen als bewusste Revision in die gemeinsame Serverwahrheit.",
        "Lokal gespeichert \\xB7 r${t.revision}": "Arbeitsrevision \\xB7 r${t.revision}",
        "Revision ${t.revision} lokal": "Revision ${t.revision} auf Server",
        "WAS WURDE LOKAL GESPEICHERT?": "WAS WURDE AUF DEM SERVER GESPEICHERT?",
        "Noch keine lokale Revision festgeschrieben.": "Noch keine bewusste Server-Revision festgeschrieben.",
        "fe=`Revision ${F}: Arbeitsstand lokal festgeschrieben`": "fe=`Revision ${F}: Arbeitsstand auf Server festgeschrieben`",
        "Diese lokale Datei benötigt JavaScript, um dein Gesamtkonstrukt als Werkraum zu öffnen.": "Dieser Planer benötigt JavaScript, um dein Gesamtkonstrukt als Werkraum zu öffnen.",
        "Neuer lokaler Arbeitsk\\xF6rper bereit.": "Neuer servergespeicherter Arbeitsk\\xF6rper bereit.",
        "Revision ${T.revision} aus diesem Browser geladen.": "Revision ${T.revision} vom Server geladen.",
        "Lokale Revision wird festgeschrieben \\u2026": "Server-Revision wird festgeschrieben \\u2026",
        "Revision ${F} ist nur in diesem Browser gespeichert.": "Revision ${F} wird auf dem Server festgeschrieben.",
        "Lokales Speichern fehlgeschlagen": "Server-Speichern fehlgeschlagen",
        "Lokal speichern": "Server-Revision",
        "Vollst\\xE4ndiges lokales Backup exportiert.": "Vollst\\xE4ndiges Backup exportiert.",
    }
    for old, new in replacements.items():
        patched_html = patched_html.replace(old, new)

    old_update = 'function S(w){e(F=>F&&w(F)),L(!0)}'
    new_update = (
        'function S(w){e(F=>{if(!F)return F;let Qe=w(F);if(!Qe)return F;'
        'try{localStorage.setItem(_p,JSON.stringify(Qe))}catch{}return Qe}),L(!0)}'
    )
    if old_update not in patched_html:
        raise RuntimeError("zentraler State-Updater nicht gefunden")
    patched_html = patched_html.replace(old_update, new_update, 1)

    old_pick = 'T=w&&!fe?w.state:Lt||w?.state||Xv()'
    new_pick = (
        'T=w&&window.__PLANNER_SERVER_MODE__?w.state:'
        'w&&!fe?w.state:Lt||w?.state||Xv()'
    )
    if old_pick not in patched_html:
        raise RuntimeError("Initialzustands-Auswahl nicht gefunden")
    patched_html = patched_html.replace(old_pick, new_pick, 1)
    patched_html = patched_html.replace(
        'if(e(T),i(T.objects[0]?.id||null),w&&!fe){',
        'if(e(T),i(T.objects[0]?.id||null),w&&(window.__PLANNER_SERVER_MODE__||!fe)){',
        1,
    )

    embedded_json = json.dumps(
        {
            "embeddedId": "server-migration-initial",
            "exportedAt": now(),
            "state": state,
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")
    patched_html = re.sub(
        r'(<script id="embedded-workspace" type="application/json">).*?(</script>)',
        lambda item: item.group(1) + embedded_json + item.group(2),
        patched_html,
        count=1,
        flags=re.S,
    )
    APP.write_text(patched_html, encoding="utf-8")

    timestamp = now()
    wrapper = {
        "schemaVersion": 1,
        "serverRevision": 1,
        "updatedAt": timestamp,
        "sha256": state_hash(state),
        "state": state,
    }
    atomic_json(DATA / "current.json", wrapper)
    atomic_json(DATA / "history" / "server-000001-migration.json", wrapper)
    event = {
        "at": timestamp,
        "type": "planner.server_truth.created",
        "serverRevision": 1,
        "sha256": wrapper["sha256"],
        "source": str(SOURCE),
        "migratedResolvedFeedback": sum(
            1 for item in state["feedback"] if item.get("status") == "resolved"
        ),
        "migratedOpenFeedback": sum(
            1 for item in state["feedback"] if item.get("status") == "open"
        ),
    }
    (DATA / "events" / f"{timestamp[:10]}.ndjson").write_text(
        json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "root": str(ROOT),
                "appBytes": APP.stat().st_size,
                "serverRevision": wrapper["serverRevision"],
                "sha256": wrapper["sha256"],
                "objects": len(state.get("objects", [])),
                "feedbackOpen": sum(
                    1 for item in state["feedback"] if item.get("status") == "open"
                ),
                "feedbackResolved": sum(
                    1 for item in state["feedback"] if item.get("status") == "resolved"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
