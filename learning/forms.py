from django import forms

from assessment.models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)

from .models import (
    CourseModule,
    LearningItem,
    Resource,
)

# =========================================================
# IELTS / General English choices
# =========================================================

IELTS_FOCUS_CHOICES = {
    "vocabulary": [
        ("Academic Vocabulary", "Academic Vocabulary"),
        ("Collocation", "Collocation"),
        ("Word Formation", "Word Formation"),
        ("Phrasal Verbs", "Phrasal Verbs"),
        ("Idioms", "Idioms"),
        ("Synonyms and Paraphrasing", "Synonyms and Paraphrasing"),
    ],
    "grammar": [
        ("Tenses", "Tenses"),
        ("Articles", "Articles"),
        ("Prepositions", "Prepositions"),
        ("Conditionals", "Conditionals"),
        ("Passive Voice", "Passive Voice"),
        ("Modal Verbs", "Modal Verbs"),
        ("Relative Clauses", "Relative Clauses"),
        ("Gerunds and Infinitives", "Gerunds and Infinitives"),
        ("Sentence Structure", "Sentence Structure"),
    ],
    "reading": [
        ("Matching Headings", "Matching Headings"),
        ("True False Not Given", "True / False / Not Given"),
        ("Multiple Choice", "Multiple Choice"),
        ("Sentence Completion", "Sentence Completion"),
        ("Summary Completion", "Summary Completion"),
        ("Matching Information", "Matching Information"),
        ("Vocabulary in Context", "Vocabulary in Context"),
    ],
    "listening": [
        ("Form Completion", "Form Completion"),
        ("Multiple Choice", "Multiple Choice"),
        ("Matching", "Matching"),
        ("Map and Diagram Labelling", "Map / Diagram Labelling"),
        ("Sentence Completion", "Sentence Completion"),
        ("Note Completion", "Note Completion"),
    ],
    "writing": [
        ("Task 1", "IELTS Writing Task 1"),
        ("Task 2", "IELTS Writing Task 2"),
        ("Task Response", "Task Response"),
        ("Coherence and Cohesion", "Coherence and Cohesion"),
        ("Lexical Resource", "Lexical Resource"),
        ("Grammar Accuracy", "Grammar Accuracy"),
    ],
    "speaking": [
        ("Part 1", "IELTS Speaking Part 1"),
        ("Part 2", "IELTS Speaking Part 2"),
        ("Part 3", "IELTS Speaking Part 3"),
        ("Fluency", "Fluency"),
        ("Pronunciation", "Pronunciation"),
        ("Lexical Resource", "Lexical Resource"),
        ("Grammar", "Grammar"),
    ],
    "review": [
        ("Mixed Review", "Mixed Review"),
        ("Error Correction", "Error Correction"),
        ("Spaced Review", "Spaced Review"),
        ("Weak Areas", "Weak Areas"),
    ],
}

IELTS_TOPIC_CHOICES = [
    ("Education", "Education"),
    ("Technology", "Technology"),
    ("Environment", "Environment"),
    ("Health", "Health"),
    ("Work and Business", "Work & Business"),
    ("Travel and Transport", "Travel & Transport"),
    ("Science", "Science"),
    ("Society", "Society"),
    ("Culture", "Culture"),
    ("Media", "Media"),
    ("Daily Life", "Daily Life"),
    ("Global Issues", "Global Issues"),
    ("Other", "Other"),
]


