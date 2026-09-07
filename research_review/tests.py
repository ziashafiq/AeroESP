import csv
import os
import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from .forms import ExpertReviewForm
from .models import (
    ExpertReview,
    ExpertReviewerProfile,
    ReviewAssignment,
    ResearchExperiment,
    ResearchQuestion,
    ResearchRun,
)


class ReviewFixtureMixin:
    """
    One experiment / run / question / reviewer / assignment, shared by
    every test below - the review workflow always needs the full chain.
    """

    def setUp(self):

        super().setUp()

        self.experiment = ResearchExperiment.objects.create(
            experiment_id="R900",
            source_id="R900",
            domain="Propulsion",
            topic="Turbofan efficiency",
            protocol="P1",
            source_material="A turbofan converts fuel energy into thrust.",
        )

        self.run = ResearchRun.objects.create(
            experiment=self.experiment,
            run_id="R900-run-1",
            provider="OpenAI",
            displayed_model="gpt-5.6-luna",
            condition="Simple / Think OFF",
        )

        self.question = ResearchQuestion.objects.create(
            run=self.run,
            blind_id="R900-Q001",
            item_number=1,
            skill="main_idea",
            stem="What is the primary function of a turbofan?",
            option_a="Generate thrust",
            option_b="Cool the cabin",
            option_c="Store fuel",
            option_d="Measure altitude",
            correct_answer="A",
        )

        self.reviewer_user = get_user_model().objects.create_user(
            username="reviewer_one",
            email="reviewer_one@example.com",
            password="AeroESP-Strong-2026",
        )

        self.reviewer = ExpertReviewerProfile.objects.create(
            user=self.reviewer_user,
            discipline="AEROSPACE",
            is_active_reviewer=True,
        )

        self.assignment = ReviewAssignment.objects.create(
            reviewer=self.reviewer,
            question=self.question,
            display_order=1,
        )

    VALID_EVAL_V1_SCORES = {
        "technical_correctness": 4,
        "linguistic_accuracy": 4,
        "clarity_answerability": 4,
        "source_fidelity": 4,
        "distractor_quality": 4,
        "cefr_alignment": 4,
        "difficulty_alignment": 4,
        "pedagogical_value": 4,
        "expert_cefr": "B2",
        "expert_cognitive_level": "UNDERSTAND",
        "keyed_answer_correct": "YES",
        "ambiguous": "NO",
        "multiple_correct_answers": "NO",
        "overall_decision": "ACCEPT",
    }


class ConstructRelevanceFieldTests(ReviewFixtureMixin, TestCase):
    """
    Part (A): the content-validity dimension used for I-CVI / S-CVI
    (Polit & Beck, 2006), rendered above the eight EVAL_V1 dimensions.
    """

    def test_accepts_the_full_1_to_4_range(self):

        review = ExpertReview.objects.create(
            assignment=self.assignment,
        )

        for value in (1, 2, 3, 4):
            review.construct_relevance = value
            # Draft (is_finalized=False), so only the field's own
            # validators run - nothing else on the model is required.
            review.full_clean()

    def test_rejects_values_outside_1_to_4(self):

        review = ExpertReview(
            assignment=self.assignment,
            construct_relevance=5,
        )

        with self.assertRaises(ValidationError) as ctx:
            review.full_clean()

        self.assertIn(
            "construct_relevance",
            ctx.exception.message_dict,
        )

    def test_draft_may_leave_it_blank(self):
        """
        Matches every EVAL_V1 dimension: autosave must not require an
        answer before the reviewer finalizes.
        """

        review = ExpertReview.objects.create(
            assignment=self.assignment,
            construct_relevance=None,
            is_finalized=False,
        )

        review.full_clean()

    def test_finalizing_without_it_is_rejected(self):

        review = ExpertReview(
            assignment=self.assignment,
            is_finalized=True,
            construct_relevance=None,
            **self.VALID_EVAL_V1_SCORES,
        )

        with self.assertRaises(ValidationError) as ctx:
            review.full_clean()

        self.assertIn(
            "construct_relevance",
            ctx.exception.message_dict,
        )

    def test_finalizing_with_it_set_succeeds(self):

        review = ExpertReview(
            assignment=self.assignment,
            is_finalized=True,
            construct_relevance=3,
            **self.VALID_EVAL_V1_SCORES,
        )

        review.full_clean()

    def test_form_field_order_places_it_first(self):

        form = ExpertReviewForm()

        self.assertEqual(
            list(form.fields.keys())[0],
            "construct_relevance",
        )

    def test_form_choices_are_the_descriptive_four_point_scale(self):

        form = ExpertReviewForm()

        rendered = str(form["construct_relevance"])

        self.assertIn("Not relevant", rendered)
        self.assertIn("Highly relevant", rendered)

        offered_values = [
            choice[0]
            for choice in form.fields[
                "construct_relevance"
            ].widget.choices
        ]

        self.assertEqual(offered_values, [1, 2, 3, 4])

    def test_renders_above_the_eval_v1_dimensions_on_the_page(self):

        self.client.force_login(self.reviewer_user)

        response = self.client.get(
            reverse(
                "research_review:review_item",
                args=[self.assignment.pk],
            )
        )

        body = response.content.decode()

        self.assertIn("construct_relevance", body)

        self.assertLess(
            body.index("construct_relevance"),
            body.index("technical_correctness"),
        )


