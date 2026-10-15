"""Fail-closed database runtime configuration for the Welt API import graph."""

import os


# Keep imports usable for source-level tests that install their synthetic DB
# driver after import. A real connection with this sentinel is intentionally
# invalid; it is not a credential or a usable database fallback.
DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "dbname=__flextrawurst_db_uri_required__ user=__missing_runtime_config__",
)
