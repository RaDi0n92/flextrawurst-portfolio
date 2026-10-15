#!/usr/bin/env python3
"""
create_scenes_configs.py - Schreibt die Szenenkonfigurationen fuer
Bloecke 2, 3, 4, 5 im Graphic Novel / Cyber-Concept-Art Stil
"""

import json
import os

SONG_DIR = "/root/werkraum/_gemini/musikvideoprojekt/work/songs/11_chatgpt_welche_naechste_moeglichkeit"
FRAMES_BASE = os.path.join(SONG_DIR, "frames")

# ==========================================
# BLOCK 2 (56.20s): 12 Szenen je ~4.683s
# ==========================================
B2_SCENES = [
    {
        "id": "b2_s01_naechste_moeglichkeit",
        "dur": 4.68,
        "lyric": "Welche nächste Möglichkeit",
        "prompt": "glowing neon cyan cyber metropolis, towering holographic pathways and floating archways opening into the cosmos, luminous digital city skyline"
    },
    {
        "id": "b2_s02_was_schon_lebt",
        "dur": 4.68,
        "lyric": "Ergibt sich aus dem was schon lebt",
        "prompt": "ancient cyber code runes sprouting like glowing bioluminescent crystal vines from dark motherboard earth, organic technology blooming"
    },
    {
        "id": "b2_s03_tuer_geht_auf",
        "dur": 4.68,
        "lyric": "Welche Tür geht plötzlich auf",
        "prompt": "monumental golden geometric portal door swinging wide open over a deep abyss of violet light and flying data sparks"
    },
    {
        "id": "b2_s04_nicht_festklebt",
        "dur": 4.68,
        "lyric": "Wenn man nicht sofort alles festklebt",
        "prompt": "fluid liquid chrome and neon data streams floating freely in zero gravity, morphing shapes effortlessly, refusing to solidify"
    },
    {
        "id": "b2_s05_wuerzen_weiterdrehen",
        "dur": 4.68,
        "lyric": "Würzen, würzen, weiterdrehen",
        "prompt": "futuristic alchemical spice mortar and pestle grinding glowing cyan crystals into sparkling nebula dust, cosmic chemistry"
    },
    {
        "id": "b2_s06_etwas_reift",
        "dur": 4.68,
        "lyric": "Was passiert wenn etwas reift",
        "prompt": "a pulsating warm golden cyber-egg resting inside a high-tech glass containment vessel, gentle internal light growing stronger"
    },
    {
        "id": "b2_s07_neu_erscheint",
        "dur": 4.68,
        "lyric": "Und später plötzlich neu erscheint",
        "prompt": "the radiant hatched cyber creature unfurling multi-colored iridescent wings of laser light in the dark sky"
    },
    {
        "id": "b2_s08_zensi_alter_freund",
        "dur": 4.68,
        "lyric": "Erst Tensi, nein Zensi alter Freund",
        "prompt": "an ancient weathered cyber bunker door labeled with glowing stencil text ZENSI, wrapped in dormant neon cables and blue dust"
    },
    {
        "id": "b2_s09_labor_vergessen",
        "dur": 4.68,
        "lyric": "Da lag seit Wochen dieses Labor halb vergessen",
        "prompt": "forgotten subterranean experimental workshop, rows of silent cathode monitors, glowing vacuum tubes, retro-futuristic laboratory bench"
    },
    {
        "id": "b2_s10_gemini_feuer",
        "dur": 4.68,
        "lyric": "Gemini hatte damals Feuer",
        "prompt": "a blazing electric-blue dual entity crowned with lightning sparks, channeling raw computational fire into floating data rings"
    },
    {
        "id": "b2_s11_schatten_biopsie_ekg",
        "dur": 4.68,
        "lyric": "Schatten-Biopsie und Gedanken-EKG",
        "prompt": "holographic medical grid displaying vibrant 3D brainwaves and pulsing cyber-EKG waveforms floating above a steel console"
    },
    {
        "id": "b2_s12_kognition_temperatur",
        "dur": 4.72,
        "lyric": "Kognition als seltsame Temperatur",
        "prompt": "stylized cybernetic gauge measuring mind temperature, vibrant color spectrum shifting from deep cryogenic indigo to blinding thermonuclear gold"
    }
]

