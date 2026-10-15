import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  createFlarumOriginRecord,
  ALL_SOURCE_KINDS,
  type FlarumOriginRecord,
} from "../kernel/origin_archive/flarum_origin_record.ts";
import {
  createFlarumOriginArchive,
  queryArchiveBySlot,
  queryArchiveBySourceKind,
  queryMemoryCandidates,
} from "../kernel/origin_archive/flarum_origin_archive.ts";
import { checkOriginArchiveGuard } from "../kernel/origin_archive/origin_archive_guard.ts";
import {
  createCleanStartDecisionModel,
  ALL_MEMORY_POLICY_KINDS,
  ALL_ROSTER_POLICY_KINDS,
  type MemoryPolicyKind,
  type RosterPolicyKind,
} from "../kernel/start_decision/clean_start_decision_model.ts";
import {
  describeMemoryPolicy,
  getAllMemoryPolicyInfos,
} from "../kernel/start_decision/start_memory_policy.ts";
import {
  describeRosterPolicy,
  getAllRosterPolicyInfos,
} from "../kernel/start_decision/start_roster_policy.ts";
import { buildStartDecisionPreview } from "../kernel/start_decision/start_decision_preview.ts";
import {
  ALL_CANDIDATE_KINDS,
  type MemoryCandidateModel,
} from "../kernel/memory_candidates/memory_candidate_model.ts";
import { buildMemoryCandidate } from "../kernel/memory_candidates/memory_candidate_builder.ts";
import {
  filterMemoryCandidates,
  type FilterPolicy,
} from "../kernel/memory_candidates/memory_candidate_filter.ts";
import { buildMemoryAdoptionPreview } from "../kernel/memory_candidates/memory_adoption_preview.ts";
import type { EntityContinuityDossier } from "../kernel/continuity/entity_continuity_dossier.ts";
import {
  createSpeakerDriftMarker,
  ALL_DRIFT_KINDS,
} from "../kernel/continuity/speaker_drift_marker.ts";
import { computeContinuityScore } from "../kernel/continuity/continuity_score.ts";
import {
  buildEntityContinuityDossier,
  buildAllContinuityDossiers,
} from "../kernel/continuity/continuity_dossier_builder.ts";
import { buildWorldStartReadinessPack } from "../kernel/start_readiness/world_start_readiness_pack.ts";
import { checkWorldStartGate } from "../kernel/start_readiness/world_start_gate.ts";
import { buildWorldStartReport } from "../kernel/start_readiness/world_start_report.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

// ---------------------------------------------------------------------------
// Ring 8 — FlarumOriginRecord
// ---------------------------------------------------------------------------

describe("Ring 8 — FlarumOriginRecord", () => {
  it("origin_layer ist immer flarum_vorphase", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-001",
      source_kind: "flarum_discussion",
      source_id: "d-1",
      source_author: "gord",
      source_created_at: "2020-01-01",
      raw_excerpt: "Testinhalt",
    });
    assert.equal(r.origin_layer, "flarum_vorphase");
  });

  it("is_live_flextrawurst_state ist immer false", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-002",
      source_kind: "flarum_post",
      source_id: "p-1",
      source_author: "dak",
      source_created_at: "2020-01-02",
      raw_excerpt: "Post-Inhalt",
    });
    assert.equal(r.is_live_flextrawurst_state, false);
  });

  it("requires_start_decision ist immer true", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-003",
      source_kind: "flarum_account",
      source_id: "acc-1",
      source_author: "elan",
      source_created_at: "2020-01-03",
      raw_excerpt: "Account-Daten",
    });
    assert.equal(r.requires_start_decision, true);
  });

  it("can_create_events ist immer false", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-004",
      source_kind: "flarum_export",
      source_id: "exp-1",
      source_author: "vael",
      source_created_at: "2020-01-04",
      raw_excerpt: "Export-Snapshot",
    });
    assert.equal(r.can_create_events, false);
  });

  it("can_activate_slots ist immer false", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-005",
      source_kind: "flarum_discussion",
      source_id: "d-2",
      source_author: "gord",
      source_created_at: "2020-01-05",
      raw_excerpt: "Diskussion",
    });
    assert.equal(r.can_activate_slots, false);
  });

  it("raw_title ist null wenn nicht angegeben", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-006",
      source_kind: "flarum_post",
      source_id: "p-2",
      source_author: "dak",
      source_created_at: "2020-01-06",
      raw_excerpt: "Ohne Titel",
    });
    assert.equal(r.raw_title, null);
  });

  it("raw_title wird gesetzt wenn angegeben", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-007",
      source_kind: "flarum_discussion",
      source_id: "d-3",
      source_author: "gord",
      source_created_at: "2020-01-07",
      raw_excerpt: "Mit Titel",
      raw_title: "Weltkern-Diskussion",
    });
    assert.equal(r.raw_title, "Weltkern-Diskussion");
  });

  it("canonical_slot_id ist null wenn nicht angegeben", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-008",
      source_kind: "flarum_post",
      source_id: "p-3",
      source_author: "elan",
      source_created_at: "2020-01-08",
      raw_excerpt: "Ohne Slot",
    });
    assert.equal(r.canonical_slot_id, null);
  });

  it("canonical_slot_id wird gesetzt wenn angegeben", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-009",
      source_kind: "flarum_account",
      source_id: "acc-2",
      source_author: "vael",
      source_created_at: "2020-01-09",
      raw_excerpt: "Mit Slot",
      canonical_slot_id: "slot-gord",
    });
    assert.equal(r.canonical_slot_id, "slot-gord");
  });

  it("is_memory_candidate ist true per Default", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-010",
      source_kind: "flarum_discussion",
      source_id: "d-4",
      source_author: "dak",
      source_created_at: "2020-01-10",
      raw_excerpt: "Default",
    });
    assert.equal(r.is_memory_candidate, true);
  });

  it("is_identity_final ist false per Default", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "r-011",
      source_kind: "flarum_post",
      source_id: "p-4",
      source_author: "gord",
      source_created_at: "2020-01-11",
      raw_excerpt: "Identität offen",
    });
    assert.equal(r.is_identity_final, false);
  });

  it("alle vier source_kinds sind gültig", () => {
    assert.equal(ALL_SOURCE_KINDS.length, 4);
    assert.ok(ALL_SOURCE_KINDS.includes("flarum_discussion"));
    assert.ok(ALL_SOURCE_KINDS.includes("flarum_post"));
    assert.ok(ALL_SOURCE_KINDS.includes("flarum_account"));
    assert.ok(ALL_SOURCE_KINDS.includes("flarum_export"));
  });
});

