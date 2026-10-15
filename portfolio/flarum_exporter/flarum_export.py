#!/usr/bin/env python3
"""
Flarum Read-Only Exporter
- Holt Diskussionen + Posts via Flarum REST API (nur GET)
- Speichert jede Diskussion als HTML + JSON
- Erstellt Index, Manifest und ZIP
- Keine Schreibzugriffe auf Flarum
"""

import argparse
import json
import os
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests


# ---------------------------------------------------------------------------
# HTTP-Client (read-only)
# ---------------------------------------------------------------------------

class FlarumClient:
    def __init__(self, base_url: str, api_token: str | None = None, delay: float = 0.5):
        self.base = base_url.rstrip("/")
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if api_token:
            self.session.headers["Authorization"] = f"Token {api_token}"

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base}{path}"
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        time.sleep(self.delay)
        return resp.json()

    def fetch_discussion(self, discussion_id: int) -> dict:
        return self._get(f"/api/discussions/{discussion_id}")

    def fetch_posts_for_discussion(self, discussion_id: int) -> list[dict]:
        posts = []
        page = 1
        while True:
            data = self._get("/api/posts", params={
                "filter[discussion]": discussion_id,
                "page[number]": page,
                "page[limit]": 50,
            })
            batch = data.get("data", [])
            posts.extend(batch)
            if not data.get("links", {}).get("next"):
                break
            page += 1
        return posts

    def fetch_all_discussion_ids(self) -> list[int]:
        ids = []
        page = 1
        while True:
            data = self._get("/api/discussions", params={
                "page[number]": page,
                "page[limit]": 20,
            })
            batch = data.get("data", [])
            if not batch:
                break
            ids.extend(int(d["id"]) for d in batch)
            if not data.get("links", {}).get("next"):
                break
            page += 1
        return ids


# ---------------------------------------------------------------------------
# Daten-Extraktion aus JSON:API
# ---------------------------------------------------------------------------

def extract_included(raw: dict, typ: str) -> dict:
    """Liefert {id: attributes} für alle included-Objekte des angegebenen Typs."""
    result = {}
    for item in raw.get("included", []):
        if item.get("type") == typ:
            result[item["id"]] = item.get("attributes", {})
    return result


def build_discussion_record(raw_discussion: dict, raw_posts: list[dict]) -> dict:
    """Normalisiert eine Diskussion + Posts zu einem flachen Dict."""
    attr = raw_discussion["data"]["attributes"]
    users = extract_included(raw_discussion, "users")

    posts_clean = []
    for p in raw_posts:
        pa = p.get("attributes", {})
        author_id = (
            (p.get("relationships") or {})
            .get("user", {})
            .get("data", {})
            .get("id")
        )
        posts_clean.append({
            "id": p["id"],
            "number": pa.get("number"),
            "content_html": pa.get("contentHtml", ""),
            "content_type": pa.get("contentType", "comment"),
            "created_at": pa.get("createdAt"),
            "author_username": users.get(author_id, {}).get("username", "?") if author_id else "?",
            "author_display": users.get(author_id, {}).get("displayName", "") if author_id else "",
        })

    return {
        "id": raw_discussion["data"]["id"],
        "title": attr.get("title", "(kein Titel)"),
        "slug": attr.get("slug", ""),
        "comment_count": attr.get("commentCount", 0),
        "created_at": attr.get("createdAt"),
        "last_posted_at": attr.get("lastPostedAt"),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "posts": posts_clean,
    }


