from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .i18n import get_text
from .models import (
    Comment,
    ContactMessage,
    ContributionProposal,
    Profile,
    Report,
    Term,
    WordClass,
    SUPPORTED_LANGUAGES,
    ORIGIN_LANGUAGES,
)

User = get_user_model()

LABELS = {
    "de": {
        "raw_form": "Rohform des Wortes",
        "language_of_origin": "Ursprungssprache",
        "word_class": "Wortart",
        "authorship_status": "Wie ist die Urheberschaft bekannt?",
        "exact_input": "Ursprünglicher Satz oder Zusammenhang",
        "source_ref": "Quelle oder Fundort",
        "definition_de": "Erklärung auf Deutsch",
        "definition_en": "Erklärung auf Englisch",
        "definition_es": "Erklärung auf Spanisch",
        "cover_image": "Darstellungsbild",
        "consent": "Freigabe",
        "body": "Dein Beitrag",
        "kind": "Art der Ergänzung",
        "language": "Sprache",
        "proposed_text": "Vorgeschlagener Inhalt",
        "rationale": "Warum ist diese Ergänzung wichtig?",
        "reason": "Grund",
        "details": "Details",
        "display_name": "Anzeigename",
        "preferred_language": "Bevorzugte Sprache",
        "bio": "Kurz über dich",
        "website": "Eigene Website",
        "decision": "Entscheidung",
        "rationale_de": "Begründung auf Deutsch",
        "rationale_en": "Begründung auf Englisch",
        "rationale_es": "Begründung auf Spanisch",
        "merged_into": "Als Variante verbinden mit",
        "evidence_refs": "Belegstellen, eine pro Zeile",
    },
    "en": {
        "raw_form": "Raw word form",
        "language_of_origin": "Language of origin",
        "word_class": "Word class",
        "authorship_status": "What is known about authorship?",
        "exact_input": "Original sentence or context",
        "source_ref": "Source or place found",
        "definition_de": "Explanation in German",
        "definition_en": "Explanation in English",
        "definition_es": "Explanation in Spanish",
        "cover_image": "Display image",
        "consent": "Permission",
        "body": "Your contribution",
        "kind": "Kind of addition",
        "language": "Language",
        "proposed_text": "Proposed content",
        "rationale": "Why does this addition matter?",
        "reason": "Reason",
        "details": "Details",
        "display_name": "Display name",
        "preferred_language": "Preferred language",
        "bio": "About you",
        "website": "Website",
        "decision": "Decision",
        "rationale_de": "Rationale in German",
        "rationale_en": "Rationale in English",
        "rationale_es": "Rationale in Spanish",
        "merged_into": "Connect as variant of",
        "evidence_refs": "Evidence references, one per line",
    },
    "es": {
        "raw_form": "Forma bruta de la palabra",
        "language_of_origin": "Lengua de origen",
        "word_class": "Clase de palabra",
        "authorship_status": "¿Qué se sabe de la autoría?",
        "exact_input": "Frase o contexto original",
        "source_ref": "Fuente o lugar de hallazgo",
        "definition_de": "Explicación en alemán",
        "definition_en": "Explicación en inglés",
        "definition_es": "Explicación en español",
        "cover_image": "Imagen de presentación",
        "consent": "Permiso",
        "body": "Tu aporte",
        "kind": "Tipo de añadido",
        "language": "Idioma",
        "proposed_text": "Contenido propuesto",
        "rationale": "¿Por qué importa este añadido?",
        "reason": "Motivo",
        "details": "Detalles",
        "display_name": "Nombre visible",
        "preferred_language": "Idioma preferido",
        "bio": "Sobre ti",
        "website": "Sitio web",
        "decision": "Decisión",
        "rationale_de": "Justificación en alemán",
        "rationale_en": "Justificación en inglés",
        "rationale_es": "Justificación en español",
        "merged_into": "Conectar como variante de",
        "evidence_refs": "Referencias, una por línea",
    },
}


class LocalizedModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if hasattr(obj, "label"):
            return obj.label(self.lang)
        return str(obj)


def translated_choices(choices, mapping):
    return [(value, mapping.get(value, label)) for value, label in choices]


class StyledFormMixin:
    lang = "de"

    def apply_style(self):
        labels = LABELS.get(self.lang, LABELS["de"])
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "field-input")
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 5)
            if name in labels:
                field.label = labels[name]
            if field.required:
                field.widget.attrs.setdefault("aria-required", "true")


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        self.fields["username"].label = get_text(lang)["auth"]["username"]
        self.fields["password"].label = get_text(lang)["auth"]["password"]
        self.apply_style()


class LocalizedPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        labels = {
            "de": {"old_password": "Bisheriges Passwort", "new_password1": "Neues Passwort", "new_password2": "Neues Passwort wiederholen"},
            "en": {"old_password": "Current password", "new_password1": "New password", "new_password2": "Repeat new password"},
            "es": {"old_password": "Contraseña actual", "new_password1": "Nueva contraseña", "new_password2": "Repetir nueva contraseña"},
        }[lang]
        for name, label in labels.items():
            self.fields[name].label = label
        self.apply_style()


class RegisterForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(max_length=80)
    preferred_language = forms.ChoiceField(choices=SUPPORTED_LANGUAGES)
    consent = forms.BooleanField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "display_name", "email", "preferred_language", "password1", "password2", "consent")

    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        self.fields["username"].label = get_text(lang)["auth"]["username"]
        self.fields["email"].label = get_text(lang)["auth"]["email"]
        self.fields["display_name"].label = get_text(lang)["auth"]["display_name"]
        text = get_text(lang)
        self.fields["preferred_language"].choices = [(code, text["origin_language"][code]) for code, _ in SUPPORTED_LANGUAGES]
        self.fields["consent"].label = text["forms"]["consent"]
        self.apply_style()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Diese E-Mail-Adresse wird bereits verwendet.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile = user.profile
            profile.display_name = self.cleaned_data["display_name"]
            profile.preferred_language = self.cleaned_data["preferred_language"]
            profile.save()
        return user


class TermSubmissionForm(StyledFormMixin, forms.Form):
    raw_form = forms.CharField(max_length=180)
    language_of_origin = forms.ChoiceField(choices=ORIGIN_LANGUAGES, initial="de")
    word_class = LocalizedModelChoiceField(queryset=WordClass.objects.all(), required=False)
    authorship_status = forms.ChoiceField(choices=Term.AUTHORSHIP_CHOICES, initial="claimed-by-submitter")
    exact_input = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}), max_length=12000)
    source_ref = forms.CharField(max_length=600, required=False)
    definition_de = forms.CharField(widget=forms.Textarea, max_length=8000)
    definition_en = forms.CharField(widget=forms.Textarea, max_length=8000, required=False)
    definition_es = forms.CharField(widget=forms.Textarea, max_length=8000, required=False)
    cover_image = forms.ImageField(required=False)
    consent = forms.BooleanField(required=True)

    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        self.fields["word_class"] = LocalizedModelChoiceField(
            queryset=WordClass.objects.all(), required=False, lang=lang, empty_label="—"
        )
        text = get_text(lang)
        self.fields["language_of_origin"].choices = translated_choices(ORIGIN_LANGUAGES, text["origin_language"])
        self.fields["authorship_status"].choices = translated_choices(Term.AUTHORSHIP_CHOICES, text["authorship"])
        self.fields["raw_form"].help_text = text["forms"]["raw_help"]
        self.fields["exact_input"].help_text = text["forms"]["exact_help"]
        self.fields["consent"].label = text["forms"]["consent"]
        self.apply_style()

    def clean_raw_form(self):
        value = self.cleaned_data["raw_form"]
        if not value.strip():
            raise ValidationError("Die Rohform darf nicht leer sein.")
        if value != value.strip():
            raise ValidationError("Bitte entferne nur versehentliche Leerzeichen am Anfang oder Ende. Innerhalb der Rohform bleibt alles unverändert.")
        return value

    def clean_cover_image(self):
        image = self.cleaned_data.get("cover_image")
        if image and image.size > 5 * 1024 * 1024:
            raise ValidationError("Das Bild darf höchstens 5 MB groß sein.")
        return image


class CommentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("language", "body")
        widgets = {"body": forms.Textarea(attrs={"rows": 5, "maxlength": 12000})}

    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        self.fields["language"].initial = lang
        text = get_text(lang)
        self.fields["language"].choices = [(code, text["origin_language"][code]) for code, _ in SUPPORTED_LANGUAGES]
        self.apply_style()


class ContributionProposalForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContributionProposal
        fields = ("kind", "language", "proposed_text", "source_ref", "rationale")
        widgets = {
            "proposed_text": forms.Textarea(attrs={"rows": 6}),
            "rationale": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        self.fields["language"].initial = lang
        text = get_text(lang)
        self.fields["language"].choices = [(code, text["origin_language"][code]) for code, _ in SUPPORTED_LANGUAGES]
        self.fields["kind"].choices = translated_choices(ContributionProposal.KIND_CHOICES, text["contribution_kind"])
        self.apply_style()


class ReportForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Report
        fields = ("reason", "details")
        widgets = {"details": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        self.fields["reason"].choices = translated_choices(Report.REASON_CHOICES, get_text(lang)["report_reason"])
        self.apply_style()


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("display_name", "preferred_language", "bio", "website")
        widgets = {"bio": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, lang="de", **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        text = get_text(lang)
        self.fields["preferred_language"].choices = [(code, text["origin_language"][code]) for code, _ in SUPPORTED_LANGUAGES]
        self.apply_style()


class CuratorDecisionForm(StyledFormMixin, forms.Form):
    decision = forms.ChoiceField(choices=Term.STATUS_CHOICES)
    rationale_de = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))
    rationale_en = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False)
    rationale_es = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False)
    merged_into = forms.ModelChoiceField(queryset=Term.objects.none(), required=False)
    evidence_refs = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False)

    def __init__(self, *args, lang="de", term=None, **kwargs):
        self.lang = lang
        self.term = term
        super().__init__(*args, **kwargs)
        queryset = Term.objects.filter(is_public=True).exclude(pk=getattr(term, "pk", None)).order_by("canonical_form")
        self.fields["decision"].choices = translated_choices(Term.STATUS_CHOICES, get_text(lang)["status"])
        self.fields["merged_into"].queryset = queryset
        if term:
            self.fields["decision"].initial = term.status
            self.fields["rationale_de"].initial = term.decision_rationale.get("de", "")
            self.fields["rationale_en"].initial = term.decision_rationale.get("en", "")
            self.fields["rationale_es"].initial = term.decision_rationale.get("es", "")
            self.fields["merged_into"].initial = term.merged_into_id
        self.apply_style()

    def clean(self):
        data = super().clean()
        if data.get("decision") == "merged" and not data.get("merged_into"):
            self.add_error("merged_into", "Für diesen Status ist ein Zielbegriff nötig.")
        return data


class ContactForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "body")
        widgets = {"body": forms.Textarea(attrs={"rows": 7})}

    def __init__(self, *args, lang="de", user=None, **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["name"].initial = getattr(user.profile, "display_name", "") or user.username
            self.fields["email"].initial = user.email
        labels = {
            "de": {"name": "Name", "email": "E-Mail", "subject": "Betreff", "body": "Nachricht"},
            "en": {"name": "Name", "email": "Email", "subject": "Subject", "body": "Message"},
            "es": {"name": "Nombre", "email": "Correo", "subject": "Asunto", "body": "Mensaje"},
        }[lang]
        for key, value in labels.items():
            self.fields[key].label = value
        self.apply_style()