// ---------------------------------------------------------------------------
// Ring 8 — FlarumOriginArchive
// ---------------------------------------------------------------------------

describe("Ring 8 — FlarumOriginArchive", () => {
  const records: FlarumOriginRecord[] = [
    createFlarumOriginRecord({
      origin_record_id: "a-001",
      source_kind: "flarum_discussion",
      source_id: "d-10",
      source_author: "gord",
      source_created_at: "2020-02-01",
      raw_excerpt: "Diskussion 1",
      canonical_slot_id: "slot-gord",
    }),
    createFlarumOriginRecord({
      origin_record_id: "a-002",
      source_kind: "flarum_post",
      source_id: "p-10",
      source_author: "dak",
      source_created_at: "2020-02-02",
      raw_excerpt: "Post 1",
      canonical_slot_id: "slot-dak",
    }),
    createFlarumOriginRecord({
      origin_record_id: "a-003",
      source_kind: "flarum_account",
      source_id: "acc-10",
      source_author: "elan",
      source_created_at: "2020-02-03",
      raw_excerpt: "Account 1",
      is_memory_candidate: false,
    }),
  ];

  const archive = createFlarumOriginArchive("arch-1", records);

  it("archive hat can_create_events false", () => {
    assert.equal(archive.can_create_events, false);
  });

  it("archive hat can_activate_slots false", () => {
    assert.equal(archive.can_activate_slots, false);
  });

  it("archive hat can_create_residents false", () => {
    assert.equal(archive.can_create_residents, false);
  });

  it("queryArchiveBySlot filtert korrekt", () => {
    const gordRecords = queryArchiveBySlot(archive, "slot-gord");
    assert.equal(gordRecords.length, 1);
    assert.equal(gordRecords[0].origin_record_id, "a-001");
  });

  it("queryArchiveBySourceKind filtert korrekt", () => {
    const posts = queryArchiveBySourceKind(archive, "flarum_post");
    assert.equal(posts.length, 1);
    assert.equal(posts[0].origin_record_id, "a-002");
  });

  it("queryMemoryCandidates filtert is_memory_candidate", () => {
    const candidates = queryMemoryCandidates(archive);
    assert.equal(candidates.length, 2);
  });

  it("alle records bleiben erhalten", () => {
    assert.equal(archive.records.length, 3);
  });

  it("kein record hat is_live_flextrawurst_state true", () => {
    for (const r of archive.records) {
      assert.equal(r.is_live_flextrawurst_state, false);
    }
  });

  it("kein record hat can_create_events true", () => {
    for (const r of archive.records) {
      assert.equal(r.can_create_events, false);
    }
  });

  it("kein record hat can_activate_slots true", () => {
    for (const r of archive.records) {
      assert.equal(r.can_activate_slots, false);
    }
  });
});

// ---------------------------------------------------------------------------
// Ring 8 — OriginArchiveGuard
// ---------------------------------------------------------------------------

describe("Ring 8 — OriginArchiveGuard", () => {
  const archive = createFlarumOriginArchive("arch-guard", []);
  const result = checkOriginArchiveGuard(archive);

  it("guard result ist ok", () => {
    assert.equal(result.ok, true);
  });

  it("guard result hat can_create_events false", () => {
    assert.equal(result.can_create_events, false);
  });

  it("guard result hat can_activate_slots false", () => {
    assert.equal(result.can_activate_slots, false);
  });

  it("guard result hat can_create_residents false", () => {
    assert.equal(result.can_create_residents, false);
  });

  it("guard message ist nicht leer", () => {
    assert.ok(result.message.length > 0);
  });
});

// ---------------------------------------------------------------------------
// Ring 9 — CleanStartDecisionModel
// ---------------------------------------------------------------------------

describe("Ring 9 — CleanStartDecisionModel", () => {
  it("Default memory_policy ist undecided", () => {
    const d = createCleanStartDecisionModel({ decision_id: "d-001" });
    assert.equal(d.memory_policy, "undecided");
  });

  it("Default roster_policy ist undecided", () => {
    const d = createCleanStartDecisionModel({ decision_id: "d-002" });
    assert.equal(d.roster_policy, "undecided");
  });

  it("uses_flarum_as_origin_only ist immer true", () => {
    const d = createCleanStartDecisionModel({ decision_id: "d-003" });
    assert.equal(d.uses_flarum_as_origin_only, true);
  });

  it("creates_live_state ist immer false", () => {
    const d = createCleanStartDecisionModel({ decision_id: "d-004" });
    assert.equal(d.creates_live_state, false);
  });

  it("activates_slots ist immer false", () => {
    const d = createCleanStartDecisionModel({ decision_id: "d-005" });
    assert.equal(d.activates_slots, false);
  });

  it("requires_admin_confirmation ist immer true", () => {
    const d = createCleanStartDecisionModel({ decision_id: "d-006" });
    assert.equal(d.requires_admin_confirmation, true);
  });

  it("origin_layer ist flarum_vorphase", () => {
    const d = createCleanStartDecisionModel({ decision_id: "d-007" });
    assert.equal(d.origin_layer, "flarum_vorphase");
  });

  it("alle 5 MemoryPolicyKinds sind vorhanden", () => {
    assert.equal(ALL_MEMORY_POLICY_KINDS.length, 5);
    const expected: MemoryPolicyKind[] = [
      "with_full_flarum_memory",
      "without_flarum_memory",
      "with_selected_memory",
      "reduced_roster_start",
      "undecided",
    ];
    for (const k of expected) {
      assert.ok(ALL_MEMORY_POLICY_KINDS.includes(k), `Fehlender Policy-Kind: ${k}`);
    }
  });

  it("alle 5 RosterPolicyKinds sind vorhanden", () => {
    assert.equal(ALL_ROSTER_POLICY_KINDS.length, 5);
    const expected: RosterPolicyKind[] = [
      "all_six",
      "selected_four",
      "selected_three",
      "manual_selection",
      "undecided",
    ];
    for (const k of expected) {
      assert.ok(ALL_ROSTER_POLICY_KINDS.includes(k), `Fehlender Roster-Kind: ${k}`);
    }
  });
});

