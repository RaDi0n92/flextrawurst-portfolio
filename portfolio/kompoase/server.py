#!/usr/bin/env python3
# KompOase Server — statische Dateien + GENI-Proxy auf Port 8900

import http.server, urllib.request, ssl, json, os, re, sys, secrets
from datetime import datetime

PORT = 8900
GENI_URL = "https://localhost:8020/api/splitter"
WELT_API = "http://localhost:8030"
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

# 2026-09-18: Observability-Zaehler im HUD wollten wissen ob splitter-physik.service
# selbst noch tickt, nicht nur ob unser eigener GENI/DB-Abruf klappt. Der Daemon schreibt
# bereits pro Tick eine Zeile mit Zeitstempel in sein Log (kein neuer Code im laufenden
# Daemon noetig, kein Neustart von splitter-physik.service) -- wir lesen hier nur die
# letzte Zeile mit.
#
# 2026-09-19: der Pfad stand hier fest eingetippt, obwohl der Daemon ihn vom Dienst
# bekommt (SPLITTER_LOG_PATH in der ExecStart-Zeile von splitter-physik.service). Nach
# dem Umzug in die eigene Unit schrieb er woanders hin, und das HUD las eine seit
# 2026-09-18 13:57 eingefrorene Datei -- es meldete "steht still", waehrend der Daemon
# durchlief. Deshalb jetzt: alle bekannten Orte auflisten und den zuletzt geschriebenen
# nehmen. Das HUD kann damit keinen toten Log mehr anzeigen, solange ein lebender liegt.
SPLITTER_LOG_KANDIDATEN = [
    "/var/log/flextrawurst/splitter-physik.log",   # splitter-physik.service, seit dem Umzug
    "/root/werkraum/logs/splitter_daemon.log",     # Ort davor, bleibt als Rueckfallebene
]


def juengster_splitter_log():
    """Den zuletzt beschriebenen der bekannten Logs zurueckgeben, sonst None."""
    neuster, neuste_zeit = None, -1.0
    for pfad in SPLITTER_LOG_KANDIDATEN:
        try:
            zeit = os.stat(pfad).st_mtime
        except OSError:
            continue
        if zeit > neuste_zeit:
            neuster, neuste_zeit = pfad, zeit
    return neuster
TICK_ZEILE_MUSTER = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) Tick (\d+):")

# SSL-Kontext der self-signed certs von GENI akzeptiert
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# 2026-09-17, Daniel: "schau dir mal /toolbox genau an und kopiere den crawlzugang und
# die keyrotation 1zu1 nix anders machen genau so absichern" -- damit KompOase oeffentlich
# und crawlbar wird, ohne dass jeder x-beliebige Besucher Daniels Basic-Auth-Login teilen
# muesste. Gleicher Mechanismus wie /toolbox (tts_service.py), /claudelive, /codexlive,
# /geminilive: ein zweiter, unabhaengiger, jederzeit rotierbarer Geheimschluessel als
# ?key=...-Parameter, den Nginx gegen eine map-Datei prueft (kompoase-crawl-key.conf) und
# bei Treffer die Basic-Auth-Pruefung fuer den Request abschaltet -- Daniels eigener Login
# bleibt unveraendert bestehen, der Schluessel ist ein zusaetzlicher, separater Weg nur fuer
# Crawler/Bots. Rotations-Schutz bewusst wie beim Toolbox-Vorbild (nicht wie /claudelive,
# das dort extra einen zweiten Nginx-Realm einzieht) -- ein einfaches Passwort im
# Request-Body der Rotations-Route, kein Extra-Realm.
sys.path.insert(0, "/root/.claude")
from live_crawlkey import CrawlKey

CRAWL_KEY = CrawlKey(
    env_path="/root/kompoase/.env_crawl_key",
    nginx_conf_path="/etc/nginx/conf.d/kompoase-crawl-key.conf",
    map_name="kompoase_key_ok_arg",
    url_prefix="/zusatz-kompoase/",
)
CRAWL_KEY_ROTATE_PASSWORD = os.environ.get("KOMPOASE_CRAWL_ROTATE_PASSWORD", "[GESCHWAERZT]")

