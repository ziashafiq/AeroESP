"""
The form field and widget for accounts.captcha.

Rendering a form creates a fresh challenge, so a reloaded page or a
form redisplayed after a validation error always carries an image that
has not been used.
"""

from django import forms
from django.urls import reverse

from .captcha import (
    TEST_RESPONSE,
    create_challenge,
    normalise,
    verify,
)


class CaptchaWidget(forms.MultiWidget):
    """
    Renders the image, a hidden field carrying the challenge key, and
    the box the answer is typed into.
    """

    template_name = "aeroesp/widgets/captcha.html"

    def __init__(self, attrs=None):

        widgets = [
            forms.HiddenInput(),
            forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "autocapitalize": "characters",
                    "spellcheck": "false",
                    "inputmode": "text",
                    "placeholder": "Characters above",
                    "aria-label": (
                        "The characters shown in the image"
                    ),
                }
            ),
        ]

        super().__init__(widgets, attrs)

    def decompress(self, value):
        return [None, None]

    def get_context(self, name, value, attrs):

        challenge = create_challenge()

        # The typed answer is deliberately not echoed back: the old
        # challenge is spent, so the previous text no longer applies.
        context = super().get_context(
            name,
            [challenge.key, ""],
            attrs,
        )

        context["widget"]["image_url"] = reverse(
            "captcha_image",
            args=[challenge.key],
        )

        context["widget"]["refresh_url"] = reverse(
            "captcha_refresh"
        )

        return context


class CaptchaField(forms.MultiValueField):

    widget = CaptchaWidget

    default_error_messages = {
        "invalid": (
            "Those characters did not match the image. "
            "A new image has been loaded - please try again."
        ),
        "incomplete": (
            "Please type the characters shown in the image."
        ),
    }

    def __init__(self, **kwargs):

        kwargs.setdefault(
            "label",
            "Type the characters shown",
        )

        fields = (
            forms.CharField(max_length=40),
            forms.CharField(max_length=16),
        )

        super().__init__(
            fields=fields,
            require_all_fields=True,
            **kwargs,
        )

    def compress(self, data_list):
        return normalise(data_list[1]) if data_list else ""

    def clean(self, value):

        # MultiValueField.clean enforces required/max_length on both
        # halves and raises "incomplete" when the box is left empty.
        cleaned = super().clean(value)

        key = (value[0] or "").strip() if value else ""
        response = (value[1] or "").strip() if value else ""

        from django.conf import settings

        if (
            getattr(
                settings,
                "AEROESP_CAPTCHA_TEST_MODE",
                False,
            )
            and normalise(response) == TEST_RESPONSE
        ):
            return cleaned

        if not verify(key, response):
            raise forms.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
            )

        return cleaned
