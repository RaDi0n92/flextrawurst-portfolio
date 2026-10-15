# Governance

## 1. Core model: open contribution, curated admission

WorldWORDS ANTIBIBEL is open to contributions, but the official registry is not an automatically expanding majority canon. Anyone may submit material. Daniel, as founding curator, decides which terms he wants to admit to the official registry.

This authority applies only to the label **“admitted by Daniel to the official WorldWORDS registry.”** It does not restrict forks or anyone's right to maintain a registry with different decisions.

## 2. Possible contributions

Contributions may include:

- new raw words and spelling variants,
- exact source locations and original inputs,
- origin stories,
- interpretations and counter-interpretations,
- boundaries and explicitly excluded meanings,
- translations of explanations,
- real embodiments in projects, files, roles or systems,
- provenance corrections,
- reports of hallucinations or false attribution.

## 3. Status flow

`SUBMITTED → EVIDENCE_CHECK → DANIEL_REVIEW → ACCEPTED / DEFERRED / DECLINED / WITHDRAWN`

Later states may include:

`ACTIVE → SUPERSEDED / DEPRECATED / RETIRED`

No transition deletes earlier history. Changes are appended as new events.

## 4. Decisions available to Daniel

Daniel may admit a contribution:

- as an independent term,
- as a spelling variant,
- as a translation or language mutation,
- as an interpretation attached to an existing term,
- defer it for further source work,
- decline it,
- close it because it cannot lawfully be published.

Admission is official only when a file under `data/approvals/` records at least the term ID, decision, date, Daniel as decision maker and a rationale.

## 5. Immutable provenance

For admitted terms, the following remain available at minimum:

- original form and capitalization,
- submitter or transmitter,
- known authorship status including uncertainty,
- date or explicitly marked date uncertainty,
- original quote or exact input body,
- source reference and hash where available,
- earlier interpretations,
- translation contributors,
- Daniel's admission decision.

False attribution is corrected but not silently overwritten. The old event remains marked `corrected` or `retracted`.

## 6. Human–AI provenance

AI contributions are not presented wholesale as human authorship. Where possible, the record separates:

- human operator,
- AI system or model,
- session or conversation body,
- exact AI wording,
- human selection, modification or confirmation,
- uncertainty about the actual birth of the word.

A `role=user` field, database attribution or later summary is not sufficient evidence of authorship.

## 7. Raw form and translation

The raw word form remains unchanged. Language versions translate the **explanation**, not the word in disguise. A translated or mutated word form may be proposed as a separate contribution with its own provenance.

## 8. Safety and privacy

Rawness does not require publishing credentials, private addresses, unpublished personal data or third-party protected full texts. Necessary omissions are logged visibly. Public provenance may point to a hashed private origin when publication is not lawful.

## 9. Forks and official labeling

Forks may modify all licensed material and create their own admission mechanisms. The field `accepted_by_daniel: true` may only be used with an unchanged or traceably continued Daniel decision record.

## 10. Governance changes

Governance changes are handled as proposals. The rule defining who makes admissions to the official main registry can only be changed by an explicit, documented decision by Daniel.
