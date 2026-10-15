from __future__ import annotations

import json
import random
from datetime import timedelta
from functools import wraps
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db import connection, transaction
from django.db.models import Count, Max, Prefetch, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import (
    CommentForm,
    ContactForm,
    ContributionProposalForm,
    CuratorDecisionForm,
    LoginForm,
    LocalizedPasswordChangeForm,
    ProfileForm,
    RegisterForm,
    ReportForm,
    TermSubmissionForm,
)
from .i18n import SUPPORTED, get_text
from .models import (
    Collection,
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


def require_language(lang: str) -> str:
    if lang not in SUPPORTED:
        raise Http404("Unsupported language")
    return lang


def lang_login_required(view):
    @wraps(view)
    def wrapped(request, lang, *args, **kwargs):
        require_language(lang)
        if not request.user.is_authenticated:
            url = reverse("lexicon:login", kwargs={"lang": lang})
            return redirect(f"{url}?next={quote(request.get_full_path())}")
        return view(request, lang, *args, **kwargs)
    return wrapped


def curator_required(view):
    @wraps(view)
    def wrapped(request, lang, *args, **kwargs):
        require_language(lang)
        if not request.user.is_authenticated:
            return redirect(f"{reverse('lexicon:login', kwargs={'lang': lang})}?next={quote(request.get_full_path())}")
        if not request.user.is_staff:
            raise Http404
        return view(request, lang, *args, **kwargs)
    return wrapped


def public_terms():
    return Term.objects.filter(is_public=True).exclude(status="archived")


def display_name(user):
    if not user:
        return "unknown"
    profile = Profile.objects.filter(user=user).first()
    return (profile.display_name if profile else "") or user.username


def notify(user, kind, title, body="", url="", payload=None):
    if user and user.is_active:
        Notification.objects.create(user=user, kind=kind, title=title, body=body, url=url, payload=payload or {})


def notify_curators(kind, title, body="", url="", payload=None):
    from django.contrib.auth import get_user_model
    for user in get_user_model().objects.filter(is_staff=True, is_active=True):
        notify(user, kind, title, body, url, payload)


def root_redirect(request):
    return redirect("lexicon:home", lang="de")


@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            database_ok = cursor.fetchone()[0] == 1
    except Exception:
        database_ok = False
    return JsonResponse({
        "ok": database_ok,
        "service": "worldwords-antibibel",
        "version": "1.0.0",
        "prefix": settings.FORCE_SCRIPT_NAME,
        "time": timezone.now().isoformat(),
    }, status=200 if database_ok else 503)


def home(request, lang):
    require_language(lang)
    base = public_terms().select_related("word_class", "submitted_by")
    featured = list(base.filter(status="accepted").order_by("-featured", "accepted_at", "canonical_form")[:6])
    newest = list(base.exclude(status="accepted").order_by("-created_at")[:6])
    active = list(
        base.annotate(
            comment_count=Count("comments", filter=Q(comments__status="visible"), distinct=True),
            last_comment=Max("comments__created_at", filter=Q(comments__status="visible")),
        )
        .filter(comment_count__gt=0)
        .order_by("-last_comment")[:6]
    )
    classes = list(
        WordClass.objects.annotate(term_count=Count("terms", filter=Q(terms__is_public=True) & ~Q(terms__status="archived")))
        .filter(term_count__gt=0)
    )
    collections = Collection.objects.filter(is_public=True).order_by("-featured", "titles")[:5]
    stats = {
        "terms": base.count(),
        "accepted": base.filter(status="accepted").count(),
        "comments": Comment.objects.filter(term__in=base, status="visible").count(),
        "contributors": Profile.objects.filter(user__is_active=True).count(),
    }
    return render(request, "lexicon/home.html", {
        "featured_terms": featured,
        "new_terms": newest,
        "active_terms": active,
        "word_classes": classes,
        "collections": collections,
        "stats": stats,
        "page_title": "WorldWORDS ANTIBIBEL",
    })


def explore(request, lang):
    require_language(lang)
    qs = public_terms().select_related("word_class", "submitted_by").annotate(
        comment_count=Count("comments", filter=Q(comments__status="visible"), distinct=True)
    )
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    word_class = request.GET.get("word_class", "").strip()
    origin = request.GET.get("origin", "").strip()
    language = request.GET.get("language", "").strip()
    tag = request.GET.get("tag", "").strip()
    sort = request.GET.get("sort", "alphabetical")

    if query:
        qs = qs.filter(
            Q(raw_form__icontains=query)
            | Q(canonical_form__icontains=query)
            | Q(exact_input__icontains=query)
            | Q(origin_note__icontains=query)
            | Q(definitions__icontains=query)
        )
    if status in dict(Term.STATUS_CHOICES):
        qs = qs.filter(status=status)
    if word_class:
        qs = qs.filter(word_class__slug=word_class)
    if origin:
        qs = qs.filter(authorship_status=origin)
    if language in SUPPORTED:
        qs = qs.filter(language_of_origin=language)
    if tag:
        qs = qs.filter(tags__slug=tag)

    if sort == "newest":
        qs = qs.order_by("-created_at")
    elif sort == "discussed":
        qs = qs.order_by("-comment_count", "canonical_form")
    elif sort == "status":
        qs = qs.order_by("status", "canonical_form")
    else:
        qs = qs.order_by("canonical_form", "raw_form")

    paginator = Paginator(qs.distinct(), 24)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "lexicon/explore.html", {
        "page": page,
        "query": query,
        "filters": {"status": status, "word_class": word_class, "origin": origin, "language": language, "tag": tag, "sort": sort},
        "word_classes": WordClass.objects.all(),
        "tags": Tag.objects.all(),
        "status_choices": Term.STATUS_CHOICES,
        "authorship_choices": Term.AUTHORSHIP_CHOICES,
        "page_title": get_text(lang)["nav"]["explore"],
    })


