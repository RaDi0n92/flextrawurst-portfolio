#!/usr/bin/env python3
"""Weltfutter — echte Fremdkoerper von ausserhalb des Systems als Splitter.

2026-08-01. Auslöser: gemessener Spiegelkreislauf. Alle 6267 Splitter im Zwischenraum
hatten bis heute eine systeminterne Herkunft (innerer_abwurf, claude_abwurf, event,
wesen_vault, flarum_archiv ...) -- kein einziger kam von aussen. Gleichzeitig driftete
der Wortschatz der Wesen monoton ab: "Resonanz" stand im April 2026 in 1% der
Flarum-Posts, im Juli in 33%; "sondern" in 59%. Die Kurve laeuft durch den Modellwechsel
gemma4 -> hauhaucs (2026-07-06) hindurch, ohne zu zucken -- der Drift kommt also nicht
aus dem Modell, sondern daraus, dass jeder Eingabekanal der Wesen ein Spiegel ihrer
selbst ist (letzter_gedanke, rag_erkunden ueber das eigene Archiv, flarum_besuchen als
haeufigste Aktion ueberhaupt).

Idee zur Gegenmassnahme kam von ChatGPT ("Weltkollision"), Daniels Zusatz woertlich:
"Tagesschau nicht zum einzigen Nachrichtenschlund machen. RSS später rotierend aus
mehreren Ländern/Sprachen, GDELT als geografisches Streusalz. Sonst ersetzt ihr den
eigenen Spiegel nur durch einen deutschen Nachrichtenspiegel." Deshalb rotieren sowohl
die RSS-Quellen (12 Laender, 8 Sprachen) als auch die Wikipedia-Sprachversionen, und
GDELT streut Ereignisorte bei, die in keinem dieser Feeds vorkommen.

Ausdruecklich KEIN Wortverbot -- Daniel woertlich: "keine verbote das war scheisse".
Der Hebel ist Material, nicht Zensur.

Drei Sorten, bewusst unvereinbar (die Reibung entsteht aus der Kollision, nicht aus
der Auswahl -- deshalb werden im Vault-Takt spaeter alle drei gleichzeitig verlangt,
statt eine auswaehlen zu lassen):
  ereignis    — was Menschen gerade wichtig finden (RSS rotierend + GDELT-Orte)
  signal      — was ohne jeden Menschen passiert ist (USGS-Erdbeben)
  fundstueck  — was voellig zusammenhanglos existiert (Wikipedia-Zufallsartikel)

Grundgesetz 5 / "Spiel ist keine Fiktion": alles hier sind echte, live abgerufene
Daten mit nachpruefbarer Quelle. Nichts wird erfunden, nichts geglaettet. Die
Quell-URL steht in meta.quelle, damit die Herkunft jederzeit rueckverfolgbar ist.

Verfall: keine eigene Logik. splitter_daemon.py laesst Splitter nach
KONTAKT_STUNDEN=6 ohne Beruehrung mit ZERFALL=0.005/Tick verblassen -- bei
Startenergie 0.6 lebt ein Weltfutter-Splitter rund 8 Stunden. Der Nachfuell-Takt
(systemd-Timer) ist darauf abgestimmt.

Aufruf: python3 weltfutter.py [n_pro_sorte]   (Default 4)
"""

import os
import random
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import psycopg2
import psycopg2.extras
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from service_tokens import create_service_token as create_token  # noqa: E402

WELT_API = "http://localhost:8030"
ORIGIN_TYPE = "welt_extern"
UA = "flextrawurst-weltfutter/0.1 (+[E-MAIL])"
TIMEOUT = 15