class ReviewerConfidenceAndTimeSpentTests(ReviewFixtureMixin, TestCase):
    """
    Part (B): an optional self-reported confidence score, and an
    automatically-captured time-on-task in seconds.
    """

    def _post(self, **overrides):

        data = dict(
            self.VALID_EVAL_V1_SCORES,
            construct_relevance=3,
            action="draft",
        )
        data.update(overrides)

        return self.client.post(
            reverse(
                "research_review:review_item",
                args=[self.assignment.pk],
            ),
            data,
        )

    def setUp(self):

        super().setUp()

        self.client.force_login(self.reviewer_user)

    def test_confidence_is_optional_on_a_draft(self):

        response = self._post(reviewer_confidence="")

        self.assertEqual(response.status_code, 302)

        review = ExpertReview.objects.get(
            assignment=self.assignment
        )

        self.assertIsNone(review.reviewer_confidence)

    def test_confidence_is_optional_even_when_finalizing(self):
        """
        Only construct_relevance and the EVAL_V1 fields are mandatory
        at finalize time - confidence stays optional per spec.
        """

        response = self._post(
            action="finalize",
            reviewer_confidence="",
        )

        self.assertEqual(response.status_code, 302)

        review = ExpertReview.objects.get(
            assignment=self.assignment
        )

        self.assertTrue(review.is_finalized)
        self.assertIsNone(review.reviewer_confidence)

    def test_confidence_is_saved_when_given(self):

        self._post(reviewer_confidence="5")

        review = ExpertReview.objects.get(
            assignment=self.assignment
        )

        self.assertEqual(review.reviewer_confidence, 5)

    def test_time_spent_is_read_from_the_hidden_field(self):

        self._post(time_spent_seconds="137")

        review = ExpertReview.objects.get(
            assignment=self.assignment
        )

        self.assertEqual(review.time_spent_seconds, 137)

    def test_missing_time_spent_does_not_error(self):
        """
        A visitor with JavaScript disabled, or a tampered request,
        must degrade to "not recorded" rather than break the save.
        """

        response = self._post(time_spent_seconds="")

        self.assertEqual(response.status_code, 302)

        review = ExpertReview.objects.get(
            assignment=self.assignment
        )

        self.assertIsNone(review.time_spent_seconds)

    def test_non_numeric_time_spent_is_ignored_not_crashed(self):

        response = self._post(
            time_spent_seconds="'; DROP TABLE--"
        )

        self.assertEqual(response.status_code, 302)

        review = ExpertReview.objects.get(
            assignment=self.assignment
        )

        self.assertIsNone(review.time_spent_seconds)

    def test_hidden_field_and_timer_script_are_present_on_the_page(
        self,
    ):

        response = self.client.get(
            reverse(
                "research_review:review_item",
                args=[self.assignment.pk],
            )
        )

        body = response.content.decode()

        self.assertIn('id="id_time_spent_seconds"', body)
        self.assertIn('id="review-form"', body)
        self.assertIn("loadedAt", body)


