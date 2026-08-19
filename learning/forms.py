from django import forms

from .models import LearningItem


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
                        "Example: depend from"
                    ),
                }
            ),
            "correct_form": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": (
                        "Example: depend on"
                    ),
                }
            ),
        }