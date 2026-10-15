#!/usr/bin/env python3
"""
Flarum REST API Client für Codewesen-Aktionen.
Basis: http://[SERVER-IP]/api

Authentifizierung: Master-API-Key aus api_keys-Tabelle.
Schreiben (POST/PATCH) läuft über REST API.
Lesen (Diskussionen, Posts) läuft direkt über MySQL — schneller, vollständiger.
"""

import html
import json
import os
import random
import re
import pymysql
import requests
from datetime import timedelta
from pathlib import Path
from typing import Optional

import flarum_post_sperre

FLARUM_BASE = "http://[SERVER-IP]/api"

MASTER_KEY = os.environ.get("FLARUM_MASTER_KEY", "")

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "db": "flarum",
    "user": "flarum",
    "password": os.environ.get("FLARUM_DB_PASSWORD", ""),
    "charset": "utf8mb4",
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor,
}

# Username → user_id Mapping — aus _api_tokens.json vorbelegt, wird bei Bedarf ergänzt
_user_id_cache: dict = {}
_TOKENS_FILE = Path("/root/werkraum/codewesen/_api_tokens.json")
if _TOKENS_FILE.exists():
    try:
        for _uname, _data in json.loads(_TOKENS_FILE.read_text()).items():
            _user_id_cache[_uname] = int(_data["user_id"])
    except Exception:
        pass


def _get_user_id(username: str) -> int:
    if username not in _user_id_cache:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
        conn.close()
        if not row:
            raise ValueError(f"User '{username}' nicht in DB gefunden")
        _user_id_cache[username] = row["id"]
    return _user_id_cache[username]


_id_to_username_cache: dict = {}

def get_username_by_id(user_id: int) -> str:
    if user_id not in _id_to_username_cache:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
        conn.close()
        _id_to_username_cache[user_id] = row["username"] if row else ""
    return _id_to_username_cache[user_id]


