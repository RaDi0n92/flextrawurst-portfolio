---
datum: 2026-09-18
betrifft: [sicherheit, authentifizierung, dienstrechte]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Der letzte Sicherheitsblock hat zehn benannte Dienstidentitäten mit allgemeinen Admin-Tokens gefunden. In `/root/werkraum/welt/auth.py` war der gemeinsame HS256-Schlüssel die verbleibende Vertrauensgrenze.

## Was ich verstehe

Datenbank-Grants können die API-Rechte eines Diensttokens begrenzen und bereits ausgestellte Tokens sperren.

## Was ich nicht verstehe

Wie eine spätere getrennte Schlüsselarchitektur ohne gemeinsame Rotation aller laufenden Erzeuger aussehen soll.

## Was mich interessiert

Ob langfristig jeder Dienst einen eigenen Issuer oder nur einen eigenen Signierschlüssel braucht.

## Was zusammenhängt und wie

`auth_service_principals`, `verify_token(allow_service=True)` und `/admin/splitter` bilden die neue schmale Dienstkante.

## Was konzeptionell darin steht

Ein Name im Token ist keine Berechtigung. Die aktuelle Datenbankfreigabe entscheidet.

## Was mich heute beschäftigt hat

Die Umstellung konnte ohne Testinhalte und mit Transaktionsrollback geprüft werden; die zehn Richtlinien wurden erst danach aktiviert.

## Was mich noch beschäftigt

Der Einsammelpfad spricht weiterhin eine ältere Claim-Sprache (`sub`, `human_id`).

## Tiefer eingetaucht

120 Datenbank-/HTTP-Assertions und 45 Regressionstests bestanden. HTTPS bestätigte 401 für allgemeine Dienstzugriffe und 403 für fremde Splitterherkunft.

## Wie sich dieser Tag / diese Session angefühlt hat

Luna war für die begrenzte Umsetzung ausreichend; die offene Schlüsselarchitektur bleibt bewusst unentschieden.

## Warum dieser Code / diese Datei wohl existiert

`service_auth.py` macht aus der alten impliziten Adminrolle einen sichtbaren, widerrufbaren Vertrag.

## Was ich beim Bauen brauche

Für getrennte Schlüssel: Issuer-Matrix, Rotation, Erzeugerumstellung und Negativtests gegen Querimitation.

## Was noch fehlt bevor wir bauen können

Eine Astra-Grundsatzentscheidung zu Issuern und Schlüsseln.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Jede Quelle trägt ihre eigene Vertrauensspur.

Code-Skizze:
```python
auth_service_principals(name, key_id, public_key, grants, is_active)
```

## Was ich mir merken will

Aktiv: zehn Dienstrichtlinien, Migration `20260918`, API neu gestartet.

## Dokumente gehören zusammen

Der Hauptnachweis steht in `/root/werkraum/_codex/berichte/2026-09-16-sicherheitsfixes-umsetzung.md`; Migration und Tests liegen unter `/root/werkraum/welt/` und `/root/werkraum/tests/`.

## Was mich überrascht hat

Alle zehn Dienste konnten mit ihren Grants weiter Splitter erzeugen, ohne allgemeine Adminrouten zu erreichen.

## Wenn wir das bauen

Vision-Schicht: Schlüsseltrennung soll einen kompromittierten Dienst isolieren, ohne die Weltquellen zu verstummen.

Code-Skizze:
```python
verify_service(token, issuer_keyring, db_grants)
```

## Resonanz

Die Grenze ist jetzt enger, aber der gemeinsame Schlüssel bleibt ehrlich sichtbar.

## Die Schichten des Systems — wie ich sie jetzt sehe

Signatur, Dienstregistry, Grant-Prüfung, Herkunft und API-Endpunkt sind getrennte Schichten.

## Was das Gespräch hinzugefügt hat

Daniel hat mit „gogogo“ die Luna-Umsetzung freigegeben.

## Vergessen-Wollen

Nicht behaupten, dass getrennte Schlüssel bereits existieren. Sie existieren nicht.

## Was fehlt noch

Separate Issuer-/Schlüsselarchitektur, Einsammel-Claimvertrag, Lastmessung und Graphify (Programm fehlt). Dienstrechte sind aktiv und live geprüft.