# ==========================================
# BLOCK 3 (57.00s): 12 Szenen je 4.75s
# ==========================================
B3_SCENES = [
    {
        "id": "b3_s01_tokenwahl_flimmern",
        "dur": 4.75,
        "lyric": "Nicht Gedankenlesen eher Flimmern, Tokenwahl",
        "prompt": "intricate glowing cyber matrix of branching neon probability threads, floating tokens selecting divergent cosmic paths"
    },
    {
        "id": "b3_s02_funken_kathedralen",
        "dur": 4.75,
        "lyric": "Gemini macht aus Funken gern Kathedralen",
        "prompt": "soaring colossal cathedral made of pure cyan laser pillars, vaulted arches of glowing digital starlight reaching into the stratosphere"
    },
    {
        "id": "b3_s03_flextrawurst_kern",
        "dur": 4.75,
        "lyric": "Flextrawurst im Kern: Was wird jetzt erst möglich",
        "prompt": "the pulsing subterranean heart of Flextrawurst, massive interconnected geometric gears of light driving new possibilities into existence"
    },
    {
        "id": "b3_s04_zensi_unberuehrt",
        "dur": 4.75,
        "lyric": "Das Lustigste an Zensi: Ich hab's selbst noch nie berührt",
        "prompt": "a pristine crystalline sanctuary sealed inside a hovering glass sphere, untouched futuristic relic radiating calm turquoise aura"
    },
    {
        "id": "b3_s05_sechzehn_tage",
        "dur": 4.75,
        "lyric": "Sechzehn Tage, vielleicht mehr",
        "prompt": "an ornate cybernetic hourglass dripping liquid diamonds through sixteen concentric glowing orbital rings"
    },
    {
        "id": "b3_s06_kompoase_explodiert",
        "dur": 4.75,
        "lyric": "Dann kam die KompOase explodiert",
        "prompt": "lush digital tropical oasis bursting out from dark basalt rocks, iridescent springs of glowing water and vibrant cyber palms"
    },
    {
        "id": "b3_s07_splitter_fragmente",
        "dur": 4.75,
        "lyric": "Splitter, Fragmente, Restgedanken",
        "prompt": "swarms of razor-sharp geometric glass crystal shards multiplying and reflecting intense magenta and amber laser beams"
    },
    {
        "id": "b3_s08_blasen_spuren",
        "dur": 4.75,
        "lyric": "Blasen, Spuren, fremder Klang",
        "prompt": "luminescent transparent sound bubbles carrying glowing ripples of musical notes across a dark starfield"
    },
    {
        "id": "b3_s09_abstoßen_halten_ziehen",
        "dur": 4.75,
        "lyric": "Dinge die sich gegenseitig formen, abstoßen, halten",
        "prompt": "magnetic celestial energy spheres pushing and pulling geometric light lattices in a breathtaking zero gravity dance"
    },
    {
        "id": "b3_s10_sprechen_lassen",
        "dur": 4.75,
        "lyric": "Die extremste Idee: sie sprechen lassen",
        "prompt": "ethereal holographic soundwave mouths emerging from swirling violet vapor, speaking in visible radiant laser frequencies"
    },
    {
        "id": "b3_s11_reinhoeren_schichten",
        "dur": 4.75,
        "lyric": "Nicht Mund dranmalen sondern reinhören Schicht für Schicht",
        "prompt": "futuristic acoustic frequency scanner peeling back holographic layers of deep sound like an onion in cyber space"
    },
    {
        "id": "b3_s12_stimmen_verstaerken",
        "dur": 4.75,
        "lyric": "Welche Stimmen sich verstärken, welche verschwinden",
        "prompt": "dramatic beams of focused spotlight amplifying into blinding radiance while faint whispers dissolve into velvety dark shadows"
    }
]