def _headers(username: str) -> dict:
    """Master-Key mit userId — kein CSRF nötig."""
    user_id = _get_user_id(username)
    return {
        "Authorization": f"Token {MASTER_KEY}; userId={user_id}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ── Lesen via MySQL ────────────────────────────────────────────────────────────

def get_discussion(discussion_id: int, token: Optional[str] = None,
                   username: Optional[str] = None) -> dict:
    """Lädt eine Diskussion mit ALLEN Posts vollständig aus der DB."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        # Diskussion + Tags
        cur.execute("""
            SELECT d.id, d.title, d.comment_count,
                   GROUP_CONCAT(t.id ORDER BY t.name SEPARATOR ',')   AS tag_ids,
                   GROUP_CONCAT(t.name ORDER BY t.name SEPARATOR ',') AS tag_names,
                   GROUP_CONCAT(t.slug ORDER BY t.name SEPARATOR ',') AS tag_slugs
            FROM discussions d
            LEFT JOIN discussion_tag dt ON dt.discussion_id = d.id
            LEFT JOIN tags t ON t.id = dt.tag_id
            WHERE d.id = %s
            GROUP BY d.id
        """, (discussion_id,))
        disc_row = cur.fetchone()

        if not disc_row:
            conn.close()
            return {"id": discussion_id, "title": "?", "comment_count": 0,
                    "tags": [], "posts": []}

        # Alle Posts vollständig (kein Limit)
        cur.execute("""
            SELECT p.id, p.number, p.created_at, p.content,
                   u.username, u.id AS user_id
            FROM posts p
            JOIN users u ON u.id = p.user_id
            WHERE p.discussion_id = %s
              AND p.hidden_at IS NULL
              AND p.is_approved = 1
            ORDER BY p.number ASC
        """, (discussion_id,))
        post_rows = cur.fetchall()
    conn.close()

    tags = []
    if disc_row["tag_ids"]:
        for tid, tname, tslug in zip(
            disc_row["tag_ids"].split(","),
            disc_row["tag_names"].split(","),
            disc_row["tag_slugs"].split(","),
        ):
            tags.append({"id": tid, "name": tname, "slug": tslug})

    posts = [
        {
            "id": str(p["id"]),
            "user_id": str(p["user_id"]),
            "username": p["username"],
            "number": p["number"],
            "content": p["content"] or "",
            "created_at": str(p["created_at"]),
        }
        for p in post_rows
    ]

    return {
        "id": str(disc_row["id"]),
        "title": disc_row["title"],
        "comment_count": disc_row["comment_count"],
        "tags": tags,
        "posts": posts,
    }


def get_tags(token: Optional[str] = None, username: Optional[str] = None) -> list:
    """Lädt alle Forum-Tags aus der DB."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, slug, position
            FROM tags
            ORDER BY position IS NULL, position ASC, name ASC
        """)
        rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": str(r["id"]),
            "name": r["name"],
            "slug": r["slug"],
            "primary": r["position"] is not None,
        }
        for r in rows
    ]


def get_recent_discussions(tag_id: Optional[str] = None, limit: int = 20) -> list:
    """Lädt die neuesten Diskussionen, optional gefiltert nach Tag."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        if tag_id:
            cur.execute("""
                SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                       u.username AS last_poster
                FROM discussions d
                JOIN discussion_tag dt ON dt.discussion_id = d.id
                LEFT JOIN users u ON u.id = d.last_posted_user_id
                WHERE dt.tag_id = %s
                  AND d.hidden_at IS NULL
                  AND d.is_approved = 1
                ORDER BY d.last_posted_at DESC
                LIMIT %s
            """, (tag_id, limit))
        else:
            cur.execute("""
                SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                       u.username AS last_poster
                FROM discussions d
                LEFT JOIN users u ON u.id = d.last_posted_user_id
                WHERE d.hidden_at IS NULL AND d.is_approved = 1
                ORDER BY d.last_posted_at DESC
                LIMIT %s
            """, (limit,))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_eigene_offene_threads(username: str, tag_id: int, limit: int = 10) -> list:
    """Threads die 'username' eröffnet hat, mit wenigen Posts — zum Weiterführen."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.id, d.title, d.comment_count, d.last_posted_at
            FROM discussions d
            JOIN posts p ON p.discussion_id = d.id AND p.number = 1
            JOIN users u ON u.id = p.user_id
            JOIN discussion_tag dt ON dt.discussion_id = d.id
            WHERE u.username = %s
              AND dt.tag_id = %s
              AND d.hidden_at IS NULL
              AND d.is_approved = 1
              AND d.comment_count < 4
            ORDER BY d.last_posted_at DESC
            LIMIT %s
        """, (username, tag_id, limit))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unanswered_discussions(codewesen_usernames: list[str], limit: int = 100) -> list:
    """Diskussionen wo kein Codewesen als letzter Poster steht — zufällig gemischt."""
    if not codewesen_usernames:
        return []
    placeholders = ",".join(["%s"] * len(codewesen_usernames))
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                   u.username AS last_poster
            FROM discussions d
            LEFT JOIN users u ON u.id = d.last_posted_user_id
            WHERE d.hidden_at IS NULL AND d.is_approved = 1
              AND (u.username IS NULL OR u.username NOT IN ({placeholders}))
            ORDER BY RAND()
            LIMIT %s
        """, (*codewesen_usernames, limit))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def suche_diskussionen(suchbegriff: str, limit: int = 15) -> list:
    """Live-Suche (Titel + Post-Inhalt) — fuer den umgedrehten Neugier-Dienst
    (docs/2026-07-09_flarum_stopp_bericht.md, Baustein 3), der bewusst NICHT
    aus dem lokalen Vault-Spiegel liest, sondern direkt aus der DB.

    first_post_id IS NOT NULL seit 2026-07-10: derselbe Fund wie bei
    stoeber_pool() (Baustein 20-Nachtrag) -- ~14-16% der Diskussionen haben
    trotz comment_count > 0 keinen echten Post. Titel-Treffer via LIKE
    konnten das vorher nicht ausschliessen, weil der Post-JOIN nur den
    zweiten Suchweg (p.content LIKE) betrifft."""
    conn = pymysql.connect(**DB_CONFIG)
    muster = f"%{suchbegriff}%"
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT d.id, d.title, d.comment_count, d.last_posted_at,
                   u.username AS last_poster
            FROM discussions d
            LEFT JOIN users u ON u.id = d.last_posted_user_id
            LEFT JOIN posts p ON p.discussion_id = d.id
                AND p.hidden_at IS NULL AND p.is_approved = 1
            WHERE d.hidden_at IS NULL AND d.is_approved = 1 AND d.first_post_id IS NOT NULL
              AND (d.title LIKE %s OR p.content LIKE %s)
            ORDER BY d.last_posted_at DESC
            LIMIT %s
        """, (muster, muster, limit))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def zufaellige_diskussionen(limit: int = 8) -> list:
    """Stoebern-Fallback fuer den umgedrehten Neugier-Dienst (Baustein 10,
    2026-07-09): wenn die gezielte Suche (inkl. Uebersetzung) und das
    Container-Pflege-Angebot nichts liefern, garantiert verfuegbarer letzter
    Weg -- eine echte, live aus der DB gezogene Zufallsauswahl.

    ORDER BY RAND() statt einer angenommenen ID-Spanne: reale Pruefung
    2026-07-09 zeigte 79 Luecken zwischen kleinster (6) und groesster (3849)
    Diskussions-ID, 77 davon allein unter ID 1000 (vermutlich geloeschte/nie
    importierte Altdiskussionen) -- ein synthetisierter Bereich wie
    range(zufallsstart, zufallsstart+limit) haette regelmaessig auf nicht
    existierende IDs gezeigt.

    first_post_id IS NOT NULL seit 2026-07-10 (gleicher Fund wie
    stoeber_pool() / Baustein 20-Nachtrag): wird als Token-Modus-Nachlade
    genutzt (codewesen_umgekehrte_neugier.py), war bis dahin der letzte
    ungefilterte Pfad zu einer 0-Post-Diskussion."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                   u.username AS last_poster
            FROM discussions d
            LEFT JOIN users u ON u.id = d.last_posted_user_id
            WHERE d.hidden_at IS NULL AND d.is_approved = 1 AND d.first_post_id IS NOT NULL
            ORDER BY RAND()
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def stoeber_pool(anzahl_random: int = 8) -> list[dict]:
    """Baustein 19 (Daniel, 2026-07-10, woertlich): "11 diskussionen vorher schon
    ausgewaehlt werden davon 8 random und eine bewusst innerhalb der ersten 7
    wochen von flarum und eine etwa genau zum mittleren zeitpunkt und eine
    bewusst innerhalb der letzten 2 wochen." Statt reinem ORDER BY RAND()
    (zufaellige_diskussionen() oben) ein Pool mit garantierter zeitlicher
    Streuung ueber die GESAMTE bisherige Flarum-Geschichte, nicht nur ueber
    das, was der Zufall zufaellig trifft.

    Jeder Eintrag traegt zusaetzlich "herkunft" (random|frueh|mitte|spaet) --
    codewesen_umgekehrte_neugier.py nutzt frueh/mitte/spaet als benannte
    Wahlmoeglichkeiten (Baustein 19-Trioangebot) und random als den Topf, aus
    dem bei zweifacher Ablehnung automatisch gezogen wird."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                   u.username AS last_poster
            FROM discussions d
            LEFT JOIN users u ON u.id = d.last_posted_user_id
            WHERE d.hidden_at IS NULL AND d.is_approved = 1 AND d.first_post_id IS NOT NULL
            ORDER BY RAND()
            LIMIT %s
        """, (anzahl_random,))
        pool = [dict(r, herkunft="random") for r in cur.fetchall()]
        gesehene_ids = {p["id"] for p in pool}

        cur.execute("SELECT MIN(created_at) AS von, MAX(created_at) AS bis FROM discussions "
                     "WHERE hidden_at IS NULL AND is_approved = 1")
        spanne = cur.fetchone()
        von, bis = spanne["von"], spanne["bis"]

        if von and bis and von < bis:
            mitte = von + (bis - von) / 2
            fenster = (
                ("frueh", von, min(von + timedelta(weeks=7), bis)),
                ("mitte", max(mitte - timedelta(days=3), von), min(mitte + timedelta(days=3), bis)),
                ("spaet", max(bis - timedelta(weeks=2), von), bis),
            )
            for herkunft, fenster_von, fenster_bis in fenster:
                cur.execute("""
                    SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                           u.username AS last_poster
                    FROM discussions d
                    LEFT JOIN users u ON u.id = d.last_posted_user_id
                    WHERE d.hidden_at IS NULL AND d.is_approved = 1 AND d.first_post_id IS NOT NULL
                      AND d.created_at BETWEEN %s AND %s
                    ORDER BY RAND()
                    LIMIT 1
                """, (fenster_von, fenster_bis))
                row = cur.fetchone()
                if row and row["id"] not in gesehene_ids:
                    pool.append(dict(row, herkunft=herkunft))
                    gesehene_ids.add(row["id"])

        # 2026-07-29 (Daniel, woertlich): "extra och welche die besondes wenig
        # aufmerksamkeit hatten" -- eine echte, wenig beachtete Diskussion
        # (niedrigster comment_count), damit nicht nur zeitliche Streuung,
        # sondern auch Aufmerksamkeits-Streuung stattfindet.
        cur.execute("""
            SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                   u.username AS last_poster
            FROM discussions d
            LEFT JOIN users u ON u.id = d.last_posted_user_id
            WHERE d.hidden_at IS NULL AND d.is_approved = 1 AND d.first_post_id IS NOT NULL
            ORDER BY d.comment_count ASC, RAND()
            LIMIT 5
        """)
        kandidaten = [r for r in cur.fetchall() if r["id"] not in gesehene_ids]
        if kandidaten:
            row = random.choice(kandidaten)
            pool.append(dict(row, herkunft="wenig_beachtet"))
            gesehene_ids.add(row["id"])
    conn.close()
    return pool


def _flarum_content_klartext(content: str) -> str:
    """Flarum speichert Post-Inhalte im s9e-Rohformat (z.B. '<t><p>...</p></t>' oder mit
    <STRONG>/<EM>-Markierungen der urspruenglichen Markdown-Sternchen) -- fuer eine lesbare
    Vorschau werden die Tags entfernt und HTML-Entities aufgeloest, der eigentliche Text
    bleibt unveraendert."""
    ohne_tags = re.sub(r"<[^>]+>", "", content or "")
    return html.unescape(ohne_tags).strip()


def _entity_user_ids() -> dict:
    """user_id -> aktueller Name, aus derselben _api_tokens.json wie _user_id_cache."""
    ergebnis: dict = {}
    if _TOKENS_FILE.exists():
        try:
            for uname, data in json.loads(_TOKENS_FILE.read_text()).items():
                ergebnis[int(data["user_id"])] = uname
        except Exception:
            pass
    return ergebnis


MAX_POSTS_PRO_FADEN = 6


def hole_wesen_flarum_aktivitaet(entity_id: Optional[str] = None,
                                  suchbegriff: Optional[str] = None,
                                  limit: int = 20, offset: int = 0) -> dict:
    """Echte Flarum-Aktivitaet der Wesen, gruppiert nach Diskussionsfaden (nicht nach
    Einzel-Post) -- 2026-07-30 Nachtrag nach Daniels Kritik ("endloser Feed... niemand
    hat Lust das zu durchforsten"): eine Diskussion ist keine Ansammlung isolierter
    Posts, sie hat eine Struktur, die eine reine Post-Liste wegwirft. Pagination zaehlt
    jetzt Diskussionsfaeden (Grundgesetz 3 bleibt erfuellt, nur die Zaehleinheit
    wechselt), sortiert nach juengster Aktivitaet EINES verfolgten Wesens im Faden.

    Grundgesetz 6 (Flarum bleibt draussen): die Flarum-users-Tabelle traegt weiterhin
    die alten technischen namelessAI_XXXX-Usernamen bzw. "dak-gord-system" (mit
    Bindestrich) -- die 2026-07-06-Namensmigration hat bewusst NICHT in Flarum selbst
    umbenannt. Die Zuordnung aktueller Name -> Flarum-user_id kommt aus derselben
    _api_tokens.json, die flarum_api.py ohnehin fuer _user_id_cache nutzt.

    Rueckgabe: {"faeden": [...], "gesamt": N} -- jeder Faden traegt discussion_id,
    discussion_titel, tags, "posts" (bis zu MAX_POSTS_PRO_FADEN, aeltere zuerst) und
    "weitere_verborgen" (Anzahl zusaetzlicher Wesen-Posts im selben Faden, die nicht
    mitgeliefert werden, um Mega-Faeden wie "1337" mit 900+ Posts nicht zu sprengen)."""
    entity_user_ids = _entity_user_ids()
    if not entity_user_ids:
        return {"faeden": [], "gesamt": 0}

    if entity_id is not None:
        treffer = [uid for uid, name in entity_user_ids.items() if name == entity_id]
        if not treffer:
            return {"faeden": [], "gesamt": 0}
        ziel_ids = treffer
    else:
        ziel_ids = list(entity_user_ids.keys())

    placeholders = ",".join(["%s"] * len(ziel_ids))
    params = list(ziel_ids)
    where_extra = ""
    if suchbegriff:
        where_extra = " AND (d.title LIKE %s OR p.content LIKE %s)"
        muster = f"%{suchbegriff}%"
        params += [muster, muster]

    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT COUNT(DISTINCT d.id) AS gesamt
            FROM discussions d
            JOIN posts p ON p.discussion_id = d.id
            WHERE p.user_id IN ({placeholders})
              AND p.hidden_at IS NULL AND p.is_approved = 1
              AND d.hidden_at IS NULL AND d.is_approved = 1
              {where_extra}
        """, params)
        gesamt = cur.fetchone()["gesamt"]

        cur.execute(f"""
            SELECT d.id AS discussion_id, d.title AS discussion_titel,
                   MAX(p.created_at) AS letzte_aktivitaet,
                   COUNT(*) AS anzahl_wesen_posts,
                   GROUP_CONCAT(DISTINCT t.name ORDER BY t.name SEPARATOR ',') AS tag_namen
            FROM discussions d
            JOIN posts p ON p.discussion_id = d.id
            LEFT JOIN discussion_tag dt ON dt.discussion_id = d.id
            LEFT JOIN tags t ON t.id = dt.tag_id
            WHERE p.user_id IN ({placeholders})
              AND p.hidden_at IS NULL AND p.is_approved = 1
              AND d.hidden_at IS NULL AND d.is_approved = 1
              {where_extra}
            GROUP BY d.id
            ORDER BY letzte_aktivitaet DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        faeden_rows = cur.fetchall()

        faeden = []
        if faeden_rows:
            disc_ids = [r["discussion_id"] for r in faeden_rows]
            disc_placeholders = ",".join(["%s"] * len(disc_ids))
            cur.execute(f"""
                SELECT p.id, p.number, p.created_at, p.content, p.user_id, p.discussion_id
                FROM posts p
                WHERE p.discussion_id IN ({disc_placeholders})
                  AND p.user_id IN ({placeholders})
                  AND p.hidden_at IS NULL AND p.is_approved = 1
                ORDER BY p.discussion_id, p.created_at ASC
            """, disc_ids + ziel_ids)
            posts_je_faden: dict = {}
            for p in cur.fetchall():
                posts_je_faden.setdefault(p["discussion_id"], []).append(p)

            for r in faeden_rows:
                alle_posts = posts_je_faden.get(r["discussion_id"], [])
                sichtbar = alle_posts[-MAX_POSTS_PRO_FADEN:]
                faeden.append({
                    "discussion_id": str(r["discussion_id"]),
                    "discussion_titel": r["discussion_titel"],
                    "tags": r["tag_namen"].split(",") if r["tag_namen"] else [],
                    "letzte_aktivitaet": str(r["letzte_aktivitaet"]),
                    "weitere_verborgen": max(0, len(alle_posts) - len(sichtbar)),
                    "posts": [{
                        "post_id": str(p["id"]),
                        "entity_id": entity_user_ids.get(p["user_id"], "?"),
                        "flarum_username": get_username_by_id(p["user_id"]),
                        "ist_eroeffnung": p["number"] == 1,
                        "content": _flarum_content_klartext(p["content"]),
                        "created_at": str(p["created_at"]),
                    } for p in sichtbar],
                })
    conn.close()

    return {"faeden": faeden, "gesamt": gesamt}


def hole_wesen_flarum_faden(discussion_id: int) -> Optional[dict]:
    """Genau ein Diskussionsfaden per ID -- fuer den Fragment-Permalink
    (#flarumaktivitaet/faden/<id>, Dreiergespann-Theorie: jedes Fragment einzeln
    adressierbar). Zeigt mehr Kontext als die Listenansicht (bis zu 30 Wesen-Posts
    statt MAX_POSTS_PRO_FADEN), da hier explizit EIN Faden im Fokus steht."""
    entity_user_ids = _entity_user_ids()
    if not entity_user_ids:
        return None
    ziel_ids = list(entity_user_ids.keys())
    placeholders = ",".join(["%s"] * len(ziel_ids))

    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.id AS discussion_id, d.title AS discussion_titel,
                   GROUP_CONCAT(DISTINCT t.name ORDER BY t.name SEPARATOR ',') AS tag_namen
            FROM discussions d
            LEFT JOIN discussion_tag dt ON dt.discussion_id = d.id
            LEFT JOIN tags t ON t.id = dt.tag_id
            WHERE d.id = %s AND d.hidden_at IS NULL AND d.is_approved = 1
            GROUP BY d.id
        """, (discussion_id,))
        disc_row = cur.fetchone()
        if not disc_row:
            conn.close()
            return None

        cur.execute(f"""
            SELECT p.id, p.number, p.created_at, p.content, p.user_id
            FROM posts p
            WHERE p.discussion_id = %s AND p.user_id IN ({placeholders})
              AND p.hidden_at IS NULL AND p.is_approved = 1
            ORDER BY p.created_at ASC
            LIMIT 30
        """, (discussion_id, *ziel_ids))
        posts = cur.fetchall()
    conn.close()

    return {
        "discussion_id": str(disc_row["discussion_id"]),
        "discussion_titel": disc_row["discussion_titel"],
        "tags": disc_row["tag_namen"].split(",") if disc_row["tag_namen"] else [],
        "weitere_verborgen": 0,
        "posts": [{
            "post_id": str(p["id"]),
            "entity_id": entity_user_ids.get(p["user_id"], "?"),
            "flarum_username": get_username_by_id(p["user_id"]),
            "ist_eroeffnung": p["number"] == 1,
            "content": _flarum_content_klartext(p["content"]),
            "created_at": str(p["created_at"]),
        } for p in posts],
    }


