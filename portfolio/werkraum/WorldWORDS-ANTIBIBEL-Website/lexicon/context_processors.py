from django.conf import settings
from .i18n import SUPPORTED, get_text


def site_context(request):
    lang = "de"
    match = getattr(request, "resolver_match", None)
    if match and match.kwargs.get("lang") in SUPPORTED:
        lang = match.kwargs["lang"]
    else:
        path = request.path
        prefix = settings.FORCE_SCRIPT_NAME or ""
        if prefix and path.startswith(prefix):
            path = path[len(prefix):]
        bits = [bit for bit in path.split("/") if bit]
        if bits and bits[0] in SUPPORTED:
            lang = bits[0]

    prefix = settings.FORCE_SCRIPT_NAME or ""
    path = request.path
    relative = path[len(prefix):] if prefix and path.startswith(prefix) else path
    bits = relative.split("/")
    language_switches = []
    for code in SUPPORTED:
        new_bits = list(bits)
        replaced = False
        for index, bit in enumerate(new_bits):
            if bit in SUPPORTED:
                new_bits[index] = code
                replaced = True
                break
        if not replaced:
            new_bits = ["", code, ""]
        switch_path = prefix + "/".join(new_bits)
        if not switch_path.endswith("/") and "." not in switch_path.rsplit("/", 1)[-1]:
            switch_path += "/"
        language_switches.append({"code": code, "url": switch_path})

    unread = 0
    if request.user.is_authenticated:
        unread = request.user.word_notifications.filter(read_at__isnull=True).count()

    return {
        "lang": lang,
        "T": get_text(lang),
        "supported_languages": SUPPORTED,
        "language_switches": language_switches,
        "site_prefix": prefix,
        "site_title": settings.SITE_TITLE,
        "unread_notification_count": unread,
    }
