from django import template
from django.utils.safestring import mark_safe
from lexicon.models import localized

register = template.Library()


@register.filter
def localize(value, lang="de"):
    return localized(value, lang)


@register.filter
def term_definition(term, arg="de:short"):
    parts = str(arg).split(":", 1)
    lang = parts[0] if parts else "de"
    length = parts[1] if len(parts) > 1 else "short"
    return term.definition(lang, length)


@register.filter
def status_label(term, lang="de"):
    return term.status_label(lang)


@register.filter
def get_item(value, key):
    if isinstance(value, dict):
        return value.get(key)
    return None


@register.filter
def reaction_count(comment, kind):
    return comment.reactions.filter(kind=kind).count()


@register.filter
def has_reaction(comment, value):
    try:
        user_id, kind = str(value).split(":", 1)
        return comment.reactions.filter(user_id=int(user_id), kind=kind).exists()
    except Exception:
        return False


@register.filter
def paragraphs(value):
    text = str(value or "")
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    return mark_safe("".join(f"<p>{template.defaultfilters.linebreaksbr(chunk)}</p>" for chunk in chunks))
