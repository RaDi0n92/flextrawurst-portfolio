from __future__ import annotations

import json
import secrets
from datetime import date, datetime, time
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from lexicon.models import (
    Collection,
    CollectionItem,
    ModerationDecision,
    Profile,
    ProvenanceEvent,
    Tag,
    Term,
    WordClass,
)

User = get_user_model()


WORD_CLASSES = [
    ("noun", {"de": "Substantive", "en": "Nouns", "es": "Sustantivos"}, {"de": "Dinge, Wesen, Zustände und Gebilde.", "en": "Things, beings, states and constructs.", "es": "Cosas, seres, estados y construcciones."}, "N", 10),
    ("verb", {"de": "Verben", "en": "Verbs", "es": "Verbos"}, {"de": "Wörter für Handlungen, Bewegungen und Veränderungen.", "en": "Words for actions, motion and transformation.", "es": "Palabras para acciones, movimientos y transformaciones."}, "V", 20),
    ("adjective", {"de": "Adjektive", "en": "Adjectives", "es": "Adjetivos"}, {"de": "Eigenschaften und Arten des Erscheinens.", "en": "Qualities and ways of appearing.", "es": "Cualidades y modos de aparecer."}, "A", 30),
    ("proper-name", {"de": "Eigennamen", "en": "Proper names", "es": "Nombres propios"}, {"de": "Benennungen einzelner Wesen, Orte, Körper oder Projekte.", "en": "Names for particular beings, places, bodies or projects.", "es": "Nombres de seres, lugares, cuerpos o proyectos concretos."}, "E", 40),
    ("blend", {"de": "Mischwörter", "en": "Blended words", "es": "Palabras mezcladas"}, {"de": "Wörter, deren Herkunft sichtbar aus mehreren Strängen besteht.", "en": "Words visibly formed from several strands.", "es": "Palabras formadas visiblemente por varias corrientes."}, "M", 50),
    ("phrase", {"de": "Wortkörper und Ausdrücke", "en": "Word bodies and expressions", "es": "Cuerpos de palabra y expresiones"}, {"de": "Mehrteilige Benennungen, die als ein Fundstück behandelt werden.", "en": "Multi-part expressions treated as one finding.", "es": "Expresiones de varias partes tratadas como un hallazgo."}, "…", 60),
    ("unknown", {"de": "Noch ungeklärt", "en": "Not yet classified", "es": "Aún sin clasificar"}, {"de": "Die Wortart bleibt offen und darf diskutiert werden.", "en": "The word class remains open for discussion.", "es": "La clase permanece abierta a debate."}, "?", 99),
]

TAGS = [
    ("human-ai", "origin", {"de": "Mensch–AI", "en": "Human–AI", "es": "Humano–AI"}, 10),
    ("daniel", "origin", {"de": "Daniel", "en": "Daniel", "es": "Daniel"}, 20),
    ("origin-open", "origin", {"de": "Herkunft offen", "en": "Origin open", "es": "Origen abierto"}, 30),
    ("typo-seed", "creation", {"de": "Fehlerkeim", "en": "Typo seed", "es": "Semilla de error"}, 10),
    ("conscious-blend", "creation", {"de": "Bewusste Mischung", "en": "Conscious blend", "es": "Mezcla consciente"}, 20),
    ("project-setting", "creation", {"de": "Projektsetzung", "en": "Project setting", "es": "Definición de proyecto"}, 30),
    ("embodied", "theme", {"de": "Verkörpert", "en": "Embodied", "es": "Encarnada"}, 10),
    ("provenance", "theme", {"de": "Provenienz", "en": "Provenance", "es": "Procedencia"}, 20),
    ("language-motion", "theme", {"de": "Sprachbewegung", "en": "Language motion", "es": "Movimiento lingüístico"}, 30),
]


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def aware_midday(value):
    parsed = parse_date(value)
    if not parsed:
        return None
    return timezone.make_aware(datetime.combine(parsed, time(12, 0)), timezone.get_current_timezone())


