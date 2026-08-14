from django import forms

from .models import Exam


class ExamAccessCodeForm(forms.Form):

    code = forms.CharField(
        label="Exam Access Code",
        max_length=16,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "placeholder": "Enter exam code",
            }
        ),
    )

    def clean_code(self):

        code = (
            self.cleaned_data["code"]
            .strip()
            .upper()
        )

        try:
            exam = Exam.objects.get(
                access_code__iexact=code,
                status=Exam.Status.PUBLISHED,
            )
        except Exam.DoesNotExist:
            raise forms.ValidationError(
                "No published exam was found "
                "with this access code."
            )

        self.exam = exam

        return code