# 2026-09-17-KORREKTUR: KompOase hat -- anders als /toolbox -- zwei Map-Bloecke in
# derselben Nginx-Datei (Parameter- und Cookie-Pruefung, siehe kompoase-crawl-key.conf-
# Kommentar). CrawlKey.rotate() ersetzt mit seinem Regex nur das erste Vorkommen
# (count=1) -- hier zusaetzlich jedes noch verbliebene Vorkommen des alten Schluessels
# in derselben Datei durch den neuen ersetzen, dann Nginx erneut pruefen/neuladen.
def _sync_zweite_map(alter_key: str, neuer_key: str) -> None:
    import subprocess
    pfad = CRAWL_KEY.nginx_conf_path
    text = pfad.read_text(encoding="utf-8")
    if alter_key and alter_key in text:
        text = text.replace(alter_key, neuer_key)
        pfad.write_text(text, encoding="utf-8")
        subprocess.run(["nginx", "-t"], check=True, capture_output=True, timeout=15)
        subprocess.run(["systemctl", "reload", "nginx"], check=True, timeout=15)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    # 2026-09-17, Daniel: waehrend aktiver Live-Iteration an den statischen JS/CSS-Dateien
    # hielt der Browser wiederholt die alte, gecachte Fassung fest ("nix sichtbar
    # filterbar" -- der Fix war laengst hochgeladen, nur nicht neu geladen). SimpleHTTP-
    # RequestHandler setzt von sich aus keine expliziten Cache-Header, Browser duerfen
    # also nach eigenem Ermessen cachen. Erzwingt jetzt immer eine Neupruefung.
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/api/zwischenraum/"):
            self.proxy_welt(self.path[len("/api"):])
        elif self.path.startswith("/api/splitter"):
            self.proxy_splitter()
        elif self.path == "/crawl-key":
            self.zeige_crawl_key()
        elif self.path == "/api/daemon-heartbeat":
            self.zeige_daemon_heartbeat()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/zwischenraum/"):
            self.proxy_welt_post(self.path[len("/api"):])
        elif self.path == "/rotate-key":
            self.rotiere_crawl_key()
        else:
            self.send_response(404)
            self.end_headers()

    def _sende_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def zeige_crawl_key(self):
        key = CRAWL_KEY.read()
        host = self.headers.get("Host", f"localhost:{PORT}")
        self._sende_json(200, {"key": key, "crawl_url": CRAWL_KEY.crawl_url(host)})

    def zeige_daemon_heartbeat(self):
        try:
            log_pfad = juengster_splitter_log()
            if log_pfad is None:
                raise FileNotFoundError(
                    "keiner der bekannten Splitter-Logs vorhanden: "
                    + ", ".join(SPLITTER_LOG_KANDIDATEN))
            with open(log_pfad, "rb") as f:
                f.seek(0, os.SEEK_END)
                groesse = f.tell()
                f.seek(max(0, groesse - 4000))
                tail = f.read().decode("utf-8", "replace")
            zeilen = [z for z in tail.splitlines() if z.strip()]
            match = None
            for zeile in reversed(zeilen):
                match = TICK_ZEILE_MUSTER.match(zeile)
                if match:
                    break
            if not match:
                raise ValueError("keine Tick-Zeile im Log gefunden")
            letzter_tick = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
            alter_s = (datetime.now() - letzter_tick).total_seconds()
            self._sende_json(200, {
                "tick_nr": int(match.group(2)),
                "letzter_tick": match.group(1),
                "alter_sekunden": round(alter_s, 1),
                "quelle": log_pfad,
            })
        except Exception as e:
            self._sende_json(503, {"fehler": str(e)})

    def rotiere_crawl_key(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            body = {}
        if body.get("password") != CRAWL_KEY_ROTATE_PASSWORD:
            self._sende_json(403, {"fehler": "Passwort falsch."})
            return
        alter_key = CRAWL_KEY.read()
        try:
            new_key = CRAWL_KEY.rotate()
            _sync_zweite_map(alter_key, new_key)
        except Exception as e:
            self._sende_json(500, {"fehler": f"Rotation fehlgeschlagen: {e}"})
            return
        host = self.headers.get("Host", f"localhost:{PORT}")
        self._sende_json(200, {"key": new_key, "crawl_url": CRAWL_KEY.crawl_url(host)})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def proxy_welt_post(self, path):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b""
            req = urllib.request.Request(
                f"{WELT_API}{path}", data=body, method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except urllib.request.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(e.read())

    def proxy_splitter(self):
        n = 60
        if "n=" in self.path:
            try:
                n = int(self.path.split("n=")[1].split("&")[0])
            except Exception:
                pass
        try:
            req = urllib.request.Request(f"{GENI_URL}?n={n}")
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=8) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"fehler": str(e)}).encode())

    def proxy_welt(self, path):
        try:
            req = urllib.request.Request(f"{WELT_API}{path}")
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"fehler": str(e)}).encode())

    def log_message(self, fmt, *args):
        pass  # stille Logs

if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as srv:
        print(f"KompOase läuft auf Port {PORT}")
        srv.serve_forever()
