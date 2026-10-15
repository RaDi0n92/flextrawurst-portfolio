#!/usr/bin/env python3
"""
Regressionstest fuer die drei Chat-Nginx-Locations (codewesen-chat, geni,
dakgord-chat): proxy_read_timeout darf nie unter 300s fallen.

2026-08-12, Daniel: 'hab versuch was zu schreiben aber bekomme keine
antworten' -- bei /codewesen-chat/ war proxy_read_timeout beim ersten
Subpath-Fix auf 30s stehen geblieben, waehrend GENI und /dakgord-chat/
schon auf 300s angehoben waren. Nginx kappte die SSE-Verbindung nach 30s
Stille, bevor unter der aktuellen Slot-Konkurrenz (GENI+Wesen+dak+gord
teilen sich 2 Slots der Chat-Instanz) das erste Token da war -- gemessen
57.5s bis zur vollstaendigen Antwort. Kein Playwright-Test moeglich: der
lokale Testlauf geht direkt gegen Port 8002/8000/8020, nicht durch Nginx.
"""
import re
from pathlib import Path

NGINX_CONF = Path("/etc/nginx/sites-available/flextrawurst")

CHAT_LOCATIONS = ["/codewesen-chat/", "/geni/", "/dakgord-chat/"]
MINDEST_TIMEOUT = 300


def _timeout_fuer_location(text: str, pfad: str) -> int:
    muster = re.compile(
        r"location\s+" + re.escape(pfad) + r"\s*\{(.*?)\n    \}", re.DOTALL)
    treffer = muster.search(text)
    assert treffer, f"Location {pfad} nicht in {NGINX_CONF} gefunden"
    block = treffer.group(1)
    zeit = re.search(r"proxy_read_timeout\s+(\d+)s", block)
    assert zeit, f"kein proxy_read_timeout in Location {pfad}"
    return int(zeit.group(1))


def test_alle_drei_chat_locations_haben_ausreichenden_timeout():
    text = NGINX_CONF.read_text()
    for pfad in CHAT_LOCATIONS:
        wert = _timeout_fuer_location(text, pfad)
        assert wert >= MINDEST_TIMEOUT, (
            f"{pfad}: proxy_read_timeout {wert}s < {MINDEST_TIMEOUT}s -- "
            f"echte Generierung unter Slot-Konkurrenz braucht laenger, siehe "
            f"docs/systemdoku/10_dakgord.md"
        )