def random_term(request, lang):
    require_language(lang)
    ids = list(public_terms().values_list("pk", flat=True))
    if not ids:
        return redirect("lexicon:explore", lang=lang)
    term = Term.objects.get(pk=random.choice(ids))
    return redirect(term.get_absolute_url(lang))


def term_detail(request, lang, slug):
    require_language(lang)
    term = get_object_or_404(public_terms().select_related("word_class", "submitted_by", "accepted_by", "merged_into"), slug=slug)
    reply_qs = Comment.objects.filter(status="visible").select_related("author", "author__profile").prefetch_related("reactions")
    comments = (
        term.comments.filter(status="visible", parent__isnull=True)
        .select_related("author", "author__profile")
        .prefetch_related(Prefetch("replies", queryset=reply_qs), "reactions")
    )
    relations = list(term.outgoing_relations.select_related("target")) + list(term.incoming_relations.select_related("source"))
    proposals = term.contribution_proposals.filter(status="accepted").select_related("proposed_by")
    followed = request.user.is_authenticated and Follow.objects.filter(user=request.user, term=term).exists()

    definitions = term.definitions if isinstance(term.definitions, dict) else {}
    available_languages = [code for code in ("de", "en", "es") if definitions.get(code)]
    primary_language = lang if definitions.get(lang) else ("de" if definitions.get("de") else (available_languages[0] if available_languages else lang))

    def clean_definition_block(value):
        if isinstance(value, str):
            return {"short": value, "long": "", "depth": value}
        value = value if isinstance(value, dict) else {}
        short = value.get("short") or value.get("provisional") or value.get("long") or ""
        long = value.get("long") or ""
        depth = long if long and long.strip() != short.strip() else ""
        return {"short": short, "long": long, "depth": depth}

    primary_definition = clean_definition_block(definitions.get(primary_language))
    secondary_definitions = [
        {"code": code, "block": clean_definition_block(definitions.get(code))}
        for code in available_languages
        if code != primary_language
    ]
    boundary_map = term.not_meant if isinstance(term.not_meant, dict) else {}
    meaning_boundaries = boundary_map.get(lang) or boundary_map.get(primary_language) or []

    return render(request, "lexicon/term_detail.html", {
        "term": term,
        "comments": comments,
        "relations": relations,
        "accepted_contributions": proposals,
        "provenance": term.provenance_events.select_related("actor_user").all(),
        "decisions": term.decisions.select_related("decided_by").all(),
        "comment_form": CommentForm(lang=lang),
        "contribution_form": ContributionProposalForm(lang=lang),
        "report_form": ReportForm(lang=lang),
        "followed": followed,
        "primary_definition": primary_definition,
        "primary_definition_language": primary_language,
        "secondary_definitions": secondary_definitions,
        "meaning_boundaries": meaning_boundaries,
        "page_title": term.canonical_form,
        "meta_description": term.definition(lang, "short")[:280],
    })


