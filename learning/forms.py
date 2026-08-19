from django import forms

from assessment.models import (
    AerospaceDomain,
    Question,
)

from .models import (
    CourseModule,
    LearningItem,
)


class LearningItemForm(forms.ModelForm):

    class Meta:
        model = LearningItem

        fields = [
            "module",
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
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

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

            self.fields[
                "module"
            ].queryset = queryset

            self.fields[
                "module"
            ].initial = module

        elif course is not None:

            queryset = queryset.filter(
                course=course,
            )

            self.fields[
                "module"
            ].queryset = queryset

        else:

            self.fields[
                "module"
            ].queryset = queryset


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

        if learning_item is None:
            return

        program_type = (
            learning_item
            .module
            .course
            .program
            .program_type
        )

        # Set track based on program type
        if program_type == "IELTS":
            self.instance.track = (
                Question.Track.GENERAL_ENGLISH
            )
            self.fields["domain_ref"].required = False
            self.fields["domain_ref"].queryset = (
                AerospaceDomain.objects.none()
            )
        else:
            self.instance.track = (
                Question.Track.AEROSPACE_ESP
            )
            self.fields["domain_ref"].required = True
            self.fields["domain_ref"].queryset = (
                AerospaceDomain.objects
                .filter(is_active=True)
                .order_by(
                    "order",
                    "name",
                )
            )

        # Optionally restrict topics based on domain if selected
        # (similar logic as TeacherQuestionForm can be added here)