class QuestionProvenanceBlindingTests(ReviewFixtureMixin, TestCase):
    """
    Part (C): question_provenance is research metadata that must never
    reach a reviewer - the entire point of blinded review is that a
    rater's judgment is not coloured by knowing an item is
    AI-generated before they evaluate it.
    """

    # Every string that could leak the field, its value, or its
    # human-readable choice labels into rendered HTML.
    LEAK_SIGNATURES = [
        "question_provenance",
        "AI_GENERATED",
        "AI Generated",
        "HUMAN_WRITTEN",
        "Human Written",
        "EXISTING_SOURCE",
        "Existing Source",
    ]

    def test_model_default_and_choices(self):

        self.assertEqual(
            self.question.question_provenance,
            "AI_GENERATED",
        )

        self.assertEqual(
            [c[0] for c in self.question.PROVENANCE_CHOICES],
            ["AI_GENERATED", "HUMAN_WRITTEN", "EXISTING_SOURCE"],
        )

    def test_provenance_never_appears_on_the_review_page(self):
        """
        Checked for every possible value, not just the default - a
        human-written or existing-source item must be exactly as
        blinded as an AI-generated one.
        """

        self.client.force_login(self.reviewer_user)
        url = reverse(
            "research_review:review_item",
            args=[self.assignment.pk],
        )

        for value, _ in self.question.PROVENANCE_CHOICES:

            self.question.question_provenance = value
            self.question.save(
                update_fields=["question_provenance"]
            )

            body = self.client.get(url).content.decode()

            for signature in self.LEAK_SIGNATURES:
                self.assertNotIn(
                    signature,
                    body,
                    f"{signature!r} leaked onto the review page "
                    f"when question_provenance={value!r}",
                )

    def test_provenance_never_appears_on_the_dashboard(self):

        self.client.force_login(self.reviewer_user)

        body = self.client.get(
            reverse("research_review:dashboard")
        ).content.decode()

        for signature in self.LEAK_SIGNATURES:
            self.assertNotIn(signature, body)

    def test_view_context_does_not_add_provenance_directly(self):
        """
        Belt and braces: even though `question` itself is passed to
        the template (and templates can reach any attribute), the view
        must not additionally hand provenance to the template under
        its own context key, which would make an accidental
        {{ provenance }} reference in a future template edit trivial.
        """

        self.client.force_login(self.reviewer_user)

        response = self.client.get(
            reverse(
                "research_review:review_item",
                args=[self.assignment.pk],
            )
        )

        self.assertNotIn("provenance", response.context)
        self.assertNotIn(
            "question_provenance",
            response.context,
        )

    def test_provenance_is_visible_to_researchers_in_the_admin(self):
        """
        The blinding requirement is specific to the reviewer-facing
        review page - the researcher/admin still needs to see and
        filter by provenance to run any provenance-stratified
        analysis later.
        """

        admin_user = get_user_model().objects.create_superuser(
            username="researcher_admin",
            email="researcher_admin@example.com",
            password="AeroESP-Strong-2026",
        )

        self.client.force_login(admin_user)

        response = self.client.get(
            reverse(
                "admin:research_review_researchquestion_changelist"
            )
        )

        self.assertContains(response, "AI Generated")


