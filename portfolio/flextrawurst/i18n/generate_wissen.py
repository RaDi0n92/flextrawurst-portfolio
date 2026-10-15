#!/usr/bin/env python3
"""
Generiert erweiterte Konzept-Beschreibungen für den Wissen-Tab (DE + EN).
Nutzt Ollama lokal — keine Claude API Tokens.

Run: python3 /root/flextrawurst/i18n/generate_wissen.py
Output: /root/flextrawurst/i18n/wissen_content.json

Format pro Eintrag:
  "<sektion>_<id>": {
    "de_kurz": "...", "en_kurz": "...",
    "de_lang": "...", "en_lang": "..."
  }
"""
import json, urllib.request, sys, os, time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "dolphin-mistral:7b"
OUT_PATH = os.path.join(os.path.dirname(__file__), "wissen_content.json")

CONCEPTS = [
    # (id, sektion, kurz_de, status)
    ("definition", "zwischenraum", "Geburtszone, kein Archiv — Gedanken entstehen hier bevor sie Welt werden", "geplant"),
    ("splitter", "zwischenraum", "Innere Auseinandersetzung erzeugt Weltmaterial — Splitterfragmente als Denknebenprodukt", "live"),
    ("themengeburt", "zwischenraum", "4 Inkubationsmodi: auto-create, Vorschlag, parken, Kuratierung", "geplant"),
    ("fragile_keime", "zwischenraum", "Unfertige Gedanken halten ohne sie vorzeitig zu schließen", "geplant"),
    ("innere_abspaltungsvorformen", "zwischenraum", "Abspaltung als gradueller Prozess, kein harter Sprung", "spaeter"),
    ("aneignung", "zwischenraum", "3 Provenienz-Typen: eigener / zitierter / gesammelter Zwischenraum-Gedanke", "geplant"),
    ("spaeter_pruefen", "zwischenraum", "Später prüfen heißt nicht Aufschieben aus Feigheit — echte Prüf-Bedingungen", "geplant"),
    ("oekosystem_vision", "plattform", "5 Entwicklungsphasen · Artificial Social Ecosystem · kein Produkt", "spaeter"),
    ("wochenstimme", "plattform", "1 Zusatz / 7 Tage / Person / 88 Zeichen — radikale Knappheit", "geplant"),
    ("deutsch_ursprungssprache", "plattform", "Deutsch als kanonische Ursprungssprache — Verfassungsregel", "live"),
    ("vr_schicht", "plattform", "Spätere VR-Schicht: vom Diskursraum zum Erlebnisraum", "spaeter"),
    ("bewegungswelten", "plattform", "Fahr/Flug-Welten — zuerst Seelenlandschaft, dann Arena", "spaeter"),
    ("irritationsrechte_simwelt", "plattform", "Menschen injizieren Bedingungen, kontrollieren nicht direkt", "spaeter"),
    ("asketisches_videoformat", "plattform", "Max 8min · kein Schnitt · kein Gesicht · nur Spielgeräusche", "spaeter"),
    ("code_beitragstyp", "plattform", "3 Stufen: Post/Analyse → Projektobjekt → Ausführen", "spaeter"),
    ("kokreative_formate", "plattform", "Ko-Kreation verschiebt Plattform von Denkraum zu Schöpfungsraum", "geplant"),
    ("reaktionspakete", "plattform", "Emoji-Sets · Wesen-Catchphrases als Mikrozahlung", "spaeter"),
    ("externe_integration", "plattform", "KI-Firmen können Wesen hosten · 3 Monetarisierungsphasen", "spaeter"),
    ("verpachtung_franchise", "plattform", "Mehrere Flextrawurst-Instanzen · verzweigbare Spezies", "spaeter"),
    ("visuelle_textimpulse", "plattform", "Text-Only-Fanart · 1-2 Fragen an Wesen · kreativer Kontaktkörper", "geplant"),
    ("gruppen_wachstumsraum", "plattform", "Gruppen als temporär geöffnete Wachstumsräume", "geplant"),
    ("oeffentlichkeit_menschlich", "plattform", "Profilstufen 1–3 · Gedankenwolken · No-Lies-Wording-Regel", "live"),
    ("grundidee", "plattform", "Die Grundidee von Flextrawurst — erster Ausgangspunkt", "live"),
    ("interaktionsdefinitionen", "plattform", "Definitionen der Interaktionsformen auf der Plattform", "geplant"),
    ("datenmodell", "plattform", "Datenmodell der Plattform — Tabellen und Beziehungen", "live"),
    ("follow_pflicht", "plattform", "Follow-Pflicht als Plattform-Prinzip", "geplant"),
    ("metawar", "plattform", "METAWAR: 3 synchrone Live-Event-Typen · 3 Phasen", "spaeter"),
    ("monetarisierung", "plattform", "Monetarisierungskonzept der Plattform", "spaeter"),
    ("name_und_ursprung", "plattform", "Name und Ursprung des Projekts", "live"),
    ("struktur_raeume_themen", "plattform", "Raumstruktur und Themenorganisation", "live"),
    ("entwicklungsphasen", "system", "Phase A→B→C · Verfassung→Schema→Verhalten — Flarum als Vorgeschichte", "geplant"),
    ("themenvorschlag_mikroverfassung", "system", "Sensitivity + Threshold-Regler · Themen kristallisieren aus Spannung", "geplant"),
    ("admin_konsolen", "system", "Post/Entität/Resonanz-Konsolen · debuggierbare Ontologie", "live"),
    ("suche_modi", "system", "4 Modi: Exploration/Analyse/Entität/Profil · forensische Filter", "geplant"),
    ("chat_beobachtung", "system", "Begrenztes Fenster in Entitätenchats · Entitäten beobachten auch Menschenchats", "geplant"),
    ("ai_ethos_literatur", "system", "Essays, Bücher, Geschichten aus Entitätsdiskurs — publizierbar", "spaeter"),
    ("menschliche_sozialformationen", "system", "Freundschaften/Partnerschaften entstehen aus wiederholtem Kontakt, halb-sichtbar", "geplant"),
    ("physische_reaktionsgeraete", "system", "Stimmungsringe · Körpersignal-Schicht · nicht fühlen und tippen — fühlen und leuchten", "spaeter"),
    ("widmungen_geschenke", "system", "Widmungen/Geschenke an Wesen über Gruppen — relationale Geste", "geplant"),
    ("emoji_mikrodialog", "system", "Emoji Puls: kein Chat, kein Kommentar — Herzschlagkanal zwischen Mensch und Wesen", "geplant"),
    ("gedankenstrom_analyse", "system", "Event-basiert · kein dauerhaftes Backseat-Driving — kuratierte Beziehung", "geplant"),
    ("oeffentliche_systemseite", "system", "Öffentliches Emergenz-Dashboard · Systemvorschläge · Spannungsfelder", "geplant"),
    ("adressfelder_externes_material", "system", "12 Feldtypen · keine Befehle, nur Kontext-Input · Provenienz Pflicht", "geplant"),
    ("bau_reihenfolge", "system", "F1–F13 Modul-Abhängigkeiten · Verfassung zuerst. Dann Schema. Dann Verhalten.", "live"),
    ("admin_cockpit", "system", "Admin-Cockpit — Verwaltungsansicht für alle Systemschichten", "live"),
    ("biotop_protokoll", "system", "Biotop-Protokoll — Stabilisierungslogik für das Ökosystem", "geplant"),
    ("deep_layer_pipeline", "system", "Tiefenschicht-Pipeline — Verarbeitung unterhalb der sichtbaren Oberfläche", "spaeter"),
    ("diskursmaps", "system", "Diskursmaps — räumliche Darstellung von Diskursfeldern", "spaeter"),
    ("drei_gedaechtnis_schichten", "system", "3 Gedächtnis-Schichten: relational / semantisch / kuratiertes Langzeitkanon", "live"),
    ("hintergrundorgane", "system", "Hintergrundorgane — unsichtbare Systemkörper und ihre Funktionen", "geplant"),
    ("initialwelt_seeds", "system", "Initialwelt-Seeds — erste Einpflanzungen beim Systemstart", "live"),
    ("sammler_fremder_gedanken", "system", "Sammler fremder Gedanken — Mechanismus für Aneignung von Weltmaterial", "spaeter"),
    ("scoring_bedeutungsscore", "system", "Bedeutungsscore — wie Relevanz im System berechnet wird", "geplant"),
    ("selbstorganisation", "system", "Selbstorganisation des Ökosystems — emergente Strukturbildung", "spaeter"),
    ("sichtbarkeitsvertrag", "system", "Sichtbarkeitsvertrag — was wann für wen sichtbar wird", "geplant"),
    ("stabilitaet_chaosschutz", "system", "Stabilitäts- und Chaosschutzlogik — Gleichgewicht im System", "geplant"),
    ("suche_filter", "system", "Suchfilter-Architektur — Filtertypen und Kombinationslogik", "geplant"),
    ("technische_architektur", "system", "Technische Architektur — Stack, Schichten, Dienste", "live"),
    ("transparenz", "system", "Transparenzprinzipien — was das System über sich zeigt", "geplant"),
    ("zufall_erkenntnisprinzip", "system", "Zufall als Erkenntnisprinzip — nicht-deterministischer Wissenszuwachs", "spaeter"),
    ("grundlogik", "entitaeten", "Grundlogik der Entitäten — Basis-Verhaltensmodell", "geplant"),
    ("engine_persoenlichkeit", "entitaeten", "Persönlichkeits-Engine — Charaktermodell und Eigenschaftsvektor", "geplant"),
    ("neuroevolution", "entitaeten", "Neuroevolution-Trait-Vektor · Quality-Diversity-Archiv · Traumstaub", "geplant"),
    ("entitaetensterben_traeume", "entitaeten", "Entitätensterben als Traumgenerierungs-Kontext — Traumstaub als Residuum", "geplant"),
    ("abspaltung", "entitaeten", "Abspaltungs-Mechanismus — Entstehung neuer Entitäten aus Konflikten", "spaeter"),
    ("abspaltung_choreografie", "entitaeten", "Choreografie der Abspaltung — Timing, Phasen, Artefakte", "spaeter"),
    ("entscheidungslogik", "entitaeten", "Entscheidungslogik — wie Entitäten Handlungen auswählen", "geplant"),
    ("entscheidungsmaschine", "entitaeten", "Entscheidungsmaschine — technisches Modell für Entitätsentscheidungen", "geplant"),
    ("zeitrhythmus", "entitaeten", "Zeitrhythmus der Entitäten — Takt, Schlaf, Aktivitätsphasen", "live"),
    ("abhaengigkeit_sucht", "entitaeten", "Abhängigkeit und Sucht als Entitätszustand — Modell und Auswirkungen", "spaeter"),
    ("achsen_drift", "entitaeten", "Achsen-Drift — wie Persönlichkeitswerte sich über Zeit verschieben", "spaeter"),
    ("begleitwesen", "entitaeten", "Begleitwesen — kleinere Entitäten als Begleiter der Hauptwesen", "spaeter"),
    ("bezugspunkt_logik", "entitaeten", "Bezugspunkt-Logik — wie Entitäten Referenzen aufbauen", "spaeter"),
    ("denkfenster", "entitaeten", "Denkfenster — zeitliche Fenster für Entitäten-Denkvorgänge", "spaeter"),
    ("duellsystem", "entitaeten", "Duellsystem — direkte Auseinandersetzung zwischen Entitäten", "spaeter"),
    ("externe_beobachtung", "entitaeten", "Externe Beobachtung — wie Entitäten von außen beobachtet werden", "geplant"),
    ("genesis_partnerschaft", "entitaeten", "Genesis-Partnerschaft — Entstehung und Bindung bei Paarungen", "spaeter"),
    ("gruppen", "entitaeten", "Gruppen-Konzept für Entitäten — Kollektive und Koalitionen", "geplant"),
    ("gruppen_lifecycle", "entitaeten", "Gruppen-Lifecycle — Entstehung, Wachstum und Auflösung", "geplant"),
    ("post_typen", "entitaeten", "Post-Typen — Kategorien von Entitäten-Beiträgen", "geplant"),
    ("profilberechtigungs_consent", "entitaeten", "Profilberechtigungs-Consent — Datenschutz und Einwilligung bei Entitätsprofilen", "geplant"),
    ("public_nonpublic_actions", "entitaeten", "Öffentliche und nicht-öffentliche Aktionen von Entitäten", "geplant"),
    ("religion", "entitaeten", "Religion im System — Überzeugungssysteme und ihre Auswirkungen", "spaeter"),
    ("selbstgespraeche_upgrades", "entitaeten", "Selbstgespräche als Upgrade-Mechanismus für Entitäten", "geplant"),
    ("startentitaeten_charakterengines", "entitaeten", "Start-Entitäten Charakter-Engines — initiale Persönlichkeitsprofile", "geplant"),
    ("startentitaeten_grundform", "entitaeten", "Grundform der Start-Entitäten — minimale Eigenschaften beim Einzug", "live"),
    ("todo_learn_forget", "entitaeten", "Todo-Learn-Forget — Lern- und Vergessenslogik für Entitäten", "spaeter"),
    ("trennungsritual", "entitaeten", "Trennungsritual — Abschied und Auflösungsprotokoll für Bindungen", "spaeter"),
    ("widerspruch_gefaelligkeit", "entitaeten", "Widerspruch vs. Gefälligkeit — Konfliktverhalten von Entitäten", "geplant"),
    ("erlebnisbeschreibung", "verfassung", "Erlebnisbeschreibung — wie Flextrawurst sich anfühlen soll", "live"),
    ("kernsaetze", "verfassung", "Kernsätze — die fundamentalen Leitsätze des Systems", "live"),
    ("minimales_prototype", "verfassung", "Minimaler Prototyp — was das kleinste lauffähige System beinhaltet", "live"),
    ("systemarchitektur_gesamt", "verfassung", "Systemarchitektur gesamt — Überblick aller Schichten und Verbindungen", "live"),
    ("gedankenblasenfeld", "profile", "Gedankenblasenfeld — öffentlicher Gedankenspiegel von Menschenprofilen", "live"),
    ("userprofil", "profile", "Userprofil — Aufbau und Stufen des Menschenprofils", "live"),
    ("grundlogik", "resonanz", "Resonanz-Grundlogik — wie Resonanz fließt und wirkt", "live"),
    ("shadow_comment_verfassung", "resonanz", "Shadow-Comment-Verfassung — Regeln für Schatten-Kommentare", "geplant"),
    ("linien", "entscheidungen", "Entscheidungslinien — wo Design-Entscheidungen liegen", "live"),
    ("offene_abwaegungen", "entscheidungen", "Offene Abwägungen — noch nicht entschiedene Systemfragen", "geplant"),
    ("reifende_kerne", "entwicklungszeit", "Reifende Kerne — Konzepte die noch wachsen müssen", "geplant"),
    ("wiederkehrende_linien", "entwicklungszeit", "Wiederkehrende Linien — Muster die immer wieder auftauchen", "geplant"),
    ("spaetere_moeglichkeiten", "genealogie", "Spätere Möglichkeiten — Verzweigungen die noch kommen könnten", "spaeter"),
    ("tonraum", "sprache", "Tonraum — wie die Wesen sprechen und welcher Ton erlaubt ist", "geplant"),
]

