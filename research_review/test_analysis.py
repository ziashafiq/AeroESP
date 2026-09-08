"""
The study analysis page.

Its charts are aggregates over ExpertReview, and the one thing they may
never carry is where a question came from. The blinding tests here
mirror test_provenance_never_appears_on_the_review_page: same leak
signatures, extended with the run-level fields (provider, displayed
model, condition) that would identify a service just as effectively as
the provenance flag itself.
"""

import pathlib
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from research_review.models import (
    ExpertReview,
    ExpertReviewerProfile,
    ResearchExperiment,
    ResearchQuestion,
    ResearchRun,
    ReviewAssignment,
)


User = get_user_model()


SCORES = {
    "construct_relevance": 5,
    "technical_correctness": 4,
    "linguistic_accuracy": 4,
    "clarity_answerability": 3,
    "source_fidelity": 5,
    "distractor_quality": 3,
    "cefr_alignment": 4,
    "difficulty_alignment": 4,
    "pedagogical_value": 5,
}


class AnalysisFixture(TestCase):

    def setUp(self):
        super().setUp()

        self.experiment = ResearchExperiment.objects.create(
            experiment_id="R901",
            source_id="R901",
            domain="Avionics",
            topic="Inertial navigation",
            protocol="P1",
            source_material="An INS integrates acceleration over time.",
        )

        self.run = ResearchRun.objects.create(
            experiment=self.experiment,
            run_id="R901-run-1",
            provider="Anthropic",
            displayed_model="claude-opus-5",
            condition="Structured / Think ON",
        )

        self.staff = User.objects.create_user(
            username="researcher",
            email="researcher@example.com",
            password="Research-Pass-12345",
            is_staff=True,
        )

        self.reviewer_user = User.objects.create_user(
            username="analysis_reviewer",
            email="analysis_reviewer@example.com",
            password="Reviewer-Pass-12345",
        )

        self.reviewer = ExpertReviewerProfile.objects.create(
            user=self.reviewer_user,
            discipline="AEROSPACE",
            is_active_reviewer=True,
        )

        self.url = reverse("research_review:analysis")

    def make_review(self, item_number, decision, **overrides):

        question = ResearchQuestion.objects.create(
            run=self.run,
            blind_id=f"R901-Q{item_number:03d}",
            item_number=item_number,
            skill="main_idea",
            stem="What does an inertial navigation system integrate?",
            option_a="Acceleration",
            option_b="Cabin pressure",
            option_c="Fuel flow",
            option_d="Runway length",
            correct_answer="A",
        )

        assignment = ReviewAssignment.objects.create(
            reviewer=self.reviewer,
            question=question,
            display_order=item_number,
            status="LOCKED",
        )

        values = dict(SCORES)
        values.update(overrides)

        return ExpertReview.objects.create(
            assignment=assignment,
            overall_decision=decision,
            is_finalized=True,
            reviewer_confidence=4,
            **values,
        )


