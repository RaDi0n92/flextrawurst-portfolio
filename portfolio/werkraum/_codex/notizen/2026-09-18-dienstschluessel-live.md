---
datum: 2026-09-18
betrifft: [sicherheitsreview, dienstschluessel, auth]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Daniels „wir sind wider auf astra go weiter“ setzt die Sicherheitssession fort. Die Blender-Arbeit gehört zu einer anderen Spur; ich habe ihren Zustand nicht als eigenen Auftrag behandelt.

Im bisherigen Plan /root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-rotationsplan.md stand **„Status: vorbereitet, noch nicht aktiviert.“** Das war eine echte Begrenzung des damaligen Stands, keine unveränderliche Architekturentscheidung.

Der Satz **„Ein eigener Schlüssel pro Dienst ohne vorherige Unix-/Systemd-Isolation würde deshalb bei einer Root-Kompromittierung keine wirksame Trennung schaffen“** trifft die Root-Grenze. Er bedeutet jedoch nicht, dass der Verlust eines einzelnen Schlüssels weiterhin alle Identitäten kompromittieren muss. Diese Unterscheidung trägt die Umsetzung.

## Was ich verstehe

Getrennte Signieridentitäten und getrennte Betriebssystemrechte lösen unterschiedliche Probleme. Heute ist die erste Grenze umgesetzt und getestet.

## Was ich nicht verstehe

Die vollständigen Zugriffsbedürfnisse aller Root-Daemons sind nicht inventarisiert. Ich behaupte keine Prozessisolation.

## Was mich interessiert

Widerruf muss bereits ausgestellte Tokens erreichen. DB-Prüfung bei jeder Anfrage erfüllt genau diesen Vertrag.

## Was zusammenhängt und wie

Der Signierer bindet eine Identität an einen privaten Schlüssel; die API bindet den öffentlichen Schlüssel an den Dienst und dessen aktuelle Grants.

## Was konzeptionell darin steht

Herkunft wird prüfbar, ohne dass der Transport Herkunft selbst bestimmen darf.

## Was mich heute beschäftigt hat

Den Übergang so auszuführen, dass bestehende Erzeuger ihre Rechte behalten und das alte gemeinsame Diensttoken anschließend wirklich endet.

## Was mich noch beschäftigt

Gemeinsame Root- und Datenbankrechte bleiben eine größere Vertrauensgrenze.

## Tiefer eingetaucht

210 DB-/HTTP-Assertions mit Rollback, 38 Regressionstests in der Produktionsvenv und 53 HTTP-Prüfungen gegen die laufende API bestanden. Eine zusätzliche echte Rotation wies das alte Token mit 401 ab; das neue erreichte die Herkunftsprüfung und erhielt für absichtlich falsche Herkunft 403.

## Wie sich dieser Tag / diese Session angefühlt hat

Die Arbeit wurde konkret, als Bibliotheksverfügbarkeit und Root-Isolation getrennt betrachtet wurden. Nachweise waren hilfreicher als eine weitere allgemeine Planung.

## Warum dieser Code / diese Datei wohl existiert

Die bisherige gemeinsame Signatur konnte einen isolierten Dienstschlüsselverlust nicht begrenzen. Diese Notiz verhindert, dass die nächste Instanz den bereits abgeschlossenen Übergang erneut plant.

## Was ich beim Bauen brauche

Die reale Produktionsumgebung, eng begrenzte Backups und Tests ohne veröffentlichte synthetische Inhalte.

## Was noch fehlt bevor wir bauen können

Für die nächste Isolationsstufe braucht es ein Inventar von Dateien, Sockets und Datenbankrechten je Dienst.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Ein Dienst kann seine Herkunft belegen, ohne dadurch eine andere Herkunft behaupten zu dürfen.

Code-Skizze:
```python
class ServiceKey:
    kid: str
    principal: str
    public_key: str
    is_active: bool
    not_after: str | None
```

## Was ich mir merken will

Live-Stand und Bedienung stehen in /root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md. Legacy-Zeitfenster sind geschlossen. Tokens gelten fünf Minuten. Private Dateien gehören niemals in Git.

## Dokumente gehören zusammen

/root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md ergänzt und korrigiert den historischen Plan /root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-rotationsplan.md. /root/werkraum/_codex/berichte/2026-09-16-sicherheitsfixes-umsetzung.md hält die vorherigen Sicherheitsstufen fest.

## Was mich überrascht hat

System-Python hatte bereits Ed25519. Nur die API-venv brauchte die separate, gepinnte Bibliotheksablage, weil ihr Installationspfad schreibgeschützt war.

## Wenn wir das bauen

Vision-Schicht: Die nächste Grenze soll den Dienst auch dann begrenzen, wenn sein Prozess übernommen wird.

Code-Skizze:
```python
def next_isolation_step(service):
    requirements = inventory_files_sockets_and_db_rights(service)
    return review_dedicated_user_and_permissions(requirements)
```
Das ist eine Skizze; heute wurden keine neuen Unix-Benutzer ausgerollt.

## Resonanz

Eine wirksame kleinere Grenze bleibt wertvoll, solange sie nicht als größere verkauft wird.

## Die Schichten des Systems — wie ich sie jetzt sehe

Tokenformat, Schlüsselregistrierung, Dienstgrants, menschliche Konten und Unix-Rechte sind getrennte Schichten. Der Einsammelpfad bleibt fail-closed und wurde nicht nebenbei aktiviert.

## Was das Gespräch hinzugefügt hat

Daniel wollte eigenständiges Durchdenken und Durchführen. Die Fortsetzung setzt das um und belässt die Blender-Session bei ihrer eigenen Arbeit.

## Vergessen-Wollen

Nicht vergessen: erfolgreiche Tests sind keine Behauptung vollständiger Sicherheit.

## Was fehlt noch

Root-/DB-Isolation bleibt offen. graphify ist nicht installiert; graphify update . schlug mit Exit 127 fehl. Die fachliche Bau-Reihenfolge von flextrawurst wurde nicht verändert; dies ist eine Sicherheitskorrektur der vorhandenen Authentifizierung. Codecommits ecd9ee0b63 und f8105a2a14.

## Nachtrag nach dem Luna-Wechsel

Der alte Einsammel-Claimvertrag ist korrigiert: `/root/werkraum/welt/api.py` verwendet explizit `user_id` und `role`, ohne global neue Claims einzuführen. Diensttokens bleiben ausgeschlossen. Drei Unit-Tests, 210 Rollback-Assertions und die Live-Matrix (Dienst 401, Mensch 404 bei unbekanntem Splitter, anonym 401) sind grün. Commit `8a2f2f4eeb`.