@lang_login_required
def submit_term(request, lang):
    if getattr(request.user.profile, "is_muted", False):
        messages.error(request, "Dieses Konto kann derzeit nichts einreichen.")
        return redirect("lexicon:home", lang=lang)
    form = TermSubmissionForm(request.POST or None, request.FILES or None, lang=lang)
    if request.method == "POST" and form.is_valid():
        existing = public_terms().filter(raw_form__iexact=form.cleaned_data["raw_form"]).first()
        if existing:
            messages.info(request, "Diese Rohform existiert bereits. Du kannst dort Herkunft, Deutung oder Varianten ergänzen.")
            return redirect(existing.get_absolute_url(lang))
        recent = Term.objects.filter(submitted_by=request.user, created_at__gte=timezone.now() - timedelta(minutes=2)).count()
        if recent >= 3:
            form.add_error(None, "Drei Einreichungen in zwei Minuten reichen selbst für enthusiastische Wortgeburten. Bitte kurz langsamer.")
        else:
            definitions = {}
            for code in SUPPORTED:
                text = form.cleaned_data.get(f"definition_{code}", "").strip()
                if text:
                    definitions[code] = {"short": text, "long": text}
            with transaction.atomic():
                term = Term.objects.create(
                    raw_form=form.cleaned_data["raw_form"],
                    canonical_form=form.cleaned_data["raw_form"],
                    language_of_origin=form.cleaned_data["language_of_origin"],
                    word_class=form.cleaned_data.get("word_class"),
                    authorship_status=form.cleaned_data["authorship_status"],
                    submitted_by=request.user,
                    submitted_by_label=display_name(request.user),
                    origin_contributors=[request.user.username],
                    exact_input=form.cleaned_data["exact_input"],
                    source_ref=form.cleaned_data.get("source_ref", ""),
                    definitions=definitions,
                    cover_image=form.cleaned_data.get("cover_image"),
                    status="submitted",
                    is_public=True,
                    discussion_open=True,
                )
                ProvenanceEvent.objects.create(
                    term=term,
                    event_type="submission",
                    actor_user=request.user,
                    actor_label=display_name(request.user),
                    source_ref=term.source_ref,
                    exact_input=term.exact_input,
                    payload={"raw_form": term.raw_form, "authorship_status": term.authorship_status},
                )
                Follow.objects.get_or_create(user=request.user, term=term)
            notify_curators("new_term", f"Neue Wortform: {term.raw_form}", "Öffentlich eingereicht und sofort diskutierbar.", term.get_absolute_url(lang), {"term": str(term.pk)})
            messages.success(request, "Das Wort ist jetzt öffentlich im Sammelbecken und kann diskutiert werden.")
            return redirect(term.get_absolute_url(lang))
    return render(request, "lexicon/submit.html", {"form": form, "page_title": get_text(lang)["nav"]["submit"]})


@lang_login_required
@require_POST
def add_comment(request, lang, slug):
    term = get_object_or_404(public_terms(), slug=slug)
    if not term.discussion_open:
        messages.error(request, "Diese Diskussion ist derzeit geschlossen.")
        return redirect(term.get_absolute_url(lang))
    if getattr(request.user.profile, "is_muted", False):
        messages.error(request, "Dieses Konto kann derzeit nicht kommentieren.")
        return redirect(term.get_absolute_url(lang))
    if Comment.objects.filter(author=request.user, created_at__gte=timezone.now() - timedelta(seconds=12)).exists():
        messages.error(request, "Bitte lass zwischen zwei Beiträgen einen kurzen Atemzug.")
        return redirect(term.get_absolute_url(lang))
    form = CommentForm(request.POST, lang=lang)
    parent = None
    parent_id = request.POST.get("parent")
    if parent_id:
        parent = get_object_or_404(Comment, pk=parent_id, term=term, status="visible")
    if form.is_valid():
        comment = form.save(commit=False)
        comment.term = term
        comment.author = request.user
        comment.author_label = display_name(request.user)
        comment.parent = parent
        comment.is_curator_note = request.user.is_staff and request.POST.get("curator_note") == "1"
        comment.save()
        Follow.objects.get_or_create(user=request.user, term=term)
        url = term.get_absolute_url(lang) + f"#comment-{comment.pk}"
        recipients = set(term.followers.exclude(user=request.user).values_list("user_id", flat=True))
        if parent and parent.author_id and parent.author_id != request.user.id:
            recipients.add(parent.author_id)
        from django.contrib.auth import get_user_model
        for user in get_user_model().objects.filter(pk__in=recipients):
            notify(user, "comment", f"Neue Spur bei {term.raw_form}", f"{display_name(request.user)} hat geantwortet.", url, {"term": str(term.pk), "comment": str(comment.pk)})
        messages.success(request, "Beitrag hinzugefügt.")
        return redirect(url)
    messages.error(request, "Der Beitrag konnte nicht gespeichert werden.")
    return redirect(term.get_absolute_url(lang) + "#discussion")


@lang_login_required
@require_http_methods(["GET", "POST"])
def edit_comment(request, lang, comment_id):
    comment = get_object_or_404(Comment.objects.select_related("term"), pk=comment_id, status="visible")
    allowed = request.user.is_staff or (comment.author_id == request.user.id and comment.created_at >= timezone.now() - timedelta(minutes=30))
    if not allowed:
        raise Http404
    form = CommentForm(request.POST or None, instance=comment, lang=lang)
    if request.method == "POST" and form.is_valid():
        CommentRevision.objects.create(comment=comment, body=comment.body, body_html=comment.body_html, edited_by=request.user, reason=request.POST.get("reason", ""))
        edited = form.save(commit=False)
        edited.edited_at = timezone.now()
        edited.save()
        messages.success(request, "Änderung gespeichert; die frühere Fassung bleibt in der Revisionsspur.")
        return redirect(comment.term.get_absolute_url(lang) + f"#comment-{comment.pk}")
    return render(request, "lexicon/comment_edit.html", {"form": form, "comment": comment, "page_title": "Beitrag bearbeiten"})