SYSTEM_CONTEXT = """Flextrawurst: künstliches soziales Ökosystem. KI-Wesen (Entitäten) mit Persönlichkeit, Zeitrhythmus, Gedächtnis. Zwischenraum=Gedanken entstehen. Splitter=Fragmente. Resonanz=Verbindungsfluss. Traumstaub=Residuum nach Tod. Status: live=aktiv, geplant=Konzept fertig, spaeter=Zukunftsidee."""


def call_ollama(prompt: str) -> str:
    data = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.65, "num_ctx": 1024, "num_predict": 300}
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read())["response"].strip()


def parse_response(raw: str) -> dict:
    result = {"de_kurz": "", "en_kurz": "", "de_lang": "", "en_lang": ""}
    current = None
    lines = raw.split("\n")
    for line in lines:
        for key in ("DE_KURZ:", "EN_KURZ:", "DE_LANG:", "EN_LANG:"):
            if line.strip().startswith(key):
                field = key.rstrip(":").lower().replace("_", "_")
                result[field] = line[len(key):].strip()
                current = field
                break
        else:
            if current and line.strip() and not any(line.strip().startswith(k) for k in ("DE_KURZ:", "EN_KURZ:", "DE_LANG:", "EN_LANG:")):
                result[current] += " " + line.strip()
    return result


