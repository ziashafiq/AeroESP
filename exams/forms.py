from django import forms
from django.forms import (
    BaseInlineFormSet,
    inlineformset_factory,
)

from .models import (
    Exam,
    ExamQuestion,
)


DATETIME_LOCAL_FORMAT = "%Y-%m-%dT%H:%M"


class ExamForm(forms.ModelForm):

    class Meta:
        model = Exam

        fields = [
            "title",
            "description",
            "instructions",
            "mode",
            "duration_minutes",
            "starts_at",
            "ends_at",
            "max_attempts",
            "shuffle_questions",
            "shuffle_options",
            "result_policy",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
            "instructions": forms.Textarea(
                attrs={
                    "rows": 5,
                }
            ),
            "starts_at": forms.DateTimeInput(
                format=DATETIME_LOCAL_FORMAT,
                attrs={
                    "type": "datetime-local",
                },
            ),
            "ends_at": forms.DateTimeInput(
                format=DATETIME_LOCAL_FORMAT,
                attrs={
                    "type": "datetime-local",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["starts_at"].input_formats = [
            DATETIME_LOCAL_FORMAT,
        ]

        self.fields["ends_at"].input_formats = [
            DATETIME_LOCAL_FORMAT,
        ]


class BaseExamQuestionFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        seen_orders = set()

        for form in self.forms:

            if not hasattr(
                form,
                "cleaned_data",
            ):
                continue

            if (
                self.can_delete
                and self._should_delete_form(form)
            ):
                continue

            order = form.cleaned_data.get(
                "order"
            )

            if order is None:
                continue

            if order in seen_orders:
                raise forms.ValidationError(
                    "Question order values must be unique "
                    "within the exam."
                )

            seen_orders.add(order)


ExamQuestionFormSet = inlineformset_factory(
    parent_model=Exam,
    model=ExamQuestion,
    formset=BaseExamQuestionFormSet,
    fields=[
        "order",
        "points",
        "required",
    ],
    extra=0,
    can_delete=True,
)