class LearningItemForm(forms.ModelForm):

    # ---------------------------------------------------------
    # New fields for IELTS / General English classification
    # ---------------------------------------------------------
    english_focus = forms.ChoiceField(
        required=False,
        choices=[("", "---------")],
        label="Learning Focus",
    )

    english_topic = forms.ChoiceField(
        required=False,
        choices=[("", "---------")],
        label="Topic / Theme",
    )

    class Meta:
        model = LearningItem

        fields = [
            "module",
            "aerospace_domain",
            "aerospace_topic",
            "english_focus",
            "english_topic",
            "title",
            "item_type",
            "definition_en",
            "explanation",
            "example",
            "common_mistake",
            "correct_form",
            "source_type",
            "source_reference",
            "is_public",
        ]

        labels = {
            "module": "Course Section",
            "aerospace_domain": "Aerospace Domain",
            "aerospace_topic": "Aerospace Topic",
            "english_focus": "Learning Focus",
            "english_topic": "Topic / Theme",
            "title": "Word / Phrase / Learning Point",
            "item_type": "Learning Type",
            "definition_en": "Definition",
            "explanation": "Notes / Explanation",
            "example": "Example",
            "common_mistake": "Common Mistake",
            "correct_form": "Correct Form",
            "source_type": "Source Type",
            "source_reference": "Source",
            "is_public": "Share with other learners",
        }

        widgets = {
            "definition_en": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": (
                        "Write a short definition..."
                    ),
                }
            ),
            "explanation": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Add notes, grammar rules, "
                        "usage tips, or anything useful..."
                    ),
                }
            ),
            "example": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": (
                        "Write an example sentence..."
                    ),
                }
            ),
            "common_mistake": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": (
                        "Write a common incorrect form..."
                    ),
                }
            ),
            "correct_form": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": (
                        "Write the correct form..."
                    ),
                }
            ),
        }

    def __init__(
        self,
        *args,
        course=None,
        module=None,
        topic=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        # Determine program type from course or module
        program_type = None
        if course is not None:
            program_type = course.program.program_type
        elif module is not None:
            program_type = module.course.program.program_type

        # Set up the module queryset
        queryset = (
            CourseModule.objects
            .filter(
                is_active=True,
                course__is_active=True,
                course__program__is_active=True,
            )
            .select_related(
                "course",
                "course__program",
            )
            .order_by(
                "course__program__order",
                "course__order",
                "order",
            )
        )

        if module is not None:
            queryset = queryset.filter(
                pk=module.pk,
            )
            self.fields["module"].queryset = queryset
            self.fields["module"].initial = module
        elif course is not None:
            queryset = queryset.filter(
                course=course,
            )
            self.fields["module"].queryset = queryset
        else:
            self.fields["module"].queryset = queryset

        # ==============================================
        # Branch based on program type (when context exists)
        # ==============================================
        if course is not None or module is not None:

            # ------------------------------------------
            # IELTS / General English
            # ------------------------------------------
            if program_type == "IELTS":
                # Remove aerospace taxonomy fields
                self.fields.pop("aerospace_domain", None)
                self.fields.pop("aerospace_topic", None)

                # English fields are required
                self.fields["english_focus"].required = True
                self.fields["english_topic"].required = True

                # Map module title to focus choices
                module_key = ""
                if module is not None:
                    module_key = module.title.strip().lower()

                focus_choices = IELTS_FOCUS_CHOICES.get(
                    module_key,
                    [
                        ("General Language Practice", "General Language Practice"),
                    ],
                )
                self.fields["english_focus"].choices = [
                    ("", "---------"),
                    *focus_choices,
                ]

                self.fields["english_topic"].choices = [
                    ("", "---------"),
                    *IELTS_TOPIC_CHOICES,
                ]

                return

            # ------------------------------------------
            # Aerospace English / ESP
            # ------------------------------------------
            if program_type == "AEROSPACE_ESP":
                # Remove English fields
                self.fields.pop("english_focus", None)
                self.fields.pop("english_topic", None)

                # Configure aerospace fields
                self.fields["aerospace_domain"].required = False
                self.fields["aerospace_domain"].queryset = (
                    AerospaceDomain.objects
                    .filter(is_active=True)
                    .order_by("order", "name")
                )

                # If module has a domain, restrict topics to that domain
                domain = None
                if module is not None and module.aerospace_domain:
                    domain = module.aerospace_domain

                if domain:
                    self.fields["aerospace_topic"].queryset = (
                        AerospaceTopic.objects
                        .filter(
                            domain=domain,
                            is_active=True,
                            approval_status__in=[
                                AerospaceTopic.ApprovalStatus.CORE,
                                AerospaceTopic.ApprovalStatus.APPROVED,
                            ],
                        )
                        .order_by("order", "name")
                    )
                else:
                    self.fields["aerospace_topic"].queryset = AerospaceTopic.objects.none()

                # If topic is provided, set it as initial and disable the field
                if topic is not None:
                    self.fields["aerospace_topic"].initial = topic
                    self.fields["aerospace_topic"].disabled = True

                return

        # ==============================================
        # No specific context – show everything
        # (user can choose either aerospace or english)
        # ==============================================

        # Aerospace fields
        self.fields["aerospace_domain"].required = False
        self.fields["aerospace_domain"].queryset = (
            AerospaceDomain.objects
            .filter(is_active=True)
            .order_by("order", "name")
        )

        domain_id = None
        if self.is_bound:
            domain_id = self.data.get("aerospace_domain")
        elif (
            self.instance
            and self.instance.pk
            and self.instance.aerospace_domain_id
        ):
            domain_id = self.instance.aerospace_domain_id

        topics = (
            AerospaceTopic.objects
            .filter(
                is_active=True,
                approval_status__in=[
                    AerospaceTopic.ApprovalStatus.CORE,
                    AerospaceTopic.ApprovalStatus.APPROVED,
                ],
            )
        )
        if domain_id:
            topics = topics.filter(domain_id=domain_id)
        else:
            topics = topics.none()

        self.fields["aerospace_topic"].queryset = topics.order_by("order", "name")

        # English fields – keep them as is, choices are already set to empty.
        # They will remain optional.

    def clean(self):
        cleaned_data = super().clean()
        # Additional validation can be added here if needed.
        return cleaned_data


class LearningQuestionForm(forms.ModelForm):
    """
    Form to create a question directly from a learning item context.
    The track is automatically determined from the learning item's program.
    """

    class Meta:
        model = Question

        fields = (
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "explanation",
            "difficulty",
            "domain_ref",
            "topic_ref",
        )

        labels = {
            "question_text": "Question",
            "option_a": "Option A",
            "option_b": "Option B",
            "option_c": "Option C",
            "option_d": "Option D",
            "correct_answer": "Correct Answer",
            "explanation": "Explanation",
            "difficulty": "Difficulty",
            "domain_ref": "Aerospace Domain",
            "topic_ref": "Aerospace Topic",
        }

        widgets = {
            "question_text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Enter the complete question..."
                    ),
                }
            ),
            "option_a": forms.TextInput(
                attrs={
                    "placeholder": "Option A",
                }
            ),
            "option_b": forms.TextInput(
                attrs={
                    "placeholder": "Option B",
                }
            ),
            "option_c": forms.TextInput(
                attrs={
                    "placeholder": "Option C",
                }
            ),
            "option_d": forms.TextInput(
                attrs={
                    "placeholder": "Option D",
                }
            ),
            "explanation": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Explain why the answer is correct..."
                    ),
                }
            ),
        }

    def __init__(
        self,
        *args,
        learning_item=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.learning_item = learning_item

        # If no learning_item is provided, we cannot determine track.
        # Default to Aerospace ESP (but it's better to raise? We'll set default)
        if learning_item is None:
            # Default to Aerospace ESP
            self.instance.track = Question.Track.AEROSPACE_ESP
            self.fields["domain_ref"].required = True
            self.fields["domain_ref"].queryset = (
                AerospaceDomain.objects.filter(is_active=True).order_by("order", "name")
            )
            self.fields["topic_ref"].required = False
            topic_queryset = AerospaceTopic.objects.none()
            self.fields["topic_ref"].queryset = topic_queryset
            return

        program_type = (
            learning_item
            .module
            .course
            .program
            .program_type
        )

        # ==============================================
        # General English / IELTS
        # ==============================================
        if program_type == "IELTS":
            self.instance.track = (
                Question.Track.GENERAL_ENGLISH
            )

            # Remove aerospace-specific fields
            self.fields.pop(
                "domain_ref",
                None,
            )
            self.fields.pop(
                "topic_ref",
                None,
            )

            return

        # ==============================================
        # Aerospace English / ESP
        # ==============================================

        self.instance.track = (
            Question.Track.AEROSPACE_ESP
        )

        self.fields[
            "domain_ref"
        ].required = True

        self.fields[
            "domain_ref"
        ].queryset = (
            AerospaceDomain.objects
            .filter(is_active=True)
            .order_by(
                "order",
                "name",
            )
        )

        self.fields[
            "topic_ref"
        ].required = False

        topic_queryset = (
            AerospaceTopic.objects
            .filter(
                is_active=True,
                approval_status__in=[
                    AerospaceTopic
                    .ApprovalStatus
                    .CORE,
                    AerospaceTopic
                    .ApprovalStatus
                    .APPROVED,
                ],
            )
            .select_related("domain")
        )

        selected_domain_id = None

        if self.is_bound:

            selected_domain_id = (
                self.data.get(
                    "domain_ref"
                )
            )

        elif (
            self.instance
            and self.instance.domain_ref_id
        ):

            selected_domain_id = (
                self.instance.domain_ref_id
            )

        if selected_domain_id:

            topic_queryset = (
                topic_queryset.filter(
                    domain_id=selected_domain_id
                )
            )

        else:

            topic_queryset = (
                topic_queryset.none()
            )

        self.fields[
            "topic_ref"
        ].queryset = (
            topic_queryset.order_by(
                "order",
                "name",
            )
        )


# =========================================================
# Resource Form
# =========================================================

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            "title",
            "description",
            "resource_type",
            "course",
            "module",
            "file",
            "external_url",
            "visibility",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "external_url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }
        labels = {
            "external_url": "External URL",
            "visibility": "Visibility",
        }