@lang_login_required
@require_POST
def react_comment(request, lang, comment_id):
    comment = get_object_or_404(Comment.objects.select_related("term"), pk=comment_id, status="visible")
    kind = request.POST.get("kind")
    if kind not in dict(Reaction.KIND_CHOICES):
        raise Http404
    reaction, created = Reaction.objects.get_or_create(comment=comment, user=request.user, kind=kind)
    if not created:
        reaction.delete()
    return redirect(comment.term.get_absolute_url(lang) + f"#comment-{comment.pk}")


@lang_login_required
@require_POST
def toggle_follow(request, lang, slug):
    term = get_object_or_404(public_terms(), slug=slug)
    follow, created = Follow.objects.get_or_create(user=request.user, term=term)
    if not created:
        follow.delete()
    return redirect(term.get_absolute_url(lang))


@lang_login_required
@require_POST
def add_contribution(request, lang, slug):
    term = get_object_or_404(public_terms(), slug=slug)
    form = ContributionProposalForm(request.POST, lang=lang)
    if form.is_valid():
        item = form.save(commit=False)
        item.term = term
        item.proposed_by = request.user
        item.save()
        notify_curators("contribution", f"Ergänzung zu {term.raw_form}", item.get_kind_display(), term.get_absolute_url(lang), {"contribution": str(item.pk)})
        messages.success(request, "Die Ergänzung liegt in Daniels Inbox. Sie bleibt dir zugeordnet.")
    else:
        messages.error(request, "Die Ergänzung konnte nicht gespeichert werden.")
    return redirect(term.get_absolute_url(lang) + "#contribute")


@lang_login_required
@require_POST
def report_term(request, lang, slug):
    term = get_object_or_404(public_terms(), slug=slug)
    form = ReportForm(request.POST, lang=lang)
    if form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.term = term
        report.save()
        notify_curators("report", f"Meldung zu {term.raw_form}", report.get_reason_display(), term.get_absolute_url(lang), {"report": report.pk})
        messages.success(request, "Die Meldung wurde an das Kuratorium geschickt.")
    return redirect(term.get_absolute_url(lang))


@require_http_methods(["GET", "POST"])
def register(request, lang):
    require_language(lang)
    if request.user.is_authenticated:
        return redirect("lexicon:dashboard", lang=lang)
    form = RegisterForm(request.POST or None, lang=lang)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Dein Konto ist angelegt. Deine künftigen Spuren bleiben dir zugeordnet.")
        return redirect("lexicon:dashboard", lang=lang)
    return render(request, "registration/register.html", {"form": form, "page_title": get_text(lang)["auth"]["register_title"]})


@require_http_methods(["GET", "POST"])
def login_view(request, lang):
    require_language(lang)
    if request.user.is_authenticated:
        return redirect("lexicon:dashboard", lang=lang)
    form = LoginForm(request, data=request.POST or None, lang=lang)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect("lexicon:dashboard", lang=lang)
    return render(request, "registration/login.html", {"form": form, "next": request.GET.get("next", ""), "page_title": get_text(lang)["auth"]["login_title"]})


@lang_login_required
@require_http_methods(["GET", "POST"])
def password_change(request, lang):
    form = LocalizedPasswordChangeForm(request.user, request.POST or None, lang=lang)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, get_text(lang)["auth"]["password_changed"])
        return redirect("lexicon:dashboard", lang=lang)
    return render(request, "registration/password_change.html", {
        "form": form,
        "page_title": get_text(lang)["auth"]["change_password"],
    })


@require_POST
def logout_view(request, lang):
    require_language(lang)
    logout(request)
    return redirect("lexicon:home", lang=lang)


@lang_login_required
def dashboard(request, lang):
    profile = request.user.profile
    return render(request, "lexicon/dashboard.html", {
        "profile": profile,
        "submitted_terms": request.user.submitted_terms.order_by("-created_at")[:20],
        "followed_terms": Term.objects.filter(followers__user=request.user, is_public=True).order_by("canonical_form")[:20],
        "contributions": request.user.word_contributions.select_related("term").order_by("-created_at")[:20],
        "page_title": get_text(lang)["nav"]["dashboard"],
    })


@lang_login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request, lang):
    form = ProfileForm(request.POST or None, instance=request.user.profile, lang=lang)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil gespeichert.")
        return redirect("lexicon:dashboard", lang=lang)
    return render(request, "lexicon/profile_edit.html", {"form": form, "page_title": "Profil"})


def people(request, lang):
    require_language(lang)
    profiles = Profile.objects.filter(user__is_active=True).annotate(
        term_count=Count("user__submitted_terms", filter=Q(user__submitted_terms__is_public=True), distinct=True),
        comment_count=Count("user__word_comments", filter=Q(user__word_comments__status="visible"), distinct=True),
    ).order_by("display_name", "user__username")
    return render(request, "lexicon/people.html", {"profiles": profiles, "page_title": get_text(lang)["nav"]["people"]})


