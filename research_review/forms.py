from django import forms

from .models import ExpertReview


SCORE_CHOICES = [
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5"),
]


CONSTRUCT_RELEVANCE_CHOICES = [
    (1, "1 - Not relevant"),
    (2, "2 - Somewhat relevant, needs major revision"),
    (3, "3 - Relevant, needs minor revision"),
    (4, "4 - Highly relevant"),
]


ERROR_CODE_CHOICES = [
    ("T1", "T1 - Incorrect technical fact"),
    ("T2", "T2 - Unsupported technical claim"),
    ("T3", "T3 - Technical oversimplification"),
    ("T4", "T4 - Technical terminology problem"),

    ("Q1", "Q1 - Ambiguous question"),
    ("Q2", "Q2 - Keyed answer problem"),

    ("D1", "D1 - Implausible distractor"),
    ("D2", "D2 - Multiple plausible answers"),
    ("D3", "D3 - Distractor gives away answer"),

    ("L1", "L1 - Grammar problem"),
    ("L2", "L2 - Vocabulary/style problem"),
    ("L3", "L3 - Language level mismatch"),

    ("S1", "S1 - Source fidelity problem"),

    ("P1", "P1 - Pedagogical problem"),

    ("C1", "C1 - Cognitive-level mismatch"),
]


class ExpertReviewForm(forms.ModelForm):

    error_codes = forms.MultipleChoiceField(
        choices=ERROR_CODE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Error codes",
    )

    class Meta:

        model = ExpertReview

        fields = [
            # First, so it renders above the EVAL_V1 quality
            # dimensions - see review_item.html.
            "construct_relevance",

            "technical_correctness",
            "linguistic_accuracy",
            "clarity_answerability",
            "source_fidelity",
            "distractor_quality",
            "cefr_alignment",
            "difficulty_alignment",
            "pedagogical_value",

            "expert_cefr",
            "expert_cognitive_level",

            "keyed_answer_correct",
            "ambiguous",
            "multiple_correct_answers",

            "overall_decision",

            "error_codes",
            "comments",

            "reviewer_confidence",
        ]

        labels = {
            "construct_relevance":
                "Construct Relevance (English for Aerospace "
                "Engineering)",

            "technical_correctness":
                "Technical Correctness (TC)",

            "linguistic_accuracy":
                "Linguistic Accuracy (LA)",

            "clarity_answerability":
                "Clarity & Answerability (CA)",

            "source_fidelity":
                "Source Fidelity (SF)",

            "distractor_quality":
                "Distractor Quality (DQ)",

            "cefr_alignment":
                "CEFR Alignment (CL)",

            "difficulty_alignment":
                "Cognitive / Difficulty Alignment (DA)",

            "pedagogical_value":
                "Aerospace ESP Pedagogical Value (PV)",

            "expert_cefr":
                "Estimated CEFR Level",

            "expert_cognitive_level":
                "Estimated Cognitive Level",

            "keyed_answer_correct":
                "Is the keyed answer correct?",

            "ambiguous":
                "Is the item ambiguous?",

            "multiple_correct_answers":
                "Is more than one answer plausible?",

            "overall_decision":
                "Overall Disposition",

            "comments":
                "Expert comments",

            "reviewer_confidence":
                "Your confidence in this assessment",
        }

        widgets = {
            "construct_relevance":
                forms.RadioSelect(
                    choices=CONSTRUCT_RELEVANCE_CHOICES
                ),

            "technical_correctness":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),

            "linguistic_accuracy":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),

            "clarity_answerability":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),

            "source_fidelity":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),

            "distractor_quality":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),

            "cefr_alignment":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),

            "difficulty_alignment":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),

            "pedagogical_value":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),

            "keyed_answer_correct":
                forms.RadioSelect,

            "ambiguous":
                forms.RadioSelect,

            "multiple_correct_answers":
                forms.RadioSelect,

            "overall_decision":
                forms.RadioSelect,

            "comments":
                forms.Textarea(
                    attrs={
                        "rows": 5,
                        "placeholder": (
                            "Optional comments, corrections, "
                            "or recommendations..."
                        ),
                    }
                ),

            "reviewer_confidence":
                forms.RadioSelect(
                    choices=SCORE_CHOICES
                ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs,
        )

        if (
            self.instance
            and self.instance.pk
            and self.instance.error_codes
        ):
            # error_codes is a JSONField holding a plain list of
            # codes - no parsing needed, unlike the comma-joined
            # CharField this used to be.
            self.initial["error_codes"] = list(
                self.instance.error_codes
            )

    def save(self, commit=True):

        instance = super().save(
            commit=False
        )

        instance.error_codes = self.cleaned_data.get(
            "error_codes",
            [],
        )

        if commit:
            instance.save()

        return instance