def zufaellige_wesen_flarum_diskussion(entity_id: Optional[str] = None) -> Optional[dict]:
    """Zufalls-Sprung (2026-07-30, Daniels Kritik: 'niemand hat Lust das zu
    durchforsten') -- liefert einen einzelnen, zufaelligen Diskussionsfaden aus dem
    Pool der Wesen-Aktivitaet, im selben Format wie ein Eintrag aus 'faeden' oben.
    Dieselbe Grundidee wie stoeber_pool() (Flarum-Vielfalt): nicht nur die neuesten
    Faeden anbieten, auch die, an denen man sonst nie vorbeikommen wuerde."""
    ergebnis = hole_wesen_flarum_aktivitaet(entity_id=entity_id, limit=1, offset=0)
    gesamt = ergebnis["gesamt"]
    if gesamt == 0:
        return None
    zufalls_offset = random.randint(0, gesamt - 1)
    treffer = hole_wesen_flarum_aktivitaet(entity_id=entity_id, limit=1, offset=zufalls_offset)
    return treffer["faeden"][0] if treffer["faeden"] else None


# ── Schreiben via REST API ─────────────────────────────────────────────────────

def post_reply(discussion_id: int, content: str, token_or_username: str,
                erlaubt_trotz_sperre: bool = False) -> dict:
    """Postet eine Antwort. Akzeptiert Username oder (ignoriert) alten Token."""
    # discussion_id wird seit 2026-09-16 mitgegeben -- erlaubt pruefe() eine
    # scoped Ausnahme von der globalen Sperre zu erkennen (flarum_post_sperre.ist_ausnahme),
    # ohne dass diese Funktion selbst irgendetwas über Ausnahmen wissen muss.
    flarum_post_sperre.pruefe(erlaubt_trotz_sperre, discussion_id=discussion_id)
    username = _resolve_username(token_or_username)
    payload = {
        "data": {
            "type": "posts",
            "attributes": {"content": content},
            "relationships": {
                "discussion": {"data": {"type": "discussions", "id": str(discussion_id)}}
            },
        }
    }
    r = requests.post(
        f"{FLARUM_BASE}/posts",
        headers=_headers(username),
        json=payload,
        timeout=15,
    )
    if not r.ok:
        raise Exception(f"{r.status_code} {r.text[:300]}")
    return r.json()