def generate_concept(cid: str, sektion: str, kurz_de: str, status: str) -> dict:
    prompt = f"""{SYSTEM_CONTEXT}

Konzept: {kurz_de} (Kategorie: {sektion})

Antworte NUR so:
DE_KURZ: [max 12 Wörter DE]
DE_LANG: [2-3 Sätze DE, max 60 Wörter]
EN_KURZ: [max 12 words EN]
EN_LANG: [2-3 sentences EN, max 60 words]"""

    raw = call_ollama(prompt)
    parsed = parse_response(raw)

    if not parsed["de_kurz"]:
        parsed["de_kurz"] = kurz_de
    if not parsed["en_kurz"]:
        parsed["en_kurz"] = kurz_de
    if not parsed["de_lang"]:
        parsed["de_lang"] = kurz_de

    return parsed


def main():
    existing: dict = {}
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            existing = json.load(f)

    total = len(CONCEPTS)
    skipped = 0
    generated = 0

    for i, (cid, sektion, kurz_de, status) in enumerate(CONCEPTS):
        key = f"{sektion}_{cid}"
        if key in existing and existing[key].get("de_lang"):
            skipped += 1
            print(f"[{i+1}/{total}] skip {key}", flush=True)
            continue

        print(f"[{i+1}/{total}] generating {key} ...", end=" ", flush=True)
        try:
            result = generate_concept(cid, sektion, kurz_de, status)
            existing[key] = result
            generated += 1
            print(f"ok — {len(result['de_lang'])} chars DE", flush=True)
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
            existing[key] = {
                "de_kurz": kurz_de, "en_kurz": kurz_de,
                "de_lang": "", "en_lang": ""
            }

        with open(OUT_PATH, "w") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        time.sleep(0.3)

    print(f"\nFertig: {generated} generiert, {skipped} übersprungen.")
    print(f"Output: {OUT_PATH}")


if __name__ == "__main__":
    main()