class CreateReviewAssignmentsCommandTests(TestCase):
    """
    Part (D): random, balanced, reproducible reviewer assignment.
    """

    def setUp(self):

        self.experiment = ResearchExperiment.objects.create(
            experiment_id="R901",
            source_id="R901",
            domain="Structures",
            topic="Fatigue",
            protocol="P1",
        )

        self.run = ResearchRun.objects.create(
            experiment=self.experiment,
            run_id="R901-run-1",
            provider="OpenAI",
        )

        self.blind_ids = []

        for i in range(1, 8):

            question = ResearchQuestion.objects.create(
                run=self.run,
                blind_id=f"R901-Q{i:03d}",
                item_number=i,
                skill="main_idea",
                stem=f"Stem {i}",
                option_a="a",
                option_b="b",
                option_c="c",
                option_d="d",
                correct_answer="A",
            )

            self.blind_ids.append(question.blind_id)

        self.reviewers = []

        for i in range(1, 5):

            user = get_user_model().objects.create_user(
                username=f"balreviewer{i}",
                email=f"balreviewer{i}@example.com",
                password="AeroESP-Strong-2026",
            )

            self.reviewers.append(
                ExpertReviewerProfile.objects.create(
                    user=user,
                    discipline="AEROSPACE",
                    is_active_reviewer=True,
                )
            )

        # An inactive reviewer must never be selected.
        inactive_user = get_user_model().objects.create_user(
            username="inactive_reviewer",
            email="inactive_reviewer@example.com",
        )

        self.inactive_reviewer = ExpertReviewerProfile.objects.create(
            user=inactive_user,
            discipline="AEROSPACE",
            is_active_reviewer=False,
        )

    def _run(self, **kwargs):

        out = StringIO()

        kwargs.setdefault(
            "blind_ids",
            ",".join(self.blind_ids),
        )

        call_command(
            "create_review_assignments",
            stdout=out,
            **kwargs,
        )

        return out.getvalue()

    def test_dry_run_writes_nothing_to_the_database(self):

        self._run(k=2, seed=42, dry_run=True)

        self.assertEqual(
            ReviewAssignment.objects.count(),
            0,
        )

    def test_real_run_creates_len_questions_times_k_assignments(self):

        self._run(k=2, seed=42)

        self.assertEqual(
            ReviewAssignment.objects.count(),
            len(self.blind_ids) * 2,
        )

    def test_inactive_reviewers_are_never_selected(self):

        self._run(k=2, seed=42)

        self.assertFalse(
            ReviewAssignment.objects.filter(
                reviewer=self.inactive_reviewer
            ).exists()
        )

    def test_load_is_balanced_within_one(self):

        self._run(k=2, seed=1)

        counts = [
            ReviewAssignment.objects.filter(
                reviewer=reviewer
            ).count()
            for reviewer in self.reviewers
        ]

        self.assertLessEqual(
            max(counts) - min(counts),
            1,
        )

    def test_each_reviewer_sees_a_different_display_order(self):
        """
        The spec explicitly requires two reviewers to see their
        shared questions in a different order from one another.
        """

        self._run(k=4, seed=7)

        orders = [
            tuple(
                ReviewAssignment.objects
                .filter(reviewer=reviewer)
                .order_by("display_order")
                .values_list("question__blind_id", flat=True)
            )
            for reviewer in self.reviewers
        ]

        # With 4 reviewers all seeing all 7 questions (k == reviewer
        # count), every reviewer has the same *set* - identical order
        # for all of them would mean no per-reviewer randomisation
        # happened at all.
        self.assertGreater(
            len(set(orders)),
            1,
        )

    def test_same_seed_reproduces_the_identical_plan(self):

        self._run(k=2, seed=99)

        first_plan = set(
            ReviewAssignment.objects.values_list(
                "reviewer_id", "question_id", "display_order"
            )
        )

        ReviewAssignment.objects.all().delete()

        self._run(k=2, seed=99)

        second_plan = set(
            ReviewAssignment.objects.values_list(
                "reviewer_id", "question_id", "display_order"
            )
        )

        self.assertEqual(first_plan, second_plan)

    def test_different_seeds_produce_different_plans(self):

        self._run(k=2, seed=1)

        plan_a = set(
            ReviewAssignment.objects.values_list(
                "reviewer_id", "question_id"
            )
        )

        ReviewAssignment.objects.all().delete()

        self._run(k=2, seed=2)

        plan_b = set(
            ReviewAssignment.objects.values_list(
                "reviewer_id", "question_id"
            )
        )

        self.assertNotEqual(plan_a, plan_b)

    def test_omitting_seed_still_prints_one_for_reproducibility(self):

        output = self._run(k=2)

        self.assertIn("Seed used:", output)

    def test_rerun_is_idempotent(self):

        self._run(k=2, seed=42)
        self._run(k=2, seed=42)

        self.assertEqual(
            ReviewAssignment.objects.count(),
            len(self.blind_ids) * 2,
        )

    def test_unknown_blind_id_raises_before_writing_anything(self):

        with self.assertRaises(CommandError):
            self._run(
                k=2,
                seed=1,
                blind_ids="R901-Q001,NOT-A-REAL-ID",
            )

        self.assertEqual(
            ReviewAssignment.objects.count(),
            0,
        )

    def test_k_greater_than_active_reviewers_raises(self):

        with self.assertRaises(CommandError):
            self._run(k=99, seed=1)

    def test_inline_blind_ids_and_csv_are_mutually_exclusive(self):

        with self.assertRaises(CommandError):
            self._run(
                k=2,
                seed=1,
                csv_path="/dev/null",
            )

    def test_reads_blind_ids_from_a_csv_file(self):

        csv_path = os.path.join(
            tempfile.gettempdir(),
            "aeroesp_test_assignments.csv",
        )

        with open(csv_path, "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["blind_id"])
            for blind_id in self.blind_ids[:3]:
                writer.writerow([blind_id])

        try:
            self._run(
                k=2,
                seed=1,
                blind_ids=None,
                csv_path=csv_path,
            )
        finally:
            os.remove(csv_path)

        self.assertEqual(
            ReviewAssignment.objects.count(),
            6,
        )

    def test_seed_is_printed_in_dry_run_output_too(self):

        output = self._run(k=2, seed=123, dry_run=True)

        self.assertIn("123", output)
        self.assertIn("DRY RUN", output)