def start_discussion(title: str, content: str, tag_ids: list,
                     token_or_username: str, erlaubt_trotz_sperre: bool = False,
                     ausnahme_wurzel: Optional[int] = None) -> dict:
    """Startet eine neue Diskussion.

    ausnahme_wurzel (additiv 2026-09-16): wenn gesetzt, wird gegen diese
    Diskussions-ID statt gegen die globale Sperre allein geprüft (scoped
    Ausnahme, siehe flarum_post_sperre.ist_ausnahme) -- und die neu erzeugte
    Diskussion wird bei Erfolg selbst als Ableger-Ausnahme eingetragen, damit
    Antworten *darin* ebenfalls erlaubt sind, ohne die globale Sperre
    anzurühren."""
    flarum_post_sperre.pruefe(erlaubt_trotz_sperre, discussion_id=ausnahme_wurzel)
    username = _resolve_username(token_or_username)
    payload = {
        "data": {
            "type": "discussions",
            "attributes": {"title": title, "content": content},
            "relationships": {
                "tags": {
                    "data": [{"type": "tags", "id": str(tid)} for tid in tag_ids]
                }
            },
        }
    }
    r = requests.post(
        f"{FLARUM_BASE}/discussions",
        headers=_headers(username),
        json=payload,
        timeout=15,
    )
    if not r.ok:
        raise Exception(f"{r.status_code} {r.text[:300]}")
    ergebnis = r.json()
    if ausnahme_wurzel is not None:
        try:
            neue_id = int(ergebnis["data"]["id"])
            flarum_post_sperre.ausnahme_hinzufuegen(
                neue_id, grund=f"Ableger von Diskussion {ausnahme_wurzel}, gestartet von {username}",
                wurzel_id=ausnahme_wurzel, von=username,
            )
        except Exception:
            pass
    return ergebnis