# ---------------------------------------------------------------------------
# HTML-Rendering
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
  .meta {{ color: #666; font-size: 0.85rem; margin-bottom: 2rem; }}
  .post {{ border-top: 1px solid #ddd; padding: 1.25rem 0; }}
  .post-header {{ display: flex; gap: 1rem; align-items: baseline; margin-bottom: 0.75rem; }}
  .post-num {{ color: #999; font-size: 0.8rem; min-width: 2rem; }}
  .author {{ font-weight: 600; font-size: 0.9rem; }}
  .post-date {{ color: #999; font-size: 0.8rem; }}
  .post-body {{ line-height: 1.6; }}
  .post-body img {{ max-width: 100%; height: auto; }}
  .post-body blockquote {{ border-left: 3px solid #ccc; margin: 0.5rem 0; padding: 0.25rem 1rem; color: #555; }}
  .post-body pre {{ background: #f4f4f4; padding: 0.75rem; overflow-x: auto; border-radius: 4px; }}
  .footer {{ margin-top: 3rem; border-top: 1px solid #eee; padding-top: 1rem; color: #aaa; font-size: 0.75rem; }}
  a.back {{ display: inline-block; margin-bottom: 1.5rem; color: #555; text-decoration: none; font-size: 0.85rem; }}
  a.back:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<a class="back" href="../index.html">← Zurück zum Index</a>
<h1>{title}</h1>
<div class="meta">
  Diskussion #{disc_id} &nbsp;·&nbsp;
  {comment_count} Beiträge &nbsp;·&nbsp;
  Erstellt: {created_at}
</div>
{posts_html}
<div class="footer">
  Exportiert: {exported_at} &nbsp;·&nbsp; Flarum-Export (read-only)
</div>
</body>
</html>
"""

POST_TEMPLATE = """\
<div class="post" id="post-{post_id}">
  <div class="post-header">
    <span class="post-num">#{number}</span>
    <span class="author">{author}</span>
    <span class="post-date">{created_at}</span>
  </div>
  <div class="post-body">{content_html}</div>
</div>
"""


def render_html(record: dict) -> str:
    posts_html = ""
    for p in record["posts"]:
        if p["content_type"] != "comment":
            continue
        author = p["author_display"] or p["author_username"]
        created = _fmt_date(p["created_at"])
        posts_html += POST_TEMPLATE.format(
            post_id=p["id"],
            number=p["number"],
            author=_escape(author),
            created_at=created,
            content_html=p["content_html"] or "",
        )

    return HTML_TEMPLATE.format(
        title=_escape(record["title"]),
        disc_id=record["id"],
        comment_count=record["comment_count"],
        created_at=_fmt_date(record["created_at"]),
        exported_at=_fmt_date(record["exported_at"]),
        posts_html=posts_html,
    )


def _escape(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso


# ---------------------------------------------------------------------------
# Index + Manifest
# ---------------------------------------------------------------------------

INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Flarum-Export — Index</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; }}
  h1 {{ font-size: 1.4rem; margin-bottom: 0.5rem; }}
  .meta {{ color: #666; font-size: 0.85rem; margin-bottom: 1.5rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th {{ text-align: left; border-bottom: 2px solid #ddd; padding: 0.4rem 0.5rem; }}
  td {{ border-bottom: 1px solid #eee; padding: 0.4rem 0.5rem; vertical-align: top; }}
  a {{ color: #0066cc; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>Flarum-Export — Index</h1>
<div class="meta">Exportiert: {exported_at} &nbsp;·&nbsp; {count} Diskussionen</div>
<table>
<thead><tr><th>#</th><th>Titel</th><th>Beiträge</th><th>Erstellt</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
</body>
</html>
"""

INDEX_ROW = '<tr><td>{disc_id}</td><td><a href="discussions/{filename}">{title}</a></td><td>{comment_count}</td><td>{created_at}</td></tr>\n'


def write_index(records: list[dict], out_dir: Path) -> None:
    rows = ""
    for r in sorted(records, key=lambda x: int(x["id"])):
        filename = f"discussion_{r['id']}.html"
        rows += INDEX_ROW.format(
            disc_id=r["id"],
            filename=filename,
            title=_escape(r["title"]),
            comment_count=r["comment_count"],
            created_at=_fmt_date(r["created_at"]),
        )
    html = INDEX_TEMPLATE.format(
        exported_at=_fmt_date(datetime.now(timezone.utc).isoformat()),
        count=len(records),
        rows=rows,
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def write_manifest(records: list[dict], out_dir: Path, base_url: str) -> None:
    manifest = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source_url": base_url,
        "discussion_count": len(records),
        "discussions": [
            {
                "id": r["id"],
                "title": r["title"],
                "slug": r["slug"],
                "comment_count": r["comment_count"],
                "created_at": r["created_at"],
                "html_file": f"discussions/discussion_{r['id']}.html",
                "json_file": f"json/discussion_{r['id']}.json",
            }
            for r in sorted(records, key=lambda x: int(x["id"]))
        ],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# ZIP
# ---------------------------------------------------------------------------

def create_zip(out_dir: Path) -> Path:
    zip_path = out_dir.parent / f"{out_dir.name}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(out_dir.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(out_dir.parent))
    return zip_path


# ---------------------------------------------------------------------------
# Export-Workflow
# ---------------------------------------------------------------------------

def export_discussion(client: FlarumClient, disc_id: int, out_dir: Path) -> dict:
    print(f"  Fetching discussion {disc_id}...", end=" ", flush=True)
    raw_disc = client.fetch_discussion(disc_id)
    raw_posts = client.fetch_posts_for_discussion(disc_id)
    print(f"{len(raw_posts)} Posts", flush=True)

    record = build_discussion_record(raw_disc, raw_posts)

    disc_dir = out_dir / "discussions"
    json_dir = out_dir / "json"
    disc_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    (json_dir / f"discussion_{disc_id}.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    html = render_html(record)
    (disc_dir / f"discussion_{disc_id}.html").write_text(html, encoding="utf-8")

    return record


def run_export(
    base_url: str,
    out_dir: Path,
    api_token: str | None,
    test_id: int | None,
    delay: float,
) -> None:
    client = FlarumClient(base_url, api_token=api_token, delay=delay)
    out_dir.mkdir(parents=True, exist_ok=True)

    if test_id is not None:
        print(f"TEST-MODUS: nur Diskussion {test_id}")
        record = export_discussion(client, test_id, out_dir)
        records = [record]
    else:
        print("Lade Diskussions-IDs...")
        ids = client.fetch_all_discussion_ids()
        print(f"{len(ids)} Diskussionen gefunden")
        records = []
        for i, disc_id in enumerate(ids, 1):
            print(f"[{i}/{len(ids)}]", end=" ")
            records.append(export_discussion(client, disc_id, out_dir))

    print("Erstelle Index und Manifest...")
    write_index(records, out_dir)
    write_manifest(records, out_dir, base_url)

    print("Erstelle ZIP...")
    zip_path = create_zip(out_dir)
    print(f"\nFertig:")
    print(f"  Ausgabe:  {out_dir}")
    print(f"  ZIP:      {zip_path}")
    print(f"  Dateien:  {len(records)} Diskussionen")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Flarum read-only Exporter — kein Schreibzugriff auf Flarum"
    )
    parser.add_argument("url", help="Flarum-Basis-URL, z.B. https://forum.example.com")
    parser.add_argument(
        "--out", default="flarum_export_output",
        help="Ausgabe-Verzeichnis (Standard: flarum_export_output)"
    )
    parser.add_argument("--token", default=None, help="API-Token für private Foren")
    parser.add_argument(
        "--test", type=int, default=None, metavar="ID",
        help="Nur eine Diskussion exportieren (Test-Modus)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5, metavar="SEC",
        help="Pause zwischen Requests in Sekunden (Standard: 0.5)"
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    try:
        run_export(
            base_url=args.url,
            out_dir=out_dir,
            api_token=args.token,
            test_id=args.test,
            delay=args.delay,
        )
    except requests.HTTPError as e:
        print(f"HTTP-Fehler: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAbgebrochen.")
        sys.exit(0)


if __name__ == "__main__":
    main()
