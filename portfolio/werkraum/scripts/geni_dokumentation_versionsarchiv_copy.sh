#!/usr/bin/env bash
set -euo pipefail

SRC="/root/werkraum/geni_dokumentation"
DST="/root/werkraum/geni_dokumentation_versionsarchiv"

mkdir -p "$DST"
stamp="$(LC_ALL=C date '+%d%b%y-%Huhr%M' | tr '[:upper:]' '[:lower:]')"

for source_file in "$SRC"/*.md; do
    [ -f "$source_file" ] || continue

    dokument="$(basename "$source_file" .md)"
    zielordner="$DST/$dokument"
    mkdir -p "$zielordner"

    bereits_gesichert=0
    while IFS= read -r archivdatei; do
        if cmp -s "$source_file" "$archivdatei"; then
            bereits_gesichert=1
            break
        fi
    done < <(find "$zielordner" -maxdepth 1 -type f -name '*.md' -print)

    [ "$bereits_gesichert" -eq 0 ] || continue

    ziel="$zielordner/$stamp.md"
    if [ -e "$ziel" ] && ! cmp -s "$source_file" "$ziel"; then
        nummer=2
        while [ -e "$zielordner/$stamp-$nummer.md" ]; do
            nummer=$((nummer + 1))
        done
        ziel="$zielordner/$stamp-$nummer.md"
    fi

    cp --preserve=mode,timestamps "$source_file" "$ziel"
    printf 'gesichert: %s -> %s\n' "$source_file" "$ziel"
done
