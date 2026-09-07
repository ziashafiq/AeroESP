from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