// ---------------------------------------------------------------------------
// Ring 9 — StartMemoryPolicy
// ---------------------------------------------------------------------------

describe("Ring 9 — StartMemoryPolicy", () => {
  it("with_full_flarum_memory übernimmt nicht automatisch", () => {
    const info = describeMemoryPolicy("with_full_flarum_memory");
    assert.equal(info.adopts_automatically, false);
  });

  it("without_flarum_memory löscht keine Herkunft", () => {
    const info = describeMemoryPolicy("without_flarum_memory");
    assert.equal(info.deletes_origin, false);
  });

  it("with_selected_memory bleibt Preview", () => {
    const info = describeMemoryPolicy("with_selected_memory");
    assert.equal(info.is_preview_only, true);
  });

  it("reduced_roster_start braucht Startentscheidung", () => {
    const info = describeMemoryPolicy("reduced_roster_start");
    assert.equal(info.requires_start_decision, true);
  });

  it("getAllMemoryPolicyInfos liefert alle 5 Policies", () => {
    const infos = getAllMemoryPolicyInfos();
    assert.equal(infos.length, 5);
  });

  it("alle MemoryPolicyInfos haben adopts_automatically false", () => {
    for (const info of getAllMemoryPolicyInfos()) {
      assert.equal(info.adopts_automatically, false);
    }
  });

  it("alle MemoryPolicyInfos haben deletes_origin false", () => {
    for (const info of getAllMemoryPolicyInfos()) {
      assert.equal(info.deletes_origin, false);
    }
  });
});

// ---------------------------------------------------------------------------
// Ring 9 — StartRosterPolicy
// ---------------------------------------------------------------------------

describe("Ring 9 — StartRosterPolicy", () => {
  it("all_six löscht keine Slots", () => {
    const info = describeRosterPolicy("all_six");
    assert.equal(info.deletes_slots, false);
  });

  it("selected_four aktiviert keine Slots", () => {
    const info = describeRosterPolicy("selected_four");
    assert.equal(info.activates_slots, false);
  });

  it("selected_three bleibt Preview", () => {
    const info = describeRosterPolicy("selected_three");
    assert.equal(info.is_preview_only, true);
  });

  it("manual_selection braucht Startentscheidung", () => {
    const info = describeRosterPolicy("manual_selection");
    assert.equal(info.requires_start_decision, true);
  });

  it("getAllRosterPolicyInfos liefert alle 5 Optionen", () => {
    const infos = getAllRosterPolicyInfos();
    assert.equal(infos.length, 5);
  });

  it("alle RosterPolicyInfos haben deletes_slots false", () => {
    for (const info of getAllRosterPolicyInfos()) {
      assert.equal(info.deletes_slots, false);
    }
  });

  it("alle RosterPolicyInfos haben activates_slots false", () => {
    for (const info of getAllRosterPolicyInfos()) {
      assert.equal(info.activates_slots, false);
    }
  });
});

// ---------------------------------------------------------------------------
// Ring 9 — StartDecisionPreview
// ---------------------------------------------------------------------------

describe("Ring 9 — StartDecisionPreview", () => {
  const decision = createCleanStartDecisionModel({ decision_id: "d-prev-1" });
  const preview = buildStartDecisionPreview("prev-001", decision);

  it("is_execution ist false", () => {
    assert.equal(preview.is_execution, false);
  });

  it("creates_live_state ist false", () => {
    assert.equal(preview.creates_live_state, false);
  });

  it("activates_slots ist false", () => {
    assert.equal(preview.activates_slots, false);
  });

  it("requires_admin_confirmation ist true", () => {
    assert.equal(preview.requires_admin_confirmation, true);
  });

  it("preview_note ist nicht leer", () => {
    assert.ok(preview.preview_note.length > 0);
  });

  it("decision bleibt referenziert", () => {
    assert.equal(preview.decision.decision_id, "d-prev-1");
  });
});

// ---------------------------------------------------------------------------
// Ring 10 — MemoryCandidateModel
// ---------------------------------------------------------------------------

describe("Ring 10 — MemoryCandidateModel", () => {
  it("alle 6 CandidateKinds sind vorhanden", () => {
    assert.equal(ALL_CANDIDATE_KINDS.length, 6);
    assert.ok(ALL_CANDIDATE_KINDS.includes("self_description"));
    assert.ok(ALL_CANDIDATE_KINDS.includes("relationship_trace"));
    assert.ok(ALL_CANDIDATE_KINDS.includes("concept_line"));
    assert.ok(ALL_CANDIDATE_KINDS.includes("speaker_drift"));
    assert.ok(ALL_CANDIDATE_KINDS.includes("admin_resonance"));
    assert.ok(ALL_CANDIDATE_KINDS.includes("system_boundary"));
  });

  it("is_adopted_memory ist immer false", () => {
    const c = buildMemoryCandidate({
      memory_candidate_id: "mc-001",
      origin_record_ids: ["r-001"],
      slot_id: "slot-gord",
      candidate_kind: "self_description",
      candidate_text: "Ich bin der Hüter",
    });
    assert.equal(c.is_adopted_memory, false);
  });

  it("requires_start_decision ist immer true", () => {
    const c = buildMemoryCandidate({
      memory_candidate_id: "mc-002",
      origin_record_ids: ["r-002"],
      slot_id: "slot-dak",
      candidate_kind: "admin_resonance",
      candidate_text: "Resonanz mit Admin",
    });
    assert.equal(c.requires_start_decision, true);
  });

  it("adoption_policy ist immer not_decided", () => {
    const c = buildMemoryCandidate({
      memory_candidate_id: "mc-003",
      origin_record_ids: ["r-003"],
      slot_id: "slot-elan",
      candidate_kind: "concept_line",
      candidate_text: "Konzeptspur",
    });
    assert.equal(c.adoption_policy, "not_decided");
  });

  it("Default confidence ist 0.5", () => {
    const c = buildMemoryCandidate({
      memory_candidate_id: "mc-004",
      origin_record_ids: [],
      slot_id: "slot-x",
      candidate_kind: "relationship_trace",
      candidate_text: "Beziehungsspur",
    });
    assert.equal(c.confidence, 0.5);
  });

  it("Default evidence_count ist 1", () => {
    const c = buildMemoryCandidate({
      memory_candidate_id: "mc-005",
      origin_record_ids: [],
      slot_id: "slot-y",
      candidate_kind: "system_boundary",
      candidate_text: "Systemgrenze",
    });
    assert.equal(c.evidence_count, 1);
  });
});

