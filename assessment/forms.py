from django import forms

from .models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


class TeacherQuestionForm(forms.ModelForm):
    """
    Form used by approved teachers to create and edit questions.

    Important:
    - Question owner is NOT exposed in this form.
    - Owner is assigned automatically in the view.
    - Only active aerospace domains are displayed.
    - Only CORE or APPROVED topics are available.
    - Pending/Rejected topics are not available for normal use.
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
                "If the required topic is not available, "
                "a new topic can be proposed separately."
            ),

            "source_reference": (
                "Optional. Enter the source used to prepare "
                "the question, such as a book, paper, standard, "
                "course material, or corpus."
            ),

            "visibility": (
                "Controls where this question may be used."
            ),
        }

        widgets = {
            "question_text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder":
                        "Enter the complete question here...",
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
                    "placeholder":
                        "Optional explanation for the correct answer...",
                }
            ),

            "source_reference": forms.TextInput(
                attrs={
                    "placeholder":
                        "Book, paper, standard, corpus, course material, etc.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # =================================================
        # Aerospace Domains
        # =================================================

        self.fields["domain_ref"].queryset = (
            AerospaceDomain.objects.filter(
                is_active=True,
            )
            .order_by(
                "order",
                "name",
            )
        )

        self.fields["domain_ref"].required = True

        # =================================================
        # Aerospace Topics
        # =================================================

        self.fields["topic_ref"].queryset = (
            AerospaceTopic.objects.filter(
                is_active=True,
                domain__is_active=True,
                approval_status__in=[
                    AerospaceTopic.ApprovalStatus.CORE,
                    AerospaceTopic.ApprovalStatus.APPROVED,
                ],
            )
            .select_related(
                "domain",
                "parent",
            )
            .order_by(
                "domain__order",
                "domain__name",
                "order",
                "name",
            )
        )

        self.fields["topic_ref"].required = False

        # =================================================
        # Visibility
        # =================================================
        #
        # Teachers are NOT allowed to directly publish
        # questions into the official AeroESP Bank.
        #
        # Official-bank publication will later require
        # review / approval.
        # =================================================

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

        domain = cleaned_data.get(
            "domain_ref"
        )

        topic = cleaned_data.get(
            "topic_ref"
        )

        # =================================================
        # Topic / Domain consistency
        # =================================================

        if topic and not domain:
            self.add_error(
                "domain_ref",
                "Please select an aerospace domain "
                "before selecting a topic.",
            )

        if topic and domain:
            if topic.domain_id != domain.id:
                self.add_error(
                    "topic_ref",
                    "The selected topic does not belong "
                    "to the selected aerospace domain.",
                )

        # =================================================
        # Topic approval validation
        # =================================================

        if topic:
            allowed_statuses = {
                AerospaceTopic.ApprovalStatus.CORE,
                AerospaceTopic.ApprovalStatus.APPROVED,
            }

            if topic.approval_status not in allowed_statuses:
                self.add_error(
                    "topic_ref",
                    "This topic has not yet been approved "
                    "for use in AeroESP.",
                )

        return cleaned_data