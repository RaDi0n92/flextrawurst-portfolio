#!/usr/bin/env python3
"""Minimaler SSE-Signalgeber fuer den Gesamtkonstrukt-Planer (Stage 3 / Live-Updates).

Bewusst als eigener, kleiner Prozess gebaut statt als Endpunkt im gemeinsamen
Django/gunicorn-Dienst: der Validierungs-Agent (2026-09-02) fand, dass gunicorn dort
mit --workers 3 --threads 2 (gthread, WSGI, kein ASGI) nur 6 Request-Slots INSGESAMT
fuer die ganze oeffentliche Website hat. Eine offene SSE-Verbindung haelt einen Slot
dauerhaft belegt - ein paar offene Betriebssystem-Fenster wuerden reichen, um die
oeffentliche Lexikon-Seite lahmzulegen. Dieser Prozess laeuft komplett getrennt, kostet
also keinen einzigen gunicorn-Slot.

Traegt bewusst NIE echten Inhalt - nur ein minimales Signal (serverRevision), analog
zu flextrawursts eigenem events_stream_api.py-Muster (siehe CLAUDE.md Grundgesetz 8).
Die eigentlichen Daten holt der Client wie immer ueber die auth-geprueften REST-APIs.

Nur Python-Standardbibliothek - kein neues pip-Paket in einer bestehenden venv noetig.
Auth passiert eine Ebene hoeher: nginx spiegelt jede Verbindung per auth_request an den
bestehenden Django is_staff-Gate (siehe planner_whoami in planner_api.py).
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CURRENT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer/data/current.json")
PORT = 18094
POLL_SECONDS = 1.0
HEARTBEAT_SECONDS = 15
MAX_CONNECTIONS = 20
MAX_CONNECTION_SECONDS = 600  # Verbindung wird nach 10 Min sauber beendet, Client reconnectet selbst

_lock = threading.Lock()
_active_connections = 0


def _read_revision() -> int:
    try:
        with CURRENT.open("r", encoding="utf-8") as handle:
            return int(json.load(handle).get("serverRevision") or 0)
    except Exception:
        return 0


class Handler(BaseHTTPRequestHandler):
    server_version = "PlannerEventsStream/1"

    def log_message(self, fmt, *args):
        pass  # eigenes access.log waere Overkill fuer diesen kleinen Dienst

    def do_GET(self):
        global _active_connections
        with _lock:
            if _active_connections >= MAX_CONNECTIONS:
                self.send_response(503)
                self.send_header("Retry-After", "5")
                self.end_headers()
                return
            _active_connections += 1
        try:
            self._stream()
        finally:
            with _lock:
                _active_connections -= 1

    def _stream(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")  # nginx: nicht puffern
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        last_sent = _read_revision()
        try:
            self.wfile.write(f"retry: 3000\ndata: {json.dumps({'serverRevision': last_sent})}\n\n".encode())
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return

        started = time.monotonic()
        last_heartbeat = started
        while time.monotonic() - started < MAX_CONNECTION_SECONDS:
            time.sleep(POLL_SECONDS)
            now = time.monotonic()
            current = _read_revision()
            try:
                if current != last_sent:
                    last_sent = current
                    self.wfile.write(f"data: {json.dumps({'serverRevision': current})}\n\n".encode())
                    self.wfile.flush()
                    last_heartbeat = now
                elif now - last_heartbeat >= HEARTBEAT_SECONDS:
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
                    last_heartbeat = now
            except (BrokenPipeError, ConnectionResetError):
                return


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server.daemon_threads = True
    print(f"planner_events_stream: listening on 127.0.0.1:{PORT}, max {MAX_CONNECTIONS} Verbindungen")
    server.serve_forever()


if __name__ == "__main__":
    main()