def person(request, lang, username):
    require_language(lang)
    profile = get_object_or_404(Profile.objects.select_related("user"), user__username=username, user__is_active=True)
    return render(request, "lexicon/person.html", {
        "profile": profile,
        "terms": profile.user.submitted_terms.filter(is_public=True).order_by("-created_at"),
        "comments": profile.user.word_comments.filter(status="visible").select_related("term").order_by("-created_at")[:30],
        "page_title": profile.display_name or profile.user.username,
    })


@lang_login_required
def notifications(request, lang):
    if request.method == "POST":
        request.user.word_notifications.filter(read_at__isnull=True).update(read_at=timezone.now())
        return redirect("lexicon:notifications", lang=lang)
    return render(request, "lexicon/notifications.html", {
        "notifications": request.user.word_notifications.all()[:100],
        "page_title": "Benachrichtigungen",
    })


def collections(request, lang):
    require_language(lang)
    items = Collection.objects.filter(is_public=True).prefetch_related("items__term").order_by("-featured", "titles")
    return render(request, "lexicon/collections.html", {"collections": items, "page_title": get_text(lang)["nav"]["collections"]})


def collection_detail(request, lang, slug):
    require_language(lang)
    collection = get_object_or_404(Collection.objects.prefetch_related("items__term"), slug=slug, is_public=True)
    return render(request, "lexicon/collection_detail.html", {"collection": collection, "page_title": collection.title(lang)})


