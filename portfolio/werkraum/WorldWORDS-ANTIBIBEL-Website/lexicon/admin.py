from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Collection,
    CollectionItem,
    Comment,
    CommentRevision,
    ContactMessage,
    ContributionProposal,
    Follow,
    ModerationDecision,
    Notification,
    Profile,
    ProvenanceEvent,
    Reaction,
    Report,
    Tag,
    Term,
    TermRelation,
    WordClass,
)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("canonical_form", "raw_form", "status", "language_of_origin", "word_class", "submitted_by_label", "is_public", "discussion_open", "created_at")
    list_filter = ("status", "is_public", "discussion_open", "language_of_origin", "word_class", "authorship_status", "featured")
    search_fields = ("raw_form", "canonical_form", "exact_input", "origin_note", "source_ref")
    readonly_fields = ("raw_form_sha256", "created_at", "updated_at", "accepted_at", "visual_seed")
    autocomplete_fields = ("submitted_by", "accepted_by", "merged_into")
    filter_horizontal = ("tags",)
    fieldsets = (
        ("Identität", {"fields": ("external_id", "slug", "raw_form", "raw_form_sha256", "canonical_form", "language_of_origin", "word_class", "tags", "visual_seed")}),
        ("Öffentlicher Zustand", {"fields": ("status", "is_public", "discussion_open", "featured", "cover_image", "cover_alt", "merged_into")}),
        ("Herkunft", {"fields": ("authorship_status", "submitted_by", "submitted_by_label", "origin_contributors", "first_seen_date", "first_seen_precision", "exact_input", "source_ref", "origin_note")}),
        ("Bedeutung", {"fields": ("definitions", "translation_provenance", "not_meant", "variants", "components", "embodiments")}),
        ("Aufnahme", {"fields": ("accepted_by", "accepted_at", "decision_rationale")}),
        ("Zeit", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ProvenanceEvent)
class ProvenanceEventAdmin(admin.ModelAdmin):
    list_display = ("term", "event_type", "actor_label", "event_at", "truth_class")
    list_filter = ("event_type", "truth_class", "event_at")
    search_fields = ("term__raw_form", "actor_label", "exact_input", "source_ref")
    readonly_fields = ("id", "created_at")
    autocomplete_fields = ("term", "actor_user", "supersedes")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("term", "author_label", "language", "status", "is_curator_note", "created_at", "edited_at")
    list_filter = ("status", "language", "is_curator_note", "created_at")
    search_fields = ("term__raw_form", "author_label", "body")
    autocomplete_fields = ("term", "author", "parent")
    readonly_fields = ("body_html", "created_at", "edited_at")


@admin.register(ContributionProposal)
class ContributionProposalAdmin(admin.ModelAdmin):
    list_display = ("term", "kind", "language", "proposed_by", "status", "created_at", "reviewed_by")
    list_filter = ("kind", "language", "status", "created_at")
    search_fields = ("term__raw_form", "proposed_text", "source_ref", "rationale")
    autocomplete_fields = ("term", "proposed_by", "reviewed_by")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reason", "target", "reporter", "status", "created_at", "assigned_to")
    list_filter = ("reason", "status", "created_at")
    search_fields = ("term__raw_form", "comment__body", "details", "resolution")
    autocomplete_fields = ("reporter", "term", "comment", "assigned_to")

    @admin.display(description="Ziel")
    def target(self, obj):
        return obj.term or obj.comment


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "language", "status", "created_at", "handled_by")
    list_filter = ("status", "language", "created_at")
    search_fields = ("subject", "name", "email", "body")
    readonly_fields = ("created_at",)


@admin.register(ModerationDecision)
class ModerationDecisionAdmin(admin.ModelAdmin):
    list_display = ("term", "decision", "decided_by", "decision_basis", "created_at")
    list_filter = ("decision", "decision_basis", "created_at")
    search_fields = ("term__raw_form", "rationale", "evidence_refs")
    readonly_fields = ("created_at",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "preferred_language", "is_muted", "created_at")
    list_filter = ("preferred_language", "is_muted", "created_at")
    search_fields = ("user__username", "user__email", "display_name", "bio")


@admin.register(WordClass)
class WordClassAdmin(admin.ModelAdmin):
    list_display = ("slug", "labels", "symbol", "sort_order")
    ordering = ("sort_order",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("slug", "kind", "labels", "sort_order")
    list_filter = ("kind",)
    ordering = ("kind", "sort_order")


class CollectionItemInline(admin.TabularInline):
    model = CollectionItem
    autocomplete_fields = ("term",)
    extra = 0


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("title_de", "slug", "owner", "is_public", "featured", "updated_at")
    list_filter = ("is_public", "featured")
    search_fields = ("titles", "descriptions")
    inlines = (CollectionItemInline,)

    @admin.display(description="Titel")
    def title_de(self, obj):
        return obj.title("de")


admin.site.register(TermRelation)
admin.site.register(CommentRevision)
admin.site.register(Reaction)
admin.site.register(Follow)
admin.site.register(Notification)
