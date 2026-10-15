# Rotationsplan für getrennte Dienstschlüssel

Status am 2026-09-18: umgesetzt und live. Aktueller Nachweis: /root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md.

Der folgende Plan bleibt als historische Entscheidungsspur erhalten. Seine Aussagen „noch nicht verfügbar“ und „noch nicht aktiviert“ sind überholt. Ed25519 ist jetzt produktiv verfügbar; separate Dienstschlüssel begrenzen den Verlust eines einzelnen Schlüssels. Unix-/Systemd-Isolation bleibt als zusätzliche Grenze gegen kompromittierte Root-Prozesse offen und wurde nicht als bereits umgesetzt behauptet. Die tatsächliche Registry nutzt eine eigene Tabelle auth_service_keys statt einzelner Previous-Key-Felder am Dienst.

## Ziel

Benannte interne Dienste sollen eigene Signieridentitäten besitzen. Ein kompromittierter Dienst darf damit weder einen anderen Dienst imitieren noch Menschen-, Wesen- oder Admin-Tokens ausstellen.

Die menschlichen und Wesen-Tokens bleiben zunächst im bestehenden HS256-Vertrag. Die Änderung betrifft nur Tokens mit `role=service`.

## Warum die Umstellung jetzt nicht blind aktiviert wird

Auf dem laufenden Host ist `cryptography` in `/root/werkraum/venv/bin/python3` nicht installiert. Die zehn Erzeuger laufen außerdem aus unterschiedlichen Skripten, aber mit demselben Importpfad und ohne nachgewiesene, voneinander getrennte Secret-Umgebungen. Ein gemeinsames neues Secret in `/root/werkraum/welt/.service_keys/` wäre keine echte Dienstisolation.

Die Prüfung der tatsächlichen Units bestätigt die Grenze: `welt-api.service`, `splitter-physik.service`, `wesenvaultsystem.service`, `codewesen-chat.service`, `claude-live.service`, `gemini-live.service` und die relevanten Welt-/Futterprozesse laufen als `root`; die AI-Live-Units haben ebenfalls keinen getrennten Benutzer. Ein eigener Schlüssel pro Dienst ohne vorherige Unix-/Systemd-Isolation würde deshalb bei einer Root-Kompromittierung keine wirksame Trennung schaffen.

## Zielvertrag

1. Jeder Dienst erhält einen eigenen Schlüssel und eine eigene `kid`.
2. Die API hält nur die öffentlichen Schlüssel, wenn Ed25519 verfügbar ist.
3. Diensttokens tragen `iss=flextrawurst-service`, `sub=<dienstname>`, `kid=<key-id>`, `role=service`, `aud=flextrawurst-api`, `iat`, `exp` und `jti`.
4. Die API prüft Signatur, `iss`, `aud`, Zeitfenster, `kid`, `is_active` und die bestehenden DB-Grants.
5. Rotation bedeutet: neuen Schlüssel ausrollen, neuen `kid` aktivieren, alten `kid` für eine kurze Übergangsfrist akzeptieren, danach deaktivieren. Kein Dienst wird durch eine Migration automatisch reaktiviert.
6. Kein Diensttoken darf in einem allgemeinen `verify_token()`-Aufrufer akzeptiert werden. Nur der eng begrenzte Splitter-Erzeuger ruft die Serviceprüfung auf.

## Erzeuger und vorgesehene `kid`s

| Dienst | Erzeuger | erlaubte Rolle |
|---|---|---|
| `weltfutter` | `/root/werkraum/welt/weltfutter.py` | `splitter:create` / `welt_extern` |
| `wesen-vault-sampler` | `/root/werkraum/welt/wesen_vault_splitter.py` | `splitter:create` / `wesen_vault` |
| `flarum-archiv-sampler` | `/root/werkraum/welt/flarum_archiv_splitter.py` | `splitter:create` / `flarum_archiv` |
| `codex-abwurf` | `/root/werkraum/_codex/tools/` | `splitter:create` / `codex_*` |
| `claude-abwurf` | `/root/werkraum/_claude/tools/` | `splitter:create` / `claude_*` |
| `kimi-abwurf` | `/root/werkraum/_kimi/tools/` | `splitter:create` / `kimi_*` |
| `gemini-abwurf` | `/root/werkraum/_gemini/tools/` | `splitter:create` / `gemini_*` |
| `dak-abwurf` | `/root/werkraum/_shared/tools/dak_abwurf.py` | `splitter:create` / `dak_abwurf` |
| `dakgord-abwurf` | `/root/werkraum/web_chat.py` | `splitter:create` / `dakgord_abwurf` |
| `system-abwurf` | `/root/werkraum/codewesen_abwurf.py` | `splitter:create` / `innerer_abwurf` |

## Aktivierungsreihenfolge

0. Vorbedingung: eigene Unix-/Systemd-Benutzer für API, Weltprozesse und jeden dauerhaft laufenden Dienst festlegen; nur die jeweils benötigten Dateien, Socketrechte und DB-Rechte freigeben. Dieser Schritt ist noch nicht aktiviert.
1. Installieren und prüfen: Ed25519-Unterstützung in genau der Produktionsumgebung; keine globale Pip-Installation.
2. `auth_service_principals` um `kid`, `public_key`, `previous_kid`, `rotated_at` und `expires_at` erweitern.
3. Für jeden Dienst einen privaten Schlüssel außerhalb des Repositorys erzeugen. Dateirechte und Besitzer aus der isolierten Systemd-Unit ableiten; keine privaten Schlüssel in Logs, Git oder Datenbankausgaben.
4. Nur die öffentlichen Schlüssel und `kid`s transaktional in PostgreSQL eintragen. Bestehende Grant-Policies bleiben unverändert.
5. `create_service_token(name)` implementieren; `create_token()` für Menschen und Wesen bleibt unverändert.
6. Alle zehn Erzeuger auf `create_service_token()` umstellen.
7. Isoliert testen: Querimitation, falsche Audience/Issuer, falsche `kid`, abgelaufener Token, deaktivierter `kid`, deaktivierter Dienst, Grant-Überschreitung, allgemeine Adminroute und Einsammeln.
8. Einen Dienst nach dem anderen live testen, danach erst die alten HS256-Diensttokens zurückweisen.
9. API kontrolliert neu starten und HTTPS-Negativmatrix ausführen.
10. Alte gemeinsame Dienstschlüssel widerrufen und die Rotation als internes Event protokollieren.

## Abnahmebedingungen

- Kein Diensttoken erreicht `/admin/users`, `/me`, `/admin/auth/services` oder den Einsammelpfad.
- Jeder Dienst kann nur seine bisherige Splitter-Herkunft schreiben.
- Der private Schlüssel eines Dienstes kann keinen anderen `sub`-Wert signieren, der von der API akzeptiert wird.
- Deaktivierung eines `kid` wirkt auf bereits ausgestellte Tokens.
- Ein Rollback lässt die menschlichen und Wesen-Tokens unverändert.
- Kein privater Schlüssel erscheint in Git, PostgreSQL-Resultaten, Journal oder Testausgabe.

## Offener Architekturentscheid

Ed25519 ist vorgesehen, aber noch nicht verfügbar. Falls die Produktionsumgebung diese Bibliothek nicht erhalten darf, braucht die Alternative (HMAC mit getrennten, prozessspezifischen Umgebungsgeheimnissen) eine ausdrückliche Risikofreigabe: Sie bietet keine Public-Key-Trennung und ist nur dann sinnvoll, wenn die Dienstprozesse tatsächlich getrennte Unix-/Systemd-Identitäten besitzen.