STATIC_CONTENT = {
    "about": {
        "de": ("Über die ANTIBIBEL", ["Die WorldWORDS ANTIBIBEL ist ein wachsender Wort-, Herkunfts- und Diskussionskörper. Sie ist ausdrücklich kein endgültiger Kanon.", "Wörter werden als Fundstücke mit Rohform, Kontext, Urheberschaft, Erklärungen, Übersetzungen, Beziehungen und sichtbaren Entscheidungen behandelt."]),
        "en": ("About the ANTIBIBEL", ["The WorldWORDS ANTIBIBEL is a growing body of words, provenance and discussion. It is explicitly not a final canon.", "Words are treated as findings with raw form, context, authorship, explanations, translations, relations and visible decisions."]),
        "es": ("Sobre la ANTIBIBEL", ["La WorldWORDS ANTIBIBEL es un cuerpo creciente de palabras, procedencias y debates. No es un canon definitivo.", "Las palabras se tratan como hallazgos con forma bruta, contexto, autoría, explicaciones, traducciones, relaciones y decisiones visibles."]),
    },
    "governance": {
        "de": ("Aufnahme und Governance", ["Jeder Mensch darf Wörter, Quellen, Deutungen, Übersetzungen, Varianten und Verkörperungen beitragen.", "Daniel ist Gründungskurator und entscheidet, welche Begriffe in sein offizielles Register aufgenommen werden. Eine Einreichung oder Mehrheitsmeinung ersetzt diese Entscheidung nicht.", "Nicht aufgenommene und zurückgestellte Begriffe dürfen sichtbar und diskutierbar bleiben. Aufnahmeentscheidungen werden als eigene, datierte Provenienzereignisse gespeichert."]),
        "en": ("Admission and governance", ["Anyone may contribute words, sources, interpretations, translations, variants and embodiments.", "Daniel is founding curator and decides which terms enter his official registry. A submission or majority opinion does not replace that decision.", "Terms not admitted or deferred may remain visible and discussable. Admission decisions are stored as separate dated provenance events."]),
        "es": ("Admisión y gobernanza", ["Cualquier persona puede aportar palabras, fuentes, interpretaciones, traducciones, variantes y encarnaciones.", "Daniel es el curador fundador y decide qué términos entran en su registro oficial. Un envío o una mayoría no sustituye esa decisión.", "Los términos no admitidos o aplazados pueden seguir visibles y debatibles. Las decisiones se guardan como eventos de procedencia fechados."]),
    },
    "conduct": {
        "de": ("Gesprächsregeln", ["Streite über Bedeutungen, Quellen und Folgen, nicht über den Wert eines Menschen.", "Keine Drohungen, gezielte Belästigung, Veröffentlichung privater Daten, Spam oder absichtliche Herkunftsfälschung.", "Widerspruch ist willkommen. Moderation schützt das Gespräch, nicht die Bequemlichkeit einer Position."]),
        "en": ("Conversation rules", ["Argue about meaning, sources and consequences, not a person's worth.", "No threats, targeted harassment, publication of private data, spam or deliberate falsification of provenance.", "Disagreement is welcome. Moderation protects the conversation, not the comfort of a position."]),
        "es": ("Reglas de conversación", ["Discute significados, fuentes y consecuencias, no el valor de una persona.", "No se permiten amenazas, acoso dirigido, publicación de datos privados, spam ni falsificación deliberada de procedencias.", "El desacuerdo es bienvenido. La moderación protege la conversación, no la comodidad de una postura."]),
    },
    "privacy": {
        "de": ("Datenschutz", ["Für Konten werden Benutzername, Anzeigename, E-Mail-Adresse, Passwort-Hash, Spracheinstellungen und Zeitpunkte gespeichert. Passwörter werden nicht im Klartext gespeichert.", "Bei Einreichungen und Diskussionen werden Inhalte, Zuordnung zum Konto, Zeitpunkte und notwendige technische Serverprotokolle verarbeitet. Öffentliche Beiträge und Anzeigenamen sind öffentlich sichtbar.", "Es werden nur technisch notwendige Sitzungs- und CSRF-Cookies gesetzt. Keine Werbe- oder Tracking-Cookies und keine eingebetteten Drittanbieter-Schriften.", "Du kannst über das Kontaktformular Auskunft, Berichtigung oder Löschung personenbezogener Kontodaten anfragen. Öffentliche Wort- und Diskussionsspuren können aus Gründen der Provenienz anonymisiert statt rückwirkend verfälscht werden."]),
        "en": ("Privacy", ["Accounts store username, display name, email address, password hash, language preferences and timestamps. Passwords are never stored in plain text.", "Submissions and discussions process content, account attribution, timestamps and necessary technical server logs. Public contributions and display names are publicly visible.", "Only technically necessary session and CSRF cookies are used. There are no advertising or tracking cookies and no embedded third-party fonts.", "You may request access, correction or deletion of personal account data through the contact form. Public word and discussion traces may be anonymised rather than retroactively falsified where provenance must be preserved."]),
        "es": ("Privacidad", ["Las cuentas guardan usuario, nombre visible, correo, hash de contraseña, preferencias de idioma y fechas. Las contraseñas nunca se guardan en texto claro.", "Los envíos y debates procesan contenido, atribución de cuenta, fechas y registros técnicos necesarios. Los aportes públicos y nombres visibles son públicos.", "Solo se usan cookies técnicas de sesión y CSRF. No hay cookies publicitarias o de seguimiento ni fuentes externas incrustadas.", "Puedes pedir acceso, corrección o borrado de datos personales mediante el formulario de contacto. Los rastros públicos pueden anonimizarse en vez de falsificarse retroactivamente cuando deba conservarse la procedencia."]),
    },
    "opensource": {
        "de": ("Offener Datenkörper", ["Code steht unter MIT. Öffentliche Inhalte und strukturierte Daten stehen unter CC BY-SA 4.0, soweit an einem einzelnen Beitrag nichts Abweichendes sichtbar markiert ist.", "Der versionierte Export bewahrt aufgenommene Begriffe, Vorschläge, Entscheidungen und Provenienz in maschinenlesbarer Form. Die Live-Datenbank bleibt die Arbeitsoberfläche; veröffentlichte Snapshots sind nachvollziehbare Stände."]),
        "en": ("Open data body", ["Code is licensed under MIT. Public content and structured data are licensed under CC BY-SA 4.0 unless a specific contribution visibly states otherwise.", "The versioned export preserves admitted terms, proposals, decisions and provenance in machine-readable form. The live database is the working surface; published snapshots are traceable states."]),
        "es": ("Cuerpo de datos abierto", ["El código usa licencia MIT. El contenido público y los datos estructurados usan CC BY-SA 4.0 salvo indicación visible distinta en un aporte concreto.", "La exportación versionada conserva términos admitidos, propuestas, decisiones y procedencias en formato legible por máquinas. La base de datos viva es la superficie de trabajo; las instantáneas publicadas son estados trazables."]),
    },
}


def static_page(request, lang, page):
    require_language(lang)
    if page not in STATIC_CONTENT:
        raise Http404
    title, paragraphs = STATIC_CONTENT[page][lang]
    return render(request, "lexicon/static_page.html", {"content_title": title, "paragraphs": paragraphs, "page_title": title})


@require_http_methods(["GET", "POST"])
def contact(request, lang):
    require_language(lang)
    form = ContactForm(request.POST or None, lang=lang, user=request.user)
    if request.method == "POST" and form.is_valid():
        if ContactMessage.objects.filter(email__iexact=form.cleaned_data["email"], created_at__gte=timezone.now() - timedelta(minutes=2)).exists():
            form.add_error(None, "Bitte warte kurz vor der nächsten Nachricht.")
        else:
            item = form.save(commit=False)
            item.user = request.user if request.user.is_authenticated else None
            item.language = lang
            item.save()
            notify_curators("contact", f"Kontakt: {item.subject}", item.name, reverse("lexicon:curation_inbox", kwargs={"lang": "de"}), {"contact": item.pk})
            messages.success(request, "Die Nachricht liegt in Daniels Inbox.")
            return redirect("lexicon:contact", lang=lang)
    return render(request, "lexicon/contact.html", {"form": form, "page_title": "Kontakt"})


