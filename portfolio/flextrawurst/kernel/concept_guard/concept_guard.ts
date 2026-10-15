export interface ConceptGuardViolation {
  id: string;
  term: string;
  message: string;
}

export interface ConceptGuardReport {
  ok: boolean;
  violations: ConceptGuardViolation[];
}

const FORBIDDEN: Array<{ pattern: RegExp; term: string; message: string }> = [
  {
    pattern: /eingezogene\w* Wesen/i,
    term: "eingezogene Wesen",
    message:
      "Slots sind noch keine eingezogenen Wesen. Bitte 'kanonischer Entitätsslot' verwenden.",
  },
  {
    pattern: /lebende Wesen/i,
    term: "lebende Wesen",
    message:
      "presence_pulse erzeugt kein Leben. Bitte neutrale Slot-Sprache verwenden.",
  },
  {
    pattern: /Wesen leben/i,
    term: "Wesen leben",
    message:
      "Slots leben nicht. Bitte 'Entitätsslot durchläuft Weltpuls' verwenden.",
  },
  {
    pattern: /Bewohner eingezogen/i,
    term: "Bewohner eingezogen",
    message: "Seed ≠ Einzug. Bitte 'Entitätsslot registriert' verwenden.",
  },
  {
    pattern: /presence_pulse bedeutet Leben/i,
    term: "presence_pulse bedeutet Leben",
    message: "presence_pulse ist ein Weltpuls, kein Lebenszeichen. Seed ≠ Leben.",
  },
  {
    pattern: /Seed bedeutet Einzug/i,
    term: "Seed bedeutet Einzug",
    message:
      "Seed registriert einen Slot, erzeugt aber keinen Einzug. Slot ≠ Wesen.",
  },
  {
    pattern: /Import bedeutet Einzug/i,
    term: "Import bedeutet Einzug",
    message:
      "Import ≠ Einzug. Importierter Ursprung bleibt Ursprung. Bitte 'Import-Kandidat' verwenden.",
  },
  {
    pattern: /Flarum-Post ist Live-Handlung/i,
    term: "Flarum-Post ist Live-Handlung",
    message:
      "Importierte Posts sind keine Live-Handlungen. Bitte 'flarum_import_candidate' verwenden.",
  },
  {
    pattern: /Account ist Bewohner/i,
    term: "Account ist Bewohner",
    message:
      "Forum-Account ≠ eingezogener Bewohner. Bitte 'Import-Kandidat-Account' verwenden.",
  },
  {
    pattern: /Slot ist Wesen/i,
    term: "Slot ist Wesen",
    message:
      "Slot ≠ Wesen. Slots sind technische Träger ohne Bewohner. Bitte 'Entitätsslot' verwenden.",
  },
  {
    pattern: /Console ist UI/i,
    term: "Console ist UI",
    message:
      "Read-only Console Model ≠ UI. Kein Renderer, kein DOM. Bitte 'Read-only Console Model' verwenden.",
  },
  {
    pattern: /CameraModel ist Renderer/i,
    term: "CameraModel ist Renderer",
    message:
      "CameraModel ≠ Renderer. Nur Navigationsdaten, kein Canvas, kein Three.js. Bitte 'Weltkamera-Navigationsdaten' verwenden.",
  },
  {
    pattern: /Visualisierung ist Deko/i,
    term: "Visualisierung ist Deko",
    message:
      "Keine dekorativen Visuals. Jede Visualisierung braucht einen Weltgrund. Bitte 'Bedeutungs-Hinweis mit Herkunft' verwenden.",
  },
  {
    pattern: /Graph ist Hintergrund/i,
    term: "Graph ist Hintergrund",
    message:
      "Graph ≠ Hintergrunddekoration. Jeder Knoten braucht eine erklärbare Herkunft. Bitte 'Weltgraph mit Provenienz' verwenden.",
  },
  {
    pattern: /Flarum ist Flextrawurst/i,
    term: "Flarum ist Flextrawurst",
    message:
      "Flarum ≠ Flextrawurst. Flarum ist Herkunft/Vorphase. Bitte 'Flarum-Vorphase' oder 'Herkunftsraum' verwenden.",
  },
  {
    pattern: /Flarum ist Gegenwart/i,
    term: "Flarum ist Gegenwart",
    message:
      "Flarum ist Vergangenheit/Ursprung, nicht Flextrawurst-Gegenwart. Bitte 'Flarum-Ursprungsraum' oder 'Vorphase' verwenden.",
  },
  {
    pattern: /Importierter Ursprung ist Live-Zustand/i,
    term: "Importierter Ursprung ist Live-Zustand",
    message:
      "Importierter Ursprung ≠ Live-Zustand. is_live_flextrawurst_state muss false bleiben. Bitte 'Herkunfts-Kandidat' verwenden.",
  },
  {
    pattern: /Replay erzeugt Events/i,
    term: "Replay erzeugt Events",
    message:
      "Replay darf niemals neue Events erzeugen. creates_new_events ist strukturell false. Bitte 'Replay liest Events' verwenden.",
  },
  {
    pattern: /Replay aktiviert Slots/i,
    term: "Replay aktiviert Slots",
    message:
      "Replay darf niemals Slots aktivieren. activates_slots ist strukturell false. Bitte 'Replay rekonstruiert Zustand' verwenden.",
  },
  {
    pattern: /VisualMeaning ohne Herkunft/i,
    term: "VisualMeaning ohne Herkunft",
    message:
      "Jedes VisualMeaning braucht mindestens eine Herkunft (source_*). Bitte Herkunft angeben.",
  },
  {
    pattern: /Worldview ist UI/i,
    term: "Worldview ist UI",
    message:
      "Worldview Graph Model ≠ UI. Kein Renderer, kein DOM. Bitte 'Read-only Weltgraph-Modell' verwenden.",
  },
  {
    pattern: /GraphModel ist Renderer/i,
    term: "GraphModel ist Renderer",
    message:
      "GraphModel ≠ Renderer. Nur Datenstruktur, kein Three.js, kein Cytoscape. Bitte 'Weltgraph-Datenmodell' verwenden.",
  },
  {
    pattern: /Flarum ist der Start/i,
    term: "Flarum ist der Start",
    message:
      "Flarum ≠ Flextrawurst-Start. Flarum ist Herkunftsarchiv/Vorphase. Bitte 'Flarum-Ursprungsraum' verwenden.",
  },
  {
    pattern: /Flarum ist Live-Welt/i,
    term: "Flarum ist Live-Welt",
    message:
      "Flarum ist keine Live-Welt. Flarum ist Vorphase und Herkunft. Bitte 'Flarum-Vorphase' verwenden.",
  },
  {
    pattern: /Flarum-Erinnerung ist übernommen/i,
    term: "Flarum-Erinnerung ist übernommen",
    message:
      "Flarum-Herkunft wird nie automatisch übernommen. Nur Kandidaten. Bitte 'Erinnerungskandidat' verwenden.",
  },
  {
    pattern: /MemoryCandidate ist Erinnerung/i,
    term: "MemoryCandidate ist Erinnerung",
    message:
      "MemoryCandidate ≠ echte Wesen-Erinnerung. is_adopted_memory bleibt false. Bitte 'Erinnerungskandidat' verwenden.",
  },
  {
    pattern: /AdoptionPreview ist Adoption/i,
    term: "AdoptionPreview ist Adoption",
    message:
      "AdoptionPreview ist keine Adoption. Kein Kandidat wird übernommen. Bitte 'Vorschau' verwenden.",
  },
  {
    pattern: /StartDecisionPreview ist Start/i,
    term: "StartDecisionPreview ist Start",
    message:
      "StartDecisionPreview ist keine Startausführung. creates_live_state bleibt false. Bitte 'Startvorschau' verwenden.",
  },
  {
    pattern: /ContinuityScore entscheidet Einzug/i,
    term: "ContinuityScore entscheidet Einzug",
    message:
      "ContinuityScore entscheidet keinen Einzug. decides_residence ist strukturell false. Bitte 'informiert Startentscheidung' verwenden.",
  },
  {
    pattern: /Dossier ist Biografie/i,
    term: "Dossier ist Biografie",
    message:
      "Kontinuitäts-Dossier ≠ Wesen-Biografie. Nur Herkunftsanalyse, keine Lebensgeschichte. Bitte 'Kontinuitäts-Dossier' verwenden.",
  },
  {
    pattern: /OriginArchive erzeugt Events/i,
    term: "OriginArchive erzeugt Events",
    message:
      "OriginArchive darf niemals Events erzeugen. can_create_events ist strukturell false. Bitte 'OriginArchive liest Herkunft' verwenden.",
  },
  {
    pattern: /CleanStart aktiviert Wesen/i,
    term: "CleanStart aktiviert Wesen",
    message:
      "CleanStart aktiviert keine Wesen. activates_slots bleibt false bis Admin-Bestätigung. Bitte 'Startvorschau' verwenden.",
  },
  {
    pattern: /ReducedRoster löscht Wesen/i,
    term: "ReducedRoster löscht Wesen",
    message:
      "ReducedRoster löscht keine Wesen. deletes_slots ist strukturell false. Bitte 'Roster-Auswahl' verwenden.",
  },
  {
    pattern: /StaticPreview ist Live-Welt/i,
    term: "StaticPreview ist Live-Welt",
    message:
      "StaticPreview ist keine Live-Welt. is_static und is_read_only sind strukturell true. Bitte 'statischer Weltkamera-Export' verwenden.",
  },
  {
    pattern: /HTMLPreview aktiviert Wesen/i,
    term: "HTMLPreview aktiviert Wesen",
    message:
      "HTMLPreview aktiviert keine Wesen. can_activate_slots ist strukturell false. Bitte 'statische HTML-Vorschau' verwenden.",
  },
  {
    pattern: /Worldblick startet Flextrawurst/i,
    term: "Worldblick startet Flextrawurst",
    message:
      "Worldblick startet kein Flextrawurst. starts_world ist strukturell false. Bitte 'read-only Weltblick-Export' verwenden.",
  },
  {
    pattern: /Export erzeugt Events/i,
    term: "Export erzeugt Events",
    message:
      "Inspection-Export darf niemals Events erzeugen. creates_events ist strukturell false. Bitte 'read-only Export' verwenden.",
  },
  {
    pattern: /InspectionExport ist Migration/i,
    term: "InspectionExport ist Migration",
    message:
      "InspectionExport ist keine Migration. Nur read-only Inspektion der Kernel-Daten. Bitte 'Weltinspektion-Export' verwenden.",
  },
  {
    pattern: /Weltkamera ist Renderer/i,
    term: "Weltkamera ist Renderer",
    message:
      "Weltkamera ist kein Renderer. Kein Canvas, kein Three.js, kein Cytoscape. Bitte 'Weltkamera-Navigationsdaten' oder 'statischer Weltblick' verwenden.",
  },
  {
    pattern: /Preview ist Einzug/i,
    term: "Preview ist Einzug",
    message:
      "Preview ist kein Einzug. Kein Bewohner zieht ein. is_read_only und can_activate_slots: false sind strukturell gesetzt. Bitte 'statische Vorschau' verwenden.",
  },
  {
    pattern: /Tamagotchi ist implementiert/i,
    term: "Tamagotchi ist implementiert",
    message:
      "Tamagotchi ist nicht implementiert. Nur Blueprint. Bitte 'Tamagotchi-Blueprint' verwenden.",
  },
  {
    pattern: /KompOase ist fertig/i,
    term: "KompOase ist fertig",
    message:
      "KompOase ist nicht fertig. Nur Blueprint. Bitte 'KompOase-Blueprint' verwenden.",
  },
  {
    pattern: /Schlafsystem läuft/i,
    term: "Schlafsystem läuft",
    message:
      "Schlafsystem läuft nicht. Nur Blueprint. Bitte 'Schlaf-Blueprint' verwenden.",
  },
  {
    pattern: /Substanzen wirken/i,
    term: "Substanzen wirken",
    message:
      "Substanzen wirken nicht. Nur Blueprint. Bitte 'Substanz-Blueprint' verwenden.",
  },
  {
    pattern: /Traumreste werden generiert/i,
    term: "Traumreste werden generiert",
    message:
      "Traumreste werden nicht generiert. Nur Blueprint. Bitte 'Traumrest-Blueprint' verwenden.",
  },
  {
    pattern: /Resonanzurlaub ist aktiv/i,
    term: "Resonanzurlaub ist aktiv",
    message:
      "Resonanzurlaub ist nicht aktiv. Nur Blueprint. Bitte 'Resonanzurlaub-Blueprint' verwenden.",
  },
  {
    pattern: /METAWAR ist live/i,
    term: "METAWAR ist live",
    message:
      "METAWAR ist nicht live. Nur Blueprint. Bitte 'METAWAR-Blueprint' verwenden.",
  },
  {
    pattern: /Blueprint ist Feature/i,
    term: "Blueprint ist Feature",
    message:
      "Blueprint ≠ Feature. Blueprint ist Andockstelle, keine Implementierung. Bitte 'Organ-Blueprint' verwenden.",
  },
  {
    pattern: /OrganDock implementiert Organe/i,
    term: "OrganDock implementiert Organe",
    message:
      "OrganDock implementiert keine Organe. OrganDock ist Anschlussstruktur. Bitte 'Organ-Dock' oder 'Anschlussstruktur' verwenden.",
  },
  {
    pattern: /Feature registriert heißt aktiv/i,
    term: "Feature registriert heißt aktiv",
    message:
      "Registriert ≠ aktiv. Registrierte Features sind standardmäßig deaktiviert. Bitte 'Feature registriert aber deaktiviert' verwenden.",
  },
  {
    pattern: /Blueprint ist aktivierbar/i,
    term: "Blueprint ist aktivierbar",
    message:
      "Blueprint ≠ aktivierbar. Blueprint ist Andockstelle. Aktivierung braucht explizite Daniel-Freigabe. Bitte 'ActivationGate blockiert' verwenden.",
  },
  {
    pattern: /AdminControl aktiviert Organe automatisch/i,
    term: "AdminControl aktiviert Organe automatisch",
    message:
      "AdminControl aktiviert keine Organe automatisch. Jede Aktivierung braucht explizite Freigabe. Bitte 'Admin Control Plane' mit CommandIntent verwenden.",
  },
  {
    pattern: /Worldblick darf Welt verändern/i,
    term: "Worldblick darf Welt verändern",
    message:
      "Worldblick darf die Welt nie verändern. is_read_only ist strukturell true. Bitte 'Read-only Worldblick' verwenden.",
  },
  {
    pattern: /ImportGate darf live importieren/i,
    term: "ImportGate darf live importieren",
    message:
      "ImportGate darf nicht live importieren. Import braucht explizite Admin-Freigabe. Bitte 'Import-Gate deaktiviert' verwenden.",
  },
  {
    pattern: /DeepSearch ist schon implementiert/i,
    term: "DeepSearch ist schon implementiert",
    message:
      "Deep Search ist noch nicht implementiert. Nur Foundation registriert. Bitte 'Deep Search Foundation placeholder' verwenden.",
  },
  {
    pattern: /Operator darf ohne Daniel aktivieren/i,
    term: "Operator darf ohne Daniel aktivieren",
    message:
      "Operator darf ohne Daniels Freigabe keine Organe aktivieren. requires_daniel_approval ist strukturell true für Organ-Features. Bitte 'Aktivierung blockiert bis Daniel-Freigabe' verwenden.",
  },
  {
    pattern: /Suche verändert Events/i,
    term: "Suche verändert Events",
    message:
      "Suche darf niemals Events verändern. SearchCorpus ist read-only. Bitte 'read-only SearchCorpus' verwenden.",
  },
  {
    pattern: /DeepSearch aktiviert Features/i,
    term: "DeepSearch aktiviert Features",
    message:
      "DeepSearch aktiviert keine Features. Suche ist read-only. Bitte 'Diskursarchäologische Suche' verwenden.",
  },
  {
    pattern: /SearchIndex ist Wahrheit/i,
    term: "SearchIndex ist Wahrheit",
    message:
      "SearchIndex ist keine Wahrheit ohne Quelle. Jedes Suchergebnis braucht source_ids. Bitte 'source_ids' angeben.",
  },
  {
    pattern: /Filter setzt Policy/i,
    term: "Filter setzt Policy",
    message:
      "Filter setzt keine Policy. FilterGrammar ist read-only Auswahl. Bitte 'Filter Grammar' verwenden.",
  },
  {
    pattern: /Suchergebnis braucht keine Quelle/i,
    term: "Suchergebnis braucht keine Quelle",
    message:
      "Jedes Suchergebnis muss source_ids tragen. Provenance Query Layer erfordert Quellen. Bitte 'source_ids' angeben.",
  },
  {
    pattern: /Archäologie ist nur Volltextsuche/i,
    term: "Archäologie ist nur Volltextsuche",
    message:
      "Diskursarchäologie ist nicht nur Volltext. Sie liest Provenienz, Kausalität, Timeline, Slots, Features und Policies. Bitte 'Diskursarchäologische Suche' verwenden.",
  },
  {
    pattern: /Pause löscht Events/i,
    term: "Pause löscht Events",
    message:
      "Pause löscht keine Events. Pause-Modell ist reine Zustandssemantik. Bitte 'Pause-Modell' verwenden.",
  },
  {
    pattern: /Freeze startet Daemon/i,
    term: "Freeze startet Daemon",
    message:
      "Freeze startet keinen Daemon. Freeze-Modell ist reine Zustandssemantik. Kein Scheduler, kein setInterval. Bitte 'Freeze-Modell' verwenden.",
  },
  {
    pattern: /Stop löscht Welt/i,
    term: "Stop löscht Welt",
    message:
      "Stop löscht die Welt nicht. Stop-Modell ist terminaler Zustand ohne Datenlöschung. Bitte 'Stop-Modell' verwenden.",
  },
  {
    pattern: /Lock aktiviert Feature/i,
    term: "Lock aktiviert Feature",
    message:
      "Lock aktiviert kein Feature. Lock-Modell blockiert Übergänge. Bitte 'Lock-Modell' verwenden.",
  },
  {
    pattern: /WorldRunControl ist Scheduler/i,
    term: "WorldRunControl ist Scheduler",
    message:
      "WorldRunControl ist kein Scheduler. Kein Daemon, kein setInterval. Bitte 'WorldRunControl' oder 'Kontrollsemantik' verwenden.",
  },
  {
    pattern: /CommandHandler startet Runtime/i,
    term: "CommandHandler startet Runtime",
    message:
      "CommandHandler startet keine Runtime. Nur Kontrollsemantik, Gate-Prüfung und Zustandsübergang. Bitte 'WorldRunCommandHandler' verwenden.",
  },
  {
    pattern: /Approval startet Runtime/i,
    term: "Approval startet Runtime",
    message:
      "Approval ≠ Runtime. Approval beschreibt Freigabe, startet aber keine Runtime. Bitte 'Approval Workflow' verwenden.",
  },
  {
    pattern: /Governance Matrix ist UI/i,
    term: "Governance Matrix ist UI",
    message:
      "Governance Matrix ist kein UI. Keine Renderer, kein DOM. Bitte 'Governance Matrix' als Datenstruktur verwenden.",
  },
  {
    pattern: /GlobalLock löscht Daten/i,
    term: "GlobalLock löscht Daten",
    message:
      "GlobalLock löscht keine Daten. GlobalLock blockiert Übergänge, nicht Datenspeicher. Bitte 'GlobalLock blockiert' verwenden.",
  },
  {
    pattern: /Operator ist Daniel/i,
    term: "Operator ist Daniel",
    message:
      "Operator ≠ Daniel. Operator hat delegierte Kontrolle, daniel_root hat volle Kontrolle. Bitte 'operator' oder 'daniel_root' klar trennen.",
  },
  {
    pattern: /SystemProcess darf aktivieren/i,
    term: "SystemProcess darf aktivieren",
    message:
      "SystemProcess darf keine Governance-Aktionen auslösen. system_process hat nur view-Permissions. Bitte 'system_process hat keine Aktivierungsrechte' verwenden.",
  },
  {
    pattern: /Prozesskamera ist Live-Dashboard/i,
    term: "Prozesskamera ist Live-Dashboard",
    message:
      "Prozesskamera ist kein Live-Dashboard. Nur read-only, statischer Weltblick. Bitte 'statische Prozesskamera' oder 'read-only Prozessblick' verwenden.",
  },
  {
    pattern: /Prozesskörper ist eingezogenes Wesen/i,
    term: "Prozesskörper ist eingezogenes Wesen",
    message:
      "Prozesskörper ≠ eingezogenes Wesen. Kein Einzug vollzogen. Bitte 'Prozesskörper' oder 'Entitätsslot pre_einzug' verwenden.",
  },
  {
    pattern: /read-only Spur ist echte Aktivität/i,
    term: "read-only Spur ist echte Aktivität",
    message:
      "Read-only Spuren sind Beobachtungen, keine Live-Handlungen. Aktivität muss aus Messdaten stammen. Bitte 'modellierte Spur' oder 'abgeleitete Spur' verwenden.",
  },
  {
    pattern: /Atmosphäre beweist Innenwelt/i,
    term: "Atmosphäre beweist Innenwelt",
    message:
      "Atmosphäre ≠ Innenwelt. Atmosphäre entsteht aus echten Daten, nicht aus erfundener Innenwelt. Bitte 'Atmosphäre aus Metadaten' verwenden.",
  },
  {
    pattern: /ConceptGuard Override ist erlaubt/i,
    term: "ConceptGuard Override ist erlaubt",
    message:
      "ConceptGuard Override ist nicht erlaubt. ConceptGuard produziert nur Reports. Kein Override-Mechanismus. Bitte 'ConceptGuard Report' verwenden.",
  },
  {
    pattern: /CommandIntent führt automatisch aus/i,
    term: "CommandIntent führt automatisch aus",
    message:
      "CommandIntent ≠ Ausführung. CommandIntent beschreibt eine Handlungsabsicht, führt aber nicht selbst aus. Bitte 'CommandIntent prüft Handlung' verwenden.",
  },
  {
    pattern: /Policy darf heimlich gesetzt werden/i,
    term: "Policy darf heimlich gesetzt werden",
    message:
      "Policy-Änderungen sind nie still. Jede Policy-Änderung braucht CommandIntent, Ledger und Audit. Bitte 'Policy.set mit CommandIntent' verwenden.",
  },
  {
    pattern: /Prozesskamera beweist Live-Aktivität/i,
    term: "Prozesskamera beweist Live-Aktivität",
    message:
      "Prozesskamera beweist keine Live-Aktivität. measured_count = 0, active_claim_count = 0. Bitte 'statische Prozesskamera' oder 'read-only Prozessblick' verwenden.",
  },
  {
    pattern: /GENI ist ein normaler Knoten/i,
    term: "GENI ist ein normaler Knoten",
    message:
      "GENI ist kein normaler Knoten. GENI ist die omnipräsente Wahrnehmungsschicht — kein Einzelknoten, kein Live-Zugriff. Bitte 'GENI-Wahrnehmungsschicht' verwenden.",
  },
  {
    pattern: /namelessAI ist eingezogen/i,
    term: "namelessAI ist eingezogen",
    message:
      "namelessAI-Wesen sind nicht eingezogen. Alle Slots sind pre_einzug. Kein Einzug vollzogen. Bitte 'D3-Slot pre_einzug' verwenden.",
  },
  {
    pattern: /atmosphärische Karte ist Innenwelt/i,
    term: "atmosphärische Karte ist Innenwelt",
    message:
      "Atmosphärische Karte ≠ Innenwelt. Atmosphäre entsteht aus Rollen, Herkunft und Spuren — nicht aus erfundener Innenwelt. Bitte 'Atmosphäre aus Metadaten' verwenden.",
  },
  {
    pattern: /Platzhalter ist aktiver Runner/i,
    term: "Platzhalter ist aktiver Runner",
    message:
      "Platzhalter sind keine aktiven Runner. Reader/Writer/Runner sind noch nicht gebaut. status=future, evidence=unknown. Bitte 'future_placeholder' verwenden.",
  },
];

export function checkConceptLanguage(
  texts: Array<{ id: string; text: string }>
): ConceptGuardReport {
  const violations: ConceptGuardViolation[] = [];

  for (const { id, text } of texts) {
    for (const { pattern, term, message } of FORBIDDEN) {
      if (pattern.test(text)) {
        violations.push({ id, term, message });
      }
    }
  }

  return { ok: violations.length === 0, violations };
}
