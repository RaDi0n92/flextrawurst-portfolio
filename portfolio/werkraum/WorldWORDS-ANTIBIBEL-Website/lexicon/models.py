from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

import bleach
import markdown
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()
SUPPORTED_LANGUAGES = (("de", "Deutsch"), ("en", "English"), ("es", "Español"))
ORIGIN_LANGUAGES = SUPPORTED_LANGUAGES + (("mixed", "Sprachübergreifend / mixed"), ("unknown", "Ungeklärt / unknown"))


def localized(value, lang: str, fallback: str = "de") -> str:
    if not isinstance(value, dict):
        return str(value or "")
    return str(value.get(lang) or value.get(fallback) or next(iter(value.values()), ""))


def unique_slug(model, value: str, current_pk=None) -> str:
    base = slugify(value, allow_unicode=False)[:72] or f"wort-{uuid.uuid4().hex[:8]}"
    candidate = base
    number = 2
    qs = model.objects.all()
    if current_pk:
        qs = qs.exclude(pk=current_pk)
    while qs.filter(slug=candidate).exists():
        candidate = f"{base[:66]}-{number}"
        number += 1
    return candidate


def word_image_path(instance, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return f"word-images/{instance.slug}/{uuid.uuid4().hex}{suffix}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=80, blank=True)
    preferred_language = models.CharField(max_length=2, choices=SUPPORTED_LANGUAGES, default="de")
    bio = models.TextField(max_length=1200, blank=True)
    website = models.URLField(blank=True)
    is_muted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.username


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={"display_name": instance.username})


class WordClass(models.Model):
    slug = models.SlugField(unique=True)
    labels = models.JSONField(default=dict)
    descriptions = models.JSONField(default=dict, blank=True)
    symbol = models.CharField(max_length=12, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ("sort_order", "slug")
        verbose_name = "Wortart"
        verbose_name_plural = "Wortarten"

    def label(self, lang="de"):
        return localized(self.labels, lang)

    def __str__(self):
        return self.label("de") or self.slug


class Tag(models.Model):
    KIND_CHOICES = (
        ("theme", "Thema"),
        ("origin", "Herkunft"),
        ("creation", "Entstehungsform"),
        ("grammar", "Grammatik"),
        ("other", "Sonstiges"),
    )
    slug = models.SlugField(unique=True)
    labels = models.JSONField(default=dict)
    descriptions = models.JSONField(default=dict, blank=True)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default="theme")
    sort_order = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ("kind", "sort_order", "slug")

    def label(self, lang="de"):
        return localized(self.labels, lang)

    def __str__(self):
        return self.label("de") or self.slug