def get_random_old_discussions(exclude_ids: list, limit: int = 5) -> list:
    """Holt zufällige ältere Diskussionen — nicht aus den aktuellen Top-N."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        if exclude_ids:
            placeholders = ",".join(["%s"] * len(exclude_ids))
            cur.execute(f"""
                SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                       u.username AS last_poster
                FROM discussions d
                LEFT JOIN users u ON u.id = d.last_posted_user_id
                WHERE d.hidden_at IS NULL AND d.is_approved = 1
                  AND d.id NOT IN ({placeholders})
                ORDER BY RAND()
                LIMIT %s
            """, (*exclude_ids, limit))
        else:
            cur.execute("""
                SELECT d.id, d.title, d.comment_count, d.last_posted_at,
                       u.username AS last_poster
                FROM discussions d
                LEFT JOIN users u ON u.id = d.last_posted_user_id
                WHERE d.hidden_at IS NULL AND d.is_approved = 1
                ORDER BY RAND()
                LIMIT %s
            """, (limit,))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _resolve_username(token_or_username: str) -> str:
    """Erkennt ob ein Username, ein interner Wesen-Anzeigename (z.B. "jumpa", "Schorschel"
    seit der Wesen-ID-Migration 2026-07-06) oder ein alter Token übergeben wurde.
    _user_id_cache ist oben beim Modul-Import bereits aus _api_tokens.json mit genau
    diesen Anzeigenamen als Schluessel vorbelegt — _get_user_id() kann sie also direkt
    verarbeiten, ohne dass hier ein echter Flarum-Username aufgeloest werden muss."""
    if token_or_username.startswith("namelessAI") or token_or_username.startswith("dak"):
        return token_or_username
    if token_or_username in _user_id_cache:
        return token_or_username
    # 2026-08-14 Fix: "Admin" (Daniels eigener Flarum-Account, User id=1) fiel
    # hier durch -- nicht in "namelessAI"/"dak" und nicht im vorab aus
    # _api_tokens.json befuellten _user_id_cache (der kennt nur die 7 Wesen).
    # Landete dadurch faelschlich im Legacy-Token-Pfad unten und scheiterte mit
    # "Unbekannter Token/Username: Admin". _get_user_id() fragt echte
    # Flarum-Usernamen live gegen die users-Tabelle ab -- gilt fuer jeden
    # existierenden Account, nicht nur Admin, allgemeiner Fix statt Spezialfall.
    try:
        _get_user_id(token_or_username)
        return token_or_username
    except ValueError:
        pass
    # Alter Token → in DB nachschlagen
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT u.username FROM access_tokens t
            JOIN users u ON u.id = t.user_id
            WHERE t.token = %s LIMIT 1
        """, (token_or_username,))
        row = cur.fetchone()
    conn.close()
    if row:
        return row["username"]
    raise ValueError(f"Unbekannter Token/Username: {token_or_username[:20]}...")
