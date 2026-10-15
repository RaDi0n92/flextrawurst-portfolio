from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


CONFIG = Path("/etc/nginx/sites-available/flextrawurst")
MARKER = "# MEIN GESAMTKONSTRUKT PLANER — kanonischer servergespeicherter Arbeitskörper"
ANCHOR = "    # WORLDWORDS ANTIBIBEL — eigener Produktionskörper (2026-07-26, Daniels Auftrag)"

BLOCK = """    # MEIN GESAMTKONSTRUKT PLANER — kanonischer servergespeicherter Arbeitskörper
    location = /Mein-Gesamtkonstrukt-planer {
        return 301 /Mein-Gesamtkonstrukt-planer/;
    }

    location ^~ /Mein-Gesamtkonstrukt-planer/ {
        proxy_pass http://127.0.0.1:18093;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port 443;
        proxy_read_timeout 65s;
        proxy_connect_timeout 5s;
        client_max_body_size 6m;
    }

"""


def main() -> None:
    text = CONFIG.read_text(encoding="utf-8")
    if MARKER in text:
        print("nginx block already present")
        return
    if ANCHOR not in text:
        raise RuntimeError("nginx insertion anchor not found")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = CONFIG.with_name(f"flextrawurst.backup-before-gesamtkonstrukt-{stamp}")
    shutil.copy2(CONFIG, backup)

    updated = text.replace(ANCHOR, BLOCK + ANCHOR, 1)
    temporary = CONFIG.with_suffix(".tmp")
    temporary.write_text(updated, encoding="utf-8")
    os.chmod(temporary, CONFIG.stat().st_mode)
    os.replace(temporary, CONFIG)
    print(f"backup={backup}")
    print("installed=1")


if __name__ == "__main__":
    main()