class Term(models.Model):
    STATUS_CHOICES = (
        ("submitted", "Eingereicht"),
        ("under_review", "In Prüfung"),
        ("accepted", "Aufgenommen"),
        ("deferred", "Zurückgestellt"),
        ("rejected", "Nicht aufgenommen"),
        ("merged", "Als Variante verbunden"),
        ("archived", "Archiviert"),
    )
    PRECISION_CHOICES = (("day", "Tag"), ("month", "Monat"), ("year", "Jahr"), ("unknown", "Unbekannt"))
    AUTHORSHIP_CHOICES = (
        ("claimed-by-submitter", "Vom Einreicher beansprucht"),
        ("direct-daniel-use", "Direkte Verwendung durch Daniel"),
        ("daniel-coined-ai-systematized", "Daniel geprägt, AI systematisiert"),
        ("joint-project-setting", "Gemeinsame Projektsetzung"),
        ("joint-or-unresolved-project-setting", "Gemeinsam oder ungeklärt"),
        ("layered-joint-origin", "Mehrschichtige gemeinsame Herkunft"),
        ("existing-word-redefined-by-daniel", "Bestehendes Wort von Daniel neu bestimmt"),
        ("existence-confirmed-authorship-open", "Existenz belegt, Urheberschaft offen"),
        ("origin-unresolved", "Herkunft ungeklärt"),
        ("intent-unclear", "Absicht ungeklärt"),
        ("other", "Andere / beschrieben"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    raw_form = models.CharField(max_length=180)
    raw_form_sha256 = models.CharField(max_length=64, editable=False)
    canonical_form = models.CharField(max_length=180, blank=True)
    language_of_origin = models.CharField(max_length=12, choices=ORIGIN_LANGUAGES, default="de")
    word_class = models.ForeignKey(WordClass, null=True, blank=True, on_delete=models.SET_NULL, related_name="terms")
    tags = models.ManyToManyField(Tag, blank=True, related_name="terms")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted", db_index=True)
    is_public = models.BooleanField(default=True, db_index=True)
    discussion_open = models.BooleanField(default=True)
    authorship_status = models.CharField(max_length=64, choices=AUTHORSHIP_CHOICES, default="claimed-by-submitter")
    submitted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="submitted_terms")
    submitted_by_label = models.CharField(max_length=100, blank=True)
    origin_contributors = models.JSONField(default=list, blank=True)
    first_seen_date = models.DateField(null=True, blank=True)
    first_seen_precision = models.CharField(max_length=12, choices=PRECISION_CHOICES, default="unknown")
    exact_input = models.TextField()
    source_ref = models.CharField(max_length=600, blank=True)
    origin_note = models.TextField(blank=True)
    definitions = models.JSONField(default=dict, blank=True)
    translation_provenance = models.JSONField(default=dict, blank=True)
    not_meant = models.JSONField(default=dict, blank=True)
    variants = models.JSONField(default=list, blank=True)
    components = models.JSONField(default=list, blank=True)
    embodiments = models.JSONField(default=list, blank=True)
    cover_image = models.ImageField(
        upload_to=word_image_path,
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    cover_alt = models.JSONField(default=dict, blank=True)
    accepted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="accepted_terms")
    accepted_at = models.DateTimeField(null=True, blank=True)
    decision_rationale = models.JSONField(default=dict, blank=True)
    merged_into = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="merged_variants")
    visual_seed = models.PositiveSmallIntegerField(default=1)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("canonical_form", "raw_form")
        indexes = [
            models.Index(fields=("status", "is_public")),
            models.Index(fields=("language_of_origin", "word_class")),
            models.Index(fields=("created_at",)),
        ]

    def clean(self):
        super().clean()
        if self.cover_image and self.cover_image.size > 5 * 1024 * 1024:
            raise ValidationError({"cover_image": "Das Bild darf höchstens 5 MB groß sein."})
        if self.merged_into_id and self.merged_into_id == self.pk:
            raise ValidationError({"merged_into": "Ein Begriff kann nicht mit sich selbst verbunden werden."})
        if self.status == "merged" and not self.merged_into_id:
            raise ValidationError({"merged_into": "Ein verbundener Begriff braucht ein Ziel."})

    def save(self, *args, **kwargs):
        if self.pk and Term.objects.filter(pk=self.pk).exists():
            old = Term.objects.only("raw_form", "exact_input").get(pk=self.pk)
            if old.raw_form != self.raw_form:
                raise ValidationError("Die Rohform ist unveränderlich. Eine andere Form wird als Variante oder neuer Begriff angelegt.")
            if old.exact_input != self.exact_input:
                raise ValidationError("Die ursprüngliche Eingabe ist unveränderlich. Korrekturen werden als Provenienzereignis ergänzt.")
        if not self.slug:
            self.slug = unique_slug(Term, self.raw_form, self.pk)
        if not self.canonical_form:
            self.canonical_form = self.raw_form
        self.raw_form_sha256 = hashlib.sha256(self.raw_form.encode("utf-8")).hexdigest()
        self.visual_seed = (int(self.raw_form_sha256[:4], 16) % 8) + 1
        self.full_clean()
        return super().save(*args, **kwargs)

    def definition(self, lang="de", length="short"):
        block = self.definitions.get(lang) or self.definitions.get("de") or {}
        if isinstance(block, str):
            return block
        return block.get(length) or block.get("provisional") or block.get("long") or ""

    def status_label(self, lang="de"):
        mapping = {
            "de": dict(self.STATUS_CHOICES),
            "en": {"submitted": "Submitted", "under_review": "Under review", "accepted": "Admitted", "deferred": "Deferred", "rejected": "Not admitted", "merged": "Connected as variant", "archived": "Archived"},
            "es": {"submitted": "Presentada", "under_review": "En revisión", "accepted": "Admitida", "deferred": "Aplazada", "rejected": "No admitida", "merged": "Conectada como variante", "archived": "Archivada"},
        }
        return mapping.get(lang, mapping["de"]).get(self.status, self.status)

    def get_absolute_url(self, lang="de"):
        return reverse("lexicon:term_detail", kwargs={"lang": lang, "slug": self.slug})

    def __str__(self):
        return self.canonical_form or self.raw_form