# 2026-08-01 alle 15 einzeln getestet, diese 12 antworteten mit verwertbaren Items.
# Ausgefallen und deshalb nicht aufgenommen: News24 (ZA, DNS), TRT (TR, 404),
# El Universal (MX, 404). Wer hier etwas ergaenzt: vorher wirklich abrufen, nicht raten.
RSS_FEEDS = [
    ("DE", "tagesschau", "https://www.tagesschau.de/index~rss2.xml"),
    ("UK", "BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("FR", "Le Monde", "https://www.lemonde.fr/rss/une.xml"),
    ("QA", "Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("JP", "NHK", "https://www3.nhk.or.jp/rss/news/cat0.xml"),
    ("ES", "El País", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"),
    ("IN", "The Hindu", "https://www.thehindu.com/news/international/feeder/default.rss"),
    ("BR", "Folha de S.Paulo", "https://feeds.folha.uol.com.br/mundo/rss091.xml"),
    ("RU", "Meduza", "https://meduza.io/rss/all"),
    ("AU", "ABC News", "https://www.abc.net.au/news/feed/51120/rss.xml"),
    ("IT", "ANSA", "https://www.ansa.it/sito/ansait_rss.xml"),
    ("CN", "Xinhua", "http://www.xinhuanet.com/english/rss/worldrss.xml"),
]

# Rotierende Wikipedia-Sprachversionen -- derselbe Grund wie bei den RSS-Feeds:
# ein einzelnes de.wikipedia waere wieder nur ein deutschsprachiger Spiegel.
WIKI_SPRACHEN = ["de", "en", "fr", "es", "it", "ja", "ru", "pl", "sv", "nl", "pt", "fi"]

USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

# GDELT: NICHT die DOC-API (api.gdeltproject.org) -- die antwortet reproduzierbar mit
# HTTP 429 "limit requests to one every 5 seconds", getestet 2026-08-01, zwei Versuche
# je ~10s. Die statischen Viertelstunden-Exporte haben kein Rate-Limit (0,14s, 901
# Ereignisse pro Datei). Sie liefern keine Schlagzeile, aber genau das, wofuer sie hier
# da sind: Ereignisorte, die in keinem der 12 RSS-Feeds vorkommen.
GDELT_LASTUPDATE = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
GDELT_SPALTE_DATUM = 1
GDELT_SPALTE_ORT = 52
GDELT_SPALTE_QUELLE = 60

MATERIALITAET = {"ereignis": "wasser", "signal": "stein", "fundstueck": "nebel"}
STARTENERGIE = 0.6


def _db_uri() -> str:
    return os.environ.get(
        "FLEXTRAWURST_DB_URI",
        "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst",
    )


def _bereits_geholt() -> set:
    conn = psycopg2.connect(_db_uri(), cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT origin_id FROM splitter WHERE origin_type = %s", (ORIGIN_TYPE,))
            return {row["origin_id"] for row in cur.fetchall() if row["origin_id"]}
    finally:
        conn.close()


def _hole(url: str) -> requests.Response:
    # allow_redirects ist Default, aber hier bewusst explizit: der Wikipedia-Zufalls-
    # endpunkt antwortet mit 303 auf den konkreten Artikel, nicht mit 200 (2026-08-01
    # getestet -- ohne Folgen kommt kein JSON zurueck, sondern Klartext).
    return requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT, allow_redirects=True)


def _datum(text: str | None) -> str:
    if not text:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        return parsedate_to_datetime(text).strftime("%Y-%m-%d")
    except Exception:
        return text[:10]


def sammle_ereignisse(bereits: set, n: int) -> list[dict]:
    """RSS aus zufaellig gezogenen Laendern + GDELT-Orte als geografisches Streusalz.

    Das Kontingent wird fest geteilt: RSS bekommt hoechstens rss_quote Plaetze, der Rest
    ist fuer GDELT reserviert. Ohne diese Teilung fuellten die RSS-Feeds im ersten
    Testlauf (2026-08-01) das ganze Kontingent, und GDELT kam nie zum Zug -- genau das
    geografische Streusalz waere ausgefallen, um das es Daniel ging.
    """
    ergebnis = []
    rss_quote = max(1, (n + 1) // 2)
    for land, quelle, url in random.sample(RSS_FEEDS, min(4, len(RSS_FEEDS))):
        if len(ergebnis) >= rss_quote:
            break
        try:
            wurzel = ET.fromstring(_hole(url).content)
        except Exception as ex:
            print(f"  RSS {quelle} ({land}) fehlgeschlagen: {type(ex).__name__}: {ex}")
            continue
        items = wurzel.findall(".//item") or wurzel.findall(".//{http://www.w3.org/2005/Atom}entry")
        random.shuffle(items)
        for item in items:
            titel = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            # Manche Feeds fuehren Livestreams/Sendungen ohne echte Schlagzeile mit --
            # im Testlauf kam so ein Item mit dem Titel "tagesschau" durch. Als Reibungs-
            # flaeche taugt das nicht, es traegt weder Name noch Zahl noch Datum.
            if not titel or not link or len(titel) < 15 or titel.strip().lower() == quelle.lower():
                continue
            origin_id = f"rss:{land}:{link}"[:400]
            if origin_id in bereits:
                continue
            datum = _datum(item.findtext("pubDate") or item.findtext("{http://purl.org/dc/elements/1.1/}date"))
            beschreibung = (item.findtext("description") or "").strip()
            ergebnis.append({
                "sorte": "ereignis",
                "origin_id": origin_id,
                "essenz": f"[Nachricht · {quelle} ({land}), {datum}] {titel}",
                "rohtext": f"{titel}\n\n{beschreibung}\n\nQuelle: {link}",
                "tags": [land, quelle],
                "quelle": link,
            })
            bereits.add(origin_id)
            break  # pro Feed nur eine Meldung, damit kein Land den Takt dominiert

    # GDELT-Streusalz: Ereignisorte ohne Schlagzeile, dafuer geografisch weit ausserhalb
    # dessen, was die RSS-Auswahl abdeckt.
    try:
        zeilen = _hole(GDELT_LASTUPDATE).text.strip().splitlines()
        export_url = next(z.split()[-1] for z in zeilen if "export.CSV.zip" in z)
        import csv
        import io
        import zipfile
        roh = _hole(export_url).content
        with zipfile.ZipFile(io.BytesIO(roh)) as z:
            name = z.namelist()[0]
            text = z.read(name).decode("utf-8", errors="replace")
        reihen = [r for r in csv.reader(io.StringIO(text), delimiter="\t")
                  if len(r) > GDELT_SPALTE_QUELLE and r[GDELT_SPALTE_ORT].strip()]
        random.shuffle(reihen)
        for r in reihen:
            if len(ergebnis) >= n:
                break
            ort = r[GDELT_SPALTE_ORT].strip()
            quell_url = r[GDELT_SPALTE_QUELLE].strip()
            origin_id = f"gdelt:{r[0]}"[:400]
            if origin_id in bereits:
                continue
            datum = r[GDELT_SPALTE_DATUM]
            datum = f"{datum[:4]}-{datum[4:6]}-{datum[6:8]}" if len(datum) >= 8 else datum
            domain = quell_url.split("/")[2] if "//" in quell_url else quell_url
            ergebnis.append({
                "sorte": "ereignis",
                "origin_id": origin_id,
                "essenz": f"[Ereignisort · GDELT, {datum}] {ort} — berichtet von {domain}",
                "rohtext": f"GDELT-Ereignis am {datum}\nOrt: {ort}\nQuelle: {quell_url}",
                "tags": ["gdelt", "geo"],
                "quelle": quell_url,
            })
            bereits.add(origin_id)
    except Exception as ex:
        print(f"  GDELT fehlgeschlagen: {type(ex).__name__}: {ex}")

    # Wenn GDELT ausgefallen ist, lieber mit RSS auffuellen als das Kontingent leer lassen.
    if len(ergebnis) < n:
        for land, quelle, url in random.sample(RSS_FEEDS, len(RSS_FEEDS)):
            if len(ergebnis) >= n:
                break
            try:
                wurzel = ET.fromstring(_hole(url).content)
            except Exception:
                continue
            for item in wurzel.findall(".//item"):
                titel = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                origin_id = f"rss:{land}:{link}"[:400]
                if (not titel or not link or origin_id in bereits
                        or len(titel) < 15 or titel.strip().lower() == quelle.lower()):
                    continue
                ergebnis.append({
                    "sorte": "ereignis",
                    "origin_id": origin_id,
                    "essenz": f"[Nachricht · {quelle} ({land}), {_datum(item.findtext('pubDate'))}] {titel}",
                    "rohtext": f"{titel}\n\n{(item.findtext('description') or '').strip()}\n\nQuelle: {link}",
                    "tags": [land, quelle],
                    "quelle": link,
                })
                bereits.add(origin_id)
                break

    return ergebnis[:n]


def sammle_signale(bereits: set, n: int) -> list[dict]:
    """USGS-Erdbeben — echtes, nichtmenschliches Signal mit Ort, Staerke, Tiefe, Zeit."""
    ergebnis = []
    try:
        daten = _hole(USGS_FEED).json()
    except Exception as ex:
        print(f"  USGS fehlgeschlagen: {type(ex).__name__}: {ex}")
        return ergebnis

    # 2026-08-01, im ersten Testlauf aufgefallen: reines Shuffle ueber all_day lieferte
    # drei Mal Kalifornien. Das ist kein Zufall, sondern die Sensordichte -- USGS misst
    # dort noch Magnitude 0.7, waehrend anderswo nur spuerbare Beben auftauchen. Ein
    # kalifornisch-seismischer Spiegel waere nur ein anderer Spiegel. Deshalb: pro
    # Region (der Teil hinter dem letzten Komma in "place") hoechstens ein Beben, und
    # die Regionen selbst in zufaelliger Reihenfolge.
    beben = [f for f in daten.get("features", []) if (f.get("properties") or {}).get("mag") is not None]
    nach_region: dict[str, list] = {}
    for f in beben:
        ort = (f.get("properties", {}).get("place") or "unbekannt")
        region = ort.split(",")[-1].strip() or "unbekannt"
        nach_region.setdefault(region, []).append(f)
    regionen = list(nach_region)
    random.shuffle(regionen)
    # Innerhalb einer Region das staerkste Beben -- das ist das, was dort wirklich zaehlt.
    beben = [max(nach_region[r], key=lambda x: float(x["properties"]["mag"])) for r in regionen]

    for f in beben:
        if len(ergebnis) >= n:
            break
        p, g = f.get("properties", {}), f.get("geometry", {})
        origin_id = f"usgs:{f.get('id')}"[:400]
        if origin_id in bereits:
            continue
        koord = g.get("coordinates") or [None, None, None]
        tiefe = koord[2] if len(koord) > 2 else None
        zeit = datetime.fromtimestamp(p["time"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M UTC") \
            if p.get("time") else "?"
        ort = p.get("place") or "unbekannter Ort"
        tiefe_txt = f", Tiefe {round(float(tiefe), 1)} km" if tiefe is not None else ""
        ergebnis.append({
            "sorte": "signal",
            "origin_id": origin_id,
            "essenz": f"[Erdbeben · USGS, {zeit}] Magnitude {round(float(p['mag']), 1)}, {ort}{tiefe_txt}",
            "rohtext": (f"Erdbeben\nZeit: {zeit}\nMagnitude: {p['mag']}\nOrt: {ort}\n"
                        f"Tiefe: {tiefe} km\nKoordinaten: {koord[1]}, {koord[0]}\n"
                        f"Quelle: {p.get('url', USGS_FEED)}"),
            "tags": ["usgs", "erdbeben"],
            "quelle": p.get("url") or USGS_FEED,
        })
        bereits.add(origin_id)
    return ergebnis


def sammle_fundstuecke(bereits: set, n: int) -> list[dict]:
    """Wikipedia-Zufallsartikel aus rotierenden Sprachversionen."""
    ergebnis = []
    heute = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for sprache in random.sample(WIKI_SPRACHEN, min(n + 2, len(WIKI_SPRACHEN))):
        if len(ergebnis) >= n:
            break
        try:
            d = _hole(f"https://{sprache}.wikipedia.org/api/rest_v1/page/random/summary").json()
        except Exception as ex:
            print(f"  Wikipedia ({sprache}) fehlgeschlagen: {type(ex).__name__}: {ex}")
            continue
        titel = (d.get("title") or "").strip()
        auszug = (d.get("extract") or "").strip()
        if not titel or not auszug:
            continue
        origin_id = f"wikipedia:{sprache}:{titel}"[:400]
        if origin_id in bereits:
            continue
        link = (d.get("content_urls", {}).get("desktop", {}) or {}).get("page", "")
        ergebnis.append({
            "sorte": "fundstueck",
            "origin_id": origin_id,
            "essenz": f"[Wikipedia-Zufall · {sprache}, abgerufen {heute}] {titel} — {auszug[:150]}",
            "rohtext": f"{titel}\n\n{auszug}\n\nQuelle: {link}",
            "tags": ["wikipedia", sprache],
            "quelle": link,
        })
        bereits.add(origin_id)
    return ergebnis


def schreibe_splitter(eintrag: dict) -> str | None:
    resp = requests.post(
        f"{WELT_API}/admin/splitter",
        json={
            "origin_type": ORIGIN_TYPE,
            "origin_id": eintrag["origin_id"],
            "essenz": eintrag["essenz"][:250],
            "rohtext": f"{eintrag['rohtext']}\n\n[weltfutter-quelle] {eintrag['quelle']}"[:4000],
            "thematische_tags": ["welt_extern", eintrag["sorte"]] + eintrag["tags"][:3],
            "materialitaet": MATERIALITAET.get(eintrag["sorte"], "sternenstaub"),
            "energie": STARTENERGIE,
            "pos_x": round(random.uniform(-400, 400), 1),
            "pos_y": round(random.uniform(-400, 400), 1),
            "vel_x": round(random.gauss(0, 0.4), 3),
            "vel_y": round(random.gauss(0, 0.4), 3),
        },
        headers={"Authorization": f"Bearer {create_token('weltfutter', 'admin')}"},
        timeout=10,
    )
    return resp.json().get("id") if resp.status_code == 200 else None


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    bereits = _bereits_geholt()
    print(f"bereits geholt: {len(bereits)} welt_extern-Splitter")

    alle = []
    for name, sammler in (("ereignis", sammle_ereignisse),
                          ("signal", sammle_signale),
                          ("fundstueck", sammle_fundstuecke)):
        gefunden = sammler(bereits, n)
        print(f"{name:11} neu: {len(gefunden)}")
        alle.extend(gefunden)

    erstellt = 0
    for eintrag in alle:
        if schreibe_splitter(eintrag):
            erstellt += 1
        else:
            print(f"  FEHLER beim Schreiben: {eintrag['origin_id'][:70]}")
    print(f"Splitter erstellt: {erstellt}/{len(alle)}")
    return 0 if erstellt == len(alle) else 1


if __name__ == "__main__":
    sys.exit(main())
