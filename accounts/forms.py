from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegistrationForm(UserCreationForm):

    ROLE_CHOICES = [
        ("STUDENT", "Student"),
        ("TEACHER", "Teacher"),
    ]

    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your first name",
            }
        )
    )

    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your last name",
            }
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
            }
        )
    )

    role = forms.ChoiceField(
        choices=[
            ("STUDENT", "Student"),
            ("TEACHER", "Teacher"),
        ],
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta:

        model = CustomUser

        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
            "password1",
            "password2",
        ]

        widgets = {
            "password1": forms.PasswordInput(
                attrs={
                    "autocomplete": "new-password",
                }
            ),
            "password2": forms.PasswordInput(
                attrs={
                    "autocomplete": "new-password",
                }
            ),
        }

    def clean_email(self):

        email = self.cleaned_data["email"]

        if CustomUser.objects.filter(
            email=email
        ).exists():

            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def save(self, commit=True):

        user = super().save(
            commit=False
        )

        user.username = (
            self.cleaned_data["email"]
            .split("@")[0]
        )

        user.email = (
            self.cleaned_data["email"]
        )

        user.selected_role = (
            self.cleaned_data["role"]
        )

        if commit:
            user.save()

        return user