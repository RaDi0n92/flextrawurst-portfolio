from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    Comment,
    ContributionProposal,
    Follow,
    ModerationDecision,
    Profile,
    ProvenanceEvent,
    Reaction,
    Term,
    WordClass,
)

User = get_user_model()


@override_settings(
    FORCE_SCRIPT_NAME="/WORLDwordsANTIbibel",
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class WorldWordsFlowTests(TestCase):
    def setUp(self):
        self.word_class = WordClass.objects.create(
            slug="blend",
            labels={"de": "Mischwörter", "en": "Blends", "es": "Mezclas"},
            descriptions={},
            symbol="M",
        )
        self.user = User.objects.create_user(username="mara", email="mara@example.invalid", password="Some-long-passphrase-42")
        self.user.profile.display_name = "Mara"
        self.user.profile.save()
        self.daniel = User.objects.create_superuser(username="daniel", email="", password="Another-long-passphrase-42")
        self.daniel.profile.display_name = "Daniel"
        self.daniel.profile.save()
        self.term = Term.objects.create(
            raw_form="Kabelgedächtnis",
            canonical_form="Kabelgedächtnis",
            language_of_origin="de",
            word_class=self.word_class,
            status="submitted",
            authorship_status="claimed-by-submitter",
            submitted_by=self.user,
            submitted_by_label="Mara",
            origin_contributors=["mara"],
            exact_input="Mein Kabel erinnert sich an die letzte Steckdose.",
            definitions={"de": {"short": "Eine Erinnerung, die an Verbindungsmaterial haftet.", "long": "Eine Erinnerung, die an Verbindungsmaterial haftet."}},
        )
        ProvenanceEvent.objects.create(
            term=self.term,
            event_type="submission",
            actor_user=self.user,
            actor_label="Mara",
            exact_input=self.term.exact_input,
        )

    def url(self, name, **kwargs):
        generated = reverse(f"lexicon:{name}", kwargs={"lang": "de", **kwargs})
        return generated.removeprefix(settings.FORCE_SCRIPT_NAME)

    def test_public_term_is_discussable_before_admission(self):
        response = self.client.get(self.url("term_detail", slug=self.term.slug))
        self.assertContains(response, "Kabelgedächtnis")
        self.assertContains(response, "Eingereicht")
        self.assertContains(response, "Die Diskussion gehört zum Begriff")
        self.client.force_login(self.user)
        response = self.client.post(
            self.url("add_comment", slug=self.term.slug),
            {"language": "de", "body": "Das Wort wirkt auf mich eher wie eine gespeicherte Verbindung."},
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get()
        self.assertEqual(comment.term, self.term)
        self.assertEqual(comment.author_label, "Mara")
        self.assertIn("gespeicherte Verbindung", comment.body_html)

    def test_raw_form_and_exact_input_are_immutable(self):
        self.term.canonical_form = "Kabel-Gedächtnis"
        self.term.save()
        self.term.refresh_from_db()
        self.assertEqual(self.term.raw_form, "Kabelgedächtnis")
        self.term.raw_form = "KabelGedächtnis"
        with self.assertRaises(Exception):
            self.term.save()
        self.term.refresh_from_db()
        self.term.exact_input = "Nachträglich geglättet"
        with self.assertRaises(Exception):
            self.term.save()

    def test_follow_react_and_contribute(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url("toggle_follow", slug=self.term.slug))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Follow.objects.filter(user=self.user, term=self.term).exists())
        comment = Comment.objects.create(term=self.term, author=self.daniel, author_label="Daniel", language="de", body="Eine kuratorische Frage.")
        response = self.client.post(self.url("react_comment", comment_id=comment.pk), {"kind": "counterpoint"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reaction.objects.filter(comment=comment, user=self.user, kind="counterpoint").exists())
        response = self.client.post(
            self.url("add_contribution", slug=self.term.slug),
            {"kind": "translation", "language": "en", "proposed_text": "Cable memory", "source_ref": "", "rationale": "First working translation"},
        )
        self.assertEqual(response.status_code, 302)
        proposal = ContributionProposal.objects.get()
        self.assertEqual(proposal.status, "pending")
        self.assertEqual(proposal.proposed_by, self.user)

    def test_curator_decision_changes_status_without_erasing_discussion(self):
        Comment.objects.create(term=self.term, author=self.user, author_label="Mara", language="de", body="Vor der Aufnahme geschrieben.")
        self.client.force_login(self.daniel)
        response = self.client.post(
            self.url("curation_term", slug=self.term.slug),
            {
                "decision": "accepted",
                "rationale_de": "Aufgenommen, weil Herkunft und Bedeutung nachvollziehbar sind.",
                "rationale_en": "Admitted because provenance and meaning are traceable.",
                "rationale_es": "Admitida porque procedencia y significado son trazables.",
                "merged_into": "",
                "evidence_refs": "source://mara/first-use",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.term.refresh_from_db()
        self.assertEqual(self.term.status, "accepted")
        self.assertEqual(self.term.accepted_by, self.daniel)
        self.assertEqual(Comment.objects.filter(term=self.term).count(), 1)
        self.assertTrue(ModerationDecision.objects.filter(term=self.term, decision="accepted").exists())
        event = ProvenanceEvent.objects.filter(term=self.term, event_type="decision").latest("created_at")
        self.assertEqual(event.payload["from"], "submitted")
        self.assertEqual(event.payload["to"], "accepted")
        response = self.client.get(self.url("term_detail", slug=self.term.slug))
        self.assertContains(response, "Vor der Aufnahme geschrieben")
        self.assertContains(response, "Aufgenommen")

    def test_register_creates_attributed_profile(self):
        response = self.client.post(
            self.url("register"),
            {
                "username": "lina",
                "display_name": "Lina",
                "email": "lina@example.invalid",
                "preferred_language": "es",
                "password1": "A-long-and-not-common-passphrase-907!",
                "password2": "A-long-and-not-common-passphrase-907!",
                "consent": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="lina")
        self.assertEqual(user.profile.display_name, "Lina")
        self.assertEqual(user.profile.preferred_language, "es")

    def test_submission_is_public_immediately(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url("submit_term"),
            {
                "raw_form": "Treppenwetter",
                "language_of_origin": "de",
                "word_class": self.word_class.pk,
                "authorship_status": "claimed-by-submitter",
                "exact_input": "Auf jeder Stufe war heute anderes Wetter.",
                "source_ref": "",
                "definition_de": "Ein Wetterwechsel, der sich wie eine Treppe staffelt.",
                "definition_en": "",
                "definition_es": "",
                "consent": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        term = Term.objects.get(raw_form="Treppenwetter")
        self.assertTrue(term.is_public)
        self.assertTrue(term.discussion_open)
        self.assertEqual(term.status, "submitted")
        self.assertTrue(ProvenanceEvent.objects.filter(term=term, event_type="submission").exists())
        response = self.client.get(self.url("term_detail", slug=term.slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Treppenwetter")