class AnalysisBlindingTests(AnalysisFixture):
    """
    The study's blinding is a property of the reviewers, not of this
    page - but a chart that split scores by provider would end up
    screenshotted into a paper, or opened on a shared screen, and the
    simplest guarantee is that the origin never reaches the template
    at all.
    """

    LEAK_SIGNATURES = [
        "question_provenance",
        "AI_GENERATED",
        "AI Generated",
        "HUMAN_WRITTEN",
        "Human Written",
        "EXISTING_SOURCE",
        "Existing Source",
        # Run-level identifiers: naming the service is as revealing as
        # naming the provenance.
        "Anthropic",
        "claude-opus-5",
        "Structured / Think ON",
        "displayed_model",
        "condition",
        "provider",
        # And the item identity itself.
        "R901-Q001",
        "blind_id",
    ]

    def test_no_origin_reaches_the_rendered_page(self):

        self.make_review(1, "ACCEPT")
        self.make_review(2, "MINOR_EDIT")

        self.client.force_login(self.staff)

        body = self.client.get(self.url).content.decode()

        for signature in self.LEAK_SIGNATURES:
            with self.subTest(signature=signature):
                self.assertNotIn(
                    signature,
                    body,
                    f"{signature!r} leaked onto the analysis page",
                )

    def test_it_holds_for_every_provenance_value(self):
        """
        Checked across all three values, exactly as the review page is
        - a human-written item must be as unidentifiable as an
        AI-generated one.
        """

        review = self.make_review(1, "ACCEPT")
        question = review.assignment.question

        self.client.force_login(self.staff)

        for value, _label in question.PROVENANCE_CHOICES:

            question.question_provenance = value
            question.save(update_fields=["question_provenance"])

            body = self.client.get(self.url).content.decode()

            for signature in self.LEAK_SIGNATURES:
                with self.subTest(provenance=value, leak=signature):
                    self.assertNotIn(signature, body)

    def test_the_context_carries_no_origin_either(self):
        """
        Belt and braces, matching the review page's own test: even a
        key that the current template never prints would make an
        accidental reference in a future edit trivial.
        """

        self.make_review(1, "ACCEPT")

        self.client.force_login(self.staff)

        context = self.client.get(self.url).context

        for key in (
            "provenance",
            "question_provenance",
            "run",
            "runs",
            "experiment",
            "experiments",
            "provider",
            "providers",
            "condition",
            "conditions",
            "service",
            "services",
            "questions",
        ):
            with self.subTest(key=key):
                self.assertNotIn(key, context)

    def test_the_template_source_never_walks_back_to_a_run(self):
        """
        The context is clean, but a template can follow relations. A
        single {{ review.assignment.question.run.provider }} would
        undo all of the above, so the source is checked directly.
        """

        source = (
            pathlib.Path(settings.BASE_DIR)
            / "research_review" / "templates" / "research_review"
            / "analysis.html"
        ).read_text(encoding="utf-8")

        # Only what actually renders. The prose explaining why these
        # relations are absent naturally has to name them.
        source = re.sub(
            r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}",
            "",
            source,
            flags=re.S,
        )

        for path in (
            ".run",
            ".experiment",
            ".question",
            "provenance",
            "provider",
        ):
            with self.subTest(path=path):
                self.assertNotIn(path, source)