def infer_word_class(raw: str, external_id: str):
    lower = raw.lower()
    if external_id == "verdeutschen" or lower.endswith(("ieren", "ern", "eln")):
        return "verb"
    if " " in raw:
        return "phrase"
    if external_id in {"symbositierung", "worldwords", "antibibel", "robotermodus", "metamonster", "ideenmonstrum"}:
        return "blend"
    if raw[:1].isupper():
        return "noun"
    return "unknown"


def normalize_definition(value):
    if not isinstance(value, dict):
        return {}
    result = {}
    for lang, block in value.items():
        if isinstance(block, str):
            result[lang] = {"short": block, "long": block}
        elif isinstance(block, dict):
            provisional = block.get("provisional")
            result[lang] = {
                "short": block.get("short") or provisional or block.get("long") or "",
                "long": block.get("long") or provisional or block.get("short") or "",
            }
            if provisional:
                result[lang]["provisional"] = provisional
    return result


class Command(BaseCommand):
    help = "Importiert den kuratierten Open-Source-Ausgangskörper idempotent in die Live-Datenbank."

    def add_arguments(self, parser):
        parser.add_argument("--source", type=str, default=str(settings.OPEN_SOURCE_ROOT))
        parser.add_argument("--reset-content", action="store_true", help="Löscht nur importierte Begriffe und Sammlungen vor dem Neuimport.")

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(options["source"]).resolve()
        if not (source / "data" / "terms").is_dir():
            raise CommandError(f"Kein gültiger Open-Source-Körper: {source}")

        if options["reset_content"]:
            Collection.objects.filter(owner__isnull=True).delete()
            Term.objects.filter(external_id__isnull=False).delete()

        classes = {}
        for slug, labels, descriptions, symbol, order in WORD_CLASSES:
            item, _ = WordClass.objects.update_or_create(slug=slug, defaults={"labels": labels, "descriptions": descriptions, "symbol": symbol, "sort_order": order})
            classes[slug] = item

        tags = {}
        for slug, kind, labels, order in TAGS:
            item, _ = Tag.objects.update_or_create(slug=slug, defaults={"kind": kind, "labels": labels, "sort_order": order})
            tags[slug] = item

        daniel, created = User.objects.get_or_create(username="daniel", defaults={"email": ""})
        daniel.is_staff = True
        daniel.is_superuser = True
        daniel.is_active = True
        credentials_path = Path(settings.BASE_DIR) / "secrets" / "admin-initial-credentials.txt"
        if created or not daniel.has_usable_password():
            password = secrets.token_urlsafe(22)
            daniel.set_password(password)
            credentials_path.write_text(
                "WorldWORDS ANTIBIBEL – initialer Adminzugang\n"
                "URL: https://flextrawurst.de/WORLDwordsANTIbibel/de/login/\n"
                "Benutzername: daniel\n"
                f"Passwort: {password}\n"
                "Nach der ersten Anmeldung im Adminbereich ändern.\n",
                encoding="utf-8",
            )
            credentials_path.chmod(0o600)
        daniel.save()
        profile, _ = Profile.objects.get_or_create(user=daniel)
        profile.display_name = "Daniel"
        profile.preferred_language = "de"
        profile.bio = "Gründer und kuratorische Aufnahmeinstanz der WorldWORDS ANTIBIBEL."
        profile.save()

        imported = []
        approvals = {}
        for path in sorted((source / "data" / "approvals").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            approvals[data["id"]] = data

        for path in sorted((source / "data" / "terms").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            origin = data.get("origin") or {}
            approval_ref = (data.get("approval") or {}).get("approval_id")
            approval = approvals.get(approval_ref, {})
            raw = data.get("canonical_form") or data["id"]
            defaults = {
                "raw_form": raw,
                "canonical_form": data.get("canonical_form") or raw,
                "language_of_origin": data.get("language_of_origin", "de"),
                "word_class": classes[infer_word_class(raw, data["id"])],
                "status": "accepted",
                "is_public": True,
                "discussion_open": True,
                "authorship_status": origin.get("authorship_status") or "other",
                "submitted_by": daniel,
                "submitted_by_label": "Daniel",
                "origin_contributors": origin.get("contributors") or [],
                "first_seen_date": parse_date((origin.get("first_seen") or {}).get("date")),
                "first_seen_precision": (origin.get("first_seen") or {}).get("precision", "unknown"),
                "exact_input": origin.get("exact_input") or raw,
                "source_ref": origin.get("source_ref", ""),
                "origin_note": origin.get("origin_note", ""),
                "definitions": normalize_definition(data.get("definitions")),
                "translation_provenance": data.get("translation_provenance") or {},
                "not_meant": data.get("not_meant") or {},
                "variants": data.get("variants") or [],
                "components": data.get("components") or [],
                "embodiments": data.get("embodiments") or [],
                "accepted_by": daniel,
                "accepted_at": aware_midday(approval.get("decision_date") or (origin.get("first_seen") or {}).get("date")),
                "decision_rationale": approval.get("rationale") or {},
                "featured": True,
            }
            term, was_created = Term.objects.update_or_create(external_id=data["id"], defaults=defaults)
            imported.append(term)
            wanted_tags = [tags["daniel"]]
            if len(term.origin_contributors) > 1:
                wanted_tags.append(tags["human-ai"])
            if term.components:
                wanted_tags.append(tags["conscious-blend"])
            if term.embodiments:
                wanted_tags.append(tags["embodied"])
            wanted_tags.append(tags["provenance"])
            term.tags.set(wanted_tags)
            if was_created or not term.provenance_events.exists():
                ProvenanceEvent.objects.create(
                    term=term,
                    event_type="first_use",
                    actor_user=daniel if "daniel" in term.origin_contributors else None,
                    actor_label=" + ".join(term.origin_contributors) or "unresolved",
                    event_at=term.accepted_at or timezone.now(),
                    source_ref=term.source_ref,
                    exact_input=term.exact_input,
                    payload={"imported_from": str(path.relative_to(source)), "authorship_status": term.authorship_status},
                    truth_class="source-bound",
                )
                decision = ModerationDecision.objects.create(
                    term=term,
                    decision="accepted",
                    rationale=approval.get("rationale") or {},
                    decided_by=daniel,
                    decision_basis=approval.get("decision_basis", "inherited-founding-canonical-state"),
                    evidence_refs=approval.get("evidence_refs") or [],
                )
                ProvenanceEvent.objects.create(
                    term=term,
                    event_type="decision",
                    actor_user=daniel,
                    actor_label="Daniel",
                    event_at=term.accepted_at or timezone.now(),
                    source_ref="; ".join(approval.get("evidence_refs") or []),
                    payload={"from": "founding-source", "to": "accepted", "decision_id": decision.pk},
                    truth_class="confirmed",
                )

        proposals = []
        for path in sorted((source / "data" / "proposals").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            raw = data.get("raw_form") or data["id"]
            status = "accepted" if (data.get("official_registry") or {}).get("accepted_by_daniel") else data.get("status", "submitted")
            if status not in dict(Term.STATUS_CHOICES):
                status = "submitted"
            submitter = daniel if data.get("submitted_by") == "daniel" else None
            defaults = {
                "raw_form": raw,
                "canonical_form": raw,
                "language_of_origin": "de",
                "word_class": classes[infer_word_class(raw, data["id"])],
                "status": status,
                "is_public": True,
                "discussion_open": True,
                "authorship_status": data.get("authorship_status") or "origin-unresolved",
                "submitted_by": submitter,
                "submitted_by_label": "Daniel" if submitter else data.get("submitted_by", "ungeklärt"),
                "origin_contributors": [data.get("submitted_by")] if data.get("submitted_by") else [],
                "first_seen_date": parse_date((data.get("first_seen") or {}).get("date")),
                "first_seen_precision": (data.get("first_seen") or {}).get("precision", "unknown"),
                "exact_input": data.get("exact_input") or raw,
                "source_ref": data.get("source_ref", ""),
                "origin_note": (data.get("review_notes") or {}).get("de", ""),
                "definitions": normalize_definition(data.get("definitions")),
                "translation_provenance": data.get("translation_provenance") or {},
                "featured": False,
            }
            term, was_created = Term.objects.update_or_create(external_id=data["id"], defaults=defaults)
            proposals.append(term)
            wanted_tags = [tags["origin-open"]]
            if submitter:
                wanted_tags.append(tags["daniel"])
            if data.get("authorship_status") == "layered-joint-origin":
                wanted_tags.append(tags["human-ai"])
            term.tags.set(wanted_tags)
            if was_created or not term.provenance_events.exists():
                ProvenanceEvent.objects.create(
                    term=term,
                    event_type="submission",
                    actor_user=submitter,
                    actor_label=term.submitted_by_label,
                    event_at=aware_midday((data.get("first_seen") or {}).get("date")) or timezone.now(),
                    source_ref=term.source_ref,
                    exact_input=term.exact_input,
                    payload={"imported_from": str(path.relative_to(source)), "authorship_status": term.authorship_status},
                    truth_class="source-bound",
                )

        collection_specs = [
            ("founding-words", {"de": "Aufgenommene Grundwörter", "en": "Admitted founding words", "es": "Palabras fundadoras admitidas"}, {"de": "Die vier bereits aufgenommenen Ausgangswörter.", "en": "The four already admitted founding words.", "es": "Las cuatro palabras fundadoras ya admitidas."}, imported, True),
            ("open-origin", {"de": "Ungeklärte Geburten", "en": "Unresolved births", "es": "Nacimientos sin resolver"}, {"de": "Wörter, deren Herkunft oder genaue Absicht noch offen ist.", "en": "Words whose origin or exact intent remains open.", "es": "Palabras cuyo origen o intención exacta sigue abierta."}, [x for x in proposals if "unresolved" in x.authorship_status or "open" in x.authorship_status or "unclear" in x.authorship_status], True),
            ("human-ai", {"de": "Mensch–AI-Mischwörter", "en": "Human–AI blended words", "es": "Palabras mezcladas humano–AI"}, {"de": "Begriffe mit mehrschichtiger oder gemeinsamer Entstehung.", "en": "Terms with layered or joint formation.", "es": "Términos de formación conjunta o por capas."}, [x for x in imported + proposals if len(x.origin_contributors) > 1 or x.authorship_status in ("layered-joint-origin", "joint-project-setting", "joint-or-unresolved-project-setting", "daniel-coined-ai-systematized")], True),
            ("language-motion", {"de": "Sprachbewegungen", "en": "Language motions", "es": "Movimientos lingüísticos"}, {"de": "Wörter, die nicht nur benennen, sondern eine Praxis oder Veränderung auslösen.", "en": "Words that do not merely name but initiate a practice or transformation.", "es": "Palabras que no solo nombran, sino que activan una práctica o transformación."}, [x for x in imported if x.external_id in ("symbositierung", "verdeutschen", "worldwords")], True),
        ]
        for slug, titles, descriptions, terms, featured in collection_specs:
            collection, _ = Collection.objects.update_or_create(slug=slug, defaults={"titles": titles, "descriptions": descriptions, "owner": None, "is_public": True, "featured": featured})
            CollectionItem.objects.filter(collection=collection).delete()
            for index, term in enumerate(terms):
                CollectionItem.objects.create(collection=collection, term=term, sort_order=(index + 1) * 10)

        self.stdout.write(self.style.SUCCESS(
            f"Import abgeschlossen: {len(imported)} aufgenommen, {len(proposals)} Vorschläge, "
            f"{WordClass.objects.count()} Wortarten, {Collection.objects.count()} Wege."
        ))
        if credentials_path.exists():
            self.stdout.write(f"Adminzugang: {credentials_path}")