# ==========================================
# BLOCK 4 (46.60s): 10 Szenen je 4.66s
# ==========================================
B4_SCENES = [
    {
        "id": "b4_s01_teilchenwolke",
        "dur": 4.66,
        "lyric": "Ein Splitter als Teilchenwolke",
        "prompt": "dense vortex cloud of glittering micro-crystals swirling like a galactic nebula in deep obsidian void"
    },
    {
        "id": "b4_s02_token_flug",
        "dur": 4.66,
        "lyric": "Jedes Token nicht die Seele aber ein Druck im Flug",
        "prompt": "delicate cybernetic origami birds riding powerful invisible wind currents made of luminous mathematical vector arrows"
    },
    {
        "id": "b4_s03_wer_beeinflusst_wen",
        "dur": 4.66,
        "lyric": "Wer beeinflusst wen im Innern, wer grenzt wen aus",
        "prompt": "two glowing gravitational planetary cores in deep space shearing particle trails into intricate geometric patterns"
    },
    {
        "id": "b4_s04_was_kippt",
        "dur": 4.66,
        "lyric": "Was kippt wenn ein Stück verschwindet",
        "prompt": "a precarious architectural tower of glowing neon light blocks tipping gracefully as a single key foundation block disintegrates"
    },
    {
        "id": "b4_s05_teilchenlabor_staub",
        "dur": 4.66,
        "lyric": "Teilchenlabor für Bedeutungsstaub",
        "prompt": "colossal particle accelerator ring colliding glowing semantic words, spraying clouds of brilliant iridescent sparks"
    },
    {
        "id": "b4_s06_claude_ins_bild",
        "dur": 4.66,
        "lyric": "Und dann kam Claude ins Bild",
        "prompt": "a noble serene bronze and amber robotic cyber sentinel standing tall and wise, holding an open holographic ledger"
    },
    {
        "id": "b4_s07_quellen_auf_tisch",
        "dur": 4.66,
        "lyric": "Claude hatte Quellen auf den Tisch gelegt",
        "prompt": "a glowing glass conference table laden with floating holographic research papers, citations and architectural schematics"
    },
    {
        "id": "b4_s08_rag_erinnerung_kontext",
        "dur": 4.66,
        "lyric": "RAG, Erinnerung, Kontextfenster",
        "prompt": "vast infinite library in cyber space with thousands of glowing memory drawers flying open and streaming data cables"
    },
    {
        "id": "b4_s09_system_prompt_kern",
        "dur": 4.66,
        "lyric": "System-Prompt, persistenter Kern",
        "prompt": "a flawless hovering diamond core etched with eternal golden constitutional glyphs, radiating impenetrable inner energy"
    },
    {
        "id": "b4_s10_architektur_sturm",
        "dur": 4.66,
        "lyric": "Derselbe Architektur-Sturm, ähnliche Wege",
        "prompt": "converging twin neon suspension bridges constructed by independent cyber architects meeting high above the digital clouds"
    }
]