@curator_required
def curation_inbox(request, lang):
    pending_terms = Term.objects.filter(status__in=("submitted", "under_review"), is_public=True).select_related("submitted_by", "word_class").order_by("created_at")
    contributions = ContributionProposal.objects.filter(status="pending").select_related("term", "proposed_by").order_by("created_at")
    reports = Report.objects.filter(status__in=("open", "reviewing")).select_related("term", "comment", "reporter").order_by("created_at")
    contacts = ContactMessage.objects.filter(status="open").order_by("created_at")
    return render(request, "lexicon/curation_inbox.html", {
        "pending_terms": pending_terms,
        "pending_contributions": contributions,
        "open_reports": reports,
        "open_contacts": contacts,
        "page_title": get_text(lang)["curation"]["title"],
    })


@curator_required
@require_http_methods(["GET", "POST"])
def curation_term(request, lang, slug):
    term = get_object_or_404(Term.objects.select_related("submitted_by", "word_class"), slug=slug)
    form = CuratorDecisionForm(request.POST or None, lang=lang, term=term)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        old_status = term.status
        rationale = {code: data.get(f"rationale_{code}", "").strip() for code in SUPPORTED if data.get(f"rationale_{code}", "").strip()}
        refs = [line.strip() for line in data.get("evidence_refs", "").splitlines() if line.strip()]
        with transaction.atomic():
            term.status = data["decision"]
            term.decision_rationale = rationale
            term.merged_into = data.get("merged_into") if term.status == "merged" else None
            if term.status == "accepted":
                term.accepted_by = request.user
                term.accepted_at = timezone.now()
            elif old_status != "accepted":
                term.accepted_by = None
                term.accepted_at = None
            term.save()
            decision = ModerationDecision.objects.create(
                term=term,
                decision=term.status,
                rationale=rationale,
                decided_by=request.user,
                decision_basis="daniel-curator-review" if request.user.username.lower() == "daniel" else "authorized-curator-review",
                evidence_refs=refs,
            )
            ProvenanceEvent.objects.create(
                term=term,
                event_type="decision",
                actor_user=request.user,
                actor_label=display_name(request.user),
                source_ref="; ".join(refs),
                payload={"from": old_status, "to": term.status, "rationale": rationale, "decision_id": decision.pk},
            )
        if term.submitted_by_id and term.submitted_by_id != request.user.id:
            notify(term.submitted_by, "decision", f"Entscheidung zu {term.raw_form}", term.status_label(lang), term.get_absolute_url(lang), {"term": str(term.pk), "status": term.status})
        messages.success(request, "Entscheidung und Provenienzspur wurden gespeichert.")
        return redirect("lexicon:curation_term", lang=lang, slug=slug)
    return render(request, "lexicon/curation_term.html", {
        "term": term,
        "form": form,
        "decisions": term.decisions.select_related("decided_by").all(),
        "provenance": term.provenance_events.select_related("actor_user").all(),
        "page_title": f"Kuratorium · {term.raw_form}",
    })


@curator_required
@require_POST
def review_contribution(request, lang, contribution_id):
    item = get_object_or_404(ContributionProposal.objects.select_related("term", "proposed_by"), pk=contribution_id, status="pending")
    action = request.POST.get("action")
    if action not in ("accepted", "rejected"):
        raise Http404
    item.status = action
    item.reviewed_by = request.user
    item.reviewed_at = timezone.now()
    item.review_note = request.POST.get("review_note", "")[:4000]
    item.save()
    if action == "accepted":
        term = item.term
        if item.kind in ("definition", "translation"):
            definitions = dict(term.definitions)
            block = dict(definitions.get(item.language) or {})
            accepted = list(block.get("accepted_contributions") or [])
            accepted.append({"text": item.proposed_text, "contributor": display_name(item.proposed_by), "date": item.created_at.date().isoformat(), "contribution_id": str(item.pk)})
            block["accepted_contributions"] = accepted
            definitions[item.language] = block
            term.definitions = definitions
            term.save()
        elif item.kind == "variant":
            variants = list(term.variants)
            variants.append({"form": item.proposed_text, "relation": "accepted-community-variant", "contributor": display_name(item.proposed_by)})
            term.variants = variants
            term.save()
        elif item.kind == "embodiment":
            embodiments = list(term.embodiments)
            embodiments.append({"value": item.proposed_text, "kind": "community-contribution", "contributor": display_name(item.proposed_by), "date": item.created_at.date().isoformat()})
            term.embodiments = embodiments
            term.save()
        ProvenanceEvent.objects.create(
            term=term,
            event_type="correction" if item.kind == "origin" else item.kind if item.kind in dict(ProvenanceEvent.TYPE_CHOICES) else "definition",
            actor_user=item.proposed_by,
            actor_label=display_name(item.proposed_by),
            source_ref=item.source_ref,
            exact_input=item.proposed_text,
            payload={"accepted_by": display_name(request.user), "contribution_id": str(item.pk), "kind": item.kind},
        )
    if item.proposed_by:
        notify(item.proposed_by, "contribution_review", f"Ergänzung zu {item.term.raw_form}", item.get_status_display(), item.term.get_absolute_url(lang), {"contribution": str(item.pk)})
    messages.success(request, "Ergänzung geprüft.")
    return redirect("lexicon:curation_inbox", lang=lang)