class TermRelation(models.Model):
    TYPE_CHOICES = (
        ("related", "Verwandt"),
        ("variant", "Variante"),
        ("component", "Bestandteil"),
        ("contrast", "Gegenbegriff"),
        ("inspired", "Angeregt durch"),
        ("embodies", "Verkörpert"),
    )
    source = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="outgoing_relations")
    target = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="incoming_relations")
    relation_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="related")
    labels = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("source", "target", "relation_type"), name="unique_term_relation")]

    def clean(self):
        if self.source_id == self.target_id:
            raise ValidationError("Eine Relation braucht zwei verschiedene Begriffe.")


class Comment(models.Model):
    STATUS_CHOICES = (("visible", "Sichtbar"), ("hidden", "Ausgeblendet"), ("deleted", "Gelöscht"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="word_comments")
    author_label = models.CharField(max_length=100, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    language = models.CharField(max_length=2, choices=SUPPORTED_LANGUAGES, default="de")
    body = models.TextField(max_length=12000)
    body_html = models.TextField(editable=False)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="visible", db_index=True)
    is_curator_note = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [models.Index(fields=("term", "status", "created_at"))]

    def clean(self):
        if self.parent_id and self.parent.term_id != self.term_id:
            raise ValidationError("Antwort und Ausgangsbeitrag müssen zum selben Begriff gehören.")
        if self.parent_id and self.parent.parent_id:
            raise ValidationError("Für gute Lesbarkeit sind zwei Diskussionsebenen vorgesehen.")

    def render_body(self):
        rendered = markdown.markdown(self.body, extensions=["nl2br", "sane_lists"])
        return bleach.clean(
            rendered,
            tags=["p", "br", "strong", "em", "ul", "ol", "li", "blockquote", "code", "pre", "a"],
            attributes={"a": ["href", "title", "rel"]},
            protocols=["http", "https", "mailto"],
            strip=True,
        )

    def save(self, *args, **kwargs):
        self.body_html = self.render_body()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.term}: {self.body[:60]}"


class CommentRevision(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="revisions")
    body = models.TextField()
    body_html = models.TextField()
    edited_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    reason = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class Reaction(models.Model):
    KIND_CHOICES = (("resonates", "Resoniert"), ("question", "Frage"), ("counterpoint", "Widerspruch"))
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="word_reactions")
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("comment", "user", "kind"), name="unique_comment_reaction")]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="word_follows")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "term"), name="unique_term_follow")]


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="word_notifications")
    kind = models.CharField(max_length=40)
    title = models.CharField(max_length=180)
    body = models.CharField(max_length=500, blank=True)
    url = models.CharField(max_length=500, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class ContributionProposal(models.Model):
    KIND_CHOICES = (
        ("definition", "Erklärung"),
        ("translation", "Übersetzung"),
        ("origin", "Herkunftskorrektur"),
        ("variant", "Variante"),
        ("relation", "Beziehung"),
        ("embodiment", "Verkörperung"),
        ("word_class", "Wortart"),
        ("other", "Andere Ergänzung"),
    )
    STATUS_CHOICES = (("pending", "Offen"), ("accepted", "Übernommen"), ("rejected", "Nicht übernommen"), ("withdrawn", "Zurückgezogen"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="contribution_proposals")
    proposed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="word_contributions")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    language = models.CharField(max_length=2, choices=SUPPORTED_LANGUAGES, default="de")
    proposed_text = models.TextField(max_length=12000)
    source_ref = models.CharField(max_length=600, blank=True)
    rationale = models.TextField(max_length=4000, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending", db_index=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_word_contributions")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)


