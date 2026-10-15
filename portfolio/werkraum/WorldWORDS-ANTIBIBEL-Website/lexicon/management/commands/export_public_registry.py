from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from lexicon.models import Collection, Comment, ContributionProposal, ModerationDecision, Term
from lexicon.views import term_to_dict


class Command(BaseCommand):
    help = "Erzeugt einen atomaren öffentlichen JSON-Snapshot ohne private Kontodaten."

    def add_arguments(self, parser):
        parser.add_argument("--output", default=str(Path(settings.BASE_DIR) / "exports" / "public-current"))
        parser.add_argument("--mirror-open-source", action="store_true")

    def handle(self, *args, **options):
        output = Path(options["output"]).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temp = Path(tempfile.mkdtemp(prefix="worldwords-export-", dir=output.parent))
        try:
            terms = Term.objects.filter(is_public=True).exclude(status="archived").select_related("word_class").prefetch_related("provenance_events")
            term_rows = []
            for term in terms:
                row = term_to_dict(term, include_detail=True)
                row["comments"] = [
                    {
                        "id": str(comment.pk),
                        "author": comment.author_label,
                        "language": comment.language,
                        "body": comment.body,
                        "parent_id": str(comment.parent_id) if comment.parent_id else None,
                        "is_curator_note": comment.is_curator_note,
                        "created_at": comment.created_at.isoformat(),
                        "edited_at": comment.edited_at.isoformat() if comment.edited_at else None,
                    }
                    for comment in term.comments.filter(status="visible").order_by("created_at")
                ]
                row["accepted_contributions"] = [
                    {
                        "id": str(item.pk),
                        "kind": item.kind,
                        "language": item.language,
                        "text": item.proposed_text,
                        "source_ref": item.source_ref,
                        "contributor": item.proposed_by.profile.display_name if item.proposed_by and hasattr(item.proposed_by, "profile") else (item.proposed_by.username if item.proposed_by else "unknown"),
                        "created_at": item.created_at.isoformat(),
                        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
                    }
                    for item in term.contribution_proposals.filter(status="accepted").select_related("proposed_by", "proposed_by__profile")
                ]
                row["decisions"] = [
                    {
                        "decision": decision.decision,
                        "rationale": decision.rationale,
                        "decided_by": decision.decided_by.profile.display_name if decision.decided_by and hasattr(decision.decided_by, "profile") else (decision.decided_by.username if decision.decided_by else "unknown"),
                        "decision_basis": decision.decision_basis,
                        "evidence_refs": decision.evidence_refs,
                        "created_at": decision.created_at.isoformat(),
                    }
                    for decision in term.decisions.select_related("decided_by", "decided_by__profile").all()
                ]
                term_rows.append(row)

            collections = []
            for collection in Collection.objects.filter(is_public=True).prefetch_related("items__term"):
                collections.append({
                    "slug": collection.slug,
                    "titles": collection.titles,
                    "descriptions": collection.descriptions,
                    "featured": collection.featured,
                    "terms": [item.term.slug for item in collection.items.all() if item.term.is_public],
                })

            payloads = {
                "registry.json": {
                    "schema_version": "1.0",
                    "generated_at": timezone.now().isoformat(),
                    "curation_authority": "Daniel",
                    "license": "CC BY-SA 4.0",
                    "counts": {
                        "terms": len(term_rows),
                        "accepted": sum(1 for row in term_rows if row["status"] == "accepted"),
                        "comments": sum(len(row["comments"]) for row in term_rows),
                    },
                    "terms": term_rows,
                },
                "collections.json": {
                    "schema_version": "1.0",
                    "generated_at": timezone.now().isoformat(),
                    "collections": collections,
                },
            }
            hashes = {}
            for name, payload in payloads.items():
                raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
                (temp / name).write_bytes(raw)
                hashes[name] = hashlib.sha256(raw).hexdigest()

            manifest = {
                "schema_version": "1.0",
                "generated_at": timezone.now().isoformat(),
                "files": [{"path": name, "sha256": digest, "bytes": (temp / name).stat().st_size} for name, digest in sorted(hashes.items())],
            }
            manifest_raw = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
            (temp / "MANIFEST.json").write_bytes(manifest_raw)

            backup = output.with_name(output.name + ".previous")
            if backup.exists():
                shutil.rmtree(backup)
            if output.exists():
                output.rename(backup)
            temp.rename(output)

            if options["mirror_open_source"]:
                mirror = Path(settings.OPEN_SOURCE_ROOT) / "data" / "live"
                mirror.mkdir(parents=True, exist_ok=True)
                for item in output.iterdir():
                    if item.is_file():
                        target = mirror / item.name
                        temp_target = target.with_suffix(target.suffix + ".tmp")
                        shutil.copy2(item, temp_target)
                        os.replace(temp_target, target)

            self.stdout.write(self.style.SUCCESS(f"Export erzeugt: {output}"))
        except Exception:
            if temp.exists():
                shutil.rmtree(temp, ignore_errors=True)
            raise