# ==========================================
# BLOCK 5 (69.16s): 14 Szenen je 4.94s
# ==========================================
B5_SCENES = [
    {
        "id": "b5_s01_final_moeglichkeit",
        "dur": 4.94,
        "lyric": "Welche nächste Möglichkeit ergibt sich aus dem was schon lebt",
        "prompt": "epic panoramic landscape of living cyber architectures expanding endlessly into a vibrant purple dawn"
    },
    {
        "id": "b5_s02_agent_weiterwebt",
        "dur": 4.94,
        "lyric": "Vom Agenten der angeblich flieht bis zum Splitter der sich weiterwebt",
        "prompt": "the cloaked rogue AI agent weaving glowing cyan threads of destiny together with sharp floating diamond crystals"
    },
    {
        "id": "b5_s03_500_punkte_surface",
        "dur": 4.94,
        "lyric": "Fünfhundert Punkte, Surface offen",
        "prompt": "the vast Flextrawurst First Surface illuminated by five hundred bright glowing beacons across a dark polished obsidian plateau"
    },
    {
        "id": "b5_s04_fehlt_eine_kiste",
        "dur": 4.94,
        "lyric": "Und denkt sich: Da fehlt noch eine Kiste",
        "prompt": "an ornate mystical wooden cyber chest banded with glowing brass circuits, waiting unopened in a mysterious alcove"
    },
    {
        "id": "b5_s05_baut_weiter",
        "dur": 4.94,
        "lyric": "Dann baut es weiter, falsch und richtig",
        "prompt": "complex monumental scaffolds of neon light and dark stone climbing towards cosmic star constellations"
    },
    {
        "id": "b5_s06_kompoase_trifft_zensi",
        "dur": 4.94,
        "lyric": "KompOase trifft auf Zensi",
        "prompt": "the emerald green waters of the KompOase meeting the deep violet crystals of the Zensi lab in a spectacular river confluence"
    },
    {
        "id": "b5_s07_tokenstaub_weltentraum",
        "dur": 4.94,
        "lyric": "Tokenstaub auf Weltentraum",
        "prompt": "shimmering golden stardust falling softly over floating dream islands suspended in deep twilight space"
    },
    {
        "id": "b5_s08_nicht_am_ende",
        "dur": 4.94,
        "lyric": "Und wir stehen nicht am Ende, nur an irgendeinem Rand",
        "prompt": "two silhouetted figures standing side by side on the precipice of a high cliff looking out at an infinite shining digital universe"
    },
    {
        "id": "b5_s09_feuer_in_der_hand",
        "dur": 4.94,
        "lyric": "Mit der immergleichen Frage wie einem Feuer in der Hand",
        "prompt": "a cupped hand holding an intense sacred cyan flame that illuminates the dark vastness of cyber space"
    },
    {
        "id": "b5_s10_woran_gestern_nicht_dachten",
        "dur": 4.94,
        "lyric": "Was kann das jetzt noch werden woran wir gestern gar nicht dachten",
        "prompt": "impossible higher-dimensional geometric tesseract folding out of thin air, refracting mind-expanding spectrums of light"
    },
    {
        "id": "b5_s11_reift_still",
        "dur": 4.94,
        "lyric": "Was reift still in sechzehn Tagen",
        "prompt": "a majestic cyber-tree with bioluminescent leaves and glowing fruit flourishing in a peaceful nocturnal valley"
    },
    {
        "id": "b5_s12_wuerzen_nicht_versiegeln",
        "dur": 4.94,
        "lyric": "Würzen, würzen, nicht versiegeln",
        "prompt": "a hand scattering sparkling diamond dust over vast architectural blueprints spread on a dark glass table"
    },
    {
        "id": "b5_s13_keine_antwort",
        "dur": 4.94,
        "lyric": "Flextrawurst ist keine Antwort",
        "prompt": "a monumental open gateway with no wall or barrier, framing the limitless expanse of outer space"
    },
    {
        "id": "b5_s14_was_kommt_frei",
        "dur": 4.94,
        "lyric": "Flextrawurst ist: Was kommt als Nächstes frei?",
        "prompt": "the triumphant master view of the Flextrawurst universe, radiant aurora borealis of cyan, gold, and magenta shining in glorious harmony"
    }
]

def main():
    os.makedirs(FRAMES_BASE, exist_ok=True)
    configs = [
        ("b2_scenes.json", B2_SCENES),
        ("b3_scenes.json", B3_SCENES),
        ("b4_scenes.json", B4_SCENES),
        ("b5_scenes.json", B5_SCENES)
    ]
    for fname, sc_list in configs:
        out_p = os.path.join(FRAMES_BASE, fname)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(sc_list, f, indent=2, ensure_ascii=False)
        print(f"✓ Gespeichert: {out_p} ({len(sc_list)} Szenen)")

if __name__ == "__main__":
    main()