class Report(models.Model):
    REASON_CHOICES = (("spam", "Spam"), ("abuse", "Beleidigung / Angriff"), ("privacy", "Private Daten"), ("copyright", "Urheberrecht"), ("provenance", "Falsche Herkunft"), ("other", "Anderer Grund"))
    STATUS_CHOICES = (("open", "Offen"), ("reviewing", "In Prüfung"), ("resolved", "Erledigt"), ("dismissed", "Verworfen"))
    reporter = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="word_reports")
    term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.CASCADE, related_name="reports")
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(max_length=4000, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="open", db_index=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_word_reports")
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if bool(self.term_id) == bool(self.comment_id):
            raise ValidationError("Eine Meldung muss genau einen Begriff oder einen Beitrag betreffen.")


class ModerationDecision(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="decisions")
    decision = models.CharField(max_length=20, choices=Term.STATUS_CHOICES)
    rationale = models.JSONField(default=dict)
    decided_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="word_decisions")
    decision_basis = models.CharField(max_length=180, default="curator-review")
    evidence_refs = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)


class ProvenanceEvent(models.Model):
    TYPE_CHOICES = (
        ("submission", "Einreichung"),
        ("first_use", "Erste Verwendung"),
        ("definition", "Erklärung"),
        ("translation", "Übersetzung"),
        ("correction", "Korrektur"),
        ("decision", "Aufnahmeentscheidung"),
        ("status", "Statusänderung"),
        ("relation", "Beziehung"),
        ("embodiment", "Verkörperung"),
        ("redaction", "Redaktion / Schwärzung"),
        ("import", "Import"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="provenance_events")
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    actor_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="provenance_events")
    actor_label = models.CharField(max_length=120, blank=True)
    event_at = models.DateTimeField(default=timezone.now, db_index=True)
    source_ref = models.CharField(max_length=600, blank=True)
    exact_input = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    truth_class = models.CharField(max_length=40, default="confirmed")
    supersedes = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="superseded_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("event_at", "created_at")

    def delete(self, *args, **kwargs):
        raise ValidationError("Provenienzereignisse sind append-only und werden nicht gelöscht.")


class Collection(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    titles = models.JSONField(default=dict)
    descriptions = models.JSONField(default=dict, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="word_collections")
    is_public = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Collection, localized(self.titles, "de"), self.pk)
        super().save(*args, **kwargs)

    def title(self, lang="de"):
        return localized(self.titles, lang)

    def description(self, lang="de"):
        return localized(self.descriptions, lang)

    def __str__(self):
        return self.title("de")


class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="items")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="collection_items")
    note = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ("sort_order", "id")
        constraints = [models.UniqueConstraint(fields=("collection", "term"), name="unique_collection_term")]


class ContactMessage(models.Model):
    STATUS_CHOICES = (("open", "Offen"), ("answered", "Beantwortet"), ("closed", "Geschlossen"))
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="word_contact_messages")
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    body = models.TextField(max_length=12000)
    language = models.CharField(max_length=2, choices=SUPPORTED_LANGUAGES, default="de")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="open", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    handled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="handled_word_contact_messages")
    internal_note = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.subject} ({self.name})"