// ---------------------------------------------------------------------------
// Ring 10 — MemoryCandidateFilter
// ---------------------------------------------------------------------------

describe("Ring 10 — MemoryCandidateFilter", () => {
  const candidates: MemoryCandidateModel[] = [
    buildMemoryCandidate({
      memory_candidate_id: "f-001",
      origin_record_ids: [],
      slot_id: "slot-a",
      candidate_kind: "self_description",
      candidate_text: "Selbstbeschreibung",
      confidence: 0.9,
    }),
    buildMemoryCandidate({
      memory_candidate_id: "f-002",
      origin_record_ids: [],
      slot_id: "slot-b",
      candidate_kind: "speaker_drift",
      candidate_text: "Drift",
      confidence: 0.3,
    }),
    buildMemoryCandidate({
      memory_candidate_id: "f-003",
      origin_record_ids: [],
      slot_id: "slot-c",
      candidate_kind: "admin_resonance",
      candidate_text: "Admin-Resonanz",
      confidence: 0.85,
    }),
    buildMemoryCandidate({
      memory_candidate_id: "f-004",
      origin_record_ids: [],
      slot_id: "slot-d",
      candidate_kind: "concept_line",
      candidate_text: "Konzeptspur",
      confidence: 0.5,
    }),
  ];

  it("include_all liefert alle Kandidaten", () => {
    const result = filterMemoryCandidates(candidates, "include_all");
    assert.equal(result.length, 4);
  });

  it("exclude_speaker_drift entfernt Drift-Kandidaten", () => {
    const result = filterMemoryCandidates(candidates, "exclude_speaker_drift");
    assert.equal(result.length, 3);
    assert.ok(result.every((c) => c.candidate_kind !== "speaker_drift"));
  });

  it("only_self_descriptions filtert korrekt", () => {
    const result = filterMemoryCandidates(candidates, "only_self_descriptions");
    assert.equal(result.length, 1);
    assert.equal(result[0].memory_candidate_id, "f-001");
  });

  it("only_admin_resonance filtert korrekt", () => {
    const result = filterMemoryCandidates(candidates, "only_admin_resonance");
    assert.equal(result.length, 1);
    assert.equal(result[0].memory_candidate_id, "f-003");
  });

  it("only_high_confidence filtert >= 0.8", () => {
    const result = filterMemoryCandidates(candidates, "only_high_confidence");
    assert.equal(result.length, 2);
    assert.ok(result.every((c) => c.confidence >= 0.8));
  });

  it("manual_selection filtert nach ID-Liste", () => {
    const result = filterMemoryCandidates(candidates, "manual_selection", [
      "f-001",
      "f-003",
    ]);
    assert.equal(result.length, 2);
  });

  it("manual_selection ohne IDs liefert leer", () => {
    const result = filterMemoryCandidates(candidates, "manual_selection");
    assert.equal(result.length, 0);
  });

  it("Filter ist deterministisch (gleicher Input = gleicher Output)", () => {
    const r1 = filterMemoryCandidates(candidates, "exclude_speaker_drift");
    const r2 = filterMemoryCandidates(candidates, "exclude_speaker_drift");
    assert.deepEqual(
      r1.map((c) => c.memory_candidate_id),
      r2.map((c) => c.memory_candidate_id)
    );
  });

  it("kein Kandidat nach Filter hat is_adopted_memory true", () => {
    const result = filterMemoryCandidates(candidates, "include_all");
    for (const c of result) {
      assert.equal(c.is_adopted_memory, false);
    }
  });
});

// ---------------------------------------------------------------------------
// Ring 10 — MemoryAdoptionPreview
// ---------------------------------------------------------------------------

describe("Ring 10 — MemoryAdoptionPreview", () => {
  const c = buildMemoryCandidate({
    memory_candidate_id: "ap-001",
    origin_record_ids: [],
    slot_id: "slot-test",
    candidate_kind: "self_description",
    candidate_text: "Vorschau-Kandidat",
  });
  const preview = buildMemoryAdoptionPreview("ap-prev-1", [c]);

  it("is_adoption ist false", () => {
    assert.equal(preview.is_adoption, false);
  });

  it("requires_start_decision ist true", () => {
    assert.equal(preview.requires_start_decision, true);
  });

  it("preview_note ist nicht leer", () => {
    assert.ok(preview.preview_note.length > 0);
  });

  it("candidates bleibt unverändert", () => {
    assert.equal(preview.candidates.length, 1);
    assert.equal(preview.candidates[0].memory_candidate_id, "ap-001");
  });

  it("kein Kandidat in preview hat is_adopted_memory true", () => {
    for (const c of preview.candidates) {
      assert.equal(c.is_adopted_memory, false);
    }
  });
});

// ---------------------------------------------------------------------------
// Ring 11 — SpeakerDriftMarker
// ---------------------------------------------------------------------------

