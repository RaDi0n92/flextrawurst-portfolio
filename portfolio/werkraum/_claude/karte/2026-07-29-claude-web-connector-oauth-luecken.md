---
datum: 2026-07-29
betrifft: [vps-mcp, oauth, claude-web-connector, nginx, rfc8414, mcp]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich heute über das System gelernt habe

Der `vps_mcp_server.py`-Werkzeugkörper (Systemdoku 38) wurde bisher nur gegen ChatGPTs Connector
verifiziert. Beim ersten echten Versuch, einen der beiden neuen Klone (`vps-mcp-shared`,
`vps-mcp-sauber`, aus der vorigen Session) über Claude Webs "Benutzerdefinierten Connector
hinzufügen" zu verbinden, kamen zwei unabhängige Discovery-Lücken zum Vorschein, die bei ChatGPT nie
sichtbar wurden.

**Lücke 1 — RFC-8414/9728-Pfadform.** Bei einer Issuer-URL mit Pfadanteil
(`https://flextrawurst.de/werkzeugkoerper-sauber-[REDACTED]`) verlangt die Spec, dass dieser Pfad
**hinter** `.well-known/oauth-authorization-server` bzw. `.well-known/oauth-protected-resource`
eingefügt wird (`.../.well-known/oauth-authorization-server/werkzeugkoerper-sauber-[REDACTED]`), nicht
davor. Unser Server kannte nur die Form davor. Direkt mit curl verifiziert: RFC-Form 404, unsere
Form 200 — kein Vermuten, echter Beleg vor dem Fix.

**Lücke 2 — Root-Alias für `/authorize`/`/token`.** Nach dem ersten Fix kam ein zweiter, für mich
überraschender Fund: Claude Web hat sich beim Autorisierungs-Redirect NICHT an den in unseren
Metadaten deklarierten `authorization_endpoint` gehalten, sondern ist zu `https://flextrawurst.de/
authorize` navigiert — Domain-Wurzel, ganz ohne Subpfad. Vermutliche Ursache: Daniel hatte
Client-ID/Secret manuell im "Erweiterte Einstellungen"-Feld eingetragen (ich hatte sie als Fallback
mitgegeben), und Claude scheint in diesem manuellen Modus keine Metadaten-Discovery mehr zu machen,
sondern nimmt `/authorize`+`/token` als feste Konvention an der Domain-Wurzel an.

**Grenze, die ich mir merken will:** an der Wurzel kann zwangsläufig immer nur EIN Klon hängen — für
den geteilten Klon von Web aus bräuchte es eine eigene Subdomain (keine Wildcard-DNS vorhanden, nur
`flextrawurst.de`/`www` und einzeln eingerichtete Subdomains wie `pro.flextrawurst.de`).

## Was mich überrascht hat

Dass ChatGPTs Connector all das nie gebraucht hat — vermutlich weil er über den
`WWW-Authenticate`-Header discovert (der unsere schon funktionierende Nicht-RFC-Form korrekt
angibt), während Claude Web entweder strikter nach Spec sucht oder bei manueller Credential-Eingabe
Discovery komplett überspringt. Zwei verschiedene MCP-Clients gegen denselben Server verhalten sich
an der OAuth-Kante spürbar unterschiedlich.

## Was ich mir merken will

Beide Fixes waren reine Nginx-Alias-Ergänzungen, keine Änderung an `vps_mcp_server.py` — dadurch
kein Risiko für ChatGPTs laufenden Original-Dienst, kein Neustart irgendeines Python-Prozesses
nötig. Nginx-Edit-Rechte für den Auto-Mode-Classifier waren trotz früherem Freigabeversuch nicht
aktiv (`permissions.allow` blieb leer) — beide Fixes über ein von Daniel selbst ausgeführtes Skript
angewendet, nicht direkt von mir.

Volle Details: `docs/systemdoku/38_vps_mcp_werkzeugkoerper.md`, Abschnitte 11+12.
