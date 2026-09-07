import secrets

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify

from .captcha_fields import CaptchaField
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

    # Image drawn by this server, no third-party script to load.
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Absent entirely when no code is configured, so a deployment
        # that never sets AEROESP_INVITE_CODE sees no field at all and
        # nothing about existing sign-up behaves differently.
        if settings.AEROESP_INVITE_CODE:

            self.fields["invite_code"] = forms.CharField(
                required=True,
                label="Invite code",
                help_text=(
                    "Provided by AeroESP - this beta is by invitation "
                    "only."
                ),
                widget=forms.TextInput(
                    attrs={
                        "placeholder": "Enter your invite code",
                        "autocomplete": "off",
                    }
                ),
            )

            self.order_fields(
                [
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "invite_code",
                    "password1",
                    "password2",
                    "captcha",
                ]
            )

    def clean_invite_code(self):

        submitted = self.cleaned_data.get(
            "invite_code",
            "",
        ).strip()

        expected = settings.AEROESP_INVITE_CODE

        if not expected:
            return submitted

        if not secrets.compare_digest(submitted, expected):

            raise forms.ValidationError(
                "That invite code is not valid."
            )

        return submitted

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

        email = (
            self.cleaned_data["email"]
            .strip()
            .lower()
        )

        if CustomUser.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    @staticmethod
    def _build_unique_username(email):
        """
        Derive a username from the local part of the email.

        Two different addresses can share a local part
        (ali@a.com / ali@b.com), so a numeric suffix is appended
        until the username is free.
        """

        base = (
            slugify(
                email.split("@")[0]
            )
            or "user"
        )[:140]

        username = base
        suffix = 1

        while CustomUser.objects.filter(
            username=username
        ).exists():

            suffix += 1
            username = f"{base}{suffix}"

        return username

    def save(self, commit=True):

        user = super().save(
            commit=False
        )

        email = self.cleaned_data["email"]

        user.email = email

        user.username = (
            self._build_unique_username(email)
        )

        user.selected_role = (
            self.cleaned_data["role"]
        )

        if commit:
            user.save()

        return user