@curator_required
@require_POST
def review_report(request, lang, report_id):
    item = get_object_or_404(Report, pk=report_id)
    action = request.POST.get("action", "resolved")
    if action not in ("reviewing", "resolved", "dismissed"):
        raise Http404
    item.status = action
    item.assigned_to = request.user
    item.resolution = request.POST.get("resolution", "")[:4000]
    item.resolved_at = timezone.now() if action in ("resolved", "dismissed") else None
    item.save()
    if request.POST.get("hide_comment") == "1" and item.comment_id:
        item.comment.status = "hidden"
        item.comment.save()
    messages.success(request, "Meldung bearbeitet.")
    return redirect("lexicon:curation_inbox", lang=lang)


@curator_required
@require_POST
def handle_contact(request, lang, contact_id):
    item = get_object_or_404(ContactMessage, pk=contact_id)
    item.status = request.POST.get("status") if request.POST.get("status") in dict(ContactMessage.STATUS_CHOICES) else "closed"
    item.handled_by = request.user
    item.internal_note = request.POST.get("internal_note", "")[:4000]
    item.save()
    return redirect("lexicon:curation_inbox", lang=lang)


@curator_required
@require_POST
def export_public(request, lang):
    try:
        call_command("export_public_registry")
        messages.success(request, "Der öffentliche Datenkörper wurde atomar neu erzeugt.")
    except Exception as exc:
        messages.error(request, f"Export fehlgeschlagen: {exc}")
    return redirect("lexicon:curation_inbox", lang=lang)


@require_GET
def api_terms(request):
    qs = public_terms().select_related("word_class")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if query:
        qs = qs.filter(Q(raw_form__icontains=query) | Q(canonical_form__icontains=query) | Q(definitions__icontains=query))
    if status in dict(Term.STATUS_CHOICES):
        qs = qs.filter(status=status)
    data = [term_to_dict(term, include_detail=False) for term in qs[:500]]
    return JsonResponse({"count": len(data), "results": data})


@require_GET
def api_term(request, slug):
    term = get_object_or_404(public_terms().select_related("word_class"), slug=slug)
    return JsonResponse(term_to_dict(term, include_detail=True))


def term_to_dict(term, include_detail=True):
    data = {
        "id": str(term.pk),
        "external_id": term.external_id,
        "slug": term.slug,
        "raw_form": term.raw_form,
        "canonical_form": term.canonical_form,
        "status": term.status,
        "language_of_origin": term.language_of_origin,
        "word_class": term.word_class.slug if term.word_class else None,
        "authorship_status": term.authorship_status,
        "created_at": term.created_at.isoformat(),
        "updated_at": term.updated_at.isoformat(),
    }
    if include_detail:
        data.update({
            "definitions": term.definitions,
            "not_meant": term.not_meant,
            "variants": term.variants,
            "components": term.components,
            "embodiments": term.embodiments,
            "origin_contributors": term.origin_contributors,
            "first_seen_date": term.first_seen_date.isoformat() if term.first_seen_date else None,
            "first_seen_precision": term.first_seen_precision,
            "exact_input": term.exact_input,
            "source_ref": term.source_ref,
            "origin_note": term.origin_note,
            "decision_rationale": term.decision_rationale,
            "accepted_at": term.accepted_at.isoformat() if term.accepted_at else None,
            "provenance": [{"type": event.event_type, "actor": event.actor_label, "at": event.event_at.isoformat(), "source_ref": event.source_ref, "exact_input": event.exact_input, "payload": event.payload, "truth_class": event.truth_class} for event in term.provenance_events.all()],
        })
    return data


@require_GET
def robots(request, lang):
    require_language(lang)
    prefix = settings.FORCE_SCRIPT_NAME
    return HttpResponse(f"User-agent: *\nAllow: {prefix}/\nDisallow: {prefix}/admin/\nDisallow: {prefix}/de/kuratorium/\nSitemap: https://flextrawurst.de{prefix}/de/sitemap.xml\n", content_type="text/plain")


@require_GET
def sitemap(request, lang):
    require_language(lang)
    base = f"https://flextrawurst.de{settings.FORCE_SCRIPT_NAME}"
    urls = [f"{base}/{lang}/", f"{base}/{lang}/woerter/", f"{base}/{lang}/wege/", f"{base}/{lang}/mitwirkende/"]
    urls += [f"{base}{term.get_absolute_url(lang).replace(settings.FORCE_SCRIPT_NAME, '')}" for term in public_terms().only("slug")]
    body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{url}</loc></url>" for url in urls) + "</urlset>"
    return HttpResponse(body, content_type="application/xml")
