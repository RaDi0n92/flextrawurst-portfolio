# Graph Report - flextrawurst  (2026-07-25)

## Corpus Check
- 197 files · ~404,515 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1245 nodes · 2852 edges · 19 communities detected
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 222 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]

## God Nodes (most connected - your core abstractions)
1. `ec` - 48 edges
2. `find()` - 32 edges
3. `generateHTML()` - 31 edges
4. `za()` - 27 edges
5. `ms()` - 25 edges
6. `va()` - 21 edges
7. `vl()` - 21 edges
8. `Gn()` - 20 edges
9. `buildCounts()` - 20 edges
10. `Rt()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `find()` --calls--> `getNodeLayout()`  [INFERRED]
  tests/world_os_ring_13_15_worldblick_static_preview.test.ts → kernel/process_camera/process_camera_layout.ts
- `find()` --calls--> `findFutureConceptById()`  [INFERRED]
  tests/world_os_ring_13_15_worldblick_static_preview.test.ts → kernel/future_concepts/future_concept_registry.ts
- `find()` --calls--> `findFeatureFlag()`  [INFERRED]
  tests/world_os_ring_13_15_worldblick_static_preview.test.ts → kernel/features/feature_registry.ts
- `find()` --calls--> `findCausalParents()`  [INFERRED]
  tests/world_os_ring_13_15_worldblick_static_preview.test.ts → kernel/queries/event_queries.ts
- `find()` --calls--> `findProcessBodyById()`  [INFERRED]
  tests/world_os_ring_13_15_worldblick_static_preview.test.ts → kernel/process_model/process_registry.ts

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (147): _a(), Ae(), An(), at(), au, bl(), Bn(), Bo() (+139 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (53): drawItem(), hexToRgb(), initAll(), noise(), sharedLoop(), startElectricBorder(), wrap(), Al() (+45 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (57): buildAdminControlExport(), serializeAdminControlExport(), buildAdminControlInspection(), buildAdminControlSnapshot(), hasPermission(), filterSearchCorpus(), explainSearchResult(), runArchaeologyQuery() (+49 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (75): buildPayload(), chat(), chatRaw(), chatStream(), defaultIdSlot(), normalizeMessages(), zielPort(), aktiveZeitachse() (+67 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (62): requireAuth(), aktiveZeitachse(), aliasePath(), allgemeinesFeedbackJsonPath(), allgemeinesFeedbackMdPath(), anhangManifestPfad(), appendProvenienz(), audioMetadaten() (+54 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (54): chip(), esc(), generateAdminView(), generateAnkuendigungenView(), generateArchaeologieView(), generateCyberlingeView(), generateDenkenView(), generateDiskursView() (+46 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (31): createWorldTick(), buildEntityProjection(), findCausalParents(), InMemoryEventStore, replay(), replayWorld(), buildRenderHints(), applyPresencePulse() (+23 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (27): mapForumAccountsToSlots(), runActivationFirewall(), assessAllSlotsActivationReadiness(), assessCameraReadiness(), checkConceptLanguage(), buildConsoleExport(), serializeConsoleExport(), buildSlotsFromScenarioPack() (+19 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (35): buildEdgesForBody(), buildNode(), buildProcessCameraModel(), toLayerKind(), toStatusKind(), buildProcessCameraHtml(), esc(), nodesForLayer() (+27 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (2): buildEntityContinuityDossier(), computeContinuityScore()

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (31): clickSplat(), compile(), corrDX(), corrDY(), correctRadius(), dpr(), frame(), genColor() (+23 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (3): lu, pu(), _u()

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (8): buildStaticPreview(), allSectionsHtml(), buildStaticPreviewHtml(), esc(), findSection(), renderSection(), buildWorldInspectionExport(), buildWorldInspectionExportFixture()

### Community 13 - "Community 13"
Cohesion: 0.17
Nodes (8): findFutureConceptById(), getFutureConceptRegistry(), buildOrganBlueprintsForRegistry(), buildOrganDock(), buildOrganDockExport(), serializeOrganDockExport(), buildOrganDockInspection(), assessAllOrganReadiness()

### Community 14 - "Community 14"
Cohesion: 0.22
Nodes (8): buildCSS(), create(), defaultCorners(), loop(), onLeave(), onOver(), start(), updateCorners()

### Community 15 - "Community 15"
Cohesion: 0.29
Nodes (9): buildKompOaseVorformHtml(), geniGrid(), namelessLayer(), plants(), splitters(), stars(), terrainH(), terrainPath() (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.38
Nodes (3): latestVerdichtung(), latestWochenlog(), readText()

### Community 18 - "Community 18"
Cohesion: 0.6
Nodes (3): buildCSS(), buildJS(), buildKompOaseDatafieldHtml()

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (2): cosine(), main()

## Knowledge Gaps
- **Thin community `Community 9`** (41 nodes): `createCleanStartDecisionModel()`, `buildAllContinuityDossiers()`, `buildEntityContinuityDossier()`, `computeContinuityScore()`, `createFlarumOriginArchive()`, `queryArchiveBySlot()`, `queryArchiveBySourceKind()`, `queryMemoryCandidates()`, `createFlarumOriginRecord()`, `continuity_dossier_builder.ts`, `continuity_score.ts`, `entity_continuity_dossier.ts`, `speaker_drift_marker.ts`, `memory_adoption_preview.ts`, `memory_candidate_builder.ts`, `memory_candidate_filter.ts`, `memory_candidate_model.ts`, `flarum_origin_archive.ts`, `flarum_origin_record.ts`, `origin_archive_guard.ts`, `clean_start_decision_model.ts`, `start_decision_preview.ts`, `start_memory_policy.ts`, `start_roster_policy.ts`, `world_start_gate.ts`, `world_start_readiness_pack.ts`, `world_start_report.ts`, `buildMemoryAdoptionPreview()`, `buildMemoryCandidate()`, `filterMemoryCandidates()`, `checkOriginArchiveGuard()`, `createSpeakerDriftMarker()`, `buildStartDecisionPreview()`, `describeMemoryPolicy()`, `getAllMemoryPolicyInfos()`, `describeRosterPolicy()`, `getAllRosterPolicyInfos()`, `world_os_ring_8_12_origin_start_memory_continuity.test.ts`, `checkWorldStartGate()`, `buildWorldStartReadinessPack()`, `buildWorldStartReport()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (3 nodes): `cosine()`, `main()`, `kalibriere_embedding_schwelle.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `find()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 8`, `Community 12`, `Community 13`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **Why does `na()` connect `Community 0` to `Community 1`, `Community 4`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `ms()` connect `Community 1` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `find()` (e.g. with `resolveCharName()` and `upsertFeedback()`) actually correct?**
  _`find()` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `generateHTML()` (e.g. with `.replace()` and `generateEinsichtView()`) actually correct?**
  _`generateHTML()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._