class AnalysisAccessTests(AnalysisFixture):

    def test_staff_may_open_it(self):

        self.client.force_login(self.staff)

        self.assertEqual(
            self.client.get(self.url).status_code,
            200,
        )

    def test_a_reviewer_may_not(self):
        """
        Reviewers are kept out while they are still reviewing: an
        aggregate mean and a decision split are precisely the anchor
        that would pull later judgements toward the group.
        """

        self.client.force_login(self.reviewer_user)

        response = self.client.get(self.url)

        self.assertNotEqual(response.status_code, 200)

    def test_anonymous_visitors_are_redirected_to_sign_in(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("Accept", response.content.decode())


class AnalysisDataTests(AnalysisFixture):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.staff)

    def test_dimension_means_are_averaged_across_reviews(self):

        self.make_review(1, "ACCEPT", construct_relevance=5)
        self.make_review(2, "ACCEPT", construct_relevance=3)

        series = self.client.get(self.url).context["dimension_series"]

        by_label = {row["label"]: row["mean"] for row in series}

        self.assertEqual(by_label["Construct relevance"], 4.0)
        self.assertEqual(len(series), 9)

    def test_unfinalised_reviews_are_excluded(self):
        """
        A draft is a reviewer part-way through an item, not a result.
        """

        self.make_review(1, "ACCEPT")

        draft = self.make_review(2, "REJECT")
        draft.is_finalized = False
        draft.save(update_fields=["is_finalized"])

        response = self.client.get(self.url)

        self.assertEqual(response.context["total"], 1)

        decisions = {
            row["label"]: row["value"]
            for row in response.context["decision_series"]
        }

        self.assertEqual(decisions["Reject"], 0)

    def test_every_decision_appears_even_at_zero(self):
        """
        Built from DECISION_CHOICES rather than from the rows present,
        so "nobody rejected anything" reads as a zero bar instead of a
        missing category.
        """

        self.make_review(1, "ACCEPT")

        series = self.client.get(self.url).context["decision_series"]

        self.assertEqual(
            [row["label"] for row in series],
            ["Accept", "Minor Edit", "Major Edit", "Reject"],
        )

    def test_reviewers_reporting_counts_people_not_reviews(self):

        self.make_review(1, "ACCEPT")
        self.make_review(2, "MINOR_EDIT")

        response = self.client.get(self.url)

        self.assertEqual(response.context["total"], 2)
        self.assertEqual(response.context["reviewers_reporting"], 1)

    def test_an_empty_study_renders_without_charts(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total"], 0)
        self.assertContains(response, "No finalised reviews yet")
        self.assertNotContains(response, 'id="dimensionChart"')

    def test_the_numbers_are_also_available_as_text(self):
        """
        A canvas is unreadable to a screen reader and uncopyable into
        a paper; the table is the accessible and citable form.
        """

        self.make_review(1, "ACCEPT")

        body = self.client.get(self.url).content.decode()

        self.assertIn("<table", body)
        self.assertIn("Construct relevance", body)


class ChartAssetTests(TestCase):
    """
    Charts must not depend on a CDN, and must follow the theme and the
    palette rather than freezing on load-time colours.
    """

    def test_chart_js_is_vendored(self):

        vendored = (
            pathlib.Path(settings.BASE_DIR)
            / "static" / "aeroesp" / "vendor" / "chart.umd.js"
        )

        self.assertTrue(vendored.exists())
        self.assertGreater(vendored.stat().st_size, 100_000)

        head = vendored.read_text(
            encoding="utf-8", errors="replace"
        )[:400]

        self.assertIn("Chart.js v", head)

    def test_no_template_loads_a_chart_library_from_a_cdn(self):
        """
        The AI dashboard used to carry an unpinned
        cdn.jsdelivr.net/npm/chart.js tag: it fails outright on a
        network that cannot reach the CDN, and changed version
        underneath the page whenever upstream published.
        """

        base = pathlib.Path(settings.BASE_DIR)

        offenders = []

        for template in base.rglob("*.html"):
            if "node_modules" in template.parts:
                continue
            if "staticfiles" in template.parts:
                continue

            text = template.read_text(
                encoding="utf-8", errors="replace"
            )

            if "cdn.jsdelivr.net" in text or "unpkg.com" in text:
                offenders.append(str(template.relative_to(base)))

        self.assertEqual(offenders, [])

    def test_no_vendored_asset_points_at_a_file_that_is_not_there(self):
        """
        Chart.js ships with a sourceMappingURL comment. Under
        ManifestStaticFilesStorage that dangling reference makes
        collectstatic raise MissingFileError, and the whole collect
        step fails - which on a build/run split host means a deploy
        that leaves every stylesheet pointing at the previous build.
        It failed silently here before this was caught.
        """

        static_root = (
            pathlib.Path(settings.BASE_DIR) / "static" / "aeroesp"
        )

        offenders = []

        for asset in list(static_root.rglob("*.js")) + list(
            static_root.rglob("*.css")
        ):
            text = asset.read_text(encoding="utf-8", errors="replace")

            for match in re.finditer(
                r"sourceMappingURL=([^\s*]+)", text
            ):
                target = match.group(1)

                if target.startswith("data:"):
                    continue

                if not (asset.parent / target).exists():
                    offenders.append(
                        f"{asset.name} -> {target}"
                    )

        self.assertEqual(offenders, [])

    def test_charts_read_their_colours_from_the_theme_tokens(self):

        source = (
            pathlib.Path(settings.BASE_DIR)
            / "static" / "aeroesp" / "js" / "charts.js"
        ).read_text(encoding="utf-8")

        for token in (
            "--theme-accent",
            "--theme-accent-strong",
            "--theme-text",
            "--theme-border",
        ):
            with self.subTest(token=token):
                self.assertIn(token, source)

    def test_charts_are_rebuilt_when_the_theme_or_palette_changes(self):
        """
        A canvas keeps the pixels it was drawn with. Without this the
        charts would stay on whichever theme was active at page load
        while the rest of the interface moved around them.
        """

        source = (
            pathlib.Path(settings.BASE_DIR)
            / "static" / "aeroesp" / "js" / "charts.js"
        ).read_text(encoding="utf-8")

        self.assertIn("MutationObserver", source)
        self.assertIn('"data-theme"', source)
        self.assertIn('"data-palette"', source)
        self.assertIn("rebuild", source)