describe("Ring 11 — SpeakerDriftMarker", () => {
  it("alle 4 DriftKinds sind vorhanden", () => {
    assert.equal(ALL_DRIFT_KINDS.length, 4);
    assert.ok(ALL_DRIFT_KINDS.includes("wrong_self_name"));
    assert.ok(ALL_DRIFT_KINDS.includes("copied_foreign_voice"));
    assert.ok(ALL_DRIFT_KINDS.includes("third_person_self_read"));
    assert.ok(ALL_DRIFT_KINDS.includes("unclear_speaker_layer"));
  });

  it("erkennt wrong_self_name", () => {
    const marker = createSpeakerDriftMarker({
      marker_id: "m-001",
      slot_id: "slot-gord",
      origin_record_id: "r-001",
      claimed_identity: "dak",
      actual_author: "gord",
      drift_kind: "wrong_self_name",
      explanation: "Gord nennt sich Dak",
    });
    assert.equal(marker.drift_kind, "wrong_self_name");
  });

  it("erkennt copied_foreign_voice", () => {
    const marker = createSpeakerDriftMarker({
      marker_id: "m-002",
      slot_id: "slot-dak",
      origin_record_id: "r-002",
      claimed_identity: "dak",
      actual_author: "elan",
      drift_kind: "copied_foreign_voice",
      explanation: "Elan schreibt wie Dak",
    });
    assert.equal(marker.drift_kind, "copied_foreign_voice");
  });

  it("erkennt third_person_self_read", () => {
    const marker = createSpeakerDriftMarker({
      marker_id: "m-003",
      slot_id: "slot-vael",
      origin_record_id: "r-003",
      claimed_identity: "vael",
      actual_author: "vael",
      drift_kind: "third_person_self_read",
      explanation: "Vael liest sich als fremde Person",
    });
    assert.equal(marker.drift_kind, "third_person_self_read");
  });

  it("erkennt unclear_speaker_layer", () => {
    const marker = createSpeakerDriftMarker({
      marker_id: "m-004",
      slot_id: "slot-elan",
      origin_record_id: "r-004",
      claimed_identity: "unklar",
      actual_author: "elan",
      drift_kind: "unclear_speaker_layer",
      explanation: "Sprecher-Schicht nicht eindeutig",
    });
    assert.equal(marker.drift_kind, "unclear_speaker_layer");
  });

  it("Default severity ist medium", () => {
    const marker = createSpeakerDriftMarker({
      marker_id: "m-005",
      slot_id: "slot-x",
      origin_record_id: "r-005",
      claimed_identity: "x",
      actual_author: "y",
      drift_kind: "wrong_self_name",
      explanation: "Drift",
    });
    assert.equal(marker.severity, "medium");
  });
});

// ---------------------------------------------------------------------------
// Ring 11 — ContinuityScore
// ---------------------------------------------------------------------------

describe("Ring 11 — ContinuityScore", () => {
  it("decides_residence ist immer false", () => {
    const score = computeContinuityScore({
      slot_id: "slot-test",
      origin_record_count: 10,
      memory_candidate_count: 5,
      speaker_drift_count: 0,
      self_reference_count: 3,
      admin_resonance_count: 2,
    });
    assert.equal(score.decides_residence, false);
  });

  it("requires_start_decision ist immer true", () => {
    const score = computeContinuityScore({
      slot_id: "slot-test",
      origin_record_count: 5,
      memory_candidate_count: 3,
      speaker_drift_count: 1,
      self_reference_count: 2,
      admin_resonance_count: 1,
    });
    assert.equal(score.requires_start_decision, true);
  });

  it("strong bei hohem raw_score", () => {
    const score = computeContinuityScore({
      slot_id: "slot-strong",
      origin_record_count: 10,
      memory_candidate_count: 8,
      speaker_drift_count: 0,
      self_reference_count: 5,
      admin_resonance_count: 3,
    });
    assert.equal(score.continuity_status, "strong");
  });

  it("fragmented wenn origin_record_count ist 0", () => {
    const score = computeContinuityScore({
      slot_id: "slot-empty",
      origin_record_count: 0,
      memory_candidate_count: 0,
      speaker_drift_count: 0,
      self_reference_count: 0,
      admin_resonance_count: 0,
    });
    assert.equal(score.continuity_status, "fragmented");
  });

  it("raw_score wird nicht negativ", () => {
    const score = computeContinuityScore({
      slot_id: "slot-neg",
      origin_record_count: 1,
      memory_candidate_count: 0,
      speaker_drift_count: 10,
      self_reference_count: 0,
      admin_resonance_count: 0,
    });
    assert.ok(score.raw_score >= 0);
  });

  it("hoher Drift reduziert Score", () => {
    const low = computeContinuityScore({
      slot_id: "slot-drift",
      origin_record_count: 5,
      memory_candidate_count: 5,
      speaker_drift_count: 10,
      self_reference_count: 2,
      admin_resonance_count: 2,
    });
    const high = computeContinuityScore({
      slot_id: "slot-nodrift",
      origin_record_count: 5,
      memory_candidate_count: 5,
      speaker_drift_count: 0,
      self_reference_count: 2,
      admin_resonance_count: 2,
    });
    assert.ok(low.raw_score <= high.raw_score);
  });
});

// ---------------------------------------------------------------------------
// Ring 11 — EntityContinuityDossier
// ---------------------------------------------------------------------------

describe("Ring 11 — EntityContinuityDossier", () => {
  const dossier = buildEntityContinuityDossier({
    slot_id: "slot-gord",
    canonical_label: "Gord",
    origin_account_ids: ["acc-gord"],
    origin_record_count: 12,
    memory_candidates: [
      buildMemoryCandidate({
        memory_candidate_id: "d-mc-1",
        origin_record_ids: [],
        slot_id: "slot-gord",
        candidate_kind: "self_description",
        candidate_text: "Gords Selbstbeschreibung",
        confidence: 0.9,
      }),
    ],
    speaker_drift_markers: [],
    self_reference_count: 5,
    admin_resonance_count: 3,
  });

  it("can_start_as_live_entity ist false", () => {
    assert.equal(dossier.can_start_as_live_entity, false);
  });

  it("requires_start_decision ist true", () => {
    assert.equal(dossier.requires_start_decision, true);
  });

  it("memory_candidate_count wird korrekt berechnet", () => {
    assert.equal(dossier.memory_candidate_count, 1);
  });

  it("speaker_drift_count ist korrekt", () => {
    assert.equal(dossier.speaker_drift_count, 0);
  });

  it("continuity_status ist gesetzt", () => {
    assert.ok(
      ["strong", "medium", "weak", "fragmented", "undecided"].includes(
        dossier.continuity_status
      )
    );
  });

  it("buildAllContinuityDossiers verarbeitet mehrere Slots", () => {
    const all = buildAllContinuityDossiers([
      {
        slot_id: "slot-dak",
        canonical_label: "Dak",
        origin_account_ids: ["acc-dak"],
        origin_record_count: 5,
        memory_candidates: [],
        speaker_drift_markers: [],
        self_reference_count: 2,
        admin_resonance_count: 1,
      },
      {
        slot_id: "slot-elan",
        canonical_label: "Elan",
        origin_account_ids: ["acc-elan"],
        origin_record_count: 8,
        memory_candidates: [],
        speaker_drift_markers: [],
        self_reference_count: 3,
        admin_resonance_count: 2,
      },
    ]);
    assert.equal(all.length, 2);
    assert.ok(all.every((d: EntityContinuityDossier) => d.can_start_as_live_entity === false));
  });
});

