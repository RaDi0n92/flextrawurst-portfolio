#!/usr/bin/env bash
set -euo pipefail
cd /root/werkraum
if ! git diff --cached --quiet; then
  echo 'ABBRUCH: Bereits fremde staged Änderungen vorhanden' >&2
  git diff --cached --name-status >&2
  exit 71
fi
git add -- _shared/KNOTENVERTRAG.md
mapfile -t staged < <(git diff --cached --name-only)
if [[ ${#staged[@]} -ne 1 || "${staged[0]}" != "_shared/KNOTENVERTRAG.md" ]]; then
  echo 'ABBRUCH: Staging enthält nicht exakt den Knotenvertrag' >&2
  printf '%s\n' "${staged[@]}" >&2
  git reset -- _shared/KNOTENVERTRAG.md >/dev/null 2>&1 || true
  exit 72
fi
git diff --cached --check
git commit -m 'docs(atlas): Urbewohner-Abnahme an Quellstand binden'
printf 'COMMIT=%s\n' "$(git rev-parse HEAD)"
