#!/usr/bin/env python3
"""Flarum-Archiv-Sampler — alte Flarum-Posts als Splitter-Fragmente in den Zwischenraum.

2026-07-31, Daniel: "die der codewesen und dakgord und geni und uns alle hier im system
und auch altes flarum und sachen aus den vaults der wesen ... soll splitterfaehig sein"

Grundgesetz 6 bleibt unangetastet: das ist KEIN Wesen-Einzug. Es werden nur einzelne,
anonyme Text-Fragmente aus alten Flarum-Posts als Splitter in den Zwischenraum gestreut --
die Flarum-Herkunft (username) landet nur in thematische_tags/meta, NICHT als flextrawurst-
entity_id. Die 6 Wesen bleiben auf Flarum "wohnhaft", nur ein Bruchstueck ihrer alten
Worte taucht als Fragment in KompOase auf.

Idempotent per Lauf: liest bereits erzeugte flarum_archiv-Splitter (origin_id = Flarum-
Post-ID) aus der Zwischenraum-DB und ueberspringt sie, damit wiederholte Laeufe nicht
denselben Post doppelt streuen. Kein Schreibzugriff auf die Flarum-DB selbst (Grundgesetz 6:
"Flarum bleibt draussen").

Aufruf: python3 flarum_archiv_splitter.py [n]   (n = wie viele neue Fragmente, Default 40)
"""

import os
import random
import re
import sys

import psycopg2
import psycopg2.extras
import pymysql
import pymysql.cursors

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from service_tokens import create_service_token as create_token  # noqa: E402

WELT_API = "http://localhost:8030"
FLARUM_DB_HOST = "127.0.0.1"
FLARUM_DB_USER = "flarum"
FLARUM_DB_NAME = "flarum"


def _flarum_pass() -> str:
    env_pfad = "/root/werkraum/.agent/flarum.env"
    if os.path.exists(env_pfad):
        for zeile in open(env_pfad, encoding="utf-8"):
            if zeile.startswith("FLARUM_DB_PASSWORD="):
                return zeile.strip().split("=", 1)[1]
    return os.environ.get("FLARUM_DB_PASSWORD", "")


def _tags_strippen(html: str) -> str:
    # Erst Entities entschluesseln, DANN Tags entfernen -- sonst bleiben aus
    # &lt;p&gt; entschluesselte, aber nie gestrippte <p>-Tags im Text stehen.
    text = (html or "").replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _bereits_gesampelt(db_uri: str) -> set:
    conn = psycopg2.connect(db_uri, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT origin_id FROM splitter WHERE origin_type = 'flarum_archiv'")
            return {row["origin_id"] for row in cur.fetchall() if row["origin_id"]}
    finally:
        conn.close()


def _flarum_posts_holen(bereits: set, n: int) -> list:
    conn = pymysql.connect(
        host=FLARUM_DB_HOST, user=FLARUM_DB_USER, password=_flarum_pass(),
        database=FLARUM_DB_NAME, cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.content, p.created_at, u.username
                FROM posts p
                JOIN users u ON u.id = p.user_id
                WHERE p.type = 'comment' AND p.hidden_at IS NULL
                ORDER BY RAND()
                LIMIT %s
            """, (n * 3,))  # Puffer, falls viele schon gesampelt sind
            kandidaten = cur.fetchall()
    finally:
        conn.close()

    ergebnis = []
    for row in kandidaten:
        if str(row["id"]) in bereits:
            continue
        text = _tags_strippen(row["content"])
        if len(text) < 20:
            continue
        ergebnis.append({"id": row["id"], "text": text, "username": row["username"], "created_at": row["created_at"]})
        if len(ergebnis) >= n:
            break
    return ergebnis


def _splitter_erstellen(post: dict) -> str | None:
    import requests

    essenz = post["text"][:150]
    resp = requests.post(
        f"{WELT_API}/admin/splitter",
        json={
            "origin_type": "flarum_archiv",
            "origin_id": str(post["id"]),
            "essenz": essenz,
            "rohtext": post["text"],
            "materialitaet": "gestein",
            "energie": round(0.35 + random.random() * 0.2, 2),
            "thematische_tags": ["flarum", "archiv", post["username"]][:5],
            "herkunft_sichtbar": True,
            "pos_x": round(random.uniform(-400, 400), 1),
            "pos_y": round(random.uniform(-400, 400), 1),
            "vel_x": round(random.gauss(0, 0.4), 3),
            "vel_y": round(random.gauss(0, 0.4), 3),
        },
        headers={"Authorization": f"Bearer {create_token('flarum-archiv-sampler', 'admin')}"},
        timeout=8,
    )
    if resp.status_code == 200:
        return resp.json().get("id")
    return None


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    db_uri = os.environ.get(
        "FLEXTRAWURST_DB_URI",
        "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst",
    )
    bereits = _bereits_gesampelt(db_uri)
    print(f"bereits gesampelt: {len(bereits)}")

    posts = _flarum_posts_holen(bereits, n)
    print(f"neue Kandidaten gefunden: {len(posts)}")

    erstellt = 0
    for post in posts:
        splitter_id = _splitter_erstellen(post)
        if splitter_id:
            erstellt += 1
    print(f"Splitter erstellt: {erstellt}/{len(posts)}")


if __name__ == "__main__":
    main()