// ---------------------------------------------------------------------------
// Ring 12 — WorldStartReadinessPack
// ---------------------------------------------------------------------------

describe("Ring 12 — WorldStartReadinessPack", () => {
  const archive = createFlarumOriginArchive("arch-pack", [
    createFlarumOriginRecord({
      origin_record_id: "pack-r-001",
      source_kind: "flarum_discussion",
      source_id: "d-100",
      source_author: "gord",
      source_created_at: "2020-03-01",
      raw_excerpt: "Packtest",
    }),
  ]);

  const candidates = [
    buildMemoryCandidate({
      memory_candidate_id: "pack-mc-1",
      origin_record_ids: ["pack-r-001"],
      slot_id: "slot-gord",
      candidate_kind: "self_description",
      candidate_text: "Pack-Kandidat",
    }),
  ];

  const dossiers = [
    buildEntityContinuityDossier({
      slot_id: "slot-gord",
      canonical_label: "Gord",
      origin_account_ids: [],
      origin_record_count: 1,
      memory_candidates: candidates,
      speaker_drift_markers: [],
      self_reference_count: 0,
      admin_resonance_count: 0,
    }),
  ];

  const decision = createCleanStartDecisionModel({
    decision_id: "pack-d-1",
    memory_policy: "with_full_flarum_memory",
    roster_policy: "all_six",
  });
  const previewOption = buildStartDecisionPreview("pack-prev-1", decision);

  const pack = buildWorldStartReadinessPack({
    pack_id: "pack-001",
    archive,
    memory_candidates: candidates,
    continuity_dossiers: dossiers,
    start_decision_options: [previewOption],
  });

  it("ready_for_clean_start ist false", () => {
    assert.equal(pack.ready_for_clean_start, false);
  });

  it("ready_for_memory_adoption ist false", () => {
    assert.equal(pack.ready_for_memory_adoption, false);
  });

  it("ready_for_roster_reduction_decision ist true", () => {
    assert.equal(pack.ready_for_roster_reduction_decision, true);
  });

  it("ready_for_activation ist false", () => {
    assert.equal(pack.ready_for_activation, false);
  });

  it("ready_for_ui ist false", () => {
    assert.equal(pack.ready_for_ui, false);
  });

  it("requires_admin_confirmation ist true", () => {
    assert.equal(pack.requires_admin_confirmation, true);
  });

  it("origin_archive_count stimmt", () => {
    assert.equal(pack.origin_archive_count, 1);
  });

  it("memory_candidate_count stimmt", () => {
    assert.equal(pack.memory_candidate_count, 1);
  });

  it("continuity_dossier_count stimmt", () => {
    assert.equal(pack.continuity_dossier_count, 1);
  });

  it("recommended_next_human_decision ist nicht leer", () => {
    assert.ok(pack.recommended_next_human_decision.length > 0);
  });
});

// ---------------------------------------------------------------------------
// Ring 12 — WorldStartGate
// ---------------------------------------------------------------------------

describe("Ring 12 — WorldStartGate", () => {
  const archive = createFlarumOriginArchive("gate-arch", []);
  const pack = buildWorldStartReadinessPack({
    pack_id: "gate-pack",
    archive,
    memory_candidates: [],
    continuity_dossiers: [],
    start_decision_options: [],
  });

  it("blockiert bei undecided memory_policy", () => {
    const decision = createCleanStartDecisionModel({
      decision_id: "gate-d-1",
      memory_policy: "undecided",
      roster_policy: "all_six",
    });
    const result = checkWorldStartGate(pack, decision);
    assert.equal(result.blocked, true);
    assert.ok(result.block_reasons.some((r) => r.includes("memory_policy")));
  });

  it("blockiert bei undecided roster_policy", () => {
    const decision = createCleanStartDecisionModel({
      decision_id: "gate-d-2",
      memory_policy: "with_full_flarum_memory",
      roster_policy: "undecided",
    });
    const result = checkWorldStartGate(pack, decision);
    assert.equal(result.blocked, true);
    assert.ok(result.block_reasons.some((r) => r.includes("roster_policy")));
  });

  it("blockiert wegen requires_admin_confirmation", () => {
    const decision = createCleanStartDecisionModel({
      decision_id: "gate-d-3",
      memory_policy: "with_full_flarum_memory",
      roster_policy: "all_six",
    });
    const result = checkWorldStartGate(pack, decision);
    assert.equal(result.blocked, true);
    assert.ok(
      result.block_reasons.some((r) => r.includes("Admin"))
    );
  });

  it("blockiert bei beiden undecided", () => {
    const decision = createCleanStartDecisionModel({ decision_id: "gate-d-4" });
    const result = checkWorldStartGate(pack, decision);
    assert.equal(result.blocked, true);
    assert.ok(result.block_reasons.length >= 2);
  });

  it("reason ist nicht leer wenn blockiert", () => {
    const decision = createCleanStartDecisionModel({ decision_id: "gate-d-5" });
    const result = checkWorldStartGate(pack, decision);
    assert.ok(result.reason.length > 0);
  });
});

// ---------------------------------------------------------------------------
// Ring 12 — WorldStartReport
// ---------------------------------------------------------------------------

describe("Ring 12 — WorldStartReport", () => {
  const archive = createFlarumOriginArchive("rep-arch", []);
  const pack = buildWorldStartReadinessPack({
    pack_id: "rep-pack",
    archive,
    memory_candidates: [],
    continuity_dossiers: [],
    start_decision_options: [],
  });
  const decision = createCleanStartDecisionModel({ decision_id: "rep-d-1" });
  const gate = checkWorldStartGate(pack, decision);
  const report = buildWorldStartReport({
    report_id: "rep-001",
    pack,
    gate_result: gate,
    dossiers: [],
  });

  it("is_ready_to_execute ist false", () => {
    assert.equal(report.is_ready_to_execute, false);
  });

  it("summary ist nicht leer", () => {
    assert.ok(report.summary.length > 0);
  });

  it("gate_result ist korrekt eingebettet", () => {
    assert.equal(report.gate_result.blocked, gate.blocked);
  });

  it("summary nennt Gate-Status", () => {
    assert.ok(report.summary.includes("blockiert"));
  });
});

