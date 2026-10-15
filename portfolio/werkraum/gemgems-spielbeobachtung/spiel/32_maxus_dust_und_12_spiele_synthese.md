# MAXUS, DUST & 12-Spiele Synthese (Achse 4: Design-Ontologie & Questkosmos)

**Analyst:** Research Subagent (Achse 4: MAXUS, DUST & 12-Spiele Synthese-Prospektor)  
**Empfänger:** Parent Agent (`039137f2-edaa-4845-830f-159c5c0b8e47`)  
**Untersuchte Primärquellen:**
1. `/root/werkraum/engine/flextrawurst-game/markdown_archive/v1_v22_rettungskoerper/10_CRE~1/FW-CREATOR-002__MAXUS++++++++++++++++++++_Masterauftrag_fur_Bauring_2.md`
2. `v21:docs/16_MAXUS_PLUSPLUS_MASTERPROMPT.md`
3. `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/05_VERTRAEGE_ARCHITEKTUR_UND_BAUREGELN_V13_BIS_V20/` (`03_ZWOELF_SPIELE_DURCHSETZUNG_BAURING3.md`, `05_PFLICHTFRAGEN_222_BEANTWORTET_01_Ontologie.md`)
4. `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V22/tools/build_v22_questkosmos.py`

---

## 1. MAXUS_DUST_VERTRAG & MAXUS++ Masterprompt

### Architektur & Verträge
- **MAXUS / MAXUS+ / MAXUS++ Masterprompts**:
  - Pfad: `/root/werkraum/engine/flextrawurst-game/markdown_archive/v1_v22_rettungskoerper/10_CRE~1/FW-CREATOR-002__MAXUS++++++++++++++++++++_Masterauftrag_fur_Bauring_2.md`
  - Quelldatei: `v21:docs/16_MAXUS_PLUSPLUS_MASTERPROMPT.md`
  - Manifest-Pfad: `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/MAXUS_DUST_VERTRAG/MANIFEST.json`
- **Kerngrundsätze von MAXUS**:
  1. **Keine bloßen UI-Behauptungen**: Flextrawurst ist eine eigenständige räumliche Lebenswelt, kein statisches Kartenspiel.
  2. **18 Pflichtfragen pro System**: Jedes neue System muss vor Code-Erstellung 18 verbindliche Pflichtfragen (Quellenstatus, Herkunft, Spielerhandlung, Ort, Sofort-Signatur, Spätfolge, Missbrauchsweg, Anti-Grind, Playwright-Testbarkeit) beantworten.
  3. **Strict Redteaming**: Vor der Freigabe eines Bauringes muss das Redteam reale Schwachstellen finden, dokumentieren und reparieren.
  4. **Systemische Ausbaukörper**: Lebende Zeit, freiwilliges Verweilen (kein FOMO), autonome Weltereignisse, Beziehungen als mehrdimensionale Geschichte, Wartung/Alterung und Sammlung ohne Besitzrecht.

---

## 2. Die 12 Vorbild-Spiele & 222 Pflichtfragen

### Die 12 Spielorgane (`03_ZWOELF_SPIELE_DURCHSETZUNG_BAURING3.md`)
Die 12 Referenzspiele werden **nicht** als Fan-Art, Kopie oder flache Zitate genutzt, sondern als **systemische Spielorgane**:
1. **Skyrim**: Handgebaute Mikroorte, Veränderungs-Erinnerung bei Rückkehr, Rollenentstehung aus Tätigkeit.
2. **Grand Theft Auto (GTA)**: Ziviler Verkehrsfluss, institutionelle Reaktionen, Infrastruktur als Wesenform mit Biografie.
3. **Minecraft**: Materialweg (Bergung, Verarbeitung, Transport, Bau, Wartung, Rückbau), räumliche Netze statt globaler Freischaltungen.
4. **Fortnite**: Unmittelbare räumliche Bedienung, dynamische Raumveränderung, frei von FOMO und Markenästhetik.
5. **Dwarf Fortress**: Ereignisgraph über alle Identitäten, Objekt- und Ortsbiografien, tiefes Vorgeschichtsregister.
6. **RimWorld**: Tiefe Bedürfnissimulation ausgewählter Akteure, ohne den Rest zu entwirklichen; Krisen und Beziehungsgeflechte.
7. **Kenshi**: Niederlage als neuer spielbarer Weltzustand (kein Game-Over-Reset), Welt entwickelt sich auch ohne Spieler.
8. **Disco Elysium**: Innere Deutungsperspektiven und Stimmen, die auch irren können; vielschichtige Aufklärung.
9. **Shadows of Doubt**: Echte Spuren konkreter Routinen, Hypothesenbildung mit Konsequenzen bei Fehlurteilen.
10. **Project Zomboid**: Körper, Versorgung, Infrastrukturbruch, Verfall, Umweltkräfte als aktive Hindernisse.
11. **No Man's Sky**: Deterministische Sektoren mit stabilen Wesenidentitäten, Entdeckungsprovenienz, mobile Traversal-Systeme.
12. **Pokémon-Community-Spiel**: Zugängliche Gemeinschaft und Feldbeobachtung **ohne** Fang-, Besitz-, Typen- oder Vollständigkeitszwang.

