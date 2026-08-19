from django import forms

from .models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


# =========================================================
# Teacher Question Form
# =========================================================

class TeacherQuestionForm(forms.ModelForm):
    """
    Form used by approved teachers to create and edit questions.

    Owner is assigned automatically by the server.
    Only active domains and approved/core topics are available.
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
            "question_language",
            "options_language",
            "track",
            "skill",
            "domain_ref",
            "topic_ref",
            "difficulty",
            "source_reference",
            "visibility",
        )

        labels = {
            "question_text": "Question",
            "option_a": "Option A",
            "option_b": "Option B",
            "option_c": "Option C",
            "option_d": "Option D",
            "correct_answer": "Correct Answer",
            "explanation": "Explanation",
            "question_language": "Question Language",
            "options_language": "Options Language",
            "track": "Learning Track",
            "skill": "Language Skill",
            "domain_ref": "Aerospace Domain",
            "topic_ref": "Aerospace Topic",
            "difficulty": "Difficulty",
            "source_reference": "Source / Reference",
            "visibility": "Question Visibility",
        }

        help_texts = {
            "domain_ref": (
                "Select the main aerospace field related "
                "to this question."
            ),
            "topic_ref": (
                "Select the most appropriate topic. "
                "If it is missing, use Propose New Topic."
            ),
            "source_reference": (
                "Optional source: book, paper, standard, "
                "course material, corpus, etc."
            ),
        }

        widgets = {
            "question_text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Enter the complete question...",
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
                        "Optional explanation for the correct answer..."
                    ),
                }
            ),

            "source_reference": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Book, paper, standard, corpus, etc."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # -------------------------------------------------
        # Determine selected track
        # -------------------------------------------------
        selected_track = None

        if self.is_bound:
            selected_track = self.data.get(
                "track"
            )

        elif (
            self.instance
            and self.instance.pk
        ):
            selected_track = (
                self.instance.track
            )

        if not selected_track:
            selected_track = (
                Question.Track.AEROSPACE_ESP
            )

        # -------------------------------------------------
        # Domains
        # -------------------------------------------------

        self.fields["domain_ref"].queryset = (
            AerospaceDomain.objects.filter(
                is_active=True,
            )
            .order_by(
                "order",
                "name",
            )
        )

        self.fields["domain_ref"].required = (
            selected_track
            == Question.Track.AEROSPACE_ESP
        )

        # -------------------------------------------------
        # Topics
        # -------------------------------------------------

        topic_queryset = (
            AerospaceTopic.objects.filter(
                is_active=True,
                approval_status__in=[
                    AerospaceTopic.ApprovalStatus.CORE,
                    AerospaceTopic.ApprovalStatus.APPROVED,
                ],
            )
            .select_related(
                "domain",
                "parent",
            )
        )

        # If track is General English, no topics/domains
        if (
            selected_track
            == Question.Track.GENERAL_ENGLISH
        ):
            topic_queryset = (
                topic_queryset.none()
            )

            self.fields[
                "domain_ref"
            ].queryset = (
                AerospaceDomain.objects.none()
            )

        # If form is submitted, restrict topics to
        # the selected domain.
        elif self.is_bound:

            domain_id = self.data.get(
                "domain_ref"
            )

            if domain_id:
                topic_queryset = topic_queryset.filter(
                    domain_id=domain_id
                )
            else:
                topic_queryset = topic_queryset.none()

        # If editing an existing question,
        # restrict topics to its current domain.
        elif self.instance and self.instance.pk:

            if self.instance.domain_ref_id:
                topic_queryset = topic_queryset.filter(
                    domain_id=self.instance.domain_ref_id
                )
            else:
                topic_queryset = topic_queryset.none()

        else:
            topic_queryset = topic_queryset.none()

        self.fields["topic_ref"].queryset = (
            topic_queryset.order_by(
                "order",
                "name",
            )
        )

        self.fields["topic_ref"].required = False

        # -------------------------------------------------
        # Visibility
        # -------------------------------------------------

        self.fields["visibility"].choices = [
            (
                Question.Visibility.PRIVATE,
                "Teacher Private",
            ),
            (
                Question.Visibility.PRACTICE_EXAM,
                "Practice + Exam",
            ),
            (
                Question.Visibility.EXAM_ONLY,
                "Exam Only",
            ),
            (
                Question.Visibility.SHARED,
                "Shared Teacher Bank",
            ),
        ]

    def clean(self):
        cleaned_data = super().clean()

        track = cleaned_data.get(
            "track"
        )

        domain = cleaned_data.get(
            "domain_ref"
        )

        topic = cleaned_data.get(
            "topic_ref"
        )

        if (
            track
            == Question.Track.AEROSPACE_ESP
            and not domain
        ):

            self.add_error(
                "domain_ref",
                "Please select an aerospace domain.",
            )

        if (
            track
            == Question.Track.GENERAL_ENGLISH
        ):

            if domain:

                self.add_error(
                    "domain_ref",
                    "General English / IELTS questions "
                    "do not use an aerospace domain.",
                )

            if topic:

                self.add_error(
                    "topic_ref",
                    "General English / IELTS questions "
                    "do not use an aerospace topic.",
                )

            return cleaned_data

        if topic and not domain:

            self.add_error(
                "domain_ref",
                "Please select an aerospace domain first.",
            )

        if topic and domain:

            if topic.domain_id != domain.id:

                self.add_error(
                    "topic_ref",
                    "The selected topic does not belong "
                    "to the selected aerospace domain.",
                )

        if topic:

            allowed_statuses = {
                AerospaceTopic.ApprovalStatus.CORE,
                AerospaceTopic.ApprovalStatus.APPROVED,
            }

            if (
                topic.approval_status
                not in allowed_statuses
            ):

                self.add_error(
                    "topic_ref",
                    "This topic has not been approved for use.",
                )

        return cleaned_data


# =========================================================
# Teacher Topic Proposal Form
# =========================================================

class TeacherTopicProposalForm(forms.ModelForm):
    """
    Allows an approved teacher to propose a missing topic.

    Parent topics are dynamically restricted to the
    selected aerospace domain.
    """

    class Meta:
        model = AerospaceTopic

        fields = (
            "domain",
            "parent",
            "name",
            "description",
        )

        labels = {
            "domain": "Aerospace Domain",
            "parent": "Parent Topic (Optional)",
            "name": "Proposed Topic Name",
            "description": "Description / Reason",
        }

        help_texts = {
            "domain": (
                "Select the main aerospace domain."
            ),

            "parent": (
                "Optional. Search and select a broader topic "
                "inside the selected aerospace domain."
            ),

            "name": (
                "Enter the missing aerospace topic."
            ),

            "description": (
                "Briefly describe the topic or explain why "
                "it should be added."
            ),
        }

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Example: Hypersonic Boundary-Layer Transition"
                    ),
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Optional explanation or scope..."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # -------------------------------------------------
        # Domains
        # -------------------------------------------------

        self.fields["domain"].queryset = (
            AerospaceDomain.objects.filter(
                is_active=True,
            )
            .order_by(
                "order",
                "name",
            )
        )

        # -------------------------------------------------
        # Parent Topic
        # -------------------------------------------------

        parent_queryset = (
            AerospaceTopic.objects.filter(
                is_active=True,
                approval_status__in=[
                    AerospaceTopic.ApprovalStatus.CORE,
                    AerospaceTopic.ApprovalStatus.APPROVED,
                ],
            )
            .select_related(
                "domain",
                "parent",
            )
        )

        # Bound form / POST request
        if self.is_bound:

            domain_id = self.data.get(
                "domain"
            )

            if domain_id:

                parent_queryset = (
                    parent_queryset.filter(
                        domain_id=domain_id
                    )
                )

            else:

                parent_queryset = (
                    parent_queryset.none()
                )

        # Editing existing proposal, if needed later
        elif self.instance and self.instance.pk:

            if self.instance.domain_id:

                parent_queryset = (
                    parent_queryset.filter(
                        domain_id=self.instance.domain_id
                    )
                )

            else:

                parent_queryset = (
                    parent_queryset.none()
                )

        # New empty form
        else:

            parent_queryset = (
                parent_queryset.none()
            )

        self.fields["parent"].queryset = (
            parent_queryset.order_by(
                "order",
                "name",
            )
        )

        self.fields["parent"].required = False

    def clean(self):
        cleaned_data = super().clean()

        domain = cleaned_data.get(
            "domain"
        )

        parent = cleaned_data.get(
            "parent"
        )

        name = cleaned_data.get(
            "name"
        )

        # -------------------------------------------------
        # Parent must belong to same Domain
        # -------------------------------------------------

        if parent and domain:

            if parent.domain_id != domain.id:

                self.add_error(
                    "parent",
                    "Parent topic must belong to "
                    "the selected aerospace domain.",
                )

        # -------------------------------------------------
        # Prevent duplicate Topic names
        # -------------------------------------------------

        if domain and name:

            existing = (
                AerospaceTopic.objects.filter(
                    domain=domain,
                    name__iexact=name.strip(),
                )
                .exists()
            )

            if existing:

                self.add_error(
                    "name",
                    "A topic with this name already exists "
                    "in the selected domain.",
                )

        return cleaned_data