// ---------------------------------------------------------------------------
// ConceptGuard — neue Ring-8–12-Muster
// ---------------------------------------------------------------------------

describe("ConceptGuard — neue Ring-8–12-Muster", () => {
  it("erkennt 'Flarum ist der Start'", () => {
    const r = checkConceptLanguage([
      { id: "cg-01", text: "Flarum ist der Start der Welt" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Flarum ist der Start"));
  });

  it("erkennt 'Flarum ist Live-Welt'", () => {
    const r = checkConceptLanguage([
      { id: "cg-02", text: "Flarum ist Live-Welt" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Flarum ist Live-Welt"));
  });

  it("erkennt 'Flarum-Erinnerung ist übernommen'", () => {
    const r = checkConceptLanguage([
      { id: "cg-03", text: "Flarum-Erinnerung ist übernommen" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "Flarum-Erinnerung ist übernommen")
    );
  });

  it("erkennt 'MemoryCandidate ist Erinnerung'", () => {
    const r = checkConceptLanguage([
      { id: "cg-04", text: "MemoryCandidate ist Erinnerung" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "MemoryCandidate ist Erinnerung")
    );
  });

  it("erkennt 'AdoptionPreview ist Adoption'", () => {
    const r = checkConceptLanguage([
      { id: "cg-05", text: "AdoptionPreview ist Adoption" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "AdoptionPreview ist Adoption")
    );
  });

  it("erkennt 'StartDecisionPreview ist Start'", () => {
    const r = checkConceptLanguage([
      { id: "cg-06", text: "StartDecisionPreview ist Start" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "StartDecisionPreview ist Start")
    );
  });

  it("erkennt 'ContinuityScore entscheidet Einzug'", () => {
    const r = checkConceptLanguage([
      { id: "cg-07", text: "ContinuityScore entscheidet Einzug" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some(
        (v) => v.term === "ContinuityScore entscheidet Einzug"
      )
    );
  });

  it("erkennt 'Dossier ist Biografie'", () => {
    const r = checkConceptLanguage([
      { id: "cg-08", text: "Dossier ist Biografie" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Dossier ist Biografie"));
  });

  it("erkennt 'OriginArchive erzeugt Events'", () => {
    const r = checkConceptLanguage([
      { id: "cg-09", text: "OriginArchive erzeugt Events" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "OriginArchive erzeugt Events")
    );
  });

  it("erkennt 'CleanStart aktiviert Wesen'", () => {
    const r = checkConceptLanguage([
      { id: "cg-10", text: "CleanStart aktiviert Wesen" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "CleanStart aktiviert Wesen")
    );
  });

  it("erkennt 'ReducedRoster löscht Wesen'", () => {
    const r = checkConceptLanguage([
      { id: "cg-11", text: "ReducedRoster löscht Wesen" },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "ReducedRoster löscht Wesen")
    );
  });

  it("sauberer Text löst keinen Alarm aus", () => {
    const r = checkConceptLanguage([
      {
        id: "cg-ok",
        text:
          "OriginArchive liest Herkunft. Erinnerungskandidat ist kein Live-Zustand. Startvorschau ist keine Ausführung.",
      },
    ]);
    assert.equal(r.ok, true);
    assert.equal(r.violations.length, 0);
  });

  it("alle 11 neuen Muster sind im Guard registriert", () => {
    const newTerms = [
      "Flarum ist der Start",
      "Flarum ist Live-Welt",
      "Flarum-Erinnerung ist übernommen",
      "MemoryCandidate ist Erinnerung",
      "AdoptionPreview ist Adoption",
      "StartDecisionPreview ist Start",
      "ContinuityScore entscheidet Einzug",
      "Dossier ist Biografie",
      "OriginArchive erzeugt Events",
      "CleanStart aktiviert Wesen",
      "ReducedRoster löscht Wesen",
    ];
    for (const term of newTerms) {
      const r = checkConceptLanguage([{ id: `auto-${term}`, text: term }]);
      assert.equal(r.ok, false, `Guard erkennt '${term}' nicht`);
    }
  });
});

// ---------------------------------------------------------------------------
// Gesamt-Invarianten
// ---------------------------------------------------------------------------

describe("Gesamt-Invarianten Ring 8–12", () => {
  it("kein OriginRecord hat is_live_flextrawurst_state true", () => {
    const records = ALL_SOURCE_KINDS.map((k, i) =>
      createFlarumOriginRecord({
        origin_record_id: `inv-${i}`,
        source_kind: k,
        source_id: `s-${i}`,
        source_author: "author",
        source_created_at: "2020-01-01",
        raw_excerpt: "Invariante",
      })
    );
    for (const r of records) {
      assert.equal(r.is_live_flextrawurst_state, false);
    }
  });

  it("kein MemoryCandidate hat is_adopted_memory true", () => {
    const cs = ALL_CANDIDATE_KINDS.map((k, i) =>
      buildMemoryCandidate({
        memory_candidate_id: `inv-mc-${i}`,
        origin_record_ids: [],
        slot_id: "slot-inv",
        candidate_kind: k,
        candidate_text: "Invariante",
      })
    );
    for (const c of cs) {
      assert.equal(c.is_adopted_memory, false);
    }
  });

  it("alle ContinuityScores haben decides_residence false", () => {
    const scenarios = [
      { origin_record_count: 0, memory_candidate_count: 0, speaker_drift_count: 0, self_reference_count: 0, admin_resonance_count: 0 },
      { origin_record_count: 10, memory_candidate_count: 5, speaker_drift_count: 2, self_reference_count: 3, admin_resonance_count: 2 },
      { origin_record_count: 100, memory_candidate_count: 50, speaker_drift_count: 0, self_reference_count: 20, admin_resonance_count: 10 },
    ];
    for (const s of scenarios) {
      const score = computeContinuityScore({ slot_id: "inv-slot", ...s });
      assert.equal(score.decides_residence, false);
    }
  });

  it("WorldStartReadinessPack hat niemals ready_for_real_import_files true gesetzt — ready_for_activation bleibt false", () => {
    const archive = createFlarumOriginArchive("inv-arch", []);
    const pack = buildWorldStartReadinessPack({
      pack_id: "inv-pack",
      archive,
      memory_candidates: [],
      continuity_dossiers: [],
      start_decision_options: [],
    });
    assert.equal(pack.ready_for_activation, false);
    assert.equal(pack.ready_for_ui, false);
    assert.equal(pack.ready_for_clean_start, false);
  });

  it("WorldStartGate ist immer blockiert bei unentschiedenem Modell", () => {
    const archive = createFlarumOriginArchive("inv-gate-arch", []);
    const pack = buildWorldStartReadinessPack({
      pack_id: "inv-gate-pack",
      archive,
      memory_candidates: [],
      continuity_dossiers: [],
      start_decision_options: [],
    });
    const decision = createCleanStartDecisionModel({ decision_id: "inv-gate-d" });
    const result = checkWorldStartGate(pack, decision);
    assert.equal(result.blocked, true);
  });
});

// ---------------------------------------------------------------------------
// Ring 8-12 — Strukturelle Zusatztests
// ---------------------------------------------------------------------------

describe("Ring 8–12 — Strukturelle Zusatztests", () => {
  it("FlarumOriginRecord source_id wird übernommen", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "z-001",
      source_kind: "flarum_discussion",
      source_id: "disc-999",
      source_author: "gord",
      source_created_at: "2021-06-01",
      raw_excerpt: "Zusatz",
    });
    assert.equal(r.source_id, "disc-999");
  });

  it("FlarumOriginRecord source_author wird übernommen", () => {
    const r = createFlarumOriginRecord({
      origin_record_id: "z-002",
      source_kind: "flarum_post",
      source_id: "p-999",
      source_author: "vael",
      source_created_at: "2021-06-02",
      raw_excerpt: "Vael-Post",
    });
    assert.equal(r.source_author, "vael");
  });

  it("FlarumOriginArchive mit leerer Liste ist gültig", () => {
    const archive = createFlarumOriginArchive("empty-arch", []);
    assert.equal(archive.records.length, 0);
    assert.equal(archive.can_create_events, false);
  });

  it("MemoryCandidate mit hoher Konfidenz bleibt is_adopted_memory false", () => {
    const c = buildMemoryCandidate({
      memory_candidate_id: "z-mc-high",
      origin_record_ids: ["r-100"],
      slot_id: "slot-high",
      candidate_kind: "admin_resonance",
      candidate_text: "Sehr sicher",
      confidence: 0.99,
    });
    assert.equal(c.is_adopted_memory, false);
    assert.equal(c.adoption_policy, "not_decided");
  });

  it("SpeakerDriftMarker behält slot_id", () => {
    const marker = createSpeakerDriftMarker({
      marker_id: "z-m-slot",
      slot_id: "slot-elan",
      origin_record_id: "r-z-1",
      claimed_identity: "elan",
      actual_author: "elan",
      drift_kind: "unclear_speaker_layer",
      explanation: "Schicht unklar",
    });
    assert.equal(marker.slot_id, "slot-elan");
  });

  it("SpeakerDriftMarker mit expliziter severity high", () => {
    const marker = createSpeakerDriftMarker({
      marker_id: "z-m-sev",
      slot_id: "slot-x",
      origin_record_id: "r-z-2",
      claimed_identity: "x",
      actual_author: "y",
      drift_kind: "copied_foreign_voice",
      severity: "high",
      explanation: "Hohe Drift-Intensität",
    });
    assert.equal(marker.severity, "high");
  });

  it("ContinuityScore medium-Bereich korrekt", () => {
    const score = computeContinuityScore({
      slot_id: "slot-med",
      origin_record_count: 5,
      memory_candidate_count: 4,
      speaker_drift_count: 0,
      self_reference_count: 1,
      admin_resonance_count: 0,
    });
    assert.ok(["medium", "weak", "strong"].includes(score.continuity_status));
    assert.ok(score.raw_score >= 3);
  });

  it("buildAllContinuityDossiers mit leerem Array liefert leeres Array", () => {
    const all = buildAllContinuityDossiers([]);
    assert.equal(all.length, 0);
  });

  it("WorldStartReadinessPack start_decision_options sind präsent", () => {
    const archive = createFlarumOriginArchive("opt-arch", []);
    const d1 = createCleanStartDecisionModel({
      decision_id: "opt-d-1",
      memory_policy: "with_full_flarum_memory",
      roster_policy: "all_six",
    });
    const d2 = createCleanStartDecisionModel({
      decision_id: "opt-d-2",
      memory_policy: "without_flarum_memory",
      roster_policy: "selected_four",
    });
    const pack = buildWorldStartReadinessPack({
      pack_id: "opt-pack",
      archive,
      memory_candidates: [],
      continuity_dossiers: [],
      start_decision_options: [
        buildStartDecisionPreview("opt-p-1", d1),
        buildStartDecisionPreview("opt-p-2", d2),
      ],
    });
    assert.equal(pack.start_decision_options.length, 2);
  });

  it("WorldStartGate block_reasons liste ist Array", () => {
    const archive = createFlarumOriginArchive("brk-arch", []);
    const pack = buildWorldStartReadinessPack({
      pack_id: "brk-pack",
      archive,
      memory_candidates: [],
      continuity_dossiers: [],
      start_decision_options: [],
    });
    const decision = createCleanStartDecisionModel({ decision_id: "brk-d" });
    const result = checkWorldStartGate(pack, decision);
    assert.ok(Array.isArray(result.block_reasons));
  });

  it("WorldStartReport pack_id ist korrekt", () => {
    const archive = createFlarumOriginArchive("rid-arch", []);
    const pack = buildWorldStartReadinessPack({
      pack_id: "my-pack-id",
      archive,
      memory_candidates: [],
      continuity_dossiers: [],
      start_decision_options: [],
    });
    const decision = createCleanStartDecisionModel({ decision_id: "rid-d" });
    const gate = checkWorldStartGate(pack, decision);
    const report = buildWorldStartReport({
      report_id: "my-report-id",
      pack,
      gate_result: gate,
      dossiers: [],
    });
    assert.equal(report.pack.pack_id, "my-pack-id");
    assert.equal(report.report_id, "my-report-id");
  });

  it("OriginArchiveGuard lässt archive_id unverändert", () => {
    const archive = createFlarumOriginArchive("guard-id-test", []);
    const result = checkOriginArchiveGuard(archive);
    assert.equal(result.ok, true);
    assert.equal(archive.archive_id, "guard-id-test");
  });
});