### Die 222 Pflichtfragen (`05_PFLICHTFRAGEN_222_BEANTWORTET.md`)
- Pfad: `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/05_VERTRAEGE_ARCHITEKTUR_UND_BAUREGELN_V13_BIS_V20/V21_05_PFLICHTFRAGEN_222_BEANTWORTET_01_Ontologie.md` u.a.
- Behandeln 222 ontologische, infrastrukturelle und architektonische Kernentscheidungen.
- Beispiel-Antworten:
  - *Q001 (Was ist ein Wesen?)*: Eine fortbestehende Identität mit Herkunft, Verkörperung, Zustandsänderung und Wirkung.
  - *Q002/Q003 (Steine/Blumen)*: Lithische Wesen speichern Wärme/Spannung/Ereignisschichten; Flora reagiert auf Pflege/Entnahme durch Bodenreaktion.
  - *Q008 (Ist 88.888 ein Sammelziel?)*: Ausdrücklich nein. Keine Rest-Anzeige, kein Vollständigkeitsbalken.

---

## 3. DUST als Weltontologie

### Das Wesen des Dusts
Dust ist die universelle physikalisch-metaphysische Substanz auf Flextrawurst, die biologische, lithische, menschliche und digitale Existenzen dauerhaft verschränkt.

### Das 88.888 Wesen-Register
Die Welt besteht nicht aus 8 benannten AI-Figuren plus Kulisse, sondern aus **exakt 88.888 deterministischen Identitäten**, aufgeteilt in 8 Körperfamilien:
- **Flora**: 22.000 (Wachstum, Bodenreaktion, Pflege-Erinnerung)
- **Lithische Wesen**: 18.000 (Wärme, Spannung, Resonanz, Geologie)
- **Fauna**: 12.000 (Bewegung, Territorium, Schwarmverhalten)
- **Menschen**: 10.000 (Haushalt, Sprache, Beziehungen, Institutionen)
- **Digitale Wesen/Systeme**: 8.888 (Modellkörper, Schnittstellen, Rechte, Verweigerung)
- **Infrastrukturwesen**: 7.000 (Wartung, Verkehrsfluss, Abhängigkeiten)
- **Dust-Hybride**: 6.000 (gemischte Herkunft, emergente Formen)
- **Wasser-/Atmosphärenkörper**: 5.000 (Strömung, Feuchte, Temperatur, Raumwirkung)

### Die 4 Simulationstiefen & Gesetze
1. **Detailkörper**: Nahbereich/aktive Interaktion, volle Zustände & Dialoge.
2. **Ereigniskörper**: Zeitgesteuert, kausal simuliert mit Bedürfnissen & Ortswechseln.
3. **Spurenkörper**: Geführt über stabile Zustandsdeltas & Provenienz; materialisiert bei Annäherung.
4. **Fernregister**: Deterministisch reproduzierbarer Bestand im Hintergrund.
- **Materialisierungsgesetz**: Stabile ID, Name, Abstammung, Sektor, Beziehungen & Narben bleiben beim Wechsel der Simulationstiefe strikt erhalten.
- **Ausdrucksgesetz**: Nicht-menschliche Wesen werden nicht vermenschlicht. Sie kommunizieren über Wachstum, Wärme, Bruch, Netzreaktion oder Spannungsänderungen.

---

## 4. Der v22 Questkosmos (111.111 Questkeime, Generatoren & R21–R26)

### Struktur & Kennzahlen (`01_QUESTKOSMOS_GESAMTBERICHT.md`)
- **111.111 Questkeime**, gebündelt in **15.873 zusammenhängende Sieben-Akt-Ketten**:
  - *Akt 1: Echo* -> *Akt 2: Reibung* -> *Akt 3: Untersuchung* -> *Akt 4: Verzweigung* -> *Akt 5: Eskalation* -> *Akt 6: Konfrontation* -> *Akt 7: Nachleben*.
- **99 Varianten pro Quest**: 9 Spielstile × 11 Weltstörungen.
- **Doppel-Pass Auswertung**:
  - Pass 1 (ungeschärft): 10.999.989 Varianten.
  - Pass 2 (redteam-geschärft): 10.999.989 Varianten.
  - **Gesamt: 21.999.978 ausgewertete Questvarianten**.
- **Prüfsystem**: 777 Einzelfragen (37 Prüfdimensionen × 21 Fragewinkel) verdichtet zu **111 maschinenlesbaren Checks** pro Quest.
- **Redteam-Schärfung**: Reduzierte Quests mit roten Checks von 111.111 auf **0** und reine Fetch-Quests von 13.494 auf **0**.

### Generatoren & Rohinputs (R21–R26)
- **Generator-Skript**: `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V22/tools/build_v22_questkosmos.py` (1.225 Zeilen Python/NumPy code).
- **R25 (Volatile Ökonomie)**: Quests verbrauchen Geld, Material & gebundenes Kapital (Kapitalbindung, Schulden, Arbitrage, -234.814,44 max. Verlust / +888.251,12 max. Gewinn).
- **R26 (Klima & Katastrophen)**: 24h-Tageszeit, 4 Jahreszeiten, 20 Wettertypen, 16 Naturkatastrophen-Typen in 9 Phasen (von `latent` bis `verwandelte Landschaft`).

---

## 5. Synthese & Zusammenhang

- **Konzeptueller Zusammenhang**:
  - **MAXUS** liefert die unerbittliche Test- und Architekturdisziplin (18 Pflichtfragen, Anti-Grind, Save/Load-Sicherheit).
  - **DUST** stiftet die kohärente Weltontologie (88.888 Wesen in 8 Familien, 4 Simulationstiefen, Verschränkung von Natur, Technik & AI).
  - **12 Spielorgane** definieren die räumlichen und mechanischen Aktionsmuster (GTA-Traffic, Minecraft-Materialnetze, RimWorld-Krisen, Disco Elysium-Interpretation).
  - **v22 Questkosmos** ist der dynamische Motor, der aus DUST-Entitäten, Weltzeit, Klima und Ökonomie deterministisch 111.111 narrative Questkeime und 21,99 Mio. simulierte Varianten erzeugt.
